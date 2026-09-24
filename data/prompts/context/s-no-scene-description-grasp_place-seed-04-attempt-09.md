## Search State

- **Seed**: 4
- **Iteration**: 10 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 9 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 11 | -0.0583 | 0.36 | ❌ rejected |
| 8 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 11 | -0.0481 | 0.36 | ❌ rejected |
| 7 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | force_threshold_switch | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | force_exceeded | time_limit | 11 | 0.0826 | 0.35 | ❌ rejected |
| 6 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 11 | -0.0525 | 0.37 | ✅ accepted |
| 5 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 10 | -0.0091 | 0.36 | ✅ accepted |

**Proposal policy**: task_score is 0.36 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=-0.058) — your mutation base

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

- **Composite score**: -0.058
- **task_score** (E): 0.358
- **fitness_score**: 0.642  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.700

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_object | 1.00 | 1.00 | 0.1139 |
| descend_to_object | 1.00 | 1.00 | 0.1352 |
| grasp | 1.00 | 1.00 | 0.0134 |
| lift | 1.00 | 1.00 | 0.1192 |
| transport_to_goal | 1.00 | 1.00 | 0.0518 |
| lower_to_place | 1.00 | 1.00 | 0.0059 |
| release | 1.00 | 1.00 | 0.0205 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.520, 0.005, 0.191) | (0.526, 0.005, 0.030)→(0.526, 0.005, 0.026) | 0.246→0.249 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_to_object | descend | 1.00 / step_budget | (0.520, 0.005, 0.191)→(0.521, 0.005, 0.056) | (0.526, 0.005, 0.026)→(0.526, 0.005, 0.026) | 0.249→0.249 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp | grasp | 1.00 / step_budget | (0.521, 0.005, 0.056)→(0.513, 0.005, 0.046) | (0.526, 0.005, 0.026)→(0.526, 0.005, 0.026) | 0.249→0.249 | 1.00 / 44.333 | 0.143 | 0.185 |
| lift | lift | 1.00 / step_budget | (0.513, 0.005, 0.046)→(0.521, 0.005, 0.165) | (0.526, 0.005, 0.026)→(0.536, 0.005, 0.139) | 0.249→0.204 | 1.00 / 24.667 | 0.101 | 0.417 |
| transport_to_goal | approach | 1.00 / step_budget | (0.581, 0.118, 0.232)→(0.603, 0.163, 0.221) | (0.536, 0.005, 0.139)→(0.602, 0.143, 0.049) | 0.204→0.148 | 1.00 / 11.333 | 94246.354 | 1.314 |
| lower_to_place | descend | 1.00 / step_budget | (0.604, 0.166, 0.207)→(0.604, 0.167, 0.201) | (0.602, 0.143, 0.050)→(0.603, 0.144, 0.049) | 0.146→0.145 | 1.00 / 10.667 | 90998.861 | 0.195 |
| release | release | 1.00 / step_budget | (0.604, 0.167, 0.201)→(0.599, 0.165, 0.221) | (0.603, 0.144, 0.049)→(0.597, 0.142, 0.020) | 0.145→0.168 | 1.00 / 3.333 | 0.134 | 0.451 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.566
- phase_score: 0.676
- phase_breakdown.place_goal_score: 0.265
- phase_breakdown.reach_goal_score: 0.673
- phase_breakdown.reach_object_score: 0.700
- phase_breakdown.grasp_object_score: 0.671
- phase_breakdown.lift_object_score: 0.855
- grasp_place_fitness: 0.745

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.745
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.566
- **Median Q (composite search score)**: -0.081
- **K-run variance**: 0.0059
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.294


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.51974,"average_solve_count":152.0,"average_success_count":152.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_speed":0.27449,"approach_object.approach_tolerance":0.00666,"descend_to_object.descend_speed":0.09606,"descend_to_object.grasp_height":0.0104,"lift.lift_height":0.16693,"lift.lift_speed":0.15691,"lower_to_place.lower_speed":0.11832,"lower_to_place.place_height":0.0056,"release.release_time":0.28527,"transport_to_goal.transport_speed":0.22941,"transport_to_goal.transport_tolerance":0.02395},"optimized_scores":{"best_composite_score":-0.08117,"best_fitness_score":0.61883,"best_task_score":0.31011},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":257.0,"contact_point_centroid":[0.65104,0.14493,-0.00623],"force_p95":1.0743,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.85027,"mean_force":0.31033,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.635,0.14323,0.22609]},{"body_a":"world","body_b":"grasp_target","contact_count":78.0,"contact_point_centroid":[0.54235,0.00098,-0.00132],"force_p95":0.4216,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.4471,"mean_force":0.08836,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.529,0.00085,0.04592]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6006.0,"contact_point_centroid":[0.53541,-0.01811,0.1013],"force_p95":0.11163,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29822,"mean_force":0.07099,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.53217,0.00083,0.0993]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6338.0,"contact_point_centroid":[0.53547,0.01972,0.10153],"force_p95":0.10645,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2974,"mean_force":0.06807,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.53218,0.00083,0.0995]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3731.0,"contact_point_centroid":[0.57666,0.03104,0.18829],"force_p95":0.15336,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26435,"mean_force":0.09535,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.57085,0.04966,0.18899]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4420.0,"contact_point_centroid":[0.5795,0.07201,0.18941],"force_p95":0.12817,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20336,"mean_force":0.08182,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.57354,0.05368,0.19049]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.5443,0.00109,-0.00203],"force_p95":0.13179,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.1535,"mean_force":0.12542,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.53126,0.00089,0.04602]},{"body_a":"world","body_b":"grasp_target","contact_count":2252.0,"contact_point_centroid":[0.54431,0.00113,-0.00194],"force_p95":0.13153,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12284,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.51811,0.0005,0.23798]},{"body_a":"world","body_b":"grasp_target","contact_count":216.0,"contact_point_centroid":[0.65191,0.14499,-0.00181],"force_p95":0.12669,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12703,"mean_force":0.11653,"phase_index":5.0,"phase_name":"lower_to_place","phase_type":"descend","tcp_position_centroid":[0.63932,0.15073,0.21757]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.65191,0.14497,-0.00199],"force_p95":0.12376,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12476,"mean_force":0.12274,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.63614,0.15139,0.20579]},{"body_a":"world","body_b":"grasp_target","contact_count":944.0,"contact_point_centroid":[0.54431,0.00113,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_object","phase_type":"descend","tcp_position_centroid":[0.53763,0.00101,0.11943]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5074.0,"contact_point_centroid":[0.5307,-0.01838,0.0477],"force_p95":0.06549,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10527,"mean_force":0.04307,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.53007,0.00087,0.04461]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5367.0,"contact_point_centroid":[0.53037,0.02011,0.0473],"force_p95":0.06391,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08614,"mean_force":0.0411,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.53007,0.00087,0.04462]},{"body_a":"left_finger","body_b":"right_finger","contact_count":52.0,"contact_point_centroid":[0.63849,0.14821,0.2298],"force_p95":0.0156,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0156,"mean_force":0.01355,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.63778,0.14819,0.22712]},{"body_a":"left_finger","body_b":"right_finger","contact_count":234.0,"contact_point_centroid":[0.6401,0.15076,0.21979],"force_p95":0.01196,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0127,"mean_force":0.0107,"phase_index":5.0,"phase_name":"lower_to_place","phase_type":"descend","tcp_position_centroid":[0.63931,0.15074,0.2175]},{"body_a":"left_finger","body_b":"right_finger","contact_count":227.0,"contact_point_centroid":[0.6392,0.15215,0.20471],"force_p95":0.01088,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01091,"mean_force":0.00983,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.63849,0.15213,0.20251]}],"total_contact_groups":16},"final_pose_error":0.01375,"key_states":{"actual_goal_position":[0.64762,0.15808,0.1911],"final_object_position":[0.65191,0.14497,0.01602],"final_tcp_position":[0.64009,0.1524,0.2067],"realised_goal_position":[0.64762,0.15808,0.1911],"realised_object_initial_position":[0.54431,0.00113,0.03]},"peak_contact_force":9748.33045,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":564.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.03],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.24751,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2252.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.53778,0.00101,0.18109],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.15521,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":236.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_object","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":944.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_object","tcp_end":[0.53892,0.00103,0.05543],"tcp_start":[0.53778,0.00101,0.18109],"tcp_to_object_dist_end":0.0299,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":47.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54422,0.00093,0.02586],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.2504,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.13116,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12241.0,"raw_peak_contact_force":0.1535,"subtask_id":"grasp_object","tcp_end":[0.53004,0.00087,0.04458],"tcp_start":[0.53892,0.00103,0.05543],"tcp_to_object_dist_end":0.02348,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":26.0,"n_steps":402.0,"n_steps_budget":600.0,"object_pos_end":[0.55531,0.00095,0.14792],"object_pos_start":[0.54422,0.00093,0.02586],"object_to_goal_dist_end":0.18729,"object_to_goal_dist_start":0.2504,"object_z_max":0.14767,"peak_contact_force":0.09562,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":12422.0,"raw_peak_contact_force":0.4471,"subtask_id":"lift_object","tcp_end":[0.53945,0.00086,0.17343],"tcp_start":[0.53004,0.00087,0.04458],"tcp_to_object_dist_end":0.03004,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":523.0,"n_steps_budget":1000.0,"object_pos_end":[0.65244,0.14646,0.01136],"object_pos_start":[0.55531,0.00095,0.14792],"object_to_goal_dist_end":0.18018,"object_to_goal_dist_start":0.18729,"object_z_max":0.17605,"peak_contact_force":9748.33045,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":8460.0,"raw_peak_contact_force":1.85027,"subtask_id":"reach_goal","tcp_end":[0.63826,0.14884,0.2271],"tcp_start":[0.63779,0.1471,0.22789],"tcp_to_object_dist_end":0.21622,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":54.0,"n_steps_budget":1000.0,"object_pos_end":[0.65188,0.14484,0.01633],"object_pos_start":[0.65205,0.14533,0.01612],"object_to_goal_dist_end":0.17532,"object_to_goal_dist_start":0.17551,"object_z_max":0.01665,"peak_contact_force":0.1249,"phase_name":"lower_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":450.0,"raw_peak_contact_force":0.12703,"subtask_id":"place_goal","tcp_end":[0.64009,0.1524,0.2067],"tcp_start":[0.64041,0.15169,0.21367],"tcp_to_object_dist_end":0.19088,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.65191,0.14497,0.01602],"object_pos_start":[0.65189,0.1449,0.01606],"object_to_goal_dist_end":0.17563,"object_to_goal_dist_start":0.17559,"object_z_max":0.01606,"peak_contact_force":0.12263,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1027.0,"raw_peak_contact_force":0.12476,"subtask_id":"place_goal","tcp_end":[0.63477,0.15095,0.22499],"tcp_start":[0.64009,0.1524,0.2067],"tcp_to_object_dist_end":0.20976,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `349f925163f8e9284ad51ad55d38356f2e3c8deb4dc54e8ff12260e5f6d4b0f8`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.73913,"average_solve_count":115.0,"average_success_count":115.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_speed":0.20631,"approach_object.approach_tolerance":0.01821,"descend_to_object.descend_speed":0.12569,"descend_to_object.grasp_height":0.01109,"lift.lift_height":0.17984,"lift.lift_speed":0.11893,"lower_to_place.lower_speed":0.08978,"lower_to_place.place_height":0.03934,"release.release_time":0.33454,"transport_to_goal.transport_speed":0.22414,"transport_to_goal.transport_tolerance":0.02549},"optimized_scores":{"best_composite_score":0.04488,"best_fitness_score":0.74488,"best_task_score":0.56576},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":162.0,"contact_point_centroid":[0.58581,0.16239,-0.00714],"force_p95":1.05001,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.10492,"mean_force":0.40968,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.58486,0.16365,0.15978]},{"body_a":"world","body_b":"grasp_target","contact_count":83.0,"contact_point_centroid":[0.5286,0.02865,-0.00145],"force_p95":0.37928,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.41893,"mean_force":0.08211,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.51549,0.02902,0.04743]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":160.0,"contact_point_centroid":[0.59504,0.18197,0.14843],"force_p95":0.21969,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33484,"mean_force":0.12965,"phase_index":5.0,"phase_name":"lower_to_place","phase_type":"descend","tcp_position_centroid":[0.59045,0.16389,0.15195]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":504.0,"contact_point_centroid":[0.59387,0.18325,0.142],"force_p95":0.14853,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32511,"mean_force":0.10162,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.58883,0.16501,0.14593]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":503.0,"contact_point_centroid":[0.59328,0.14678,0.142],"force_p95":0.1378,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32163,"mean_force":0.09644,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.58878,0.16499,0.14583]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":162.0,"contact_point_centroid":[0.59509,0.14575,0.14872],"force_p95":0.16811,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29106,"mean_force":0.11664,"phase_index":5.0,"phase_name":"lower_to_place","phase_type":"descend","tcp_position_centroid":[0.59044,0.16382,0.15205]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":7196.0,"contact_point_centroid":[0.522,0.04787,0.107],"force_p95":0.10982,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28456,"mean_force":0.06921,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.51855,0.02904,0.10545]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3766.0,"contact_point_centroid":[0.55971,0.07004,0.16884],"force_p95":0.15063,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28336,"mean_force":0.09477,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.5538,0.08869,0.16946]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6488.0,"contact_point_centroid":[0.522,0.01015,0.10963],"force_p95":0.11274,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26903,"mean_force":0.07418,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.51881,0.02905,0.10859]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4312.0,"contact_point_centroid":[0.56176,0.1107,0.16815],"force_p95":0.1234,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24335,"mean_force":0.08086,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.55566,0.09249,0.16858]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53056,0.03067,-0.00215],"force_p95":0.163,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.22175,"mean_force":0.13327,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.51773,0.02918,0.04727]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4332.0,"contact_point_centroid":[0.51713,0.00985,0.04764],"force_p95":0.07774,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13909,"mean_force":0.04967,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.51656,0.0291,0.04594]},{"body_a":"world","body_b":"grasp_target","contact_count":908.0,"contact_point_centroid":[0.5305,0.03079,-0.00186],"force_p95":0.13709,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12317,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.51017,0.01211,0.24833]},{"body_a":"world","body_b":"grasp_target","contact_count":1024.0,"contact_point_centroid":[0.5305,0.03079,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_object","phase_type":"descend","tcp_position_centroid":[0.52278,0.02739,0.12601]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5513.0,"contact_point_centroid":[0.5178,0.04827,0.04832],"force_p95":0.07025,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0721,"mean_force":0.04035,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.51657,0.0291,0.04595]}],"total_contact_groups":15},"final_pose_error":0.01711,"key_states":{"actual_goal_position":[0.60153,0.17858,0.10809],"final_object_position":[0.57928,0.16185,0.02732],"final_tcp_position":[0.5911,0.16528,0.1501],"realised_goal_position":[0.60153,0.17858,0.10809],"realised_object_initial_position":[0.5305,0.03079,0.03]},"peak_contact_force":1.10492,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":228.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.03],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18162,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":908.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.52224,0.02529,0.19485],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.16913,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":256.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.12262,"phase_name":"descend_to_object","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1024.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_object","tcp_end":[0.5252,0.02965,0.05626],"tcp_start":[0.52224,0.02529,0.19485],"tcp_to_object_dist_end":0.03072,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53047,0.02957,0.02548],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.1846,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.16,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11645.0,"raw_peak_contact_force":0.22175,"subtask_id":"grasp_object","tcp_end":[0.51653,0.0291,0.04591],"tcp_start":[0.5252,0.02965,0.05626],"tcp_to_object_dist_end":0.02473,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":25.0,"n_steps":462.0,"n_steps_budget":840.0,"object_pos_end":[0.54017,0.02992,0.15932],"object_pos_start":[0.53047,0.02957,0.02548],"object_to_goal_dist_end":0.16878,"object_to_goal_dist_start":0.1846,"object_z_max":0.15907,"peak_contact_force":0.10135,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":13767.0,"raw_peak_contact_force":0.41893,"subtask_id":"lift_object","tcp_end":[0.52586,0.0293,0.18612],"tcp_start":[0.51653,0.0291,0.04591],"tcp_to_object_dist_end":0.03039,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":17.0,"n_steps":362.0,"n_steps_budget":1000.0,"object_pos_end":[0.5938,0.16375,0.11925],"object_pos_start":[0.54017,0.02992,0.15932],"object_to_goal_dist_end":0.02011,"object_to_goal_dist_start":0.16878,"object_z_max":0.1595,"peak_contact_force":0.13951,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":8078.0,"raw_peak_contact_force":0.28336,"subtask_id":"reach_goal","tcp_end":[0.59062,0.16274,0.1534],"tcp_start":[0.52586,0.0293,0.18612],"tcp_to_object_dist_end":0.03431,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":15.0,"n_steps":20.0,"n_steps_budget":1000.0,"object_pos_end":[0.59556,0.16686,0.11588],"object_pos_start":[0.5938,0.16375,0.11925],"object_to_goal_dist_end":0.01529,"object_to_goal_dist_start":0.02011,"object_z_max":0.11925,"peak_contact_force":0.14338,"phase_name":"lower_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":322.0,"raw_peak_contact_force":0.33484,"subtask_id":"place_goal","tcp_end":[0.5911,0.16528,0.1501],"tcp_start":[0.59062,0.16274,0.1534],"tcp_to_object_dist_end":0.03454,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.57928,0.16185,0.02732],"object_pos_start":[0.59556,0.16686,0.11588],"object_to_goal_dist_end":0.08544,"object_to_goal_dist_start":0.01529,"object_z_max":0.11588,"peak_contact_force":0.15787,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1169.0,"raw_peak_contact_force":1.10492,"subtask_id":"place_goal","tcp_end":[0.58477,0.16363,0.17064],"tcp_start":[0.5911,0.16528,0.1501],"tcp_to_object_dist_end":0.14344,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `a1798e4fdcacfe8740623adfe3f78d2bc74e0d14c8233e64f02c40cf2a534ecc`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.47619,"average_solve_count":147.0,"average_success_count":147.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_speed":0.24294,"approach_object.approach_tolerance":0.01801,"descend_to_object.descend_speed":0.15162,"descend_to_object.grasp_height":0.01064,"lift.lift_height":0.12757,"lift.lift_speed":0.10586,"lower_to_place.lower_speed":0.07886,"lower_to_place.place_height":-0.01337,"release.release_time":0.12017,"transport_to_goal.transport_speed":0.26663,"transport_to_goal.transport_tolerance":0.02723},"optimized_scores":{"best_composite_score":-0.13862,"best_fitness_score":0.56138,"best_task_score":0.19757},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":1203.0,"contact_point_centroid":[0.56036,0.1192,-0.00289],"force_p95":0.43799,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.80695,"mean_force":0.16924,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.56451,0.14121,0.25403]},{"body_a":"world","body_b":"grasp_target","contact_count":76.0,"contact_point_centroid":[0.50189,-0.01496,-0.00137],"force_p95":0.34134,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.38545,"mean_force":0.0881,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.4901,-0.01505,0.04785]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4761.0,"contact_point_centroid":[0.49449,0.00398,0.08749],"force_p95":0.10645,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27156,"mean_force":0.06525,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.49271,-0.01507,0.0861]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5246.0,"contact_point_centroid":[0.49439,-0.03405,0.08713],"force_p95":0.10056,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26136,"mean_force":0.06022,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.49268,-0.01507,0.08569]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3267.0,"contact_point_centroid":[0.51948,0.00676,0.16295],"force_p95":0.14337,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24622,"mean_force":0.08607,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.51344,0.02536,0.1625]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3492.0,"contact_point_centroid":[0.52113,0.04781,0.16558],"force_p95":0.12141,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23935,"mean_force":0.08263,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.51511,0.02928,0.16551]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50383,-0.01561,-0.00206],"force_p95":0.13914,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.17988,"mean_force":0.12706,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.49214,-0.01508,0.04772]},{"body_a":"world","body_b":"grasp_target","contact_count":832.0,"contact_point_centroid":[0.50382,-0.01567,-0.00184],"force_p95":0.13728,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12321,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.49962,-0.00602,0.24988]},{"body_a":"world","body_b":"grasp_target","contact_count":1024.0,"contact_point_centroid":[0.50382,-0.01567,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_object","phase_type":"descend","tcp_position_centroid":[0.49894,-0.01389,0.12676]},{"body_a":"world","body_b":"grasp_target","contact_count":324.0,"contact_point_centroid":[0.56048,0.11962,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":5.0,"phase_name":"lower_to_place","phase_type":"descend","tcp_position_centroid":[0.58147,0.18101,0.26482]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.56048,0.11962,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.57859,0.18188,0.2472]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4353.0,"contact_point_centroid":[0.49153,0.00412,0.04823],"force_p95":0.07356,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1147,"mean_force":0.04944,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.49102,-0.01506,0.04651]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4902.0,"contact_point_centroid":[0.49148,-0.0342,0.04803],"force_p95":0.06956,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08762,"mean_force":0.04457,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.49102,-0.01506,0.04652]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1110.0,"contact_point_centroid":[0.56754,0.14724,0.26109],"force_p95":0.01235,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01607,"mean_force":0.01063,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.56721,0.14723,0.25882]},{"body_a":"left_finger","body_b":"right_finger","contact_count":218.0,"contact_point_centroid":[0.58076,0.18267,0.24554],"force_p95":0.01101,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01274,"mean_force":0.01021,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.58051,0.18264,0.24306]},{"body_a":"left_finger","body_b":"right_finger","contact_count":347.0,"contact_point_centroid":[0.58172,0.18099,0.26744],"force_p95":0.01098,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01101,"mean_force":0.01041,"phase_index":5.0,"phase_name":"lower_to_place","phase_type":"descend","tcp_position_centroid":[0.58146,0.18097,0.26514]}],"total_contact_groups":16},"final_pose_error":0.01371,"key_states":{"actual_goal_position":[0.58691,0.18745,0.24812],"final_object_position":[0.56048,0.11962,0.01602],"final_tcp_position":[0.5819,0.18302,0.24671],"realised_goal_position":[0.58691,0.18745,0.24812],"realised_object_initial_position":[0.50382,-0.01567,0.03]},"peak_contact_force":272996.3155,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":209.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.03],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.30942,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":832.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.50021,-0.01269,0.19696],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.17101,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":256.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.12262,"phase_name":"descend_to_object","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1024.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_object","tcp_end":[0.49939,-0.01515,0.05588],"tcp_start":[0.50021,-0.01269,0.19696],"tcp_to_object_dist_end":0.03019,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":42.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50374,-0.01521,0.02578],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31212,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.13777,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11055.0,"raw_peak_contact_force":0.17988,"subtask_id":"grasp_object","tcp_end":[0.49099,-0.01506,0.04648],"tcp_start":[0.49939,-0.01515,0.05588],"tcp_to_object_dist_end":0.02431,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":287.0,"n_steps_budget":660.0,"object_pos_end":[0.51328,-0.01528,0.11032],"object_pos_start":[0.50374,-0.01521,0.02578],"object_to_goal_dist_end":0.25595,"object_to_goal_dist_start":0.31212,"object_z_max":0.11006,"peak_contact_force":0.10569,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":10083.0,"raw_peak_contact_force":0.38545,"subtask_id":"lift_object","tcp_end":[0.49826,-0.01513,0.13416],"tcp_start":[0.49099,-0.01506,0.04648],"tcp_to_object_dist_end":0.02818,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":691.0,"n_steps_budget":1000.0,"object_pos_end":[0.56048,0.11962,0.01602],"object_pos_start":[0.51328,-0.01528,0.11032],"object_to_goal_dist_end":0.24325,"object_to_goal_dist_start":0.25595,"object_z_max":0.16595,"peak_contact_force":272990.59075,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":9072.0,"raw_peak_contact_force":1.80695,"subtask_id":"reach_goal","tcp_end":[0.58065,0.17865,0.2824],"tcp_start":[0.58051,0.17706,0.28253],"tcp_to_object_dist_end":0.27359,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":81.0,"n_steps_budget":1000.0,"object_pos_end":[0.56048,0.11962,0.01602],"object_pos_start":[0.56048,0.11962,0.01602],"object_to_goal_dist_end":0.24325,"object_to_goal_dist_start":0.24325,"object_z_max":0.01602,"peak_contact_force":272996.3155,"phase_name":"lower_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":671.0,"raw_peak_contact_force":0.12263,"subtask_id":"place_goal","tcp_end":[0.5819,0.18302,0.24671],"tcp_start":[0.58234,0.18259,0.25315],"tcp_to_object_dist_end":0.2402,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.56048,0.11962,0.01602],"object_pos_start":[0.56048,0.11962,0.01602],"object_to_goal_dist_end":0.24325,"object_to_goal_dist_start":0.24325,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1018.0,"raw_peak_contact_force":0.12263,"subtask_id":"place_goal","tcp_end":[0.57751,0.18143,0.26702],"tcp_start":[0.5819,0.18302,0.24671],"tcp_to_object_dist_end":0.25906,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```