## Search State

- **Seed**: 1
- **Iteration**: 5 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 4 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 12 | -0.1850 | 0.23 | ❌ rejected |
| 3 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 13 | -0.2445 | 0.21 | ❌ rejected |
| 2 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 11 | -0.0743 | 0.35 | ✅ accepted |
| 1 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | impedance_control | impedance_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 0 | 0.4159 | 0.23 | ✅ accepted |
| 0 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 0 | 0.3911 | 0.18 | ✅ accepted |

**Proposal policy**: task_score is 0.23 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=-0.185) — your mutation base

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

- **Composite score**: -0.185
- **task_score** (E): 0.230
- **fitness_score**: 0.595  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.780

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1907 |
| descend_1 | 1.00 | 1.00 | 0.0800 |
| grasp_1 | 1.00 | 1.00 | 0.0111 |
| lift_1 | 1.00 | 1.00 | 0.1213 |
| approach_2 | 1.00 | 1.00 | 0.2351 |
| descend_2 | 1.00 | 1.00 | 0.0890 |
| release_1 | 1.00 | 1.00 | 0.0208 |
| retract_1 | 1.00 | 1.00 | 0.1096 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.476, -0.001, 0.115) | (0.479, -0.000, 0.030)→(0.479, -0.000, 0.026) | 0.276→0.278 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.476, -0.001, 0.115)→(0.474, -0.000, 0.035) | (0.479, -0.000, 0.026)→(0.479, -0.000, 0.026) | 0.278→0.278 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_1 | grasp | 1.00 / step_budget | (0.474, -0.000, 0.035)→(0.466, -0.001, 0.027) | (0.479, -0.000, 0.026)→(0.479, -0.001, 0.026) | 0.278→0.278 | 1.00 / 44.667 | 0.144 | 0.215 |
| lift_1 | lift | 1.00 / step_budget | (0.466, -0.001, 0.027)→(0.473, -0.001, 0.148) | (0.479, -0.001, 0.026)→(0.488, -0.001, 0.134) | 0.278→0.243 | 1.00 / 27.000 | 0.113 | 0.647 |
| approach_2 | approach | 1.00 / step_budget | (0.473, -0.001, 0.148)→(0.586, 0.175, 0.238) | (0.488, -0.001, 0.134)→(0.504, 0.058, 0.016) | 0.243→0.226 | 1.00 / 8.000 | 3249.691 | 1.830 |
| descend_2 | descend | 1.00 / step_budget | (0.586, 0.175, 0.238)→(0.602, 0.199, 0.154) | (0.504, 0.058, 0.016)→(0.504, 0.058, 0.016) | 0.226→0.226 | 1.00 / 8.667 | 182006.003 | 0.123 |
| release_1 | release | 1.00 / step_budget | (0.602, 0.199, 0.154)→(0.596, 0.196, 0.174) | (0.504, 0.058, 0.016)→(0.504, 0.058, 0.016) | 0.226→0.226 | 1.00 / 4.000 | 0.123 | 0.123 |
| retract_1 | retract | 1.00 / step_budget | (0.596, 0.196, 0.174)→(0.606, 0.203, 0.283) | (0.504, 0.058, 0.016)→(0.504, 0.058, 0.016) | 0.226→0.226 | 1.00 / 4.000 | 0.123 | 0.123 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.298
- phase_score: 0.828
- phase_breakdown.reach_object_score: 0.848
- phase_breakdown.reach_goal_score: 0.819
- grasp_place_fitness: 0.630

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.630
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.298
- **Median Q (composite search score)**: -0.182
- **K-run variance**: 0.0009
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.364


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.13534,"average_solve_count":133.0,"average_success_count":133.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.38945,"approach_1.approach_z":0.09521,"approach_2.approach2_z":0.06213,"approach_2.arc_height":0.05034,"approach_2.transport_speed":0.35854,"descend_1.descend_speed":0.15064,"descend_2.place_speed":0.18859,"grasp_1.grasp_force_threshold":0.56224,"lift_1.lift_speed":0.09445,"lift_1.lift_z":0.15181,"release_1.release_duration":0.2529,"retract_1.retract_speed":0.2519},"optimized_scores":{"best_composite_score":-0.18224,"best_fitness_score":0.59776,"best_task_score":0.23727},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":3229.0,"contact_point_centroid":[0.4937,0.08847,-0.00226],"force_p95":0.12924,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.7491,"mean_force":0.13887,"phase_index":4.0,"phase_name":"approach_2","phase_type":"approach","tcp_position_centroid":[0.52679,0.14086,0.22221]},{"body_a":"world","body_b":"grasp_target","contact_count":155.0,"contact_point_centroid":[0.49923,0.04251,-0.00122],"force_p95":0.4727,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.65117,"mean_force":0.07929,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48668,0.04324,0.02787]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":13718.0,"contact_point_centroid":[0.49233,0.06184,0.08605],"force_p95":0.12061,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30894,"mean_force":0.07011,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48942,0.04302,0.08503]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":13283.0,"contact_point_centroid":[0.49247,0.02425,0.08842],"force_p95":0.11806,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29902,"mean_force":0.07117,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48959,0.04302,0.08728]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1114.0,"contact_point_centroid":[0.49957,0.06674,0.16756],"force_p95":0.16608,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25564,"mean_force":0.10704,"phase_index":4.0,"phase_name":"approach_2","phase_type":"approach","tcp_position_centroid":[0.49671,0.0491,0.17244]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50124,0.04468,-0.00215],"force_p95":0.16695,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.25092,"mean_force":0.1345,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.48919,0.0435,0.02718]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":869.0,"contact_point_centroid":[0.49947,0.0297,0.16604],"force_p95":0.17013,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23295,"mean_force":0.10842,"phase_index":4.0,"phase_name":"approach_2","phase_type":"approach","tcp_position_centroid":[0.49649,0.04769,0.17073]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4045.0,"contact_point_centroid":[0.4886,0.0242,0.02877],"force_p95":0.08192,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14849,"mean_force":0.05193,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.48803,0.0434,0.02596]},{"body_a":"world","body_b":"grasp_target","contact_count":1860.0,"contact_point_centroid":[0.50118,0.04505,-0.00193],"force_p95":0.13354,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12289,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49767,0.02028,0.21616]},{"body_a":"world","body_b":"grasp_target","contact_count":1236.0,"contact_point_centroid":[0.50118,0.04505,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49538,0.04257,0.08354]},{"body_a":"world","body_b":"grasp_target","contact_count":840.0,"contact_point_centroid":[0.4935,0.08855,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.55535,0.22867,0.18368]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.4935,0.08855,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.55447,0.23685,0.15295]},{"body_a":"world","body_b":"grasp_target","contact_count":2168.0,"contact_point_centroid":[0.4935,0.08855,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":7.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.5555,0.23884,0.22242]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5026.0,"contact_point_centroid":[0.48858,0.06259,0.02777],"force_p95":0.07445,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08667,"mean_force":0.0448,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.48803,0.0434,0.02597]},{"body_a":"left_finger","body_b":"right_finger","contact_count":3272.0,"contact_point_centroid":[0.52889,0.14553,0.2262],"force_p95":0.01107,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01623,"mean_force":0.01041,"phase_index":4.0,"phase_name":"approach_2","phase_type":"approach","tcp_position_centroid":[0.52838,0.14551,0.22392]},{"body_a":"left_finger","body_b":"right_finger","contact_count":216.0,"contact_point_centroid":[0.55748,0.23815,0.15077],"force_p95":0.01103,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01274,"mean_force":0.01027,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.55708,0.23811,0.14863]}],"total_contact_groups":17},"final_pose_error":0.01707,"key_states":{"actual_goal_position":[0.56442,0.24486,0.14677],"final_object_position":[0.4935,0.08855,0.01602],"final_tcp_position":[0.56136,0.24308,0.28007],"realised_goal_position":[0.56442,0.24486,0.14677],"realised_object_initial_position":[0.50118,0.04505,0.03]},"peak_contact_force":273009.98235,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":466.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.03],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.23992,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1860.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.49717,0.04123,0.1333],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.10742,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":309.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1236.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.49614,0.04414,0.03456],"tcp_start":[0.49717,0.04123,0.1333],"tcp_to_object_dist_end":0.00996,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50107,0.0434,0.0255],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.24354,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"peak_contact_force":0.15713,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10871.0,"raw_peak_contact_force":0.25092,"tcp_end":[0.488,0.04339,0.02593],"tcp_start":[0.49614,0.04414,0.03456],"tcp_to_object_dist_end":0.01308,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":20.0,"n_steps":933.0,"n_steps_budget":1000.0,"object_pos_end":[0.51068,0.04325,0.14642],"object_pos_start":[0.50107,0.0434,0.0255],"object_to_goal_dist_end":0.20865,"object_to_goal_dist_start":0.24354,"object_z_max":0.14634,"peak_contact_force":0.14615,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":27156.0,"raw_peak_contact_force":0.65117,"tcp_end":[0.49675,0.04306,0.16564],"tcp_start":[0.488,0.04339,0.02593],"tcp_to_object_dist_end":0.02373,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.4935,0.08855,0.01602],"object_pos_start":[0.51068,0.04325,0.14642],"object_to_goal_dist_end":0.21578,"object_to_goal_dist_start":0.20865,"object_z_max":0.15437,"peak_contact_force":9748.82755,"phase_name":"approach_2","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":8484.0,"raw_peak_contact_force":1.7491,"subtask_id":"reach_goal","tcp_end":[0.55391,0.21995,0.21679],"tcp_start":[0.49675,0.04306,0.16564],"tcp_to_object_dist_end":0.24744,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":210.0,"n_steps_budget":1000.0,"object_pos_end":[0.4935,0.08855,0.01602],"object_pos_start":[0.4935,0.08855,0.01602],"object_to_goal_dist_end":0.21578,"object_to_goal_dist_start":0.21578,"object_z_max":0.01602,"peak_contact_force":273009.98235,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1738.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_goal","tcp_end":[0.55883,0.23866,0.15199],"tcp_start":[0.55391,0.21995,0.21679],"tcp_to_object_dist_end":0.21281,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.4935,0.08855,0.01602],"object_pos_start":[0.4935,0.08855,0.01602],"object_to_goal_dist_end":0.21578,"object_to_goal_dist_start":0.21578,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1016.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.5529,0.23609,0.1729],"tcp_start":[0.55883,0.23866,0.15199],"tcp_to_object_dist_end":0.2234,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":542.0,"n_steps_budget":600.0,"object_pos_end":[0.4935,0.08855,0.01602],"object_pos_start":[0.4935,0.08855,0.01602],"object_to_goal_dist_end":0.21578,"object_to_goal_dist_start":0.21578,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2168.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.56136,0.24308,0.28007],"tcp_start":[0.5529,0.23609,0.1729],"tcp_to_object_dist_end":0.31339,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.37008,"average_solve_count":127.0,"average_success_count":127.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.17879,"approach_1.approach_z":0.08297,"approach_2.approach2_z":0.12676,"approach_2.arc_height":0.05921,"approach_2.transport_speed":0.3209,"descend_1.descend_speed":0.18646,"descend_2.place_speed":0.10697,"grasp_1.grasp_force_threshold":4.89907,"lift_1.lift_speed":0.29761,"lift_1.lift_z":0.14034,"release_1.release_duration":0.77346,"retract_1.retract_speed":0.37591},"optimized_scores":{"best_composite_score":-0.22259,"best_fitness_score":0.55741,"best_task_score":0.15434},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":3067.0,"contact_point_centroid":[0.48864,-0.00783,-0.00232],"force_p95":0.1297,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.72428,"mean_force":0.13898,"phase_index":4.0,"phase_name":"approach_2","phase_type":"approach","tcp_position_centroid":[0.53522,0.05402,0.2733]},{"body_a":"world","body_b":"grasp_target","contact_count":129.0,"contact_point_centroid":[0.47479,-0.01935,-0.00108],"force_p95":0.50146,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.67919,"mean_force":0.05452,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46264,-0.01961,0.02886]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1189.0,"contact_point_centroid":[0.47819,0.00208,0.16255],"force_p95":0.20083,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.34278,"mean_force":0.12624,"phase_index":4.0,"phase_name":"approach_2","phase_type":"approach","tcp_position_centroid":[0.47227,-0.01629,0.16438]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1405.0,"contact_point_centroid":[0.47801,-0.03457,0.16177],"force_p95":0.19746,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32074,"mean_force":0.11235,"phase_index":4.0,"phase_name":"approach_2","phase_type":"approach","tcp_position_centroid":[0.47226,-0.01637,0.16402]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":7983.0,"contact_point_centroid":[0.46769,-0.00063,0.08143],"force_p95":0.10913,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31213,"mean_force":0.06939,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46505,-0.01955,0.07926]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8488.0,"contact_point_centroid":[0.46756,-0.03843,0.07938],"force_p95":0.10566,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29471,"mean_force":0.0661,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46492,-0.01955,0.07767]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.47616,-0.02003,-0.00204],"force_p95":0.13639,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.18555,"mean_force":0.12644,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46487,-0.01967,0.02801]},{"body_a":"world","body_b":"grasp_target","contact_count":1916.0,"contact_point_centroid":[0.47616,-0.02015,-0.00193],"force_p95":0.13319,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12288,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48638,-0.00905,0.21131]},{"body_a":"world","body_b":"grasp_target","contact_count":1132.0,"contact_point_centroid":[0.47616,-0.02015,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.47166,-0.0191,0.07827]},{"body_a":"world","body_b":"grasp_target","contact_count":1404.0,"contact_point_centroid":[0.48861,-0.00782,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.61142,0.13977,0.25231]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.48861,-0.00782,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.62036,0.15338,0.19486]},{"body_a":"world","body_b":"grasp_target","contact_count":2168.0,"contact_point_centroid":[0.48861,-0.00782,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":7.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.62234,0.15505,0.26375]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5069.0,"contact_point_centroid":[0.46354,-0.0004,0.0298],"force_p95":0.06628,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09312,"mean_force":0.04289,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46375,-0.01964,0.02691]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5397.0,"contact_point_centroid":[0.46341,-0.0389,0.02929],"force_p95":0.06479,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08789,"mean_force":0.04119,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46376,-0.01964,0.02691]},{"body_a":"left_finger","body_b":"right_finger","contact_count":3018.0,"contact_point_centroid":[0.53974,0.05866,0.28075],"force_p95":0.01108,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01643,"mean_force":0.01055,"phase_index":4.0,"phase_name":"approach_2","phase_type":"approach","tcp_position_centroid":[0.53943,0.05866,0.27847]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1501.0,"contact_point_centroid":[0.61185,0.13986,0.25422],"force_p95":0.01097,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01271,"mean_force":0.01043,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.6115,0.13985,0.25199]}],"total_contact_groups":17},"final_pose_error":0.018,"key_states":{"actual_goal_position":[0.63142,0.15919,0.19002],"final_object_position":[0.48861,-0.00782,0.01602],"final_tcp_position":[0.62884,0.1581,0.32223],"realised_goal_position":[0.63142,0.15919,0.19002],"realised_object_initial_position":[0.47616,-0.02015,0.03]},"peak_contact_force":1.72428,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":480.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.03],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28614,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1916.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.47416,-0.01847,0.12258],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.0966,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":283.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1132.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.47155,-0.01981,0.03464],"tcp_start":[0.47416,-0.01847,0.12258],"tcp_to_object_dist_end":0.00979,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":47.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.47603,-0.01966,0.02583],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28826,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.13445,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12266.0,"raw_peak_contact_force":0.18555,"tcp_end":[0.46373,-0.01964,0.02688],"tcp_start":[0.47155,-0.01981,0.03464],"tcp_to_object_dist_end":0.01235,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":24.0,"n_steps":542.0,"n_steps_budget":600.0,"object_pos_end":[0.49076,-0.01959,0.13949],"object_pos_start":[0.47603,-0.01966,0.02583],"object_to_goal_dist_end":0.23303,"object_to_goal_dist_start":0.28826,"object_z_max":0.13934,"peak_contact_force":0.11089,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":16600.0,"raw_peak_contact_force":0.67919,"tcp_end":[0.47161,-0.01955,0.15168],"tcp_start":[0.46373,-0.01964,0.02688],"tcp_to_object_dist_end":0.0227,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.48861,-0.00782,0.01602],"object_pos_start":[0.49076,-0.01959,0.13949],"object_to_goal_dist_end":0.28029,"object_to_goal_dist_start":0.23303,"object_z_max":0.16017,"peak_contact_force":0.12263,"phase_name":"approach_2","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":8679.0,"raw_peak_contact_force":1.72428,"subtask_id":"reach_goal","tcp_end":[0.60044,0.12636,0.31109],"tcp_start":[0.47161,-0.01955,0.15168],"tcp_to_object_dist_end":0.34289,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":351.0,"n_steps_budget":1000.0,"object_pos_end":[0.48861,-0.00782,0.01602],"object_pos_start":[0.48861,-0.00782,0.01602],"object_to_goal_dist_end":0.28029,"object_to_goal_dist_start":0.28029,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2905.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_goal","tcp_end":[0.62444,0.15445,0.19512],"tcp_start":[0.60044,0.12636,0.31109],"tcp_to_object_dist_end":0.27723,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.48861,-0.00782,0.01602],"object_pos_start":[0.48861,-0.00782,0.01602],"object_to_goal_dist_end":0.28029,"object_to_goal_dist_start":0.28029,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1022.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.61892,0.15292,0.21427],"tcp_start":[0.62444,0.15445,0.19512],"tcp_to_object_dist_end":0.28657,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":542.0,"n_steps_budget":600.0,"object_pos_end":[0.48861,-0.00782,0.01602],"object_pos_start":[0.48861,-0.00782,0.01602],"object_to_goal_dist_end":0.28029,"object_to_goal_dist_start":0.28029,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2168.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.62884,0.1581,0.32223],"tcp_start":[0.61892,0.15292,0.21427],"tcp_to_object_dist_end":0.37545,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.89209,"average_solve_count":139.0,"average_success_count":139.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.39386,"approach_1.approach_z":0.04823,"approach_2.approach2_z":0.05242,"approach_2.arc_height":0.07341,"approach_2.transport_speed":0.45072,"descend_1.descend_speed":0.27114,"descend_2.place_speed":0.10927,"grasp_1.grasp_force_threshold":6.91877,"lift_1.lift_speed":0.05497,"lift_1.lift_z":0.14989,"release_1.release_duration":0.24442,"retract_1.retract_speed":0.14235},"optimized_scores":{"best_composite_score":-0.15022,"best_fitness_score":0.62978,"best_task_score":0.29825},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":1707.0,"contact_point_centroid":[0.5308,0.09237,-0.0026],"force_p95":0.28197,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.01627,"mean_force":0.15351,"phase_index":4.0,"phase_name":"approach_2","phase_type":"approach","tcp_position_centroid":[0.56712,0.12946,0.20627]},{"body_a":"world","body_b":"grasp_target","contact_count":165.0,"contact_point_centroid":[0.4554,-0.02498,-0.00117],"force_p95":0.44486,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.61085,"mean_force":0.0889,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44524,-0.02545,0.0293]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5650.0,"contact_point_centroid":[0.47324,-0.01597,0.16125],"force_p95":0.1597,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.40075,"mean_force":0.08188,"phase_index":4.0,"phase_name":"approach_2","phase_type":"approach","tcp_position_centroid":[0.46961,0.00275,0.1609]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6014.0,"contact_point_centroid":[0.47595,0.0243,0.16438],"force_p95":0.14871,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.34351,"mean_force":0.07988,"phase_index":4.0,"phase_name":"approach_2","phase_type":"approach","tcp_position_centroid":[0.47185,0.00572,0.16392]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":20276.0,"contact_point_centroid":[0.44685,-0.04453,0.07877],"force_p95":0.07323,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27906,"mean_force":0.05027,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44683,-0.02537,0.077]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":20418.0,"contact_point_centroid":[0.44693,-0.00622,0.08036],"force_p95":0.07274,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27349,"mean_force":0.0496,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44694,-0.02537,0.07836]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.45857,-0.02615,-0.00207],"force_p95":0.14347,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.20722,"mean_force":0.12832,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44762,-0.02554,0.02865]},{"body_a":"world","body_b":"grasp_target","contact_count":2172.0,"contact_point_centroid":[0.45856,-0.02632,-0.00193],"force_p95":0.13205,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12285,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.47798,-0.01203,0.19377]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5049.0,"contact_point_centroid":[0.44622,-0.00628,0.03021],"force_p95":0.06674,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12984,"mean_force":0.04289,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44654,-0.0255,0.02764]},{"body_a":"world","body_b":"grasp_target","contact_count":740.0,"contact_point_centroid":[0.45856,-0.02632,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.45458,-0.02505,0.06129]},{"body_a":"world","body_b":"grasp_target","contact_count":1076.0,"contact_point_centroid":[0.53059,0.09245,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.6117,0.18948,0.14857]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.53059,0.09245,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.61699,0.2008,0.11483]},{"body_a":"world","body_b":"grasp_target","contact_count":2168.0,"contact_point_centroid":[0.53059,0.09245,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":7.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.61881,0.20262,0.18535]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5186.0,"contact_point_centroid":[0.44645,-0.04477,0.02959],"force_p95":0.06765,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08135,"mean_force":0.04304,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44654,-0.0255,0.02764]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1618.0,"contact_point_centroid":[0.57164,0.13499,0.20787],"force_p95":0.01178,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01563,"mean_force":0.01058,"phase_index":4.0,"phase_name":"approach_2","phase_type":"approach","tcp_position_centroid":[0.57138,0.13499,0.20553]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1130.0,"contact_point_centroid":[0.61198,0.18943,0.15095],"force_p95":0.01101,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01251,"mean_force":0.01059,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.61166,0.18942,0.14874]}],"total_contact_groups":17},"final_pose_error":0.01881,"key_states":{"actual_goal_position":[0.63013,0.20822,0.11412],"final_object_position":[0.53059,0.09245,0.01602],"final_tcp_position":[0.6264,0.20656,0.24576],"realised_goal_position":[0.63013,0.20822,0.11412],"realised_object_initial_position":[0.45856,-0.02632,0.03]},"peak_contact_force":273007.90386,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":544.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.03],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30252,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2172.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.45716,-0.02444,0.08789],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.06191,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":185.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":740.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.45407,-0.02576,0.03481],"tcp_start":[0.45716,-0.02444,0.08789],"tcp_to_object_dist_end":0.00989,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":46.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.45845,-0.02558,0.02575],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30322,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.1402,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12035.0,"raw_peak_contact_force":0.20722,"tcp_end":[0.44651,-0.0255,0.02761],"tcp_start":[0.45407,-0.02576,0.03481],"tcp_to_object_dist_end":0.01208,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.46225,-0.02536,0.11633],"object_pos_start":[0.45845,-0.02558,0.02575],"object_to_goal_dist_end":0.28766,"object_to_goal_dist_start":0.30322,"object_z_max":0.11627,"peak_contact_force":0.08086,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":40859.0,"raw_peak_contact_force":0.61085,"tcp_end":[0.45082,-0.02538,0.12627],"tcp_start":[0.44651,-0.0255,0.02761],"tcp_to_object_dist_end":0.01514,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53059,0.09245,0.01602],"object_pos_start":[0.46225,-0.02536,0.11633],"object_to_goal_dist_end":0.18147,"object_to_goal_dist_start":0.28766,"object_z_max":0.18253,"peak_contact_force":0.12263,"phase_name":"approach_2","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":14989.0,"raw_peak_contact_force":2.01627,"subtask_id":"reach_goal","tcp_end":[0.60378,0.17741,0.18635],"tcp_start":[0.45082,-0.02538,0.12627],"tcp_to_object_dist_end":0.20393,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":269.0,"n_steps_budget":1000.0,"object_pos_end":[0.53059,0.09245,0.01602],"object_pos_start":[0.53059,0.09245,0.01602],"object_to_goal_dist_end":0.18147,"object_to_goal_dist_start":0.18147,"object_z_max":0.01602,"peak_contact_force":273007.90386,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2206.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_goal","tcp_end":[0.62208,0.20245,0.11514],"tcp_start":[0.60378,0.17741,0.18635],"tcp_to_object_dist_end":0.17405,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53059,0.09245,0.01602],"object_pos_start":[0.53059,0.09245,0.01602],"object_to_goal_dist_end":0.18147,"object_to_goal_dist_start":0.18147,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1028.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.61509,0.20008,0.13414],"tcp_start":[0.62208,0.20245,0.11514],"tcp_to_object_dist_end":0.18077,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":542.0,"n_steps_budget":600.0,"object_pos_end":[0.53059,0.09245,0.01602],"object_pos_start":[0.53059,0.09245,0.01602],"object_to_goal_dist_end":0.18147,"object_to_goal_dist_start":0.18147,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2168.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.6264,0.20656,0.24576],"tcp_start":[0.61509,0.20008,0.13414],"tcp_to_object_dist_end":0.27383,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```