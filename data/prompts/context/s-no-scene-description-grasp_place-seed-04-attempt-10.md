## Search State

- **Seed**: 4
- **Iteration**: 11 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 10 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 10 | 0.0051 | 0.33 | ❌ rejected |
| 9 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 11 | -0.0583 | 0.36 | ❌ rejected |
| 8 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 11 | -0.0481 | 0.36 | ❌ rejected |
| 7 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | force_threshold_switch | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | force_exceeded | time_limit | 11 | 0.0826 | 0.35 | ❌ rejected |
| 6 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 11 | -0.0525 | 0.37 | ✅ accepted |

**Proposal policy**: task_score is 0.33 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.005) — your mutation base

```yaml
skill: grasp_place
dsl_version: 2
skill_type: arm_gripper
subtasks:
- id: reach_object
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.15
  weight: 0.3
- id: grasp_object
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.03
  weight: 0.3
- id: lift_object
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.15
  weight: 0.2
- id: reach_goal
  offset:
  - 0.0
  - 0.0
  - 0.15
  weight: 0.1
- id: place_goal
  offset:
  - 0.0
  - 0.0
  - 0.05
  weight: 0.1
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
    - 0.15
    orientation:
      mode: keep_current
  parameters:
    approach_speed:
      type: scalar
      range:
      - 0.05
      - 0.4
      default: 0.15
      binds_to:
      - path: generator.speed
        mode: replace
    approach_tolerance:
      type: scalar
      range:
      - 0.005
      - 0.05
      default: 0.02
      binds_to:
      - path: termination.pose_tolerance
        mode: replace
  retries:
    max_attempts: 1
    strategy: offset_target
    offset:
    - 0.0
    - 0.0
    - -0.01
  subtask_id: reach_object
- id: descend_to_object
  type: descend
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.0
    - 0.03
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    descend_speed:
      type: scalar
      range:
      - 0.02
      - 0.2
      default: 0.08
      binds_to:
      - path: generator.speed
        mode: replace
    grasp_height:
      type: scalar
      range:
      - 0.01
      - 0.06
      default: 0.03
      binds_to:
      - path: target.offset.z
        mode: replace
  retries:
    max_attempts: 2
    strategy: reduce_speed
    offset:
    - 0.0
    - 0.0
    - 0.0
  subtask_id: grasp_object
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
  guards:
  - id: grasp_check
    when: after_phase
    predicate: bilateral_grasp
    threshold: 0.0
    on_failure: retry
  retries:
    max_attempts: 1
    strategy: repeat
    offset:
    - 0.0
    - 0.0
    - 0.0
  subtask_id: grasp_object
- id: lift
  type: lift
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
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    lift_height:
      type: scalar
      range:
      - 0.08
      - 0.3
      default: 0.15
      binds_to:
      - path: target.offset.z
        mode: replace
    lift_speed:
      type: scalar
      range:
      - 0.02
      - 0.25
      default: 0.1
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: lift_check
    when: after_phase
    predicate: object_lifted
    threshold: 0.0
    on_failure: retry
  retries:
    max_attempts: 1
    strategy: repeat
    offset:
    - 0.0
    - 0.0
    - 0.0
  subtask_id: lift_object
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
    - 0.05
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    transport_speed:
      type: scalar
      range:
      - 0.05
      - 0.4
      default: 0.12
      binds_to:
      - path: generator.speed
        mode: replace
    transport_tolerance:
      type: scalar
      range:
      - 0.005
      - 0.05
      default: 0.02
      binds_to:
      - path: termination.pose_tolerance
        mode: replace
  guards:
  - id: object_retained
    when: after_phase
    predicate: object_lifted
    threshold: 0.0
    on_failure: retry
  retries:
    max_attempts: 1
    strategy: reduce_speed
    offset:
    - 0.0
    - 0.0
    - 0.0
  subtask_id: reach_goal
- id: lower_to_place
  type: descend
  generator: linear_cartesian
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.05
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    lower_speed:
      type: scalar
      range:
      - 0.02
      - 0.2
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
    place_height:
      type: scalar
      range:
      - 0.02
      - 0.12
      default: 0.05
      binds_to:
      - path: target.offset.z
        mode: replace
  guards:
  - id: object_held_descent
    when: after_phase
    predicate: object_lifted
    threshold: 0.0
    on_failure: retry
  retries:
    max_attempts: 1
    strategy: reduce_speed
    offset:
    - 0.0
    - 0.0
    - 0.0
  subtask_id: place_goal
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
  parameters:
    release_time:
      type: scalar
      range:
      - 0.1
      - 0.5
      default: 0.3
      binds_to:
      - path: duration.max_time
        mode: replace
  retries:
    max_attempts: 0
    strategy: repeat
    offset:
    - 0.0
    - 0.0
    - 0.0
  subtask_id: place_goal

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_object** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.15]
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (replace)
    - approach_tolerance: status=consumed; consumers=termination.pose_tolerance (replace)
  - retries: max_attempts=1, strategy=offset_target, offset=[0.0, 0.0, -0.01]
- **descend_to_object** (`descend`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.03], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - descend_speed: status=consumed; consumers=generator.speed (replace)
    - grasp_height: status=consumed; consumers=target.offset.z (replace)
  - retries: max_attempts=2, strategy=reduce_speed, offset=[0.0, 0.0, 0.0]
- **grasp** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings: none
  - guards:
    - id=grasp_check, when=after_phase, predicate=bilateral_grasp, on_failure=retry, threshold=0.0
  - retries: max_attempts=1, strategy=repeat, offset=[0.0, 0.0, 0.0]
- **lift** (`lift`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.15], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset.z (replace)
    - lift_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=lift_check, when=after_phase, predicate=object_lifted, on_failure=retry, threshold=0.0
  - retries: max_attempts=1, strategy=repeat, offset=[0.0, 0.0, 0.0]
- **transport_to_goal** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.05], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - transport_speed: status=consumed; consumers=generator.speed (replace)
    - transport_tolerance: status=consumed; consumers=termination.pose_tolerance (replace)
  - guards:
    - id=object_retained, when=after_phase, predicate=object_lifted, on_failure=retry, threshold=0.0
  - retries: max_attempts=1, strategy=reduce_speed, offset=[0.0, 0.0, 0.0]
- **lower_to_place** (`descend`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.05], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - lower_speed: status=consumed; consumers=generator.speed (replace)
    - place_height: status=consumed; consumers=target.offset.z (replace)
  - guards:
    - id=object_held_descent, when=after_phase, predicate=object_lifted, on_failure=retry, threshold=0.0
  - retries: max_attempts=1, strategy=reduce_speed, offset=[0.0, 0.0, 0.0]
- **release** (`release`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings:
    - release_time: status=consumed; consumers=duration.max_time (replace)
  - retries: max_attempts=0, strategy=repeat, offset=[0.0, 0.0, 0.0]

## Design Metrics

- **Composite score**: 0.005
- **task_score** (E): 0.331
- **fitness_score**: 0.625  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.620

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_object | 1.00 | 1.00 | 0.0969 |
| descend_to_object | 1.00 | 1.00 | 0.1492 |
| grasp | 1.00 | 1.00 | 0.0133 |
| lift | 1.00 | 1.00 | 0.1076 |
| transport_to_goal | 1.00 | 1.00 | 0.0015 |
| place_at_goal | 1.00 | 1.00 | 0.0771 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.517, 0.003, 0.207) | (0.526, 0.005, 0.030)→(0.526, 0.005, 0.026) | 0.246→0.249 | 1.00 / 4.000 | 35.231 | 0.138 |
| descend_to_object | descend | 1.00 / step_budget | (0.517, 0.003, 0.207)→(0.521, 0.005, 0.058) | (0.526, 0.005, 0.026)→(0.526, 0.005, 0.026) | 0.249→0.249 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp | grasp | 1.00 / step_budget | (0.521, 0.005, 0.058)→(0.512, 0.005, 0.048) | (0.526, 0.005, 0.026)→(0.526, 0.005, 0.026) | 0.249→0.249 | 1.00 / 39.000 | 0.146 | 0.191 |
| lift | lift | 1.00 / step_budget | (0.512, 0.005, 0.048)→(0.521, 0.005, 0.155) | (0.526, 0.005, 0.026)→(0.530, 0.005, 0.128) | 0.249→0.202 | 1.00 / 30.000 | 0.090 | 0.362 |
| transport_to_goal | approach | 1.00 / step_budget | (0.606, 0.166, 0.316)→(0.606, 0.167, 0.316) | (0.530, 0.005, 0.128)→(0.592, 0.125, 0.016) | 0.202→0.177 | 1.00 / 8.333 | 0.123 | 1.867 |
| place_at_goal | descend | 1.00 / step_budget | (0.606, 0.167, 0.316)→(0.608, 0.172, 0.239) | (0.592, 0.125, 0.016)→(0.592, 0.125, 0.016) | 0.177→0.177 | 1.00 / 8.000 | 0.123 | 0.123 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.517
- phase_score: 0.630
- phase_breakdown.place_goal_score: 0.644
- phase_breakdown.reach_goal_score: 0.682
- phase_breakdown.reach_object_score: 0.448
- phase_breakdown.grasp_object_score: 0.720
- phase_breakdown.lift_object_score: 0.625
- grasp_place_fitness: 0.712

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.712
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.517
- **Median Q (composite search score)**: -0.023
- **K-run variance**: 0.0040
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.378


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `104d9d5641b6f93313b49acc931f841aa27a6ce63eca9eff4a16c33838e2c9c3`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.05,0.05],"goal_z_delta":0.15,"object_xy_delta":[0.05,0.05]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `9de75aa839370ff688dada9a37e29517e2f368ed4f09f6a013379103594581cf`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.76866,"average_solve_count":134.0,"average_success_count":134.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_speed":0.25833,"approach_object.approach_tolerance":0.02975,"descend_to_object.descend_speed":0.12283,"descend_to_object.grasp_height":0.01042,"lift.lift_height":0.1356,"lift.lift_speed":0.1938,"place_at_goal.place_height":0.04908,"place_at_goal.place_speed":0.08146,"transport_to_goal.transport_speed":0.25591,"transport_to_goal.transport_tolerance":0.02882},"optimized_scores":{"best_composite_score":-0.02294,"best_fitness_score":0.59706,"best_task_score":0.26794},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":1619.0,"contact_point_centroid":[0.60157,0.079,-0.00264],"force_p95":0.28989,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.95319,"mean_force":0.15345,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.61641,0.11557,0.27966]},{"body_a":"world","body_b":"grasp_target","contact_count":78.0,"contact_point_centroid":[0.54238,0.00099,-0.00133],"force_p95":0.38594,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.40998,"mean_force":0.0809,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52843,0.00082,0.04599]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3319.0,"contact_point_centroid":[0.56146,0.04658,0.17266],"force_p95":0.1214,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30284,"mean_force":0.07727,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.5552,0.02804,0.17186]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5080.0,"contact_point_centroid":[0.53467,0.01974,0.08852],"force_p95":0.10889,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27368,"mean_force":0.06922,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.53162,0.00081,0.08625]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5054.0,"contact_point_centroid":[0.53487,-0.01809,0.08864],"force_p95":0.10825,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27242,"mean_force":0.06959,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.53162,0.00081,0.08632]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2918.0,"contact_point_centroid":[0.55996,0.00724,0.17087],"force_p95":0.14347,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25021,"mean_force":0.0851,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.55383,0.02595,0.16943]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.54431,0.00109,-0.00203],"force_p95":0.1327,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.16079,"mean_force":0.12566,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.53059,0.00087,0.04608]},{"body_a":"world","body_b":"grasp_target","contact_count":564.0,"contact_point_centroid":[0.54431,0.00113,-0.00178],"force_p95":0.13791,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12349,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.51454,0.00039,0.25513]},{"body_a":"world","body_b":"grasp_target","contact_count":1100.0,"contact_point_centroid":[0.54431,0.00113,-0.00199],"force_p95":0.12264,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12264,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_object","phase_type":"descend","tcp_position_centroid":[0.5334,0.00089,0.13054]},{"body_a":"world","body_b":"grasp_target","contact_count":448.0,"contact_point_centroid":[0.60148,0.07907,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":5.0,"phase_name":"place_at_goal","phase_type":"descend","tcp_position_centroid":[0.64281,0.15362,0.29354]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5075.0,"contact_point_centroid":[0.53029,-0.0184,0.04775],"force_p95":0.06561,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09878,"mean_force":0.04307,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.52939,0.00085,0.04469]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5357.0,"contact_point_centroid":[0.52993,0.02008,0.04732],"force_p95":0.06409,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0866,"mean_force":0.04116,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.52939,0.00085,0.04469]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1503.0,"contact_point_centroid":[0.62028,0.12034,0.28792],"force_p95":0.01211,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01645,"mean_force":0.01067,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.6198,0.12033,0.28559]},{"body_a":"left_finger","body_b":"right_finger","contact_count":476.0,"contact_point_centroid":[0.64329,0.15364,0.29562],"force_p95":0.01099,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01266,"mean_force":0.0105,"phase_index":5.0,"phase_name":"place_at_goal","phase_type":"descend","tcp_position_centroid":[0.64281,0.15362,0.29343]}],"total_contact_groups":14},"final_pose_error":0.01983,"key_states":{"actual_goal_position":[0.64762,0.15808,0.1911],"final_object_position":[0.60148,0.07907,0.01602],"final_tcp_position":[0.64398,0.15547,0.2595],"realised_goal_position":[0.64762,0.15808,0.1911],"realised_object_initial_position":[0.54431,0.00113,0.03]},"peak_contact_force":1.95319,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":142.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.03],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.24751,"object_z_max":0.03,"peak_contact_force":0.12264,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":564.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.53063,0.0008,0.20635],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.18084,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":275.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_object","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1100.0,"raw_peak_contact_force":0.12264,"subtask_id":"grasp_object","tcp_end":[0.53821,0.00101,0.05547],"tcp_start":[0.53063,0.0008,0.20635],"tcp_to_object_dist_end":0.03007,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":47.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54422,0.00092,0.02585],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25041,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.13198,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12232.0,"raw_peak_contact_force":0.16079,"subtask_id":"grasp_object","tcp_end":[0.52936,0.00085,0.04465],"tcp_start":[0.53821,0.00101,0.05547],"tcp_to_object_dist_end":0.02396,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":29.0,"n_steps":331.0,"n_steps_budget":600.0,"object_pos_end":[0.55444,0.00081,0.11906],"object_pos_start":[0.54422,0.00092,0.02585],"object_to_goal_dist_end":0.19649,"object_to_goal_dist_start":0.25041,"object_z_max":0.11882,"peak_contact_force":0.08803,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":10212.0,"raw_peak_contact_force":0.40998,"subtask_id":"lift_object","tcp_end":[0.53865,0.00084,0.14226],"tcp_start":[0.52936,0.00085,0.04465],"tcp_to_object_dist_end":0.02806,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":757.0,"n_steps_budget":1000.0,"object_pos_end":[0.60148,0.07907,0.01602],"object_pos_start":[0.55444,0.00081,0.11906],"object_to_goal_dist_end":0.19755,"object_to_goal_dist_start":0.19649,"object_z_max":0.17518,"peak_contact_force":0.12263,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":9359.0,"raw_peak_contact_force":1.95319,"subtask_id":"reach_goal","tcp_end":[0.64188,0.152,0.32333],"tcp_start":[0.6415,0.15087,0.32349],"tcp_to_object_dist_end":0.31842,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":112.0,"n_steps_budget":1000.0,"object_pos_end":[0.60148,0.07907,0.01602],"object_pos_start":[0.60148,0.07907,0.01602],"object_to_goal_dist_end":0.19755,"object_to_goal_dist_start":0.19755,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"place_at_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":924.0,"raw_peak_contact_force":0.12263,"subtask_id":"place_goal","tcp_end":[0.64398,0.15547,0.2595],"tcp_start":[0.64188,0.152,0.32333],"tcp_to_object_dist_end":0.2587,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `349f925163f8e9284ad51ad55d38356f2e3c8deb4dc54e8ff12260e5f6d4b0f8`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.45178,"average_solve_count":197.0,"average_success_count":197.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_speed":0.09848,"approach_object.approach_tolerance":0.04083,"descend_to_object.descend_speed":0.06161,"descend_to_object.grasp_height":0.01775,"lift.lift_height":0.151,"lift.lift_speed":0.05823,"place_at_goal.place_height":0.03216,"place_at_goal.place_speed":0.13171,"transport_to_goal.transport_speed":0.15405,"transport_to_goal.transport_tolerance":0.02763},"optimized_scores":{"best_composite_score":0.09235,"best_fitness_score":0.71235,"best_task_score":0.51669},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":585.0,"contact_point_centroid":[0.5962,0.14228,-0.00368],"force_p95":0.79679,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.79544,"mean_force":0.20743,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.58668,0.15394,0.23446]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4633.0,"contact_point_centroid":[0.52026,0.04703,0.09948],"force_p95":0.12557,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29791,"mean_force":0.08735,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.5189,0.02854,0.10231]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4129.0,"contact_point_centroid":[0.52042,0.00999,0.10268],"force_p95":0.12637,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29708,"mean_force":0.09428,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.5192,0.02856,0.10532]},{"body_a":"world","body_b":"grasp_target","contact_count":97.0,"contact_point_centroid":[0.52886,0.02823,-0.00155],"force_p95":0.26876,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.2953,"mean_force":0.06863,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.51527,0.02838,0.05368]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2635.0,"contact_point_centroid":[0.54607,0.04885,0.17446],"force_p95":0.15499,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2539,"mean_force":0.10649,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.54214,0.06707,0.17799]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53056,0.03062,-0.00219],"force_p95":0.1757,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.23067,"mean_force":0.13648,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.5174,0.02853,0.0536]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2818.0,"contact_point_centroid":[0.54801,0.08846,0.17634],"force_p95":0.13221,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20508,"mean_force":0.09962,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.54382,0.07037,0.18012]},{"body_a":"world","body_b":"grasp_target","contact_count":400.0,"contact_point_centroid":[0.5305,0.03079,-0.00169],"force_p95":0.13815,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12389,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.5091,0.00901,0.26193]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2418.0,"contact_point_centroid":[0.5179,0.0097,0.04981],"force_p95":0.10641,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12927,"mean_force":0.08221,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.51625,0.02846,0.05226]},{"body_a":"world","body_b":"grasp_target","contact_count":596.0,"contact_point_centroid":[0.59641,0.14242,-0.00199],"force_p95":0.12302,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12336,"mean_force":0.12261,"phase_index":5.0,"phase_name":"place_at_goal","phase_type":"descend","tcp_position_centroid":[0.59488,0.17199,0.20302]},{"body_a":"world","body_b":"grasp_target","contact_count":1192.0,"contact_point_centroid":[0.5305,0.03079,-0.00199],"force_p95":0.12264,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12264,"mean_force":0.12261,"phase_index":1.0,"phase_name":"descend_to_object","phase_type":"descend","tcp_position_centroid":[0.52071,0.02436,0.13864]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3658.0,"contact_point_centroid":[0.51857,0.04726,0.05065],"force_p95":0.0985,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10143,"mean_force":0.05959,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.51626,0.02846,0.05227]},{"body_a":"left_finger","body_b":"right_finger","contact_count":397.0,"contact_point_centroid":[0.59042,0.16037,0.24074],"force_p95":0.01427,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01637,"mean_force":0.01122,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.58998,0.16035,0.23861]},{"body_a":"left_finger","body_b":"right_finger","contact_count":634.0,"contact_point_centroid":[0.59523,0.17201,0.20548],"force_p95":0.01102,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01273,"mean_force":0.01048,"phase_index":5.0,"phase_name":"place_at_goal","phase_type":"descend","tcp_position_centroid":[0.59488,0.17198,0.20316]}],"total_contact_groups":14},"final_pose_error":0.01996,"key_states":{"actual_goal_position":[0.60153,0.17858,0.10809],"final_object_position":[0.59642,0.14242,0.01602],"final_tcp_position":[0.59658,0.17515,0.15928],"realised_goal_position":[0.60153,0.17858,0.10809],"realised_object_initial_position":[0.5305,0.03079,0.03]},"peak_contact_force":54.72656,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":101.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.03],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18162,"object_z_max":0.03,"peak_contact_force":54.72656,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":400.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.51896,0.01986,0.21684],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.19149,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":298.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_object","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1192.0,"raw_peak_contact_force":0.12264,"subtask_id":"grasp_object","tcp_end":[0.52477,0.02896,0.06253],"tcp_start":[0.51896,0.01986,0.21684],"tcp_to_object_dist_end":0.037,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":28.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53047,0.02921,0.02528],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18499,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.16901,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":7876.0,"raw_peak_contact_force":0.23067,"subtask_id":"grasp_object","tcp_end":[0.51622,0.02846,0.05223],"tcp_start":[0.52477,0.02896,0.06253],"tcp_to_object_dist_end":0.0305,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":390.0,"n_steps_budget":1000.0,"object_pos_end":[0.52963,0.02913,0.1244],"object_pos_start":[0.53047,0.02921,0.02528],"object_to_goal_dist_end":0.16665,"object_to_goal_dist_start":0.18499,"object_z_max":0.12415,"peak_contact_force":0.10518,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":8859.0,"raw_peak_contact_force":0.29791,"subtask_id":"lift_object","tcp_end":[0.52521,0.02887,0.15716],"tcp_start":[0.51622,0.02846,0.05223],"tcp_to_object_dist_end":0.03306,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":549.0,"n_steps_budget":1000.0,"object_pos_end":[0.59639,0.14231,0.01602],"object_pos_start":[0.52963,0.02913,0.1244],"object_to_goal_dist_end":0.09909,"object_to_goal_dist_start":0.16665,"object_z_max":0.16941,"peak_contact_force":0.12339,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":6435.0,"raw_peak_contact_force":1.79544,"subtask_id":"reach_goal","tcp_end":[0.59399,0.16929,0.24314],"tcp_start":[0.5938,0.1676,0.24352],"tcp_to_object_dist_end":0.22873,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":149.0,"n_steps_budget":1000.0,"object_pos_end":[0.59642,0.14242,0.01602],"object_pos_start":[0.59641,0.1424,0.016],"object_to_goal_dist_end":0.09905,"object_to_goal_dist_start":0.09908,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"place_at_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1230.0,"raw_peak_contact_force":0.12336,"subtask_id":"place_goal","tcp_end":[0.59658,0.17515,0.15928],"tcp_start":[0.59399,0.16929,0.24314],"tcp_to_object_dist_end":0.14695,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `a1798e4fdcacfe8740623adfe3f78d2bc74e0d14c8233e64f02c40cf2a534ecc`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.34091,"average_solve_count":220.0,"average_success_count":220.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_speed":0.25839,"approach_object.approach_tolerance":0.01957,"descend_to_object.descend_speed":0.05013,"descend_to_object.grasp_height":0.01171,"lift.lift_height":0.1602,"lift.lift_speed":0.047,"place_at_goal.place_height":0.03069,"place_at_goal.place_speed":0.13984,"transport_to_goal.transport_speed":0.20091,"transport_to_goal.transport_tolerance":0.02049},"optimized_scores":{"best_composite_score":-0.05413,"best_fitness_score":0.56587,"best_task_score":0.20906},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":928.0,"contact_point_centroid":[0.57774,0.1534,-0.00352],"force_p95":0.72621,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.85327,"mean_force":0.18308,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.57283,0.15738,0.35688]},{"body_a":"world","body_b":"grasp_target","contact_count":86.0,"contact_point_centroid":[0.50041,-0.015,-0.00146],"force_p95":0.36506,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.3773,"mean_force":0.13435,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.49007,-0.01503,0.04853]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":7311.0,"contact_point_centroid":[0.52299,0.01912,0.22232],"force_p95":0.11633,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32143,"mean_force":0.06856,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.51956,0.03781,0.22226]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8046.0,"contact_point_centroid":[0.49297,0.00413,0.10572],"force_p95":0.08008,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26416,"mean_force":0.05692,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.4931,-0.01505,0.10481]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":9032.0,"contact_point_centroid":[0.49278,-0.03416,0.10592],"force_p95":0.07683,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25628,"mean_force":0.05166,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.49311,-0.01505,0.10498]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":7005.0,"contact_point_centroid":[0.52299,0.05712,0.22246],"force_p95":0.12626,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18841,"mean_force":0.07275,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.51978,0.03832,0.22281]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50383,-0.01562,-0.00206],"force_p95":0.13959,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.18079,"mean_force":0.12714,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.49207,-0.01505,0.04871]},{"body_a":"world","body_b":"grasp_target","contact_count":772.0,"contact_point_centroid":[0.50382,-0.01567,-0.00183],"force_p95":0.13759,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12326,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.49972,-0.00592,0.25076]},{"body_a":"world","body_b":"grasp_target","contact_count":580.0,"contact_point_centroid":[0.57769,0.15336,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12264,"mean_force":0.12263,"phase_index":5.0,"phase_name":"place_at_goal","phase_type":"descend","tcp_position_centroid":[0.58362,0.18238,0.34151]},{"body_a":"world","body_b":"grasp_target","contact_count":1140.0,"contact_point_centroid":[0.50382,-0.01567,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_object","phase_type":"descend","tcp_position_centroid":[0.49877,-0.01376,0.12839]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4352.0,"contact_point_centroid":[0.49146,0.00415,0.04889],"force_p95":0.07344,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11533,"mean_force":0.04946,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.49095,-0.01503,0.0475]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4903.0,"contact_point_centroid":[0.49141,-0.03417,0.04872],"force_p95":0.06955,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08761,"mean_force":0.04456,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.49095,-0.01503,0.04751]},{"body_a":"left_finger","body_b":"right_finger","contact_count":872.0,"contact_point_centroid":[0.57466,0.16035,0.36257],"force_p95":0.01276,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01626,"mean_force":0.01073,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.57417,0.16034,0.36022]},{"body_a":"left_finger","body_b":"right_finger","contact_count":624.0,"contact_point_centroid":[0.58403,0.18239,0.34377],"force_p95":0.01096,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01099,"mean_force":0.01037,"phase_index":5.0,"phase_name":"place_at_goal","phase_type":"descend","tcp_position_centroid":[0.58362,0.18238,0.34155]}],"total_contact_groups":14},"final_pose_error":0.01953,"key_states":{"actual_goal_position":[0.58691,0.18745,0.24812],"final_object_position":[0.57769,0.15336,0.01602],"final_tcp_position":[0.58455,0.18492,0.29803],"realised_goal_position":[0.58691,0.18745,0.24812],"realised_object_initial_position":[0.50382,-0.01567,0.03]},"peak_contact_force":9748.85358,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":194.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.03],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.30942,"object_z_max":0.03,"peak_contact_force":50.84481,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":772.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.50028,-0.01247,0.19861],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.17266,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":285.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.12262,"phase_name":"descend_to_object","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1140.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_object","tcp_end":[0.49924,-0.01512,0.05677],"tcp_start":[0.50028,-0.01247,0.19861],"tcp_to_object_dist_end":0.0311,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":42.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50374,-0.0152,0.02578],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31212,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.13827,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11055.0,"raw_peak_contact_force":0.18079,"subtask_id":"grasp_object","tcp_end":[0.49092,-0.01503,0.04747],"tcp_start":[0.49924,-0.01512,0.05677],"tcp_to_object_dist_end":0.0252,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":38.0,"n_steps":425.0,"n_steps_budget":1000.0,"object_pos_end":[0.50707,-0.01524,0.14193],"object_pos_start":[0.50374,-0.0152,0.02578],"object_to_goal_dist_end":0.24235,"object_to_goal_dist_start":0.31212,"object_z_max":0.14166,"peak_contact_force":0.07798,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":17164.0,"raw_peak_contact_force":0.3773,"subtask_id":"lift_object","tcp_end":[0.49889,-0.01512,0.16671],"tcp_start":[0.49092,-0.01503,0.04747],"tcp_to_object_dist_end":0.0261,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":864.0,"n_steps_budget":1000.0,"object_pos_end":[0.57769,0.15336,0.01602],"object_pos_start":[0.50707,-0.01524,0.14193],"object_to_goal_dist_end":0.23477,"object_to_goal_dist_start":0.24235,"object_z_max":0.26284,"peak_contact_force":0.12264,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":16116.0,"raw_peak_contact_force":1.85327,"subtask_id":"reach_goal","tcp_end":[0.58272,0.18011,0.38108],"tcp_start":[0.58243,0.17869,0.38089],"tcp_to_object_dist_end":0.36607,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":145.0,"n_steps_budget":1000.0,"object_pos_end":[0.57769,0.15336,0.01602],"object_pos_start":[0.57769,0.15336,0.01602],"object_to_goal_dist_end":0.23477,"object_to_goal_dist_start":0.23477,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"place_at_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1204.0,"raw_peak_contact_force":0.12264,"subtask_id":"place_goal","tcp_end":[0.58455,0.18492,0.29803],"tcp_start":[0.58272,0.18011,0.38108],"tcp_to_object_dist_end":0.28385,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```