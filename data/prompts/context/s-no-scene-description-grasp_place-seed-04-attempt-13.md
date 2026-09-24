## Search State

- **Seed**: 4
- **Iteration**: 14 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 13 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 12 | -0.1738 | 0.23 | ❌ rejected |
| 12 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 12 | -0.1439 | 0.29 | ❌ rejected |
| 11 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 12 | -0.1400 | 0.30 | ❌ rejected |
| 10 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 10 | 0.0051 | 0.33 | ❌ rejected |
| 9 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 11 | -0.0583 | 0.36 | ❌ rejected |

**Proposal policy**: task_score is 0.23 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=-0.174) — your mutation base

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

- **Composite score**: -0.174
- **task_score** (E): 0.227
- **fitness_score**: 0.576  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.750

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_object | 1.00 | 1.00 | 0.0964 |
| descend_to_object | 1.00 | 1.00 | 0.1524 |
| grasp | 1.00 | 1.00 | 0.0134 |
| lift | 1.00 | 1.00 | 0.1294 |
| transport_to_goal | 1.00 | 1.00 | 0.0028 |
| lower_to_place | 1.00 | 1.00 | 0.0067 |
| release | 1.00 | 1.00 | 0.0199 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.517, 0.004, 0.208) | (0.526, 0.005, 0.030)→(0.526, 0.005, 0.026) | 0.246→0.249 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_to_object | descend | 1.00 / step_budget | (0.517, 0.004, 0.208)→(0.521, 0.005, 0.056) | (0.526, 0.005, 0.026)→(0.526, 0.005, 0.026) | 0.249→0.249 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp | grasp | 1.00 / step_budget | (0.521, 0.005, 0.056)→(0.512, 0.005, 0.045) | (0.526, 0.005, 0.026)→(0.526, 0.005, 0.026) | 0.249→0.249 | 1.00 / 42.667 | 0.145 | 0.189 |
| lift | lift | 1.00 / step_budget | (0.522, 0.005, 0.190)→(0.532, 0.007, 0.319) | (0.526, 0.005, 0.026)→(0.535, 0.008, 0.155) | 0.249→0.198 | 1.00 / 13.333 | 6499.224 | 1.285 |
| transport_to_goal | approach | 1.00 / step_budget | (0.606, 0.162, 0.379)→(0.606, 0.164, 0.377) | (0.534, 0.024, 0.094)→(0.543, 0.038, 0.016) | 0.206→0.230 | 1.00 / 8.000 | 3249.704 | 0.746 |
| lower_to_place | descend | 1.00 / step_budget | (0.609, 0.172, 0.253)→(0.608, 0.172, 0.246) | (0.543, 0.038, 0.016)→(0.543, 0.038, 0.016) | 0.230→0.230 | 1.00 / 8.667 | 182001.888 | 0.123 |
| release | release | 1.00 / step_budget | (0.608, 0.172, 0.246)→(0.604, 0.171, 0.265) | (0.543, 0.038, 0.016)→(0.543, 0.038, 0.016) | 0.230→0.230 | 1.00 / 4.000 | 0.123 | 0.123 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.326
- phase_score: 0.498
- phase_breakdown.place_goal_score: 0.727
- phase_breakdown.reach_goal_score: 0.636
- phase_breakdown.reach_object_score: 0.531
- phase_breakdown.grasp_object_score: 0.659
- phase_breakdown.lift_object_score: 0.023
- grasp_place_fitness: 0.626

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.626
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.326
- **Median Q (composite search score)**: -0.184
- **K-run variance**: 0.0014
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.381


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.5671,"average_solve_count":231.0,"average_success_count":231.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_speed":0.32404,"approach_object.approach_tolerance":0.03555,"descend_to_object.descend_speed":0.07891,"descend_to_object.grasp_height":0.01023,"lift.lift_height":0.17487,"lift.lift_speed":0.23344,"lower_to_place.lower_speed":0.05213,"lower_to_place.place_height":0.06648,"release.release_time":0.47347,"transport_to_goal.transport_height":0.24994,"transport_to_goal.transport_speed":0.268,"transport_to_goal.transport_tolerance":0.04938},"optimized_scores":{"best_composite_score":-0.18356,"best_fitness_score":0.56644,"best_task_score":0.20625},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":1035.0,"contact_point_centroid":[0.54642,0.03204,-0.003],"force_p95":0.52523,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.82236,"mean_force":0.17263,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.54622,0.00077,0.25604]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6844.0,"contact_point_centroid":[0.53737,0.0194,0.11682],"force_p95":0.12564,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.37863,"mean_force":0.07668,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.5328,0.00074,0.11513]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6030.0,"contact_point_centroid":[0.5369,-0.01809,0.1142],"force_p95":0.13172,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31093,"mean_force":0.08248,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.53255,0.00074,0.11237]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.54431,0.00103,-0.00203],"force_p95":0.13249,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.15455,"mean_force":0.12547,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.53031,0.00086,0.04568]},{"body_a":"world","body_b":"grasp_target","contact_count":460.0,"contact_point_centroid":[0.54431,0.00113,-0.00173],"force_p95":0.13814,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12369,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.51399,0.00037,0.25863]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4116.0,"contact_point_centroid":[0.53039,-0.01836,0.04694],"force_p95":0.07634,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12434,"mean_force":0.05182,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.52912,0.00084,0.04428]},{"body_a":"world","body_b":"grasp_target","contact_count":2308.0,"contact_point_centroid":[0.54672,0.03464,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12265,"mean_force":0.12263,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.59898,0.07868,0.36831]},{"body_a":"world","body_b":"grasp_target","contact_count":1176.0,"contact_point_centroid":[0.54431,0.00113,-0.00199],"force_p95":0.12264,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12264,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_object","phase_type":"descend","tcp_position_centroid":[0.53244,0.00086,0.13284]},{"body_a":"world","body_b":"grasp_target","contact_count":1100.0,"contact_point_centroid":[0.54672,0.03464,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"lower_to_place","phase_type":"descend","tcp_position_centroid":[0.64456,0.15329,0.34711]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.54672,0.03464,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.64188,0.15525,0.26908]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4875.0,"contact_point_centroid":[0.53029,0.01992,0.04607],"force_p95":0.06842,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09414,"mean_force":0.04471,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.52912,0.00084,0.04428]},{"body_a":"left_finger","body_b":"right_finger","contact_count":880.0,"contact_point_centroid":[0.5486,0.00077,0.28018],"force_p95":0.01256,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01522,"mean_force":0.0106,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.54829,0.00077,0.27792]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1179.0,"contact_point_centroid":[0.64498,0.15331,0.34948],"force_p95":0.011,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01292,"mean_force":0.0104,"phase_index":5.0,"phase_name":"lower_to_place","phase_type":"descend","tcp_position_centroid":[0.64456,0.15329,0.34724]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2460.0,"contact_point_centroid":[0.59928,0.07858,0.3705],"force_p95":0.01098,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01277,"mean_force":0.01046,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.59892,0.07857,0.36823]},{"body_a":"left_finger","body_b":"right_finger","contact_count":224.0,"contact_point_centroid":[0.64409,0.15588,0.26845],"force_p95":0.01104,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01274,"mean_force":0.01,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.64354,0.15584,0.26595]}],"total_contact_groups":15},"final_pose_error":0.0131,"key_states":{"actual_goal_position":[0.64762,0.15808,0.1911],"final_object_position":[0.54672,0.03464,0.01602],"final_tcp_position":[0.64474,0.15617,0.27022],"realised_goal_position":[0.64762,0.15808,0.1911],"realised_object_initial_position":[0.54431,0.00113,0.03]},"peak_contact_force":273002.30133,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":116.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.03],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.24751,"object_z_max":0.03,"peak_contact_force":0.12249,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":460.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.5293,0.00075,0.21214],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.18672,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":294.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_object","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1176.0,"raw_peak_contact_force":0.12264,"subtask_id":"grasp_object","tcp_end":[0.53795,0.001,0.05505],"tcp_start":[0.5293,0.00075,0.21214],"tcp_to_object_dist_end":0.02972,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54422,0.00076,0.02587],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.2505,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.13082,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10791.0,"raw_peak_contact_force":0.15455,"subtask_id":"grasp_object","tcp_end":[0.52909,0.00084,0.04424],"tcp_start":[0.53795,0.001,0.05505],"tcp_to_object_dist_end":0.0238,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":829.0,"n_steps_budget":600.0,"object_pos_end":[0.55569,0.00089,0.15522],"object_pos_start":[0.54422,0.00076,0.02587],"object_to_goal_dist_end":0.1856,"object_to_goal_dist_start":0.2505,"object_z_max":0.17026,"peak_contact_force":9748.69207,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":14789.0,"raw_peak_contact_force":1.82236,"subtask_id":"lift_object","tcp_end":[0.55226,0.00081,0.31064],"tcp_start":[0.53953,0.0007,0.18131],"tcp_to_object_dist_end":0.15545,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":577.0,"n_steps_budget":1000.0,"object_pos_end":[0.54672,0.03464,0.01602],"object_pos_start":[0.54672,0.03464,0.01602],"object_to_goal_dist_end":0.2368,"object_to_goal_dist_start":0.2368,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4768.0,"raw_peak_contact_force":0.12265,"subtask_id":"reach_goal","tcp_end":[0.64327,0.15027,0.42416],"tcp_start":[0.64251,0.14861,0.4242],"tcp_to_object_dist_end":0.43505,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":275.0,"n_steps_budget":1000.0,"object_pos_end":[0.54672,0.03464,0.01602],"object_pos_start":[0.54672,0.03464,0.01602],"object_to_goal_dist_end":0.2368,"object_to_goal_dist_start":0.2368,"object_z_max":0.01602,"peak_contact_force":273002.30133,"phase_name":"lower_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2279.0,"raw_peak_contact_force":0.12263,"subtask_id":"place_goal","tcp_end":[0.64474,0.15617,0.27022],"tcp_start":[0.64528,0.15612,0.27721],"tcp_to_object_dist_end":0.29832,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54672,0.03464,0.01602],"object_pos_start":[0.54672,0.03464,0.01602],"object_to_goal_dist_end":0.2368,"object_to_goal_dist_start":0.2368,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1024.0,"raw_peak_contact_force":0.12263,"subtask_id":"place_goal","tcp_end":[0.64099,0.15491,0.28817],"tcp_start":[0.64474,0.15617,0.27022],"tcp_to_object_dist_end":0.31211,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `349f925163f8e9284ad51ad55d38356f2e3c8deb4dc54e8ff12260e5f6d4b0f8`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.84293,"average_solve_count":191.0,"average_success_count":191.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_speed":0.20293,"approach_object.approach_tolerance":0.03223,"descend_to_object.descend_speed":0.12859,"descend_to_object.grasp_height":0.0103,"lift.lift_height":0.21837,"lift.lift_speed":0.15549,"lower_to_place.lower_speed":0.08156,"lower_to_place.place_height":0.02632,"release.release_time":0.22371,"transport_to_goal.transport_height":0.16565,"transport_to_goal.transport_speed":0.34283,"transport_to_goal.transport_tolerance":0.02073},"optimized_scores":{"best_composite_score":-0.12418,"best_fitness_score":0.62582,"best_task_score":0.32584},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":1547.0,"contact_point_centroid":[0.53907,0.05096,-0.0027],"force_p95":0.37305,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.64661,"mean_force":0.15156,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.53127,0.03315,0.29251]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6654.0,"contact_point_centroid":[0.52219,0.00989,0.11759],"force_p95":0.13106,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33886,"mean_force":0.07926,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.51831,0.02873,0.11647]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":7380.0,"contact_point_centroid":[0.52218,0.04749,0.11698],"force_p95":0.12626,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31313,"mean_force":0.07502,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.51825,0.02873,0.11554]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53057,0.03064,-0.00217],"force_p95":0.17024,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.23023,"mean_force":0.13506,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.51753,0.02879,0.04625]},{"body_a":"world","body_b":"grasp_target","contact_count":512.0,"contact_point_centroid":[0.5305,0.03079,-0.00175],"force_p95":0.13797,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12358,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.50966,0.01026,0.25645]},{"body_a":"world","body_b":"grasp_target","contact_count":1120.0,"contact_point_centroid":[0.5305,0.03079,-0.00199],"force_p95":0.12264,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12264,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_object","phase_type":"descend","tcp_position_centroid":[0.52161,0.0255,0.13149]},{"body_a":"world","body_b":"grasp_target","contact_count":1384.0,"contact_point_centroid":[0.53949,0.05223,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.56608,0.10151,0.31842]},{"body_a":"world","body_b":"grasp_target","contact_count":936.0,"contact_point_centroid":[0.53949,0.05223,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":5.0,"phase_name":"lower_to_place","phase_type":"descend","tcp_position_centroid":[0.59399,0.16955,0.20869]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.53949,0.05223,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.59078,0.17336,0.14644]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4407.0,"contact_point_centroid":[0.51718,0.00947,0.04704],"force_p95":0.07871,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11744,"mean_force":0.04888,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.51636,0.02871,0.04492]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5552.0,"contact_point_centroid":[0.51681,0.04793,0.04752],"force_p95":0.07157,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07447,"mean_force":0.04033,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.51637,0.02871,0.04493]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1373.0,"contact_point_centroid":[0.53322,0.03381,0.31628],"force_p95":0.01218,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0162,"mean_force":0.01065,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.53287,0.0338,0.31395]},{"body_a":"left_finger","body_b":"right_finger","contact_count":997.0,"contact_point_centroid":[0.59443,0.16957,0.21106],"force_p95":0.01104,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01288,"mean_force":0.01046,"phase_index":5.0,"phase_name":"lower_to_place","phase_type":"descend","tcp_position_centroid":[0.59399,0.16954,0.20879]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1470.0,"contact_point_centroid":[0.56674,0.10181,0.32049],"force_p95":0.01099,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01281,"mean_force":0.01049,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.56621,0.10179,0.31822]},{"body_a":"left_finger","body_b":"right_finger","contact_count":221.0,"contact_point_centroid":[0.59417,0.17436,0.14471],"force_p95":0.01094,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01096,"mean_force":0.01007,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.59362,0.17431,0.14241]}],"total_contact_groups":15},"final_pose_error":0.01372,"key_states":{"actual_goal_position":[0.60153,0.17858,0.10809],"final_object_position":[0.53949,0.05223,0.01602],"final_tcp_position":[0.5955,0.17483,0.14615],"realised_goal_position":[0.60153,0.17858,0.10809],"realised_object_initial_position":[0.5305,0.03079,0.03]},"peak_contact_force":9748.87755,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":129.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.03],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18162,"object_z_max":0.03,"peak_contact_force":0.1226,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":512.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.52021,0.02189,0.20859],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.18307,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":280.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_object","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1120.0,"raw_peak_contact_force":0.12264,"subtask_id":"grasp_object","tcp_end":[0.525,0.02924,0.0552],"tcp_start":[0.52021,0.02189,0.20859],"tcp_to_object_dist_end":0.02974,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":45.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53049,0.02938,0.02539],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18479,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.1653,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11759.0,"raw_peak_contact_force":0.23023,"subtask_id":"grasp_object","tcp_end":[0.51633,0.02871,0.04489],"tcp_start":[0.525,0.02924,0.0552],"tcp_to_object_dist_end":0.0241,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":978.0,"n_steps_budget":810.0,"object_pos_end":[0.54058,0.03737,0.16914],"object_pos_start":[0.53049,0.02938,0.02539],"object_to_goal_dist_end":0.16548,"object_to_goal_dist_start":0.18479,"object_z_max":0.18314,"peak_contact_force":9748.87755,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":16954.0,"raw_peak_contact_force":1.64661,"subtask_id":"lift_object","tcp_end":[0.53819,0.03655,0.36794],"tcp_start":[0.52656,0.02912,0.22424],"tcp_to_object_dist_end":0.19881,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":346.0,"n_steps_budget":1000.0,"object_pos_end":[0.53949,0.05223,0.01602],"object_pos_start":[0.53949,0.05223,0.01602],"object_to_goal_dist_end":0.1682,"object_to_goal_dist_start":0.1682,"object_z_max":0.01602,"peak_contact_force":9748.86764,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2854.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_goal","tcp_end":[0.59249,0.16418,0.27306],"tcp_start":[0.59214,0.16141,0.27675],"tcp_to_object_dist_end":0.28533,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":234.0,"n_steps_budget":1000.0,"object_pos_end":[0.53949,0.05223,0.01602],"object_pos_start":[0.53949,0.05223,0.01602],"object_to_goal_dist_end":0.1682,"object_to_goal_dist_start":0.1682,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"lower_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1933.0,"raw_peak_contact_force":0.12263,"subtask_id":"place_goal","tcp_end":[0.5955,0.17483,0.14615],"tcp_start":[0.59645,0.17468,0.15296],"tcp_to_object_dist_end":0.18735,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53949,0.05223,0.01602],"object_pos_start":[0.53949,0.05223,0.01602],"object_to_goal_dist_end":0.1682,"object_to_goal_dist_start":0.1682,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1021.0,"raw_peak_contact_force":0.12263,"subtask_id":"place_goal","tcp_end":[0.58908,0.17278,0.16619],"tcp_start":[0.5955,0.17483,0.14615],"tcp_to_object_dist_end":0.19885,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `a1798e4fdcacfe8740623adfe3f78d2bc74e0d14c8233e64f02c40cf2a534ecc`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.64762,"average_solve_count":210.0,"average_success_count":210.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_speed":0.20799,"approach_object.approach_tolerance":0.02361,"descend_to_object.descend_speed":0.17268,"descend_to_object.grasp_height":0.01143,"lift.lift_height":0.15854,"lift.lift_speed":0.06041,"lower_to_place.lower_speed":0.09783,"lower_to_place.place_height":0.06041,"release.release_time":0.49942,"transport_to_goal.transport_height":0.20273,"transport_to_goal.transport_speed":0.16775,"transport_to_goal.transport_tolerance":0.01706},"optimized_scores":{"best_composite_score":-0.21365,"best_fitness_score":0.53635,"best_task_score":0.14926},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":2141.0,"contact_point_centroid":[0.54144,0.02781,-0.00268],"force_p95":0.18929,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.99214,"mean_force":0.1491,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.55548,0.11207,0.38053]},{"body_a":"world","body_b":"grasp_target","contact_count":85.0,"contact_point_centroid":[0.50174,-0.01475,-0.00141],"force_p95":0.33692,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.38532,"mean_force":0.09356,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.49015,-0.01496,0.04846]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":12383.0,"contact_point_centroid":[0.49776,0.004,0.14918],"force_p95":0.1016,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26954,"mean_force":0.06491,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.49596,-0.01503,0.14829]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":815.0,"contact_point_centroid":[0.51471,0.01418,0.28524],"force_p95":0.18992,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26272,"mean_force":0.10439,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.50801,-0.00446,0.28579]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":13629.0,"contact_point_centroid":[0.49757,-0.03399,0.14811],"force_p95":0.09647,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26265,"mean_force":0.06,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.4959,-0.01503,0.14731]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1059.0,"contact_point_centroid":[0.51501,-0.02107,0.28539],"force_p95":0.14882,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25637,"mean_force":0.08425,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.50853,-0.00296,0.28681]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50383,-0.01561,-0.00206],"force_p95":0.14055,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.18247,"mean_force":0.12742,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.49219,-0.01499,0.04845]},{"body_a":"world","body_b":"grasp_target","contact_count":648.0,"contact_point_centroid":[0.50382,-0.01567,-0.0018],"force_p95":0.13762,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12338,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.5,-0.00563,0.25327]},{"body_a":"world","body_b":"grasp_target","contact_count":1032.0,"contact_point_centroid":[0.50382,-0.01567,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12264,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_object","phase_type":"descend","tcp_position_centroid":[0.49912,-0.01348,0.12981]},{"body_a":"world","body_b":"grasp_target","contact_count":824.0,"contact_point_centroid":[0.54142,0.02787,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":5.0,"phase_name":"lower_to_place","phase_type":"descend","tcp_position_centroid":[0.58445,0.18203,0.37784]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.54142,0.02787,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.58282,0.18428,0.32228]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4351.0,"contact_point_centroid":[0.49155,0.00421,0.04871],"force_p95":0.0736,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11655,"mean_force":0.04945,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.49107,-0.01497,0.04724]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4913.0,"contact_point_centroid":[0.4915,-0.03412,0.04854],"force_p95":0.06971,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07925,"mean_force":0.04452,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.49107,-0.01497,0.04725]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2162.0,"contact_point_centroid":[0.55752,0.11588,0.38605],"force_p95":0.01145,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01624,"mean_force":0.01056,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.55708,0.11587,0.38373]},{"body_a":"left_finger","body_b":"right_finger","contact_count":881.0,"contact_point_centroid":[0.58492,0.18205,0.37991],"force_p95":0.01095,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01268,"mean_force":0.01043,"phase_index":5.0,"phase_name":"lower_to_place","phase_type":"descend","tcp_position_centroid":[0.58446,0.18204,0.3777]},{"body_a":"left_finger","body_b":"right_finger","contact_count":224.0,"contact_point_centroid":[0.58449,0.18489,0.32057],"force_p95":0.01091,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01094,"mean_force":0.00995,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.584,0.18487,0.31829]}],"total_contact_groups":16},"final_pose_error":0.01377,"key_states":{"actual_goal_position":[0.58691,0.18745,0.24812],"final_object_position":[0.54142,0.02787,0.01602],"final_tcp_position":[0.58496,0.18519,0.32197],"realised_goal_position":[0.58691,0.18745,0.24812],"realised_object_initial_position":[0.50382,-0.01567,0.03]},"peak_contact_force":273003.24057,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":163.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.03],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.30942,"object_z_max":0.03,"peak_contact_force":0.12264,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":648.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.50051,-0.01195,0.20274],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.17679,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":258.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_object","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1032.0,"raw_peak_contact_force":0.12264,"subtask_id":"grasp_object","tcp_end":[0.49943,-0.01506,0.05661],"tcp_start":[0.50051,-0.01195,0.20274],"tcp_to_object_dist_end":0.03091,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":42.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50374,-0.01515,0.02577],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31209,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.13911,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11064.0,"raw_peak_contact_force":0.18247,"subtask_id":"grasp_object","tcp_end":[0.49104,-0.01497,0.04721],"tcp_start":[0.49943,-0.01506,0.05661],"tcp_to_object_dist_end":0.02493,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":24.0,"n_steps":768.0,"n_steps_budget":1000.0,"object_pos_end":[0.50802,-0.01518,0.14001],"object_pos_start":[0.50374,-0.01515,0.02577],"object_to_goal_dist_end":0.24284,"object_to_goal_dist_start":0.31209,"object_z_max":0.25017,"peak_contact_force":0.10202,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":26097.0,"raw_peak_contact_force":0.38532,"subtask_id":"lift_object","tcp_end":[0.50464,-0.01513,0.27905],"tcp_start":[0.4989,-0.01507,0.16516],"tcp_to_object_dist_end":0.13908,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":742.0,"n_steps_budget":1000.0,"object_pos_end":[0.54142,0.02787,0.01602],"object_pos_start":[0.51689,-0.0152,0.25042],"object_to_goal_dist_end":0.28531,"object_to_goal_dist_start":0.21441,"object_z_max":0.26435,"peak_contact_force":0.12263,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":6177.0,"raw_peak_contact_force":1.99214,"subtask_id":"reach_goal","tcp_end":[0.58315,0.17862,0.43482],"tcp_start":[0.58267,0.17681,0.43461],"tcp_to_object_dist_end":0.44706,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":206.0,"n_steps_budget":1000.0,"object_pos_end":[0.54142,0.02787,0.01602],"object_pos_start":[0.54142,0.02787,0.01602],"object_to_goal_dist_end":0.28531,"object_to_goal_dist_start":0.28531,"object_z_max":0.01602,"peak_contact_force":273003.24057,"phase_name":"lower_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1705.0,"raw_peak_contact_force":0.12263,"subtask_id":"place_goal","tcp_end":[0.58496,0.18519,0.32197],"tcp_start":[0.58533,0.18505,0.32831],"tcp_to_object_dist_end":0.34677,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54142,0.02787,0.01602],"object_pos_start":[0.54142,0.02787,0.01602],"object_to_goal_dist_end":0.28531,"object_to_goal_dist_start":0.28531,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1024.0,"raw_peak_contact_force":0.12263,"subtask_id":"place_goal","tcp_end":[0.58226,0.18394,0.342],"tcp_start":[0.58496,0.18519,0.32197],"tcp_to_object_dist_end":0.36372,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```