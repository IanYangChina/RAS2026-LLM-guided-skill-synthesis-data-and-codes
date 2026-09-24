## Search State

- **Seed**: 6
- **Iteration**: 12 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 11 | approach → descend → grasp → lift → approach → descend → release → retract | arc_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | impedance_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 13 | -0.2044 | 0.29 | ❌ rejected |
| 10 | approach → descend → grasp → lift → approach → descend | arc_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | position_control | position_control | position_control | impedance_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 11 | -0.0518 | 0.28 | ❌ rejected |
| 9 | approach → descend → grasp → lift → approach → descend → release → retract | arc_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | impedance_control | impedance_control | force_threshold_switch | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 14 | -0.1292 | 0.29 | ❌ rejected |
| 8 | approach → descend → grasp → lift → approach → descend → release → retract | arc_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | impedance_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | time_limit | time_limit | pose_tolerance | 14 | -0.2650 | 0.27 | ❌ rejected |
| 7 | approach → descend → grasp → lift → approach → descend → release → retract | arc_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | force_threshold_switch | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 15 | -0.1803 | 0.29 | ❌ rejected |

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

## Current Skill (Q=-0.204) — your mutation base

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

- **Composite score**: -0.204
- **task_score** (E): 0.292
- **fitness_score**: 0.626  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.830

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_pre_grasp | 1.00 | 1.00 | 0.1245 |
| descend_to_grasp | 1.00 | 1.00 | 0.1502 |
| grasp_object | 1.00 | 1.00 | 0.0115 |
| lift_object | 1.00 | 1.00 | 0.2709 |
| transport_to_goal | 1.00 | 1.00 | 0.2163 |
| descend_to_place | 1.00 | 1.00 | 0.2049 |
| release_object | 1.00 | 1.00 | 0.0207 |
| retract_after_place | 0.00 | 1.00 | 0.2373 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_pre_grasp | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.496, 0.032, 0.184) | (0.500, 0.024, 0.030)→(0.500, 0.024, 0.026) | 0.269→0.271 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_to_grasp | descend | 1.00 / step_budget | (0.496, 0.032, 0.184)→(0.495, 0.024, 0.034) | (0.500, 0.024, 0.026)→(0.500, 0.024, 0.026) | 0.271→0.271 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_object | grasp | 1.00 / step_budget | (0.495, 0.024, 0.034)→(0.487, 0.024, 0.026) | (0.500, 0.024, 0.026)→(0.500, 0.024, 0.026) | 0.271→0.272 | 1.00 / 43.000 | 0.139 | 0.208 |
| lift_object | lift | 1.00 / step_budget | (0.487, 0.024, 0.026)→(0.496, 0.024, 0.297) | (0.500, 0.024, 0.026)→(0.507, 0.024, 0.288) | 0.272→0.220 | 1.00 / 41.000 | 0.072 | 0.661 |
| transport_to_goal | approach | 1.00 / step_budget | (0.496, 0.024, 0.297)→(0.591, 0.185, 0.394) | (0.507, 0.024, 0.288)→(0.600, 0.185, 0.380) | 0.220→0.172 | 1.00 / 37.333 | 0.078 | 0.101 |
| descend_to_place | descend | 1.00 / step_budget | (0.591, 0.185, 0.394)→(0.595, 0.194, 0.189) | (0.600, 0.185, 0.380)→(0.602, 0.194, 0.171) | 0.172→0.037 | 1.00 / 30.000 | 0.086 | 0.163 |
| release_object | release | 1.00 / step_budget | (0.595, 0.194, 0.189)→(0.589, 0.192, 0.209) | (0.602, 0.194, 0.171)→(0.600, 0.194, 0.013) | 0.037→0.195 | 1.00 / 4.000 | 0.085 | 1.704 |
| retract_after_place | retract | 0.00 / step_budget | (0.589, 0.192, 0.209)→(0.597, 0.195, 0.446) | (0.600, 0.194, 0.013)→(0.600, 0.194, 0.016) | 0.195→0.192 | 1.00 / 4.000 | 27.129 | 0.125 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.423
- phase_score: 0.201
- phase_breakdown.reach_retract_score: 0.217
- phase_breakdown.reach_lift_score: 0.202
- phase_breakdown.reach_pre_grasp_score: 0.353
- phase_breakdown.reach_place_score: 0.033
- phase_breakdown.reach_grasp_score: 0.688
- grasp_place_fitness: 0.691

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.691
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.423
- **Median Q (composite search score)**: -0.230
- **K-run variance**: 0.0022
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.302


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.95009,"average_solve_count":581.0,"average_success_count":581.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_pre_grasp.arc_height":0.15167,"approach_pre_grasp.speed":0.02722,"descend_to_grasp.descend_z":-0.01204,"descend_to_grasp.speed":0.05619,"descend_to_place.place_z":-0.02282,"descend_to_place.speed":0.02563,"grasp_object.grasp_duration":0.54095,"lift_object.lift_height":0.29318,"lift_object.speed":0.05814,"release_object.release_duration":0.42143,"retract_after_place.retract_z":0.30467,"retract_after_place.speed":0.03518,"transport_to_goal.speed":0.05101},"optimized_scores":{"best_composite_score":-0.24411,"best_fitness_score":0.58589,"best_task_score":0.2128},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":159.0,"contact_point_centroid":[0.58595,0.18555,-0.00917],"force_p95":1.42006,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.96822,"mean_force":0.48725,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.57905,0.18375,0.2483]},{"body_a":"world","body_b":"grasp_target","contact_count":82.0,"contact_point_centroid":[0.50099,-0.0147,-0.00139],"force_p95":0.55487,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.65868,"mean_force":0.17456,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.48986,-0.01518,0.02722]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":17959.0,"contact_point_centroid":[0.49436,0.00404,0.16673],"force_p95":0.07827,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31201,"mean_force":0.05427,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.49383,-0.01508,0.1645]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":18514.0,"contact_point_centroid":[0.4942,-0.03416,0.16322],"force_p95":0.07672,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29489,"mean_force":0.053,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.49367,-0.01508,0.16124]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8110.0,"contact_point_centroid":[0.58552,0.19931,0.33903],"force_p95":0.09169,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18273,"mean_force":0.06576,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.5827,0.18038,0.33922]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50381,-0.01548,-0.00204],"force_p95":0.13589,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.17599,"mean_force":0.12636,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.49205,-0.01521,0.02727]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":828.0,"contact_point_centroid":[0.58482,0.16613,0.22823],"force_p95":0.09435,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15719,"mean_force":0.06137,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.58199,0.18494,0.23007]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8473.0,"contact_point_centroid":[0.58544,0.16143,0.34151],"force_p95":0.09095,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15349,"mean_force":0.06298,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.58267,0.18025,0.34184]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":841.0,"contact_point_centroid":[0.58473,0.20378,0.22787],"force_p95":0.09385,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15339,"mean_force":0.06114,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.58197,0.18493,0.23003]},{"body_a":"world","body_b":"grasp_target","contact_count":1752.0,"contact_point_centroid":[0.50382,-0.01567,-0.00192],"force_p95":0.13383,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.1229,"phase_index":0.0,"phase_name":"approach_pre_grasp","phase_type":"approach","tcp_position_centroid":[0.49895,0.00868,0.24031]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.58768,0.18546,-0.00201],"force_p95":0.12291,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.1256,"mean_force":0.12088,"phase_index":7.0,"phase_name":"retract_after_place","phase_type":"retract","tcp_position_centroid":[0.58152,0.18482,0.37546]},{"body_a":"world","body_b":"grasp_target","contact_count":3744.0,"contact_point_centroid":[0.50382,-0.01567,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.49783,-0.01147,0.10359]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4098.0,"contact_point_centroid":[0.49133,0.00401,0.0288],"force_p95":0.07696,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11542,"mean_force":0.05179,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.49087,-0.01519,0.02603]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":14077.0,"contact_point_centroid":[0.53965,0.09553,0.3618],"force_p95":0.0885,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10541,"mean_force":0.05731,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.5385,0.07639,0.36058]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":16586.0,"contact_point_centroid":[0.54075,0.06115,0.36378],"force_p95":0.07421,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09494,"mean_force":0.04943,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.54011,0.08009,0.36322]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4904.0,"contact_point_centroid":[0.49139,-0.03428,0.02788],"force_p95":0.06892,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09305,"mean_force":0.04479,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.49087,-0.01519,0.02604]}],"total_contact_groups":16},"final_pose_error":0.0532,"key_states":{"actual_goal_position":[0.58691,0.18745,0.24812],"final_object_position":[0.58768,0.18546,0.01602],"final_tcp_position":[0.58644,0.18679,0.49959],"realised_goal_position":[0.58691,0.18745,0.24812],"realised_object_initial_position":[0.50382,-0.01567,0.03]},"peak_contact_force":1.96822,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":439.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.03],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.30942,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_pre_grasp","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1752.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_pre_grasp","tcp_end":[0.49991,-0.0073,0.18335],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.1576,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":936.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3744.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_grasp","tcp_end":[0.49886,-0.01529,0.03447],"tcp_start":[0.49991,-0.0073,0.18335],"tcp_to_object_dist_end":0.0098,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50368,-0.01507,0.02584],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.312,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.13273,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10802.0,"raw_peak_contact_force":0.17599,"subtask_id":"reach_grasp","tcp_end":[0.49084,-0.01519,0.026],"tcp_start":[0.49886,-0.01529,0.03447],"tcp_to_object_dist_end":0.01284,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":38.0,"n_steps":951.0,"n_steps_budget":1000.0,"object_pos_end":[0.51183,-0.01512,0.28997],"object_pos_start":[0.50368,-0.01507,0.02584],"object_to_goal_dist_end":0.22005,"object_to_goal_dist_start":0.312,"object_z_max":0.28971,"peak_contact_force":0.07754,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":36555.0,"raw_peak_contact_force":0.65868,"subtask_id":"reach_lift","tcp_end":[0.50075,-0.01504,0.29943],"tcp_start":[0.49084,-0.01519,0.026],"tcp_to_object_dist_end":0.01456,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":32.0,"n_steps":820.0,"n_steps_budget":1000.0,"object_pos_end":[0.58981,0.17664,0.4171],"object_pos_start":[0.51183,-0.01512,0.28997],"object_to_goal_dist_end":0.16935,"object_to_goal_dist_start":0.22005,"object_z_max":0.41697,"peak_contact_force":0.09281,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":30663.0,"raw_peak_contact_force":0.10541,"subtask_id":"reach_place","tcp_end":[0.58213,0.1763,0.4324],"tcp_start":[0.50075,-0.01504,0.29943],"tcp_to_object_dist_end":0.01713,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":26.0,"n_steps":558.0,"n_steps_budget":1000.0,"object_pos_end":[0.59016,0.18539,0.21466],"object_pos_start":[0.58981,0.17664,0.4171],"object_to_goal_dist_end":0.03368,"object_to_goal_dist_start":0.16935,"object_z_max":0.4171,"peak_contact_force":0.09225,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":16583.0,"raw_peak_contact_force":0.18273,"subtask_id":"reach_place","tcp_end":[0.58365,0.18548,0.2342],"tcp_start":[0.58213,0.1763,0.4324],"tcp_to_object_dist_end":0.0206,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.58773,0.1848,0.00863],"object_pos_start":[0.59016,0.18539,0.21466],"object_to_goal_dist_end":0.2395,"object_to_goal_dist_start":0.03368,"object_z_max":0.21466,"peak_contact_force":0.07472,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1828.0,"raw_peak_contact_force":1.96822,"tcp_end":[0.57902,0.18375,0.2545],"tcp_start":[0.58365,0.18548,0.2342],"tcp_to_object_dist_end":0.24603,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.58768,0.18546,0.01602],"object_pos_start":[0.58773,0.1848,0.00863],"object_to_goal_dist_end":0.23211,"object_to_goal_dist_start":0.2395,"object_z_max":0.01671,"peak_contact_force":0.12263,"phase_name":"retract_after_place","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.1256,"subtask_id":"reach_retract","tcp_end":[0.58644,0.18679,0.49959],"tcp_start":[0.57902,0.18375,0.2545],"tcp_to_object_dist_end":0.48357,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `fe7e0be33c0bb4db9d2bbbb069b6113d0e5a69a675a0d70bc1f582243e99e3cf`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.14644,"average_solve_count":519.0,"average_success_count":519.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_pre_grasp.arc_height":0.05698,"approach_pre_grasp.speed":0.06484,"descend_to_grasp.descend_z":-0.00805,"descend_to_grasp.speed":0.03075,"descend_to_place.place_z":-0.02813,"descend_to_place.speed":0.011,"grasp_object.grasp_duration":0.72349,"lift_object.lift_height":0.32269,"lift_object.speed":0.02162,"release_object.release_duration":0.39881,"retract_after_place.retract_z":0.30457,"retract_after_place.speed":0.03773,"transport_to_goal.speed":0.07159},"optimized_scores":{"best_composite_score":-0.13909,"best_fitness_score":0.69091,"best_task_score":0.42305},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":294.0,"contact_point_centroid":[0.62628,0.1696,-0.00448],"force_p95":0.85394,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.27616,"mean_force":0.2427,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.61549,0.1682,0.13302]},{"body_a":"world","body_b":"grasp_target","contact_count":87.0,"contact_point_centroid":[0.50967,0.03831,-0.00142],"force_p95":0.5598,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.65663,"mean_force":0.17171,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.49842,0.03872,0.02786]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":19168.0,"contact_point_centroid":[0.50254,0.05763,0.169],"force_p95":0.07854,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30868,"mean_force":0.05375,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.50203,0.03852,0.16703]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":19254.0,"contact_point_centroid":[0.50279,0.01943,0.17283],"force_p95":0.07774,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30288,"mean_force":0.05321,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.50219,0.03852,0.17069]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":840.0,"contact_point_centroid":[0.62263,0.18847,0.11836],"force_p95":0.09692,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23221,"mean_force":0.06291,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.61999,0.16963,0.12029]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":828.0,"contact_point_centroid":[0.62286,0.15081,0.11877],"force_p95":0.09762,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22363,"mean_force":0.06257,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.62002,0.16964,0.12033]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.51253,0.03946,-0.00208],"force_p95":0.14592,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.21968,"mean_force":0.12899,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.50073,0.03893,0.02796]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8176.0,"contact_point_centroid":[0.6209,0.14595,0.23489],"force_p95":0.09523,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15242,"mean_force":0.0681,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.61833,0.16486,0.23475]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":9093.0,"contact_point_centroid":[0.62137,0.18381,0.23189],"force_p95":0.08665,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15232,"mean_force":0.06211,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.61841,0.16498,0.23172]},{"body_a":"world","body_b":"grasp_target","contact_count":2556.0,"contact_point_centroid":[0.51251,0.03972,-0.00194],"force_p95":0.13017,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12282,"phase_index":0.0,"phase_name":"approach_pre_grasp","phase_type":"approach","tcp_position_centroid":[0.50138,0.05012,0.25584]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4079.0,"contact_point_centroid":[0.50004,0.01964,0.02948],"force_p95":0.07867,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13265,"mean_force":0.0518,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.49953,0.03884,0.02667]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.62857,0.16981,-0.00199],"force_p95":0.12278,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12412,"mean_force":0.12257,"phase_index":7.0,"phase_name":"retract_after_place","phase_type":"retract","tcp_position_centroid":[0.61777,0.16902,0.25539]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.51251,0.03972,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.50634,0.04338,0.09833]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":9255.0,"contact_point_centroid":[0.56382,0.08178,0.32053],"force_p95":0.08042,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10591,"mean_force":0.05357,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.56282,0.1007,0.32007]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8335.0,"contact_point_centroid":[0.56484,0.12062,0.32107],"force_p95":0.08773,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10328,"mean_force":0.05798,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.56358,0.10156,0.32026]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4943.0,"contact_point_centroid":[0.50003,0.05796,0.02849],"force_p95":0.07107,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08856,"mean_force":0.04483,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.49954,0.03884,0.02667]}],"total_contact_groups":16},"final_pose_error":0.08093,"key_states":{"actual_goal_position":[0.62757,0.17252,0.14502],"final_object_position":[0.62857,0.16981,0.01602],"final_tcp_position":[0.62377,0.17096,0.36877],"realised_goal_position":[0.62757,0.17252,0.14502],"realised_object_initial_position":[0.51251,0.03972,0.03]},"peak_contact_force":81.14225,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":640.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.03],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21001,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_pre_grasp","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2556.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_pre_grasp","tcp_end":[0.50815,0.04856,0.18111],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.1554,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_grasp","tcp_end":[0.50754,0.03949,0.03536],"tcp_start":[0.50815,0.04856,0.18111],"tcp_to_object_dist_end":0.01058,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51238,0.03876,0.02574],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21305,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.14034,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10822.0,"raw_peak_contact_force":0.21968,"subtask_id":"reach_grasp","tcp_end":[0.4995,0.03883,0.02664],"tcp_start":[0.50754,0.03949,0.03536],"tcp_to_object_dist_end":0.01291,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":42.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51954,0.03855,0.29958],"object_pos_start":[0.51238,0.03876,0.02574],"object_to_goal_dist_end":0.23131,"object_to_goal_dist_start":0.21305,"object_z_max":0.29932,"peak_contact_force":0.06988,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":38509.0,"raw_peak_contact_force":0.65663,"subtask_id":"reach_lift","tcp_end":[0.50888,0.03856,0.30995],"tcp_start":[0.4995,0.03883,0.02664],"tcp_to_object_dist_end":0.01487,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":38.0,"n_steps":483.0,"n_steps_budget":1000.0,"object_pos_end":[0.62536,0.16066,0.31973],"object_pos_start":[0.51954,0.03855,0.29958],"object_to_goal_dist_end":0.17512,"object_to_goal_dist_start":0.23131,"object_z_max":0.31971,"peak_contact_force":0.07377,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":17590.0,"raw_peak_contact_force":0.10591,"subtask_id":"reach_place","tcp_end":[0.61622,0.16067,0.33375],"tcp_start":[0.50888,0.03856,0.30995],"tcp_to_object_dist_end":0.01673,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":26.0,"n_steps":582.0,"n_steps_budget":1000.0,"object_pos_end":[0.62957,0.17032,0.10607],"object_pos_start":[0.62536,0.16066,0.31973],"object_to_goal_dist_end":0.03907,"object_to_goal_dist_start":0.17512,"object_z_max":0.31973,"peak_contact_force":0.09442,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":17269.0,"raw_peak_contact_force":0.15242,"subtask_id":"reach_place","tcp_end":[0.62239,0.1703,0.12486],"tcp_start":[0.61622,0.16067,0.33375],"tcp_to_object_dist_end":0.02012,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.62866,0.16983,0.01634],"object_pos_start":[0.62957,0.17032,0.10607],"object_to_goal_dist_end":0.12872,"object_to_goal_dist_start":0.03907,"object_z_max":0.10607,"peak_contact_force":0.11255,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1962.0,"raw_peak_contact_force":1.27616,"tcp_end":[0.61539,0.16816,0.14394],"tcp_start":[0.62239,0.1703,0.12486],"tcp_to_object_dist_end":0.1283,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.62857,0.16981,0.01602],"object_pos_start":[0.62866,0.16983,0.01634],"object_to_goal_dist_end":0.12904,"object_to_goal_dist_start":0.12872,"object_z_max":0.01639,"peak_contact_force":81.14225,"phase_name":"retract_after_place","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.12412,"subtask_id":"reach_retract","tcp_end":[0.62377,0.17096,0.36877],"tcp_start":[0.61539,0.16816,0.14394],"tcp_to_object_dist_end":0.35278,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `28f75809d7d1d0a11ca1a36dd459ad950e5a80b6bae34006f33ac9620425f5e5`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.05331,"average_solve_count":544.0,"average_success_count":544.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_pre_grasp.arc_height":0.1254,"approach_pre_grasp.speed":0.06221,"descend_to_grasp.descend_z":-0.01486,"descend_to_grasp.speed":0.05214,"descend_to_place.place_z":-0.03206,"descend_to_place.speed":0.03835,"grasp_object.grasp_duration":0.57061,"lift_object.lift_height":0.27432,"lift_object.speed":0.02275,"release_object.release_duration":0.36857,"retract_after_place.retract_z":0.32203,"retract_after_place.speed":0.05166,"transport_to_goal.speed":0.04869},"optimized_scores":{"best_composite_score":-0.23004,"best_fitness_score":0.59996,"best_task_score":0.23933},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":191.0,"contact_point_centroid":[0.58253,0.22714,-0.00774],"force_p95":1.30253,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.86809,"mean_force":0.39947,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.57334,0.2244,0.22021]},{"body_a":"world","body_b":"grasp_target","contact_count":84.0,"contact_point_centroid":[0.47865,0.04706,-0.00147],"force_p95":0.64354,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.66718,"mean_force":0.24354,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.46938,0.04759,0.02622]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":18064.0,"contact_point_centroid":[0.47281,0.06658,0.15491],"force_p95":0.07224,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2949,"mean_force":0.0502,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.47294,0.04739,0.15331]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":18562.0,"contact_point_centroid":[0.47263,0.02823,0.15524],"force_p95":0.07159,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2632,"mean_force":0.04855,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.47295,0.04739,0.15354]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.48272,0.04849,-0.00208],"force_p95":0.14798,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.22968,"mean_force":0.12966,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.47144,0.04782,0.02623]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":10554.0,"contact_point_centroid":[0.57781,0.20313,0.31527],"force_p95":0.07917,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15484,"mean_force":0.05389,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.57685,0.2222,0.31481]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":11023.0,"contact_point_centroid":[0.57806,0.24137,0.31172],"force_p95":0.07386,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15385,"mean_force":0.05255,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.57689,0.22232,0.31177]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":906.0,"contact_point_centroid":[0.57721,0.2068,0.20332],"force_p95":0.09734,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14882,"mean_force":0.05711,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.57653,0.22594,0.20327]},{"body_a":"world","body_b":"grasp_target","contact_count":1884.0,"contact_point_centroid":[0.4827,0.04873,-0.00193],"force_p95":0.13354,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12289,"phase_index":0.0,"phase_name":"approach_pre_grasp","phase_type":"approach","tcp_position_centroid":[0.49144,0.04038,0.25465]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.58438,0.22689,-0.00199],"force_p95":0.1229,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12576,"mean_force":0.12152,"phase_index":7.0,"phase_name":"retract_after_place","phase_type":"retract","tcp_position_centroid":[0.57544,0.22538,0.34706]},{"body_a":"world","body_b":"grasp_target","contact_count":3812.0,"contact_point_centroid":[0.4827,0.04873,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.47807,0.05101,0.10637]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1184.0,"contact_point_centroid":[0.57815,0.24494,0.20312],"force_p95":0.07297,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11287,"mean_force":0.04495,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.57657,0.22595,0.20335]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5031.0,"contact_point_centroid":[0.47011,0.02847,0.02802],"force_p95":0.06786,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10276,"mean_force":0.04293,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.4703,0.04771,0.02509]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":17411.0,"contact_point_centroid":[0.52698,0.11442,0.34733],"force_p95":0.06905,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09096,"mean_force":0.04639,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.52689,0.13353,0.34586]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":16030.0,"contact_point_centroid":[0.52739,0.153,0.34752],"force_p95":0.07234,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08921,"mean_force":0.04997,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.52705,0.13379,0.34608]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5452.0,"contact_point_centroid":[0.46993,0.067,0.02741],"force_p95":0.06735,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08613,"mean_force":0.04128,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.47031,0.04771,0.02509]}],"total_contact_groups":16},"final_pose_error":0.08353,"key_states":{"actual_goal_position":[0.58187,0.22885,0.23048],"final_object_position":[0.58438,0.22689,0.01602],"final_tcp_position":[0.58018,0.22754,0.46901],"realised_goal_position":[0.58187,0.22885,0.23048],"realised_object_initial_position":[0.4827,0.04873,0.03]},"peak_contact_force":1.86809,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":472.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.03],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28719,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_pre_grasp","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1884.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_pre_grasp","tcp_end":[0.48124,0.05402,0.18828],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.16235,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":953.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3812.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_grasp","tcp_end":[0.47804,0.04849,0.03291],"tcp_start":[0.48124,0.05402,0.18828],"tcp_to_object_dist_end":0.00832,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":47.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.48257,0.04776,0.0257],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.29085,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.14358,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12283.0,"raw_peak_contact_force":0.22968,"subtask_id":"reach_grasp","tcp_end":[0.47027,0.0477,0.02506],"tcp_start":[0.47804,0.04849,0.03291],"tcp_to_object_dist_end":0.01231,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":874.0,"n_steps_budget":1000.0,"object_pos_end":[0.49038,0.04751,0.27419],"object_pos_start":[0.48257,0.04776,0.0257],"object_to_goal_dist_end":0.20776,"object_to_goal_dist_start":0.29085,"object_z_max":0.27392,"peak_contact_force":0.06973,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":36710.0,"raw_peak_contact_force":0.66718,"subtask_id":"reach_lift","tcp_end":[0.47945,0.0475,0.28049],"tcp_start":[0.47027,0.0477,0.02506],"tcp_to_object_dist_end":0.01262,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":42.0,"n_steps":806.0,"n_steps_budget":1000.0,"object_pos_end":[0.5844,0.21859,0.40256],"object_pos_start":[0.49038,0.04751,0.27419],"object_to_goal_dist_end":0.1724,"object_to_goal_dist_start":0.20776,"object_z_max":0.40242,"peak_contact_force":0.06857,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":33441.0,"raw_peak_contact_force":0.09096,"subtask_id":"reach_place","tcp_end":[0.57597,0.21862,0.41449],"tcp_start":[0.47945,0.0475,0.28049],"tcp_to_object_dist_end":0.01461,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":38.0,"n_steps":579.0,"n_steps_budget":1000.0,"object_pos_end":[0.58561,0.22652,0.1911],"object_pos_start":[0.5844,0.21859,0.40256],"object_to_goal_dist_end":0.03963,"object_to_goal_dist_start":0.1724,"object_z_max":0.40256,"peak_contact_force":0.07246,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":21577.0,"raw_peak_contact_force":0.15484,"subtask_id":"reach_place","tcp_end":[0.5783,0.22666,0.20749],"tcp_start":[0.57597,0.21862,0.41449],"tcp_to_object_dist_end":0.01795,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.5844,0.2262,0.01268],"object_pos_start":[0.58561,0.22652,0.1911],"object_to_goal_dist_end":0.21784,"object_to_goal_dist_start":0.03963,"object_z_max":0.1911,"peak_contact_force":0.06899,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2281.0,"raw_peak_contact_force":1.86809,"tcp_end":[0.5733,0.22439,0.22758],"tcp_start":[0.5783,0.22666,0.20749],"tcp_to_object_dist_end":0.21519,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.58438,0.22689,0.01602],"object_pos_start":[0.5844,0.2262,0.01268],"object_to_goal_dist_end":0.21449,"object_to_goal_dist_start":0.21784,"object_z_max":0.01664,"peak_contact_force":0.12263,"phase_name":"retract_after_place","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.12576,"subtask_id":"reach_retract","tcp_end":[0.58018,0.22754,0.46901],"tcp_start":[0.5733,0.22439,0.22758],"tcp_to_object_dist_end":0.45301,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
```