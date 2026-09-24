## Search State

- **Seed**: 4
- **Iteration**: 8 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 7 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | force_threshold_switch | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | force_exceeded | time_limit | 11 | 0.0826 | 0.35 | ❌ rejected |
| 6 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 11 | -0.0525 | 0.37 | ✅ accepted |
| 5 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 10 | -0.0091 | 0.36 | ✅ accepted |
| 4 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | force_threshold_switch | position_control | impedance_control | position_control | impedance_control | position_control | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 8 | -0.1853 | 0.20 | ❌ rejected |
| 3 | push → align → release → insert → lift | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | impedance_control | position_control | admittance_control | impedance_control | position_control | time_limit | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 6 | 0.0580 | 0.20 | ❌ rejected |

**Proposal policy**: task_score is 0.35 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.083) — your mutation base

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

- **Composite score**: 0.083
- **task_score** (E): 0.354
- **fitness_score**: 0.640  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.143
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.700

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_object | 1.00 | 1.00 | 0.0967 |
| descend_to_object | 1.00 | 1.00 | 0.1522 |
| grasp | 1.00 | 1.00 | 0.0133 |
| lift | 1.00 | 1.00 | 0.1109 |
| transport_to_goal | 1.00 | 1.00 | 0.0512 |
| lower_to_place | 1.00 | 1.00 | 0.0015 |
| release | 1.00 | 1.00 | 0.0208 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.518, 0.006, 0.208) | (0.526, 0.005, 0.030)→(0.526, 0.005, 0.026) | 0.246→0.249 | 1.00 / 4.000 | 0.122 | 0.138 |
| descend_to_object | descend | 1.00 / step_budget | (0.518, 0.006, 0.208)→(0.521, 0.005, 0.056) | (0.526, 0.005, 0.026)→(0.526, 0.005, 0.026) | 0.249→0.249 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp | grasp | 1.00 / step_budget | (0.521, 0.005, 0.056)→(0.512, 0.005, 0.046) | (0.526, 0.005, 0.026)→(0.526, 0.005, 0.026) | 0.249→0.249 | 1.00 / 42.667 | 0.144 | 0.191 |
| lift | lift | 1.00 / step_budget | (0.512, 0.005, 0.046)→(0.521, 0.005, 0.156) | (0.526, 0.005, 0.026)→(0.534, 0.005, 0.132) | 0.249→0.205 | 1.00 / 27.667 | 0.100 | 0.411 |
| transport_to_goal | approach | 1.00 / step_budget | (0.581, 0.118, 0.227)→(0.603, 0.164, 0.220) | (0.534, 0.005, 0.132)→(0.595, 0.135, 0.052) | 0.205→0.149 | 1.00 / 15.333 | 3249.640 | 1.217 |
| lower_to_place | descend | 1.00 / force_exceeded | (0.603, 0.164, 0.220)→(0.603, 0.164, 0.219) | (0.595, 0.135, 0.052)→(0.595, 0.136, 0.050) | 0.149→0.148 | 1.00 / 15.000 | 6588.606 | 0.167 |
| release | release | 1.00 / step_budget | (0.603, 0.164, 0.219)→(0.598, 0.163, 0.239) | (0.595, 0.136, 0.050)→(0.589, 0.139, 0.020) | 0.148→0.170 | 1.00 / 3.667 | 0.128 | 0.534 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.564
- phase_score: 0.618
- phase_breakdown.place_goal_score: 0.272
- phase_breakdown.reach_goal_score: 0.116
- phase_breakdown.reach_object_score: 0.725
- phase_breakdown.grasp_object_score: 0.659
- phase_breakdown.lift_object_score: 0.823
- grasp_place_fitness: 0.745

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.745
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.564
- **Median Q (composite search score)**: 0.061
- **K-run variance**: 0.0062
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Parameters at lower bound**: lower_to_place.lower_speed
- **Final σ (mean)**: 0.318


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.70796,"average_solve_count":113.0,"average_success_count":113.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_speed":0.1359,"approach_object.approach_tolerance":0.03128,"descend_to_object.descend_speed":0.12798,"descend_to_object.grasp_height":0.01015,"lift.lift_height":0.1505,"lift.lift_speed":0.17342,"lower_to_place.lower_speed":0.08838,"lower_to_place.place_force_threshold":7.03146,"release.release_time":0.27345,"transport_to_goal.transport_speed":0.21211,"transport_to_goal.transport_tolerance":0.02286},"optimized_scores":{"best_composite_score":0.06091,"best_fitness_score":0.61806,"best_task_score":0.30844},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":461.0,"contact_point_centroid":[0.63968,0.13763,-0.0042],"force_p95":0.84569,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.72111,"mean_force":0.22103,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.63112,0.13765,0.22191]},{"body_a":"world","body_b":"grasp_target","contact_count":76.0,"contact_point_centroid":[0.54286,0.0008,-0.00138],"force_p95":0.33001,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.43949,"mean_force":0.08209,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52834,0.00082,0.04519]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5040.0,"contact_point_centroid":[0.53611,-0.01803,0.09835],"force_p95":0.11352,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31588,"mean_force":0.077,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.5321,0.00074,0.0962]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5050.0,"contact_point_centroid":[0.53563,0.01953,0.09525],"force_p95":0.11403,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2935,"mean_force":0.07696,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.53181,0.00075,0.09326]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3945.0,"contact_point_centroid":[0.57378,0.02643,0.17589],"force_p95":0.14877,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27836,"mean_force":0.08585,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.56737,0.04512,0.17561]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4511.0,"contact_point_centroid":[0.57808,0.06985,0.17876],"force_p95":0.12809,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26047,"mean_force":0.07931,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.57166,0.05149,0.17865]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.54431,0.00103,-0.00203],"force_p95":0.13247,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.15442,"mean_force":0.12547,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.53056,0.00087,0.0454]},{"body_a":"world","body_b":"grasp_target","contact_count":536.0,"contact_point_centroid":[0.54431,0.00113,-0.00176],"force_p95":0.13797,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12354,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.51445,0.00038,0.25588]},{"body_a":"world","body_b":"grasp_target","contact_count":16.0,"contact_point_centroid":[0.63988,0.13773,-0.00196],"force_p95":0.12527,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12529,"mean_force":0.12444,"phase_index":5.0,"phase_name":"lower_to_place","phase_type":"descend","tcp_position_centroid":[0.63847,0.14938,0.22639]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.63988,0.13773,-0.00199],"force_p95":0.1237,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12471,"mean_force":0.12273,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.63488,0.14859,0.22587]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4116.0,"contact_point_centroid":[0.53054,-0.01836,0.04668],"force_p95":0.07633,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12416,"mean_force":0.05182,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.52936,0.00085,0.044]},{"body_a":"world","body_b":"grasp_target","contact_count":1112.0,"contact_point_centroid":[0.54431,0.00113,-0.00199],"force_p95":0.12264,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12264,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_object","phase_type":"descend","tcp_position_centroid":[0.53324,0.00088,0.13072]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4875.0,"contact_point_centroid":[0.53046,0.01992,0.04581],"force_p95":0.06841,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09411,"mean_force":0.04471,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.52936,0.00085,0.04401]},{"body_a":"left_finger","body_b":"right_finger","contact_count":288.0,"contact_point_centroid":[0.63596,0.14374,0.22718],"force_p95":0.01482,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0165,"mean_force":0.01133,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.63529,0.14373,0.22492]},{"body_a":"left_finger","body_b":"right_finger","contact_count":226.0,"contact_point_centroid":[0.63748,0.1493,0.22533],"force_p95":0.01092,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0126,"mean_force":0.00991,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.63709,0.14928,0.22273]},{"body_a":"left_finger","body_b":"right_finger","contact_count":18.0,"contact_point_centroid":[0.63783,0.1494,0.2286],"force_p95":0.01095,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01095,"mean_force":0.01017,"phase_index":5.0,"phase_name":"lower_to_place","phase_type":"descend","tcp_position_centroid":[0.63847,0.14938,0.22638]}],"total_contact_groups":16},"final_pose_error":0.03727,"key_states":{"actual_goal_position":[0.64762,0.15808,0.1911],"final_object_position":[0.63988,0.13773,0.01602],"final_tcp_position":[0.63837,0.14949,0.22617],"realised_goal_position":[0.64762,0.15808,0.1911],"realised_object_initial_position":[0.54431,0.00113,0.03]},"peak_contact_force":273062.05168,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":135.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.03],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.24751,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":536.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.53036,0.00079,0.20757],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.18209,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":278.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_object","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1112.0,"raw_peak_contact_force":0.12264,"subtask_id":"grasp_object","tcp_end":[0.53817,0.00101,0.05476],"tcp_start":[0.53036,0.00079,0.20757],"tcp_to_object_dist_end":0.02939,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54421,0.00076,0.02586],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.2505,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.1308,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10791.0,"raw_peak_contact_force":0.15442,"subtask_id":"grasp_object","tcp_end":[0.52933,0.00085,0.04397],"tcp_start":[0.53817,0.00101,0.05476],"tcp_to_object_dist_end":0.02344,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":22.0,"n_steps":370.0,"n_steps_budget":600.0,"object_pos_end":[0.55487,0.00082,0.13291],"object_pos_start":[0.54421,0.00076,0.02586],"object_to_goal_dist_end":0.19163,"object_to_goal_dist_start":0.2505,"object_z_max":0.13267,"peak_contact_force":0.11618,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":10166.0,"raw_peak_contact_force":0.43949,"subtask_id":"lift_object","tcp_end":[0.53905,0.0007,0.15725],"tcp_start":[0.52933,0.00085,0.04397],"tcp_to_object_dist_end":0.02903,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":554.0,"n_steps_budget":1000.0,"object_pos_end":[0.63987,0.13757,0.01639],"object_pos_start":[0.55487,0.00082,0.13291],"object_to_goal_dist_end":0.17608,"object_to_goal_dist_start":0.19163,"object_z_max":0.16754,"peak_contact_force":0.12544,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":9205.0,"raw_peak_contact_force":1.72111,"subtask_id":"reach_goal","tcp_end":[0.63853,0.14929,0.22648],"tcp_start":[0.63811,0.14765,0.22711],"tcp_to_object_dist_end":0.21042,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":4.0,"n_steps_budget":1000.0,"object_pos_end":[0.63987,0.13763,0.01607],"object_pos_start":[0.63987,0.13762,0.01608],"object_to_goal_dist_end":0.1764,"object_to_goal_dist_start":0.17638,"object_z_max":0.01608,"peak_contact_force":9748.7803,"phase_name":"lower_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":34.0,"raw_peak_contact_force":0.12529,"subtask_id":"place_goal","tcp_end":[0.63837,0.14949,0.22617],"tcp_start":[0.63845,0.14941,0.22637],"tcp_to_object_dist_end":0.21044,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.63988,0.13773,0.01602],"object_pos_start":[0.63987,0.13764,0.01605],"object_to_goal_dist_end":0.17643,"object_to_goal_dist_start":0.17641,"object_z_max":0.01605,"peak_contact_force":0.12263,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1026.0,"raw_peak_contact_force":0.12471,"subtask_id":"place_goal","tcp_end":[0.63363,0.14819,0.24506],"tcp_start":[0.63837,0.14949,0.22617],"tcp_to_object_dist_end":0.22936,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `349f925163f8e9284ad51ad55d38356f2e3c8deb4dc54e8ff12260e5f6d4b0f8`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.53521,"average_solve_count":142.0,"average_success_count":142.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_speed":0.16831,"approach_object.approach_tolerance":0.01627,"descend_to_object.descend_speed":0.07967,"descend_to_object.grasp_height":0.01018,"lift.lift_height":0.16543,"lift.lift_speed":0.05936,"lower_to_place.lower_speed":0.02001,"lower_to_place.place_force_threshold":6.36895,"release.release_time":0.36704,"transport_to_goal.transport_speed":0.19794,"transport_to_goal.transport_tolerance":0.03424},"optimized_scores":{"best_composite_score":0.18795,"best_fitness_score":0.74509,"best_task_score":0.56353},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":236.0,"contact_point_centroid":[0.57534,0.17613,-0.00523],"force_p95":0.94445,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.35332,"mean_force":0.29358,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.58351,0.1624,0.15741]},{"body_a":"world","body_b":"grasp_target","contact_count":93.0,"contact_point_centroid":[0.52824,0.02879,-0.00147],"force_p95":0.34895,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.42041,"mean_force":0.09463,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.51543,0.02908,0.04608]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":9764.0,"contact_point_centroid":[0.51989,0.04822,0.10804],"force_p95":0.07961,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28643,"mean_force":0.05275,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.51907,0.02913,0.10604]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":898.0,"contact_point_centroid":[0.58651,0.18275,0.14152],"force_p95":0.10543,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26775,"mean_force":0.06748,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.58755,0.16367,0.14386]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8599.0,"contact_point_centroid":[0.51994,0.00996,0.10851],"force_p95":0.08236,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26259,"mean_force":0.0577,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.51912,0.02913,0.10648]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":315.0,"contact_point_centroid":[0.58903,0.18291,0.14876],"force_p95":0.13765,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25369,"mean_force":0.075,"phase_index":5.0,"phase_name":"lower_to_place","phase_type":"descend","tcp_position_centroid":[0.59018,0.16403,0.1502]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":861.0,"contact_point_centroid":[0.58636,0.14503,0.14216],"force_p95":0.09699,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24058,"mean_force":0.05654,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.58774,0.16373,0.14416]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":315.0,"contact_point_centroid":[0.58844,0.14519,0.14871],"force_p95":0.13605,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23147,"mean_force":0.06786,"phase_index":5.0,"phase_name":"lower_to_place","phase_type":"descend","tcp_position_centroid":[0.59018,0.16403,0.1502]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53055,0.03066,-0.00214],"force_p95":0.16049,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.22168,"mean_force":0.13281,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.51759,0.02924,0.04605]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":7276.0,"contact_point_centroid":[0.55727,0.11476,0.16062],"force_p95":0.08037,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17188,"mean_force":0.05135,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.55704,0.09585,0.15991]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6499.0,"contact_point_centroid":[0.55703,0.07609,0.16085],"force_p95":0.09666,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17172,"mean_force":0.06117,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.55676,0.09526,0.16001]},{"body_a":"world","body_b":"grasp_target","contact_count":1004.0,"contact_point_centroid":[0.5305,0.03079,-0.00187],"force_p95":0.13691,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12311,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.51025,0.01236,0.24722]},{"body_a":"world","body_b":"grasp_target","contact_count":1052.0,"contact_point_centroid":[0.5305,0.03079,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_object","phase_type":"descend","tcp_position_centroid":[0.52278,0.02764,0.12467]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4572.0,"contact_point_centroid":[0.51711,0.00993,0.04726],"force_p95":0.07395,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11497,"mean_force":0.04728,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.51642,0.02916,0.04472]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5508.0,"contact_point_centroid":[0.51672,0.0484,0.04735],"force_p95":0.0696,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07213,"mean_force":0.04059,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.51643,0.02916,0.04473]}],"total_contact_groups":15},"final_pose_error":0.04388,"key_states":{"actual_goal_position":[0.60153,0.17858,0.10809],"final_object_position":[0.57389,0.17646,0.02665],"final_tcp_position":[0.58974,0.16428,0.14786],"realised_goal_position":[0.60153,0.17858,0.10809],"realised_object_initial_position":[0.5305,0.03079,0.03]},"peak_contact_force":268.35937,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":252.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.03],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18162,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1004.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.52255,0.02574,0.19306],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.16731,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":263.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_object","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1052.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_object","tcp_end":[0.52509,0.02971,0.05501],"tcp_start":[0.52255,0.02574,0.19306],"tcp_to_object_dist_end":0.02952,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":45.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53047,0.02966,0.0255],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18452,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.15673,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11880.0,"raw_peak_contact_force":0.22168,"subtask_id":"grasp_object","tcp_end":[0.51639,0.02916,0.04468],"tcp_start":[0.52509,0.02971,0.05501],"tcp_to_object_dist_end":0.0238,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":38.0,"n_steps":468.0,"n_steps_budget":1000.0,"object_pos_end":[0.53506,0.02966,0.14824],"object_pos_start":[0.53047,0.02966,0.0255],"object_to_goal_dist_end":0.16795,"object_to_goal_dist_start":0.18452,"object_z_max":0.14799,"peak_contact_force":0.07924,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":18456.0,"raw_peak_contact_force":0.42041,"subtask_id":"lift_object","tcp_end":[0.52558,0.02936,0.17174],"tcp_start":[0.51639,0.02916,0.04468],"tcp_to_object_dist_end":0.02534,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":30.0,"n_steps":369.0,"n_steps_budget":1000.0,"object_pos_end":[0.59079,0.16372,0.12251],"object_pos_start":[0.53506,0.02966,0.14824],"object_to_goal_dist_end":0.02333,"object_to_goal_dist_start":0.16795,"object_z_max":0.14842,"peak_contact_force":0.09881,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":13775.0,"raw_peak_contact_force":0.17188,"subtask_id":"reach_goal","tcp_end":[0.59071,0.16325,0.15187],"tcp_start":[0.52558,0.02936,0.17174],"tcp_to_object_dist_end":0.02936,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":29.0,"n_steps":21.0,"n_steps_budget":1000.0,"object_pos_end":[0.59039,0.16528,0.11833],"object_pos_start":[0.59079,0.16372,0.12251],"object_to_goal_dist_end":0.02015,"object_to_goal_dist_start":0.02333,"object_z_max":0.12251,"peak_contact_force":268.35937,"phase_name":"lower_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":630.0,"raw_peak_contact_force":0.25369,"subtask_id":"place_goal","tcp_end":[0.58974,0.16428,0.14786],"tcp_start":[0.59071,0.16325,0.15187],"tcp_to_object_dist_end":0.02955,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.57389,0.17646,0.02665],"object_pos_start":[0.59039,0.16528,0.11833],"object_to_goal_dist_end":0.08603,"object_to_goal_dist_start":0.02015,"object_z_max":0.11833,"peak_contact_force":0.1373,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1995.0,"raw_peak_contact_force":1.35332,"subtask_id":"place_goal","tcp_end":[0.58342,0.16237,0.16854],"tcp_start":[0.58974,0.16428,0.14786],"tcp_to_object_dist_end":0.1429,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `a1798e4fdcacfe8740623adfe3f78d2bc74e0d14c8233e64f02c40cf2a534ecc`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.79562,"average_solve_count":137.0,"average_success_count":137.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_speed":0.34971,"approach_object.approach_tolerance":0.04364,"descend_to_object.descend_speed":0.08585,"descend_to_object.grasp_height":0.01202,"lift.lift_height":0.1326,"lift.lift_speed":0.10696,"lower_to_place.lower_speed":0.07275,"lower_to_place.place_force_threshold":6.36046,"release.release_time":0.28296,"transport_to_goal.transport_speed":0.20525,"transport_to_goal.transport_tolerance":0.0323},"optimized_scores":{"best_composite_score":-0.00111,"best_fitness_score":0.55603,"best_task_score":0.19047},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":1486.0,"contact_point_centroid":[0.55419,0.10418,-0.0027],"force_p95":0.34749,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.75712,"mean_force":0.15128,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.56091,0.13313,0.249]},{"body_a":"world","body_b":"grasp_target","contact_count":78.0,"contact_point_centroid":[0.50203,-0.01441,-0.0014],"force_p95":0.33655,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.37433,"mean_force":0.07478,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.49028,-0.01469,0.04937]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3033.0,"contact_point_centroid":[0.5183,0.04144,0.164],"force_p95":0.1315,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29482,"mean_force":0.08439,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.51226,0.02286,0.16436]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4808.0,"contact_point_centroid":[0.49473,0.00426,0.08929],"force_p95":0.10791,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26918,"mean_force":0.06709,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.4928,-0.01476,0.08854]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5260.0,"contact_point_centroid":[0.49461,-0.03372,0.08914],"force_p95":0.10265,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26177,"mean_force":0.06244,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.49278,-0.01476,0.08828]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2937.0,"contact_point_centroid":[0.51724,0.00201,0.16271],"force_p95":0.14911,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25995,"mean_force":0.0865,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.51131,0.02057,0.16269]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50384,-0.0156,-0.00208],"force_p95":0.14628,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.19556,"mean_force":0.12888,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.49234,-0.01471,0.04922]},{"body_a":"world","body_b":"grasp_target","contact_count":328.0,"contact_point_centroid":[0.50382,-0.01567,-0.00162],"force_p95":0.13823,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12428,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.50141,-0.00424,0.26495]},{"body_a":"world","body_b":"grasp_target","contact_count":1236.0,"contact_point_centroid":[0.50382,-0.01567,-0.00199],"force_p95":0.12264,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12264,"mean_force":0.12258,"phase_index":1.0,"phase_name":"descend_to_object","phase_type":"descend","tcp_position_centroid":[0.49995,-0.0121,0.13899]},{"body_a":"world","body_b":"grasp_target","contact_count":8.0,"contact_point_centroid":[0.5542,0.1042,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"lower_to_place","phase_type":"descend","tcp_position_centroid":[0.58054,0.17848,0.28254]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.5542,0.1042,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.57784,0.1777,0.28365]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4345.0,"contact_point_centroid":[0.49163,0.00449,0.04917],"force_p95":0.07413,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12091,"mean_force":0.0495,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.49122,-0.0147,0.04802]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4934.0,"contact_point_centroid":[0.49159,-0.03385,0.04909],"force_p95":0.07051,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07216,"mean_force":0.04444,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.49122,-0.0147,0.04802]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1350.0,"contact_point_centroid":[0.56455,0.14035,0.25689],"force_p95":0.01158,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01701,"mean_force":0.0106,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.56413,0.14034,0.25457]},{"body_a":"left_finger","body_b":"right_finger","contact_count":224.0,"contact_point_centroid":[0.57966,0.17841,0.28201],"force_p95":0.01096,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01257,"mean_force":0.00998,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.57949,0.1784,0.27968]},{"body_a":"left_finger","body_b":"right_finger","contact_count":9.0,"contact_point_centroid":[0.58002,0.1785,0.28568],"force_p95":0.01098,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01098,"mean_force":0.01022,"phase_index":5.0,"phase_name":"lower_to_place","phase_type":"descend","tcp_position_centroid":[0.58054,0.17848,0.28253]}],"total_contact_groups":16},"final_pose_error":0.03609,"key_states":{"actual_goal_position":[0.58691,0.18745,0.24812],"final_object_position":[0.5542,0.1042,0.01602],"final_tcp_position":[0.58047,0.17856,0.2825],"realised_goal_position":[0.58691,0.18745,0.24812],"realised_object_initial_position":[0.50382,-0.01567,0.03]},"peak_contact_force":273230.01317,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":83.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02597],"object_pos_start":[0.50382,-0.01567,0.03],"object_to_goal_dist_end":0.31227,"object_to_goal_dist_start":0.30942,"object_z_max":0.03,"peak_contact_force":0.12212,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":328.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.50214,-0.00944,0.22274],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.19688,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":309.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.02597],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.31227,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_object","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1236.0,"raw_peak_contact_force":0.12264,"subtask_id":"grasp_object","tcp_end":[0.49956,-0.01477,0.05737],"tcp_start":[0.50214,-0.00944,0.22274],"tcp_to_object_dist_end":0.03165,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":42.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50375,-0.01499,0.02569],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31204,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.14438,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11079.0,"raw_peak_contact_force":0.19556,"subtask_id":"grasp_object","tcp_end":[0.49119,-0.0147,0.04798],"tcp_start":[0.49956,-0.01477,0.05737],"tcp_to_object_dist_end":0.02559,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":298.0,"n_steps_budget":660.0,"object_pos_end":[0.5127,-0.01517,0.11336],"object_pos_start":[0.50375,-0.01499,0.02569],"object_to_goal_dist_end":0.2544,"object_to_goal_dist_start":0.31204,"object_z_max":0.1131,"peak_contact_force":0.10572,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":10146.0,"raw_peak_contact_force":0.37433,"subtask_id":"lift_object","tcp_end":[0.49842,-0.01489,0.13919],"tcp_start":[0.49119,-0.0147,0.04798],"tcp_to_object_dist_end":0.02952,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":719.0,"n_steps_budget":1000.0,"object_pos_end":[0.5542,0.1042,0.01602],"object_pos_start":[0.5127,-0.01517,0.11336],"object_to_goal_dist_end":0.24874,"object_to_goal_dist_start":0.2544,"object_z_max":0.16049,"peak_contact_force":9748.69682,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":8806.0,"raw_peak_contact_force":1.75712,"subtask_id":"reach_goal","tcp_end":[0.58057,0.17845,0.28254],"tcp_start":[0.58042,0.17681,0.28269],"tcp_to_object_dist_end":0.27793,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":2.0,"n_steps_budget":1000.0,"object_pos_end":[0.5542,0.1042,0.01602],"object_pos_start":[0.5542,0.1042,0.01602],"object_to_goal_dist_end":0.24874,"object_to_goal_dist_start":0.24874,"object_z_max":0.01602,"peak_contact_force":9748.67877,"phase_name":"lower_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":17.0,"raw_peak_contact_force":0.12263,"subtask_id":"place_goal","tcp_end":[0.58047,0.17856,0.2825],"tcp_start":[0.58051,0.17851,0.28253],"tcp_to_object_dist_end":0.2779,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.5542,0.1042,0.01602],"object_pos_start":[0.5542,0.1042,0.01602],"object_to_goal_dist_end":0.24874,"object_to_goal_dist_start":0.24874,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1024.0,"raw_peak_contact_force":0.12263,"subtask_id":"place_goal","tcp_end":[0.57696,0.17731,0.30342],"tcp_start":[0.58047,0.17856,0.2825],"tcp_to_object_dist_end":0.29743,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```