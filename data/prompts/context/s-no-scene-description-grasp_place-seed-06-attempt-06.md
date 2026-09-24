## Search State

- **Seed**: 6
- **Iteration**: 7 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 6 | approach → descend → grasp → lift → approach → descend → release → retract | arc_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | impedance_control | position_control | force_threshold_switch | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 15 | -0.2966 | 0.31 | ✅ accepted |
| 5 | approach → descend → grasp → lift → approach → descend → release → retract | arc_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 14 | -0.2877 | 0.23 | ❌ rejected |
| 4 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | admittance_control | position_control | admittance_control | position_control | admittance_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 15 | -0.7858 | 0.17 | ❌ rejected |
| 3 | align → lift → push → approach → approach → descend → grasp → rotate | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | arc_cartesian | linear_cartesian | — | impedance_motion | position_control | position_control | impedance_control | force_threshold_switch | position_control | admittance_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 6 | -0.1415 | 0.25 | ✅ accepted |
| 2 | approach → descend → grasp → lift → approach → descend → release | arc_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | impedance_control | position_control | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 6 | 0.1266 | 0.20 | ❌ rejected |

**Proposal policy**: task_score is 0.31 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=-0.297) — your mutation base

```yaml
skill: grasp_place
dsl_version: 2
skill_type: arm_gripper
subtasks:
- id: reach_pre_grasp
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.1
  weight: 0.1
- id: reach_grasp
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.01
  weight: 0.1
- id: reach_lift
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.2
  weight: 0.2
- id: reach_place
  offset:
  - 0.0
  - 0.0
  - 0.15
  weight: 0.4
- id: reach_retract
  offset:
  - 0.0
  - 0.0
  - 0.3
  weight: 0.2
phases:
- id: approach_pre_grasp
  type: approach
  generator: arc_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    entity: tcp
    offset:
    - 0.0
    - 0.0
    - 0.15
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    arc_height:
      type: scalar
      range:
      - 0.02
      - 0.25
      default: 0.12
      binds_to:
      - path: generator.arc_height
        mode: replace
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: reach_pre_grasp
- id: descend_to_grasp
  type: descend
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    entity: tcp
    offset:
    - 0.0
    - 0.0
    - 0.02
    tolerance: 0.005
    orientation:
      mode: keep_current
  parameters:
    descend_z:
      type: scalar
      range:
      - -0.03
      - 0.0
      default: -0.01
      binds_to:
      - path: target.offset.z
        mode: add
    speed:
      type: scalar
      range:
      - 0.01
      - 0.08
      default: 0.03
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: reach_grasp
- id: grasp_object
  type: grasp
  control: position_control
  termination: time_limit
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
  parameters:
    grasp_duration:
      type: scalar
      range:
      - 0.1
      - 0.8
      default: 0.4
      binds_to:
      - path: duration.max_time
        mode: replace
  guards:
  - id: grasp_success_guard
    when: after_phase
    predicate: bilateral_grasp
    threshold: 0.02
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.0
    - 0.01
    - 0.0
  subtask_id: reach_grasp
- id: lift_object
  type: lift
  generator: linear_cartesian
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    entity: tcp
    offset:
    - 0.0
    - 0.0
    - 0.25
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    lift_height:
      type: scalar
      range:
      - 0.1
      - 0.35
      default: 0.25
      binds_to:
      - path: target.offset.z
        mode: replace
    speed:
      type: scalar
      range:
      - 0.02
      - 0.1
      default: 0.06
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: reach_lift
- id: transport_to_goal
  type: approach
  generator: arc_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    entity: tcp
    offset:
    - 0.0
    - 0.0
    - 0.2
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    arc_height:
      type: scalar
      range:
      - 0.05
      - 0.25
      default: 0.15
      binds_to:
      - path: generator.arc_height
        mode: replace
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: object_grasped_guard
    when: during_phase
    predicate: bilateral_grasp
    threshold: 0.02
    on_failure: abort
  subtask_id: reach_place
- id: descend_to_place
  type: descend
  generator: linear_cartesian
  control: force_threshold_switch
  termination: force_exceeded
  target:
    source: yaml
    anchor: task_goal
    entity: tcp
    offset:
    - 0.0
    - 0.0
    - -0.02
    orientation:
      mode: keep_current
  parameters:
    force_threshold:
      type: scalar
      range:
      - 1.0
      - 15.0
      default: 5.0
      binds_to:
      - path: termination.force_threshold
        mode: replace
    place_z_offset:
      type: scalar
      range:
      - -0.05
      - 0.0
      default: -0.02
      binds_to:
      - path: target.offset.z
        mode: replace
    speed:
      type: scalar
      range:
      - 0.01
      - 0.05
      default: 0.02
      binds_to:
      - path: generator.speed
        mode: replace
- id: release_object
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
    release_duration:
      type: scalar
      range:
      - 0.1
      - 0.5
      default: 0.2
      binds_to:
      - path: duration.max_time
        mode: replace
- id: retract_after_place
  type: retract
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    entity: tcp
    offset:
    - 0.0
    - 0.0
    - 0.3
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    retract_z:
      type: scalar
      range:
      - 0.1
      - 0.4
      default: 0.3
      binds_to:
      - path: target.offset.z
        mode: replace
    speed:
      type: scalar
      range:
      - 0.02
      - 0.1
      default: 0.06
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: reach_retract

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_pre_grasp** (`approach`)
  - target: source=yaml, anchor=task_object, entity=tcp, offset=[0.0, 0.0, 0.15], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - arc_height: status=consumed; consumers=generator.arc_height (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
- **descend_to_grasp** (`descend`)
  - target: source=yaml, anchor=task_object, entity=tcp, offset=[0.0, 0.0, 0.02], tolerance=0.005
  - orientation: mode=keep_current
  - parameter_bindings:
    - descend_z: status=consumed; consumers=target.offset.z (add)
    - speed: status=consumed; consumers=generator.speed (replace)
- **grasp_object** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings:
    - grasp_duration: status=consumed; consumers=duration.max_time (replace)
  - guards:
    - id=grasp_success_guard, when=after_phase, predicate=bilateral_grasp, on_failure=retry, threshold=0.02
  - retries: max_attempts=2, strategy=offset_target, offset=[0.0, 0.01, 0.0]
- **lift_object** (`lift`)
  - target: source=yaml, anchor=task_object, entity=tcp, offset=[0.0, 0.0, 0.25], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset.z (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
- **transport_to_goal** (`approach`)
  - target: source=yaml, anchor=task_goal, entity=tcp, offset=[0.0, 0.0, 0.2], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - arc_height: status=consumed; consumers=generator.arc_height (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=object_grasped_guard, when=during_phase, predicate=bilateral_grasp, on_failure=abort, threshold=0.02
- **descend_to_place** (`descend`)
  - target: source=yaml, anchor=task_goal, entity=tcp, offset=[0.0, 0.0, -0.02]
  - orientation: mode=keep_current
  - parameter_bindings:
    - force_threshold: status=consumed; consumers=termination.force_threshold (replace)
    - place_z_offset: status=consumed; consumers=target.offset.z (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
- **release_object** (`release`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings:
    - release_duration: status=consumed; consumers=duration.max_time (replace)
- **retract_after_place** (`retract`)
  - target: source=yaml, anchor=task_goal, entity=tcp, offset=[0.0, 0.0, 0.3], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - retract_z: status=consumed; consumers=target.offset.z (replace)
    - speed: status=consumed; consumers=generator.speed (replace)

## Design Metrics

- **Composite score**: -0.297
- **task_score** (E): 0.312
- **fitness_score**: 0.633  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.930

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_pre_grasp | 1.00 | 1.00 | 0.1233 |
| descend_to_grasp | 1.00 | 1.00 | 0.1482 |
| grasp_object | 1.00 | 1.00 | 0.0115 |
| lift_object | 1.00 | 0.67 | 0.1882 |
| transport_to_goal | 0.00 | 0.67 | 0.1216 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_pre_grasp | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.496, 0.031, 0.185) | (0.500, 0.024, 0.030)→(0.500, 0.024, 0.026) | 0.269→0.271 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_to_grasp | descend | 1.00 / step_budget | (0.496, 0.031, 0.185)→(0.495, 0.024, 0.037) | (0.500, 0.024, 0.026)→(0.500, 0.024, 0.026) | 0.271→0.271 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_object | grasp | 1.00 / step_budget | (0.495, 0.024, 0.037)→(0.487, 0.024, 0.029) | (0.500, 0.024, 0.026)→(0.500, 0.024, 0.026) | 0.271→0.272 | 1.00 / 43.000 | 0.142 | 0.219 |
| lift_object | lift | 1.00 / step_budget | (0.487, 0.024, 0.029)→(0.496, 0.024, 0.217) | (0.500, 0.024, 0.026)→(0.508, 0.028, 0.175) | 0.272→0.198 | 0.67 / 19.667 | 0.064 | 0.626 |
| transport_to_goal | approach | 0.00 / guard_failure | (0.496, 0.024, 0.217)→(0.515, 0.066, 0.329) | (0.508, 0.028, 0.175)→(0.524, 0.070, 0.277) | 0.198→0.175 | 0.67 / 5.333 | 0.003 | 0.172 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.333
- phase_score: 0.264
- phase_breakdown.reach_retract_score: 0.000
- phase_breakdown.reach_lift_score: 0.786
- phase_breakdown.reach_pre_grasp_score: 0.318
- phase_breakdown.reach_place_score: 0.024
- phase_breakdown.reach_grasp_score: 0.656
- grasp_place_fitness: 0.645

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.645
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.334
- **Median Q (composite search score)**: -0.289
- **K-run variance**: 0.0002
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.283


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `daf90631fcbaf423e19452d0c9b90b9715013985cc94ef12ca0cd881e96195aa`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.05,0.05],"goal_z_delta":0.15,"object_xy_delta":[0.05,0.05]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `94660347aa4f41f6801e53bd449f8df59691da8bebfa4fef4947a3513fe04781`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.03236,"average_solve_count":309.0,"average_success_count":309.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_pre_grasp.arc_height":0.11293,"approach_pre_grasp.speed":0.067,"descend_to_grasp.descend_z":-0.02232,"descend_to_grasp.speed":0.01387,"descend_to_place.force_threshold":8.8621,"descend_to_place.place_z_offset":-0.04092,"descend_to_place.speed":0.04093,"grasp_object.grasp_duration":0.41621,"lift_object.lift_height":0.21806,"lift_object.speed":0.05714,"release_object.release_duration":0.35728,"retract_after_place.retract_z":0.23532,"retract_after_place.speed":0.06238,"transport_to_goal.arc_height":0.08521,"transport_to_goal.speed":0.05085},"optimized_scores":{"best_composite_score":-0.31583,"best_fitness_score":0.61417,"best_task_score":0.2702},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":85.0,"contact_point_centroid":[0.50096,-0.0142,-0.00144],"force_p95":0.54913,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.65298,"mean_force":0.1636,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.48961,-0.0146,0.02702]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":12616.0,"contact_point_centroid":[0.49396,0.0046,0.12757],"force_p95":0.08067,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30626,"mean_force":0.0565,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.49329,-0.01452,0.1251]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":13465.0,"contact_point_centroid":[0.49376,-0.03357,0.1241],"force_p95":0.0779,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29557,"mean_force":0.05373,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.49309,-0.01452,0.12199]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":9264.0,"contact_point_centroid":[0.50679,0.01809,0.31182],"force_p95":0.14539,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26157,"mean_force":0.08008,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.50386,-0.00062,0.31185]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50384,-0.01539,-0.0021],"force_p95":0.15151,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.22643,"mean_force":0.13047,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.49179,-0.01462,0.02698]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":9964.0,"contact_point_centroid":[0.50697,-0.01945,0.31277],"force_p95":0.13237,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21337,"mean_force":0.07559,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.50372,-0.00085,0.31304]},{"body_a":"world","body_b":"grasp_target","contact_count":1772.0,"contact_point_centroid":[0.50382,-0.01567,-0.00192],"force_p95":0.1336,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.1229,"phase_index":0.0,"phase_name":"approach_pre_grasp","phase_type":"approach","tcp_position_centroid":[0.49907,0.01355,0.23858]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4069.0,"contact_point_centroid":[0.49116,0.00459,0.02849],"force_p95":0.07938,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1345,"mean_force":0.05186,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.4906,-0.01461,0.02574]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.50382,-0.01567,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.49766,-0.01081,0.10204]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4964.0,"contact_point_centroid":[0.49121,-0.03374,0.0276],"force_p95":0.07118,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08967,"mean_force":0.04479,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.49061,-0.01461,0.02575]}],"total_contact_groups":10},"final_pose_error":0.13926,"key_states":{"actual_goal_position":[0.58691,0.18745,0.24812],"final_object_position":[0.54199,0.06156,0.39187],"final_tcp_position":[0.53257,0.06304,0.4171],"realised_goal_position":[0.58691,0.18745,0.24812],"realised_object_initial_position":[0.50382,-0.01567,0.03]},"peak_contact_force":0.65298,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":444.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.03],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.30942,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_pre_grasp","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1772.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_pre_grasp","tcp_end":[0.49996,-0.00652,0.18112],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.15542,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_grasp","tcp_end":[0.49862,-0.0147,0.03418],"tcp_start":[0.49996,-0.00652,0.18112],"tcp_to_object_dist_end":0.00972,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50369,-0.01454,0.02567],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31178,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.14502,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10833.0,"raw_peak_contact_force":0.22643,"subtask_id":"reach_grasp","tcp_end":[0.49058,-0.01461,0.02571],"tcp_start":[0.49862,-0.0147,0.03418],"tcp_to_object_dist_end":0.01311,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":695.0,"n_steps_budget":1000.0,"object_pos_end":[0.5118,-0.01449,0.21709],"object_pos_start":[0.50369,-0.01454,0.02567],"object_to_goal_dist_end":0.21768,"object_to_goal_dist_start":0.31178,"object_z_max":0.21683,"peak_contact_force":0.08137,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":26166.0,"raw_peak_contact_force":0.65298,"subtask_id":"reach_lift","tcp_end":[0.49979,-0.01449,0.22436],"tcp_start":[0.49058,-0.01461,0.02571],"tcp_to_object_dist_end":0.01404,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":7.0,"n_steps":753.0,"n_steps_budget":1000.0,"object_pos_end":[0.54199,0.06156,0.39187],"object_pos_start":[0.5118,-0.01449,0.21709],"object_to_goal_dist_end":0.19629,"object_to_goal_dist_start":0.21768,"object_z_max":0.39261,"peak_contact_force":0.0,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":19228.0,"raw_peak_contact_force":0.26157,"subtask_id":"reach_place","tcp_end":[0.53257,0.06304,0.4171],"tcp_start":[0.49979,-0.01449,0.22436],"tcp_to_object_dist_end":0.02697,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `fe7e0be33c0bb4db9d2bbbb069b6113d0e5a69a675a0d70bc1f582243e99e3cf`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.40764,"average_solve_count":157.0,"average_success_count":157.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_pre_grasp.arc_height":0.13357,"approach_pre_grasp.speed":0.05574,"descend_to_grasp.descend_z":-0.01412,"descend_to_grasp.speed":0.05442,"descend_to_place.force_threshold":9.76806,"descend_to_place.place_z_offset":-0.02218,"descend_to_place.speed":0.03369,"grasp_object.grasp_duration":0.50149,"lift_object.lift_height":0.23523,"lift_object.speed":0.097,"release_object.release_duration":0.24485,"retract_after_place.retract_z":0.25513,"retract_after_place.speed":0.07811,"transport_to_goal.arc_height":0.1408,"transport_to_goal.speed":0.08738},"optimized_scores":{"best_composite_score":-0.28472,"best_fitness_score":0.64528,"best_task_score":0.33278},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":78.0,"contact_point_centroid":[0.50974,0.03844,-0.00137],"force_p95":0.65576,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.70921,"mean_force":0.15533,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.4982,0.03871,0.02492]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8423.0,"contact_point_centroid":[0.50399,0.01972,0.10918],"force_p95":0.1506,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31957,"mean_force":0.08124,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.50048,0.03847,0.10769]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8956.0,"contact_point_centroid":[0.50386,0.05719,0.10864],"force_p95":0.15274,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30854,"mean_force":0.07974,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.50051,0.03847,0.10755]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.51252,0.03944,-0.00207],"force_p95":0.14571,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.22343,"mean_force":0.129,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.50056,0.03893,0.02486]},{"body_a":"world","body_b":"grasp_target","contact_count":1896.0,"contact_point_centroid":[0.51251,0.03972,-0.00193],"force_p95":0.13354,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12288,"phase_index":0.0,"phase_name":"approach_pre_grasp","phase_type":"approach","tcp_position_centroid":[0.5019,0.0354,0.25122]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4075.0,"contact_point_centroid":[0.49992,0.01964,0.02637],"force_p95":0.0786,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12847,"mean_force":0.05178,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.49935,0.03883,0.02357]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.51251,0.03972,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.5061,0.04182,0.10105]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4941.0,"contact_point_centroid":[0.4999,0.05795,0.02539],"force_p95":0.07098,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09103,"mean_force":0.04491,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.49936,0.03883,0.02358]}],"total_contact_groups":8},"final_pose_error":0.20689,"key_states":{"actual_goal_position":[0.62757,0.17252,0.14502],"final_object_position":[0.51768,0.04956,0.13852],"final_tcp_position":[0.50872,0.03848,0.24152],"realised_goal_position":[0.62757,0.17252,0.14502],"realised_object_initial_position":[0.51251,0.03972,0.03]},"peak_contact_force":0.70921,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":475.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.03],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21001,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_pre_grasp","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1896.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_pre_grasp","tcp_end":[0.50768,0.04485,0.18691],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.16104,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_grasp","tcp_end":[0.5074,0.0395,0.03226],"tcp_start":[0.50768,0.04485,0.18691],"tcp_to_object_dist_end":0.00807,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51237,0.03873,0.02574],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21307,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.13991,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10816.0,"raw_peak_contact_force":0.22343,"subtask_id":"reach_grasp","tcp_end":[0.49932,0.03883,0.02354],"tcp_start":[0.5074,0.0395,0.03226],"tcp_to_object_dist_end":0.01323,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":712.0,"n_steps_budget":1000.0,"object_pos_end":[0.5178,0.04939,0.14067],"object_pos_start":[0.51237,0.03873,0.02574],"object_to_goal_dist_end":0.16501,"object_to_goal_dist_start":0.21307,"object_z_max":0.20003,"peak_contact_force":0.0,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":17457.0,"raw_peak_contact_force":0.70921,"subtask_id":"reach_lift","tcp_end":[0.50866,0.03848,0.24133],"tcp_start":[0.49932,0.03883,0.02354],"tcp_to_object_dist_end":0.10167,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.51768,0.04956,0.13852],"object_pos_start":[0.5178,0.04939,0.14067],"object_to_goal_dist_end":0.16504,"object_to_goal_dist_start":0.16501,"object_z_max":0.14067,"peak_contact_force":0.0,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"reach_place","tcp_end":[0.50872,0.03848,0.24152],"tcp_start":[0.50866,0.03848,0.24133],"tcp_to_object_dist_end":0.10398,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `28f75809d7d1d0a11ca1a36dd459ad950e5a80b6bae34006f33ac9620425f5e5`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.08997,"average_solve_count":289.0,"average_success_count":289.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_pre_grasp.arc_height":0.11446,"approach_pre_grasp.speed":0.02532,"descend_to_grasp.descend_z":-0.00299,"descend_to_grasp.speed":0.04027,"descend_to_place.force_threshold":4.61398,"descend_to_place.place_z_offset":-0.03314,"descend_to_place.speed":0.02638,"grasp_object.grasp_duration":0.36752,"lift_object.lift_height":0.17819,"lift_object.speed":0.0712,"release_object.release_duration":0.42413,"retract_after_place.retract_z":0.13199,"retract_after_place.speed":0.05917,"transport_to_goal.arc_height":0.05384,"transport_to_goal.speed":0.04722},"optimized_scores":{"best_composite_score":-0.28932,"best_fitness_score":0.64068,"best_task_score":0.33375},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":77.0,"contact_point_centroid":[0.47977,0.04746,-0.00142],"force_p95":0.45919,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.51637,"mean_force":0.15244,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.46948,0.04767,0.03824]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8010.0,"contact_point_centroid":[0.47358,0.06652,0.10191],"force_p95":0.10791,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29709,"mean_force":0.06519,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.47173,0.04749,0.09991]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":7881.0,"contact_point_centroid":[0.47412,0.02858,0.10479],"force_p95":0.10457,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27182,"mean_force":0.06586,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.47193,0.04749,0.10274]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5192.0,"contact_point_centroid":[0.49028,0.04457,0.24866],"force_p95":0.15964,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25426,"mean_force":0.09905,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.48464,0.0629,0.24944]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.48271,0.04858,-0.00207],"force_p95":0.14433,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.20781,"mean_force":0.12849,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.47155,0.0479,0.03816]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5165.0,"contact_point_centroid":[0.49075,0.08228,0.25174],"force_p95":0.14081,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19028,"mean_force":0.09921,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.48521,0.06392,0.25281]},{"body_a":"world","body_b":"grasp_target","contact_count":2120.0,"contact_point_centroid":[0.4827,0.04873,-0.00193],"force_p95":0.13221,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12286,"phase_index":0.0,"phase_name":"approach_pre_grasp","phase_type":"approach","tcp_position_centroid":[0.49153,0.04202,0.25575]},{"body_a":"world","body_b":"grasp_target","contact_count":3524.0,"contact_point_centroid":[0.4827,0.04873,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.47797,0.0515,0.11234]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5055.0,"contact_point_centroid":[0.4702,0.02856,0.0398],"force_p95":0.0675,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11397,"mean_force":0.04295,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.47043,0.0478,0.03701]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5435.0,"contact_point_centroid":[0.47002,0.06707,0.03922],"force_p95":0.06697,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07488,"mean_force":0.04114,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.47044,0.0478,0.03702]}],"total_contact_groups":10},"final_pose_error":0.18375,"key_states":{"actual_goal_position":[0.58187,0.22885,0.23048],"final_object_position":[0.51085,0.09776,0.30023],"final_tcp_position":[0.50467,0.09697,0.32845],"realised_goal_position":[0.58187,0.22885,0.23048],"realised_object_initial_position":[0.4827,0.04873,0.03]},"peak_contact_force":0.51637,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":531.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.03],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28719,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_pre_grasp","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2120.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_pre_grasp","tcp_end":[0.48107,0.05495,0.18743],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.16154,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":881.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3524.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_grasp","tcp_end":[0.47805,0.04856,0.04487],"tcp_start":[0.48107,0.05495,0.18743],"tcp_to_object_dist_end":0.01941,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":47.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.48261,0.04797,0.02573],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.29068,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.14119,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12290.0,"raw_peak_contact_force":0.20781,"subtask_id":"reach_grasp","tcp_end":[0.47041,0.04779,0.03698],"tcp_start":[0.47805,0.04856,0.04487],"tcp_to_object_dist_end":0.0166,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":22.0,"n_steps":487.0,"n_steps_budget":1000.0,"object_pos_end":[0.49555,0.04785,0.16768],"object_pos_start":[0.48261,0.04797,0.02573],"object_to_goal_dist_end":0.21013,"object_to_goal_dist_start":0.29068,"object_z_max":0.16743,"peak_contact_force":0.11153,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":15968.0,"raw_peak_contact_force":0.51637,"subtask_id":"reach_lift","tcp_end":[0.47807,0.0476,0.18464],"tcp_start":[0.47041,0.04779,0.03698],"tcp_to_object_dist_end":0.02436,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":547.0,"n_steps_budget":1000.0,"object_pos_end":[0.51085,0.09776,0.30023],"object_pos_start":[0.49555,0.04785,0.16768],"object_to_goal_dist_end":0.1646,"object_to_goal_dist_start":0.21013,"object_z_max":0.3003,"peak_contact_force":0.01017,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":10357.0,"raw_peak_contact_force":0.25426,"subtask_id":"reach_place","tcp_end":[0.50467,0.09697,0.32845],"tcp_start":[0.47807,0.0476,0.18464],"tcp_to_object_dist_end":0.0289,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```