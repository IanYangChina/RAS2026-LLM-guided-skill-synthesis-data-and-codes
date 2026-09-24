## Search State

- **Seed**: 4
- **Iteration**: 13 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 12 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 12 | -0.1439 | 0.29 | ❌ rejected |
| 11 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 12 | -0.1400 | 0.30 | ❌ rejected |
| 10 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 10 | 0.0051 | 0.33 | ❌ rejected |
| 9 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 11 | -0.0583 | 0.36 | ❌ rejected |
| 8 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 11 | -0.0481 | 0.36 | ❌ rejected |

**Proposal policy**: task_score is 0.29 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=-0.144) — your mutation base

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

- **Composite score**: -0.144
- **task_score** (E): 0.291
- **fitness_score**: 0.606  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.750

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_object | 1.00 | 1.00 | 0.0949 |
| descend_to_object | 1.00 | 1.00 | 0.1522 |
| grasp | 1.00 | 1.00 | 0.0133 |
| lift | 1.00 | 1.00 | 0.1259 |
| transport_to_goal | 1.00 | 1.00 | 0.0085 |
| lower_to_place | 1.00 | 1.00 | 0.0036 |
| release | 1.00 | 1.00 | 0.0201 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.518, 0.003, 0.209) | (0.526, 0.005, 0.030)→(0.526, 0.005, 0.026) | 0.246→0.249 | 1.00 / 4.000 | 43.853 | 0.138 |
| descend_to_object | descend | 1.00 / step_budget | (0.518, 0.003, 0.209)→(0.521, 0.005, 0.057) | (0.526, 0.005, 0.026)→(0.526, 0.005, 0.026) | 0.249→0.249 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp | grasp | 1.00 / step_budget | (0.521, 0.005, 0.057)→(0.512, 0.005, 0.047) | (0.526, 0.005, 0.026)→(0.526, 0.005, 0.026) | 0.249→0.249 | 1.00 / 38.667 | 0.149 | 0.192 |
| lift | lift | 1.00 / step_budget | (0.512, 0.005, 0.047)→(0.517, 0.005, 0.173) | (0.526, 0.005, 0.026)→(0.523, 0.005, 0.142) | 0.249→0.199 | 1.00 / 26.000 | 0.098 | 0.399 |
| transport_to_goal | approach | 1.00 / step_budget | (0.603, 0.165, 0.312)→(0.607, 0.169, 0.318) | (0.523, 0.005, 0.142)→(0.575, 0.080, 0.016) | 0.199→0.198 | 1.00 / 8.333 | 97502.004 | 1.826 |
| lower_to_place | descend | 1.00 / step_budget | (0.605, 0.171, 0.237)→(0.606, 0.171, 0.234) | (0.575, 0.080, 0.016)→(0.575, 0.080, 0.016) | 0.198→0.198 | 1.00 / 8.333 | 91000.112 | 0.123 |
| release | release | 1.00 / step_budget | (0.606, 0.171, 0.234)→(0.601, 0.170, 0.253) | (0.575, 0.080, 0.016)→(0.575, 0.080, 0.016) | 0.198→0.198 | 1.00 / 4.000 | 0.123 | 0.123 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.430
- phase_score: 0.519
- phase_breakdown.place_goal_score: 0.329
- phase_breakdown.reach_goal_score: 0.781
- phase_breakdown.reach_object_score: 0.386
- phase_breakdown.grasp_object_score: 0.660
- phase_breakdown.lift_object_score: 0.468
- grasp_place_fitness: 0.677

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.677
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.430
- **Median Q (composite search score)**: -0.141
- **K-run variance**: 0.0035
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.371


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.26066,"average_solve_count":211.0,"average_success_count":211.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_speed":0.19633,"approach_object.approach_tolerance":0.01917,"descend_to_object.descend_speed":0.11464,"descend_to_object.grasp_height":0.01006,"lift.lift_height":0.18147,"lift.lift_speed":0.05907,"lower_to_place.lower_speed":0.13351,"lower_to_place.place_height":0.0513,"release.release_time":0.30699,"transport_to_goal.transport_height":0.10483,"transport_to_goal.transport_speed":0.10316,"transport_to_goal.transport_tolerance":0.02914},"optimized_scores":{"best_composite_score":-0.14106,"best_fitness_score":0.60894,"best_task_score":0.29047},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":2848.0,"contact_point_centroid":[0.61643,0.10555,-0.0024],"force_p95":0.12595,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.13245,"mean_force":0.13989,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.63078,0.13849,0.2689]},{"body_a":"world","body_b":"grasp_target","contact_count":88.0,"contact_point_centroid":[0.54199,0.00082,-0.0014],"force_p95":0.34099,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.41397,"mean_force":0.10106,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52868,0.00083,0.04546]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":17136.0,"contact_point_centroid":[0.53524,-0.01838,0.14388],"force_p95":0.08443,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28544,"mean_force":0.05673,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.53412,0.00071,0.14225]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":18159.0,"contact_point_centroid":[0.53554,0.01973,0.14569],"force_p95":0.07903,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27184,"mean_force":0.0536,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.53423,0.00071,0.14402]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4375.0,"contact_point_centroid":[0.56338,0.05501,0.20183],"force_p95":0.11838,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27076,"mean_force":0.0747,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.55845,0.03644,0.2021]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3904.0,"contact_point_centroid":[0.56205,0.01607,0.20083],"force_p95":0.14051,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23328,"mean_force":0.08264,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.55727,0.03479,0.20094]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.54431,0.00103,-0.00203],"force_p95":0.13234,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.15412,"mean_force":0.12548,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.53089,0.00088,0.04579]},{"body_a":"world","body_b":"grasp_target","contact_count":876.0,"contact_point_centroid":[0.54431,0.00113,-0.00185],"force_p95":0.13713,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12318,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.51564,0.00043,0.24869]},{"body_a":"world","body_b":"grasp_target","contact_count":1036.0,"contact_point_centroid":[0.54431,0.00113,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_object","phase_type":"descend","tcp_position_centroid":[0.53499,0.00094,0.12574]},{"body_a":"world","body_b":"grasp_target","contact_count":1836.0,"contact_point_centroid":[0.61638,0.10558,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"lower_to_place","phase_type":"descend","tcp_position_centroid":[0.64019,0.15364,0.25396]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.61638,0.10558,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.63708,0.15301,0.2472]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4119.0,"contact_point_centroid":[0.53076,-0.01835,0.04708],"force_p95":0.07631,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11899,"mean_force":0.05178,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.52969,0.00086,0.04439]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4878.0,"contact_point_centroid":[0.5307,0.01993,0.0462],"force_p95":0.06837,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09384,"mean_force":0.04468,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.5297,0.00086,0.04439]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2831.0,"contact_point_centroid":[0.63313,0.14107,0.27262],"force_p95":0.01105,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01656,"mean_force":0.01057,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.63257,0.14105,0.27041]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1964.0,"contact_point_centroid":[0.64066,0.15367,0.25623],"force_p95":0.01097,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01283,"mean_force":0.01043,"phase_index":5.0,"phase_name":"lower_to_place","phase_type":"descend","tcp_position_centroid":[0.64019,0.15364,0.25394]},{"body_a":"left_finger","body_b":"right_finger","contact_count":220.0,"contact_point_centroid":[0.63924,0.15369,0.24649],"force_p95":0.01097,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01099,"mean_force":0.0101,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.63895,0.15365,0.24409]}],"total_contact_groups":16},"final_pose_error":0.01011,"key_states":{"actual_goal_position":[0.64762,0.15808,0.1911],"final_object_position":[0.61638,0.10558,0.01602],"final_tcp_position":[0.64041,0.15397,0.24817],"realised_goal_position":[0.64762,0.15808,0.1911],"realised_object_initial_position":[0.54431,0.00113,0.03]},"peak_contact_force":9748.61102,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":220.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.03],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.24751,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":876.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.53339,0.00089,0.19565],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.16999,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":259.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.12262,"phase_name":"descend_to_object","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1036.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_object","tcp_end":[0.53852,0.00102,0.05519],"tcp_start":[0.53339,0.00089,0.19565],"tcp_to_object_dist_end":0.02974,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54421,0.00077,0.02586],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25049,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.13071,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10797.0,"raw_peak_contact_force":0.15412,"subtask_id":"grasp_object","tcp_end":[0.52966,0.00086,0.04435],"tcp_start":[0.53852,0.00102,0.05519],"tcp_to_object_dist_end":0.02353,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":34.0,"n_steps":540.0,"n_steps_budget":1000.0,"object_pos_end":[0.54102,0.00079,0.15508],"object_pos_start":[0.54421,0.00077,0.02586],"object_to_goal_dist_end":0.1934,"object_to_goal_dist_start":0.25049,"object_z_max":0.16489,"peak_contact_force":0.08816,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":35383.0,"raw_peak_contact_force":0.41397,"subtask_id":"lift_object","tcp_end":[0.53567,0.00065,0.1817],"tcp_start":[0.52966,0.00086,0.04435],"tcp_to_object_dist_end":0.02715,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":748.0,"n_steps_budget":1000.0,"object_pos_end":[0.61638,0.10558,0.01602],"object_pos_start":[0.54102,0.00079,0.15508],"object_to_goal_dist_end":0.18544,"object_to_goal_dist_start":0.1934,"object_z_max":0.19787,"peak_contact_force":9748.61102,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":13958.0,"raw_peak_contact_force":2.13245,"subtask_id":"reach_goal","tcp_end":[0.64096,0.15252,0.27804],"tcp_start":[0.63651,0.14745,0.27161],"tcp_to_object_dist_end":0.26733,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":59.0,"n_steps_budget":1000.0,"object_pos_end":[0.61638,0.10558,0.01602],"object_pos_start":[0.61638,0.10558,0.01602],"object_to_goal_dist_end":0.18544,"object_to_goal_dist_start":0.18544,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"lower_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3800.0,"raw_peak_contact_force":0.12263,"subtask_id":"place_goal","tcp_end":[0.64041,0.15397,0.24817],"tcp_start":[0.63982,0.15356,0.25168],"tcp_to_object_dist_end":0.23836,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.61638,0.10558,0.01602],"object_pos_start":[0.61638,0.10558,0.01602],"object_to_goal_dist_end":0.18544,"object_to_goal_dist_start":0.18544,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1020.0,"raw_peak_contact_force":0.12263,"subtask_id":"place_goal","tcp_end":[0.63605,0.15264,0.26633],"tcp_start":[0.64041,0.15397,0.24817],"tcp_to_object_dist_end":0.25546,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `349f925163f8e9284ad51ad55d38356f2e3c8deb4dc54e8ff12260e5f6d4b0f8`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.3242,"average_solve_count":219.0,"average_success_count":219.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_speed":0.15272,"approach_object.approach_tolerance":0.04811,"descend_to_object.descend_speed":0.10904,"descend_to_object.grasp_height":0.01064,"lift.lift_height":0.14331,"lift.lift_speed":0.23036,"lower_to_place.lower_speed":0.03246,"lower_to_place.place_height":0.02609,"release.release_time":0.20641,"transport_to_goal.transport_height":0.17664,"transport_to_goal.transport_speed":0.26853,"transport_to_goal.transport_tolerance":0.04947},"optimized_scores":{"best_composite_score":-0.07261,"best_fitness_score":0.67739,"best_task_score":0.42969},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":3112.0,"contact_point_centroid":[0.56962,0.09765,-0.00232],"force_p95":0.12907,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.60154,"mean_force":0.13835,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.58433,0.1526,0.24946]},{"body_a":"world","body_b":"grasp_target","contact_count":80.0,"contact_point_centroid":[0.52899,0.02767,-0.00153],"force_p95":0.38744,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.4565,"mean_force":0.07223,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.51524,0.02827,0.04663]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":10093.0,"contact_point_centroid":[0.52458,0.0472,0.11698],"force_p95":0.10666,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30823,"mean_force":0.07429,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.51995,0.02847,0.11579]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":9597.0,"contact_point_centroid":[0.52468,0.00971,0.11882],"force_p95":0.10931,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28742,"mean_force":0.076,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52012,0.02848,0.11817]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1520.0,"contact_point_centroid":[0.53391,0.02601,0.15414],"force_p95":0.17152,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24785,"mean_force":0.09,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.5278,0.04464,0.15513]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53059,0.03062,-0.0022],"force_p95":0.17813,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.23715,"mean_force":0.13709,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.51749,0.02843,0.04642]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1803.0,"contact_point_centroid":[0.53526,0.06575,0.15599],"force_p95":0.12184,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20409,"mean_force":0.07723,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.52914,0.04739,0.15742]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4153.0,"contact_point_centroid":[0.51724,0.00912,0.04721],"force_p95":0.08156,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1438,"mean_force":0.05147,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.51632,0.02835,0.04508]},{"body_a":"world","body_b":"grasp_target","contact_count":316.0,"contact_point_centroid":[0.5305,0.03079,-0.0016],"force_p95":0.13825,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12436,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.5089,0.00813,0.26565]},{"body_a":"world","body_b":"grasp_target","contact_count":1236.0,"contact_point_centroid":[0.5305,0.03079,-0.00199],"force_p95":0.12264,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12264,"mean_force":0.12258,"phase_index":1.0,"phase_name":"descend_to_object","phase_type":"descend","tcp_position_centroid":[0.52062,0.02346,0.13826]},{"body_a":"world","body_b":"grasp_target","contact_count":2532.0,"contact_point_centroid":[0.56965,0.09758,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"lower_to_place","phase_type":"descend","tcp_position_centroid":[0.59373,0.17475,0.16796]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.56965,0.09758,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.58814,0.17361,0.14161]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5376.0,"contact_point_centroid":[0.51718,0.04756,0.04771],"force_p95":0.07482,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.078,"mean_force":0.04166,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.51633,0.02835,0.04509]},{"body_a":"left_finger","body_b":"right_finger","contact_count":3078.0,"contact_point_centroid":[0.58698,0.15664,0.2551],"force_p95":0.01106,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01509,"mean_force":0.01058,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.58643,0.15661,0.25288]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2693.0,"contact_point_centroid":[0.59431,0.1748,0.17028],"force_p95":0.011,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01278,"mean_force":0.01048,"phase_index":5.0,"phase_name":"lower_to_place","phase_type":"descend","tcp_position_centroid":[0.59374,0.17475,0.1681]},{"body_a":"left_finger","body_b":"right_finger","contact_count":222.0,"contact_point_centroid":[0.5919,0.17462,0.13965],"force_p95":0.01101,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01102,"mean_force":0.01007,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.59097,0.17456,0.13755]}],"total_contact_groups":16},"final_pose_error":0.0116,"key_states":{"actual_goal_position":[0.60153,0.17858,0.10809],"final_object_position":[0.56965,0.09758,0.01602],"final_tcp_position":[0.59301,0.17515,0.14126],"realised_goal_position":[0.60153,0.17858,0.10809],"realised_object_initial_position":[0.5305,0.03079,0.03]},"peak_contact_force":9748.69513,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":80.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02596],"object_pos_start":[0.5305,0.03079,0.03],"object_to_goal_dist_end":0.18339,"object_to_goal_dist_start":0.18162,"object_z_max":0.03,"peak_contact_force":69.57047,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":316.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.51836,0.0181,0.22418],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.19899,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":309.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.02596],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18339,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_object","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1236.0,"raw_peak_contact_force":0.12264,"subtask_id":"grasp_object","tcp_end":[0.52494,0.02886,0.05534],"tcp_start":[0.51836,0.0181,0.22418],"tcp_to_object_dist_end":0.02991,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.5305,0.0291,0.0253],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18506,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.17249,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11329.0,"raw_peak_contact_force":0.23715,"subtask_id":"grasp_object","tcp_end":[0.51629,0.02835,0.04505],"tcp_start":[0.52494,0.02886,0.05534],"tcp_to_object_dist_end":0.02434,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":26.0,"n_steps":341.0,"n_steps_budget":600.0,"object_pos_end":[0.52876,0.0289,0.11355],"object_pos_start":[0.5305,0.0291,0.0253],"object_to_goal_dist_end":0.16652,"object_to_goal_dist_start":0.18506,"object_z_max":0.12423,"peak_contact_force":0.0928,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":19770.0,"raw_peak_contact_force":0.4565,"subtask_id":"lift_object","tcp_end":[0.52105,0.0285,0.14332],"tcp_start":[0.51629,0.02835,0.04505],"tcp_to_object_dist_end":0.03076,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":618.0,"n_steps_budget":1000.0,"object_pos_end":[0.56965,0.09758,0.01602],"object_pos_start":[0.52876,0.0289,0.11355],"object_to_goal_dist_end":0.1267,"object_to_goal_dist_start":0.16652,"object_z_max":0.14108,"peak_contact_force":9748.69513,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":9513.0,"raw_peak_contact_force":1.60154,"subtask_id":"reach_goal","tcp_end":[0.59501,0.17271,0.26681],"tcp_start":[0.59185,0.16838,0.26047],"tcp_to_object_dist_end":0.26303,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":233.0,"n_steps_budget":1000.0,"object_pos_end":[0.56965,0.09758,0.01602],"object_pos_start":[0.56965,0.09758,0.01602],"object_to_goal_dist_end":0.1267,"object_to_goal_dist_start":0.1267,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"lower_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":5225.0,"raw_peak_contact_force":0.12263,"subtask_id":"place_goal","tcp_end":[0.59301,0.17515,0.14126],"tcp_start":[0.59258,0.17491,0.14476],"tcp_to_object_dist_end":0.14916,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.56965,0.09758,0.01602],"object_pos_start":[0.56965,0.09758,0.01602],"object_to_goal_dist_end":0.1267,"object_to_goal_dist_start":0.1267,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1022.0,"raw_peak_contact_force":0.12263,"subtask_id":"place_goal","tcp_end":[0.58643,0.17303,0.16136],"tcp_start":[0.59301,0.17515,0.14126],"tcp_to_object_dist_end":0.16461,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `a1798e4fdcacfe8740623adfe3f78d2bc74e0d14c8233e64f02c40cf2a534ecc`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.36564,"average_solve_count":227.0,"average_success_count":227.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_speed":0.19939,"approach_object.approach_tolerance":0.02914,"descend_to_object.descend_speed":0.13229,"descend_to_object.grasp_height":0.01634,"lift.lift_height":0.19356,"lift.lift_speed":0.06412,"lower_to_place.lower_speed":0.03769,"lower_to_place.place_height":0.0562,"release.release_time":0.2509,"transport_to_goal.transport_height":0.18062,"transport_to_goal.transport_speed":0.245,"transport_to_goal.transport_tolerance":0.02124},"optimized_scores":{"best_composite_score":-0.218,"best_fitness_score":0.532,"best_task_score":0.15283},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":4267.0,"contact_point_centroid":[0.53792,0.03538,-0.00224],"force_p95":0.12399,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.74331,"mean_force":0.13402,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.56302,0.13701,0.36075]},{"body_a":"world","body_b":"grasp_target","contact_count":87.0,"contact_point_centroid":[0.50178,-0.01472,-0.00141],"force_p95":0.27732,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.32608,"mean_force":0.0725,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.49025,-0.01486,0.05356]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8803.0,"contact_point_centroid":[0.49759,0.00344,0.14623],"force_p95":0.12942,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30639,"mean_force":0.09813,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.49425,-0.01492,0.14949]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":9306.0,"contact_point_centroid":[0.49721,-0.03323,0.14494],"force_p95":0.12947,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29584,"mean_force":0.09346,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.49416,-0.01492,0.14826]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":806.0,"contact_point_centroid":[0.50482,0.01485,0.19959],"force_p95":0.15856,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23369,"mean_force":0.1122,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.49919,-0.00336,0.20461]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50382,-0.01559,-0.00208],"force_p95":0.14421,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.18497,"mean_force":0.12895,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.49239,-0.01489,0.05342]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":931.0,"contact_point_centroid":[0.50539,-0.01948,0.20152],"force_p95":0.13205,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17325,"mean_force":0.09472,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.49989,-0.0016,0.20641]},{"body_a":"world","body_b":"grasp_target","contact_count":524.0,"contact_point_centroid":[0.50382,-0.01567,-0.00176],"force_p95":0.13797,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12356,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.50041,-0.00525,0.25648]},{"body_a":"world","body_b":"grasp_target","contact_count":1080.0,"contact_point_centroid":[0.50382,-0.01567,-0.00199],"force_p95":0.12264,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12264,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_object","phase_type":"descend","tcp_position_centroid":[0.49932,-0.01309,0.13473]},{"body_a":"world","body_b":"grasp_target","contact_count":2328.0,"contact_point_centroid":[0.53797,0.03538,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":5.0,"phase_name":"lower_to_place","phase_type":"descend","tcp_position_centroid":[0.58359,0.18447,0.33098]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.53797,0.03538,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.581,0.18394,0.31239]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3150.0,"contact_point_centroid":[0.49295,0.00396,0.05054],"force_p95":0.09746,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11169,"mean_force":0.06548,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.49128,-0.01488,0.05222]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3721.0,"contact_point_centroid":[0.49237,-0.03369,0.05074],"force_p95":0.09147,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09319,"mean_force":0.0574,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.49128,-0.01488,0.05222]},{"body_a":"left_finger","body_b":"right_finger","contact_count":4356.0,"contact_point_centroid":[0.5656,0.14159,0.36813],"force_p95":0.01104,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01631,"mean_force":0.01049,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.56514,0.14159,0.36586]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2494.0,"contact_point_centroid":[0.58409,0.1845,0.33323],"force_p95":0.01097,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01282,"mean_force":0.01041,"phase_index":5.0,"phase_name":"lower_to_place","phase_type":"descend","tcp_position_centroid":[0.58359,0.18447,0.33098]},{"body_a":"left_finger","body_b":"right_finger","contact_count":226.0,"contact_point_centroid":[0.58314,0.1846,0.31031],"force_p95":0.01092,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01094,"mean_force":0.0099,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.58227,0.18456,0.30843]}],"total_contact_groups":16},"final_pose_error":0.00885,"key_states":{"actual_goal_position":[0.58691,0.18745,0.24812],"final_object_position":[0.53797,0.03538,0.01602],"final_tcp_position":[0.5832,0.18488,0.31192],"realised_goal_position":[0.58691,0.18745,0.24812],"realised_object_initial_position":[0.50382,-0.01567,0.03]},"peak_contact_force":273008.70555,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":132.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.03],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.30942,"object_z_max":0.03,"peak_contact_force":61.86612,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":524.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.5009,-0.01126,0.20818],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.18223,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":270.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_object","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1080.0,"raw_peak_contact_force":0.12264,"subtask_id":"grasp_object","tcp_end":[0.49955,-0.01496,0.06155],"tcp_start":[0.5009,-0.01126,0.20818],"tcp_to_object_dist_end":0.03579,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":32.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50373,-0.01508,0.02563],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31215,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.14333,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":8671.0,"raw_peak_contact_force":0.18497,"subtask_id":"grasp_object","tcp_end":[0.49125,-0.01487,0.05218],"tcp_start":[0.49955,-0.01496,0.06155],"tcp_to_object_dist_end":0.02934,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":18.0,"n_steps":508.0,"n_steps_budget":1000.0,"object_pos_end":[0.5003,-0.0151,0.15659],"object_pos_start":[0.50373,-0.01508,0.02563],"object_to_goal_dist_end":0.23854,"object_to_goal_dist_start":0.31215,"object_z_max":0.16608,"peak_contact_force":0.11325,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":18196.0,"raw_peak_contact_force":0.32608,"subtask_id":"lift_object","tcp_end":[0.49562,-0.01494,0.1941],"tcp_start":[0.49125,-0.01487,0.05218],"tcp_to_object_dist_end":0.0378,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":863.0,"n_steps_budget":1000.0,"object_pos_end":[0.53797,0.03538,0.01602],"object_pos_start":[0.5003,-0.0151,0.15659],"object_to_goal_dist_end":0.28176,"object_to_goal_dist_start":0.23854,"object_z_max":0.17941,"peak_contact_force":273008.70555,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":10360.0,"raw_peak_contact_force":1.74331,"subtask_id":"reach_goal","tcp_end":[0.584,0.18213,0.40984],"tcp_start":[0.58195,0.17832,0.40334],"tcp_to_object_dist_end":0.42279,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":182.0,"n_steps_budget":1000.0,"object_pos_end":[0.53797,0.03538,0.01602],"object_pos_start":[0.53797,0.03538,0.01602],"object_to_goal_dist_end":0.28176,"object_to_goal_dist_start":0.28176,"object_z_max":0.01602,"peak_contact_force":273000.0909,"phase_name":"lower_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4822.0,"raw_peak_contact_force":0.12263,"subtask_id":"place_goal","tcp_end":[0.5832,0.18488,0.31192],"tcp_start":[0.58305,0.18468,0.31547],"tcp_to_object_dist_end":0.3346,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53797,0.03538,0.01602],"object_pos_start":[0.53797,0.03538,0.01602],"object_to_goal_dist_end":0.28176,"object_to_goal_dist_start":0.28176,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1026.0,"raw_peak_contact_force":0.12263,"subtask_id":"place_goal","tcp_end":[0.58038,0.1836,0.33211],"tcp_start":[0.5832,0.18488,0.31192],"tcp_to_object_dist_end":0.35168,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```