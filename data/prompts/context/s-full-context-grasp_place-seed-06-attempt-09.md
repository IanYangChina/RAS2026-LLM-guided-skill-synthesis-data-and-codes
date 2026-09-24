## Search State

- **Seed**: 6
- **Iteration**: 10 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 9 | approach → descend → grasp → lift → approach → descend → release → retract | arc_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 14 | -0.2636 | 0.31 | ❌ rejected |
| 8 | approach → descend → grasp → lift → approach | arc_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | 9 | 0.2855 | 0.73 | ✅ accepted |
| 7 | approach → descend → grasp → lift → approach → release → retract | arc_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 12 | -0.1355 | 0.30 | ✅ accepted |
| 6 | approach → descend → grasp → lift → approach → release → retract | arc_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 12 | -0.1606 | 0.25 | ❌ rejected |
| 5 | approach → descend → grasp → lift → approach → release → retract | arc_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 12 | -0.1606 | 0.25 | ❌ rejected |

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
- Frozen realised-scene SHA-256: `584133b5261cffac0dd4282704ff39e97bf4d452e60b02507679bbdea5a4de22`
- Frozen object start: [0.5038164351471943, -0.015672913018666156, 0.03]
- Frozen task target: [0.5869067239795378, 0.18744967655878825, 0.24811674852797]
- Goal object position: (0.5869067239795378, 0.18744967655878825, 0.24811674852797)
- place_goal_position (task success criterion — final object 3D position must be close to the realised airborne target here): (0.5869067239795378, 0.18744967655878825, 0.24811674852797)
- Grasp/lift components are optimiser fitness diagnostics only; canonical task_score is final object-to-realised-target proximity.
- Object initial pose: (0.5038164351471943, -0.015672913018666156, 0.03)
- Goal tolerance: 0.02 m
- Expressivity sigma: 0.15 m
- Expressivity threshold: 0.3
- Force limit: 20.0 N
- Robot initial TCP position: (0.5, 0.0, 0.3)
- Robot initial gripper state: **open** (gripper starts fully open; ensure a `grasp`/`force_grasp` phase closes it before lifting)
- Phase navigation guidance: the task `phase_target_map` may provide internal predefined TCP waypoint aliases / semantic phase ids. These names are not DSL phase types and are intentionally not enumerated here to avoid confusing ids with types. Phase `id` may be semantic, but phase `type` must be exactly one of the DSL enum values listed in the prompt.
- Primary evaluation target: **final object-to-realised-airborne-3D-target proximity. Grasp/lift signals are optimiser fitness diagnostics only; they do not gate the canonical task_score.**

## Scene Entities

robot:
  model: panda_full
  tcp_site: attachment_site
  gripper: franka_hand
  tcp_initial_world: [0.5, 0, 0.3]
objects:
  - name: grasp_target
    role: manipulated_object
    dynamics: free
    geometry: box
    dimensions_m: [0.04, 0.04, 0.06]
    mass_kg: 0.05
  - name: placement_surface
    role: goal_area
    dynamics: static
    geometry: point
task_landmarks:
  frozen_object_start: [0.5038, -0.0157, 0.03]
  frozen_task_target: [0.5869, 0.1874, 0.2481]
  frozen_object_starts: {'grasp_target': [0.5038164351471943, -0.015672913018666156, 0.03]}
  frozen_targets: {'place_target': [0.5869067239795378, 0.18744967655878825, 0.24811674852797]}
  goal_tolerance_m: 0.02
  force_limit_n: 20
  force_scale_n: 5
  realized_scene_sha256: 584133b5261cffac0dd4282704ff39e97bf4d452e60b02507679bbdea5a4de22

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
| `object` | offset from object initial position (0.5038164351471943, -0.015672913018666156, 0.03) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.5869067239795378, 0.18744967655878825, 0.24811674852797) | final destination targets |
| `fixture` | offset from fixture pose (if defined, else world) | targets near fixture |

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

## Current Skill (Q=-0.264) — your mutation base

```yaml
skill: grasp_place
dsl_version: 2
skill_type: arm_gripper
subtasks:
- id: approach_pre_grasp
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.12
  weight: 0.2
- id: reach_grasp
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.04
  weight: 0.2
- id: lift_clearance
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
  - 0.035
  weight: 0.4
phases:
- id: approach_above
  type: approach
  generator: arc_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    entity: grasp_target
    offset:
    - 0.0
    - 0.0
    - 0.12
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    approach_height:
      type: scalar
      range:
      - 0.08
      - 0.18
      default: 0.12
      binds_to:
      - path: target.offset.z
        mode: replace
    arc_height:
      type: scalar
      range:
      - 0.02
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.arc_height
        mode: replace
    speed:
      type: scalar
      range:
      - 0.02
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: approach_pre_grasp
- id: descend_to_grasp
  type: descend
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    entity: grasp_target
    offset:
    - 0.0
    - 0.0
    - 0.04
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    descend_offset:
      type: scalar
      range:
      - 0.02
      - 0.08
      default: 0.04
      binds_to:
      - path: target.offset.z
        mode: replace
    speed:
      type: scalar
      range:
      - 0.01
      - 0.05
      default: 0.03
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: reach_grasp
- id: grasp_close
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
  parameters:
    grasp_duration:
      type: scalar
      range:
      - 0.05
      - 0.3
      default: 0.15
      binds_to:
      - path: duration.max_time
        mode: replace
  guards:
  - id: check_grasp
    when: after_phase
    predicate: bilateral_grasp
    threshold: 0.5
    on_failure: retry
  retries:
    max_attempts: 1
    strategy: repeat
- id: lift_object
  type: lift
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.2
      axis: world_z
      mode: add_to_offset
      sign: positive
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    lift_distance:
      type: scalar
      range:
      - 0.1
      - 0.35
      default: 0.2
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    speed:
      type: scalar
      range:
      - 0.02
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: lift_clearance
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
    - 0.035
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    transport_speed:
      type: scalar
      range:
      - 0.05
      - 0.3
      default: 0.15
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: reach_goal

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_above** (`approach`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.12], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_height: status=consumed; consumers=target.offset.z (replace)
    - arc_height: status=consumed; consumers=generator.arc_height (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
- **descend_to_grasp** (`descend`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.04], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - descend_offset: status=consumed; consumers=target.offset.z (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
- **grasp_close** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings:
    - grasp_duration: status=consumed; consumers=duration.max_time (replace)
  - guards:
    - id=check_grasp, when=after_phase, predicate=bilateral_grasp, on_failure=retry, threshold=0.5
  - retries: max_attempts=1, strategy=repeat
- **lift_object** (`lift`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=world_z, distance=0.2, mode=add_to_offset, sign=positive}, tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - lift_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
- **transport_to_goal** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.035], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - transport_speed: status=consumed; consumers=generator.speed (replace)

## Design Metrics

- **Composite score**: -0.264
- **task_score** (E): 0.309
- **fitness_score**: 0.616  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.880

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_above | 1.00 | 1.00 | 0.1553 |
| descend_to_grasp | 1.00 | 1.00 | 0.0971 |
| grasp_close | 1.00 | 1.00 | 0.0117 |
| lift_object | 1.00 | 1.00 | 0.1953 |
| transport_to_goal | 1.00 | 1.00 | 0.1625 |
| descend_to_place | 1.00 | 1.00 | 0.0463 |
| release_object | 1.00 | 1.00 | 0.0209 |
| retract_from_goal | 0.00 | 1.00 | 0.2733 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_above | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.496, 0.033, 0.152) | (0.500, 0.024, 0.030)→(0.500, 0.024, 0.026) | 0.269→0.271 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_to_grasp | descend | 1.00 / step_budget | (0.496, 0.033, 0.152)→(0.495, 0.025, 0.056) | (0.500, 0.024, 0.026)→(0.500, 0.024, 0.026) | 0.271→0.271 | 1.00 / 4.000 | 8.478 | 0.123 |
| grasp_close | grasp | 1.00 / step_budget | (0.495, 0.025, 0.056)→(0.487, 0.025, 0.047) | (0.500, 0.024, 0.026)→(0.500, 0.025, 0.026) | 0.271→0.271 | 1.00 / 43.333 | 0.168 | 0.196 |
| lift_object | lift | 1.00 / step_budget | (0.487, 0.025, 0.047)→(0.484, 0.024, 0.242) | (0.500, 0.025, 0.026)→(0.490, 0.025, 0.216) | 0.271→0.209 | 1.00 / 38.000 | 55983.961 | 0.395 |
| transport_to_goal | approach | 1.00 / step_budget | (0.484, 0.024, 0.242)→(0.572, 0.156, 0.239) | (0.490, 0.025, 0.216)→(0.572, 0.155, 0.207) | 0.209→0.051 | 1.00 / 24.667 | 3253.515 | 0.271 |
| descend_to_place | descend | 1.00 / step_budget | (0.572, 0.156, 0.239)→(0.594, 0.193, 0.228) | (0.572, 0.155, 0.207)→(0.592, 0.194, 0.128) | 0.051→0.080 | 1.00 / 17.000 | 0.120 | 1.122 |
| release_object | release | 1.00 / step_budget | (0.594, 0.193, 0.228)→(0.590, 0.191, 0.248) | (0.592, 0.194, 0.128)→(0.585, 0.193, 0.022) | 0.080→0.187 | 1.00 / 3.333 | 0.177 | 1.108 |
| retract_from_goal | retract | 0.00 / step_budget | (0.590, 0.191, 0.248)→(0.592, 0.192, 0.521) | (0.585, 0.193, 0.022)→(0.579, 0.192, 0.026) | 0.187→0.183 | 1.00 / 4.000 | 0.123 | 0.181 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.446
- phase_score: 0.677
- phase_breakdown.approach_pre_grasp_score: 0.816
- phase_breakdown.reach_goal_score: 0.755
- phase_breakdown.reach_grasp_score: 0.720
- phase_breakdown.lift_clearance_score: 0.341
- grasp_place_fitness: 0.687

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.687
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.446
- **Median Q (composite search score)**: -0.292
- **K-run variance**: 0.0025
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.334


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `daf90631fcbaf423e19452d0c9b90b9715013985cc94ef12ca0cd881e96195aa`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.05,0.05],"goal_z_delta":0.15,"object_xy_delta":[0.05,0.05]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `94660347aa4f41f6801e53bd449f8df59691da8bebfa4fef4947a3513fe04781`; realized-scene SHA-256: `584133b5261cffac0dd4282704ff39e97bf4d452e60b02507679bbdea5a4de22`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50382,-0.01567,0.03]},{"name":"goal","value":[0.58691,0.18745,0.24812]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.50382,-0.01567,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.58691,0.18745,0.24812]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":8.0,"average_failure_rate":0.02266,"average_mean_iterations":7.67705,"average_solve_count":353.0,"average_success_count":345.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above.approach_height":0.12341,"approach_above.arc_height":0.06301,"approach_above.speed":0.03165,"descend_to_grasp.descend_offset":0.02063,"descend_to_grasp.speed":0.02703,"descend_to_place.descend_place_offset":0.02395,"descend_to_place.speed":0.0428,"grasp_close.grasp_duration":0.18533,"lift_object.lift_distance":0.22941,"lift_object.speed":0.05627,"release_object.release_duration":0.25868,"retract_from_goal.retract_distance":0.3518,"retract_from_goal.speed":0.16174,"transport_to_goal.transport_speed":0.17214},"optimized_scores":{"best_composite_score":-0.30513,"best_fitness_score":0.57487,"best_task_score":0.22505},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":142.0,"contact_point_centroid":[0.56392,0.18067,-0.00948],"force_p95":1.64105,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.77026,"mean_force":0.54619,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.57889,0.18192,0.27895]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5087.0,"contact_point_centroid":[0.57516,0.18536,0.26165],"force_p95":0.10482,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.56927,"mean_force":0.07798,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.57509,0.16692,0.26519]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4306.0,"contact_point_centroid":[0.57512,0.14804,0.26231],"force_p95":0.11601,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.41827,"mean_force":0.08964,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.575,0.16672,0.26524]},{"body_a":"world","body_b":"grasp_target","contact_count":86.0,"contact_point_centroid":[0.50109,-0.01439,-0.00146],"force_p95":0.35695,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.41372,"mean_force":0.10635,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.48969,-0.01443,0.0477]},{"body_a":"world","body_b":"grasp_target","contact_count":3198.0,"contact_point_centroid":[0.56233,0.18018,-0.00216],"force_p95":0.19955,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.2789,"mean_force":0.1289,"phase_index":7.0,"phase_name":"retract_from_goal","phase_type":"retract","tcp_position_centroid":[0.57888,0.18166,0.42509]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":14369.0,"contact_point_centroid":[0.48811,-0.03346,0.14902],"force_p95":0.08093,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27827,"mean_force":0.05411,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.48746,-0.01438,0.14764]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":13332.0,"contact_point_centroid":[0.48799,0.00476,0.15226],"force_p95":0.08186,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27593,"mean_force":0.05741,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.48746,-0.01438,0.15114]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50385,-0.01558,-0.0021],"force_p95":0.15209,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.21012,"mean_force":0.13047,"phase_index":2.0,"phase_name":"grasp_close","phase_type":"grasp","tcp_position_centroid":[0.492,-0.01445,0.04767]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3117.0,"contact_point_centroid":[0.52535,0.03779,0.26287],"force_p95":0.12021,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20358,"mean_force":0.06788,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.52377,0.05696,0.26235]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3274.0,"contact_point_centroid":[0.52587,0.07829,0.26257],"force_p95":0.09747,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16981,"mean_force":0.05829,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.52501,0.0595,0.26257]},{"body_a":"world","body_b":"grasp_target","contact_count":3156.0,"contact_point_centroid":[0.50382,-0.01567,-0.00195],"force_p95":0.12742,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12278,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.49883,0.03021,0.21946]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":813.0,"contact_point_centroid":[0.58137,0.20154,0.25642],"force_p95":0.10043,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13697,"mean_force":0.06292,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.58144,0.18303,0.26051]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":707.0,"contact_point_centroid":[0.58039,0.16421,0.25707],"force_p95":0.10391,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13309,"mean_force":0.07031,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.58141,0.18302,0.26044]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4337.0,"contact_point_centroid":[0.49143,0.00475,0.04805],"force_p95":0.07538,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12755,"mean_force":0.0495,"phase_index":2.0,"phase_name":"grasp_close","phase_type":"grasp","tcp_position_centroid":[0.49086,-0.01444,0.04644]},{"body_a":"world","body_b":"grasp_target","contact_count":1360.0,"contact_point_centroid":[0.50382,-0.01567,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.49795,-0.01094,0.10237]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4966.0,"contact_point_centroid":[0.49136,-0.0336,0.04798],"force_p95":0.0717,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0735,"mean_force":0.04432,"phase_index":2.0,"phase_name":"grasp_close","phase_type":"grasp","tcp_position_centroid":[0.49087,-0.01444,0.04644]}],"total_contact_groups":16},"final_pose_error":0.08357,"key_states":{"actual_goal_position":[0.58691,0.18745,0.24812],"final_object_position":[0.56101,0.18024,0.02602],"final_tcp_position":[0.58168,0.18256,0.55309],"realised_goal_position":[0.58691,0.18745,0.24812],"realised_object_initial_position":[0.50382,-0.01567,0.03]},"peak_contact_force":1.77026,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":790.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.03],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.30942,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_above","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3156.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_pre_grasp","tcp_end":[0.49982,-0.00756,0.1494],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.12372,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":340.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1360.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_grasp","tcp_end":[0.49878,-0.01452,0.05511],"tcp_start":[0.49982,-0.00756,0.1494],"tcp_to_object_dist_end":0.02955,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":42.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50377,-0.01481,0.02562],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31197,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.14936,"phase_name":"grasp_close","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11103.0,"raw_peak_contact_force":0.21012,"tcp_end":[0.49083,-0.01444,0.04641],"tcp_start":[0.49878,-0.01452,0.05511],"tcp_to_object_dist_end":0.02449,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":38.0,"n_steps":719.0,"n_steps_budget":1000.0,"object_pos_end":[0.49453,-0.0147,0.22991],"object_pos_start":[0.50377,-0.01481,0.02562],"object_to_goal_dist_end":0.223,"object_to_goal_dist_start":0.31197,"object_z_max":0.22965,"peak_contact_force":0.07605,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":27787.0,"raw_peak_contact_force":0.41372,"subtask_id":"lift_clearance","tcp_end":[0.48809,-0.01439,0.25627],"tcp_start":[0.49083,-0.01444,0.04641],"tcp_to_object_dist_end":0.02713,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":29.0,"n_steps":181.0,"n_steps_budget":1000.0,"object_pos_end":[0.5687,0.14279,0.24125],"object_pos_start":[0.49453,-0.0147,0.22991],"object_to_goal_dist_end":0.04872,"object_to_goal_dist_start":0.223,"object_z_max":0.24122,"peak_contact_force":0.12517,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":6391.0,"raw_peak_contact_force":0.20358,"tcp_end":[0.56664,0.14408,0.27211],"tcp_start":[0.48809,-0.01439,0.25627],"tcp_to_object_dist_end":0.03095,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":21.0,"n_steps":420.0,"n_steps_budget":1000.0,"object_pos_end":[0.58295,0.18319,0.22968],"object_pos_start":[0.5687,0.14279,0.24125],"object_to_goal_dist_end":0.01933,"object_to_goal_dist_start":0.04872,"object_z_max":0.24125,"peak_contact_force":0.11697,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":9393.0,"raw_peak_contact_force":0.56927,"subtask_id":"reach_goal","tcp_end":[0.58269,0.18335,0.26399],"tcp_start":[0.56664,0.14408,0.27211],"tcp_to_object_dist_end":0.03431,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.57679,0.18203,0.01395],"object_pos_start":[0.58295,0.18319,0.22968],"object_to_goal_dist_end":0.23445,"object_to_goal_dist_start":0.01933,"object_z_max":0.22968,"peak_contact_force":0.29487,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1662.0,"raw_peak_contact_force":1.77026,"tcp_end":[0.57887,0.18192,0.28481],"tcp_start":[0.58269,0.18335,0.26399],"tcp_to_object_dist_end":0.27087,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":857.0,"n_steps_budget":1000.0,"object_pos_end":[0.56101,0.18024,0.02602],"object_pos_start":[0.57679,0.18203,0.01395],"object_to_goal_dist_end":0.22372,"object_to_goal_dist_start":0.23445,"object_z_max":0.03049,"peak_contact_force":0.12263,"phase_name":"retract_from_goal","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3198.0,"raw_peak_contact_force":0.2789,"tcp_end":[0.58168,0.18256,0.55309],"tcp_start":[0.57887,0.18192,0.28481],"tcp_to_object_dist_end":0.52748,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `fe7e0be33c0bb4db9d2bbbb069b6113d0e5a69a675a0d70bc1f582243e99e3cf`; realized-scene SHA-256: `8a4edc50bf1a337961423afe5cdf858aa28147f944f8fcd30a2ce1adc75d1bd6`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.51251,0.03972,0.03]},{"name":"goal","value":[0.62757,0.17252,0.14502]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.51251,0.03972,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.62757,0.17252,0.14502]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.33144,"average_solve_count":353.0,"average_success_count":353.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above.approach_height":0.11637,"approach_above.arc_height":0.06289,"approach_above.speed":0.05435,"descend_to_grasp.descend_offset":0.02005,"descend_to_grasp.speed":0.02661,"descend_to_place.descend_place_offset":0.02545,"descend_to_place.speed":0.04083,"grasp_close.grasp_duration":0.26381,"lift_object.lift_distance":0.20567,"lift_object.speed":0.02821,"release_object.release_duration":0.15901,"retract_from_goal.retract_distance":0.34759,"retract_from_goal.speed":0.14519,"transport_to_goal.transport_speed":0.16783},"optimized_scores":{"best_composite_score":-0.19329,"best_fitness_score":0.68671,"best_task_score":0.44598},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":270.0,"contact_point_centroid":[0.60584,0.16689,-0.00518],"force_p95":0.85248,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.43223,"mean_force":0.25322,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.61664,0.16842,0.17161]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8877.0,"contact_point_centroid":[0.61081,0.17683,0.16589],"force_p95":0.0954,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.54043,"mean_force":0.07569,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.61146,0.15843,0.16917]},{"body_a":"world","body_b":"grasp_target","contact_count":90.0,"contact_point_centroid":[0.50864,0.03984,-0.00148],"force_p95":0.38555,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.41618,"mean_force":0.16709,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.4982,0.03973,0.0462]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":7483.0,"contact_point_centroid":[0.60945,0.13898,0.16726],"force_p95":0.11576,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.36319,"mean_force":0.08742,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.61079,0.15772,0.16961]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2729.0,"contact_point_centroid":[0.54176,0.06454,0.21267],"force_p95":0.12649,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28142,"mean_force":0.06339,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.54194,0.08375,0.21169]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":12992.0,"contact_point_centroid":[0.49584,0.05869,0.13753],"force_p95":0.0759,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26559,"mean_force":0.05309,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.49577,0.03952,0.13511]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":13266.0,"contact_point_centroid":[0.49565,0.02041,0.13554],"force_p95":0.07729,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23567,"mean_force":0.05254,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.49578,0.03953,0.13378]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.51251,0.03977,-0.00203],"force_p95":0.22367,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.22686,"mean_force":0.16287,"phase_index":2.0,"phase_name":"grasp_close","phase_type":"grasp","tcp_position_centroid":[0.50046,0.03992,0.0467]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2559.0,"contact_point_centroid":[0.54126,0.10182,0.21288],"force_p95":0.11216,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21123,"mean_force":0.06241,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.54101,0.08282,0.21212]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.60574,0.16687,-0.00198],"force_p95":0.12358,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.1415,"mean_force":0.12246,"phase_index":7.0,"phase_name":"retract_from_goal","phase_type":"retract","tcp_position_centroid":[0.61515,0.16778,0.32001]},{"body_a":"world","body_b":"grasp_target","contact_count":3024.0,"contact_point_centroid":[0.51251,0.03972,-0.00195],"force_p95":0.12817,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12279,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.50168,0.05521,0.23802]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":780.0,"contact_point_centroid":[0.61999,0.18806,0.15396],"force_p95":0.09558,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1345,"mean_force":0.06349,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.62075,0.16977,0.15831]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":599.0,"contact_point_centroid":[0.61861,0.15089,0.1548],"force_p95":0.12017,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12481,"mean_force":0.08118,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.6207,0.16975,0.15823]},{"body_a":"world","body_b":"grasp_target","contact_count":1324.0,"contact_point_centroid":[0.51251,0.03972,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.5063,0.04446,0.10101]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4647.0,"contact_point_centroid":[0.49978,0.05908,0.04839],"force_p95":0.07895,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11837,"mean_force":0.05645,"phase_index":2.0,"phase_name":"grasp_close","phase_type":"grasp","tcp_position_centroid":[0.49931,0.03983,0.04542]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5114.0,"contact_point_centroid":[0.50004,0.02068,0.04763],"force_p95":0.07569,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10392,"mean_force":0.05094,"phase_index":2.0,"phase_name":"grasp_close","phase_type":"grasp","tcp_position_centroid":[0.49931,0.03983,0.04542]}],"total_contact_groups":16},"final_pose_error":0.06667,"key_states":{"actual_goal_position":[0.62757,0.17252,0.14502],"final_object_position":[0.60574,0.16687,0.02602],"final_tcp_position":[0.6174,0.16833,0.4626],"realised_goal_position":[0.62757,0.17252,0.14502],"realised_object_initial_position":[0.51251,0.03972,0.03]},"peak_contact_force":1.43223,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":757.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.03],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21001,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_above","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3024.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_pre_grasp","tcp_end":[0.50801,0.04847,0.14757],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.12195,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":331.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1324.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_grasp","tcp_end":[0.50735,0.04054,0.05444],"tcp_start":[0.50801,0.04847,0.14757],"tcp_to_object_dist_end":0.0289,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51242,0.03993,0.02588],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21221,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.22312,"phase_name":"grasp_close","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11561.0,"raw_peak_contact_force":0.22686,"tcp_end":[0.49928,0.03983,0.04538],"tcp_start":[0.50735,0.04054,0.05444],"tcp_to_object_dist_end":0.02352,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":38.0,"n_steps":657.0,"n_steps_budget":1000.0,"object_pos_end":[0.50346,0.03968,0.20767],"object_pos_start":[0.51242,0.03993,0.02588],"object_to_goal_dist_end":0.19228,"object_to_goal_dist_start":0.21221,"object_z_max":0.2074,"peak_contact_force":0.07702,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":26348.0,"raw_peak_contact_force":0.41618,"subtask_id":"lift_clearance","tcp_end":[0.49628,0.03956,0.23131],"tcp_start":[0.49928,0.03983,0.04538],"tcp_to_object_dist_end":0.0247,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":27.0,"n_steps":142.0,"n_steps_budget":1000.0,"object_pos_end":[0.59257,0.1362,0.16141],"object_pos_start":[0.50346,0.03968,0.20767],"object_to_goal_dist_end":0.05303,"object_to_goal_dist_start":0.19228,"object_z_max":0.20799,"peak_contact_force":0.11426,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":5288.0,"raw_peak_contact_force":0.28142,"tcp_end":[0.594,0.13685,0.18913],"tcp_start":[0.49628,0.03956,0.23131],"tcp_to_object_dist_end":0.02776,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":21.0,"n_steps":717.0,"n_steps_budget":1000.0,"object_pos_end":[0.62122,0.16992,0.12952],"object_pos_start":[0.59257,0.1362,0.16141],"object_to_goal_dist_end":0.01695,"object_to_goal_dist_start":0.05303,"object_z_max":0.16141,"peak_contact_force":0.11899,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":16360.0,"raw_peak_contact_force":0.54043,"subtask_id":"reach_goal","tcp_end":[0.62252,0.17027,0.16207],"tcp_start":[0.594,0.13685,0.18913],"tcp_to_object_dist_end":0.03258,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.60659,0.16715,0.02631],"object_pos_start":[0.62122,0.16992,0.12952],"object_to_goal_dist_end":0.12067,"object_to_goal_dist_start":0.01695,"object_z_max":0.12952,"peak_contact_force":0.11438,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1649.0,"raw_peak_contact_force":1.43223,"tcp_end":[0.61658,0.1684,0.18167],"tcp_start":[0.62252,0.17027,0.16207],"tcp_to_object_dist_end":0.15569,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.60574,0.16687,0.02602],"object_pos_start":[0.60659,0.16715,0.02631],"object_to_goal_dist_end":0.12112,"object_to_goal_dist_start":0.12067,"object_z_max":0.02655,"peak_contact_force":0.12263,"phase_name":"retract_from_goal","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.1415,"tcp_end":[0.6174,0.16833,0.4626],"tcp_start":[0.61658,0.1684,0.18167],"tcp_to_object_dist_end":0.43674,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `28f75809d7d1d0a11ca1a36dd459ad950e5a80b6bae34006f33ac9620425f5e5`; realized-scene SHA-256: `f44a4a1356de6cb8b5dec75995af4354e38cafd01c85526c1c2a33c8dd2e5b1c`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.4827,0.04873,0.03]},{"name":"goal","value":[0.58187,0.22885,0.23048]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.4827,0.04873,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.58187,0.22885,0.23048]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":16.0,"average_failure_rate":0.03747,"average_mean_iterations":10.55504,"average_solve_count":427.0,"average_success_count":411.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above.approach_height":0.12712,"approach_above.arc_height":0.0958,"approach_above.speed":0.02967,"descend_to_grasp.descend_offset":0.02234,"descend_to_grasp.speed":0.03334,"descend_to_place.descend_place_offset":0.0352,"descend_to_place.speed":0.02883,"grasp_close.grasp_duration":0.18237,"lift_object.lift_distance":0.20945,"lift_object.speed":0.02234,"release_object.release_duration":0.23225,"retract_from_goal.retract_distance":0.36633,"retract_from_goal.speed":0.09524,"transport_to_goal.transport_speed":0.25092},"optimized_scores":{"best_composite_score":-0.29223,"best_fitness_score":0.58777,"best_task_score":0.25539},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":2506.0,"contact_point_centroid":[0.57135,0.23063,-0.00251],"force_p95":0.21221,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.25565,"mean_force":0.14731,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.5703,0.21323,0.25383]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":172.0,"contact_point_centroid":[0.55681,0.20654,0.24864],"force_p95":0.26466,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.49556,"mean_force":0.09349,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.55714,0.18948,0.25354]},{"body_a":"world","body_b":"grasp_target","contact_count":86.0,"contact_point_centroid":[0.4792,0.04805,-0.00146],"force_p95":0.33989,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.3544,"mean_force":0.15444,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.46937,0.04848,0.04976]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2017.0,"contact_point_centroid":[0.5036,0.08757,0.24287],"force_p95":0.16066,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32796,"mean_force":0.0908,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.50571,0.10671,0.24497]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":13177.0,"contact_point_centroid":[0.467,0.06714,0.14436],"force_p95":0.07804,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25545,"mean_force":0.05243,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.46707,0.04824,0.14374]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":11151.0,"contact_point_centroid":[0.4661,0.02907,0.14392],"force_p95":0.09692,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24203,"mean_force":0.06225,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.46707,0.04824,0.14322]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2483.0,"contact_point_centroid":[0.50481,0.12549,0.2429],"force_p95":0.13181,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22541,"mean_force":0.07158,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.50591,0.10703,0.24501]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":42.0,"contact_point_centroid":[0.55161,0.17038,0.24931],"force_p95":0.18446,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20112,"mean_force":0.08769,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.55713,0.18874,0.25398]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.48269,0.04868,-0.00202],"force_p95":0.13022,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.15239,"mean_force":0.12465,"phase_index":2.0,"phase_name":"grasp_close","phase_type":"grasp","tcp_position_centroid":[0.47148,0.04869,0.05012]},{"body_a":"world","body_b":"grasp_target","contact_count":3036.0,"contact_point_centroid":[0.4827,0.04873,-0.00195],"force_p95":0.12792,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12279,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.49139,0.05585,0.24811]},{"body_a":"world","body_b":"grasp_target","contact_count":1456.0,"contact_point_centroid":[0.4827,0.04873,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.47767,0.05347,0.10846]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.57125,0.22987,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.57524,0.22452,0.25791]},{"body_a":"world","body_b":"grasp_target","contact_count":3924.0,"contact_point_centroid":[0.57125,0.22987,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":7.0,"phase_name":"retract_from_goal","phase_type":"retract","tcp_position_centroid":[0.57396,0.22356,0.40893]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5310.0,"contact_point_centroid":[0.46996,0.0677,0.05022],"force_p95":0.06398,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08905,"mean_force":0.04115,"phase_index":2.0,"phase_name":"grasp_close","phase_type":"grasp","tcp_position_centroid":[0.47039,0.04859,0.04897]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4374.0,"contact_point_centroid":[0.47038,0.02933,0.05006],"force_p95":0.07303,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0882,"mean_force":0.04954,"phase_index":2.0,"phase_name":"grasp_close","phase_type":"grasp","tcp_position_centroid":[0.47039,0.04859,0.04897]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2531.0,"contact_point_centroid":[0.57134,0.21415,0.25638],"force_p95":0.01155,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0165,"mean_force":0.01053,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.57084,0.21411,0.25402]}],"total_contact_groups":17},"final_pose_error":0.09575,"key_states":{"actual_goal_position":[0.58187,0.22885,0.23048],"final_object_position":[0.57125,0.22987,0.02602],"final_tcp_position":[0.57742,0.22492,0.5482],"realised_goal_position":[0.58187,0.22885,0.23048],"realised_object_initial_position":[0.4827,0.04873,0.03]},"peak_contact_force":167951.73011,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":760.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.03],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28719,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_above","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3036.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_pre_grasp","tcp_end":[0.47995,0.05771,0.16006],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.13437,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":364.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":25.18866,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1456.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_grasp","tcp_end":[0.47804,0.04938,0.05704],"tcp_start":[0.47995,0.05771,0.16006],"tcp_to_object_dist_end":0.03137,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.48262,0.04852,0.0259],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.29022,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.13009,"phase_name":"grasp_close","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11484.0,"raw_peak_contact_force":0.15239,"tcp_end":[0.47036,0.04858,0.04894],"tcp_start":[0.47804,0.04938,0.05704],"tcp_to_object_dist_end":0.0261,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":38.0,"n_steps":646.0,"n_steps_budget":1000.0,"object_pos_end":[0.47254,0.04871,0.21113],"object_pos_start":[0.48262,0.04852,0.0259],"object_to_goal_dist_end":0.21161,"object_to_goal_dist_start":0.29022,"object_z_max":0.21085,"peak_contact_force":167951.73011,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":24414.0,"raw_peak_contact_force":0.3544,"subtask_id":"lift_clearance","tcp_end":[0.46751,0.04828,0.23885],"tcp_start":[0.47036,0.04858,0.04894],"tcp_to_object_dist_end":0.02818,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":18.0,"n_steps":165.0,"n_steps_budget":1000.0,"object_pos_end":[0.55522,0.18735,0.21908],"object_pos_start":[0.47254,0.04871,0.21113],"object_to_goal_dist_end":0.05063,"object_to_goal_dist_start":0.21161,"object_z_max":0.21908,"peak_contact_force":9760.30694,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4500.0,"raw_peak_contact_force":0.32796,"tcp_end":[0.55659,0.1873,0.25427],"tcp_start":[0.46751,0.04828,0.23885],"tcp_to_object_dist_end":0.03522,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":746.0,"n_steps_budget":1000.0,"object_pos_end":[0.57125,0.22987,0.02602],"object_pos_start":[0.55522,0.18735,0.21908],"object_to_goal_dist_end":0.20474,"object_to_goal_dist_start":0.05063,"object_z_max":0.21908,"peak_contact_force":0.12263,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":5251.0,"raw_peak_contact_force":2.25565,"subtask_id":"reach_goal","tcp_end":[0.57804,0.2258,0.25697],"tcp_start":[0.55659,0.1873,0.25427],"tcp_to_object_dist_end":0.23108,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.57125,0.22987,0.02602],"object_pos_start":[0.57125,0.22987,0.02602],"object_to_goal_dist_end":0.20474,"object_to_goal_dist_start":0.20474,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1024.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.57426,0.22399,0.27756],"tcp_start":[0.57804,0.2258,0.25697],"tcp_to_object_dist_end":0.25162,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":981.0,"n_steps_budget":1000.0,"object_pos_end":[0.57125,0.22987,0.02602],"object_pos_start":[0.57125,0.22987,0.02602],"object_to_goal_dist_end":0.20474,"object_to_goal_dist_start":0.20474,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"retract_from_goal","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3924.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.57742,0.22492,0.5482],"tcp_start":[0.57426,0.22399,0.27756],"tcp_to_object_dist_end":0.52224,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
```