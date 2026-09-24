## Search State

- **Seed**: 8
- **Iteration**: 9 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 8 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | contact_detected | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 8 | 0.0140 | 0.17 | ❌ rejected |
| 7 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | impedance_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 8 | 0.0216 | 0.19 | ❌ rejected |
| 6 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | impedance_control | position_control | position_control | pose_tolerance | contact_detected | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 8 | 0.0817 | 0.32 | ✅ accepted |
| 5 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 6 | 0.1223 | 0.19 | ❌ rejected |
| 4 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | force_threshold_switch | position_control | position_control | position_control | position_control | position_control | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 7 | -0.2194 | 0.15 | ❌ rejected |

**Proposal policy**: task_score is 0.17 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.014) — your mutation base

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

- **Composite score**: 0.014
- **task_score** (E): 0.175
- **fitness_score**: 0.564  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.550

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_object | 1.00 | 1.00 | 0.1588 |
| descend_to_grasp | 1.00 | 1.00 | 0.1144 |
| grasp | 1.00 | 1.00 | 0.0123 |
| lift | 0.00 | 1.00 | 0.0042 |
| transport_to_goal | 0.00 | 0.67 | 0.0002 |
| descend_to_place | 0.00 | 1.00 | 0.1181 |
| release | 1.00 | 1.00 | 0.0226 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.516, -0.001, 0.148) | (0.522, -0.001, 0.030)→(0.522, -0.001, 0.026) | 0.287→0.289 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_to_grasp | descend | 1.00 / step_budget | (0.516, -0.001, 0.148)→(0.516, -0.000, 0.033) | (0.522, -0.001, 0.026)→(0.522, -0.001, 0.026) | 0.289→0.289 | 1.00 / 4.000 | 63.851 | 0.123 |
| grasp | grasp | 1.00 / step_budget | (0.516, -0.000, 0.033)→(0.508, -0.001, 0.024) | (0.522, -0.001, 0.026)→(0.522, -0.001, 0.026) | 0.289→0.289 | 1.00 / 43.000 | 0.146 | 0.225 |
| lift | lift | 0.00 / guard_failure | (0.504, -0.001, 0.136)→(0.503, -0.001, 0.140) | (0.522, -0.001, 0.026)→(0.524, -0.001, 0.131) | 0.289→0.237 | 1.00 / 25.000 | 0.000 | 0.743 |
| transport_to_goal | approach | 0.00 / guard_failure | (0.513, 0.029, 0.222)→(0.513, 0.029, 0.222) | (0.523, -0.001, 0.135)→(0.529, 0.019, 0.183) | 0.236→0.206 | 0.67 / 3.000 | 0.016 | 0.322 |
| descend_to_place | descend | 0.00 / step_budget | (0.513, 0.029, 0.222)→(0.565, 0.133, 0.205) | (0.531, 0.029, 0.193)→(0.523, 0.047, 0.016) | 0.196→0.263 | 1.00 / 8.333 | 91002.467 | 1.912 |
| release | release | 1.00 / step_budget | (0.565, 0.133, 0.205)→(0.560, 0.131, 0.227) | (0.523, 0.047, 0.016)→(0.523, 0.047, 0.016) | 0.263→0.263 | 1.00 / 4.000 | 0.123 | 0.123 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.210
- phase_score: 0.428
- phase_breakdown.lift_object_score: 0.664
- phase_breakdown.grasp_contact_score: 0.783
- phase_breakdown.approach_goal_score: 0.149
- phase_breakdown.approach_object_score: 0.674
- phase_breakdown.final_placement_score: 0.173
- grasp_place_fitness: 0.580

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.580
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.210
- **Median Q (composite search score)**: 0.007
- **K-run variance**: 0.0001
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.325


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.59412,"average_solve_count":170.0,"average_success_count":170.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_speed":0.23476,"descend_to_grasp.descend_speed":0.06166,"descend_to_grasp.force_limit":6.88072,"descend_to_place.descend_place_speed":0.06026,"lift.lift_height":0.23386,"release.release_time":0.61296,"transport_to_goal.transport_arc_height":0.29252,"transport_to_goal.transport_speed":0.06276},"optimized_scores":{"best_composite_score":0.00493,"best_fitness_score":0.55493,"best_task_score":0.15359},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":3659.0,"contact_point_centroid":[0.47024,0.08577,-0.0023],"force_p95":0.12613,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.89378,"mean_force":0.13844,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.50636,0.11747,0.22158]},{"body_a":"world","body_b":"grasp_target","contact_count":75.0,"contact_point_centroid":[0.47943,0.04635,-0.00147],"force_p95":0.80076,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.84257,"mean_force":0.20342,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.46894,0.04697,0.02105]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2512.0,"contact_point_centroid":[0.47183,0.03218,0.18357],"force_p95":0.19697,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.34888,"mean_force":0.10664,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.46614,0.05057,0.18382]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6754.0,"contact_point_centroid":[0.46873,0.06572,0.07829],"force_p95":0.10986,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31676,"mean_force":0.06497,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.46662,0.04674,0.07638]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2453.0,"contact_point_centroid":[0.47183,0.06973,0.18614],"force_p95":0.21316,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30513,"mean_force":0.1136,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.46652,0.05122,0.18655]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6401.0,"contact_point_centroid":[0.46882,0.0278,0.08106],"force_p95":0.1092,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29655,"mean_force":0.06745,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.46662,0.04674,0.07873]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.48275,0.04833,-0.00215],"force_p95":0.16558,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.26836,"mean_force":0.1347,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.47134,0.04723,0.02075]},{"body_a":"world","body_b":"grasp_target","contact_count":1100.0,"contact_point_centroid":[0.4827,0.04873,-0.00188],"force_p95":0.1365,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12307,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.49073,0.02009,0.22535]},{"body_a":"world","body_b":"grasp_target","contact_count":2976.0,"contact_point_centroid":[0.4827,0.04873,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.47827,0.04478,0.08391]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.47013,0.0857,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.52956,0.15698,0.22446]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4980.0,"contact_point_centroid":[0.47005,0.02788,0.0227],"force_p95":0.07123,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10817,"mean_force":0.04305,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.47019,0.04712,0.01961]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5525.0,"contact_point_centroid":[0.46985,0.06647,0.022],"force_p95":0.07004,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08933,"mean_force":0.0414,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.4702,0.04712,0.01962]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":33.0,"contact_point_centroid":[0.47848,0.07661,0.21922],"force_p95":0.03007,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.03136,"mean_force":0.00911,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.47261,0.06163,0.22602]},{"body_a":"left_finger","body_b":"right_finger","contact_count":3713.0,"contact_point_centroid":[0.50847,0.12002,0.22388],"force_p95":0.01106,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01622,"mean_force":0.01048,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.508,0.12,0.22158]},{"body_a":"left_finger","body_b":"right_finger","contact_count":225.0,"contact_point_centroid":[0.53216,0.15776,0.22189],"force_p95":0.01094,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01096,"mean_force":0.00996,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.53176,0.15774,0.21956]}],"total_contact_groups":15},"final_pose_error":0.08661,"key_states":{"actual_goal_position":[0.58187,0.22885,0.23048],"final_object_position":[0.47013,0.0857,0.01602],"final_tcp_position":[0.53294,0.15791,0.22191],"realised_goal_position":[0.58187,0.22885,0.23048],"realised_object_initial_position":[0.4827,0.04873,0.03]},"peak_contact_force":273007.15503,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":276.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.03],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28719,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1100.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_object","tcp_end":[0.48193,0.04168,0.14819],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.12238,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":744.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2976.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_contact","tcp_end":[0.47798,0.0479,0.02741],"tcp_start":[0.48193,0.04168,0.14819],"tcp_to_object_dist_end":0.00498,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":47.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.48255,0.04711,0.0255],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.2914,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.15735,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12305.0,"raw_peak_contact_force":0.26836,"tcp_end":[0.47017,0.04711,0.01958],"tcp_start":[0.47798,0.0479,0.02741],"tcp_to_object_dist_end":0.01373,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":25.0,"n_steps":409.0,"n_steps_budget":1000.0,"object_pos_end":[0.48808,0.0469,0.15088],"object_pos_start":[0.48255,0.04711,0.0255],"object_to_goal_dist_end":0.21964,"object_to_goal_dist_start":0.2914,"object_z_max":0.15205,"peak_contact_force":0.0,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":13230.0,"raw_peak_contact_force":0.84257,"subtask_id":"lift_object","tcp_end":[0.46611,0.04669,0.15299],"tcp_start":[0.46655,0.04673,0.15132],"tcp_to_object_dist_end":0.02207,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":6.0,"n_steps":251.0,"n_steps_budget":1000.0,"object_pos_end":[0.49264,0.06277,0.19878],"object_pos_start":[0.48761,0.04681,0.15235],"object_to_goal_dist_end":0.19118,"object_to_goal_dist_start":0.21939,"object_z_max":0.20167,"peak_contact_force":0.01645,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4965.0,"raw_peak_contact_force":0.34888,"subtask_id":"approach_goal","tcp_end":[0.47253,0.06147,0.22603],"tcp_start":[0.4725,0.06136,0.22585],"tcp_to_object_dist_end":0.03389,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.47013,0.0857,0.01602],"object_pos_start":[0.49218,0.0638,0.1968],"object_to_goal_dist_end":0.28102,"object_to_goal_dist_start":0.19085,"object_z_max":0.1968,"peak_contact_force":273007.15503,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":7405.0,"raw_peak_contact_force":1.89378,"subtask_id":"final_placement","tcp_end":[0.53294,0.15791,0.22191],"tcp_start":[0.47253,0.06147,0.22603],"tcp_to_object_dist_end":0.22705,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.47013,0.0857,0.01602],"object_pos_start":[0.47013,0.0857,0.01602],"object_to_goal_dist_end":0.28102,"object_to_goal_dist_start":0.28102,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1025.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.52831,0.15654,0.24487],"tcp_start":[0.53294,0.15791,0.22191],"tcp_to_object_dist_end":0.24653,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `2b35d39beba75b46a5edd8e67b975c00ef2c88fb75a3753bdd32db5918adf9e2`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.74359,"average_solve_count":156.0,"average_success_count":156.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_speed":0.20274,"descend_to_grasp.descend_speed":0.09617,"descend_to_grasp.force_limit":13.34086,"descend_to_place.descend_place_speed":0.0658,"lift.lift_height":0.18155,"release.release_time":0.71649,"transport_to_goal.transport_arc_height":0.35853,"transport_to_goal.transport_speed":0.04841},"optimized_scores":{"best_composite_score":0.00715,"best_fitness_score":0.55715,"best_task_score":0.16057},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":3627.0,"contact_point_centroid":[0.53985,0.04428,-0.0023],"force_p95":0.13263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.0342,"mean_force":0.13912,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.55564,0.09931,0.2227]},{"body_a":"world","body_b":"grasp_target","contact_count":77.0,"contact_point_centroid":[0.53378,-0.0205,-0.00136],"force_p95":0.71846,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.76617,"mean_force":0.1704,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52135,-0.02073,0.02414]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5185.0,"contact_point_centroid":[0.52162,-0.00176,0.0741],"force_p95":0.11346,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33972,"mean_force":0.07463,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.51867,-0.02067,0.0717]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3495.0,"contact_point_centroid":[0.52522,0.01417,0.18009],"force_p95":0.1736,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32818,"mean_force":0.10537,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.51967,-0.00432,0.1801]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5662.0,"contact_point_centroid":[0.52171,-0.03946,0.07216],"force_p95":0.10977,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31817,"mean_force":0.06979,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.51869,-0.02067,0.07048]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3800.0,"contact_point_centroid":[0.52506,-0.02304,0.17889],"force_p95":0.17116,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30635,"mean_force":0.09987,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.51961,-0.00465,0.17907]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53702,-0.0211,-0.00205],"force_p95":0.13847,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.18433,"mean_force":0.12708,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.5239,-0.02078,0.02427]},{"body_a":"world","body_b":"grasp_target","contact_count":1112.0,"contact_point_centroid":[0.53702,-0.02132,-0.00188],"force_p95":0.13647,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12307,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.51332,-0.00885,0.22471]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.53702,-0.02132,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.52862,-0.01983,0.07657]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.53979,0.04428,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.57224,0.14856,0.21475]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4092.0,"contact_point_centroid":[0.52363,-0.00155,0.02557],"force_p95":0.07736,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11789,"mean_force":0.05179,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.52265,-0.02075,0.02286]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4914.0,"contact_point_centroid":[0.5236,-0.03985,0.02464],"force_p95":0.06929,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08862,"mean_force":0.0448,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.52265,-0.02075,0.02286]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":20.0,"contact_point_centroid":[0.53645,0.00971,0.23523],"force_p95":0.07351,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07403,"mean_force":0.02784,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.52982,0.0276,0.24227]},{"body_a":"left_finger","body_b":"right_finger","contact_count":3730.0,"contact_point_centroid":[0.55719,0.10199,0.22445],"force_p95":0.01096,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01632,"mean_force":0.01039,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.5567,0.10198,0.22217]},{"body_a":"left_finger","body_b":"right_finger","contact_count":228.0,"contact_point_centroid":[0.57499,0.14932,0.21255],"force_p95":0.01088,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0109,"mean_force":0.00981,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.57455,0.14931,0.2105]}],"total_contact_groups":15},"final_pose_error":0.08579,"key_states":{"actual_goal_position":[0.61031,0.22775,0.20741],"final_object_position":[0.53979,0.04428,0.01602],"final_tcp_position":[0.57583,0.14941,0.21324],"realised_goal_position":[0.61031,0.22775,0.20741],"realised_object_initial_position":[0.53702,-0.02132,0.03]},"peak_contact_force":2.0342,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":279.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.03],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31446,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1112.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_object","tcp_end":[0.52852,-0.01826,0.14771],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.12203,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_contact","tcp_end":[0.53103,-0.02091,0.03235],"tcp_start":[0.52852,-0.01826,0.14771],"tcp_to_object_dist_end":0.00873,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53687,-0.02063,0.02582],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31633,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.13473,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10806.0,"raw_peak_contact_force":0.18433,"tcp_end":[0.52262,-0.02075,0.02282],"tcp_start":[0.53103,-0.02091,0.03235],"tcp_to_object_dist_end":0.01456,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":25.0,"n_steps":368.0,"n_steps_budget":1000.0,"object_pos_end":[0.539,-0.02063,0.12512],"object_pos_start":[0.53687,-0.02063,0.02582],"object_to_goal_dist_end":0.27121,"object_to_goal_dist_start":0.31633,"object_z_max":0.13062,"peak_contact_force":0.0,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":10924.0,"raw_peak_contact_force":0.76617,"subtask_id":"lift_object","tcp_end":[0.51709,-0.02062,0.13467],"tcp_start":[0.51847,-0.02065,0.12825],"tcp_to_object_dist_end":0.0239,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":364.0,"n_steps_budget":1000.0,"object_pos_end":[0.54027,-0.00151,0.18002],"object_pos_start":[0.53806,-0.02057,0.13099],"object_to_goal_dist_end":0.24129,"object_to_goal_dist_start":0.26967,"object_z_max":0.21712,"peak_contact_force":0.03138,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":7295.0,"raw_peak_contact_force":0.32818,"subtask_id":"approach_goal","tcp_end":[0.5297,0.02723,0.2423],"tcp_start":[0.52966,0.02696,0.24208],"tcp_to_object_dist_end":0.06941,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53979,0.04428,0.01602],"object_pos_start":[0.54586,0.02617,0.21554],"object_to_goal_dist_end":0.27435,"object_to_goal_dist_start":0.21179,"object_z_max":0.21554,"peak_contact_force":0.12263,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":7377.0,"raw_peak_contact_force":2.0342,"subtask_id":"final_placement","tcp_end":[0.57583,0.14941,0.21324],"tcp_start":[0.5297,0.02723,0.2423],"tcp_to_object_dist_end":0.22638,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53979,0.04428,0.01602],"object_pos_start":[0.53979,0.04428,0.01602],"object_to_goal_dist_end":0.27435,"object_to_goal_dist_start":0.27435,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1028.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.57091,0.14813,0.2347],"tcp_start":[0.57583,0.14941,0.21324],"tcp_to_object_dist_end":0.24408,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `530652a2467d9ac78fab654e7ed7fc5283ca1649270bc8f158e04c16074f9f95`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.61111,"average_solve_count":144.0,"average_success_count":144.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_speed":0.1339,"descend_to_grasp.descend_speed":0.09033,"descend_to_grasp.force_limit":7.26621,"descend_to_place.descend_place_speed":0.04941,"lift.lift_height":0.17268,"release.release_time":0.4697,"transport_to_goal.transport_arc_height":0.30024,"transport_to_goal.transport_speed":0.14106},"optimized_scores":{"best_composite_score":0.02998,"best_fitness_score":0.57998,"best_task_score":0.2096},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":3691.0,"contact_point_centroid":[0.55965,0.01102,-0.00228],"force_p95":0.1265,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.80702,"mean_force":0.13649,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.56487,0.05319,0.1844]},{"body_a":"world","body_b":"grasp_target","contact_count":79.0,"contact_point_centroid":[0.5422,-0.02776,-0.00141],"force_p95":0.58029,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.61918,"mean_force":0.13288,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52923,-0.02809,0.03174]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4636.0,"contact_point_centroid":[0.52984,-0.00911,0.07711],"force_p95":0.11438,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33326,"mean_force":0.07699,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52663,-0.028,0.07466]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5079.0,"contact_point_centroid":[0.52997,-0.04677,0.0757],"force_p95":0.10949,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31698,"mean_force":0.07234,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52666,-0.028,0.07403]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1947.0,"contact_point_centroid":[0.53388,-1e-05,0.16128],"force_p95":0.18936,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28928,"mean_force":0.10725,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.5279,-0.01856,0.16115]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2327.0,"contact_point_centroid":[0.53409,-0.03627,0.16166],"force_p95":0.15807,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28524,"mean_force":0.0961,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.52822,-0.01801,0.16227]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.54564,-0.02899,-0.0021],"force_p95":0.1522,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.22312,"mean_force":0.13048,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.53181,-0.02817,0.03185]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4078.0,"contact_point_centroid":[0.53178,-0.00893,0.03309],"force_p95":0.07951,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13935,"mean_force":0.05185,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.53055,-0.02814,0.03039]},{"body_a":"world","body_b":"grasp_target","contact_count":1216.0,"contact_point_centroid":[0.5456,-0.02923,-0.00189],"force_p95":0.13606,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12303,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.51693,-0.0122,0.22419]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.5456,-0.02923,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.53633,-0.02707,0.08092]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.55962,0.01104,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.58238,0.08999,0.18049]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4964.0,"contact_point_centroid":[0.5317,-0.04726,0.03216],"force_p95":0.07173,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0857,"mean_force":0.04471,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.53056,-0.02814,0.0304]},{"body_a":"left_finger","body_b":"right_finger","contact_count":3706.0,"contact_point_centroid":[0.56664,0.05564,0.18638],"force_p95":0.01101,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01612,"mean_force":0.01053,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.56626,0.05565,0.184]},{"body_a":"left_finger","body_b":"right_finger","contact_count":217.0,"contact_point_centroid":[0.58542,0.09053,0.1785],"force_p95":0.01099,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01271,"mean_force":0.01022,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.58509,0.09053,0.17623]}],"total_contact_groups":14},"final_pose_error":0.08765,"key_states":{"actual_goal_position":[0.63284,0.16493,0.17692],"final_object_position":[0.55962,0.01104,0.01602],"final_tcp_position":[0.58647,0.09058,0.17887],"realised_goal_position":[0.63284,0.16493,0.17692],"realised_object_initial_position":[0.5456,-0.02923,0.03]},"peak_contact_force":191.30921,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":305.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.03],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.25864,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1216.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_object","tcp_end":[0.53611,-0.02518,0.14683],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.12125,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":191.30921,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_contact","tcp_end":[0.53893,-0.02839,0.04021],"tcp_start":[0.53611,-0.02518,0.14683],"tcp_to_object_dist_end":0.0157,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54549,-0.02814,0.02566],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26036,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.14611,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10842.0,"raw_peak_contact_force":0.22312,"tcp_end":[0.53053,-0.02813,0.03036],"tcp_start":[0.53893,-0.02839,0.04021],"tcp_to_object_dist_end":0.01569,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":25.0,"n_steps":340.0,"n_steps_budget":1000.0,"object_pos_end":[0.54494,-0.02805,0.11799],"object_pos_start":[0.54549,-0.02814,0.02566],"object_to_goal_dist_end":0.22009,"object_to_goal_dist_start":0.26036,"object_z_max":0.12138,"peak_contact_force":0.0,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":9794.0,"raw_peak_contact_force":0.61918,"subtask_id":"lift_object","tcp_end":[0.52527,-0.02795,0.13223],"tcp_start":[0.52639,-0.02798,0.12811],"tcp_to_object_dist_end":0.02428,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":223.0,"n_steps_budget":1000.0,"object_pos_end":[0.55395,-0.00416,0.16896],"object_pos_start":[0.54396,-0.02789,0.12175],"object_to_goal_dist_end":0.18675,"object_to_goal_dist_start":0.21937,"object_z_max":0.17249,"peak_contact_force":0.0,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4274.0,"raw_peak_contact_force":0.28928,"subtask_id":"approach_goal","tcp_end":[0.53677,-0.00164,0.19851],"tcp_start":[0.5367,-0.00173,0.19841],"tcp_to_object_dist_end":0.03428,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.55962,0.01104,0.01602],"object_pos_start":[0.55415,-0.00405,0.16791],"object_to_goal_dist_end":0.23438,"object_to_goal_dist_start":0.18662,"object_z_max":0.16791,"peak_contact_force":0.12263,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":7397.0,"raw_peak_contact_force":1.80702,"subtask_id":"final_placement","tcp_end":[0.58647,0.09058,0.17887],"tcp_start":[0.53677,-0.00164,0.19851],"tcp_to_object_dist_end":0.18322,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.55962,0.01104,0.01602],"object_pos_start":[0.55962,0.01104,0.01602],"object_to_goal_dist_end":0.23438,"object_to_goal_dist_start":0.23438,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1017.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.5808,0.08969,0.20048],"tcp_start":[0.58647,0.09058,0.17887],"tcp_to_object_dist_end":0.20164,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```