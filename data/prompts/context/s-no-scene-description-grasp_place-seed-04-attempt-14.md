## Search State

- **Seed**: 4
- **Iteration**: 15 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 14 | approach → descend → grasp → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | impedance_control | impedance_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | time_limit | 9 | -0.1768 | 0.36 | ❌ rejected |
| 13 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 12 | -0.1738 | 0.23 | ❌ rejected |
| 12 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 12 | -0.1439 | 0.29 | ❌ rejected |
| 11 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 12 | -0.1400 | 0.30 | ❌ rejected |
| 10 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 10 | 0.0051 | 0.33 | ❌ rejected |

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

## Current Skill (Q=-0.177) — your mutation base

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

- **Composite score**: -0.177
- **task_score** (E): 0.364
- **fitness_score**: 0.393  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.570

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_object | 1.00 | 1.00 | 0.1047 |
| descend_to_object | 1.00 | 1.00 | 0.1430 |
| grasp | 1.00 | 1.00 | 0.0133 |
| approach_goal_high | 0.00 | 1.00 | 0.0001 |
| descend_to_goal | 1.00 | 1.00 | 0.2374 |
| release | 1.00 | 1.00 | 0.0214 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.520, 0.003, 0.200) | (0.526, 0.005, 0.030)→(0.526, 0.005, 0.026) | 0.246→0.249 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_to_object | descend | 1.00 / step_budget | (0.520, 0.003, 0.200)→(0.521, 0.005, 0.057) | (0.526, 0.005, 0.026)→(0.526, 0.005, 0.026) | 0.249→0.249 | 1.00 / 4.000 | 27.129 | 0.123 |
| grasp | grasp | 1.00 / step_budget | (0.521, 0.005, 0.057)→(0.513, 0.005, 0.047) | (0.526, 0.005, 0.026)→(0.526, 0.005, 0.026) | 0.249→0.249 | 1.00 / 41.333 | 0.146 | 0.188 |
| approach_goal_high | approach | 0.00 / guard_failure | (0.513, 0.005, 0.047)→(0.513, 0.005, 0.047) | (0.526, 0.005, 0.026)→(0.526, 0.005, 0.026) | 0.249→0.249 | 1.00 / 41.333 | 0.251 | 0.253 |
| descend_to_goal | descend | 1.00 / step_budget | (0.513, 0.005, 0.047)→(0.598, 0.156, 0.206) | (0.526, 0.005, 0.026)→(0.602, 0.155, 0.177) | 0.249→0.032 | 1.00 / 29.333 | 0.101 | 0.389 |
| release | release | 1.00 / step_budget | (0.598, 0.156, 0.206)→(0.593, 0.155, 0.227) | (0.602, 0.155, 0.177)→(0.591, 0.153, 0.022) | 0.032→0.164 | 1.00 / 2.667 | 0.216 | 1.573 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 0.000
- transport_retention: None
- terminal_score: 0.562
- phase_score: 0.415
- phase_breakdown.transport_goal_score: 0.001
- phase_breakdown.reach_object_score: 0.460
- phase_breakdown.place_goal_score: 0.589
- phase_breakdown.grasp_object_score: 0.684
- grasp_place_fitness: 0.491

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.491
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.562
- **Median Q (composite search score)**: -0.196
- **K-run variance**: 0.0054
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.370


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.79762,"average_solve_count":252.0,"average_success_count":252.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal_high.transport_speed":0.18105,"approach_goal_high.transport_tolerance":0.01808,"approach_object.approach_speed":0.35619,"approach_object.approach_tolerance":0.00558,"descend_to_goal.lower_speed":0.02002,"descend_to_goal.place_height":0.06649,"descend_to_object.descend_speed":0.02262,"descend_to_object.grasp_height":0.01001,"release.release_time":0.23709},"optimized_scores":{"best_composite_score":-0.19622,"best_fitness_score":0.37378,"best_task_score":0.31878},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":128.0,"contact_point_centroid":[0.6211,0.13567,-0.01007],"force_p95":1.50194,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.57888,"mean_force":0.59739,"phase_index":5.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.62497,0.13646,0.23293]},{"body_a":"world","body_b":"grasp_target","contact_count":146.0,"contact_point_centroid":[0.54434,0.00375,-0.00139],"force_p95":0.302,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.34264,"mean_force":0.23328,"phase_index":4.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.53036,0.00297,0.0455]},{"body_a":"world","body_b":"grasp_target","contact_count":8.0,"contact_point_centroid":[0.54432,0.00082,-0.00207],"force_p95":0.23933,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.23957,"mean_force":0.2191,"phase_index":3.0,"phase_name":"approach_goal_high","phase_type":"approach","tcp_position_centroid":[0.5302,0.00088,0.04417]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":20180.0,"contact_point_centroid":[0.57973,0.05164,0.13455],"force_p95":0.07602,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22889,"mean_force":0.0514,"phase_index":4.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.57888,0.07074,0.13267]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":18734.0,"contact_point_centroid":[0.57978,0.08985,0.13443],"force_p95":0.0774,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21556,"mean_force":0.05357,"phase_index":4.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.57888,0.07072,0.13265]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1173.0,"contact_point_centroid":[0.62938,0.15667,0.21915],"force_p95":0.075,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17326,"mean_force":0.04544,"phase_index":5.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.62837,0.13749,0.21852]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1173.0,"contact_point_centroid":[0.62982,0.11836,0.21993],"force_p95":0.07375,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17084,"mean_force":0.04414,"phase_index":5.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.62837,0.13749,0.21852]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.5443,0.00103,-0.00203],"force_p95":0.13163,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.14895,"mean_force":0.12531,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.53144,0.0009,0.04562]},{"body_a":"world","body_b":"grasp_target","contact_count":3200.0,"contact_point_centroid":[0.54431,0.00113,-0.00195],"force_p95":0.12705,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12278,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.5207,0.00057,0.23012]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4118.0,"contact_point_centroid":[0.53112,-0.01832,0.04692],"force_p95":0.0762,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12291,"mean_force":0.05179,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.53024,0.00088,0.04422]},{"body_a":"world","body_b":"grasp_target","contact_count":1004.0,"contact_point_centroid":[0.54431,0.00113,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_object","phase_type":"descend","tcp_position_centroid":[0.53807,0.00103,0.11867]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":40.0,"contact_point_centroid":[0.53105,0.01987,0.04598],"force_p95":0.10054,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11405,"mean_force":0.06918,"phase_index":3.0,"phase_name":"approach_goal_high","phase_type":"approach","tcp_position_centroid":[0.5302,0.00088,0.04417]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":34.0,"contact_point_centroid":[0.53108,-0.01827,0.04687],"force_p95":0.10499,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11131,"mean_force":0.07524,"phase_index":3.0,"phase_name":"approach_goal_high","phase_type":"approach","tcp_position_centroid":[0.5302,0.00088,0.04417]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4875.0,"contact_point_centroid":[0.53108,0.01995,0.04604],"force_p95":0.06823,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0936,"mean_force":0.04471,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.53024,0.00088,0.04422]}],"total_contact_groups":14},"final_pose_error":0.04492,"key_states":{"actual_goal_position":[0.64762,0.15808,0.1911],"final_object_position":[0.62698,0.13535,0.02239],"final_tcp_position":[0.62973,0.13753,0.22189],"realised_goal_position":[0.64762,0.15808,0.1911],"realised_object_initial_position":[0.54431,0.00113,0.03]},"peak_contact_force":81.14225,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":801.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.03],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.24751,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3200.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.53908,0.00104,0.1772],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.15127,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":251.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":81.14225,"phase_name":"descend_to_object","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1004.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_object","tcp_end":[0.53907,0.00104,0.05499],"tcp_start":[0.53908,0.00104,0.1772],"tcp_to_object_dist_end":0.02944,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54421,0.00077,0.02587],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25048,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.13009,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10793.0,"raw_peak_contact_force":0.14895,"subtask_id":"grasp_object","tcp_end":[0.53021,0.00088,0.04418],"tcp_start":[0.53907,0.00104,0.05499],"tcp_to_object_dist_end":0.02305,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":2.0,"n_steps_budget":1000.0,"object_pos_end":[0.5442,0.00077,0.02584],"object_pos_start":[0.54421,0.00077,0.02587],"object_to_goal_dist_end":0.25051,"object_to_goal_dist_start":0.25048,"object_z_max":0.02587,"peak_contact_force":0.23957,"phase_name":"approach_goal_high","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":82.0,"raw_peak_contact_force":0.23957,"subtask_id":"transport_goal","tcp_end":[0.53016,0.00088,0.0441],"tcp_start":[0.53019,0.00088,0.04415],"tcp_to_object_dist_end":0.02304,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":38.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.63506,0.13714,0.19608],"object_pos_start":[0.54418,0.00077,0.02579],"object_to_goal_dist_end":0.02493,"object_to_goal_dist_start":0.25055,"object_z_max":0.19592,"peak_contact_force":0.07428,"phase_name":"descend_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":39060.0,"raw_peak_contact_force":0.34264,"subtask_id":"place_goal","tcp_end":[0.62973,0.13753,0.22189],"tcp_start":[0.53016,0.00088,0.0441],"tcp_to_object_dist_end":0.02635,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.62698,0.13535,0.02239],"object_pos_start":[0.63506,0.13714,0.19608],"object_to_goal_dist_end":0.17149,"object_to_goal_dist_start":0.02493,"object_z_max":0.19616,"peak_contact_force":0.14534,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2474.0,"raw_peak_contact_force":1.57888,"subtask_id":"place_goal","tcp_end":[0.62494,0.13646,0.24156],"tcp_start":[0.62973,0.13753,0.22189],"tcp_to_object_dist_end":0.21918,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `349f925163f8e9284ad51ad55d38356f2e3c8deb4dc54e8ff12260e5f6d4b0f8`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.23729,"average_solve_count":177.0,"average_success_count":177.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal_high.transport_speed":0.07806,"approach_goal_high.transport_tolerance":0.0317,"approach_object.approach_speed":0.1881,"approach_object.approach_tolerance":0.03913,"descend_to_goal.lower_speed":0.02995,"descend_to_goal.place_height":0.0631,"descend_to_object.descend_speed":0.10731,"descend_to_object.grasp_height":0.01298,"release.release_time":0.28736},"optimized_scores":{"best_composite_score":-0.079,"best_fitness_score":0.491,"best_task_score":0.56234},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":271.0,"contact_point_centroid":[0.57502,0.164,-0.00482],"force_p95":1.05479,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.19717,"mean_force":0.26324,"phase_index":5.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.58701,0.16743,0.167]},{"body_a":"world","body_b":"grasp_target","contact_count":255.0,"contact_point_centroid":[0.53289,0.03591,-0.00157],"force_p95":0.4094,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.4582,"mean_force":0.26269,"phase_index":4.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.5177,0.03427,0.0499]},{"body_a":"world","body_b":"grasp_target","contact_count":8.0,"contact_point_centroid":[0.53076,0.03035,-0.00232],"force_p95":0.27319,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.27422,"mean_force":0.22912,"phase_index":3.0,"phase_name":"approach_goal_high","phase_type":"approach","tcp_position_centroid":[0.51638,0.02853,0.04749]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53058,0.03067,-0.00218],"force_p95":0.17294,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.23009,"mean_force":0.13576,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.51758,0.0286,0.04887]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":9999.0,"contact_point_centroid":[0.5499,0.11087,0.09333],"force_p95":0.12171,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22852,"mean_force":0.07483,"phase_index":4.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.54876,0.09188,0.09415]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1069.0,"contact_point_centroid":[0.59161,0.1503,0.15259],"force_p95":0.09596,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21356,"mean_force":0.05022,"phase_index":5.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.59118,0.16888,0.153]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":718.0,"contact_point_centroid":[0.59346,0.18782,0.14993],"force_p95":0.11381,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19471,"mean_force":0.07179,"phase_index":5.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.59112,0.16885,0.15289]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":13943.0,"contact_point_centroid":[0.55406,0.08101,0.10102],"force_p95":0.09894,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17467,"mean_force":0.05695,"phase_index":4.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.55313,0.09962,0.10032]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4322.0,"contact_point_centroid":[0.51699,0.00937,0.04859],"force_p95":0.07735,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1395,"mean_force":0.04948,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.51641,0.02853,0.04754]},{"body_a":"world","body_b":"grasp_target","contact_count":408.0,"contact_point_centroid":[0.5305,0.03079,-0.00169],"force_p95":0.13814,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12386,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.50936,0.00932,0.26051]},{"body_a":"world","body_b":"grasp_target","contact_count":1164.0,"contact_point_centroid":[0.5305,0.03079,-0.00199],"force_p95":0.12264,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12264,"mean_force":0.12261,"phase_index":1.0,"phase_name":"descend_to_object","phase_type":"descend","tcp_position_centroid":[0.52116,0.02456,0.13578]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":38.0,"contact_point_centroid":[0.51753,0.04761,0.04871],"force_p95":0.10575,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12037,"mean_force":0.07176,"phase_index":3.0,"phase_name":"approach_goal_high","phase_type":"approach","tcp_position_centroid":[0.51638,0.02853,0.04749]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":36.0,"contact_point_centroid":[0.51694,0.00944,0.04858],"force_p95":0.10389,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11018,"mean_force":0.06898,"phase_index":3.0,"phase_name":"approach_goal_high","phase_type":"approach","tcp_position_centroid":[0.51638,0.02853,0.04749]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4880.0,"contact_point_centroid":[0.51748,0.04777,0.04874],"force_p95":0.07755,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07986,"mean_force":0.04548,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.51642,0.02853,0.04755]}],"total_contact_groups":14},"final_pose_error":0.0198,"key_states":{"actual_goal_position":[0.60153,0.17858,0.10809],"final_object_position":[0.57742,0.16429,0.02642],"final_tcp_position":[0.59291,0.169,0.15617],"realised_goal_position":[0.60153,0.17858,0.10809],"realised_object_initial_position":[0.5305,0.03079,0.03]},"peak_contact_force":1.19717,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":103.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.03],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18162,"object_z_max":0.03,"peak_contact_force":0.12229,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":408.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.51933,0.02017,0.21561],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.19022,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":291.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_object","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1164.0,"raw_peak_contact_force":0.12264,"subtask_id":"grasp_object","tcp_end":[0.52501,0.02904,0.05782],"tcp_start":[0.51933,0.02017,0.21561],"tcp_to_object_dist_end":0.03232,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53049,0.02933,0.02536],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18484,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.1685,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11002.0,"raw_peak_contact_force":0.23009,"subtask_id":"grasp_object","tcp_end":[0.51638,0.02853,0.0475],"tcp_start":[0.52501,0.02904,0.05782],"tcp_to_object_dist_end":0.02627,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":2.0,"n_steps_budget":1000.0,"object_pos_end":[0.53049,0.02933,0.02533],"object_pos_start":[0.53049,0.02933,0.02536],"object_to_goal_dist_end":0.18486,"object_to_goal_dist_start":0.18484,"object_z_max":0.02536,"peak_contact_force":0.27129,"phase_name":"approach_goal_high","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":82.0,"raw_peak_contact_force":0.27422,"subtask_id":"transport_goal","tcp_end":[0.51633,0.02852,0.04743],"tcp_start":[0.51637,0.02853,0.04748],"tcp_to_object_dist_end":0.02626,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":28.0,"n_steps":748.0,"n_steps_budget":1000.0,"object_pos_end":[0.59657,0.16668,0.12544],"object_pos_start":[0.53047,0.02933,0.02528],"object_to_goal_dist_end":0.02162,"object_to_goal_dist_start":0.18489,"object_z_max":0.12531,"peak_contact_force":0.11375,"phase_name":"descend_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":24197.0,"raw_peak_contact_force":0.4582,"subtask_id":"place_goal","tcp_end":[0.59291,0.169,0.15617],"tcp_start":[0.51633,0.02852,0.04743],"tcp_to_object_dist_end":0.03104,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.57742,0.16429,0.02642],"object_pos_start":[0.59657,0.16668,0.12544],"object_to_goal_dist_end":0.08635,"object_to_goal_dist_start":0.02162,"object_z_max":0.12549,"peak_contact_force":0.11408,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2058.0,"raw_peak_contact_force":1.19717,"subtask_id":"place_goal","tcp_end":[0.58694,0.16741,0.17715],"tcp_start":[0.59291,0.169,0.15617],"tcp_to_object_dist_end":0.15107,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `a1798e4fdcacfe8740623adfe3f78d2bc74e0d14c8233e64f02c40cf2a534ecc`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.25595,"average_solve_count":168.0,"average_success_count":168.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal_high.transport_speed":0.05787,"approach_goal_high.transport_tolerance":0.02247,"approach_object.approach_speed":0.26111,"approach_object.approach_tolerance":0.02739,"descend_to_goal.lower_speed":0.04683,"descend_to_goal.place_height":0.02777,"descend_to_object.descend_speed":0.10014,"descend_to_object.grasp_height":0.0128,"release.release_time":0.3309},"optimized_scores":{"best_composite_score":-0.25509,"best_fitness_score":0.31491,"best_task_score":0.21038},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":140.0,"contact_point_centroid":[0.55558,0.16566,-0.00907],"force_p95":1.42593,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.94421,"mean_force":0.54278,"phase_index":5.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.56818,0.16102,0.25542]},{"body_a":"world","body_b":"grasp_target","contact_count":133.0,"contact_point_centroid":[0.50277,-0.01155,-0.0014],"force_p95":0.339,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.36538,"mean_force":0.24805,"phase_index":4.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.49099,-0.01254,0.05032]},{"body_a":"world","body_b":"grasp_target","contact_count":8.0,"contact_point_centroid":[0.50388,-0.01549,-0.00213],"force_p95":0.24372,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24459,"mean_force":0.21612,"phase_index":3.0,"phase_name":"approach_goal_high","phase_type":"approach","tcp_position_centroid":[0.49125,-0.0149,0.04894]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":18936.0,"contact_point_centroid":[0.52734,0.05124,0.13828],"force_p95":0.09244,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24306,"mean_force":0.05454,"phase_index":4.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.52788,0.06978,0.13852]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":12580.0,"contact_point_centroid":[0.52584,0.08285,0.13078],"force_p95":0.11973,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21521,"mean_force":0.07806,"phase_index":4.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.52507,0.06382,0.13196]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":606.0,"contact_point_centroid":[0.57222,0.18086,0.23477],"force_p95":0.12788,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20811,"mean_force":0.0832,"phase_index":5.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.57113,0.16211,0.23782]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50383,-0.01562,-0.00207],"force_p95":0.14214,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.18442,"mean_force":0.12777,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.4924,-0.01492,0.05019]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":729.0,"contact_point_centroid":[0.57195,0.14366,0.23449],"force_p95":0.10646,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17917,"mean_force":0.06827,"phase_index":5.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.57114,0.16212,0.23782]},{"body_a":"world","body_b":"grasp_target","contact_count":556.0,"contact_point_centroid":[0.50382,-0.01567,-0.00177],"force_p95":0.13792,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.1235,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.5003,-0.00535,0.25562]},{"body_a":"world","body_b":"grasp_target","contact_count":1116.0,"contact_point_centroid":[0.50382,-0.01567,-0.00199],"force_p95":0.12264,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12264,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_object","phase_type":"descend","tcp_position_centroid":[0.4993,-0.01318,0.13254]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4351.0,"contact_point_centroid":[0.49165,0.00428,0.04985],"force_p95":0.07343,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11657,"mean_force":0.04949,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.49128,-0.0149,0.04898]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":40.0,"contact_point_centroid":[0.49157,-0.03397,0.04973],"force_p95":0.10024,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11313,"mean_force":0.06787,"phase_index":3.0,"phase_name":"approach_goal_high","phase_type":"approach","tcp_position_centroid":[0.49125,-0.0149,0.04894]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":36.0,"contact_point_centroid":[0.49161,0.00422,0.04983],"force_p95":0.10153,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11211,"mean_force":0.0717,"phase_index":3.0,"phase_name":"approach_goal_high","phase_type":"approach","tcp_position_centroid":[0.49125,-0.0149,0.04894]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4914.0,"contact_point_centroid":[0.49162,-0.03405,0.04977],"force_p95":0.06977,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07977,"mean_force":0.04449,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.49129,-0.0149,0.04898]}],"total_contact_groups":14},"final_pose_error":0.04554,"key_states":{"actual_goal_position":[0.58691,0.18745,0.24812],"final_object_position":[0.56806,0.15945,0.01674],"final_tcp_position":[0.5725,0.16217,0.24086],"realised_goal_position":[0.58691,0.18745,0.24812],"realised_object_initial_position":[0.50382,-0.01567,0.03]},"peak_contact_force":1.94421,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":140.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.03],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.30942,"object_z_max":0.03,"peak_contact_force":0.12264,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":556.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.50078,-0.01143,0.20681],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.18086,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":279.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_object","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1116.0,"raw_peak_contact_force":0.12264,"subtask_id":"grasp_object","tcp_end":[0.49961,-0.01499,0.05835],"tcp_start":[0.50078,-0.01143,0.20681],"tcp_to_object_dist_end":0.03261,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":42.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50375,-0.01513,0.02575],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31209,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.14074,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11065.0,"raw_peak_contact_force":0.18442,"subtask_id":"grasp_object","tcp_end":[0.49126,-0.0149,0.04895],"tcp_start":[0.49961,-0.01499,0.05835],"tcp_to_object_dist_end":0.02635,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":42.0,"n_steps":2.0,"n_steps_budget":1000.0,"object_pos_end":[0.50374,-0.01513,0.02572],"object_pos_start":[0.50375,-0.01513,0.02575],"object_to_goal_dist_end":0.31212,"object_to_goal_dist_start":0.31209,"object_z_max":0.02575,"peak_contact_force":0.24211,"phase_name":"approach_goal_high","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":84.0,"raw_peak_contact_force":0.24459,"subtask_id":"transport_goal","tcp_end":[0.4912,-0.0149,0.04888],"tcp_start":[0.49124,-0.0149,0.04892],"tcp_to_object_dist_end":0.02634,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":22.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.57464,0.16058,0.20853],"object_pos_start":[0.50372,-0.01513,0.02567],"object_to_goal_dist_end":0.0494,"object_to_goal_dist_start":0.31216,"object_z_max":0.20834,"peak_contact_force":0.11403,"phase_name":"descend_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":31649.0,"raw_peak_contact_force":0.36538,"subtask_id":"place_goal","tcp_end":[0.5725,0.16217,0.24086],"tcp_start":[0.4912,-0.0149,0.04888],"tcp_to_object_dist_end":0.03244,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.56806,0.15945,0.01674],"object_pos_start":[0.57464,0.16058,0.20853],"object_to_goal_dist_end":0.23383,"object_to_goal_dist_start":0.0494,"object_z_max":0.20862,"peak_contact_force":0.38982,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1475.0,"raw_peak_contact_force":1.94421,"subtask_id":"place_goal","tcp_end":[0.56814,0.16101,0.26249],"tcp_start":[0.5725,0.16217,0.24086],"tcp_to_object_dist_end":0.24576,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```