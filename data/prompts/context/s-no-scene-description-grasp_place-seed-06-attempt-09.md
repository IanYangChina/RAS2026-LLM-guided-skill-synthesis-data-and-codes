## Search State

- **Seed**: 6
- **Iteration**: 10 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 9 | approach → descend → grasp → lift → approach → descend → release → retract | arc_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | impedance_control | impedance_control | force_threshold_switch | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 14 | -0.1292 | 0.29 | ❌ rejected |
| 8 | approach → descend → grasp → lift → approach → descend → release → retract | arc_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | impedance_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | time_limit | time_limit | pose_tolerance | 14 | -0.2650 | 0.27 | ❌ rejected |
| 7 | approach → descend → grasp → lift → approach → descend → release → retract | arc_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | force_threshold_switch | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 15 | -0.1803 | 0.29 | ❌ rejected |
| 6 | approach → descend → grasp → lift → approach → descend → release → retract | arc_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | impedance_control | position_control | force_threshold_switch | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 15 | -0.2966 | 0.31 | ✅ accepted |
| 5 | approach → descend → grasp → lift → approach → descend → release → retract | arc_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 14 | -0.2877 | 0.23 | ❌ rejected |

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

## Current Skill (Q=-0.129) — your mutation base

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

- **Composite score**: -0.129
- **task_score** (E): 0.293
- **fitness_score**: 0.626  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.125
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.880

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_pre_grasp | 1.00 | 1.00 | 0.1243 |
| descend_to_grasp | 1.00 | 1.00 | 0.1497 |
| grasp_object | 1.00 | 1.00 | 0.0115 |
| lift_object | 1.00 | 1.00 | 0.2144 |
| transport_to_goal | 1.00 | 1.00 | 0.2439 |
| descend_to_place | 1.00 | 1.00 | 0.0435 |
| release_object | 1.00 | 0.67 | 0.0201 |
| retract_after_place | 1.00 | 1.00 | 0.0820 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_pre_grasp | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.496, 0.031, 0.184) | (0.500, 0.024, 0.030)→(0.500, 0.024, 0.026) | 0.269→0.271 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_to_grasp | descend | 1.00 / step_budget | (0.496, 0.031, 0.184)→(0.495, 0.024, 0.035) | (0.500, 0.024, 0.026)→(0.500, 0.024, 0.026) | 0.271→0.271 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_object | grasp | 1.00 / step_budget | (0.495, 0.024, 0.035)→(0.487, 0.024, 0.026) | (0.500, 0.024, 0.026)→(0.500, 0.024, 0.026) | 0.271→0.272 | 1.00 / 43.000 | 0.136 | 0.194 |
| lift_object | lift | 1.00 / step_budget | (0.487, 0.024, 0.026)→(0.496, 0.024, 0.241) | (0.500, 0.024, 0.026)→(0.507, 0.024, 0.233) | 0.272→0.199 | 1.00 / 39.667 | 12.340 | 0.649 |
| transport_to_goal | approach | 1.00 / step_budget | (0.496, 0.024, 0.241)→(0.593, 0.187, 0.391) | (0.507, 0.024, 0.233)→(0.603, 0.187, 0.377) | 0.199→0.169 | 1.00 / 31.333 | 0.106 | 0.137 |
| descend_to_place | descend | 1.00 / force_exceeded | (0.593, 0.187, 0.391)→(0.593, 0.189, 0.348) | (0.603, 0.187, 0.377)→(0.603, 0.189, 0.332) | 0.169→0.125 | 1.00 / 31.000 | 3299.829 | 0.194 |
| release_object | release | 1.00 / step_budget | (0.593, 0.189, 0.348)→(0.591, 0.188, 0.368) | (0.603, 0.189, 0.332)→(0.594, 0.192, 0.021) | 0.125→0.187 | 0.67 / 2.667 | 0.475 | 1.567 |
| retract_after_place | retract | 1.00 / step_budget | (0.591, 0.188, 0.368)→(0.597, 0.194, 0.448) | (0.594, 0.192, 0.021)→(0.592, 0.196, 0.017) | 0.187→0.192 | 1.00 / 4.000 | 0.113 | 1.181 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.426
- phase_score: 0.433
- phase_breakdown.reach_retract_score: 0.137
- phase_breakdown.reach_lift_score: 0.533
- phase_breakdown.reach_pre_grasp_score: 0.320
- phase_breakdown.reach_place_score: 0.494
- phase_breakdown.reach_grasp_score: 0.690
- grasp_place_fitness: 0.692

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.692
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.426
- **Median Q (composite search score)**: -0.155
- **K-run variance**: 0.0022
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.258


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.99436,"average_solve_count":532.0,"average_success_count":532.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_pre_grasp.arc_height":0.08943,"approach_pre_grasp.speed":0.06463,"descend_to_grasp.descend_z":-0.01252,"descend_to_grasp.speed":0.01975,"descend_to_place.force_threshold":12.94751,"descend_to_place.place_z_offset":-0.02132,"descend_to_place.speed":0.0187,"grasp_object.grasp_duration":0.52309,"lift_object.lift_height":0.26741,"lift_object.speed":0.05222,"release_object.release_duration":0.31554,"retract_after_place.retract_z":0.31866,"retract_after_place.speed":0.06153,"transport_to_goal.speed":0.03877},"optimized_scores":{"best_composite_score":-0.16933,"best_fitness_score":0.58567,"best_task_score":0.21262},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":92.0,"contact_point_centroid":[0.58479,0.17961,-0.01126],"force_p95":1.74029,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.94992,"mean_force":0.85155,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.58004,0.18067,0.32954]},{"body_a":"world","body_b":"grasp_target","contact_count":84.0,"contact_point_centroid":[0.50044,-0.01469,-0.0014],"force_p95":0.61883,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.67081,"mean_force":0.1899,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.48978,-0.01516,0.02625]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":16615.0,"contact_point_centroid":[0.49397,0.00407,0.15303],"force_p95":0.07784,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31128,"mean_force":0.05365,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.49365,-0.01506,0.15078]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":17215.0,"contact_point_centroid":[0.49385,-0.03415,0.1492],"force_p95":0.07627,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29535,"mean_force":0.05224,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.49346,-0.01506,0.14726]},{"body_a":"world","body_b":"grasp_target","contact_count":3300.0,"contact_point_centroid":[0.58632,0.17948,-0.00219],"force_p95":0.12386,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.28894,"mean_force":0.12028,"phase_index":7.0,"phase_name":"retract_after_place","phase_type":"retract","tcp_position_centroid":[0.58319,0.18358,0.43663]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8810.0,"contact_point_centroid":[0.58413,0.19846,0.37261],"force_p95":0.07255,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18411,"mean_force":0.05206,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.58252,0.17935,0.37268]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50381,-0.01548,-0.00204],"force_p95":0.13662,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.17813,"mean_force":0.12656,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.49198,-0.01519,0.02637]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8816.0,"contact_point_centroid":[0.5842,0.16029,0.37288],"force_p95":0.07266,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15351,"mean_force":0.05159,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.58252,0.17935,0.37272]},{"body_a":"world","body_b":"grasp_target","contact_count":1992.0,"contact_point_centroid":[0.50382,-0.01567,-0.00193],"force_p95":0.13279,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12287,"phase_index":0.0,"phase_name":"approach_pre_grasp","phase_type":"approach","tcp_position_centroid":[0.49909,0.01831,0.23634]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1080.0,"contact_point_centroid":[0.58325,0.16246,0.30893],"force_p95":0.07303,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12818,"mean_force":0.04747,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.5819,0.1816,0.30916]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.50382,-0.01567,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.4978,-0.01118,0.10011]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4097.0,"contact_point_centroid":[0.49126,0.00402,0.02789],"force_p95":0.07735,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11683,"mean_force":0.05178,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.4908,-0.01518,0.02513]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":16595.0,"contact_point_centroid":[0.54029,0.09873,0.35033],"force_p95":0.0798,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.105,"mean_force":0.05364,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.53951,0.07957,0.34903]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1139.0,"contact_point_centroid":[0.58335,0.20074,0.30852],"force_p95":0.07314,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10097,"mean_force":0.04558,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.58188,0.18159,0.3091]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4905.0,"contact_point_centroid":[0.49136,-0.03427,0.02697],"force_p95":0.06874,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09181,"mean_force":0.0448,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.4908,-0.01518,0.02513]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":18635.0,"contact_point_centroid":[0.5406,0.06192,0.35102],"force_p95":0.07282,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09039,"mean_force":0.0483,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.54013,0.08094,0.35021]}],"total_contact_groups":16},"final_pose_error":0.01979,"key_states":{"actual_goal_position":[0.58691,0.18745,0.24812],"final_object_position":[0.58631,0.17948,0.01602],"final_tcp_position":[0.58915,0.18767,0.54711],"realised_goal_position":[0.58691,0.18745,0.24812],"realised_object_initial_position":[0.50382,-0.01567,0.03]},"peak_contact_force":9760.30694,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":499.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.03],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.30942,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_pre_grasp","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1992.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_pre_grasp","tcp_end":[0.49997,-0.00661,0.17861],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.15291,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_grasp","tcp_end":[0.49877,-0.01528,0.03352],"tcp_start":[0.49997,-0.00661,0.17861],"tcp_to_object_dist_end":0.00905,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50368,-0.01505,0.02584],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.312,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.13326,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10802.0,"raw_peak_contact_force":0.17813,"subtask_id":"reach_grasp","tcp_end":[0.49077,-0.01517,0.0251],"tcp_start":[0.49877,-0.01528,0.03352],"tcp_to_object_dist_end":0.01293,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":869.0,"n_steps_budget":1000.0,"object_pos_end":[0.51197,-0.01501,0.26601],"object_pos_start":[0.50368,-0.01505,0.02584],"object_to_goal_dist_end":0.21662,"object_to_goal_dist_start":0.312,"object_z_max":0.26574,"peak_contact_force":0.06982,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":33914.0,"raw_peak_contact_force":0.67081,"subtask_id":"reach_lift","tcp_end":[0.50041,-0.01501,0.27355],"tcp_start":[0.49077,-0.01517,0.0251],"tcp_to_object_dist_end":0.0138,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":32.0,"n_steps":894.0,"n_steps_budget":1000.0,"object_pos_end":[0.59065,0.17763,0.41754],"object_pos_start":[0.51197,-0.01501,0.26601],"object_to_goal_dist_end":0.16975,"object_to_goal_dist_start":0.21662,"object_z_max":0.4174,"peak_contact_force":0.09306,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":35230.0,"raw_peak_contact_force":0.105,"subtask_id":"reach_place","tcp_end":[0.5825,0.17724,0.43179],"tcp_start":[0.50041,-0.01501,0.27355],"tcp_to_object_dist_end":0.01642,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":34.0,"n_steps":464.0,"n_steps_budget":1000.0,"object_pos_end":[0.58996,0.18191,0.29555],"object_pos_start":[0.59065,0.17763,0.41754],"object_to_goal_dist_end":0.04785,"object_to_goal_dist_start":0.16975,"object_z_max":0.41754,"peak_contact_force":9760.30694,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":17626.0,"raw_peak_contact_force":0.18411,"tcp_end":[0.58292,0.18195,0.31287],"tcp_start":[0.5825,0.17724,0.43179],"tcp_to_object_dist_end":0.0187,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.58592,0.17912,-0.00577],"object_pos_start":[0.58996,0.18191,0.29555],"object_to_goal_dist_end":0.25403,"object_to_goal_dist_start":0.04785,"object_z_max":0.29555,"peak_contact_force":0.31764,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2311.0,"raw_peak_contact_force":1.94992,"tcp_end":[0.58002,0.18067,0.33324],"tcp_start":[0.58292,0.18195,0.31287],"tcp_to_object_dist_end":0.33907,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":825.0,"n_steps_budget":1000.0,"object_pos_end":[0.58631,0.17948,0.01602],"object_pos_start":[0.58592,0.17912,-0.00577],"object_to_goal_dist_end":0.23224,"object_to_goal_dist_start":0.25403,"object_z_max":0.01686,"peak_contact_force":0.12263,"phase_name":"retract_after_place","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3300.0,"raw_peak_contact_force":0.28894,"subtask_id":"reach_retract","tcp_end":[0.58915,0.18767,0.54711],"tcp_start":[0.58002,0.18067,0.33324],"tcp_to_object_dist_end":0.53117,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `fe7e0be33c0bb4db9d2bbbb069b6113d0e5a69a675a0d70bc1f582243e99e3cf`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.95954,"average_solve_count":346.0,"average_success_count":346.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_pre_grasp.arc_height":0.12658,"approach_pre_grasp.speed":0.0393,"descend_to_grasp.descend_z":-0.02054,"descend_to_grasp.speed":0.04909,"descend_to_place.force_threshold":7.79317,"descend_to_place.place_z_offset":-0.02311,"descend_to_place.speed":0.03639,"grasp_object.grasp_duration":0.41644,"lift_object.lift_height":0.19256,"lift_object.speed":0.04863,"release_object.release_duration":0.21875,"retract_after_place.retract_z":0.21928,"retract_after_place.speed":0.04368,"transport_to_goal.speed":0.04379},"optimized_scores":{"best_composite_score":-0.06328,"best_fitness_score":0.69172,"best_task_score":0.42588},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":48.0,"contact_point_centroid":[0.62259,0.16058,-0.01394],"force_p95":2.45595,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.46583,"mean_force":1.42821,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.61605,0.16361,0.33417]},{"body_a":"world","body_b":"grasp_target","contact_count":224.0,"contact_point_centroid":[0.61901,0.16656,-0.00727],"force_p95":0.58541,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.04084,"mean_force":0.15602,"phase_index":7.0,"phase_name":"retract_after_place","phase_type":"retract","tcp_position_centroid":[0.61841,0.16548,0.34073]},{"body_a":"world","body_b":"grasp_target","contact_count":86.0,"contact_point_centroid":[0.5086,0.03866,-0.00141],"force_p95":0.59031,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.63225,"mean_force":0.21283,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.49823,0.0391,0.0283]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1180.0,"contact_point_centroid":[0.61836,0.18361,0.31364],"force_p95":0.07718,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.3621,"mean_force":0.04825,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.61775,0.1644,0.3137]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":12169.0,"contact_point_centroid":[0.50158,0.05794,0.11087],"force_p95":0.07695,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2984,"mean_force":0.05276,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.50145,0.03883,0.10876]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":11759.0,"contact_point_centroid":[0.50184,0.01971,0.11334],"force_p95":0.0776,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29678,"mean_force":0.05393,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.5016,0.03883,0.11084]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1315.0,"contact_point_centroid":[0.61822,0.14516,0.31404],"force_p95":0.07565,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26657,"mean_force":0.04697,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.61769,0.16438,0.31349]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.51251,0.03953,-0.00204],"force_p95":0.13665,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.17746,"mean_force":0.1265,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.50036,0.0393,0.0285]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":924.0,"contact_point_centroid":[0.61946,0.18416,0.32455],"force_p95":0.07088,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14875,"mean_force":0.04928,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.61917,0.16493,0.32401]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":924.0,"contact_point_centroid":[0.61957,0.14583,0.32487],"force_p95":0.06976,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14681,"mean_force":0.04741,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.61917,0.16493,0.32401]},{"body_a":"world","body_b":"grasp_target","contact_count":2008.0,"contact_point_centroid":[0.51251,0.03972,-0.00193],"force_p95":0.13256,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12287,"phase_index":0.0,"phase_name":"approach_pre_grasp","phase_type":"approach","tcp_position_centroid":[0.50179,0.03637,0.25163]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.51251,0.03972,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.50598,0.04218,0.1011]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4099.0,"contact_point_centroid":[0.49979,0.02,0.03],"force_p95":0.07731,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11914,"mean_force":0.05174,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.49916,0.0392,0.02721]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":15883.0,"contact_point_centroid":[0.56444,0.12289,0.26495],"force_p95":0.07132,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08961,"mean_force":0.04974,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.56419,0.10367,0.26357]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":17288.0,"contact_point_centroid":[0.56358,0.08387,0.26423],"force_p95":0.06848,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08902,"mean_force":0.0461,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.56356,0.10298,0.26282]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4905.0,"contact_point_centroid":[0.49978,0.05829,0.029],"force_p95":0.06961,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08654,"mean_force":0.04482,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.49917,0.0392,0.02721]}],"total_contact_groups":16},"final_pose_error":0.01994,"key_states":{"actual_goal_position":[0.62757,0.17252,0.14502],"final_object_position":[0.6191,0.16456,0.01752],"final_tcp_position":[0.62146,0.16798,0.34587],"realised_goal_position":[0.62757,0.17252,0.14502],"realised_object_initial_position":[0.51251,0.03972,0.03]},"peak_contact_force":37.25245,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":503.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.03],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21001,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_pre_grasp","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2008.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_pre_grasp","tcp_end":[0.50767,0.04534,0.18655],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.1607,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_grasp","tcp_end":[0.50718,0.03987,0.03591],"tcp_start":[0.50767,0.04534,0.18655],"tcp_to_object_dist_end":0.01123,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51238,0.03909,0.02584],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21279,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.1331,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10804.0,"raw_peak_contact_force":0.17746,"subtask_id":"reach_grasp","tcp_end":[0.49913,0.03919,0.02717],"tcp_start":[0.50718,0.03987,0.03591],"tcp_to_object_dist_end":0.01331,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":614.0,"n_steps_budget":1000.0,"object_pos_end":[0.51934,0.03886,0.19226],"object_pos_start":[0.51238,0.03909,0.02584],"object_to_goal_dist_end":0.17835,"object_to_goal_dist_start":0.21279,"object_z_max":0.192,"peak_contact_force":0.08048,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":24014.0,"raw_peak_contact_force":0.63225,"subtask_id":"reach_lift","tcp_end":[0.5081,0.03882,0.19891],"tcp_start":[0.49913,0.03919,0.02717],"tcp_to_object_dist_end":0.01306,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":42.0,"n_steps":795.0,"n_steps_budget":1000.0,"object_pos_end":[0.62804,0.16464,0.31585],"object_pos_start":[0.51934,0.03886,0.19226],"object_to_goal_dist_end":0.171,"object_to_goal_dist_start":0.17835,"object_z_max":0.31571,"peak_contact_force":0.0684,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":33171.0,"raw_peak_contact_force":0.08961,"subtask_id":"reach_place","tcp_end":[0.61957,0.16469,0.32845],"tcp_start":[0.5081,0.03882,0.19891],"tcp_to_object_dist_end":0.01519,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":44.0,"n_steps_budget":1000.0,"object_pos_end":[0.62736,0.16476,0.30473],"object_pos_start":[0.62804,0.16464,0.31585],"object_to_goal_dist_end":0.15989,"object_to_goal_dist_start":0.171,"object_z_max":0.31586,"peak_contact_force":37.25245,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1848.0,"raw_peak_contact_force":0.14875,"tcp_end":[0.61876,0.16477,0.31794],"tcp_start":[0.61957,0.16469,0.32845],"tcp_to_object_dist_end":0.01576,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.61885,0.15885,-0.01518],"object_pos_start":[0.62736,0.16476,0.30473],"object_to_goal_dist_end":0.16103,"object_to_goal_dist_start":0.15989,"object_z_max":0.30473,"peak_contact_force":1.10723,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2543.0,"raw_peak_contact_force":2.46583,"tcp_end":[0.61605,0.1636,0.33704],"tcp_start":[0.61876,0.16477,0.31794],"tcp_to_object_dist_end":0.35227,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":56.0,"n_steps_budget":600.0,"object_pos_end":[0.6191,0.16456,0.01752],"object_pos_start":[0.61885,0.15885,-0.01518],"object_to_goal_dist_end":0.12804,"object_to_goal_dist_start":0.16103,"object_z_max":0.01748,"peak_contact_force":0.1136,"phase_name":"retract_after_place","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":224.0,"raw_peak_contact_force":1.04084,"subtask_id":"reach_retract","tcp_end":[0.62146,0.16798,0.34587],"tcp_start":[0.61605,0.1636,0.33704],"tcp_to_object_dist_end":0.32838,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `28f75809d7d1d0a11ca1a36dd459ad950e5a80b6bae34006f33ac9620425f5e5`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.13932,"average_solve_count":323.0,"average_success_count":323.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_pre_grasp.arc_height":0.1133,"approach_pre_grasp.speed":0.0522,"descend_to_grasp.descend_z":-0.01308,"descend_to_grasp.speed":0.05136,"descend_to_place.force_threshold":10.83553,"descend_to_place.place_z_offset":-0.0268,"descend_to_place.speed":0.02655,"grasp_object.grasp_duration":0.51344,"lift_object.lift_height":0.24328,"lift_object.speed":0.05299,"release_object.release_duration":0.35223,"retract_after_place.retract_z":0.24134,"retract_after_place.speed":0.0511,"transport_to_goal.speed":0.06171},"optimized_scores":{"best_composite_score":-0.15491,"best_fitness_score":0.60009,"best_task_score":0.23963},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":298.0,"contact_point_centroid":[0.57223,0.24449,-0.00809],"force_p95":1.50455,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.21227,"mean_force":0.35665,"phase_index":7.0,"phase_name":"retract_after_place","phase_type":"retract","tcp_position_centroid":[0.57826,0.22277,0.44354]},{"body_a":"world","body_b":"grasp_target","contact_count":84.0,"contact_point_centroid":[0.48004,0.04718,-0.00143],"force_p95":0.53991,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.64509,"mean_force":0.17987,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.46932,0.04763,0.02817]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":14687.0,"contact_point_centroid":[0.47286,0.06657,0.13663],"force_p95":0.07866,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30103,"mean_force":0.05353,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.47262,0.04744,0.13454]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":784.0,"contact_point_centroid":[0.57928,0.20169,0.4061],"force_p95":0.20927,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2843,"mean_force":0.08833,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.57591,0.21984,0.40875]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":848.0,"contact_point_centroid":[0.57952,0.23864,0.40486],"force_p95":0.22058,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27963,"mean_force":0.10298,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.57586,0.21977,0.40826]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":14668.0,"contact_point_centroid":[0.47315,0.02835,0.1401],"force_p95":0.0774,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27161,"mean_force":0.05317,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.47279,0.04744,0.13775]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":72.0,"contact_point_centroid":[0.58051,0.23887,0.41058],"force_p95":0.20723,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25031,"mean_force":0.12051,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.57639,0.21995,0.41364]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":88.0,"contact_point_centroid":[0.58032,0.2018,0.41109],"force_p95":0.17224,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23842,"mean_force":0.0871,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.57639,0.21995,0.41364]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.48271,0.04852,-0.00208],"force_p95":0.14691,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.22557,"mean_force":0.12931,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.47147,0.04787,0.0281]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":14832.0,"contact_point_centroid":[0.52554,0.1096,0.32558],"force_p95":0.09001,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2159,"mean_force":0.05877,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.52354,0.12843,0.3246]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":13593.0,"contact_point_centroid":[0.52746,0.15049,0.32886],"force_p95":0.09103,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20837,"mean_force":0.06384,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.52528,0.13146,0.32755]},{"body_a":"world","body_b":"grasp_target","contact_count":2032.0,"contact_point_centroid":[0.4827,0.04873,-0.00193],"force_p95":0.13256,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12287,"phase_index":0.0,"phase_name":"approach_pre_grasp","phase_type":"approach","tcp_position_centroid":[0.49159,0.04237,0.25571]},{"body_a":"world","body_b":"grasp_target","contact_count":3748.0,"contact_point_centroid":[0.4827,0.04873,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.47804,0.05152,0.10709]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5041.0,"contact_point_centroid":[0.47014,0.02852,0.02986],"force_p95":0.06753,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10445,"mean_force":0.04291,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.47034,0.04776,0.02696]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5446.0,"contact_point_centroid":[0.46995,0.06705,0.02925],"force_p95":0.06722,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08369,"mean_force":0.04123,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.47034,0.04776,0.02696]}],"total_contact_groups":15},"final_pose_error":0.01979,"key_states":{"actual_goal_position":[0.58187,0.22885,0.23048],"final_object_position":[0.5718,0.24437,0.01698],"final_tcp_position":[0.58013,0.2255,0.4524],"realised_goal_position":[0.58187,0.22885,0.23048],"realised_object_initial_position":[0.4827,0.04873,0.03]},"peak_contact_force":101.92827,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":509.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.03],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28719,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_pre_grasp","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2032.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_pre_grasp","tcp_end":[0.48116,0.05502,0.18761],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.16172,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":937.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3748.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_grasp","tcp_end":[0.47806,0.04854,0.03478],"tcp_start":[0.48116,0.05502,0.18761],"tcp_to_object_dist_end":0.00992,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":47.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.48258,0.04783,0.02571],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.2908,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.14287,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12287.0,"raw_peak_contact_force":0.22557,"subtask_id":"reach_grasp","tcp_end":[0.47031,0.04775,0.02693],"tcp_start":[0.47806,0.04854,0.03478],"tcp_to_object_dist_end":0.01233,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":39.0,"n_steps":759.0,"n_steps_budget":1000.0,"object_pos_end":[0.49017,0.04757,0.24126],"object_pos_start":[0.48258,0.04783,0.02571],"object_to_goal_dist_end":0.20345,"object_to_goal_dist_start":0.2908,"object_z_max":0.24099,"peak_contact_force":36.86858,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":29439.0,"raw_peak_contact_force":0.64509,"subtask_id":"reach_lift","tcp_end":[0.47908,0.04754,0.24942],"tcp_start":[0.47031,0.04775,0.02693],"tcp_to_object_dist_end":0.01377,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":20.0,"n_steps":876.0,"n_steps_budget":1000.0,"object_pos_end":[0.59069,0.2201,0.39733],"object_pos_start":[0.49017,0.04757,0.24126],"object_to_goal_dist_end":0.16731,"object_to_goal_dist_start":0.20345,"object_z_max":0.39722,"peak_contact_force":0.15782,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":28425.0,"raw_peak_contact_force":0.2159,"subtask_id":"reach_place","tcp_end":[0.57643,0.21971,0.41384],"tcp_start":[0.47908,0.04754,0.24942],"tcp_to_object_dist_end":0.02182,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":19.0,"n_steps":8.0,"n_steps_budget":1000.0,"object_pos_end":[0.59043,0.22072,0.3962],"object_pos_start":[0.59069,0.2201,0.39733],"object_to_goal_dist_end":0.16613,"object_to_goal_dist_start":0.16731,"object_z_max":0.39733,"peak_contact_force":101.92827,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":160.0,"raw_peak_contact_force":0.25031,"tcp_end":[0.57633,0.22012,0.41302],"tcp_start":[0.57643,0.21971,0.41384],"tcp_to_object_dist_end":0.02196,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.57837,0.23859,0.0847],"object_pos_start":[0.59043,0.22072,0.3962],"object_to_goal_dist_end":0.14615,"object_to_goal_dist_start":0.16613,"object_z_max":0.3962,"peak_contact_force":0.0,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1632.0,"raw_peak_contact_force":0.2843,"tcp_end":[0.57587,0.21928,0.4333],"tcp_start":[0.57633,0.22012,0.41302],"tcp_to_object_dist_end":0.34914,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":88.0,"n_steps_budget":600.0,"object_pos_end":[0.5718,0.24437,0.01698],"object_pos_start":[0.57837,0.23859,0.0847],"object_to_goal_dist_end":0.2143,"object_to_goal_dist_start":0.14615,"object_z_max":0.0847,"peak_contact_force":0.10277,"phase_name":"retract_after_place","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":298.0,"raw_peak_contact_force":2.21227,"subtask_id":"reach_retract","tcp_end":[0.58013,0.2255,0.4524],"tcp_start":[0.57587,0.21928,0.4333],"tcp_to_object_dist_end":0.4359,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```