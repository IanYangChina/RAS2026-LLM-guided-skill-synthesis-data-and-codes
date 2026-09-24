## Search State

- **Seed**: 8
- **Iteration**: 6 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 5 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 6 | 0.1223 | 0.19 | ❌ rejected |
| 4 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | force_threshold_switch | position_control | position_control | position_control | position_control | position_control | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 7 | -0.2194 | 0.15 | ❌ rejected |
| 3 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | force_threshold_switch | position_control | position_control | position_control | position_control | position_control | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 9 | -0.2667 | 0.15 | ❌ rejected |
| 2 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | force_threshold_switch | position_control | position_control | impedance_control | impedance_control | position_control | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 9 | -0.2643 | 0.15 | ❌ rejected |
| 1 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | contact_detected | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 7 | 0.0732 | 0.20 | ✅ accepted |

**Proposal policy**: task_score is 0.19 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.122) — your mutation base

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

- **Composite score**: 0.122
- **task_score** (E): 0.189
- **fitness_score**: 0.572  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.450

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_object | 1.00 | 1.00 | 0.1587 |
| descend_to_grasp | 1.00 | 1.00 | 0.1137 |
| grasp | 1.00 | 1.00 | 0.0126 |
| lift | 1.00 | 1.00 | 0.1089 |
| approach_goal | 1.00 | 1.00 | 0.2719 |
| descend_to_place | 1.00 | 1.00 | 0.0802 |
| release | 1.00 | 1.00 | 0.0200 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.516, -0.001, 0.148) | (0.522, -0.001, 0.030)→(0.522, -0.001, 0.026) | 0.287→0.289 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_to_grasp | descend | 1.00 / step_budget | (0.516, -0.001, 0.148)→(0.516, -0.001, 0.034) | (0.522, -0.001, 0.026)→(0.522, -0.001, 0.026) | 0.289→0.289 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp | grasp | 1.00 / step_budget | (0.516, -0.001, 0.034)→(0.508, -0.001, 0.025) | (0.522, -0.001, 0.026)→(0.522, -0.001, 0.026) | 0.289→0.289 | 1.00 / 43.000 | 0.148 | 0.225 |
| lift | lift | 1.00 / step_budget | (0.508, -0.001, 0.025)→(0.504, -0.001, 0.134) | (0.522, -0.001, 0.026)→(0.524, -0.001, 0.128) | 0.289→0.240 | 1.00 / 22.667 | 0.112 | 0.732 |
| approach_goal | approach | 1.00 / step_budget | (0.504, -0.001, 0.134)→(0.600, 0.194, 0.292) | (0.524, -0.001, 0.128)→(0.537, 0.058, 0.016) | 0.240→0.253 | 1.00 / 8.667 | 94254.889 | 1.821 |
| descend_to_place | descend | 1.00 / step_budget | (0.600, 0.194, 0.292)→(0.604, 0.204, 0.213) | (0.537, 0.058, 0.016)→(0.537, 0.058, 0.016) | 0.253→0.253 | 1.00 / 8.667 | 91002.029 | 0.123 |
| release | release | 1.00 / step_budget | (0.604, 0.204, 0.213)→(0.599, 0.202, 0.232) | (0.537, 0.058, 0.016)→(0.537, 0.058, 0.016) | 0.253→0.253 | 1.00 / 4.000 | 0.123 | 0.123 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: 0.000
- terminal_score: 0.238
- phase_score: 0.742
- phase_breakdown.lift_object_score: 0.615
- phase_breakdown.grasp_contact_score: 0.867
- phase_breakdown.approach_goal_score: 0.670
- phase_breakdown.approach_object_score: 0.675
- phase_breakdown.final_placement_score: 0.819
- grasp_place_fitness: 0.596

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.596
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.238
- **Median Q (composite search score)**: 0.120
- **K-run variance**: 0.0003
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.326


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.4375,"average_solve_count":224.0,"average_success_count":224.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.approach_arc_height":0.0302,"approach_object.approach_speed":0.15608,"descend_to_grasp.descend_speed":0.0487,"descend_to_place.descend_place_speed":0.02925,"lift.lift_height":0.11468,"release.release_time":0.67813},"optimized_scores":{"best_composite_score":0.11969,"best_fitness_score":0.56969,"best_task_score":0.17905},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":2163.0,"contact_point_centroid":[0.51648,0.10114,-0.00248],"force_p95":0.16278,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.88515,"mean_force":0.14564,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.53402,0.15638,0.27374]},{"body_a":"world","body_b":"grasp_target","contact_count":77.0,"contact_point_centroid":[0.47924,0.04589,-0.00149],"force_p95":0.67088,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.70731,"mean_force":0.16415,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.46901,0.04659,0.02813]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5458.0,"contact_point_centroid":[0.46812,0.06544,0.0712],"force_p95":0.0977,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32312,"mean_force":0.0583,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.46679,0.04637,0.06926]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5078.0,"contact_point_centroid":[0.4681,0.0273,0.07317],"force_p95":0.10166,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29694,"mean_force":0.06103,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.46679,0.04637,0.07064]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2929.0,"contact_point_centroid":[0.48061,0.08279,0.15856],"force_p95":0.17351,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28734,"mean_force":0.10175,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.47513,0.06407,0.15771]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.48277,0.04839,-0.00219],"force_p95":0.17554,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.26557,"mean_force":0.13699,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.47142,0.04685,0.02772]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3443.0,"contact_point_centroid":[0.48156,0.04682,0.15996],"force_p95":0.152,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25486,"mean_force":0.09122,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.47577,0.06512,0.15966]},{"body_a":"world","body_b":"grasp_target","contact_count":1124.0,"contact_point_centroid":[0.4827,0.04873,-0.00188],"force_p95":0.13644,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12306,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.49076,0.02004,0.22554]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4989.0,"contact_point_centroid":[0.47011,0.0275,0.02955],"force_p95":0.0718,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12521,"mean_force":0.0431,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.47029,0.04674,0.02659]},{"body_a":"world","body_b":"grasp_target","contact_count":1580.0,"contact_point_centroid":[0.4827,0.04873,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.47868,0.04443,0.09073]},{"body_a":"world","body_b":"grasp_target","contact_count":952.0,"contact_point_centroid":[0.51636,0.10125,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.57458,0.22062,0.27878]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.51636,0.10125,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.57424,0.22393,0.23913]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5483.0,"contact_point_centroid":[0.47003,0.06611,0.02893],"force_p95":0.07322,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0846,"mean_force":0.04176,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.4703,0.04674,0.0266]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2077.0,"contact_point_centroid":[0.53792,0.16177,0.28115],"force_p95":0.01124,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01653,"mean_force":0.01059,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.53748,0.16174,0.27886]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1024.0,"contact_point_centroid":[0.57506,0.22066,0.28107],"force_p95":0.01095,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01276,"mean_force":0.01037,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.57459,0.22063,0.27871]},{"body_a":"left_finger","body_b":"right_finger","contact_count":229.0,"contact_point_centroid":[0.57657,0.2249,0.23764],"force_p95":0.01095,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01097,"mean_force":0.00981,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.57614,0.22486,0.23509]}],"total_contact_groups":16},"final_pose_error":0.00997,"key_states":{"actual_goal_position":[0.58187,0.22885,0.23048],"final_object_position":[0.51636,0.10125,0.01602],"final_tcp_position":[0.57752,0.22537,0.23875],"realised_goal_position":[0.58187,0.22885,0.23048],"realised_object_initial_position":[0.4827,0.04873,0.03]},"peak_contact_force":1.88515,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":282.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.03],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28719,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1124.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_object","tcp_end":[0.482,0.04162,0.14847],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.12265,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":395.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1580.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_contact","tcp_end":[0.47814,0.0475,0.03457],"tcp_start":[0.482,0.04162,0.14847],"tcp_to_object_dist_end":0.00977,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":47.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.4826,0.04691,0.02536],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.2916,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.16681,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12272.0,"raw_peak_contact_force":0.26557,"tcp_end":[0.47026,0.04673,0.02656],"tcp_start":[0.47814,0.0475,0.03457],"tcp_to_object_dist_end":0.0124,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":292.0,"n_steps_budget":720.0,"object_pos_end":[0.48444,0.04658,0.1173],"object_pos_start":[0.4826,0.04691,0.02536],"object_to_goal_dist_end":0.23564,"object_to_goal_dist_start":0.2916,"object_z_max":0.11702,"peak_contact_force":0.10906,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":10613.0,"raw_peak_contact_force":0.70731,"subtask_id":"lift_object","tcp_end":[0.46654,0.04635,0.1216],"tcp_start":[0.47026,0.04673,0.02656],"tcp_to_object_dist_end":0.01841,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":926.0,"n_steps_budget":1000.0,"object_pos_end":[0.51636,0.10125,0.01602],"object_pos_start":[0.48444,0.04658,0.1173],"object_to_goal_dist_end":0.25801,"object_to_goal_dist_start":0.23564,"object_z_max":0.18014,"peak_contact_force":0.12263,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":10612.0,"raw_peak_contact_force":1.88515,"subtask_id":"approach_goal","tcp_end":[0.57316,0.21686,0.31732],"tcp_start":[0.46654,0.04635,0.1216],"tcp_to_object_dist_end":0.32768,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":238.0,"n_steps_budget":1000.0,"object_pos_end":[0.51636,0.10125,0.01602],"object_pos_start":[0.51636,0.10125,0.01602],"object_to_goal_dist_end":0.25801,"object_to_goal_dist_start":0.25801,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1976.0,"raw_peak_contact_force":0.12263,"subtask_id":"final_placement","tcp_end":[0.57752,0.22537,0.23875],"tcp_start":[0.57316,0.21686,0.31732],"tcp_to_object_dist_end":0.26221,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51636,0.10125,0.01602],"object_pos_start":[0.51636,0.10125,0.01602],"object_to_goal_dist_end":0.25801,"object_to_goal_dist_start":0.25801,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1029.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.57316,0.22337,0.25885],"tcp_start":[0.57752,0.22537,0.23875],"tcp_to_object_dist_end":0.27768,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `2b35d39beba75b46a5edd8e67b975c00ef2c88fb75a3753bdd32db5918adf9e2`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.68878,"average_solve_count":196.0,"average_success_count":196.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.approach_arc_height":0.03029,"approach_object.approach_speed":0.19471,"descend_to_grasp.descend_speed":0.04932,"descend_to_place.descend_place_speed":0.06383,"lift.lift_height":0.15946,"release.release_time":0.45565},"optimized_scores":{"best_composite_score":0.10157,"best_fitness_score":0.55157,"best_task_score":0.14905},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":2590.0,"contact_point_centroid":[0.5345,0.02996,-0.00237],"force_p95":0.13331,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.84034,"mean_force":0.14452,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.56742,0.11775,0.26425]},{"body_a":"world","body_b":"grasp_target","contact_count":76.0,"contact_point_centroid":[0.53354,-0.02022,-0.00137],"force_p95":0.69739,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.741,"mean_force":0.16323,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52122,-0.0207,0.02541]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6148.0,"contact_point_centroid":[0.52209,-0.00178,0.08816],"force_p95":0.11538,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.34079,"mean_force":0.07795,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.51861,-0.02064,0.08588]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6682.0,"contact_point_centroid":[0.52217,-0.03938,0.08625],"force_p95":0.11115,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31888,"mean_force":0.07303,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.51864,-0.02064,0.08457]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1395.0,"contact_point_centroid":[0.52783,0.01277,0.17641],"force_p95":0.20604,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27843,"mean_force":0.12055,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.52204,-0.00559,0.17835]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1469.0,"contact_point_centroid":[0.52775,-0.0239,0.17626],"force_p95":0.20924,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27465,"mean_force":0.11939,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.52208,-0.00557,0.1784]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53703,-0.0211,-0.00205],"force_p95":0.13918,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.18491,"mean_force":0.12726,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.5238,-0.02075,0.02553]},{"body_a":"world","body_b":"grasp_target","contact_count":1112.0,"contact_point_centroid":[0.53702,-0.02132,-0.00188],"force_p95":0.13647,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12307,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.51332,-0.00885,0.22471]},{"body_a":"world","body_b":"grasp_target","contact_count":1524.0,"contact_point_centroid":[0.53702,-0.02132,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.52827,-0.01953,0.08968]},{"body_a":"world","body_b":"grasp_target","contact_count":912.0,"contact_point_centroid":[0.53428,0.03,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.60389,0.21761,0.25645]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.53428,0.03,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.60238,0.22221,0.21473]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4092.0,"contact_point_centroid":[0.52357,-0.00153,0.02685],"force_p95":0.07748,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1199,"mean_force":0.05179,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.52256,-0.02073,0.02413]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4918.0,"contact_point_centroid":[0.52353,-0.03982,0.02592],"force_p95":0.06942,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08876,"mean_force":0.04478,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.52256,-0.02073,0.02414]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2531.0,"contact_point_centroid":[0.5707,0.12538,0.27065],"force_p95":0.01111,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01584,"mean_force":0.01054,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.57031,0.12537,0.26845]},{"body_a":"left_finger","body_b":"right_finger","contact_count":986.0,"contact_point_centroid":[0.60436,0.21763,0.25867],"force_p95":0.0109,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01268,"mean_force":0.01032,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.6039,0.21761,0.25639]},{"body_a":"left_finger","body_b":"right_finger","contact_count":227.0,"contact_point_centroid":[0.60487,0.22322,0.21354],"force_p95":0.01089,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01091,"mean_force":0.00984,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.60453,0.2232,0.2112]}],"total_contact_groups":16},"final_pose_error":0.00973,"key_states":{"actual_goal_position":[0.61031,0.22775,0.20741],"final_object_position":[0.53428,0.03,0.01602],"final_tcp_position":[0.60607,0.22368,0.21516],"realised_goal_position":[0.61031,0.22775,0.20741],"realised_object_initial_position":[0.53702,-0.02132,0.03]},"peak_contact_force":273015.96934,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":279.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.03],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31446,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1112.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_object","tcp_end":[0.52852,-0.01826,0.14771],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.12203,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":381.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1524.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_contact","tcp_end":[0.53116,-0.02087,0.03393],"tcp_start":[0.52852,-0.01826,0.14771],"tcp_to_object_dist_end":0.00986,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53687,-0.02061,0.02581],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31632,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.13537,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10810.0,"raw_peak_contact_force":0.18491,"tcp_end":[0.52253,-0.02072,0.0241],"tcp_start":[0.53116,-0.02087,0.03393],"tcp_to_object_dist_end":0.01445,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":22.0,"n_steps":460.0,"n_steps_budget":990.0,"object_pos_end":[0.54016,-0.02061,0.15651],"object_pos_start":[0.53687,-0.02061,0.02581],"object_to_goal_dist_end":0.26305,"object_to_goal_dist_start":0.31632,"object_z_max":0.15626,"peak_contact_force":0.1183,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":12906.0,"raw_peak_contact_force":0.741,"subtask_id":"lift_object","tcp_end":[0.5188,-0.02063,0.16416],"tcp_start":[0.52253,-0.02072,0.0241],"tcp_to_object_dist_end":0.02269,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":892.0,"n_steps_budget":1000.0,"object_pos_end":[0.53428,0.03,0.01602],"object_pos_start":[0.54016,-0.02061,0.15651],"object_to_goal_dist_end":0.28552,"object_to_goal_dist_start":0.26305,"object_z_max":0.1747,"peak_contact_force":273015.96934,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":7985.0,"raw_peak_contact_force":1.84034,"subtask_id":"approach_goal","tcp_end":[0.60317,0.21249,0.29677],"tcp_start":[0.5188,-0.02063,0.16416],"tcp_to_object_dist_end":0.34186,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":228.0,"n_steps_budget":1000.0,"object_pos_end":[0.53428,0.03,0.01602],"object_pos_start":[0.53428,0.03,0.01602],"object_to_goal_dist_end":0.28552,"object_to_goal_dist_start":0.28552,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1898.0,"raw_peak_contact_force":0.12263,"subtask_id":"final_placement","tcp_end":[0.60607,0.22368,0.21516],"tcp_start":[0.60317,0.21249,0.29677],"tcp_to_object_dist_end":0.28692,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53428,0.03,0.01602],"object_pos_start":[0.53428,0.03,0.01602],"object_to_goal_dist_end":0.28552,"object_to_goal_dist_start":0.28552,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1027.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.60115,0.22162,0.23412],"tcp_start":[0.60607,0.22368,0.21516],"tcp_to_object_dist_end":0.29792,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `530652a2467d9ac78fab654e7ed7fc5283ca1649270bc8f158e04c16074f9f95`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.48387,"average_solve_count":217.0,"average_success_count":217.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.approach_arc_height":0.02002,"approach_object.approach_speed":0.21429,"descend_to_grasp.descend_speed":0.04167,"descend_to_place.descend_place_speed":0.0313,"lift.lift_height":0.11057,"release.release_time":0.3979},"optimized_scores":{"best_composite_score":0.14565,"best_fitness_score":0.59565,"best_task_score":0.2383},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":1979.0,"contact_point_centroid":[0.56167,0.0407,-0.00255],"force_p95":0.19385,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.7377,"mean_force":0.15275,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.59185,0.0956,0.2303]},{"body_a":"world","body_b":"grasp_target","contact_count":80.0,"contact_point_centroid":[0.54228,-0.02801,-0.00138],"force_p95":0.65809,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.74785,"mean_force":0.16387,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52952,-0.02832,0.02497]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4377.0,"contact_point_centroid":[0.52976,-0.00929,0.06588],"force_p95":0.11171,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33747,"mean_force":0.07377,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52688,-0.02822,0.06339]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4811.0,"contact_point_centroid":[0.52987,-0.04702,0.06422],"force_p95":0.10673,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32161,"mean_force":0.06886,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52691,-0.02822,0.06258]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2769.0,"contact_point_centroid":[0.54212,0.01382,0.14111],"force_p95":0.18188,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29814,"mean_force":0.10455,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.53637,-0.00465,0.14127]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2816.0,"contact_point_centroid":[0.54195,-0.02331,0.14081],"force_p95":0.18348,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28332,"mean_force":0.10494,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.53632,-0.00484,0.14107]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.54562,-0.02896,-0.00208],"force_p95":0.14643,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.22403,"mean_force":0.1292,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.53209,-0.02839,0.02507]},{"body_a":"world","body_b":"grasp_target","contact_count":1148.0,"contact_point_centroid":[0.5456,-0.02923,-0.00188],"force_p95":0.13644,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12305,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.51703,-0.01223,0.22402]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4076.0,"contact_point_centroid":[0.53196,-0.00916,0.02634],"force_p95":0.07865,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12662,"mean_force":0.05182,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.53083,-0.02836,0.02363]},{"body_a":"world","body_b":"grasp_target","contact_count":1516.0,"contact_point_centroid":[0.5456,-0.02923,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.53622,-0.02684,0.08918]},{"body_a":"world","body_b":"grasp_target","contact_count":912.0,"contact_point_centroid":[0.56132,0.04132,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.62498,0.15698,0.22471]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.56132,0.04132,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.62338,0.16043,0.18428]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4945.0,"contact_point_centroid":[0.5319,-0.04748,0.02541],"force_p95":0.07064,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08869,"mean_force":0.04483,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.53084,-0.02836,0.02364]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1910.0,"contact_point_centroid":[0.59505,0.10072,0.2363],"force_p95":0.01148,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01642,"mean_force":0.01058,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.59473,0.10072,0.23403]},{"body_a":"left_finger","body_b":"right_finger","contact_count":974.0,"contact_point_centroid":[0.62529,0.15698,0.22704],"force_p95":0.01099,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01283,"mean_force":0.01043,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.62498,0.15697,0.22475]},{"body_a":"left_finger","body_b":"right_finger","contact_count":222.0,"contact_point_centroid":[0.62642,0.16125,0.18285],"force_p95":0.01097,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01099,"mean_force":0.01007,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.62592,0.16123,0.1808]}],"total_contact_groups":16},"final_pose_error":0.00999,"key_states":{"actual_goal_position":[0.63284,0.16493,0.17692],"final_object_position":[0.56132,0.04132,0.01602],"final_tcp_position":[0.62766,0.16162,0.18479],"realised_goal_position":[0.63284,0.16493,0.17692],"realised_object_initial_position":[0.5456,-0.02923,0.03]},"peak_contact_force":273005.84105,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":288.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.03],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.25864,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1148.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_object","tcp_end":[0.53609,-0.02519,0.14669],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.12111,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":379.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1516.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_contact","tcp_end":[0.53955,-0.02861,0.03375],"tcp_start":[0.53609,-0.02519,0.14669],"tcp_to_object_dist_end":0.00984,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54545,-0.02826,0.02573],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26042,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.14093,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10821.0,"raw_peak_contact_force":0.22403,"tcp_end":[0.5308,-0.02835,0.0236],"tcp_start":[0.53955,-0.02861,0.03375],"tcp_to_object_dist_end":0.0148,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":309.0,"n_steps_budget":720.0,"object_pos_end":[0.54666,-0.02817,0.11167],"object_pos_start":[0.54545,-0.02826,0.02573],"object_to_goal_dist_end":0.2213,"object_to_goal_dist_start":0.26042,"object_z_max":0.11142,"peak_contact_force":0.10944,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":9268.0,"raw_peak_contact_force":0.74785,"subtask_id":"lift_object","tcp_end":[0.52658,-0.0282,0.11484],"tcp_start":[0.5308,-0.02835,0.0236],"tcp_to_object_dist_end":0.02033,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":863.0,"n_steps_budget":1000.0,"object_pos_end":[0.56132,0.04132,0.01602],"object_pos_start":[0.54666,-0.02817,0.11167],"object_to_goal_dist_end":0.21514,"object_to_goal_dist_start":0.2213,"object_z_max":0.15053,"peak_contact_force":9748.57625,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":9474.0,"raw_peak_contact_force":1.7377,"subtask_id":"approach_goal","tcp_end":[0.62416,0.15317,0.26327],"tcp_start":[0.52658,-0.0282,0.11484],"tcp_to_object_dist_end":0.27856,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":228.0,"n_steps_budget":1000.0,"object_pos_end":[0.56132,0.04132,0.01602],"object_pos_start":[0.56132,0.04132,0.01602],"object_to_goal_dist_end":0.21514,"object_to_goal_dist_start":0.21514,"object_z_max":0.01602,"peak_contact_force":273005.84105,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1886.0,"raw_peak_contact_force":0.12263,"subtask_id":"final_placement","tcp_end":[0.62766,0.16162,0.18479],"tcp_start":[0.62416,0.15317,0.26327],"tcp_to_object_dist_end":0.21761,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.56132,0.04132,0.01602],"object_pos_start":[0.56132,0.04132,0.01602],"object_to_goal_dist_end":0.21514,"object_to_goal_dist_start":0.21514,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1022.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.62188,0.15995,0.20363],"tcp_start":[0.62766,0.16162,0.18479],"tcp_to_object_dist_end":0.23008,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```