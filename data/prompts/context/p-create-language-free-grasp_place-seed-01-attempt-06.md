## Search State

- **Seed**: 1
- **Iteration**: 7 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 6 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 13 | -0.3398 | 0.19 | ❌ rejected |
| 5 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 11 | -0.0696 | 0.36 | ✅ accepted |
| 4 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 12 | -0.1850 | 0.23 | ❌ rejected |
| 3 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 13 | -0.2445 | 0.21 | ❌ rejected |
| 2 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 11 | -0.0743 | 0.35 | ✅ accepted |

**Proposal policy**: task_score is 0.19 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `a2ed2c4162d37489f2d2d0fa0373774d72c951d58f2469e0ba2d602ff46b6cfb`
- Frozen object start: [0.5011821624700257, 0.045046369632593536, 0.03]
- Frozen task target: [0.5644159612719634, 0.2448649447137244, 0.1467747178015728]
- Goal object position: (0.5644159612719634, 0.2448649447137244, 0.1467747178015728)
- place_goal_position (task success criterion — final object 3D position must be close to the realised airborne target here): (0.5644159612719634, 0.2448649447137244, 0.1467747178015728)
- Grasp/lift components are optimiser fitness diagnostics only; canonical task_score is final object-to-realised-target proximity.
- Object initial pose: (0.5011821624700257, 0.045046369632593536, 0.03)
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
  frozen_object_start: [0.5012, 0.045, 0.03]
  frozen_task_target: [0.5644, 0.2449, 0.1468]
  frozen_object_starts: {'grasp_target': [0.5011821624700257, 0.045046369632593536, 0.03]}
  frozen_targets: {'place_target': [0.5644159612719634, 0.2448649447137244, 0.1467747178015728]}
  goal_tolerance_m: 0.02
  force_limit_n: 20
  force_scale_n: 5
  realized_scene_sha256: a2ed2c4162d37489f2d2d0fa0373774d72c951d58f2469e0ba2d602ff46b6cfb

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
| `object` | offset from object initial position (0.5011821624700257, 0.045046369632593536, 0.03) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.5644159612719634, 0.2448649447137244, 0.1467747178015728) | final destination targets |
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

## Current Skill (Q=-0.340) — your mutation base

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
  - 0.05
  weight: 0.3
- id: reach_goal
  weight: 0.7
phases:
- id: approach_1
  type: approach
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
    - 0.05
    orientation:
      mode: keep_current
  parameters:
    approach_speed:
      type: scalar
      range:
      - 0.1
      - 0.5
      default: 0.3
      binds_to:
      - path: generator.speed
        mode: replace
    approach_z:
      type: scalar
      range:
      - 0.03
      - 0.15
      default: 0.05
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: reach_object
- id: descend_1
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
    - 0.0
    orientation:
      mode: keep_current
  parameters:
    descend_speed:
      type: scalar
      range:
      - 0.05
      - 0.3
      default: 0.15
      binds_to:
      - path: generator.speed
        mode: replace
- id: grasp_1
  type: grasp
  control: position_control
  termination: force_exceeded
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
    grasp_force_threshold:
      type: scalar
      range:
      - 0.1
      - 5.0
      default: 0.5
      binds_to:
      - path: termination.force_threshold
        mode: replace
- id: lift_1
  type: lift
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
    - 0.15
    orientation:
      mode: keep_current
  parameters:
    lift_speed:
      type: scalar
      range:
      - 0.05
      - 0.3
      default: 0.15
      binds_to:
      - path: generator.speed
        mode: replace
    lift_z:
      type: scalar
      range:
      - 0.08
      - 0.25
      default: 0.15
      binds_to:
      - path: target.offset.z
        mode: replace
- id: approach_2
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
    - 0.1
    orientation:
      mode: keep_current
  parameters:
    approach2_z:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.1
      binds_to:
      - path: target.offset.z
        mode: replace
    transport_speed:
      type: scalar
      range:
      - 0.1
      - 0.5
      default: 0.25
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: reach_goal
- id: descend_2
  type: descend
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.0
    orientation:
      mode: keep_current
  parameters:
    place_speed:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.1
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: reach_goal
- id: release_1
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
      - 1.0
      default: 0.3
      binds_to:
      - path: duration.max_time
        mode: replace
- id: retract_1
  type: retract
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.15
    orientation:
      mode: keep_current
  parameters:
    retract_speed:
      type: scalar
      range:
      - 0.1
      - 0.5
      default: 0.2
      binds_to:
      - path: generator.speed
        mode: replace

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.05]
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (replace)
    - approach_z: status=consumed; consumers=target.offset.z (replace)
- **descend_1** (`descend`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings:
    - descend_speed: status=consumed; consumers=generator.speed (replace)
- **grasp_1** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings:
    - grasp_force_threshold: status=consumed; consumers=termination.force_threshold (replace)
- **lift_1** (`lift`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.15]
  - orientation: mode=keep_current
  - parameter_bindings:
    - lift_speed: status=consumed; consumers=generator.speed (replace)
    - lift_z: status=consumed; consumers=target.offset.z (replace)
- **approach_2** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.1]
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach2_z: status=consumed; consumers=target.offset.z (replace)
    - transport_speed: status=consumed; consumers=generator.speed (replace)
- **descend_2** (`descend`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings:
    - place_speed: status=consumed; consumers=generator.speed (replace)
- **release_1** (`release`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings:
    - release_duration: status=consumed; consumers=duration.max_time (replace)
- **retract_1** (`retract`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.15]
  - orientation: mode=keep_current
  - parameter_bindings:
    - retract_speed: status=consumed; consumers=generator.speed (replace)

## Design Metrics

- **Composite score**: -0.340
- **task_score** (E): 0.187
- **fitness_score**: 0.490  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.830

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1758 |
| descend_1 | 1.00 | 1.00 | 0.0952 |
| grasp_1 | 1.00 | 1.00 | 0.0111 |
| lift_1 | 0.67 | 1.00 | 0.1560 |
| approach_2 | 0.00 | 1.00 | 0.2212 |
| descend_2 | 1.00 | 1.00 | 0.1383 |
| release_1 | 1.00 | 1.00 | 0.0205 |
| retract_1 | 1.00 | 1.00 | 0.0759 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.476, -0.001, 0.130) | (0.479, -0.000, 0.030)→(0.479, -0.000, 0.026) | 0.276→0.278 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.476, -0.001, 0.130)→(0.474, -0.000, 0.035) | (0.479, -0.000, 0.026)→(0.479, -0.000, 0.026) | 0.278→0.278 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_1 | grasp | 1.00 / step_budget | (0.474, -0.000, 0.035)→(0.466, -0.001, 0.027) | (0.479, -0.000, 0.026)→(0.479, -0.001, 0.026) | 0.278→0.278 | 1.00 / 44.333 | 0.143 | 0.210 |
| lift_1 | lift | 0.67 / step_budget | (0.466, -0.001, 0.027)→(0.473, -0.001, 0.183) | (0.479, -0.001, 0.026)→(0.495, 0.005, 0.094) | 0.278→0.240 | 1.00 / 25.000 | 0.104 | 1.057 |
| approach_2 | approach | 0.00 / step_budget | (0.473, -0.001, 0.183)→(0.571, 0.139, 0.303) | (0.495, 0.005, 0.094)→(0.490, 0.024, 0.016) | 0.240→0.258 | 1.00 / 8.333 | 0.123 | 1.336 |
| descend_2 | descend | 1.00 / step_budget | (0.571, 0.139, 0.303)→(0.602, 0.198, 0.190) | (0.490, 0.024, 0.016)→(0.490, 0.024, 0.016) | 0.258→0.258 | 1.00 / 8.333 | 91003.219 | 0.123 |
| release_1 | release | 1.00 / step_budget | (0.602, 0.198, 0.190)→(0.597, 0.196, 0.210) | (0.490, 0.024, 0.016)→(0.490, 0.024, 0.016) | 0.258→0.258 | 1.00 / 4.000 | 0.123 | 0.123 |
| retract_1 | retract | 1.00 / step_budget | (0.597, 0.196, 0.210)→(0.606, 0.203, 0.285) | (0.490, 0.024, 0.016)→(0.490, 0.024, 0.016) | 0.258→0.258 | 1.00 / 4.000 | 0.123 | 0.123 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.264
- phase_score: 0.333
- phase_breakdown.reach_object_score: 0.214
- phase_breakdown.reach_goal_score: 0.383
- grasp_place_fitness: 0.611

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.611
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.264
- **Median Q (composite search score)**: -0.281
- **K-run variance**: 0.0168
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.322


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `8110053be9072e64e15984c6424e4a66fe19af4b6c37a60139a43e94cc34ad53`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.05,0.05],"goal_z_delta":0.15,"object_xy_delta":[0.05,0.05]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `46ef03f7b16015a0d14bf26d80c05d326b92c02b0bf759391930f5ab902d1933`; realized-scene SHA-256: `a2ed2c4162d37489f2d2d0fa0373774d72c951d58f2469e0ba2d602ff46b6cfb`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50118,0.04505,0.03]},{"name":"goal","value":[0.56442,0.24486,0.14677]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.50118,0.04505,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.56442,0.24486,0.14677]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.88,"average_solve_count":150.0,"average_success_count":150.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.43386,"approach_1.approach_z":0.11885,"approach_2.approach2_z":0.05952,"approach_2.arc_height":0.12573,"approach_2.transport_speed":0.16179,"descend_1.descend_speed":0.13293,"descend_2.descend_z":0.0518,"descend_2.place_speed":0.08952,"grasp_1.grasp_force_threshold":1.5193,"lift_1.lift_speed":0.05834,"lift_1.lift_z":0.20069,"release_1.release_duration":0.90571,"retract_1.retract_speed":0.38662},"optimized_scores":{"best_composite_score":-0.21868,"best_fitness_score":0.61132,"best_task_score":0.26419},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":1244.0,"contact_point_centroid":[0.50007,0.10851,-0.00295],"force_p95":0.46517,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.19117,"mean_force":0.1629,"phase_index":4.0,"phase_name":"approach_2","phase_type":"approach","tcp_position_centroid":[0.51101,0.10615,0.25453]},{"body_a":"world","body_b":"grasp_target","contact_count":195.0,"contact_point_centroid":[0.49715,0.04218,-0.00124],"force_p95":0.45153,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.66042,"mean_force":0.09681,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48648,0.04325,0.02783]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":19745.0,"contact_point_centroid":[0.48768,0.06215,0.07574],"force_p95":0.07657,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31213,"mean_force":0.05191,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48727,0.04304,0.07398]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":19373.0,"contact_point_centroid":[0.48784,0.02392,0.0781],"force_p95":0.07776,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29679,"mean_force":0.05205,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48739,0.04304,0.07601]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":7702.0,"contact_point_centroid":[0.49052,0.02493,0.16545],"force_p95":0.14016,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28986,"mean_force":0.07362,"phase_index":4.0,"phase_name":"approach_2","phase_type":"approach","tcp_position_centroid":[0.48759,0.04364,0.16533]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":7756.0,"contact_point_centroid":[0.49109,0.06353,0.16833],"force_p95":0.14939,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28232,"mean_force":0.07684,"phase_index":4.0,"phase_name":"approach_2","phase_type":"approach","tcp_position_centroid":[0.48806,0.04478,0.16829]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50124,0.04468,-0.00215],"force_p95":0.16609,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.25052,"mean_force":0.13429,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.48926,0.04353,0.02725]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4046.0,"contact_point_centroid":[0.48864,0.02422,0.02885],"force_p95":0.08179,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14942,"mean_force":0.05192,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.4881,0.04342,0.02603]},{"body_a":"world","body_b":"grasp_target","contact_count":1660.0,"contact_point_centroid":[0.50118,0.04505,-0.00192],"force_p95":0.13462,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12292,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49779,0.01987,0.22835]},{"body_a":"world","body_b":"grasp_target","contact_count":1492.0,"contact_point_centroid":[0.50118,0.04505,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49548,0.04233,0.09526]},{"body_a":"world","body_b":"grasp_target","contact_count":2744.0,"contact_point_centroid":[0.49987,0.10847,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.54005,0.18841,0.2243]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.49987,0.10847,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.55522,0.23648,0.19514]},{"body_a":"world","body_b":"grasp_target","contact_count":2052.0,"contact_point_centroid":[0.49987,0.10847,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":7.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.55641,0.23893,0.24699]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5021.0,"contact_point_centroid":[0.48863,0.06261,0.02786],"force_p95":0.07434,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08788,"mean_force":0.04481,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.4881,0.04343,0.02604]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1165.0,"contact_point_centroid":[0.51264,0.10915,0.25824],"force_p95":0.01214,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01648,"mean_force":0.01069,"phase_index":4.0,"phase_name":"approach_2","phase_type":"approach","tcp_position_centroid":[0.51212,0.10914,0.25608]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2932.0,"contact_point_centroid":[0.5405,0.18837,0.2266],"force_p95":0.01097,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01276,"mean_force":0.01043,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.54002,0.18834,0.22434]}],"total_contact_groups":17},"final_pose_error":0.01421,"key_states":{"actual_goal_position":[0.56442,0.24486,0.14677],"final_object_position":[0.49987,0.10847,0.01602],"final_tcp_position":[0.56134,0.24303,0.28302],"realised_goal_position":[0.56442,0.24486,0.14677],"realised_object_initial_position":[0.50118,0.04505,0.03]},"peak_contact_force":273009.41079,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":416.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.03],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.23992,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1660.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.49736,0.04074,0.15679],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.1309,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":373.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1492.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.49621,0.04417,0.03464],"tcp_start":[0.49736,0.04074,0.15679],"tcp_to_object_dist_end":0.00999,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50107,0.04342,0.02551],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.24351,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"peak_contact_force":0.15644,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10867.0,"raw_peak_contact_force":0.25052,"tcp_end":[0.48807,0.04342,0.026],"tcp_start":[0.49621,0.04417,0.03464],"tcp_to_object_dist_end":0.01301,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5005,0.04306,0.11229],"object_pos_start":[0.50107,0.04342,0.02551],"object_to_goal_dist_end":0.21448,"object_to_goal_dist_start":0.24351,"object_z_max":0.11219,"peak_contact_force":0.0697,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":39313.0,"raw_peak_contact_force":0.66042,"tcp_end":[0.49047,0.04305,0.122],"tcp_start":[0.48807,0.04342,0.026],"tcp_to_object_dist_end":0.01396,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49987,0.10847,0.01602],"object_pos_start":[0.5005,0.04306,0.11229],"object_to_goal_dist_end":0.19966,"object_to_goal_dist_start":0.21448,"object_z_max":0.20311,"peak_contact_force":0.12262,"phase_name":"approach_2","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":17867.0,"raw_peak_contact_force":2.19117,"subtask_id":"reach_goal","tcp_end":[0.52133,0.13375,0.26328],"tcp_start":[0.49047,0.04305,0.122],"tcp_to_object_dist_end":0.24948,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":686.0,"n_steps_budget":1000.0,"object_pos_end":[0.49987,0.10847,0.01602],"object_pos_start":[0.49987,0.10847,0.01602],"object_to_goal_dist_end":0.19966,"object_to_goal_dist_start":0.19966,"object_z_max":0.01602,"peak_contact_force":273009.41079,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":5676.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_goal","tcp_end":[0.5589,0.238,0.19389],"tcp_start":[0.52133,0.13375,0.26328],"tcp_to_object_dist_end":0.22782,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.49987,0.10847,0.01602],"object_pos_start":[0.49987,0.10847,0.01602],"object_to_goal_dist_end":0.19966,"object_to_goal_dist_start":0.19966,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1028.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.55388,0.23579,0.21502],"tcp_start":[0.5589,0.238,0.19389],"tcp_to_object_dist_end":0.24234,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":513.0,"n_steps_budget":600.0,"object_pos_end":[0.49987,0.10847,0.01602],"object_pos_start":[0.49987,0.10847,0.01602],"object_to_goal_dist_end":0.19966,"object_to_goal_dist_start":0.19966,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2052.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.56134,0.24303,0.28302],"tcp_start":[0.55388,0.23579,0.21502],"tcp_to_object_dist_end":0.30525,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `1efc3ad2e58ea1c47cd56203c4986b53dab7b80d759e458b85d233ccc9cc04bd`; realized-scene SHA-256: `67b45068113fe0ef6f199d4981822d51bd0bd66bb4f388f7402a08094b41852a`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.47616,-0.02015,0.03]},{"name":"goal","value":[0.63142,0.15919,0.19002]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.47616,-0.02015,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.63142,0.15919,0.19002]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.45763,"average_solve_count":118.0,"average_success_count":118.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.29636,"approach_1.approach_z":0.07492,"approach_2.approach2_z":0.12051,"approach_2.arc_height":0.11916,"approach_2.transport_speed":0.33934,"descend_1.descend_speed":0.24774,"descend_2.descend_z":0.03376,"descend_2.place_speed":0.13426,"grasp_1.grasp_force_threshold":3.8983,"lift_1.lift_speed":0.17582,"lift_1.lift_z":0.15396,"release_1.release_duration":0.78371,"retract_1.retract_speed":0.30959},"optimized_scores":{"best_composite_score":-0.28134,"best_fitness_score":0.54866,"best_task_score":0.13692},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":3216.0,"contact_point_centroid":[0.47583,-0.02643,-0.00234],"force_p95":0.12455,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.68419,"mean_force":0.13653,"phase_index":4.0,"phase_name":"approach_2","phase_type":"approach","tcp_position_centroid":[0.5173,0.0333,0.3143]},{"body_a":"world","body_b":"grasp_target","contact_count":110.0,"contact_point_centroid":[0.47406,-0.01945,-0.00112],"force_p95":0.50942,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.69195,"mean_force":0.06514,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46268,-0.0196,0.02877]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1056.0,"contact_point_centroid":[0.47315,-0.00402,0.17335],"force_p95":0.20114,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32539,"mean_force":0.11364,"phase_index":4.0,"phase_name":"approach_2","phase_type":"approach","tcp_position_centroid":[0.4672,-0.02237,0.17538]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1052.0,"contact_point_centroid":[0.47324,-0.04072,0.17296],"force_p95":0.2047,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32496,"mean_force":0.11474,"phase_index":4.0,"phase_name":"approach_2","phase_type":"approach","tcp_position_centroid":[0.46729,-0.02232,0.17511]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":7994.0,"contact_point_centroid":[0.46775,-0.00061,0.08714],"force_p95":0.10924,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31902,"mean_force":0.06957,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46514,-0.01954,0.08491]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8576.0,"contact_point_centroid":[0.46758,-0.03841,0.08474],"force_p95":0.1071,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30015,"mean_force":0.06563,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46499,-0.01954,0.08303]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.47616,-0.02003,-0.00204],"force_p95":0.13657,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.18599,"mean_force":0.12649,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46485,-0.01966,0.02805]},{"body_a":"world","body_b":"grasp_target","contact_count":1932.0,"contact_point_centroid":[0.47616,-0.02015,-0.00193],"force_p95":0.13308,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12288,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48634,-0.0091,0.20714]},{"body_a":"world","body_b":"grasp_target","contact_count":1040.0,"contact_point_centroid":[0.47616,-0.02015,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.47159,-0.01913,0.07436]},{"body_a":"world","body_b":"grasp_target","contact_count":1276.0,"contact_point_centroid":[0.47576,-0.02641,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.61136,0.1391,0.28169]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.47576,-0.02641,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.62104,0.15316,0.22867]},{"body_a":"world","body_b":"grasp_target","contact_count":2052.0,"contact_point_centroid":[0.47576,-0.02641,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":7.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.62324,0.15512,0.28402]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5066.0,"contact_point_centroid":[0.46353,-0.00039,0.02986],"force_p95":0.06635,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0931,"mean_force":0.04291,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46374,-0.01963,0.02696]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5398.0,"contact_point_centroid":[0.46339,-0.03889,0.02935],"force_p95":0.06484,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08805,"mean_force":0.04119,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46374,-0.01963,0.02696]},{"body_a":"left_finger","body_b":"right_finger","contact_count":3161.0,"contact_point_centroid":[0.52209,0.03821,0.32345],"force_p95":0.01103,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01605,"mean_force":0.01056,"phase_index":4.0,"phase_name":"approach_2","phase_type":"approach","tcp_position_centroid":[0.52179,0.03822,0.32122]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1351.0,"contact_point_centroid":[0.61176,0.13911,0.28394],"force_p95":0.011,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01277,"mean_force":0.01052,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.61137,0.1391,0.28167]}],"total_contact_groups":17},"final_pose_error":0.01568,"key_states":{"actual_goal_position":[0.63142,0.15919,0.19002],"final_object_position":[0.47576,-0.02641,0.01602],"final_tcp_position":[0.62883,0.15807,0.3246],"realised_goal_position":[0.63142,0.15919,0.19002],"realised_object_initial_position":[0.47616,-0.02015,0.03]},"peak_contact_force":1.68419,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":484.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.03],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28614,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1932.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.47398,-0.01853,0.1145],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.08852,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":260.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1040.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.47153,-0.0198,0.0347],"tcp_start":[0.47398,-0.01853,0.1145],"tcp_to_object_dist_end":0.00984,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":47.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.47603,-0.01965,0.02583],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28825,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.1346,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12264.0,"raw_peak_contact_force":0.18599,"tcp_end":[0.46371,-0.01963,0.02693],"tcp_start":[0.47153,-0.0198,0.0347],"tcp_to_object_dist_end":0.01237,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":24.0,"n_steps":542.0,"n_steps_budget":600.0,"object_pos_end":[0.49136,-0.01962,0.15236],"object_pos_start":[0.47603,-0.01965,0.02583],"object_to_goal_dist_end":0.23024,"object_to_goal_dist_start":0.28825,"object_z_max":0.15219,"peak_contact_force":0.11028,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":16680.0,"raw_peak_contact_force":0.69195,"tcp_end":[0.4718,-0.01955,0.16472],"tcp_start":[0.46371,-0.01963,0.02693],"tcp_to_object_dist_end":0.02313,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.47576,-0.02641,0.01602],"object_pos_start":[0.49136,-0.01962,0.15236],"object_to_goal_dist_end":0.29825,"object_to_goal_dist_start":0.23024,"object_z_max":0.16968,"peak_contact_force":0.12263,"phase_name":"approach_2","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":8485.0,"raw_peak_contact_force":1.68419,"subtask_id":"reach_goal","tcp_end":[0.60008,0.12536,0.33621],"tcp_start":[0.4718,-0.01955,0.16472],"tcp_to_object_dist_end":0.37552,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":319.0,"n_steps_budget":1000.0,"object_pos_end":[0.47576,-0.02641,0.01602],"object_pos_start":[0.47576,-0.02641,0.01602],"object_to_goal_dist_end":0.29825,"object_to_goal_dist_start":0.29825,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2627.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_goal","tcp_end":[0.62461,0.15411,0.22898],"tcp_start":[0.60008,0.12536,0.33621],"tcp_to_object_dist_end":0.31638,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.47576,-0.02641,0.01602],"object_pos_start":[0.47576,-0.02641,0.01602],"object_to_goal_dist_end":0.29825,"object_to_goal_dist_start":0.29825,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1028.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.61982,0.15273,0.24807],"tcp_start":[0.62461,0.15411,0.22898],"tcp_to_object_dist_end":0.32664,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":513.0,"n_steps_budget":600.0,"object_pos_end":[0.47576,-0.02641,0.01602],"object_pos_start":[0.47576,-0.02641,0.01602],"object_to_goal_dist_end":0.29825,"object_to_goal_dist_start":0.29825,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2052.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.62883,0.15807,0.3246],"tcp_start":[0.61982,0.15273,0.24807],"tcp_to_object_dist_end":0.39075,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `37495cb43897015e78e007c86af160d11c8460c1ce7249e5c03dce38206c0daf`; realized-scene SHA-256: `5ce27bcdb8582e1d517b17df0f9c2ad7b05701113a75707627744a889253e6a7`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.45856,-0.02632,0.03]},{"name":"goal","value":[0.63013,0.20822,0.11412]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.45856,-0.02632,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.63013,0.20822,0.11412]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.544,"average_solve_count":125.0,"average_success_count":125.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.21901,"approach_1.approach_z":0.07884,"approach_2.approach2_z":0.10743,"approach_2.arc_height":0.10625,"approach_2.transport_speed":0.24851,"descend_1.descend_speed":0.21194,"descend_2.descend_z":0.02981,"descend_2.place_speed":0.14211,"grasp_1.grasp_force_threshold":3.48526,"lift_1.lift_speed":0.27004,"lift_1.lift_z":0.25773,"release_1.release_duration":0.87126,"retract_1.retract_speed":0.49819},"optimized_scores":{"best_composite_score":-0.51941,"best_fitness_score":0.31059,"best_task_score":0.15948},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":519.0,"contact_point_centroid":[0.48368,-0.0139,-0.00383],"force_p95":0.92666,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.82011,"mean_force":0.21023,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.45197,-0.02551,0.1851]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5496.0,"contact_point_centroid":[0.44885,-0.00651,0.08538],"force_p95":0.12843,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.35564,"mean_force":0.07338,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44616,-0.02545,0.08313]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5895.0,"contact_point_centroid":[0.44867,-0.04435,0.08282],"force_p95":0.12497,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31003,"mean_force":0.06913,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44605,-0.02545,0.0812]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.45857,-0.02615,-0.00206],"force_p95":0.1409,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.19391,"mean_force":0.12758,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44777,-0.02562,0.02881]},{"body_a":"world","body_b":"grasp_target","contact_count":1912.0,"contact_point_centroid":[0.45856,-0.02632,-0.00193],"force_p95":0.13329,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12288,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.47836,-0.01187,0.20914]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.49326,-0.00968,-0.00199],"force_p95":0.12284,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13237,"mean_force":0.12271,"phase_index":4.0,"phase_name":"approach_2","phase_type":"approach","tcp_position_centroid":[0.51654,0.05834,0.31869]},{"body_a":"world","body_b":"grasp_target","contact_count":1096.0,"contact_point_centroid":[0.45856,-0.02632,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.4549,-0.02495,0.07655]},{"body_a":"world","body_b":"grasp_target","contact_count":1888.0,"contact_point_centroid":[0.49326,-0.00968,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.60661,0.1801,0.22731]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.49326,-0.00968,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.61845,0.20122,0.14797]},{"body_a":"world","body_b":"grasp_target","contact_count":2052.0,"contact_point_centroid":[0.49326,-0.00968,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":7.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.62017,0.20308,0.20535]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4813.0,"contact_point_centroid":[0.44672,-0.00637,0.03019],"force_p95":0.06821,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09829,"mean_force":0.04489,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44669,-0.02558,0.0278]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5175.0,"contact_point_centroid":[0.44657,-0.04482,0.02968],"force_p95":0.06707,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08244,"mean_force":0.04301,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44669,-0.02558,0.0278]},{"body_a":"left_finger","body_b":"right_finger","contact_count":179.0,"contact_point_centroid":[0.4553,-0.02551,0.25504],"force_p95":0.01496,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01629,"mean_force":0.01171,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.45499,-0.02551,0.25273]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2021.0,"contact_point_centroid":[0.60687,0.17999,0.23002],"force_p95":0.01098,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01278,"mean_force":0.01042,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.60652,0.17998,0.22774]},{"body_a":"left_finger","body_b":"right_finger","contact_count":4261.0,"contact_point_centroid":[0.51703,0.0586,0.32106],"force_p95":0.01099,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01271,"mean_force":0.01046,"phase_index":4.0,"phase_name":"approach_2","phase_type":"approach","tcp_position_centroid":[0.51674,0.0586,0.31878]},{"body_a":"left_finger","body_b":"right_finger","contact_count":223.0,"contact_point_centroid":[0.62166,0.20233,0.14691],"force_p95":0.01095,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01271,"mean_force":0.01001,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.62127,0.20232,0.14458]}],"total_contact_groups":16},"final_pose_error":0.01653,"key_states":{"actual_goal_position":[0.63013,0.20822,0.11412],"final_object_position":[0.49326,-0.00968,0.01602],"final_tcp_position":[0.62646,0.20656,0.24809],"realised_goal_position":[0.63013,0.20822,0.11412],"realised_object_initial_position":[0.45856,-0.02632,0.03]},"peak_contact_force":1.82011,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":479.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.03],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30252,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1912.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.45781,-0.02417,0.11849],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.0925,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":274.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1096.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.45428,-0.02585,0.03501],"tcp_start":[0.45781,-0.02417,0.11849],"tcp_to_object_dist_end":0.00997,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":45.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.45844,-0.02563,0.02578],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30325,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.13798,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11788.0,"raw_peak_contact_force":0.19391,"tcp_end":[0.44666,-0.02558,0.02777],"tcp_start":[0.45428,-0.02585,0.03501],"tcp_to_object_dist_end":0.01195,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":571.0,"n_steps_budget":600.0,"object_pos_end":[0.49324,-0.00945,0.01641],"object_pos_start":[0.45844,-0.02563,0.02578],"object_to_goal_dist_end":0.27507,"object_to_goal_dist_start":0.30325,"object_z_max":0.16352,"peak_contact_force":0.1326,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":12089.0,"raw_peak_contact_force":1.82011,"tcp_end":[0.45554,-0.02552,0.26161],"tcp_start":[0.44666,-0.02558,0.02777],"tcp_to_object_dist_end":0.2486,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49326,-0.00968,0.01602],"object_pos_start":[0.49324,-0.00945,0.01641],"object_to_goal_dist_end":0.27538,"object_to_goal_dist_start":0.27507,"object_z_max":0.01641,"peak_contact_force":0.12263,"phase_name":"approach_2","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":8261.0,"raw_peak_contact_force":0.13237,"subtask_id":"reach_goal","tcp_end":[0.59206,0.15853,0.31004],"tcp_start":[0.45554,-0.02552,0.26161],"tcp_to_object_dist_end":0.35285,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":472.0,"n_steps_budget":1000.0,"object_pos_end":[0.49326,-0.00968,0.01602],"object_pos_start":[0.49326,-0.00968,0.01602],"object_to_goal_dist_end":0.27538,"object_to_goal_dist_start":0.27538,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3909.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_goal","tcp_end":[0.62312,0.20277,0.14848],"tcp_start":[0.59206,0.15853,0.31004],"tcp_to_object_dist_end":0.28203,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.49326,-0.00968,0.01602],"object_pos_start":[0.49326,-0.00968,0.01602],"object_to_goal_dist_end":0.27538,"object_to_goal_dist_start":0.27538,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1023.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.61676,0.20055,0.16728],"tcp_start":[0.62312,0.20277,0.14848],"tcp_to_object_dist_end":0.28693,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":513.0,"n_steps_budget":600.0,"object_pos_end":[0.49326,-0.00968,0.01602],"object_pos_start":[0.49326,-0.00968,0.01602],"object_to_goal_dist_end":0.27538,"object_to_goal_dist_start":0.27538,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2052.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.62646,0.20656,0.24809],"tcp_start":[0.61676,0.20055,0.16728],"tcp_to_object_dist_end":0.34403,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```