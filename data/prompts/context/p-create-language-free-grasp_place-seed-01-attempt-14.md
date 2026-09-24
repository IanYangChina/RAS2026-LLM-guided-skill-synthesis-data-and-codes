## Search State

- **Seed**: 1
- **Iteration**: 15 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 14 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | impedance_control | position_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 11 | -0.1379 | 0.22 | ❌ rejected |
| 13 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | impedance_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 11 | -0.2109 | 0.24 | ❌ rejected |
| 12 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 11 | -0.1002 | 0.30 | ❌ rejected |
| 11 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 11 | -0.0685 | 0.36 | ✅ accepted |
| 10 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 11 | -0.1071 | 0.29 | ❌ rejected |

**Proposal policy**: task_score is 0.22 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=-0.138) — your mutation base

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

- **Composite score**: -0.138
- **task_score** (E): 0.224
- **fitness_score**: 0.592  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.730

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1604 |
| descend_1 | 1.00 | 1.00 | 0.1109 |
| grasp_1 | 1.00 | 1.00 | 0.0111 |
| lift_1 | 0.67 | 1.00 | 0.1314 |
| approach_2 | 0.00 | 1.00 | 0.0063 |
| descend_2 | 0.00 | 1.00 | 0.0779 |
| release_1 | 1.00 | 1.00 | 0.0236 |
| retract_1 | 0.67 | 1.00 | 0.2122 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.477, -0.001, 0.146) | (0.479, -0.000, 0.030)→(0.479, -0.000, 0.026) | 0.276→0.278 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.477, -0.001, 0.146)→(0.474, -0.001, 0.035) | (0.479, -0.000, 0.026)→(0.479, -0.000, 0.026) | 0.278→0.278 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_1 | grasp | 1.00 / step_budget | (0.474, -0.001, 0.035)→(0.466, -0.001, 0.027) | (0.479, -0.000, 0.026)→(0.479, -0.001, 0.026) | 0.278→0.278 | 1.00 / 44.333 | 0.143 | 0.206 |
| lift_1 | lift | 0.67 / step_budget | (0.466, -0.001, 0.027)→(0.473, -0.001, 0.158) | (0.479, -0.001, 0.026)→(0.490, -0.001, 0.144) | 0.278→0.242 | 1.00 / 21.333 | 617.879 | 0.675 |
| approach_2 | approach | 0.00 / guard_failure | (0.515, 0.005, 0.070)→(0.521, 0.004, 0.068) | (0.490, -0.001, 0.144)→(0.538, 0.005, 0.056) | 0.242→0.253 | 1.00 / 10.667 | 0.899 | 1.438 |
| descend_2 | descend | 0.00 / step_budget | (0.521, 0.004, 0.068)→(0.548, 0.070, 0.081) | (0.544, 0.004, 0.054)→(0.567, 0.040, 0.016) | 0.250→0.226 | 1.00 / 8.333 | 3249.683 | 750.063 |
| release_1 | release | 1.00 / step_budget | (0.548, 0.070, 0.081)→(0.541, 0.069, 0.103) | (0.567, 0.040, 0.016)→(0.567, 0.040, 0.016) | 0.226→0.226 | 1.00 / 4.000 | 0.123 | 0.123 |
| retract_1 | retract | 0.67 / step_budget | (0.541, 0.069, 0.103)→(0.599, 0.187, 0.264) | (0.567, 0.040, 0.016)→(0.567, 0.040, 0.016) | 0.226→0.226 | 1.00 / 4.000 | 0.123 | 0.123 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.250
- phase_score: 0.080
- phase_breakdown.reach_object_score: 0.180
- phase_breakdown.reach_goal_score: 0.038
- grasp_place_fitness: 0.604

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.604
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.250
- **Median Q (composite search score)**: -0.133
- **K-run variance**: 0.0002
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.236


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":20.0,"average_failure_rate":0.15385,"average_mean_iterations":34.61538,"average_solve_count":130.0,"average_success_count":110.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.1788,"approach_1.approach_z":0.12778,"approach_2.approach2_z":0.16998,"approach_2.transport_speed":0.29312,"descend_1.descend_speed":0.11902,"descend_2.place_speed":0.08266,"grasp_1.grasp_force_threshold":2.32013,"lift_1.lift_speed":0.15314,"lift_1.lift_z":0.16797,"release_1.release_duration":0.88813,"retract_1.retract_speed":0.26817},"optimized_scores":{"best_composite_score":-0.1256,"best_fitness_score":0.6044,"best_task_score":0.25017},"replay_outcomes":[{"contacts":{"omitted_contact_groups":6,"reported_contact_groups":[{"body_a":"world","body_b":"hand","contact_count":44.0,"contact_point_centroid":[0.56983,0.1165,-0.00531],"force_p95":954.71765,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1159.78303,"mean_force":247.34466,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.5234,0.063,-0.02392]},{"body_a":"world","body_b":"right_finger","contact_count":1016.0,"contact_point_centroid":[0.52925,0.08241,-0.01242],"force_p95":8.632,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":41.46052,"mean_force":4.93764,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.52661,0.06367,-0.01074]},{"body_a":"world","body_b":"left_finger","contact_count":1009.0,"contact_point_centroid":[0.5265,0.04464,-0.01246],"force_p95":9.08712,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":40.72788,"mean_force":5.00739,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.52656,0.06366,-0.01087]},{"body_a":"world","body_b":"grasp_target","contact_count":13.0,"contact_point_centroid":[0.56949,0.0586,-0.00781],"force_p95":3.21705,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.22244,"mean_force":2.91861,"phase_index":4.0,"phase_name":"approach_2","phase_type":"approach","tcp_position_centroid":[0.55432,0.0615,0.03498]},{"body_a":"grasp_target","body_b":"hand","contact_count":491.0,"contact_point_centroid":[0.58381,0.0693,0.03962],"force_p95":1.15714,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":3.12928,"mean_force":0.64784,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.53746,0.07353,0.01344]},{"body_a":"world","body_b":"grasp_target","contact_count":2854.0,"contact_point_centroid":[0.57646,0.07843,-0.00429],"force_p95":0.5809,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.92743,"mean_force":0.26906,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.54126,0.091,0.02824]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":622.0,"contact_point_centroid":[0.55276,0.06912,0.13449],"force_p95":0.57694,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.28824,"mean_force":0.27375,"phase_index":4.0,"phase_name":"approach_2","phase_type":"approach","tcp_position_centroid":[0.54818,0.0518,0.13905]},{"body_a":"world","body_b":"grasp_target","contact_count":135.0,"contact_point_centroid":[0.49936,0.04232,-0.00119],"force_p95":0.50337,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.71108,"mean_force":0.07169,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48692,0.04329,0.02808]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":556.0,"contact_point_centroid":[0.5479,0.03229,0.1395],"force_p95":0.53656,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.68547,"mean_force":0.25921,"phase_index":4.0,"phase_name":"approach_2","phase_type":"approach","tcp_position_centroid":[0.54509,0.05091,0.14485]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3612.0,"contact_point_centroid":[0.54795,0.06275,0.01804],"force_p95":0.22194,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.44909,"mean_force":0.13983,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.53903,0.07735,0.01823]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8673.0,"contact_point_centroid":[0.49286,0.02426,0.09149],"force_p95":0.11911,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.34249,"mean_force":0.07437,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48962,0.04308,0.08963]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":9163.0,"contact_point_centroid":[0.49256,0.06192,0.08847],"force_p95":0.11671,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32669,"mean_force":0.07203,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48944,0.04308,0.08694]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50124,0.04468,-0.00215],"force_p95":0.16584,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.25013,"mean_force":0.13422,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.48932,0.04354,0.02724]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4273.0,"contact_point_centroid":[0.55089,0.09157,0.02375],"force_p95":0.14393,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23914,"mean_force":0.07607,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.54129,0.08149,0.02369]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4047.0,"contact_point_centroid":[0.48868,0.02424,0.02884],"force_p95":0.08175,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14944,"mean_force":0.05192,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.48815,0.04344,0.02602]},{"body_a":"world","body_b":"grasp_target","contact_count":1584.0,"contact_point_centroid":[0.50118,0.04505,-0.00191],"force_p95":0.13467,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12293,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49784,0.01972,0.23283]}],"total_contact_groups":22},"final_pose_error":0.02451,"key_states":{"actual_goal_position":[0.56442,0.24486,0.14677],"final_object_position":[0.58684,0.08487,0.01602],"final_tcp_position":[0.5623,0.23679,0.27372],"realised_goal_position":[0.56442,0.24486,0.14677],"realised_object_initial_position":[0.50118,0.04505,0.03]},"peak_contact_force":1159.78303,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":397.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.03],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.23992,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1584.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.49744,0.04053,0.1656],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.1397,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":405.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1620.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.49627,0.04418,0.03463],"tcp_start":[0.49744,0.04053,0.1656],"tcp_to_object_dist_end":0.00995,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50107,0.04343,0.02551],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.2435,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"peak_contact_force":0.15624,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10867.0,"raw_peak_contact_force":0.25013,"tcp_end":[0.48813,0.04343,0.02599],"tcp_start":[0.49627,0.04418,0.03463],"tcp_to_object_dist_end":0.01295,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":15.0,"n_steps":632.0,"n_steps_budget":690.0,"object_pos_end":[0.51468,0.04301,0.16146],"object_pos_start":[0.50107,0.04343,0.02551],"object_to_goal_dist_end":0.20841,"object_to_goal_dist_start":0.2435,"object_z_max":0.16135,"peak_contact_force":0.8069,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":17971.0,"raw_peak_contact_force":0.71108,"tcp_end":[0.49688,0.04311,0.17837],"tcp_start":[0.48813,0.04343,0.02599],"tcp_to_object_dist_end":0.02455,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":74.0,"n_steps_budget":1000.0,"object_pos_end":[0.57262,0.05869,0.00417],"object_pos_start":[0.51468,0.04301,0.16146],"object_to_goal_dist_end":0.23466,"object_to_goal_dist_start":0.20841,"object_z_max":0.16156,"peak_contact_force":2.35466,"phase_name":"approach_2","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1191.0,"raw_peak_contact_force":3.22244,"subtask_id":"reach_goal","tcp_end":[0.54547,0.06232,0.01765],"tcp_start":[0.54547,0.06232,0.01765],"tcp_to_object_dist_end":0.03053,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.58684,0.08487,0.01602],"object_pos_start":[0.57262,0.05869,0.00417],"object_to_goal_dist_end":0.20785,"object_to_goal_dist_start":0.23466,"object_z_max":0.02692,"peak_contact_force":0.12263,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":14325.0,"raw_peak_contact_force":1159.78303,"subtask_id":"reach_goal","tcp_end":[0.54586,0.11515,0.04817],"tcp_start":[0.54547,0.06232,0.01765],"tcp_to_object_dist_end":0.06025,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.58684,0.08487,0.01602],"object_pos_start":[0.58684,0.08487,0.01602],"object_to_goal_dist_end":0.20785,"object_to_goal_dist_start":0.20785,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1026.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.53809,0.11376,0.07],"tcp_start":[0.54586,0.11515,0.04817],"tcp_to_object_dist_end":0.07826,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":601.0,"n_steps_budget":630.0,"object_pos_end":[0.58684,0.08487,0.01602],"object_pos_start":[0.58684,0.08487,0.01602],"object_to_goal_dist_end":0.20785,"object_to_goal_dist_start":0.20785,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2404.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.5623,0.23679,0.27372],"tcp_start":[0.53809,0.11376,0.07],"tcp_to_object_dist_end":0.30016,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":24.0,"average_failure_rate":0.19512,"average_mean_iterations":42.61789,"average_solve_count":123.0,"average_success_count":99.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.30138,"approach_1.approach_z":0.10713,"approach_2.approach2_z":0.11252,"approach_2.transport_speed":0.29164,"descend_1.descend_speed":0.13014,"descend_2.place_speed":0.06586,"grasp_1.grasp_force_threshold":1.77918,"lift_1.lift_speed":0.16933,"lift_1.lift_z":0.14934,"release_1.release_duration":0.45348,"retract_1.retract_speed":0.28302},"optimized_scores":{"best_composite_score":-0.15511,"best_fitness_score":0.57489,"best_task_score":0.18918},"replay_outcomes":[{"contacts":{"omitted_contact_groups":4,"reported_contact_groups":[{"body_a":"world","body_b":"hand","contact_count":45.0,"contact_point_centroid":[0.55947,-0.07461,-0.00434],"force_p95":933.28304,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1089.20558,"mean_force":210.37704,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.51632,-0.01849,-0.02654]},{"body_a":"world","body_b":"left_finger","contact_count":764.0,"contact_point_centroid":[0.51998,-0.03609,-0.01815],"force_p95":23.7979,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":42.85343,"mean_force":5.76463,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.51775,-0.01846,-0.01834]},{"body_a":"world","body_b":"right_finger","contact_count":764.0,"contact_point_centroid":[0.51819,-0.00069,-0.01816],"force_p95":23.24236,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":42.56305,"mean_force":5.82971,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.51775,-0.01846,-0.01834]},{"body_a":"grasp_target","body_b":"hand","contact_count":96.0,"contact_point_centroid":[0.57828,-0.0314,0.03156],"force_p95":2.79846,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":4.67632,"mean_force":0.97006,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.51991,-0.01849,-0.01205]},{"body_a":"world","body_b":"grasp_target","contact_count":3867.0,"contact_point_centroid":[0.59947,-0.01753,-0.0028],"force_p95":0.39641,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.38754,"mean_force":0.16631,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.55221,-0.00162,0.05655]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":643.0,"contact_point_centroid":[0.52149,-0.03974,0.1403],"force_p95":0.44137,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.79466,"mean_force":0.18045,"phase_index":4.0,"phase_name":"approach_2","phase_type":"approach","tcp_position_centroid":[0.51494,-0.02165,0.14106]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":605.0,"contact_point_centroid":[0.51932,-0.00219,0.13849],"force_p95":0.43863,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.72021,"mean_force":0.19632,"phase_index":4.0,"phase_name":"approach_2","phase_type":"approach","tcp_position_centroid":[0.51405,-0.02157,0.14]},{"body_a":"world","body_b":"grasp_target","contact_count":116.0,"contact_point_centroid":[0.47414,-0.01912,-0.0011],"force_p95":0.5063,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.68867,"mean_force":0.05812,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46272,-0.01963,0.02883]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8004.0,"contact_point_centroid":[0.4677,-0.00063,0.08511],"force_p95":0.10953,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31776,"mean_force":0.06936,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46513,-0.01957,0.08289]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8579.0,"contact_point_centroid":[0.4676,-0.03844,0.08305],"force_p95":0.10608,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29741,"mean_force":0.06552,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46501,-0.01957,0.08134]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1.0,"contact_point_centroid":[0.56536,-0.03825,0.05905],"force_p95":0.26057,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26057,"mean_force":0.26057,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.55136,-0.02145,0.05549]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.47615,-0.02002,-0.00204],"force_p95":0.13525,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.17517,"mean_force":0.12614,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46491,-0.01968,0.02806]},{"body_a":"world","body_b":"grasp_target","contact_count":1652.0,"contact_point_centroid":[0.47616,-0.02015,-0.00192],"force_p95":0.13462,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12292,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48674,-0.00887,0.22372]},{"body_a":"world","body_b":"grasp_target","contact_count":1400.0,"contact_point_centroid":[0.47616,-0.02015,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.47186,-0.01898,0.09031]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.60283,-0.01769,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.55878,0.0178,0.07948]},{"body_a":"world","body_b":"grasp_target","contact_count":2044.0,"contact_point_centroid":[0.60283,-0.01769,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":7.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.58065,0.06686,0.17664]}],"total_contact_groups":20},"final_pose_error":0.07939,"key_states":{"actual_goal_position":[0.63142,0.15919,0.19002],"final_object_position":[0.60283,-0.01769,0.01602],"final_tcp_position":[0.61359,0.12421,0.27101],"realised_goal_position":[0.63142,0.15919,0.19002],"realised_object_initial_position":[0.47616,-0.02015,0.03]},"peak_contact_force":1089.20558,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":414.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.03],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28614,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1652.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.47463,-0.01823,0.14677],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.12077,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":350.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1400.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.47159,-0.01983,0.03469],"tcp_start":[0.47463,-0.01823,0.14677],"tcp_to_object_dist_end":0.00981,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":47.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.47603,-0.01967,0.02584],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28826,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.13348,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12264.0,"raw_peak_contact_force":0.17517,"tcp_end":[0.46377,-0.01965,0.02693],"tcp_start":[0.47159,-0.01983,0.03469],"tcp_to_object_dist_end":0.01231,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":22.0,"n_steps":542.0,"n_steps_budget":600.0,"object_pos_end":[0.4912,-0.01963,0.14814],"object_pos_start":[0.47603,-0.01967,0.02584],"object_to_goal_dist_end":0.23107,"object_to_goal_dist_start":0.28826,"object_z_max":0.14797,"peak_contact_force":0.11979,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":16699.0,"raw_peak_contact_force":0.68867,"tcp_end":[0.47175,-0.01957,0.16044],"tcp_start":[0.46377,-0.01965,0.02693],"tcp_to_object_dist_end":0.02301,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":62.0,"n_steps_budget":1000.0,"object_pos_end":[0.57766,-0.01834,0.0422],"object_pos_start":[0.4912,-0.01963,0.14814],"object_to_goal_dist_end":0.23719,"object_to_goal_dist_start":0.23107,"object_z_max":0.14837,"peak_contact_force":0.34215,"phase_name":"approach_2","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1248.0,"raw_peak_contact_force":0.79466,"subtask_id":"reach_goal","tcp_end":[0.55136,-0.02145,0.05549],"tcp_start":[0.55136,-0.02145,0.05549],"tcp_to_object_dist_end":0.02963,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.60283,-0.01769,0.01602],"object_pos_start":[0.57766,-0.01834,0.0422],"object_to_goal_dist_end":0.24976,"object_to_goal_dist_start":0.23719,"object_z_max":0.0422,"peak_contact_force":0.12263,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":8990.0,"raw_peak_contact_force":1089.20558,"subtask_id":"reach_goal","tcp_end":[0.56404,0.01811,0.07766],"tcp_start":[0.55136,-0.02145,0.05549],"tcp_to_object_dist_end":0.08115,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.60283,-0.01769,0.01602],"object_pos_start":[0.60283,-0.01769,0.01602],"object_to_goal_dist_end":0.24976,"object_to_goal_dist_start":0.24976,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1026.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.55666,0.01762,0.09951],"tcp_start":[0.56404,0.01811,0.07766],"tcp_to_object_dist_end":0.10173,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":511.0,"n_steps_budget":660.0,"object_pos_end":[0.60283,-0.01769,0.01602],"object_pos_start":[0.60283,-0.01769,0.01602],"object_to_goal_dist_end":0.24976,"object_to_goal_dist_start":0.24976,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2044.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.61359,0.12421,0.27101],"tcp_start":[0.55666,0.01762,0.09951],"tcp_to_object_dist_end":0.29202,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.18321,"average_solve_count":131.0,"average_success_count":131.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.44611,"approach_1.approach_z":0.08493,"approach_2.approach2_z":0.17466,"approach_2.transport_speed":0.26439,"descend_1.descend_speed":0.18673,"descend_2.place_speed":0.09595,"grasp_1.grasp_force_threshold":2.88134,"lift_1.lift_speed":0.06374,"lift_1.lift_z":0.20229,"release_1.release_duration":0.55787,"retract_1.retract_speed":0.2883},"optimized_scores":{"best_composite_score":-0.13304,"best_fitness_score":0.59696,"best_task_score":0.2322},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":1796.0,"contact_point_centroid":[0.5125,0.05158,-0.00239],"force_p95":0.20863,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.20103,"mean_force":0.14058,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.52023,0.05407,0.11835]},{"body_a":"world","body_b":"grasp_target","contact_count":152.0,"contact_point_centroid":[0.45614,-0.02534,-0.00115],"force_p95":0.47389,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.62523,"mean_force":0.08645,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44542,-0.02554,0.02957]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5406.0,"contact_point_centroid":[0.48499,0.01476,0.11729],"force_p95":0.14884,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.4487,"mean_force":0.09193,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.48181,-0.00352,0.11994]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5168.0,"contact_point_centroid":[0.48427,-0.02452,0.11769],"force_p95":0.16205,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.42447,"mean_force":0.09207,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.48016,-0.00631,0.1195]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":261.0,"contact_point_centroid":[0.45886,-0.00789,0.13446],"force_p95":0.20441,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29738,"mean_force":0.11977,"phase_index":4.0,"phase_name":"approach_2","phase_type":"approach","tcp_position_centroid":[0.4549,-0.02672,0.13408]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":255.0,"contact_point_centroid":[0.4592,-0.04518,0.13514],"force_p95":0.21168,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2828,"mean_force":0.11096,"phase_index":4.0,"phase_name":"approach_2","phase_type":"approach","tcp_position_centroid":[0.45489,-0.02671,0.13408]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":17788.0,"contact_point_centroid":[0.44736,-0.04442,0.07977],"force_p95":0.08984,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28175,"mean_force":0.0579,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44587,-0.02544,0.07812]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":17001.0,"contact_point_centroid":[0.4474,-0.00643,0.08075],"force_p95":0.09166,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28107,"mean_force":0.05992,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44591,-0.02544,0.07882]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.45857,-0.02615,-0.00206],"force_p95":0.14076,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.19367,"mean_force":0.12753,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44778,-0.02563,0.02885]},{"body_a":"world","body_b":"grasp_target","contact_count":1856.0,"contact_point_centroid":[0.45856,-0.02632,-0.00193],"force_p95":0.13354,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12289,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.47841,-0.01185,0.21201]},{"body_a":"world","body_b":"grasp_target","contact_count":1164.0,"contact_point_centroid":[0.45856,-0.02632,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.45496,-0.02492,0.07953]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.51248,0.05167,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.53051,0.07517,0.11957]},{"body_a":"world","body_b":"grasp_target","contact_count":2192.0,"contact_point_centroid":[0.51248,0.05167,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":7.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.57222,0.13482,0.18997]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4815.0,"contact_point_centroid":[0.44673,-0.00638,0.03022],"force_p95":0.06819,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09817,"mean_force":0.04487,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.4467,-0.02559,0.02783]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5174.0,"contact_point_centroid":[0.44658,-0.04483,0.02971],"force_p95":0.06705,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08234,"mean_force":0.04301,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.4467,-0.02559,0.02783]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1582.0,"contact_point_centroid":[0.52357,0.05813,0.12024],"force_p95":0.01188,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01635,"mean_force":0.01057,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.52298,0.05807,0.11802]}],"total_contact_groups":17},"final_pose_error":0.02162,"key_states":{"actual_goal_position":[0.63013,0.20822,0.11412],"final_object_position":[0.51248,0.05167,0.01602],"final_tcp_position":[0.62113,0.1985,0.24703],"realised_goal_position":[0.63013,0.20822,0.11412],"realised_object_initial_position":[0.45856,-0.02632,0.03]},"peak_contact_force":9748.80287,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":465.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.03],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30252,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1856.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.45798,-0.02411,0.12458],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.09859,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":291.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1164.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.45429,-0.02586,0.03504],"tcp_start":[0.45798,-0.02411,0.12458],"tcp_to_object_dist_end":0.01,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":45.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.45844,-0.02563,0.02579],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30326,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.13788,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11789.0,"raw_peak_contact_force":0.19367,"tcp_end":[0.44667,-0.02559,0.0278],"tcp_start":[0.45429,-0.02586,0.03504],"tcp_to_object_dist_end":0.01195,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":27.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.46475,-0.02537,0.12287],"object_pos_start":[0.45844,-0.02563,0.02579],"object_to_goal_dist_end":0.28633,"object_to_goal_dist_start":0.30326,"object_z_max":0.12278,"peak_contact_force":1852.70963,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":34941.0,"raw_peak_contact_force":0.62523,"tcp_end":[0.44933,-0.02545,0.13566],"tcp_start":[0.44667,-0.02559,0.0278],"tcp_to_object_dist_end":0.02004,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":29.0,"n_steps":18.0,"n_steps_budget":1000.0,"object_pos_end":[0.46504,-0.02538,0.12287],"object_pos_start":[0.46475,-0.02537,0.12287],"object_to_goal_dist_end":0.28618,"object_to_goal_dist_start":0.28633,"object_z_max":0.12289,"peak_contact_force":0.0,"phase_name":"approach_2","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":516.0,"raw_peak_contact_force":0.29738,"subtask_id":"reach_goal","tcp_end":[0.46716,-0.02894,0.12986],"tcp_start":[0.44965,-0.02547,0.13572],"tcp_to_object_dist_end":0.00813,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51248,0.05167,0.01602],"object_pos_start":[0.48102,-0.02804,0.11556],"object_to_goal_dist_end":0.21903,"object_to_goal_dist_start":0.27938,"object_z_max":0.11556,"peak_contact_force":9748.80287,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":13952.0,"raw_peak_contact_force":1.20103,"subtask_id":"reach_goal","tcp_end":[0.53513,0.07578,0.11653],"tcp_start":[0.46716,-0.02894,0.12986],"tcp_to_object_dist_end":0.10581,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51248,0.05167,0.01602],"object_pos_start":[0.51248,0.05167,0.01602],"object_to_goal_dist_end":0.21903,"object_to_goal_dist_start":0.21903,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1020.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.52869,0.07487,0.14022],"tcp_start":[0.53513,0.07578,0.11653],"tcp_to_object_dist_end":0.12739,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":548.0,"n_steps_budget":600.0,"object_pos_end":[0.51248,0.05167,0.01602],"object_pos_start":[0.51248,0.05167,0.01602],"object_to_goal_dist_end":0.21903,"object_to_goal_dist_start":0.21903,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2192.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.62113,0.1985,0.24703],"tcp_start":[0.52869,0.07487,0.14022],"tcp_to_object_dist_end":0.2945,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```