## Search State

- **Seed**: 1
- **Iteration**: 12 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 11 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 11 | -0.0685 | 0.36 | ✅ accepted |
| 10 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 11 | -0.1071 | 0.29 | ❌ rejected |
| 9 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 12 | -0.2164 | 0.17 | ❌ rejected |
| 8 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 11 | -0.1019 | 0.30 | ❌ rejected |
| 7 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 11 | -0.0906 | 0.32 | ❌ rejected |

**Proposal policy**: task_score is 0.36 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=-0.068) — your mutation base

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

- **Composite score**: -0.068
- **task_score** (E): 0.363
- **fitness_score**: 0.662  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.730

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1494 |
| descend_1 | 1.00 | 1.00 | 0.1223 |
| grasp_1 | 1.00 | 1.00 | 0.0112 |
| lift_1 | 0.67 | 1.00 | 0.0972 |
| approach_2 | 0.67 | 1.00 | 0.2363 |
| descend_2 | 1.00 | 1.00 | 0.0819 |
| release_1 | 1.00 | 1.00 | 0.0209 |
| retract_1 | 1.00 | 1.00 | 0.1127 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.477, 0.000, 0.157) | (0.479, -0.000, 0.030)→(0.479, -0.000, 0.026) | 0.276→0.278 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.477, 0.000, 0.157)→(0.474, -0.001, 0.035) | (0.479, -0.000, 0.026)→(0.479, -0.000, 0.026) | 0.278→0.278 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_1 | grasp | 1.00 / step_budget | (0.474, -0.001, 0.035)→(0.466, -0.001, 0.027) | (0.479, -0.000, 0.026)→(0.479, -0.001, 0.026) | 0.278→0.278 | 1.00 / 44.333 | 0.143 | 0.206 |
| lift_1 | lift | 0.67 / step_budget | (0.466, -0.001, 0.027)→(0.472, -0.001, 0.124) | (0.479, -0.001, 0.026)→(0.487, -0.001, 0.114) | 0.278→0.245 | 1.00 / 30.333 | 0.096 | 0.672 |
| approach_2 | approach | 0.67 / step_budget | (0.472, -0.001, 0.124)→(0.582, 0.170, 0.223) | (0.487, -0.001, 0.114)→(0.556, 0.139, 0.016) | 0.245→0.161 | 1.00 / 8.333 | 91002.462 | 1.700 |
| descend_2 | descend | 1.00 / step_budget | (0.582, 0.170, 0.223)→(0.602, 0.199, 0.151) | (0.556, 0.139, 0.016)→(0.556, 0.139, 0.016) | 0.161→0.162 | 1.00 / 8.333 | 3249.665 | 0.125 |
| release_1 | release | 1.00 / step_budget | (0.602, 0.199, 0.151)→(0.596, 0.197, 0.170) | (0.556, 0.139, 0.016)→(0.556, 0.139, 0.016) | 0.162→0.162 | 1.00 / 4.000 | 0.123 | 0.123 |
| retract_1 | retract | 1.00 / step_budget | (0.596, 0.197, 0.170)→(0.606, 0.203, 0.283) | (0.556, 0.139, 0.016)→(0.556, 0.139, 0.016) | 0.162→0.162 | 1.00 / 4.000 | 0.123 | 0.123 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.487
- phase_score: 0.612
- phase_breakdown.reach_object_score: 0.129
- phase_breakdown.reach_goal_score: 0.819
- grasp_place_fitness: 0.725

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.725
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.487
- **Median Q (composite search score)**: -0.053
- **K-run variance**: 0.0035
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.380


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.86861,"average_solve_count":137.0,"average_success_count":137.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.26563,"approach_1.approach_z":0.08779,"approach_2.approach2_z":0.11709,"approach_2.transport_speed":0.34759,"descend_1.descend_speed":0.24224,"descend_2.place_speed":0.11537,"grasp_1.grasp_force_threshold":0.10033,"lift_1.lift_speed":0.05785,"lift_1.lift_z":0.18825,"release_1.release_duration":0.97879,"retract_1.retract_speed":0.29239},"optimized_scores":{"best_composite_score":-0.05254,"best_fitness_score":0.67746,"best_task_score":0.39673},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":580.0,"contact_point_centroid":[0.54607,0.2037,-0.00375],"force_p95":0.93104,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.9152,"mean_force":0.22895,"phase_index":4.0,"phase_name":"approach_2","phase_type":"approach","tcp_position_centroid":[0.54781,0.20624,0.22992]},{"body_a":"world","body_b":"grasp_target","contact_count":197.0,"contact_point_centroid":[0.4972,0.04216,-0.00125],"force_p95":0.45061,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.65919,"mean_force":0.09686,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.4864,0.0432,0.02768]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":11915.0,"contact_point_centroid":[0.51209,0.12169,0.15804],"force_p95":0.09943,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.37028,"mean_force":0.06273,"phase_index":4.0,"phase_name":"approach_2","phase_type":"approach","tcp_position_centroid":[0.50961,0.10313,0.15806]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":19646.0,"contact_point_centroid":[0.48783,0.0621,0.07478],"force_p95":0.07719,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31136,"mean_force":0.05216,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48736,0.04299,0.07302]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":19314.0,"contact_point_centroid":[0.48799,0.02388,0.07722],"force_p95":0.07814,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29497,"mean_force":0.0522,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.4875,0.04299,0.07513]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50124,0.04467,-0.00215],"force_p95":0.16721,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.25154,"mean_force":0.13457,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.48917,0.04349,0.02711]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":9046.0,"contact_point_centroid":[0.51042,0.07902,0.15494],"force_p95":0.14404,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23758,"mean_force":0.07838,"phase_index":4.0,"phase_name":"approach_2","phase_type":"approach","tcp_position_centroid":[0.50772,0.09798,0.15448]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4045.0,"contact_point_centroid":[0.48859,0.02418,0.0287],"force_p95":0.08196,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1483,"mean_force":0.05192,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.488,0.04338,0.02589]},{"body_a":"world","body_b":"grasp_target","contact_count":1924.0,"contact_point_centroid":[0.50118,0.04505,-0.00193],"force_p95":0.13308,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12288,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49763,0.02035,0.21248]},{"body_a":"world","body_b":"grasp_target","contact_count":1048.0,"contact_point_centroid":[0.5438,0.20353,-0.00199],"force_p95":0.12282,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12348,"mean_force":0.12261,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.55496,0.22845,0.19558]},{"body_a":"world","body_b":"grasp_target","contact_count":1152.0,"contact_point_centroid":[0.50118,0.04505,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49536,0.04263,0.07975]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.5438,0.20353,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.55466,0.23749,0.15376]},{"body_a":"world","body_b":"grasp_target","contact_count":2168.0,"contact_point_centroid":[0.5438,0.20353,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":7.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.55561,0.23919,0.22284]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5026.0,"contact_point_centroid":[0.48856,0.06258,0.0277],"force_p95":0.07448,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08728,"mean_force":0.04482,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.48801,0.04338,0.0259]},{"body_a":"left_finger","body_b":"right_finger","contact_count":485.0,"contact_point_centroid":[0.5495,0.20958,0.23435],"force_p95":0.01364,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0164,"mean_force":0.01087,"phase_index":4.0,"phase_name":"approach_2","phase_type":"approach","tcp_position_centroid":[0.54906,0.20956,0.23223]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1123.0,"contact_point_centroid":[0.55534,0.22853,0.19759],"force_p95":0.011,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01271,"mean_force":0.01041,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.55498,0.2285,0.19533]}],"total_contact_groups":17},"final_pose_error":0.01702,"key_states":{"actual_goal_position":[0.56442,0.24486,0.14677],"final_object_position":[0.5438,0.20353,0.01602],"final_tcp_position":[0.56137,0.24313,0.28012],"realised_goal_position":[0.56442,0.24486,0.14677],"realised_object_initial_position":[0.50118,0.04505,0.03]},"peak_contact_force":273007.13627,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":482.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.03],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.23992,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1924.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.4971,0.04136,0.12592],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.10005,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":288.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1152.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.49612,0.04412,0.03449],"tcp_start":[0.4971,0.04136,0.12592],"tcp_to_object_dist_end":0.00991,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50107,0.04338,0.0255],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.24355,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"peak_contact_force":0.15731,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10871.0,"raw_peak_contact_force":0.25154,"tcp_end":[0.48798,0.04338,0.02586],"tcp_start":[0.49612,0.04412,0.03449],"tcp_to_object_dist_end":0.0131,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50086,0.04302,0.11046],"object_pos_start":[0.50107,0.04338,0.0255],"object_to_goal_dist_end":0.2147,"object_to_goal_dist_start":0.24355,"object_z_max":0.11037,"peak_contact_force":0.06955,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":39157.0,"raw_peak_contact_force":0.65919,"tcp_end":[0.49073,0.04301,0.12016],"tcp_start":[0.48798,0.04338,0.02586],"tcp_to_object_dist_end":0.01402,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5438,0.20352,0.016],"object_pos_start":[0.50086,0.04302,0.11046],"object_to_goal_dist_end":0.13869,"object_to_goal_dist_start":0.2147,"object_z_max":0.18452,"peak_contact_force":273007.13627,"phase_name":"approach_2","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":22026.0,"raw_peak_contact_force":1.9152,"subtask_id":"reach_goal","tcp_end":[0.55265,0.21888,0.23878],"tcp_start":[0.49073,0.04301,0.12016],"tcp_to_object_dist_end":0.22349,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":262.0,"n_steps_budget":1000.0,"object_pos_end":[0.5438,0.20353,0.01602],"object_pos_start":[0.5438,0.20352,0.016],"object_to_goal_dist_end":0.13867,"object_to_goal_dist_start":0.13869,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2171.0,"raw_peak_contact_force":0.12348,"subtask_id":"reach_goal","tcp_end":[0.55902,0.23934,0.15286],"tcp_start":[0.55265,0.21888,0.23878],"tcp_to_object_dist_end":0.14227,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.5438,0.20353,0.01602],"object_pos_start":[0.5438,0.20353,0.01602],"object_to_goal_dist_end":0.13867,"object_to_goal_dist_start":0.13867,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1021.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.5531,0.23674,0.1737],"tcp_start":[0.55902,0.23934,0.15286],"tcp_to_object_dist_end":0.16141,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":542.0,"n_steps_budget":600.0,"object_pos_end":[0.5438,0.20353,0.01602],"object_pos_start":[0.5438,0.20353,0.01602],"object_to_goal_dist_end":0.13867,"object_to_goal_dist_start":0.13867,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2168.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.56137,0.24313,0.28012],"tcp_start":[0.5531,0.23674,0.1737],"tcp_to_object_dist_end":0.26763,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.13281,"average_solve_count":128.0,"average_success_count":128.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.28988,"approach_1.approach_z":0.12348,"approach_2.approach2_z":0.15062,"approach_2.transport_speed":0.30284,"descend_1.descend_speed":0.09685,"descend_2.place_speed":0.11847,"grasp_1.grasp_force_threshold":0.61978,"lift_1.lift_speed":0.16794,"lift_1.lift_z":0.11649,"release_1.release_duration":0.61508,"retract_1.retract_speed":0.21224},"optimized_scores":{"best_composite_score":-0.14751,"best_fitness_score":0.58249,"best_task_score":0.20409},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":2441.0,"contact_point_centroid":[0.52031,0.04006,-0.00236],"force_p95":0.13459,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.7537,"mean_force":0.1408,"phase_index":4.0,"phase_name":"approach_2","phase_type":"approach","tcp_position_centroid":[0.55181,0.07321,0.23278]},{"body_a":"world","body_b":"grasp_target","contact_count":146.0,"contact_point_centroid":[0.47442,-0.01955,-0.00117],"force_p95":0.48437,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.69846,"mean_force":0.07724,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46267,-0.01963,0.02874]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8091.0,"contact_point_centroid":[0.46736,-0.0006,0.07207],"force_p95":0.10781,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31854,"mean_force":0.06785,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46502,-0.01957,0.06978]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3025.0,"contact_point_centroid":[0.49082,0.01763,0.14618],"force_p95":0.15999,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31517,"mean_force":0.10151,"phase_index":4.0,"phase_name":"approach_2","phase_type":"approach","tcp_position_centroid":[0.48532,-0.00067,0.14751]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2913.0,"contact_point_centroid":[0.48982,-0.02038,0.14495],"force_p95":0.1651,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30791,"mean_force":0.10368,"phase_index":4.0,"phase_name":"approach_2","phase_type":"approach","tcp_position_centroid":[0.48417,-0.00201,0.14603]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8788.0,"contact_point_centroid":[0.46733,-0.03844,0.0707],"force_p95":0.10323,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30609,"mean_force":0.06333,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46494,-0.01957,0.06899]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.47615,-0.02002,-0.00204],"force_p95":0.13523,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.17494,"mean_force":0.12614,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46503,-0.01969,0.02828]},{"body_a":"world","body_b":"grasp_target","contact_count":1508.0,"contact_point_centroid":[0.47616,-0.02015,-0.00191],"force_p95":0.13496,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12295,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48703,-0.00872,0.23214]},{"body_a":"world","body_b":"grasp_target","contact_count":1652.0,"contact_point_centroid":[0.47616,-0.02015,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.47209,-0.01888,0.09854]},{"body_a":"world","body_b":"grasp_target","contact_count":1412.0,"contact_point_centroid":[0.52024,0.04007,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.60521,0.13333,0.23334]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.52024,0.04007,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.61922,0.15239,0.19081]},{"body_a":"world","body_b":"grasp_target","contact_count":2168.0,"contact_point_centroid":[0.52024,0.04007,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":7.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.62168,0.15452,0.26156]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5067.0,"contact_point_centroid":[0.46365,-0.00042,0.02993],"force_p95":0.06586,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09145,"mean_force":0.04291,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46391,-0.01966,0.02719]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5397.0,"contact_point_centroid":[0.46352,-0.03892,0.02943],"force_p95":0.06456,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0872,"mean_force":0.04119,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46392,-0.01966,0.02719]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2354.0,"contact_point_centroid":[0.55562,0.07712,0.23956],"force_p95":0.01115,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01616,"mean_force":0.01053,"phase_index":4.0,"phase_name":"approach_2","phase_type":"approach","tcp_position_centroid":[0.55537,0.07712,0.23733]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1511.0,"contact_point_centroid":[0.60568,0.13335,0.23566],"force_p95":0.01097,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01282,"mean_force":0.01042,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.60522,0.13335,0.2333]}],"total_contact_groups":17},"final_pose_error":0.0183,"key_states":{"actual_goal_position":[0.63142,0.15919,0.19002],"final_object_position":[0.52024,0.04007,0.01602],"final_tcp_position":[0.62876,0.15805,0.32195],"realised_goal_position":[0.63142,0.15919,0.19002],"realised_object_initial_position":[0.47616,-0.02015,0.03]},"peak_contact_force":9748.75078,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":378.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.03],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28614,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1508.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.47502,-0.01803,0.1631],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.1371,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":413.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1652.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.47173,-0.01984,0.03494],"tcp_start":[0.47502,-0.01803,0.1631],"tcp_to_object_dist_end":0.00997,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":47.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.47603,-0.01968,0.02584],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28826,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.13349,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12264.0,"raw_peak_contact_force":0.17494,"tcp_end":[0.46388,-0.01966,0.02716],"tcp_start":[0.47173,-0.01984,0.03494],"tcp_to_object_dist_end":0.01222,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":25.0,"n_steps":538.0,"n_steps_budget":600.0,"object_pos_end":[0.48944,-0.01943,0.11842],"object_pos_start":[0.47603,-0.01968,0.02584],"object_to_goal_dist_end":0.23915,"object_to_goal_dist_start":0.28826,"object_z_max":0.11829,"peak_contact_force":0.10379,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":17025.0,"raw_peak_contact_force":0.69846,"tcp_end":[0.47133,-0.01957,0.12933],"tcp_start":[0.46388,-0.01966,0.02716],"tcp_to_object_dist_end":0.02114,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.52024,0.04007,0.01602],"object_pos_start":[0.48944,-0.01943,0.11842],"object_to_goal_dist_end":0.23838,"object_to_goal_dist_start":0.23915,"object_z_max":0.14764,"peak_contact_force":0.12263,"phase_name":"approach_2","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":10733.0,"raw_peak_contact_force":1.7537,"subtask_id":"reach_goal","tcp_end":[0.58889,0.114,0.28011],"tcp_start":[0.47133,-0.01957,0.12933],"tcp_to_object_dist_end":0.2827,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":353.0,"n_steps_budget":1000.0,"object_pos_end":[0.52024,0.04007,0.01602],"object_pos_start":[0.52024,0.04007,0.01602],"object_to_goal_dist_end":0.23838,"object_to_goal_dist_start":0.23838,"object_z_max":0.01602,"peak_contact_force":9748.75078,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2923.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_goal","tcp_end":[0.62332,0.1534,0.19087],"tcp_start":[0.58889,0.114,0.28011],"tcp_to_object_dist_end":0.23247,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.52024,0.04007,0.01602],"object_pos_start":[0.52024,0.04007,0.01602],"object_to_goal_dist_end":0.23838,"object_to_goal_dist_start":0.23838,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1020.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.61775,0.15193,0.21022],"tcp_start":[0.62332,0.1534,0.19087],"tcp_to_object_dist_end":0.24441,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":542.0,"n_steps_budget":600.0,"object_pos_end":[0.52024,0.04007,0.01602],"object_pos_start":[0.52024,0.04007,0.01602],"object_to_goal_dist_end":0.23838,"object_to_goal_dist_start":0.23838,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2168.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.62876,0.15805,0.32195],"tcp_start":[0.61775,0.15193,0.21022],"tcp_to_object_dist_end":0.34538,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.2314,"average_solve_count":121.0,"average_success_count":121.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.37344,"approach_1.approach_z":0.14279,"approach_2.approach2_z":0.05053,"approach_2.transport_speed":0.44246,"descend_1.descend_speed":0.14952,"descend_2.place_speed":0.10624,"grasp_1.grasp_force_threshold":2.28282,"lift_1.lift_speed":0.17297,"lift_1.lift_z":0.10867,"release_1.release_duration":0.69513,"retract_1.retract_speed":0.25242},"optimized_scores":{"best_composite_score":-0.00534,"best_fitness_score":0.72466,"best_task_score":0.4872},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":294.0,"contact_point_centroid":[0.60349,0.17285,-0.00479],"force_p95":1.06735,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.43037,"mean_force":0.27188,"phase_index":4.0,"phase_name":"approach_2","phase_type":"approach","tcp_position_centroid":[0.59899,0.17092,0.14982]},{"body_a":"world","body_b":"grasp_target","contact_count":132.0,"contact_point_centroid":[0.45604,-0.02528,-0.00125],"force_p95":0.48345,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.65949,"mean_force":0.08933,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44572,-0.02558,0.02922]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":10828.0,"contact_point_centroid":[0.51848,0.07654,0.13249],"force_p95":0.11711,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.34157,"mean_force":0.07895,"phase_index":4.0,"phase_name":"approach_2","phase_type":"approach","tcp_position_centroid":[0.5137,0.0582,0.13211]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":9362.0,"contact_point_centroid":[0.51078,0.02989,0.13054],"force_p95":0.15532,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33608,"mean_force":0.0869,"phase_index":4.0,"phase_name":"approach_2","phase_type":"approach","tcp_position_centroid":[0.50644,0.04858,0.13059]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8314.0,"contact_point_centroid":[0.44986,-0.0065,0.07039],"force_p95":0.10424,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.301,"mean_force":0.06485,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44792,-0.0255,0.06815]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8995.0,"contact_point_centroid":[0.44974,-0.04442,0.06892],"force_p95":0.10227,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28924,"mean_force":0.0609,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44781,-0.0255,0.06728]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.45857,-0.02616,-0.00206],"force_p95":0.13998,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.19259,"mean_force":0.12737,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44788,-0.02567,0.02874]},{"body_a":"world","body_b":"grasp_target","contact_count":1388.0,"contact_point_centroid":[0.45856,-0.02632,-0.0019],"force_p95":0.1356,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12298,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.47985,-0.01118,0.24172]},{"body_a":"world","body_b":"grasp_target","contact_count":1300.0,"contact_point_centroid":[0.60363,0.17205,-0.00197],"force_p95":0.12639,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.1303,"mean_force":0.12258,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.61412,0.19256,0.12432]},{"body_a":"world","body_b":"grasp_target","contact_count":1776.0,"contact_point_centroid":[0.45856,-0.02632,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.45593,-0.02451,0.10784]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.60363,0.17204,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.61834,0.20246,0.10796]},{"body_a":"world","body_b":"grasp_target","contact_count":2168.0,"contact_point_centroid":[0.60363,0.17204,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":7.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.61951,0.20353,0.18182]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4816.0,"contact_point_centroid":[0.44681,-0.00642,0.03006],"force_p95":0.06807,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09779,"mean_force":0.04488,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.4468,-0.02563,0.02773]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5172.0,"contact_point_centroid":[0.44667,-0.04486,0.02956],"force_p95":0.06686,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08234,"mean_force":0.043,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44681,-0.02563,0.02773]},{"body_a":"left_finger","body_b":"right_finger","contact_count":53.0,"contact_point_centroid":[0.60359,0.17665,0.15265],"force_p95":0.01632,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01632,"mean_force":0.01416,"phase_index":4.0,"phase_name":"approach_2","phase_type":"approach","tcp_position_centroid":[0.60318,0.17665,0.15074]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1390.0,"contact_point_centroid":[0.6146,0.19255,0.1265],"force_p95":0.01119,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0128,"mean_force":0.0105,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.6141,0.19253,0.12436]}],"total_contact_groups":17},"final_pose_error":0.01903,"key_states":{"actual_goal_position":[0.63013,0.20822,0.11412],"final_object_position":[0.60363,0.17204,0.01602],"final_tcp_position":[0.62653,0.20671,0.24549],"realised_goal_position":[0.63013,0.20822,0.11412],"realised_object_initial_position":[0.45856,-0.02632,0.03]},"peak_contact_force":1.43037,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":348.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.03],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30252,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1388.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.45991,-0.02325,0.18216],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.15618,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":444.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1776.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.4544,-0.02589,0.03495],"tcp_start":[0.45991,-0.02325,0.18216],"tcp_to_object_dist_end":0.00986,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":45.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.45844,-0.02566,0.02579],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30328,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.13725,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11788.0,"raw_peak_contact_force":0.19259,"tcp_end":[0.44678,-0.02562,0.0277],"tcp_start":[0.4544,-0.02589,0.03495],"tcp_to_object_dist_end":0.01182,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":529.0,"n_steps_budget":600.0,"object_pos_end":[0.47121,-0.02545,0.1119],"object_pos_start":[0.45844,-0.02566,0.02579],"object_to_goal_dist_end":0.2826,"object_to_goal_dist_start":0.30328,"object_z_max":0.11178,"peak_contact_force":0.11435,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":17441.0,"raw_peak_contact_force":0.65949,"tcp_end":[0.45379,-0.0255,0.12238],"tcp_start":[0.44678,-0.02562,0.0277],"tcp_to_object_dist_end":0.02034,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.60367,0.17212,0.0166],"object_pos_start":[0.47121,-0.02545,0.1119],"object_to_goal_dist_end":0.1073,"object_to_goal_dist_start":0.2826,"object_z_max":0.12059,"peak_contact_force":0.12569,"phase_name":"approach_2","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":20537.0,"raw_peak_contact_force":1.43037,"subtask_id":"reach_goal","tcp_end":[0.60436,0.17786,0.15085],"tcp_start":[0.45379,-0.0255,0.12238],"tcp_to_object_dist_end":0.13438,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":325.0,"n_steps_budget":1000.0,"object_pos_end":[0.60363,0.17204,0.01602],"object_pos_start":[0.60367,0.17212,0.0166],"object_to_goal_dist_end":0.10786,"object_to_goal_dist_start":0.1073,"object_z_max":0.0166,"peak_contact_force":0.12263,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2690.0,"raw_peak_contact_force":0.1303,"subtask_id":"reach_goal","tcp_end":[0.62334,0.20415,0.10801],"tcp_start":[0.60436,0.17786,0.15085],"tcp_to_object_dist_end":0.09941,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.60363,0.17204,0.01602],"object_pos_start":[0.60363,0.17204,0.01602],"object_to_goal_dist_end":0.10786,"object_to_goal_dist_start":0.10786,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1025.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.61637,0.20173,0.12721],"tcp_start":[0.62334,0.20415,0.10801],"tcp_to_object_dist_end":0.11579,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":542.0,"n_steps_budget":600.0,"object_pos_end":[0.60363,0.17204,0.01602],"object_pos_start":[0.60363,0.17204,0.01602],"object_to_goal_dist_end":0.10786,"object_to_goal_dist_start":0.10786,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2168.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.62653,0.20671,0.24549],"tcp_start":[0.61637,0.20173,0.12721],"tcp_to_object_dist_end":0.23321,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```