## Search State

- **Seed**: 4
- **Iteration**: 7 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 6 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 11 | -0.0525 | 0.37 | ✅ accepted |
| 5 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 10 | -0.0091 | 0.36 | ✅ accepted |
| 4 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | force_threshold_switch | position_control | impedance_control | position_control | impedance_control | position_control | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 8 | -0.1853 | 0.20 | ❌ rejected |
| 3 | push → align → release → insert → lift | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | impedance_control | position_control | admittance_control | impedance_control | position_control | time_limit | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 6 | 0.0580 | 0.20 | ❌ rejected |
| 2 | push → align → release → insert → lift | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | impedance_control | position_control | admittance_control | impedance_control | position_control | time_limit | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 6 | 0.0580 | 0.20 | ❌ rejected |

**Proposal policy**: task_score is 0.37 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=-0.053) — your mutation base

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

- **Composite score**: -0.053
- **task_score** (E): 0.368
- **fitness_score**: 0.647  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.700

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_object | 1.00 | 1.00 | 0.0996 |
| descend_to_object | 1.00 | 1.00 | 0.1497 |
| grasp | 1.00 | 1.00 | 0.0133 |
| lift | 1.00 | 1.00 | 0.1206 |
| transport_to_goal | 1.00 | 1.00 | 0.1285 |
| lower_to_place | 1.00 | 0.67 | 0.0159 |
| release | 1.00 | 1.00 | 0.0207 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.520, 0.005, 0.205) | (0.526, 0.005, 0.030)→(0.526, 0.005, 0.026) | 0.246→0.249 | 1.00 / 4.000 | 0.122 | 0.138 |
| descend_to_object | descend | 1.00 / step_budget | (0.520, 0.005, 0.205)→(0.521, 0.005, 0.055) | (0.526, 0.005, 0.026)→(0.526, 0.005, 0.026) | 0.249→0.249 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp | grasp | 1.00 / step_budget | (0.521, 0.005, 0.055)→(0.512, 0.005, 0.045) | (0.526, 0.005, 0.026)→(0.526, 0.005, 0.026) | 0.249→0.249 | 1.00 / 45.667 | 0.146 | 0.195 |
| lift | lift | 1.00 / step_budget | (0.512, 0.005, 0.045)→(0.521, 0.005, 0.165) | (0.526, 0.005, 0.026)→(0.534, 0.005, 0.141) | 0.249→0.199 | 1.00 / 30.667 | 0.095 | 0.435 |
| transport_to_goal | approach | 1.00 / step_budget | (0.554, 0.054, 0.190)→(0.603, 0.163, 0.221) | (0.534, 0.005, 0.141)→(0.605, 0.156, 0.127) | 0.199→0.069 | 1.00 / 13.667 | 0.148 | 0.739 |
| lower_to_place | descend | 1.00 / step_budget | (0.605, 0.165, 0.232)→(0.607, 0.171, 0.246) | (0.605, 0.156, 0.127)→(0.606, 0.153, 0.086) | 0.069→0.119 | 0.67 / 8.333 | 3249.660 | 0.254 |
| release | release | 1.00 / step_budget | (0.607, 0.171, 0.246)→(0.603, 0.170, 0.266) | (0.606, 0.153, 0.086)→(0.602, 0.151, 0.023) | 0.119→0.162 | 1.00 / 3.333 | 0.152 | 1.182 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.576
- phase_score: 0.601
- phase_breakdown.place_goal_score: 0.460
- phase_breakdown.reach_goal_score: 0.115
- phase_breakdown.reach_object_score: 0.636
- phase_breakdown.grasp_object_score: 0.656
- phase_breakdown.lift_object_score: 0.780
- grasp_place_fitness: 0.751

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.751
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.576
- **Median Q (composite search score)**: -0.084
- **K-run variance**: 0.0057
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Parameters at lower bound**: descend_to_object.grasp_height
- **Final σ (mean)**: 0.330


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.44366,"average_solve_count":142.0,"average_success_count":142.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_speed":0.17199,"approach_object.approach_tolerance":0.01461,"descend_to_object.descend_speed":0.15175,"descend_to_object.grasp_height":0.01104,"lift.lift_height":0.1457,"lift.lift_speed":0.14529,"lower_to_place.lower_speed":0.11122,"lower_to_place.place_height":0.08784,"release.release_time":0.18557,"transport_to_goal.transport_speed":0.38434,"transport_to_goal.transport_tolerance":0.0353},"optimized_scores":{"best_composite_score":-0.08441,"best_fitness_score":0.61559,"best_task_score":0.30489},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":553.0,"contact_point_centroid":[0.63599,0.12704,-0.00379],"force_p95":0.75735,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.73923,"mean_force":0.20471,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.62931,0.13508,0.21989]},{"body_a":"world","body_b":"grasp_target","contact_count":74.0,"contact_point_centroid":[0.54283,0.00048,-0.00136],"force_p95":0.33707,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.4314,"mean_force":0.08759,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52881,0.00084,0.04622]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3450.0,"contact_point_centroid":[0.57351,0.02704,0.17259],"force_p95":0.14974,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31601,"mean_force":0.09196,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.5676,0.04574,0.17231]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5771.0,"contact_point_centroid":[0.53552,0.01965,0.09466],"force_p95":0.10305,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29281,"mean_force":0.06648,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.5321,0.00081,0.09232]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5171.0,"contact_point_centroid":[0.53518,-0.01814,0.09282],"force_p95":0.11302,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29268,"mean_force":0.07273,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.53195,0.00081,0.09096]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4179.0,"contact_point_centroid":[0.57609,0.06771,0.17392],"force_p95":0.12916,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23241,"mean_force":0.07903,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.57002,0.04932,0.17413]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.54431,0.0011,-0.00204],"force_p95":0.13305,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.16023,"mean_force":0.12567,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.53101,0.00088,0.04636]},{"body_a":"world","body_b":"grasp_target","contact_count":1124.0,"contact_point_centroid":[0.54431,0.00113,-0.00188],"force_p95":0.13644,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12306,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.51622,0.00045,0.24562]},{"body_a":"world","body_b":"grasp_target","contact_count":764.0,"contact_point_centroid":[0.63614,0.12714,-0.00199],"force_p95":0.12295,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12348,"mean_force":0.12263,"phase_index":5.0,"phase_name":"lower_to_place","phase_type":"descend","tcp_position_centroid":[0.64068,0.15294,0.24362]},{"body_a":"world","body_b":"grasp_target","contact_count":964.0,"contact_point_centroid":[0.54431,0.00113,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_object","phase_type":"descend","tcp_position_centroid":[0.53587,0.00096,0.12383]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.63614,0.12714,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.64043,0.15498,0.25957]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4838.0,"contact_point_centroid":[0.53092,-0.01838,0.04759],"force_p95":0.06761,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09907,"mean_force":0.04511,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.52981,0.00086,0.04496]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5365.0,"contact_point_centroid":[0.53045,0.02006,0.04757],"force_p95":0.06405,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08622,"mean_force":0.04099,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.52981,0.00086,0.04496]},{"body_a":"left_finger","body_b":"right_finger","contact_count":371.0,"contact_point_centroid":[0.63459,0.14189,0.22579],"force_p95":0.01419,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01609,"mean_force":0.01094,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.63401,0.14188,0.22349]},{"body_a":"left_finger","body_b":"right_finger","contact_count":822.0,"contact_point_centroid":[0.64126,0.15296,0.24584],"force_p95":0.01092,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01095,"mean_force":0.01036,"phase_index":5.0,"phase_name":"lower_to_place","phase_type":"descend","tcp_position_centroid":[0.64068,0.15294,0.2436]},{"body_a":"left_finger","body_b":"right_finger","contact_count":224.0,"contact_point_centroid":[0.64272,0.15563,0.25919],"force_p95":0.0109,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01091,"mean_force":0.00996,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.64228,0.1556,0.25667]}],"total_contact_groups":16},"final_pose_error":0.01968,"key_states":{"actual_goal_position":[0.64762,0.15808,0.1911],"final_object_position":[0.63614,0.12714,0.01602],"final_tcp_position":[0.64329,0.15585,0.25987],"realised_goal_position":[0.64762,0.15808,0.1911],"realised_object_initial_position":[0.54431,0.00113,0.03]},"peak_contact_force":273005.25619,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":282.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.03],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.24751,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1124.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.53481,0.00093,0.19069],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.16495,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":241.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_object","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":964.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_object","tcp_end":[0.53863,0.00102,0.05575],"tcp_start":[0.53481,0.00093,0.19069],"tcp_to_object_dist_end":0.03027,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":46.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54422,0.00091,0.02585],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25041,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.1325,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12003.0,"raw_peak_contact_force":0.16023,"subtask_id":"grasp_object","tcp_end":[0.52978,0.00086,0.04492],"tcp_start":[0.53863,0.00102,0.05575],"tcp_to_object_dist_end":0.02392,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":27.0,"n_steps":357.0,"n_steps_budget":600.0,"object_pos_end":[0.55463,0.00105,0.12792],"object_pos_start":[0.54422,0.00091,0.02585],"object_to_goal_dist_end":0.19313,"object_to_goal_dist_start":0.25041,"object_z_max":0.12768,"peak_contact_force":0.1008,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":11016.0,"raw_peak_contact_force":0.4314,"subtask_id":"lift_object","tcp_end":[0.53895,0.00084,0.15236],"tcp_start":[0.52978,0.00086,0.04492],"tcp_to_object_dist_end":0.02904,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":556.0,"n_steps_budget":1000.0,"object_pos_end":[0.63612,0.12703,0.01606],"object_pos_start":[0.55463,0.00105,0.12792],"object_to_goal_dist_end":0.17815,"object_to_goal_dist_start":0.19313,"object_z_max":0.16342,"peak_contact_force":0.12351,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":8553.0,"raw_peak_contact_force":1.73923,"subtask_id":"reach_goal","tcp_end":[0.63866,0.1495,0.22632],"tcp_start":[0.63827,0.14792,0.22691],"tcp_to_object_dist_end":0.21147,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":191.0,"n_steps_budget":1000.0,"object_pos_end":[0.63614,0.12714,0.01602],"object_pos_start":[0.63613,0.1271,0.016],"object_to_goal_dist_end":0.17817,"object_to_goal_dist_start":0.1782,"object_z_max":0.01602,"peak_contact_force":9748.84621,"phase_name":"lower_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1586.0,"raw_peak_contact_force":0.12348,"subtask_id":"place_goal","tcp_end":[0.64329,0.15585,0.25987],"tcp_start":[0.6434,0.15566,0.25958],"tcp_to_object_dist_end":0.24564,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.63614,0.12714,0.01602],"object_pos_start":[0.63614,0.12714,0.01602],"object_to_goal_dist_end":0.17817,"object_to_goal_dist_start":0.17817,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1024.0,"raw_peak_contact_force":0.12263,"subtask_id":"place_goal","tcp_end":[0.63944,0.15462,0.27861],"tcp_start":[0.64329,0.15585,0.25987],"tcp_to_object_dist_end":0.26404,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `349f925163f8e9284ad51ad55d38356f2e3c8deb4dc54e8ff12260e5f6d4b0f8`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.87288,"average_solve_count":118.0,"average_success_count":118.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_speed":0.22401,"approach_object.approach_tolerance":0.02317,"descend_to_object.descend_speed":0.09377,"descend_to_object.grasp_height":0.01,"lift.lift_height":0.1625,"lift.lift_speed":0.14002,"lower_to_place.lower_speed":0.16278,"lower_to_place.place_height":0.08373,"release.release_time":0.22977,"transport_to_goal.transport_speed":0.27007,"transport_to_goal.transport_tolerance":0.04296},"optimized_scores":{"best_composite_score":0.05144,"best_fitness_score":0.75144,"best_task_score":0.57605},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":190.0,"contact_point_centroid":[0.58311,0.1718,-0.00678],"force_p95":1.17013,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.50081,"mean_force":0.36526,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.58987,0.17196,0.18416]},{"body_a":"world","body_b":"grasp_target","contact_count":80.0,"contact_point_centroid":[0.5288,0.02869,-0.00146],"force_p95":0.31689,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.45935,"mean_force":0.08022,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.51525,0.02888,0.04596]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":973.0,"contact_point_centroid":[0.59592,0.18669,0.15676],"force_p95":0.15473,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33708,"mean_force":0.1163,"phase_index":5.0,"phase_name":"lower_to_place","phase_type":"descend","tcp_position_centroid":[0.59208,0.16839,0.16063]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6419.0,"contact_point_centroid":[0.52208,0.04777,0.10181],"force_p95":0.1072,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30677,"mean_force":0.06789,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.51863,0.02895,0.09943]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5599.0,"contact_point_centroid":[0.52199,0.01001,0.09989],"force_p95":0.11433,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29237,"mean_force":0.07502,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.51852,0.02894,0.09826]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1089.0,"contact_point_centroid":[0.59688,0.15052,0.15807],"force_p95":0.12352,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2853,"mean_force":0.09925,"phase_index":5.0,"phase_name":"lower_to_place","phase_type":"descend","tcp_position_centroid":[0.59221,0.16863,0.16122]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3592.0,"contact_point_centroid":[0.56112,0.07361,0.15844],"force_p95":0.15079,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23237,"mean_force":0.10157,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.55526,0.09224,0.15863]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53056,0.03063,-0.00215],"force_p95":0.16294,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.2252,"mean_force":0.13355,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.51749,0.02903,0.04586]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4394.0,"contact_point_centroid":[0.56177,0.11164,0.15825],"force_p95":0.12251,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20223,"mean_force":0.0815,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.55593,0.09354,0.15852]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":550.0,"contact_point_centroid":[0.59802,0.19172,0.16604],"force_p95":0.13344,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17548,"mean_force":0.0918,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.5937,0.17329,0.17036]},{"body_a":"world","body_b":"grasp_target","contact_count":724.0,"contact_point_centroid":[0.5305,0.03079,-0.00182],"force_p95":0.13759,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.1233,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.50996,0.01146,0.2512]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":600.0,"contact_point_centroid":[0.59818,0.15504,0.16673],"force_p95":0.11624,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13509,"mean_force":0.07996,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.59375,0.17331,0.17046]},{"body_a":"world","body_b":"grasp_target","contact_count":1088.0,"contact_point_centroid":[0.5305,0.03079,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_object","phase_type":"descend","tcp_position_centroid":[0.52236,0.02672,0.12748]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4655.0,"contact_point_centroid":[0.51721,0.00978,0.04709],"force_p95":0.07354,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11606,"mean_force":0.04622,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.51632,0.02896,0.04452]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5114.0,"contact_point_centroid":[0.51707,0.04825,0.04646],"force_p95":0.07359,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07663,"mean_force":0.04383,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.51632,0.02896,0.04453]}],"total_contact_groups":15},"final_pose_error":0.01988,"key_states":{"actual_goal_position":[0.60153,0.17858,0.10809],"final_object_position":[0.58817,0.16958,0.02694],"final_tcp_position":[0.5953,0.17362,0.1736],"realised_goal_position":[0.60153,0.17858,0.10809],"realised_object_initial_position":[0.5305,0.03079,0.03]},"peak_contact_force":1.50081,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":182.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.03],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18162,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":724.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.52146,0.02409,0.19966],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.17401,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":272.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.12262,"phase_name":"descend_to_object","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1088.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_object","tcp_end":[0.52499,0.0295,0.05481],"tcp_start":[0.52146,0.02409,0.19966],"tcp_to_object_dist_end":0.02934,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":45.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53047,0.02952,0.02547],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18464,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.15836,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11569.0,"raw_peak_contact_force":0.2252,"subtask_id":"grasp_object","tcp_end":[0.51629,0.02896,0.04449],"tcp_start":[0.52499,0.0295,0.05481],"tcp_to_object_dist_end":0.02373,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":24.0,"n_steps":402.0,"n_steps_budget":660.0,"object_pos_end":[0.54118,0.02979,0.14312],"object_pos_start":[0.53047,0.02952,0.02547],"object_to_goal_dist_end":0.16434,"object_to_goal_dist_start":0.18464,"object_z_max":0.14288,"peak_contact_force":0.10738,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":12098.0,"raw_peak_contact_force":0.45935,"subtask_id":"lift_object","tcp_end":[0.52559,0.02923,0.1687],"tcp_start":[0.51629,0.02896,0.04449],"tcp_to_object_dist_end":0.02996,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":18.0,"n_steps":372.0,"n_steps_budget":1000.0,"object_pos_end":[0.59402,0.16477,0.1174],"object_pos_start":[0.54118,0.02979,0.14312],"object_to_goal_dist_end":0.01827,"object_to_goal_dist_start":0.16434,"object_z_max":0.14331,"peak_contact_force":0.13663,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":7986.0,"raw_peak_contact_force":0.23237,"subtask_id":"reach_goal","tcp_end":[0.59078,0.16338,0.15155],"tcp_start":[0.52559,0.02923,0.1687],"tcp_to_object_dist_end":0.03434,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":17.0,"n_steps":121.0,"n_steps_budget":1000.0,"object_pos_end":[0.59962,0.17515,0.13851],"object_pos_start":[0.59402,0.16477,0.1174],"object_to_goal_dist_end":0.03067,"object_to_goal_dist_start":0.01827,"object_z_max":0.13832,"peak_contact_force":0.13291,"phase_name":"lower_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2062.0,"raw_peak_contact_force":0.33708,"subtask_id":"place_goal","tcp_end":[0.5953,0.17362,0.1736],"tcp_start":[0.59078,0.16338,0.15155],"tcp_to_object_dist_end":0.03539,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.58817,0.16958,0.02694],"object_pos_start":[0.59962,0.17515,0.13851],"object_to_goal_dist_end":0.08273,"object_to_goal_dist_start":0.03067,"object_z_max":0.13859,"peak_contact_force":0.2096,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1340.0,"raw_peak_contact_force":1.50081,"subtask_id":"place_goal","tcp_end":[0.58981,0.17194,0.19452],"tcp_start":[0.5953,0.17362,0.1736],"tcp_to_object_dist_end":0.16761,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `a1798e4fdcacfe8740623adfe3f78d2bc74e0d14c8233e64f02c40cf2a534ecc`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.58152,"average_solve_count":184.0,"average_success_count":184.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_speed":0.17465,"approach_object.approach_tolerance":0.0458,"descend_to_object.descend_speed":0.07132,"descend_to_object.grasp_height":0.01033,"lift.lift_height":0.16891,"lift.lift_speed":0.04606,"lower_to_place.lower_speed":0.10149,"lower_to_place.place_height":0.07569,"release.release_time":0.22353,"transport_to_goal.transport_speed":0.22272,"transport_to_goal.transport_tolerance":0.02234},"optimized_scores":{"best_composite_score":-0.12464,"best_fitness_score":0.57536,"best_task_score":0.2243},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":718.0,"contact_point_centroid":[0.58121,0.15732,-0.00381],"force_p95":0.8056,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.92249,"mean_force":0.19583,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.58065,0.18248,0.30635]},{"body_a":"world","body_b":"grasp_target","contact_count":89.0,"contact_point_centroid":[0.50069,-0.01433,-0.00148],"force_p95":0.38809,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.41533,"mean_force":0.14079,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.49036,-0.01469,0.04714]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":120.0,"contact_point_centroid":[0.58298,0.1941,0.2781],"force_p95":0.20016,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30246,"mean_force":0.13101,"phase_index":5.0,"phase_name":"lower_to_place","phase_type":"descend","tcp_position_centroid":[0.57969,0.17624,0.28378]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":9003.0,"contact_point_centroid":[0.49305,0.00447,0.11017],"force_p95":0.07859,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26318,"mean_force":0.05471,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.49339,-0.01474,0.10924]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":10087.0,"contact_point_centroid":[0.49309,-0.03386,0.10938],"force_p95":0.07576,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25633,"mean_force":0.04987,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.4933,-0.01474,0.10795]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8927.0,"contact_point_centroid":[0.533,0.08391,0.2178],"force_p95":0.13557,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2453,"mean_force":0.06893,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.53149,0.06513,0.21843]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":198.0,"contact_point_centroid":[0.58327,0.16009,0.27963],"force_p95":0.21685,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24278,"mean_force":0.09172,"phase_index":5.0,"phase_name":"lower_to_place","phase_type":"descend","tcp_position_centroid":[0.57974,0.17671,0.28473]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8797.0,"contact_point_centroid":[0.53353,0.04652,0.218],"force_p95":0.12559,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20963,"mean_force":0.07012,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.53157,0.06527,0.21854]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50384,-0.0156,-0.00209],"force_p95":0.14952,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.19894,"mean_force":0.12964,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.4924,-0.01471,0.04723]},{"body_a":"world","body_b":"grasp_target","contact_count":312.0,"contact_point_centroid":[0.50382,-0.01567,-0.0016],"force_p95":0.13827,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12438,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.50146,-0.00412,0.26592]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4348.0,"contact_point_centroid":[0.49171,0.00463,0.04781],"force_p95":0.07579,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12895,"mean_force":0.04998,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.49128,-0.0147,0.04603]},{"body_a":"world","body_b":"grasp_target","contact_count":1272.0,"contact_point_centroid":[0.50382,-0.01567,-0.00199],"force_p95":0.12264,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12264,"mean_force":0.12258,"phase_index":1.0,"phase_name":"descend_to_object","phase_type":"descend","tcp_position_centroid":[0.49985,-0.012,0.1386]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5910.0,"contact_point_centroid":[0.49154,-0.0338,0.04896],"force_p95":0.06322,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.06813,"mean_force":0.03742,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.49128,-0.0147,0.04603]}],"total_contact_groups":13},"final_pose_error":0.0198,"key_states":{"actual_goal_position":[0.58691,0.18745,0.24812],"final_object_position":[0.58124,0.15726,0.02602],"final_tcp_position":[0.58307,0.18337,0.30482],"realised_goal_position":[0.58691,0.18745,0.24812],"realised_object_initial_position":[0.50382,-0.01567,0.03]},"peak_contact_force":1.92249,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":79.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02595],"object_pos_start":[0.50382,-0.01567,0.03],"object_to_goal_dist_end":0.31228,"object_to_goal_dist_start":0.30942,"object_z_max":0.03,"peak_contact_force":0.12221,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":312.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.50226,-0.00923,0.2244],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.19856,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":318.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.02595],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.31228,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_object","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1272.0,"raw_peak_contact_force":0.12264,"subtask_id":"grasp_object","tcp_end":[0.49962,-0.01477,0.05534],"tcp_start":[0.50226,-0.00923,0.2244],"tcp_to_object_dist_end":0.02964,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":46.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50376,-0.01491,0.02565],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31201,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.14837,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12058.0,"raw_peak_contact_force":0.19894,"subtask_id":"grasp_object","tcp_end":[0.49125,-0.0147,0.04599],"tcp_start":[0.49962,-0.01477,0.05534],"tcp_to_object_dist_end":0.02388,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":460.0,"n_steps_budget":1000.0,"object_pos_end":[0.50734,-0.01511,0.15168],"object_pos_start":[0.50376,-0.01491,0.02565],"object_to_goal_dist_end":0.23803,"object_to_goal_dist_start":0.31201,"object_z_max":0.15141,"peak_contact_force":0.07585,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":19179.0,"raw_peak_contact_force":0.41533,"subtask_id":"lift_object","tcp_end":[0.49908,-0.01483,0.17512],"tcp_start":[0.49125,-0.0147,0.04599],"tcp_to_object_dist_end":0.02485,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":15.0,"n_steps":619.0,"n_steps_budget":1000.0,"object_pos_end":[0.58456,0.1759,0.24691],"object_pos_start":[0.50734,-0.01511,0.15168],"object_to_goal_dist_end":0.01185,"object_to_goal_dist_start":0.23803,"object_z_max":0.24683,"peak_contact_force":0.18509,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":17724.0,"raw_peak_contact_force":0.2453,"subtask_id":"reach_goal","tcp_end":[0.57991,0.17559,0.28367],"tcp_start":[0.49908,-0.01483,0.17512],"tcp_to_object_dist_end":0.03705,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":105.0,"n_steps_budget":1000.0,"object_pos_end":[0.58365,0.15691,0.10385],"object_pos_start":[0.58456,0.1759,0.24691],"object_to_goal_dist_end":0.1475,"object_to_goal_dist_start":0.01185,"object_z_max":0.24691,"peak_contact_force":0.0,"phase_name":"lower_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":318.0,"raw_peak_contact_force":0.30246,"subtask_id":"place_goal","tcp_end":[0.58307,0.18337,0.30482],"tcp_start":[0.57991,0.17559,0.28367],"tcp_to_object_dist_end":0.2027,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.58124,0.15726,0.02602],"object_pos_start":[0.58365,0.15691,0.10385],"object_to_goal_dist_end":0.22421,"object_to_goal_dist_start":0.1475,"object_z_max":0.10385,"peak_contact_force":0.1242,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":718.0,"raw_peak_contact_force":1.92249,"subtask_id":"place_goal","tcp_end":[0.58015,0.18221,0.3258],"tcp_start":[0.58307,0.18337,0.30482],"tcp_to_object_dist_end":0.30082,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```