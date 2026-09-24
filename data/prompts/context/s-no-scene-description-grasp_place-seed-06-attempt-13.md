## Search State

- **Seed**: 6
- **Iteration**: 14 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 13 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | impedance_control | position_control | force_threshold_switch | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 15 | -0.1797 | 0.29 | ❌ rejected |
| 12 | approach → descend → grasp → lift → approach → descend | arc_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | position_control | position_control | position_control | impedance_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 10 | 0.0007 | 0.28 | ❌ rejected |
| 11 | approach → descend → grasp → lift → approach → descend → release → retract | arc_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | impedance_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 13 | -0.2044 | 0.29 | ❌ rejected |
| 10 | approach → descend → grasp → lift → approach → descend | arc_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | position_control | position_control | position_control | impedance_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 11 | -0.0518 | 0.28 | ❌ rejected |
| 9 | approach → descend → grasp → lift → approach → descend → release → retract | arc_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | impedance_control | impedance_control | force_threshold_switch | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 14 | -0.1292 | 0.29 | ❌ rejected |

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

## Current Skill (Q=-0.180) — your mutation base

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

- **Composite score**: -0.180
- **task_score** (E): 0.292
- **fitness_score**: 0.625  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.125
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.930

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_pre_grasp | 1.00 | 1.00 | 0.1181 |
| descend_to_grasp | 1.00 | 1.00 | 0.1528 |
| grasp_object | 1.00 | 1.00 | 0.0118 |
| lift_object | 1.00 | 1.00 | 0.2314 |
| transport_to_goal | 1.00 | 1.00 | 0.2387 |
| descend_to_place | 1.00 | 1.00 | 0.0076 |
| release_object | 1.00 | 1.00 | 0.0202 |
| retract_after_place | 1.00 | 1.00 | 0.0301 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_pre_grasp | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.496, 0.022, 0.188) | (0.500, 0.024, 0.030)→(0.500, 0.024, 0.026) | 0.269→0.271 | 1.00 / 4.000 | 7.051 | 0.138 |
| descend_to_grasp | descend | 1.00 / step_budget | (0.496, 0.022, 0.188)→(0.495, 0.024, 0.035) | (0.500, 0.024, 0.026)→(0.500, 0.024, 0.026) | 0.271→0.271 | 1.00 / 4.000 | 9.473 | 0.123 |
| grasp_object | grasp | 1.00 / step_budget | (0.495, 0.024, 0.035)→(0.487, 0.023, 0.027) | (0.500, 0.024, 0.026)→(0.500, 0.023, 0.026) | 0.271→0.272 | 1.00 / 43.000 | 0.147 | 0.220 |
| lift_object | lift | 1.00 / step_budget | (0.487, 0.023, 0.027)→(0.496, 0.023, 0.258) | (0.500, 0.023, 0.026)→(0.507, 0.023, 0.250) | 0.272→0.216 | 1.00 / 43.000 | 0.070 | 0.626 |
| transport_to_goal | approach | 1.00 / step_budget | (0.496, 0.023, 0.258)→(0.588, 0.179, 0.403) | (0.507, 0.023, 0.250)→(0.599, 0.179, 0.387) | 0.216→0.180 | 1.00 / 27.333 | 0.109 | 0.157 |
| descend_to_place | descend | 1.00 / force_exceeded | (0.588, 0.179, 0.403)→(0.588, 0.180, 0.396) | (0.599, 0.179, 0.387)→(0.599, 0.180, 0.379) | 0.180→0.172 | 1.00 / 28.000 | 111973.303 | 0.311 |
| release_object | release | 1.00 / step_budget | (0.588, 0.180, 0.396)→(0.587, 0.179, 0.416) | (0.599, 0.180, 0.379)→(0.593, 0.180, 0.013) | 0.172→0.196 | 1.00 / 2.667 | 91002.912 | 2.464 |
| retract_after_place | retract | 1.00 / step_budget | (0.587, 0.179, 0.416)→(0.593, 0.189, 0.398) | (0.593, 0.180, 0.013)→(0.597, 0.182, 0.017) | 0.196→0.192 | 1.00 / 4.000 | 0.104 | 2.052 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.423
- phase_score: 0.347
- phase_breakdown.reach_retract_score: 0.121
- phase_breakdown.reach_lift_score: 0.238
- phase_breakdown.reach_pre_grasp_score: 0.820
- phase_breakdown.reach_place_score: 0.315
- phase_breakdown.reach_grasp_score: 0.673
- grasp_place_fitness: 0.690

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.690
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.423
- **Median Q (composite search score)**: -0.205
- **K-run variance**: 0.0022
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.300


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.96359,"average_solve_count":412.0,"average_success_count":412.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_pre_grasp.speed":0.03261,"descend_to_grasp.descend_z":-0.01887,"descend_to_grasp.speed":0.05556,"descend_to_place.force_threshold":11.45082,"descend_to_place.place_z_offset":-0.01036,"descend_to_place.speed":0.0326,"grasp_object.grasp_duration":0.38397,"lift_object.lift_height":0.2521,"lift_object.speed":0.03012,"release_object.release_duration":0.2644,"retract_after_place.retract_z":0.22655,"retract_after_place.speed":0.06793,"transport_to_goal.arc_height":0.0622,"transport_to_goal.lifted_threshold":0.09005,"transport_to_goal.speed":0.03756},"optimized_scores":{"best_composite_score":-0.21925,"best_fitness_score":0.58575,"best_task_score":0.21311},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":5.0,"contact_point_centroid":[0.56583,0.17052,-0.0022],"force_p95":2.42782,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.45447,"mean_force":2.02289,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.5794,0.17073,0.44155]},{"body_a":"world","body_b":"grasp_target","contact_count":287.0,"contact_point_centroid":[0.59143,0.169,-0.00844],"force_p95":1.41795,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.22125,"mean_force":0.33789,"phase_index":7.0,"phase_name":"retract_after_place","phase_type":"retract","tcp_position_centroid":[0.58169,0.17537,0.44851]},{"body_a":"world","body_b":"grasp_target","contact_count":86.0,"contact_point_centroid":[0.49982,-0.0148,-0.00142],"force_p95":0.56383,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.5942,"mean_force":0.22955,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.48975,-0.01534,0.02795]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":16250.0,"contact_point_centroid":[0.49338,0.00393,0.14387],"force_p95":0.07509,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28843,"mean_force":0.05175,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.49343,-0.01523,0.14186]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":16980.0,"contact_point_centroid":[0.49332,-0.03436,0.14409],"force_p95":0.07251,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2692,"mean_force":0.04991,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.49346,-0.01523,0.14235]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1286.0,"contact_point_centroid":[0.58259,0.19009,0.43197],"force_p95":0.08389,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17115,"mean_force":0.05952,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.57964,0.17122,0.43148]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1000.0,"contact_point_centroid":[0.58191,0.1523,0.43239],"force_p95":0.09695,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16467,"mean_force":0.07219,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.57964,0.17121,0.43163]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.5038,-0.01552,-0.00203],"force_p95":0.13254,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.1614,"mean_force":0.12548,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.4919,-0.01537,0.0282]},{"body_a":"world","body_b":"grasp_target","contact_count":1496.0,"contact_point_centroid":[0.50382,-0.01567,-0.00191],"force_p95":0.13511,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12295,"phase_index":0.0,"phase_name":"approach_pre_grasp","phase_type":"approach","tcp_position_centroid":[0.49892,-0.00659,0.24498]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":894.0,"contact_point_centroid":[0.58233,0.1521,0.41807],"force_p95":0.09754,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13585,"mean_force":0.05777,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.57945,0.17118,0.41766]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1018.0,"contact_point_centroid":[0.58266,0.19002,0.41839],"force_p95":0.08274,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12396,"mean_force":0.05132,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.57947,0.17119,0.41785]},{"body_a":"world","body_b":"grasp_target","contact_count":2076.0,"contact_point_centroid":[0.50382,-0.01567,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.49801,-0.01457,0.11136]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4111.0,"contact_point_centroid":[0.49123,0.00385,0.02973],"force_p95":0.07608,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11467,"mean_force":0.05173,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.49072,-0.01535,0.02697]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":18587.0,"contact_point_centroid":[0.52655,0.02723,0.36705],"force_p95":0.07888,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10577,"mean_force":0.05258,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.52528,0.04614,0.36616]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":15918.0,"contact_point_centroid":[0.52728,0.06618,0.36865],"force_p95":0.08754,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10555,"mean_force":0.06005,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.52569,0.04707,0.36681]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4886.0,"contact_point_centroid":[0.49129,-0.03443,0.02881],"force_p95":0.06835,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08843,"mean_force":0.04478,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.49072,-0.01535,0.02697]}],"total_contact_groups":16},"final_pose_error":0.01992,"key_states":{"actual_goal_position":[0.58691,0.18745,0.24812],"final_object_position":[0.5913,0.1695,0.01696],"final_tcp_position":[0.58423,0.18074,0.45611],"realised_goal_position":[0.58691,0.18745,0.24812],"realised_object_initial_position":[0.50382,-0.01567,0.03]},"peak_contact_force":167951.73011,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":375.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.03],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.30942,"object_z_max":0.03,"peak_contact_force":20.90646,"phase_name":"approach_pre_grasp","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1496.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_pre_grasp","tcp_end":[0.49988,-0.01375,0.1887],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.16274,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":519.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2076.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_grasp","tcp_end":[0.49888,-0.01545,0.03561],"tcp_start":[0.49988,-0.01375,0.1887],"tcp_to_object_dist_end":0.01079,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50368,-0.01522,0.02588],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31207,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.13016,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10797.0,"raw_peak_contact_force":0.1614,"subtask_id":"reach_grasp","tcp_end":[0.49069,-0.01535,0.02694],"tcp_start":[0.49888,-0.01545,0.03561],"tcp_to_object_dist_end":0.01303,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":816.0,"n_steps_budget":1000.0,"object_pos_end":[0.51105,-0.01508,0.25081],"object_pos_start":[0.50368,-0.01522,0.02588],"object_to_goal_dist_end":0.21628,"object_to_goal_dist_start":0.31207,"object_z_max":0.25055,"peak_contact_force":0.07042,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":33316.0,"raw_peak_contact_force":0.5942,"subtask_id":"reach_lift","tcp_end":[0.50022,-0.01518,0.25854],"tcp_start":[0.49069,-0.01535,0.02694],"tcp_to_object_dist_end":0.01331,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":32.0,"n_steps":977.0,"n_steps_budget":1000.0,"object_pos_end":[0.58902,0.17049,0.42542],"object_pos_start":[0.51105,-0.01508,0.25081],"object_to_goal_dist_end":0.17812,"object_to_goal_dist_start":0.21628,"object_z_max":0.42557,"peak_contact_force":0.0845,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":34505.0,"raw_peak_contact_force":0.10577,"subtask_id":"reach_place","tcp_end":[0.57975,0.17037,0.44085],"tcp_start":[0.50022,-0.01518,0.25854],"tcp_to_object_dist_end":0.01801,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":31.0,"n_steps":76.0,"n_steps_budget":1000.0,"object_pos_end":[0.58889,0.17116,0.40497],"object_pos_start":[0.58902,0.17049,0.42542],"object_to_goal_dist_end":0.15771,"object_to_goal_dist_start":0.17812,"object_z_max":0.42542,"peak_contact_force":167951.73011,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2286.0,"raw_peak_contact_force":0.17115,"tcp_end":[0.57977,0.17138,0.42147],"tcp_start":[0.57975,0.17037,0.44085],"tcp_to_object_dist_end":0.01885,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.58582,0.17088,0.01738],"object_pos_start":[0.58889,0.17116,0.40497],"object_to_goal_dist_end":0.23133,"object_to_goal_dist_start":0.15771,"object_z_max":0.40497,"peak_contact_force":2.32123,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1917.0,"raw_peak_contact_force":2.45447,"tcp_end":[0.5794,0.17073,0.44211],"tcp_start":[0.57977,0.17138,0.42147],"tcp_to_object_dist_end":0.42478,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":73.0,"n_steps_budget":600.0,"object_pos_end":[0.5913,0.1695,0.01696],"object_pos_start":[0.58582,0.17088,0.01738],"object_to_goal_dist_end":0.23189,"object_to_goal_dist_start":0.23133,"object_z_max":0.01738,"peak_contact_force":0.10017,"phase_name":"retract_after_place","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":287.0,"raw_peak_contact_force":2.22125,"subtask_id":"reach_retract","tcp_end":[0.58423,0.18074,0.45611],"tcp_start":[0.5794,0.17073,0.44211],"tcp_to_object_dist_end":0.43935,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `fe7e0be33c0bb4db9d2bbbb069b6113d0e5a69a675a0d70bc1f582243e99e3cf`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.1268,"average_solve_count":347.0,"average_success_count":347.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_pre_grasp.speed":0.05913,"descend_to_grasp.descend_z":-0.01998,"descend_to_grasp.speed":0.0334,"descend_to_place.force_threshold":8.09366,"descend_to_place.place_z_offset":-0.01853,"descend_to_place.speed":0.02628,"grasp_object.grasp_duration":0.32001,"lift_object.lift_height":0.29565,"lift_object.speed":0.04696,"release_object.release_duration":0.39648,"retract_after_place.retract_z":0.17859,"retract_after_place.speed":0.05224,"transport_to_goal.arc_height":0.16055,"transport_to_goal.lifted_threshold":0.08777,"transport_to_goal.speed":0.06329},"optimized_scores":{"best_composite_score":-0.11463,"best_fitness_score":0.69037,"best_task_score":0.42311},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":10.0,"contact_point_centroid":[0.62137,0.15528,-0.00381],"force_p95":2.12289,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.14196,"mean_force":1.81962,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.61231,0.15804,0.36648]},{"body_a":"world","body_b":"grasp_target","contact_count":248.0,"contact_point_centroid":[0.6176,0.17005,-0.00834],"force_p95":1.25103,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.7098,"mean_force":0.32956,"phase_index":7.0,"phase_name":"retract_after_place","phase_type":"retract","tcp_position_centroid":[0.61549,0.16095,0.35596]},{"body_a":"world","body_b":"grasp_target","contact_count":88.0,"contact_point_centroid":[0.50829,0.03731,-0.0015],"force_p95":0.63719,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.67045,"mean_force":0.22243,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.49813,0.03816,0.02684]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":40.0,"contact_point_centroid":[0.61823,0.17689,0.34673],"force_p95":0.34432,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.54007,"mean_force":0.14747,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.61458,0.15863,0.34896]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":40.0,"contact_point_centroid":[0.61866,0.1404,0.34595],"force_p95":0.36303,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.44911,"mean_force":0.14466,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.61458,0.15863,0.34896]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":807.0,"contact_point_centroid":[0.61642,0.17722,0.33925],"force_p95":0.18977,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.325,"mean_force":0.09786,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.61338,0.15871,0.34325]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":765.0,"contact_point_centroid":[0.61653,0.14057,0.33966],"force_p95":0.2567,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31818,"mean_force":0.09176,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.6134,0.15872,0.34333]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":19770.0,"contact_point_centroid":[0.50226,0.05709,0.16425],"force_p95":0.07528,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31039,"mean_force":0.05148,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.50215,0.03796,0.16251]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":19468.0,"contact_point_centroid":[0.50255,0.01882,0.16904],"force_p95":0.07592,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29893,"mean_force":0.05159,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.50237,0.03796,0.16692]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8091.0,"contact_point_centroid":[0.55074,0.06341,0.3465],"force_p95":0.11342,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25494,"mean_force":0.0702,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.54709,0.08203,0.34635]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":7423.0,"contact_point_centroid":[0.55137,0.10176,0.3471],"force_p95":0.11916,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25254,"mean_force":0.07525,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.5479,0.08294,0.34672]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.51256,0.03937,-0.00213],"force_p95":0.1619,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24636,"mean_force":0.13321,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.50032,0.03836,0.02685]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4053.0,"contact_point_centroid":[0.4998,0.01906,0.02837],"force_p95":0.08105,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14614,"mean_force":0.05188,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.49914,0.03826,0.02558]},{"body_a":"world","body_b":"grasp_target","contact_count":1624.0,"contact_point_centroid":[0.51251,0.03972,-0.00192],"force_p95":0.13462,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12293,"phase_index":0.0,"phase_name":"approach_pre_grasp","phase_type":"approach","tcp_position_centroid":[0.50272,0.017,0.24372]},{"body_a":"world","body_b":"grasp_target","contact_count":2092.0,"contact_point_centroid":[0.51251,0.03972,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.50608,0.03693,0.1103]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5005.0,"contact_point_centroid":[0.49976,0.05743,0.02739],"force_p95":0.07349,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08719,"mean_force":0.04482,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.49914,0.03826,0.02558]}],"total_contact_groups":16},"final_pose_error":0.01989,"key_states":{"actual_goal_position":[0.62757,0.17252,0.14502],"final_object_position":[0.61742,0.16716,0.01652],"final_tcp_position":[0.61937,0.16489,0.34006],"realised_goal_position":[0.62757,0.17252,0.14502],"realised_object_initial_position":[0.51251,0.03972,0.03]},"peak_contact_force":273004.08959,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":407.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.03],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21001,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_pre_grasp","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1624.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_pre_grasp","tcp_end":[0.50768,0.03516,0.18738],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.1615,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":523.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2092.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_grasp","tcp_end":[0.5074,0.03894,0.03456],"tcp_start":[0.50768,0.03516,0.18738],"tcp_to_object_dist_end":0.00998,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51239,0.03824,0.02556],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21347,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.15306,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10858.0,"raw_peak_contact_force":0.24636,"subtask_id":"reach_grasp","tcp_end":[0.49911,0.03826,0.02555],"tcp_start":[0.5074,0.03894,0.03456],"tcp_to_object_dist_end":0.01328,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":979.0,"n_steps_budget":1000.0,"object_pos_end":[0.5204,0.03804,0.29299],"object_pos_start":[0.51239,0.03824,0.02556],"object_to_goal_dist_end":0.22685,"object_to_goal_dist_start":0.21347,"object_z_max":0.29273,"peak_contact_force":0.06926,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":39326.0,"raw_peak_contact_force":0.67045,"subtask_id":"reach_lift","tcp_end":[0.50948,0.03803,0.30165],"tcp_start":[0.49911,0.03826,0.02555],"tcp_to_object_dist_end":0.01394,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":20.0,"n_steps":558.0,"n_steps_budget":1000.0,"object_pos_end":[0.62818,0.1585,0.33152],"object_pos_start":[0.5204,0.03804,0.29299],"object_to_goal_dist_end":0.18702,"object_to_goal_dist_start":0.22685,"object_z_max":0.35554,"peak_contact_force":0.15586,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":15514.0,"raw_peak_contact_force":0.25494,"subtask_id":"reach_place","tcp_end":[0.61465,0.15841,0.34955],"tcp_start":[0.50948,0.03803,0.30165],"tcp_to_object_dist_end":0.02254,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":22.0,"n_steps":4.0,"n_steps_budget":1000.0,"object_pos_end":[0.62792,0.15925,0.32996],"object_pos_start":[0.62818,0.1585,0.33152],"object_to_goal_dist_end":0.18541,"object_to_goal_dist_start":0.18702,"object_z_max":0.33152,"peak_contact_force":16.4496,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":80.0,"raw_peak_contact_force":0.54007,"tcp_end":[0.61443,0.15889,0.34808],"tcp_start":[0.61465,0.15841,0.34955],"tcp_to_object_dist_end":0.02259,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.61755,0.16192,0.00768],"object_pos_start":[0.62792,0.15925,0.32996],"object_to_goal_dist_end":0.13812,"object_to_goal_dist_start":0.18541,"object_z_max":0.32996,"peak_contact_force":273004.08959,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1582.0,"raw_peak_contact_force":2.14196,"tcp_end":[0.61231,0.15804,0.36729],"tcp_start":[0.61443,0.15889,0.34808],"tcp_to_object_dist_end":0.35967,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":62.0,"n_steps_budget":600.0,"object_pos_end":[0.61742,0.16716,0.01652],"object_pos_start":[0.61755,0.16192,0.00768],"object_to_goal_dist_end":0.12902,"object_to_goal_dist_start":0.13812,"object_z_max":0.01637,"peak_contact_force":0.08699,"phase_name":"retract_after_place","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":248.0,"raw_peak_contact_force":1.7098,"subtask_id":"reach_retract","tcp_end":[0.61937,0.16489,0.34006],"tcp_start":[0.61231,0.15804,0.36729],"tcp_to_object_dist_end":0.32355,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `28f75809d7d1d0a11ca1a36dd459ad950e5a80b6bae34006f33ac9620425f5e5`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.98925,"average_solve_count":372.0,"average_success_count":372.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_pre_grasp.speed":0.04617,"descend_to_grasp.descend_z":-0.01935,"descend_to_grasp.speed":0.04412,"descend_to_place.force_threshold":10.14817,"descend_to_place.place_z_offset":-0.04359,"descend_to_place.speed":0.01718,"grasp_object.grasp_duration":0.40119,"lift_object.lift_height":0.2073,"lift_object.speed":0.04332,"release_object.release_duration":0.4189,"retract_after_place.retract_z":0.14978,"retract_after_place.speed":0.07839,"transport_to_goal.arc_height":0.057,"transport_to_goal.lifted_threshold":0.09182,"transport_to_goal.speed":0.01641},"optimized_scores":{"best_composite_score":-0.20535,"best_fitness_score":0.59965,"best_task_score":0.23942},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":6.0,"contact_point_centroid":[0.55813,0.20674,-0.00403],"force_p95":2.79462,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.79468,"mean_force":2.3756,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.56963,0.20835,0.4376]},{"body_a":"world","body_b":"grasp_target","contact_count":344.0,"contact_point_centroid":[0.58287,0.21042,-0.00717],"force_p95":1.30231,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.2235,"mean_force":0.29112,"phase_index":7.0,"phase_name":"retract_after_place","phase_type":"retract","tcp_position_centroid":[0.57305,0.21368,0.41976]},{"body_a":"world","body_b":"grasp_target","contact_count":88.0,"contact_point_centroid":[0.4785,0.0464,-0.00154],"force_p95":0.59263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.61278,"mean_force":0.22719,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.46929,0.04692,0.02862]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":13314.0,"contact_point_centroid":[0.47236,0.06595,0.12099],"force_p95":0.07396,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29159,"mean_force":0.05037,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.47257,0.04675,0.11941]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":13588.0,"contact_point_centroid":[0.47206,0.02758,0.12063],"force_p95":0.0726,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25227,"mean_force":0.04876,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.47254,0.04675,0.11898]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.48275,0.04842,-0.00215],"force_p95":0.16632,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.2517,"mean_force":0.1345,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.47136,0.04714,0.02857]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":126.0,"contact_point_centroid":[0.57257,0.22785,0.41988],"force_p95":0.18338,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2222,"mean_force":0.09451,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.57018,0.20886,0.41876]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":144.0,"contact_point_centroid":[0.57259,0.19008,0.41922],"force_p95":0.12818,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18292,"mean_force":0.06336,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.57018,0.20886,0.41876]},{"body_a":"world","body_b":"grasp_target","contact_count":1616.0,"contact_point_centroid":[0.4827,0.04873,-0.00192],"force_p95":0.13462,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12293,"phase_index":0.0,"phase_name":"approach_pre_grasp","phase_type":"approach","tcp_position_centroid":[0.49003,0.02075,0.24426]},{"body_a":"world","body_b":"grasp_target","contact_count":2124.0,"contact_point_centroid":[0.4827,0.04873,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.47833,0.04534,0.11101]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5005.0,"contact_point_centroid":[0.47006,0.02779,0.03045],"force_p95":0.07078,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11545,"mean_force":0.04302,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.47023,0.04703,0.02744]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1021.0,"contact_point_centroid":[0.5722,0.19006,0.41517],"force_p95":0.08013,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1126,"mean_force":0.05092,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.56971,0.20892,0.41405]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":970.0,"contact_point_centroid":[0.57221,0.22804,0.41528],"force_p95":0.08532,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11116,"mean_force":0.05345,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.56969,0.2089,0.41385]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":17149.0,"contact_point_centroid":[0.50845,0.11935,0.32999],"force_p95":0.08715,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11041,"mean_force":0.05782,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.50746,0.10018,0.32818]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":20244.0,"contact_point_centroid":[0.50814,0.08142,0.33072],"force_p95":0.07725,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10707,"mean_force":0.04969,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.50756,0.10036,0.32954]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5532.0,"contact_point_centroid":[0.46988,0.06638,0.0298],"force_p95":0.07041,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08275,"mean_force":0.04117,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.47024,0.04703,0.02744]}],"total_contact_groups":16},"final_pose_error":0.0196,"key_states":{"actual_goal_position":[0.58187,0.22885,0.23048],"final_object_position":[0.58253,0.21012,0.01688],"final_tcp_position":[0.57684,0.22025,0.39715],"realised_goal_position":[0.58187,0.22885,0.23048],"realised_object_initial_position":[0.4827,0.04873,0.03]},"peak_contact_force":167951.73011,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":405.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.03],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28719,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_pre_grasp","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1616.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_pre_grasp","tcp_end":[0.48131,0.04314,0.18791],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.16199,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":531.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":28.17447,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2124.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_grasp","tcp_end":[0.47811,0.04781,0.03544],"tcp_start":[0.48131,0.04314,0.18791],"tcp_to_object_dist_end":0.01052,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":47.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.4826,0.0472,0.02547],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.29135,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.15887,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12337.0,"raw_peak_contact_force":0.2517,"subtask_id":"reach_grasp","tcp_end":[0.47021,0.04703,0.02741],"tcp_start":[0.47811,0.04781,0.03544],"tcp_to_object_dist_end":0.01254,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":639.0,"n_steps_budget":1000.0,"object_pos_end":[0.48934,0.04694,0.20682],"object_pos_start":[0.4826,0.0472,0.02547],"object_to_goal_dist_end":0.20547,"object_to_goal_dist_start":0.29135,"object_z_max":0.20655,"peak_contact_force":0.07138,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":26990.0,"raw_peak_contact_force":0.61278,"subtask_id":"reach_lift","tcp_end":[0.47866,0.04687,0.21344],"tcp_start":[0.47021,0.04703,0.02741],"tcp_to_object_dist_end":0.01256,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":30.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.57953,0.20838,0.40506],"object_pos_start":[0.48934,0.04694,0.20682],"object_to_goal_dist_end":0.17579,"object_to_goal_dist_start":0.20547,"object_z_max":0.405,"peak_contact_force":0.08629,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":37393.0,"raw_peak_contact_force":0.11041,"subtask_id":"reach_place","tcp_end":[0.5702,0.20833,0.41938],"tcp_start":[0.47866,0.04687,0.21344],"tcp_to_object_dist_end":0.01709,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":31.0,"n_steps":9.0,"n_steps_budget":1000.0,"object_pos_end":[0.5793,0.2092,0.40297],"object_pos_start":[0.57953,0.20838,0.40506],"object_to_goal_dist_end":0.17363,"object_to_goal_dist_start":0.17579,"object_z_max":0.40506,"peak_contact_force":167951.73011,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":270.0,"raw_peak_contact_force":0.2222,"tcp_end":[0.57009,0.20913,0.41772],"tcp_start":[0.5702,0.20833,0.41938],"tcp_to_object_dist_end":0.01739,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.57678,0.20756,0.01381],"object_pos_start":[0.5793,0.2092,0.40297],"object_to_goal_dist_end":0.21778,"object_to_goal_dist_start":0.17363,"object_z_max":0.40297,"peak_contact_force":2.32597,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1997.0,"raw_peak_contact_force":2.79468,"tcp_end":[0.56963,0.20835,0.43827],"tcp_start":[0.57009,0.20913,0.41772],"tcp_to_object_dist_end":0.42453,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":87.0,"n_steps_budget":600.0,"object_pos_end":[0.58253,0.21012,0.01688],"object_pos_start":[0.57678,0.20756,0.01381],"object_to_goal_dist_end":0.21443,"object_to_goal_dist_start":0.21778,"object_z_max":0.01706,"peak_contact_force":0.12449,"phase_name":"retract_after_place","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":344.0,"raw_peak_contact_force":2.2235,"subtask_id":"reach_retract","tcp_end":[0.57684,0.22025,0.39715],"tcp_start":[0.56963,0.20835,0.43827],"tcp_to_object_dist_end":0.38045,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```