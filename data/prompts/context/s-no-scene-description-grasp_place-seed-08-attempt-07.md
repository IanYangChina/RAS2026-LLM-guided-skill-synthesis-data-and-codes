## Search State

- **Seed**: 8
- **Iteration**: 8 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 7 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | impedance_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 8 | 0.0216 | 0.19 | ❌ rejected |
| 6 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | impedance_control | position_control | position_control | pose_tolerance | contact_detected | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 8 | 0.0817 | 0.32 | ✅ accepted |
| 5 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 6 | 0.1223 | 0.19 | ❌ rejected |
| 4 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | force_threshold_switch | position_control | position_control | position_control | position_control | position_control | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 7 | -0.2194 | 0.15 | ❌ rejected |
| 3 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | force_threshold_switch | position_control | position_control | position_control | position_control | position_control | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 9 | -0.2667 | 0.15 | ❌ rejected |

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

## Current Skill (Q=0.022) — your mutation base

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

- **Composite score**: 0.022
- **task_score** (E): 0.187
- **fitness_score**: 0.572  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.550

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_object | 1.00 | 1.00 | 0.1587 |
| descend_to_grasp | 1.00 | 1.00 | 0.1137 |
| grasp | 1.00 | 1.00 | 0.0126 |
| lift | 1.00 | 1.00 | 0.1116 |
| approach_goal | 0.67 | 0.67 | 0.2611 |
| descend_to_place | 1.00 | 1.00 | 0.1128 |
| release | 1.00 | 1.00 | 0.0202 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.516, -0.001, 0.148) | (0.522, -0.001, 0.030)→(0.522, -0.001, 0.026) | 0.287→0.289 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_to_grasp | descend | 1.00 / step_budget | (0.516, -0.001, 0.148)→(0.516, -0.001, 0.034) | (0.522, -0.001, 0.026)→(0.522, -0.001, 0.026) | 0.289→0.289 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp | grasp | 1.00 / step_budget | (0.516, -0.001, 0.034)→(0.508, -0.001, 0.025) | (0.522, -0.001, 0.026)→(0.522, -0.001, 0.026) | 0.289→0.289 | 1.00 / 43.000 | 0.148 | 0.225 |
| lift | lift | 1.00 / step_budget | (0.508, -0.001, 0.025)→(0.504, -0.001, 0.136) | (0.522, -0.001, 0.026)→(0.524, -0.001, 0.131) | 0.289→0.239 | 1.00 / 22.333 | 0.113 | 0.729 |
| approach_goal | approach | 0.67 / step_budget | (0.504, -0.001, 0.136)→(0.589, 0.167, 0.316) | (0.524, -0.001, 0.131)→(0.539, 0.077, 0.029) | 0.239→0.244 | 0.67 / 6.000 | 0.082 | 1.327 |
| descend_to_place | descend | 1.00 / step_budget | (0.589, 0.167, 0.316)→(0.603, 0.202, 0.210) | (0.539, 0.077, 0.029)→(0.538, 0.084, 0.016) | 0.244→0.257 | 1.00 / 8.333 | 94252.904 | 0.897 |
| release | release | 1.00 / step_budget | (0.603, 0.202, 0.210)→(0.598, 0.200, 0.230) | (0.538, 0.084, 0.016)→(0.538, 0.084, 0.016) | 0.257→0.257 | 1.00 / 4.000 | 0.123 | 0.123 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: 0.000
- terminal_score: 0.238
- phase_score: 0.731
- phase_breakdown.lift_object_score: 0.719
- phase_breakdown.grasp_contact_score: 0.877
- phase_breakdown.approach_goal_score: 0.490
- phase_breakdown.approach_object_score: 0.671
- phase_breakdown.final_placement_score: 0.820
- grasp_place_fitness: 0.599

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.599
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.238
- **Median Q (composite search score)**: 0.028
- **K-run variance**: 0.0007
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Parameters at upper bound**: approach_goal.transport_arc_height
- **Final σ (mean)**: 0.353


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.20377,"average_solve_count":265.0,"average_success_count":265.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.transport_arc_height":0.3,"approach_goal.transport_speed":0.01786,"approach_object.approach_speed":0.15094,"descend_to_grasp.descend_speed":0.04386,"descend_to_grasp.force_limit":11.04452,"descend_to_place.descend_place_speed":0.05022,"lift.lift_height":0.12039,"release.release_time":0.42083},"optimized_scores":{"best_composite_score":0.04894,"best_fitness_score":0.59894,"best_task_score":0.23754},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":1067.0,"contact_point_centroid":[0.56344,0.23963,-0.00362],"force_p95":0.64126,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.44488,"mean_force":0.19235,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.5688,0.21158,0.27676]},{"body_a":"world","body_b":"grasp_target","contact_count":77.0,"contact_point_centroid":[0.4798,0.0459,-0.00152],"force_p95":0.66306,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.70201,"mean_force":0.16413,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.46904,0.04659,0.02808]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5649.0,"contact_point_centroid":[0.46828,0.06541,0.07297],"force_p95":0.10028,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32138,"mean_force":0.05985,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.46677,0.04637,0.07103]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5267.0,"contact_point_centroid":[0.4683,0.02732,0.07507],"force_p95":0.10342,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29387,"mean_force":0.06258,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.46677,0.04637,0.07257]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":10514.0,"contact_point_centroid":[0.49006,0.06224,0.23413],"force_p95":0.13262,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27193,"mean_force":0.0832,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.48594,0.08069,0.23481]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.48277,0.04839,-0.00219],"force_p95":0.1756,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.26566,"mean_force":0.13701,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.47142,0.04684,0.02773]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":10268.0,"contact_point_centroid":[0.49226,0.10232,0.23808],"force_p95":0.13033,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25484,"mean_force":0.08655,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.48797,0.08384,0.23857]},{"body_a":"world","body_b":"grasp_target","contact_count":1136.0,"contact_point_centroid":[0.4827,0.04873,-0.00188],"force_p95":0.13644,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12306,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.49075,0.02003,0.22559]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4989.0,"contact_point_centroid":[0.47011,0.0275,0.02956],"force_p95":0.07182,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12507,"mean_force":0.0431,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.47029,0.04673,0.02659]},{"body_a":"world","body_b":"grasp_target","contact_count":1588.0,"contact_point_centroid":[0.4827,0.04873,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.47861,0.0444,0.09081]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.56326,0.24095,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.57289,0.22191,0.2369]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5482.0,"contact_point_centroid":[0.47003,0.06611,0.02893],"force_p95":0.07323,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08463,"mean_force":0.04177,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.47029,0.04673,0.0266]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1124.0,"contact_point_centroid":[0.56944,0.21197,0.27741],"force_p95":0.01256,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01637,"mean_force":0.01068,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.569,0.21194,0.27514]},{"body_a":"left_finger","body_b":"right_finger","contact_count":220.0,"contact_point_centroid":[0.57528,0.22292,0.23521],"force_p95":0.01099,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01101,"mean_force":0.01008,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.57485,0.22289,0.23291]}],"total_contact_groups":14},"final_pose_error":0.00992,"key_states":{"actual_goal_position":[0.58187,0.22885,0.23048],"final_object_position":[0.56326,0.24095,0.01602],"final_tcp_position":[0.57618,0.22328,0.23638],"realised_goal_position":[0.58187,0.22885,0.23048],"realised_object_initial_position":[0.4827,0.04873,0.03]},"peak_contact_force":9748.99329,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":285.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.03],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28719,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1136.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_object","tcp_end":[0.48199,0.04158,0.14861],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.1228,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":397.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1588.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_contact","tcp_end":[0.47814,0.0475,0.03458],"tcp_start":[0.48199,0.04158,0.14861],"tcp_to_object_dist_end":0.00978,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":47.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.4826,0.04691,0.02536],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.29161,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.16687,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12271.0,"raw_peak_contact_force":0.26566,"tcp_end":[0.47026,0.04673,0.02656],"tcp_start":[0.47814,0.0475,0.03458],"tcp_to_object_dist_end":0.0124,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":312.0,"n_steps_budget":780.0,"object_pos_end":[0.48484,0.04662,0.12278],"object_pos_start":[0.4826,0.04691,0.02536],"object_to_goal_dist_end":0.23286,"object_to_goal_dist_start":0.29161,"object_z_max":0.12251,"peak_contact_force":0.10938,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":10993.0,"raw_peak_contact_force":0.70201,"subtask_id":"lift_object","tcp_end":[0.46656,0.04635,0.12754],"tcp_start":[0.47026,0.04673,0.02656],"tcp_to_object_dist_end":0.01889,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.56684,0.22168,0.0555],"object_pos_start":[0.48484,0.04662,0.12278],"object_to_goal_dist_end":0.17578,"object_to_goal_dist_start":0.23286,"object_z_max":0.29702,"peak_contact_force":0.0,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":20782.0,"raw_peak_contact_force":0.27193,"subtask_id":"approach_goal","tcp_end":[0.56227,0.19958,0.32492],"tcp_start":[0.46656,0.04635,0.12754],"tcp_to_object_dist_end":0.27037,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":294.0,"n_steps_budget":1000.0,"object_pos_end":[0.56327,0.24095,0.01602],"object_pos_start":[0.56684,0.22168,0.0555],"object_to_goal_dist_end":0.21561,"object_to_goal_dist_start":0.17578,"object_z_max":0.0555,"peak_contact_force":9748.99329,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2191.0,"raw_peak_contact_force":2.44488,"subtask_id":"final_placement","tcp_end":[0.57618,0.22328,0.23638],"tcp_start":[0.56227,0.19958,0.32492],"tcp_to_object_dist_end":0.22145,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.56326,0.24095,0.01602],"object_pos_start":[0.56327,0.24095,0.01602],"object_to_goal_dist_end":0.21561,"object_to_goal_dist_start":0.21561,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1020.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.57179,0.22134,0.25665],"tcp_start":[0.57618,0.22328,0.23638],"tcp_to_object_dist_end":0.24158,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `2b35d39beba75b46a5edd8e67b975c00ef2c88fb75a3753bdd32db5918adf9e2`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.53401,"average_solve_count":294.0,"average_success_count":294.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.transport_arc_height":0.12562,"approach_goal.transport_speed":0.03908,"approach_object.approach_speed":0.20748,"descend_to_grasp.descend_speed":0.03761,"descend_to_grasp.force_limit":9.65144,"descend_to_place.descend_place_speed":0.04488,"lift.lift_height":0.16039,"release.release_time":0.45054},"optimized_scores":{"best_composite_score":-0.01266,"best_fitness_score":0.53734,"best_task_score":0.1206},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":2851.0,"contact_point_centroid":[0.50237,-0.00099,-0.00238],"force_p95":0.12498,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.83581,"mean_force":0.14089,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.54177,0.04677,0.32199]},{"body_a":"world","body_b":"grasp_target","contact_count":78.0,"contact_point_centroid":[0.5336,-0.02075,-0.00135],"force_p95":0.68683,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.73859,"mean_force":0.16964,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52126,-0.0207,0.02539]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6271.0,"contact_point_centroid":[0.5221,-0.00178,0.08865],"force_p95":0.11511,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33919,"mean_force":0.07787,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.51862,-0.02064,0.08639]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1891.0,"contact_point_centroid":[0.52009,-0.00679,0.18752],"force_p95":0.20913,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32674,"mean_force":0.11928,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.51464,-0.02485,0.18959]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6791.0,"contact_point_centroid":[0.52217,-0.03938,0.0865],"force_p95":0.11119,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31737,"mean_force":0.07311,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.51864,-0.02064,0.08484]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1579.0,"contact_point_centroid":[0.52022,-0.04319,0.18563],"force_p95":0.20667,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30916,"mean_force":0.12245,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.51471,-0.02477,0.18717]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53703,-0.0211,-0.00205],"force_p95":0.13915,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.18489,"mean_force":0.12725,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.5238,-0.02075,0.02546]},{"body_a":"world","body_b":"grasp_target","contact_count":1112.0,"contact_point_centroid":[0.53702,-0.02132,-0.00188],"force_p95":0.13647,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12307,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.51332,-0.00885,0.22471]},{"body_a":"world","body_b":"grasp_target","contact_count":1536.0,"contact_point_centroid":[0.53702,-0.02132,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.52825,-0.01953,0.08973]},{"body_a":"world","body_b":"grasp_target","contact_count":2116.0,"contact_point_centroid":[0.50225,-0.00109,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.59233,0.18566,0.27856]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.50225,-0.00109,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.60108,0.2189,0.21036]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4092.0,"contact_point_centroid":[0.52357,-0.00153,0.02678],"force_p95":0.07747,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11979,"mean_force":0.05179,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.52256,-0.02073,0.02407]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4918.0,"contact_point_centroid":[0.52354,-0.03982,0.02586],"force_p95":0.06941,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08875,"mean_force":0.04478,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.52257,-0.02073,0.02407]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2866.0,"contact_point_centroid":[0.54364,0.0508,0.32826],"force_p95":0.01114,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01605,"mean_force":0.0106,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.54332,0.0508,0.32595]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2275.0,"contact_point_centroid":[0.59279,0.18566,0.28087],"force_p95":0.01097,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0127,"mean_force":0.01038,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.59233,0.18564,0.27862]},{"body_a":"left_finger","body_b":"right_finger","contact_count":225.0,"contact_point_centroid":[0.60375,0.21996,0.20905],"force_p95":0.01094,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0126,"mean_force":0.00995,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.60328,0.21994,0.2068]}],"total_contact_groups":16},"final_pose_error":0.00984,"key_states":{"actual_goal_position":[0.61031,0.22775,0.20741],"final_object_position":[0.50225,-0.00109,0.01602],"final_tcp_position":[0.60479,0.22022,0.21052],"realised_goal_position":[0.61031,0.22775,0.20741],"realised_object_initial_position":[0.53702,-0.02132,0.03]},"peak_contact_force":273009.59584,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":279.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.03],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31446,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1112.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_object","tcp_end":[0.52852,-0.01826,0.14771],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.12203,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":384.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1536.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_contact","tcp_end":[0.53117,-0.02087,0.03387],"tcp_start":[0.52852,-0.01826,0.14771],"tcp_to_object_dist_end":0.0098,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53687,-0.02061,0.02581],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31632,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.13534,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10810.0,"raw_peak_contact_force":0.18489,"tcp_end":[0.52253,-0.02072,0.02403],"tcp_start":[0.53117,-0.02087,0.03387],"tcp_to_object_dist_end":0.01445,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":21.0,"n_steps":468.0,"n_steps_budget":1000.0,"object_pos_end":[0.54021,-0.02061,0.15722],"object_pos_start":[0.53687,-0.02061,0.02581],"object_to_goal_dist_end":0.2629,"object_to_goal_dist_start":0.31632,"object_z_max":0.15697,"peak_contact_force":0.12133,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":13140.0,"raw_peak_contact_force":0.73859,"subtask_id":"lift_object","tcp_end":[0.5188,-0.02063,0.16501],"tcp_start":[0.52253,-0.02072,0.02403],"tcp_to_object_dist_end":0.02278,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50225,-0.00109,0.01602],"object_pos_start":[0.54021,-0.02061,0.15722],"object_to_goal_dist_end":0.3173,"object_to_goal_dist_start":0.2629,"object_z_max":0.19377,"peak_contact_force":0.12263,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":9187.0,"raw_peak_contact_force":1.83581,"subtask_id":"approach_goal","tcp_end":[0.58151,0.1523,0.35109],"tcp_start":[0.5188,-0.02063,0.16501],"tcp_to_object_dist_end":0.37693,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":529.0,"n_steps_budget":1000.0,"object_pos_end":[0.50225,-0.00109,0.01602],"object_pos_start":[0.50225,-0.00109,0.01602],"object_to_goal_dist_end":0.3173,"object_to_goal_dist_start":0.3173,"object_z_max":0.01602,"peak_contact_force":273009.59584,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4391.0,"raw_peak_contact_force":0.12263,"subtask_id":"final_placement","tcp_end":[0.60479,0.22022,0.21052],"tcp_start":[0.58151,0.1523,0.35109],"tcp_to_object_dist_end":0.31197,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50225,-0.00109,0.01602],"object_pos_start":[0.50225,-0.00109,0.01602],"object_to_goal_dist_end":0.3173,"object_to_goal_dist_start":0.3173,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1025.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.59981,0.21829,0.22977],"tcp_start":[0.60479,0.22022,0.21052],"tcp_to_object_dist_end":0.32146,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `530652a2467d9ac78fab654e7ed7fc5283ca1649270bc8f158e04c16074f9f95`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.97386,"average_solve_count":153.0,"average_success_count":153.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.transport_arc_height":0.29365,"approach_goal.transport_speed":0.14862,"approach_object.approach_speed":0.14451,"descend_to_grasp.descend_speed":0.09983,"descend_to_grasp.force_limit":13.67473,"descend_to_place.descend_place_speed":0.05184,"lift.lift_height":0.11215,"release.release_time":0.36701},"optimized_scores":{"best_composite_score":0.02849,"best_fitness_score":0.57849,"best_task_score":0.20393},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":1799.0,"contact_point_centroid":[0.54745,0.01115,-0.00254],"force_p95":0.24458,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.87469,"mean_force":0.15459,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.58202,0.07641,0.25756]},{"body_a":"world","body_b":"grasp_target","contact_count":80.0,"contact_point_centroid":[0.54227,-0.02801,-0.00137],"force_p95":0.65799,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.74743,"mean_force":0.16057,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52951,-0.02831,0.02511]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4397.0,"contact_point_centroid":[0.52976,-0.00929,0.06655],"force_p95":0.11166,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33845,"mean_force":0.0737,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52688,-0.02822,0.06408]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4829.0,"contact_point_centroid":[0.52987,-0.04702,0.06485],"force_p95":0.10681,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32245,"mean_force":0.06881,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52691,-0.02822,0.06322]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2599.0,"contact_point_centroid":[0.53486,0.00018,0.15473],"force_p95":0.18012,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31186,"mean_force":0.10855,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.52913,-0.01831,0.15475]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2820.0,"contact_point_centroid":[0.5348,-0.03679,0.15398],"force_p95":0.18707,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27904,"mean_force":0.10424,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.52913,-0.01837,0.15429]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.54562,-0.02896,-0.00208],"force_p95":0.14649,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.22396,"mean_force":0.12921,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.53209,-0.02839,0.02519]},{"body_a":"world","body_b":"grasp_target","contact_count":1196.0,"contact_point_centroid":[0.5456,-0.02923,-0.00189],"force_p95":0.13615,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12304,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.51697,-0.0122,0.22421]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4076.0,"contact_point_centroid":[0.53196,-0.00916,0.02646],"force_p95":0.07865,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12686,"mean_force":0.05182,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.53083,-0.02836,0.02375]},{"body_a":"world","body_b":"grasp_target","contact_count":1384.0,"contact_point_centroid":[0.5456,-0.02923,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.53644,-0.02686,0.08926]},{"body_a":"world","body_b":"grasp_target","contact_count":1004.0,"contact_point_centroid":[0.54704,0.01121,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.62405,0.15456,0.22778]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.54704,0.01121,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.62323,0.15994,0.18387]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4945.0,"contact_point_centroid":[0.53189,-0.04747,0.02553],"force_p95":0.07064,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08861,"mean_force":0.04483,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.53083,-0.02836,0.02376]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1681.0,"contact_point_centroid":[0.58673,0.08399,0.26398],"force_p95":0.01146,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01637,"mean_force":0.01066,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.5863,0.08399,0.26169]},{"body_a":"left_finger","body_b":"right_finger","contact_count":219.0,"contact_point_centroid":[0.62648,0.16076,0.1825],"force_p95":0.01103,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01288,"mean_force":0.01019,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.62578,0.16075,0.18037]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1069.0,"contact_point_centroid":[0.62445,0.15455,0.23016],"force_p95":0.01099,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01256,"mean_force":0.01045,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.62404,0.15454,0.22791]}],"total_contact_groups":16},"final_pose_error":0.0099,"key_states":{"actual_goal_position":[0.63284,0.16493,0.17692],"final_object_position":[0.54704,0.01121,0.01602],"final_tcp_position":[0.62752,0.16111,0.18434],"realised_goal_position":[0.63284,0.16493,0.17692],"realised_object_initial_position":[0.5456,-0.02923,0.03]},"peak_contact_force":1.87469,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":300.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.03],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.25864,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1196.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_object","tcp_end":[0.53613,-0.02519,0.1467],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.12112,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":346.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.12262,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1384.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_contact","tcp_end":[0.53956,-0.02861,0.03389],"tcp_start":[0.53613,-0.02519,0.1467],"tcp_to_object_dist_end":0.00994,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54545,-0.02826,0.02573],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26042,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.14099,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10821.0,"raw_peak_contact_force":0.22396,"tcp_end":[0.5308,-0.02835,0.02372],"tcp_start":[0.53956,-0.02861,0.03389],"tcp_to_object_dist_end":0.01479,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":310.0,"n_steps_budget":720.0,"object_pos_end":[0.54667,-0.02818,0.11305],"object_pos_start":[0.54545,-0.02826,0.02573],"object_to_goal_dist_end":0.2209,"object_to_goal_dist_start":0.26042,"object_z_max":0.1128,"peak_contact_force":0.10942,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":9306.0,"raw_peak_contact_force":0.74743,"subtask_id":"lift_object","tcp_end":[0.5266,-0.0282,0.11635],"tcp_start":[0.5308,-0.02835,0.02372],"tcp_to_object_dist_end":0.02034,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":807.0,"n_steps_budget":1000.0,"object_pos_end":[0.54704,0.01121,0.01602],"object_pos_start":[0.54667,-0.02818,0.11305],"object_to_goal_dist_end":0.2385,"object_to_goal_dist_start":0.2209,"object_z_max":0.1757,"peak_contact_force":0.12263,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":8899.0,"raw_peak_contact_force":1.87469,"subtask_id":"approach_goal","tcp_end":[0.62251,0.14883,0.27132],"tcp_start":[0.5266,-0.0282,0.11635],"tcp_to_object_dist_end":0.29969,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":251.0,"n_steps_budget":1000.0,"object_pos_end":[0.54704,0.01121,0.01602],"object_pos_start":[0.54704,0.01121,0.01602],"object_to_goal_dist_end":0.2385,"object_to_goal_dist_start":0.2385,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2073.0,"raw_peak_contact_force":0.12263,"subtask_id":"final_placement","tcp_end":[0.62752,0.16111,0.18434],"tcp_start":[0.62251,0.14883,0.27132],"tcp_to_object_dist_end":0.23933,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54704,0.01121,0.01602],"object_pos_start":[0.54704,0.01121,0.01602],"object_to_goal_dist_end":0.2385,"object_to_goal_dist_start":0.2385,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1019.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.62173,0.15945,0.20322],"tcp_start":[0.62752,0.16111,0.18434],"tcp_to_object_dist_end":0.2502,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```