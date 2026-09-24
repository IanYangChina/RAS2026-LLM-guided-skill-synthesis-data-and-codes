## Search State

- **Seed**: 4
- **Iteration**: 12 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 11 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 12 | -0.1400 | 0.30 | ❌ rejected |
| 10 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 10 | 0.0051 | 0.33 | ❌ rejected |
| 9 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 11 | -0.0583 | 0.36 | ❌ rejected |
| 8 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 11 | -0.0481 | 0.36 | ❌ rejected |
| 7 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | force_threshold_switch | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | force_exceeded | time_limit | 11 | 0.0826 | 0.35 | ❌ rejected |

**Proposal policy**: task_score is 0.30 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=-0.140) — your mutation base

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

- **Composite score**: -0.140
- **task_score** (E): 0.299
- **fitness_score**: 0.610  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.750

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_object | 1.00 | 1.00 | 0.1087 |
| descend_to_object | 1.00 | 1.00 | 0.1385 |
| grasp | 1.00 | 1.00 | 0.0133 |
| lift | 1.00 | 1.00 | 0.1331 |
| transport_to_goal | 1.00 | 0.67 | 0.0725 |
| lower_to_place | 0.00 | 0.67 | 0.0002 |
| release | 1.00 | 1.00 | 0.0197 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.518, 0.005, 0.196) | (0.526, 0.005, 0.030)→(0.526, 0.005, 0.026) | 0.246→0.249 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_to_object | descend | 1.00 / step_budget | (0.518, 0.005, 0.196)→(0.521, 0.005, 0.058) | (0.526, 0.005, 0.026)→(0.526, 0.005, 0.026) | 0.249→0.249 | 1.00 / 4.000 | 42.225 | 0.123 |
| grasp | grasp | 1.00 / step_budget | (0.521, 0.005, 0.058)→(0.512, 0.005, 0.047) | (0.526, 0.005, 0.026)→(0.526, 0.005, 0.026) | 0.249→0.249 | 1.00 / 43.000 | 0.141 | 0.183 |
| lift | lift | 1.00 / step_budget | (0.512, 0.005, 0.047)→(0.521, 0.005, 0.180) | (0.526, 0.005, 0.026)→(0.531, 0.004, 0.152) | 0.249→0.205 | 1.00 / 26.667 | 0.060 | 0.355 |
| transport_to_goal | approach | 1.00 / step_budget | (0.584, 0.121, 0.334)→(0.608, 0.168, 0.383) | (0.531, 0.004, 0.152)→(0.579, 0.090, 0.101) | 0.205→0.225 | 0.67 / 6.000 | 90997.576 | 1.520 |
| lower_to_place | descend | 0.00 / guard_failure | (0.608, 0.169, 0.370)→(0.608, 0.169, 0.369) | (0.579, 0.090, 0.101)→(0.583, 0.090, 0.037) | 0.225→0.183 | 0.67 / 5.333 | 3249.589 | 0.082 |
| release | release | 1.00 / step_budget | (0.608, 0.169, 0.369)→(0.607, 0.168, 0.389) | (0.583, 0.090, 0.035)→(0.581, 0.089, 0.016) | 0.184→0.202 | 1.00 / 4.000 | 0.123 | 0.898 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.530
- phase_score: 0.648
- phase_breakdown.place_goal_score: 0.051
- phase_breakdown.reach_goal_score: 0.242
- phase_breakdown.reach_object_score: 0.799
- phase_breakdown.grasp_object_score: 0.660
- phase_breakdown.lift_object_score: 0.905
- grasp_place_fitness: 0.729

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.729
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.530
- **Median Q (composite search score)**: -0.188
- **K-run variance**: 0.0071
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.361


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.49189,"average_solve_count":185.0,"average_success_count":185.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_speed":0.27077,"approach_object.approach_tolerance":0.02965,"descend_to_object.descend_speed":0.07821,"descend_to_object.grasp_height":0.01482,"lift.lift_height":0.21236,"lift.lift_speed":0.12388,"lower_to_place.lower_speed":0.13388,"lower_to_place.place_height":0.0633,"release.release_time":0.27047,"transport_to_goal.transport_height_offset":0.256,"transport_to_goal.transport_speed":0.13005,"transport_to_goal.transport_tolerance":0.02723},"optimized_scores":{"best_composite_score":-0.21061,"best_fitness_score":0.53939,"best_task_score":0.16212},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":3500.0,"contact_point_centroid":[0.55613,-0.03021,-0.00231],"force_p95":0.12603,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.83469,"mean_force":0.13623,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.5982,0.08766,0.33764]},{"body_a":"world","body_b":"grasp_target","contact_count":79.0,"contact_point_centroid":[0.54214,0.00073,-0.00131],"force_p95":0.34643,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.3576,"mean_force":0.07091,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52822,0.00083,0.05013]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":7177.0,"contact_point_centroid":[0.53617,-0.01795,0.12384],"force_p95":0.12809,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27414,"mean_force":0.08008,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.53199,0.0008,0.12393]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":7438.0,"contact_point_centroid":[0.53592,0.01953,0.12043],"force_p95":0.12921,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27186,"mean_force":0.07717,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.5317,0.0008,0.12026]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.54431,0.00109,-0.00203],"force_p95":0.13317,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.16025,"mean_force":0.12558,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.5305,0.00087,0.0502]},{"body_a":"world","body_b":"grasp_target","contact_count":568.0,"contact_point_centroid":[0.54431,0.00113,-0.00178],"force_p95":0.13791,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12349,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.51464,0.00039,0.25482]},{"body_a":"world","body_b":"grasp_target","contact_count":1100.0,"contact_point_centroid":[0.54431,0.00113,-0.00199],"force_p95":0.12264,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12264,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_object","phase_type":"descend","tcp_position_centroid":[0.53329,0.00089,0.13244]},{"body_a":"world","body_b":"grasp_target","contact_count":8.0,"contact_point_centroid":[0.55608,-0.03019,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"lower_to_place","phase_type":"descend","tcp_position_centroid":[0.64454,0.15334,0.42893]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.55608,-0.03019,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.64465,0.15317,0.42842]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":19.0,"contact_point_centroid":[0.54741,-0.01308,0.21197],"force_p95":0.10099,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10099,"mean_force":0.0407,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.54008,0.00087,0.219]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4365.0,"contact_point_centroid":[0.5302,-0.01834,0.04981],"force_p95":0.07259,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09664,"mean_force":0.04937,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.52931,0.00085,0.0488]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4876.0,"contact_point_centroid":[0.53038,0.01998,0.04957],"force_p95":0.06855,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08559,"mean_force":0.04463,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.52931,0.00085,0.0488]},{"body_a":"left_finger","body_b":"right_finger","contact_count":3556.0,"contact_point_centroid":[0.6011,0.09125,0.34502],"force_p95":0.01101,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01583,"mean_force":0.01051,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.60072,0.09125,0.34278]},{"body_a":"left_finger","body_b":"right_finger","contact_count":228.0,"contact_point_centroid":[0.64501,0.15341,0.42799],"force_p95":0.01092,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01094,"mean_force":0.00979,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.64448,0.15339,0.42557]},{"body_a":"left_finger","body_b":"right_finger","contact_count":9.0,"contact_point_centroid":[0.64593,0.15336,0.43181],"force_p95":0.01086,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01086,"mean_force":0.01013,"phase_index":5.0,"phase_name":"lower_to_place","phase_type":"descend","tcp_position_centroid":[0.64454,0.15334,0.42894]}],"total_contact_groups":15},"final_pose_error":0.17453,"key_states":{"actual_goal_position":[0.64762,0.15808,0.1911],"final_object_position":[0.55608,-0.03019,0.01602],"final_tcp_position":[0.64455,0.1534,0.42885],"realised_goal_position":[0.64762,0.15808,0.1911],"realised_object_initial_position":[0.54431,0.00113,0.03]},"peak_contact_force":272989.24266,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":143.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.03],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.24751,"object_z_max":0.03,"peak_contact_force":0.12264,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":568.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.53081,0.0008,0.20574],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.18023,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":275.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":45.41133,"phase_name":"descend_to_object","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1100.0,"raw_peak_contact_force":0.12264,"subtask_id":"grasp_object","tcp_end":[0.53808,0.00101,0.05959],"tcp_start":[0.53081,0.0008,0.20574],"tcp_to_object_dist_end":0.03414,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":42.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54422,0.00088,0.02585],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25043,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.13258,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11041.0,"raw_peak_contact_force":0.16025,"subtask_id":"grasp_object","tcp_end":[0.52928,0.00085,0.04876],"tcp_start":[0.53808,0.00101,0.05959],"tcp_to_object_dist_end":0.02735,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":566.0,"n_steps_budget":960.0,"object_pos_end":[0.55078,-0.00329,0.1813],"object_pos_start":[0.54422,0.00088,0.02585],"object_to_goal_dist_end":0.18846,"object_to_goal_dist_start":0.25043,"object_z_max":0.18213,"peak_contact_force":0.01956,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":14694.0,"raw_peak_contact_force":0.3576,"subtask_id":"lift_object","tcp_end":[0.54,0.00082,0.21871],"tcp_start":[0.52928,0.00085,0.04876],"tcp_to_object_dist_end":0.03915,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":961.0,"n_steps_budget":1000.0,"object_pos_end":[0.55608,-0.03019,0.01602],"object_pos_start":[0.55078,-0.00329,0.1813],"object_to_goal_dist_end":0.27291,"object_to_goal_dist_start":0.18846,"object_z_max":0.1813,"peak_contact_force":0.12263,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":7075.0,"raw_peak_contact_force":1.83469,"subtask_id":"reach_goal","tcp_end":[0.64455,0.15332,0.42895],"tcp_start":[0.644,0.15248,0.42914],"tcp_to_object_dist_end":0.46045,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":2.0,"n_steps_budget":1000.0,"object_pos_end":[0.55608,-0.03019,0.01602],"object_pos_start":[0.55608,-0.03019,0.01602],"object_to_goal_dist_end":0.27291,"object_to_goal_dist_start":0.27291,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"lower_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":17.0,"raw_peak_contact_force":0.12263,"subtask_id":"place_goal","tcp_end":[0.64455,0.1534,0.42885],"tcp_start":[0.64453,0.15336,0.42891],"tcp_to_object_dist_end":0.46039,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.55608,-0.03019,0.01602],"object_pos_start":[0.55608,-0.03019,0.01602],"object_to_goal_dist_end":0.27291,"object_to_goal_dist_start":0.27291,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1028.0,"raw_peak_contact_force":0.12263,"subtask_id":"place_goal","tcp_end":[0.64503,0.15309,0.44749],"tcp_start":[0.64455,0.1534,0.42885],"tcp_to_object_dist_end":0.47714,"terminated_normally":true,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `349f925163f8e9284ad51ad55d38356f2e3c8deb4dc54e8ff12260e5f6d4b0f8`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.83333,"average_solve_count":342.0,"average_success_count":342.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_speed":0.22851,"approach_object.approach_tolerance":0.0115,"descend_to_object.descend_speed":0.02055,"descend_to_object.grasp_height":0.01002,"lift.lift_height":0.17415,"lift.lift_speed":0.02487,"lower_to_place.lower_speed":0.15158,"lower_to_place.place_height":0.11415,"release.release_time":0.19493,"transport_to_goal.transport_height_offset":0.23703,"transport_to_goal.transport_speed":0.06918,"transport_to_goal.transport_tolerance":0.04412},"optimized_scores":{"best_composite_score":-0.02148,"best_fitness_score":0.72852,"best_task_score":0.53032},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":734.0,"contact_point_centroid":[0.61724,0.15994,-0.0039],"force_p95":0.94324,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.4485,"mean_force":0.21186,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.59351,0.17144,0.28715]},{"body_a":"world","body_b":"grasp_target","contact_count":112.0,"contact_point_centroid":[0.52741,0.02924,-0.00162],"force_p95":0.31641,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.35851,"mean_force":0.14377,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.5154,0.02925,0.04561]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":11000.0,"contact_point_centroid":[0.55753,0.10921,0.24246],"force_p95":0.10099,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30505,"mean_force":0.06634,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.55425,0.09033,0.24182]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":11431.0,"contact_point_centroid":[0.5191,0.04837,0.11074],"force_p95":0.07666,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24513,"mean_force":0.04985,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.51894,0.02927,0.10847]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":10998.0,"contact_point_centroid":[0.55758,0.07257,0.24327],"force_p95":0.1028,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23755,"mean_force":0.06589,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.55478,0.09136,0.24293]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":9979.0,"contact_point_centroid":[0.51912,0.01007,0.11152],"force_p95":0.0797,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22334,"mean_force":0.05506,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.519,0.02927,0.10908]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53055,0.03067,-0.00213],"force_p95":0.1571,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.2181,"mean_force":0.13195,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.51768,0.02941,0.04613]},{"body_a":"world","body_b":"grasp_target","contact_count":1348.0,"contact_point_centroid":[0.5305,0.03079,-0.0019],"force_p95":0.13563,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12299,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.51059,0.0131,0.24404]},{"body_a":"world","body_b":"grasp_target","contact_count":1096.0,"contact_point_centroid":[0.5305,0.03079,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_object","phase_type":"descend","tcp_position_centroid":[0.52319,0.02834,0.12356]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4576.0,"contact_point_centroid":[0.51714,0.0101,0.04734],"force_p95":0.07347,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11456,"mean_force":0.04727,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.51651,0.02933,0.0448]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5487.0,"contact_point_centroid":[0.51685,0.04856,0.04742],"force_p95":0.06897,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07124,"mean_force":0.04065,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.51652,0.02933,0.0448]},{"body_a":"left_finger","body_b":"right_finger","contact_count":64.0,"contact_point_centroid":[0.59526,0.17195,0.28302],"force_p95":0.01568,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0158,"mean_force":0.01194,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.5947,0.17192,0.28125]}],"total_contact_groups":12},"final_pose_error":0.06543,"key_states":{"actual_goal_position":[0.60153,0.17858,0.10809],"final_object_position":[0.61662,0.15994,0.01602],"final_tcp_position":[0.59648,0.17251,0.28719],"realised_goal_position":[0.60153,0.17858,0.10809],"realised_object_initial_position":[0.5305,0.03079,0.03]},"peak_contact_force":81.14225,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":338.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.03],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18162,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1348.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.5235,0.02702,0.18795],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.16212,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":274.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":81.14225,"phase_name":"descend_to_object","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1096.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_object","tcp_end":[0.52514,0.02989,0.05504],"tcp_start":[0.5235,0.02702,0.18795],"tcp_to_object_dist_end":0.02953,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":45.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53047,0.02977,0.02555],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18442,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.15379,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11863.0,"raw_peak_contact_force":0.2181,"subtask_id":"grasp_object","tcp_end":[0.51648,0.02933,0.04476],"tcp_start":[0.52514,0.02989,0.05504],"tcp_to_object_dist_end":0.02377,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":38.0,"n_steps":529.0,"n_steps_budget":1000.0,"object_pos_end":[0.53424,0.0297,0.15751],"object_pos_start":[0.53047,0.02977,0.02555],"object_to_goal_dist_end":0.17069,"object_to_goal_dist_start":0.18442,"object_z_max":0.15726,"peak_contact_force":0.08099,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":21522.0,"raw_peak_contact_force":0.35851,"subtask_id":"lift_object","tcp_end":[0.52569,0.02948,0.18048],"tcp_start":[0.51648,0.02933,0.04476],"tcp_to_object_dist_end":0.02451,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":773.0,"n_steps_budget":1000.0,"object_pos_end":[0.60884,0.16379,0.27239],"object_pos_start":[0.53424,0.0297,0.15751],"object_to_goal_dist_end":0.16513,"object_to_goal_dist_start":0.17069,"object_z_max":0.29085,"peak_contact_force":0.0,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":21998.0,"raw_peak_contact_force":0.30505,"subtask_id":"reach_goal","tcp_end":[0.59569,0.17006,0.3282],"tcp_start":[0.52569,0.02948,0.18048],"tcp_to_object_dist_end":0.05768,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":75.0,"n_steps_budget":1000.0,"object_pos_end":[0.62091,0.16523,0.07821],"object_pos_start":[0.60884,0.16379,0.27239],"object_to_goal_dist_end":0.03803,"object_to_goal_dist_start":0.16513,"object_z_max":0.27239,"peak_contact_force":0.0,"phase_name":"lower_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"place_goal","tcp_end":[0.59648,0.17251,0.28719],"tcp_start":[0.5965,0.17248,0.2877],"tcp_to_object_dist_end":0.21053,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.61662,0.15994,0.01602],"object_pos_start":[0.62107,0.16525,0.07411],"object_to_goal_dist_end":0.09514,"object_to_goal_dist_start":0.0414,"object_z_max":0.07411,"peak_contact_force":0.12289,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":798.0,"raw_peak_contact_force":2.4485,"subtask_id":"place_goal","tcp_end":[0.59287,0.17114,0.3066],"tcp_start":[0.59648,0.17251,0.28719],"tcp_to_object_dist_end":0.29176,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `a1798e4fdcacfe8740623adfe3f78d2bc74e0d14c8233e64f02c40cf2a534ecc`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.36898,"average_solve_count":187.0,"average_success_count":187.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_speed":0.3698,"approach_object.approach_tolerance":0.01501,"descend_to_object.descend_speed":0.07236,"descend_to_object.grasp_height":0.01278,"lift.lift_height":0.13449,"lift.lift_speed":0.03798,"lower_to_place.lower_speed":0.06942,"lower_to_place.place_height":0.02499,"release.release_time":0.32713,"transport_to_goal.transport_height_offset":0.16125,"transport_to_goal.transport_speed":0.38336,"transport_to_goal.transport_tolerance":0.03237},"optimized_scores":{"best_composite_score":-0.18787,"best_fitness_score":0.56213,"best_task_score":0.20437},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":1197.0,"contact_point_centroid":[0.5715,0.13628,-0.00314],"force_p95":0.54839,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.42149,"mean_force":0.16742,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.57094,0.15293,0.35658]},{"body_a":"world","body_b":"grasp_target","contact_count":90.0,"contact_point_centroid":[0.50055,-0.01504,-0.00149],"force_p95":0.33064,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.34789,"mean_force":0.133,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.49005,-0.01509,0.04951]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5736.0,"contact_point_centroid":[0.51826,0.01036,0.1947],"force_p95":0.1278,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24652,"mean_force":0.07008,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.51547,0.02901,0.19508]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6516.0,"contact_point_centroid":[0.49265,0.00409,0.09319],"force_p95":0.07921,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24609,"mean_force":0.0562,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.49293,-0.01511,0.09272]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":7334.0,"contact_point_centroid":[0.49244,-0.03423,0.09387],"force_p95":0.07587,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24333,"mean_force":0.05089,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.49299,-0.01511,0.09323]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5494.0,"contact_point_centroid":[0.51924,0.04997,0.19737],"force_p95":0.13282,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22195,"mean_force":0.07517,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.51644,0.03123,0.19794]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50383,-0.01562,-0.00205],"force_p95":0.1378,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.17202,"mean_force":0.12661,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.49205,-0.01512,0.04987]},{"body_a":"world","body_b":"grasp_target","contact_count":968.0,"contact_point_centroid":[0.50382,-0.01567,-0.00187],"force_p95":0.13691,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12313,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.49941,-0.00622,0.24823]},{"body_a":"world","body_b":"grasp_target","contact_count":1056.0,"contact_point_centroid":[0.50382,-0.01567,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_object","phase_type":"descend","tcp_position_centroid":[0.49871,-0.01408,0.12678]},{"body_a":"world","body_b":"grasp_target","contact_count":8.0,"contact_point_centroid":[0.57148,0.13626,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":5.0,"phase_name":"lower_to_place","phase_type":"descend","tcp_position_centroid":[0.58344,0.18181,0.39198]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.57148,0.13626,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.58243,0.18133,0.39293]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4355.0,"contact_point_centroid":[0.49143,0.00409,0.04968],"force_p95":0.07303,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11276,"mean_force":0.04945,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.49093,-0.0151,0.04867]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4898.0,"contact_point_centroid":[0.49138,-0.03424,0.04954],"force_p95":0.06918,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08605,"mean_force":0.04457,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.49094,-0.0151,0.04867]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1128.0,"contact_point_centroid":[0.57295,0.15662,0.3637],"force_p95":0.01263,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01631,"mean_force":0.01077,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.5726,0.15662,0.36138]},{"body_a":"left_finger","body_b":"right_finger","contact_count":225.0,"contact_point_centroid":[0.58327,0.18177,0.39152],"force_p95":0.01089,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01091,"mean_force":0.00993,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.58294,0.18175,0.3891]},{"body_a":"left_finger","body_b":"right_finger","contact_count":10.0,"contact_point_centroid":[0.58542,0.18183,0.39382],"force_p95":0.00962,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.00962,"mean_force":0.0096,"phase_index":5.0,"phase_name":"lower_to_place","phase_type":"descend","tcp_position_centroid":[0.58344,0.18181,0.39198]}],"total_contact_groups":16},"final_pose_error":0.11901,"key_states":{"actual_goal_position":[0.58691,0.18745,0.24812],"final_object_position":[0.57148,0.13626,0.01602],"final_tcp_position":[0.58337,0.18185,0.39193],"realised_goal_position":[0.58691,0.18745,0.24812],"realised_object_initial_position":[0.50382,-0.01567,0.03]},"peak_contact_force":272992.60669,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":243.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.03],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.30942,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":968.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.50008,-0.01305,0.19416],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.1682,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":264.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.12262,"phase_name":"descend_to_object","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1056.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_object","tcp_end":[0.49926,-0.01519,0.05801],"tcp_start":[0.50008,-0.01305,0.19416],"tcp_to_object_dist_end":0.03231,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":42.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50374,-0.01524,0.0258],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31213,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.13675,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11053.0,"raw_peak_contact_force":0.17202,"subtask_id":"grasp_object","tcp_end":[0.4909,-0.0151,0.04864],"tcp_start":[0.49926,-0.01519,0.05801],"tcp_to_object_dist_end":0.02619,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":38.0,"n_steps":338.0,"n_steps_budget":1000.0,"object_pos_end":[0.50709,-0.01529,0.11616],"object_pos_start":[0.50374,-0.01524,0.0258],"object_to_goal_dist_end":0.25473,"object_to_goal_dist_start":0.31213,"object_z_max":0.11589,"peak_contact_force":0.07857,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":13940.0,"raw_peak_contact_force":0.34789,"subtask_id":"lift_object","tcp_end":[0.49838,-0.01516,0.14119],"tcp_start":[0.4909,-0.0151,0.04864],"tcp_to_object_dist_end":0.0265,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":817.0,"n_steps_budget":1000.0,"object_pos_end":[0.57148,0.13626,0.01602],"object_pos_start":[0.50709,-0.01529,0.11616],"object_to_goal_dist_end":0.23818,"object_to_goal_dist_start":0.25473,"object_z_max":0.23901,"peak_contact_force":272992.60669,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":13555.0,"raw_peak_contact_force":2.42149,"subtask_id":"reach_goal","tcp_end":[0.58346,0.1818,0.39199],"tcp_start":[0.5833,0.18092,0.39191],"tcp_to_object_dist_end":0.37891,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":2.0,"n_steps_budget":1000.0,"object_pos_end":[0.57148,0.13626,0.01602],"object_pos_start":[0.57148,0.13626,0.01602],"object_to_goal_dist_end":0.23818,"object_to_goal_dist_start":0.23818,"object_z_max":0.01602,"peak_contact_force":9748.64474,"phase_name":"lower_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":18.0,"raw_peak_contact_force":0.12263,"subtask_id":"place_goal","tcp_end":[0.58337,0.18185,0.39193],"tcp_start":[0.58341,0.18182,0.39197],"tcp_to_object_dist_end":0.37886,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.57148,0.13626,0.01602],"object_pos_start":[0.57148,0.13626,0.01602],"object_to_goal_dist_end":0.23818,"object_to_goal_dist_start":0.23818,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1025.0,"raw_peak_contact_force":0.12263,"subtask_id":"place_goal","tcp_end":[0.58234,0.18111,0.41262],"tcp_start":[0.58337,0.18185,0.39193],"tcp_to_object_dist_end":0.39928,"terminated_normally":true,"termination_reason":"step_budget"}],"success":false}]}
```