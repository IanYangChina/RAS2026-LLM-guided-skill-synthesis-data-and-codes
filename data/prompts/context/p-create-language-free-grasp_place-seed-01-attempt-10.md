## Search State

- **Seed**: 1
- **Iteration**: 11 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 10 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 11 | -0.1071 | 0.29 | ❌ rejected |
| 9 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 12 | -0.2164 | 0.17 | ❌ rejected |
| 8 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 11 | -0.1019 | 0.30 | ❌ rejected |
| 7 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 11 | -0.0906 | 0.32 | ❌ rejected |
| 6 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 13 | -0.3398 | 0.19 | ❌ rejected |

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

## Current Skill (Q=-0.107) — your mutation base

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

- **Composite score**: -0.107
- **task_score** (E): 0.285
- **fitness_score**: 0.623  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.730

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1659 |
| descend_1 | 1.00 | 1.00 | 0.1053 |
| grasp_1 | 1.00 | 1.00 | 0.0111 |
| lift_1 | 1.00 | 1.00 | 0.0950 |
| approach_2 | 0.33 | 1.00 | 0.2204 |
| descend_2 | 1.00 | 1.00 | 0.0786 |
| release_1 | 1.00 | 1.00 | 0.0209 |
| retract_1 | 1.00 | 1.00 | 0.1139 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.477, -0.000, 0.140) | (0.479, -0.000, 0.030)→(0.479, -0.000, 0.026) | 0.276→0.278 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.477, -0.000, 0.140)→(0.474, -0.001, 0.035) | (0.479, -0.000, 0.026)→(0.479, -0.000, 0.026) | 0.278→0.278 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_1 | grasp | 1.00 / step_budget | (0.474, -0.001, 0.035)→(0.466, -0.001, 0.027) | (0.479, -0.000, 0.026)→(0.479, -0.001, 0.026) | 0.278→0.278 | 1.00 / 44.333 | 0.143 | 0.209 |
| lift_1 | lift | 1.00 / step_budget | (0.466, -0.001, 0.027)→(0.474, -0.001, 0.122) | (0.479, -0.001, 0.026)→(0.491, -0.001, 0.112) | 0.278→0.245 | 1.00 / 23.667 | 0.111 | 0.656 |
| approach_2 | approach | 0.33 / step_budget | (0.474, -0.001, 0.122)→(0.579, 0.161, 0.215) | (0.491, -0.001, 0.112)→(0.527, 0.100, 0.016) | 0.245→0.191 | 1.00 / 8.667 | 91000.500 | 1.534 |
| descend_2 | descend | 1.00 / step_budget | (0.579, 0.161, 0.215)→(0.601, 0.198, 0.149) | (0.527, 0.100, 0.016)→(0.527, 0.100, 0.016) | 0.191→0.191 | 1.00 / 8.333 | 3249.613 | 0.123 |
| release_1 | release | 1.00 / step_budget | (0.601, 0.198, 0.149)→(0.595, 0.196, 0.169) | (0.527, 0.100, 0.016)→(0.527, 0.100, 0.016) | 0.191→0.191 | 1.00 / 4.000 | 0.123 | 0.123 |
| retract_1 | retract | 1.00 / step_budget | (0.595, 0.196, 0.169)→(0.606, 0.203, 0.283) | (0.527, 0.100, 0.016)→(0.527, 0.100, 0.016) | 0.191→0.191 | 1.00 / 4.000 | 0.123 | 0.123 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.319
- phase_score: 0.642
- phase_breakdown.reach_object_score: 0.226
- phase_breakdown.reach_goal_score: 0.820
- grasp_place_fitness: 0.641

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.641
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.322
- **Median Q (composite search score)**: -0.090
- **K-run variance**: 0.0006
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.290


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.15966,"average_solve_count":119.0,"average_success_count":119.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.32989,"approach_1.approach_z":0.08078,"approach_2.approach2_z":0.0989,"approach_2.transport_speed":0.21689,"descend_1.descend_speed":0.21723,"descend_2.place_speed":0.10348,"grasp_1.grasp_force_threshold":0.64061,"lift_1.lift_speed":0.16156,"lift_1.lift_z":0.10767,"release_1.release_duration":0.36823,"retract_1.retract_speed":0.29171},"optimized_scores":{"best_composite_score":-0.08997,"best_fitness_score":0.64003,"best_task_score":0.32193},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":2155.0,"contact_point_centroid":[0.51998,0.14542,-0.00238],"force_p95":0.17112,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.46104,"mean_force":0.146,"phase_index":4.0,"phase_name":"approach_2","phase_type":"approach","tcp_position_centroid":[0.53008,0.15275,0.18257]},{"body_a":"world","body_b":"grasp_target","contact_count":164.0,"contact_point_centroid":[0.49867,0.04244,-0.00133],"force_p95":0.45696,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.65403,"mean_force":0.08953,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48671,0.0432,0.02752]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8462.0,"contact_point_centroid":[0.49177,0.06188,0.06609],"force_p95":0.10585,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30744,"mean_force":0.06553,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48924,0.04299,0.06431]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":7994.0,"contact_point_centroid":[0.49209,0.0241,0.06864],"force_p95":0.10633,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29903,"mean_force":0.06804,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48947,0.04299,0.06656]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3452.0,"contact_point_centroid":[0.50723,0.05223,0.13204],"force_p95":0.17225,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29111,"mean_force":0.10294,"phase_index":4.0,"phase_name":"approach_2","phase_type":"approach","tcp_position_centroid":[0.50226,0.07055,0.13298]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3914.0,"contact_point_centroid":[0.5075,0.09062,0.13256],"force_p95":0.1599,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27971,"mean_force":0.0994,"phase_index":4.0,"phase_name":"approach_2","phase_type":"approach","tcp_position_centroid":[0.50283,0.07246,0.13404]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50125,0.04467,-0.00216],"force_p95":0.1689,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.25756,"mean_force":0.13489,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.48915,0.04347,0.02708]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3974.0,"contact_point_centroid":[0.48871,0.02416,0.02864],"force_p95":0.08302,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15112,"mean_force":0.05281,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.48798,0.04336,0.02586]},{"body_a":"world","body_b":"grasp_target","contact_count":1984.0,"contact_point_centroid":[0.50118,0.04505,-0.00193],"force_p95":0.133,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12287,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49763,0.02041,0.20902]},{"body_a":"world","body_b":"grasp_target","contact_count":1080.0,"contact_point_centroid":[0.50118,0.04505,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49535,0.04266,0.07642]},{"body_a":"world","body_b":"grasp_target","contact_count":1256.0,"contact_point_centroid":[0.52007,0.14567,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.55012,0.2148,0.17381]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.52007,0.14567,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.55383,0.23547,0.14716]},{"body_a":"world","body_b":"grasp_target","contact_count":2168.0,"contact_point_centroid":[0.52007,0.14567,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":7.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.55511,0.23808,0.21926]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5030.0,"contact_point_centroid":[0.48854,0.06254,0.02767],"force_p95":0.07469,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08813,"mean_force":0.04474,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.48799,0.04336,0.02587]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2062.0,"contact_point_centroid":[0.53191,0.15686,0.18742],"force_p95":0.01169,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01614,"mean_force":0.01061,"phase_index":4.0,"phase_name":"approach_2","phase_type":"approach","tcp_position_centroid":[0.53149,0.15684,0.18508]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1332.0,"contact_point_centroid":[0.55061,0.21483,0.17608],"force_p95":0.011,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01271,"mean_force":0.0105,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.55012,0.2148,0.17381]}],"total_contact_groups":17},"final_pose_error":0.0175,"key_states":{"actual_goal_position":[0.56442,0.24486,0.14677],"final_object_position":[0.52007,0.14567,0.01602],"final_tcp_position":[0.56132,0.243,0.27965],"realised_goal_position":[0.56442,0.24486,0.14677],"realised_object_initial_position":[0.50118,0.04505,0.03]},"peak_contact_force":1.46104,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":497.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.03],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.23992,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1984.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.49706,0.04143,0.1191],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.09324,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":270.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1080.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.4961,0.0441,0.03446],"tcp_start":[0.49706,0.04143,0.1191],"tcp_to_object_dist_end":0.0099,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50107,0.04337,0.02548],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.24357,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"peak_contact_force":0.15829,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10804.0,"raw_peak_contact_force":0.25756,"tcp_end":[0.48796,0.04336,0.02583],"tcp_start":[0.4961,0.0441,0.03446],"tcp_to_object_dist_end":0.01312,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":25.0,"n_steps":534.0,"n_steps_budget":600.0,"object_pos_end":[0.51409,0.04312,0.1107],"object_pos_start":[0.50107,0.04337,0.02548],"object_to_goal_dist_end":0.21104,"object_to_goal_dist_start":0.24357,"object_z_max":0.11058,"peak_contact_force":0.10298,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":16620.0,"raw_peak_contact_force":0.65403,"tcp_end":[0.49608,0.043,0.12021],"tcp_start":[0.48796,0.04336,0.02583],"tcp_to_object_dist_end":0.02036,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.52007,0.14567,0.01602],"object_pos_start":[0.51409,0.04312,0.1107],"object_to_goal_dist_end":0.17001,"object_to_goal_dist_start":0.21104,"object_z_max":0.12694,"peak_contact_force":0.12263,"phase_name":"approach_2","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":11583.0,"raw_peak_contact_force":1.46104,"subtask_id":"reach_goal","tcp_end":[0.54387,0.19251,0.20684],"tcp_start":[0.49608,0.043,0.12021],"tcp_to_object_dist_end":0.19792,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":314.0,"n_steps_budget":1000.0,"object_pos_end":[0.52007,0.14567,0.01602],"object_pos_start":[0.52007,0.14567,0.01602],"object_to_goal_dist_end":0.17001,"object_to_goal_dist_start":0.17001,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2588.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_goal","tcp_end":[0.55816,0.23719,0.14592],"tcp_start":[0.54387,0.19251,0.20684],"tcp_to_object_dist_end":0.16341,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.52007,0.14567,0.01602],"object_pos_start":[0.52007,0.14567,0.01602],"object_to_goal_dist_end":0.17001,"object_to_goal_dist_start":0.17001,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1020.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.55222,0.2347,0.16709],"tcp_start":[0.55816,0.23719,0.14592],"tcp_to_object_dist_end":0.17828,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":542.0,"n_steps_budget":600.0,"object_pos_end":[0.52007,0.14567,0.01602],"object_pos_start":[0.52007,0.14567,0.01602],"object_to_goal_dist_end":0.17001,"object_to_goal_dist_start":0.17001,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2168.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.56132,0.243,0.27965],"tcp_start":[0.55222,0.2347,0.16709],"tcp_to_object_dist_end":0.28404,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.08594,"average_solve_count":128.0,"average_success_count":128.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.46994,"approach_1.approach_z":0.10688,"approach_2.approach2_z":0.11786,"approach_2.transport_speed":0.28382,"descend_1.descend_speed":0.17049,"descend_2.place_speed":0.06537,"grasp_1.grasp_force_threshold":0.89915,"lift_1.lift_speed":0.18138,"lift_1.lift_z":0.10845,"release_1.release_duration":0.89101,"retract_1.retract_speed":0.31832},"optimized_scores":{"best_composite_score":-0.14207,"best_fitness_score":0.58793,"best_task_score":0.21531},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":2243.0,"contact_point_centroid":[0.52492,0.05231,-0.00238],"force_p95":0.16107,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.6714,"mean_force":0.14239,"phase_index":4.0,"phase_name":"approach_2","phase_type":"approach","tcp_position_centroid":[0.55529,0.07733,0.21639]},{"body_a":"world","body_b":"grasp_target","contact_count":139.0,"contact_point_centroid":[0.47382,-0.01939,-0.00123],"force_p95":0.47944,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.64996,"mean_force":0.09003,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46267,-0.01962,0.02862]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3374.0,"contact_point_centroid":[0.49217,-0.01742,0.13905],"force_p95":0.17593,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33622,"mean_force":0.10176,"phase_index":4.0,"phase_name":"approach_2","phase_type":"approach","tcp_position_centroid":[0.48671,0.00102,0.13912]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3730.0,"contact_point_centroid":[0.49437,0.02198,0.1411],"force_p95":0.1551,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29506,"mean_force":0.09628,"phase_index":4.0,"phase_name":"approach_2","phase_type":"approach","tcp_position_centroid":[0.48903,0.00374,0.14173]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8228.0,"contact_point_centroid":[0.46713,-0.00059,0.06951],"force_p95":0.10515,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29483,"mean_force":0.06581,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46502,-0.01956,0.06732]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8871.0,"contact_point_centroid":[0.46709,-0.03845,0.06811],"force_p95":0.10257,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28356,"mean_force":0.06191,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46492,-0.01956,0.06649]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.47615,-0.02003,-0.00204],"force_p95":0.13562,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.17536,"mean_force":0.12624,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46492,-0.01968,0.02825]},{"body_a":"world","body_b":"grasp_target","contact_count":1656.0,"contact_point_centroid":[0.47616,-0.02015,-0.00192],"force_p95":0.13462,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12292,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48674,-0.00887,0.22361]},{"body_a":"world","body_b":"grasp_target","contact_count":1396.0,"contact_point_centroid":[0.47616,-0.02015,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.47186,-0.01898,0.09032]},{"body_a":"world","body_b":"grasp_target","contact_count":1468.0,"contact_point_centroid":[0.5248,0.05233,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.60579,0.13435,0.21804]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.5248,0.05233,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.61938,0.15261,0.188]},{"body_a":"world","body_b":"grasp_target","contact_count":2168.0,"contact_point_centroid":[0.5248,0.05233,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":7.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.62177,0.15465,0.26022]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5067.0,"contact_point_centroid":[0.46357,-0.00041,0.03],"force_p95":0.06611,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09211,"mean_force":0.04291,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.4638,-0.01965,0.02715]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5397.0,"contact_point_centroid":[0.46344,-0.03891,0.02949],"force_p95":0.06466,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08752,"mean_force":0.04119,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.4638,-0.01965,0.02716]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2130.0,"contact_point_centroid":[0.55935,0.08147,0.22279],"force_p95":0.01148,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01598,"mean_force":0.0106,"phase_index":4.0,"phase_name":"approach_2","phase_type":"approach","tcp_position_centroid":[0.55906,0.08147,0.22062]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1576.0,"contact_point_centroid":[0.60602,0.13418,0.22065],"force_p95":0.01103,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01292,"mean_force":0.01039,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.60563,0.13417,0.21831]}],"total_contact_groups":17},"final_pose_error":0.01801,"key_states":{"actual_goal_position":[0.63142,0.15919,0.19002],"final_object_position":[0.5248,0.05233,0.01602],"final_tcp_position":[0.62887,0.1581,0.32222],"realised_goal_position":[0.63142,0.15919,0.19002],"realised_object_initial_position":[0.47616,-0.02015,0.03]},"peak_contact_force":273001.25331,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":415.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.03],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28614,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1656.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.47463,-0.01823,0.14654],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.12054,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":349.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1396.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.4716,-0.01983,0.0349],"tcp_start":[0.47463,-0.01823,0.14654],"tcp_to_object_dist_end":0.00999,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":47.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.47603,-0.01967,0.02584],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28826,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.1338,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12264.0,"raw_peak_contact_force":0.17536,"tcp_end":[0.46377,-0.01965,0.02713],"tcp_start":[0.4716,-0.01983,0.0349],"tcp_to_object_dist_end":0.01233,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":531.0,"n_steps_budget":600.0,"object_pos_end":[0.4889,-0.01945,0.11189],"object_pos_start":[0.47603,-0.01967,0.02584],"object_to_goal_dist_end":0.24151,"object_to_goal_dist_start":0.28826,"object_z_max":0.11177,"peak_contact_force":0.11424,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":17238.0,"raw_peak_contact_force":0.64996,"tcp_end":[0.47124,-0.01956,0.12185],"tcp_start":[0.46377,-0.01965,0.02713],"tcp_to_object_dist_end":0.02028,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5248,0.05233,0.01602],"object_pos_start":[0.4889,-0.01945,0.11189],"object_to_goal_dist_end":0.23035,"object_to_goal_dist_start":0.24151,"object_z_max":0.14251,"peak_contact_force":273001.25331,"phase_name":"approach_2","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":11477.0,"raw_peak_contact_force":1.6714,"subtask_id":"reach_goal","tcp_end":[0.58931,0.11466,0.25449],"tcp_start":[0.47124,-0.01956,0.12185],"tcp_to_object_dist_end":0.25479,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":367.0,"n_steps_budget":1000.0,"object_pos_end":[0.5248,0.05233,0.01602],"object_pos_start":[0.5248,0.05233,0.01602],"object_to_goal_dist_end":0.23035,"object_to_goal_dist_start":0.23035,"object_z_max":0.01602,"peak_contact_force":9748.59328,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3044.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_goal","tcp_end":[0.62344,0.15362,0.1879],"tcp_start":[0.58931,0.11466,0.25449],"tcp_to_object_dist_end":0.22256,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.5248,0.05233,0.01602],"object_pos_start":[0.5248,0.05233,0.01602],"object_to_goal_dist_end":0.23035,"object_to_goal_dist_start":0.23035,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1025.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.61788,0.15214,0.2074],"tcp_start":[0.62344,0.15362,0.1879],"tcp_to_object_dist_end":0.23506,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":542.0,"n_steps_budget":600.0,"object_pos_end":[0.5248,0.05233,0.01602],"object_pos_start":[0.5248,0.05233,0.01602],"object_to_goal_dist_end":0.23035,"object_to_goal_dist_start":0.23035,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2168.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.62887,0.1581,0.32222],"tcp_start":[0.61788,0.15214,0.2074],"tcp_to_object_dist_end":0.34026,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.28926,"average_solve_count":121.0,"average_success_count":121.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.2424,"approach_1.approach_z":0.1148,"approach_2.approach2_z":0.08687,"approach_2.transport_speed":0.36316,"descend_1.descend_speed":0.20453,"descend_2.place_speed":0.07936,"grasp_1.grasp_force_threshold":3.5366,"lift_1.lift_speed":0.13462,"lift_1.lift_z":0.10891,"release_1.release_duration":0.20025,"retract_1.retract_speed":0.20321},"optimized_scores":{"best_composite_score":-0.08938,"best_fitness_score":0.64062,"best_task_score":0.3192},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":2027.0,"contact_point_centroid":[0.53725,0.10253,-0.00239],"force_p95":0.19087,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.47102,"mean_force":0.14629,"phase_index":4.0,"phase_name":"approach_2","phase_type":"approach","tcp_position_centroid":[0.56535,0.12635,0.16669]},{"body_a":"world","body_b":"grasp_target","contact_count":132.0,"contact_point_centroid":[0.45603,-0.02528,-0.00124],"force_p95":0.48635,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.66346,"mean_force":0.0892,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44568,-0.02558,0.02912]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4504.0,"contact_point_centroid":[0.48513,0.03133,0.13108],"force_p95":0.16174,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.3303,"mean_force":0.09098,"phase_index":4.0,"phase_name":"approach_2","phase_type":"approach","tcp_position_centroid":[0.47985,0.01309,0.13128]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3738.0,"contact_point_centroid":[0.48268,-0.00889,0.13069],"force_p95":0.17614,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32852,"mean_force":0.10345,"phase_index":4.0,"phase_name":"approach_2","phase_type":"approach","tcp_position_centroid":[0.47734,0.00962,0.13029]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8303.0,"contact_point_centroid":[0.44986,-0.0065,0.07044],"force_p95":0.10422,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30241,"mean_force":0.06497,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44789,-0.02549,0.06819]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8948.0,"contact_point_centroid":[0.44976,-0.04442,0.06895],"force_p95":0.10238,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29112,"mean_force":0.06121,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44779,-0.02549,0.0673]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.45857,-0.02616,-0.00206],"force_p95":0.13998,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.19263,"mean_force":0.12737,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44785,-0.02567,0.02865]},{"body_a":"world","body_b":"grasp_target","contact_count":1608.0,"contact_point_centroid":[0.45856,-0.02632,-0.00191],"force_p95":0.13462,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12293,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.47913,-0.01153,0.22759]},{"body_a":"world","body_b":"grasp_target","contact_count":1500.0,"contact_point_centroid":[0.45856,-0.02632,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.45535,-0.02475,0.09412]},{"body_a":"world","body_b":"grasp_target","contact_count":1068.0,"contact_point_centroid":[0.53735,0.10282,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.61194,0.18947,0.14634]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.53735,0.10282,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.61703,0.20079,0.11432]},{"body_a":"world","body_b":"grasp_target","contact_count":2168.0,"contact_point_centroid":[0.53735,0.10282,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":7.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.61881,0.20262,0.18506]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4816.0,"contact_point_centroid":[0.44678,-0.00641,0.02998],"force_p95":0.06808,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09772,"mean_force":0.04488,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44676,-0.02563,0.02763]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5172.0,"contact_point_centroid":[0.44663,-0.04486,0.02948],"force_p95":0.06689,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08248,"mean_force":0.043,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44677,-0.02563,0.02763]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1893.0,"contact_point_centroid":[0.57034,0.13252,0.17082],"force_p95":0.01148,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01557,"mean_force":0.01068,"phase_index":4.0,"phase_name":"approach_2","phase_type":"approach","tcp_position_centroid":[0.57004,0.13252,0.16864]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1134.0,"contact_point_centroid":[0.61234,0.18952,0.14851],"force_p95":0.011,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01103,"mean_force":0.01049,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.61197,0.18951,0.14623]}],"total_contact_groups":17},"final_pose_error":0.01885,"key_states":{"actual_goal_position":[0.63013,0.20822,0.11412],"final_object_position":[0.53735,0.10282,0.01602],"final_tcp_position":[0.6264,0.20657,0.24571],"realised_goal_position":[0.63013,0.20822,0.11412],"realised_object_initial_position":[0.45856,-0.02632,0.03]},"peak_contact_force":1.47102,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":403.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.03],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30252,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1608.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.45886,-0.02375,0.15431],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.12832,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":375.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1500.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.45431,-0.02589,0.03481],"tcp_start":[0.45886,-0.02375,0.15431],"tcp_to_object_dist_end":0.00978,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":45.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.45844,-0.02566,0.02579],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30328,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.13724,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11788.0,"raw_peak_contact_force":0.19263,"tcp_end":[0.44674,-0.02562,0.0276],"tcp_start":[0.45431,-0.02589,0.03481],"tcp_to_object_dist_end":0.01185,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":529.0,"n_steps_budget":600.0,"object_pos_end":[0.47127,-0.02545,0.11217],"object_pos_start":[0.45844,-0.02566,0.02579],"object_to_goal_dist_end":0.28256,"object_to_goal_dist_start":0.30328,"object_z_max":0.11205,"peak_contact_force":0.11434,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":17383.0,"raw_peak_contact_force":0.66346,"tcp_end":[0.45379,-0.0255,0.1226],"tcp_start":[0.44674,-0.02562,0.0276],"tcp_to_object_dist_end":0.02036,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53735,0.10282,0.01602],"object_pos_start":[0.47127,-0.02545,0.11217],"object_to_goal_dist_end":0.17129,"object_to_goal_dist_start":0.28256,"object_z_max":0.12149,"peak_contact_force":0.12263,"phase_name":"approach_2","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":12162.0,"raw_peak_contact_force":1.47102,"subtask_id":"reach_goal","tcp_end":[0.60396,0.17725,0.18251],"tcp_start":[0.45379,-0.0255,0.1226],"tcp_to_object_dist_end":0.19416,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":267.0,"n_steps_budget":1000.0,"object_pos_end":[0.53735,0.10282,0.01602],"object_pos_start":[0.53735,0.10282,0.01602],"object_to_goal_dist_end":0.17129,"object_to_goal_dist_start":0.17129,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2202.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_goal","tcp_end":[0.62209,0.20242,0.11461],"tcp_start":[0.60396,0.17725,0.18251],"tcp_to_object_dist_end":0.16377,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53735,0.10282,0.01602],"object_pos_start":[0.53735,0.10282,0.01602],"object_to_goal_dist_end":0.17129,"object_to_goal_dist_start":0.17129,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1029.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.61511,0.20007,0.13362],"tcp_start":[0.62209,0.20242,0.11461],"tcp_to_object_dist_end":0.17127,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":542.0,"n_steps_budget":600.0,"object_pos_end":[0.53735,0.10282,0.01602],"object_pos_start":[0.53735,0.10282,0.01602],"object_to_goal_dist_end":0.17129,"object_to_goal_dist_start":0.17129,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2168.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.6264,0.20657,0.24571],"tcp_start":[0.61511,0.20007,0.13362],"tcp_to_object_dist_end":0.26731,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```