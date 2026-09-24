## Search State

- **Seed**: 1
- **Iteration**: 5 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 4 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 3 | 0.3380 | 0.43 | ✅ accepted |
| 3 | rotate → align → push → align → lift | impedance_motion | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | impedance_control | position_control | position_control | position_control | position_control | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 3 | -0.0465 | 0.16 | ❌ rejected |
| 2 | rotate → align → push → align → lift | impedance_motion | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | impedance_control | position_control | position_control | position_control | position_control | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 3 | -0.0465 | 0.16 | ❌ rejected |
| 1 | rotate → align → push → align → lift | impedance_motion | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | impedance_control | position_control | position_control | position_control | position_control | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 3 | -0.0465 | 0.16 | ❌ rejected |
| 0 | rotate → align → push → align → lift | impedance_motion | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | impedance_control | position_control | position_control | position_control | position_control | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 3 | -0.0465 | 0.16 | ✅ accepted |

**Proposal policy**: task_score is 0.43 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.338) — your mutation base

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
  - 0.15
  weight: 0.3
- id: reach_goal
  offset:
  - 0.0
  - 0.0
  - 0.03
  weight: 0.7
phases:
- id: approach_object
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.0
    - 0.15
    tolerance: 0.02
    orientation:
      mode: keep_current
  subtask_id: reach_object
- id: descend_to_grasp
  type: descend
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.03
      axis: world_z
      mode: add_to_offset
      sign: negative
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    grasp_descend_dist:
      type: scalar
      range:
      - 0.02
      - 0.06
      default: 0.03
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
  subtask_id: reach_object
- id: grasp
  type: grasp
  control: position_control
  termination: grasp_success
  end_effector_action: force_grasp
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0
  guards:
  - id: grasp_hold
    when: after_phase
    predicate: bilateral_grasp
    threshold: 1.0
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.0
    - 0.0
    - -0.005
- id: lift
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
    - 0.15
    tolerance: 0.02
    orientation:
      mode: keep_current
- id: approach_goal
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
    - 0.15
    tolerance: 0.02
    orientation:
      mode: keep_current
  subtask_id: reach_goal
- id: descend_place
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
    - 0.03
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    place_xy_offset_x:
      type: scalar
      range:
      - -0.02
      - 0.02
      default: 0.0
      binds_to:
      - path: target.offset.x
        mode: replace
    place_xy_offset_y:
      type: scalar
      range:
      - -0.02
      - 0.02
      default: 0.0
      binds_to:
      - path: target.offset.y
        mode: replace
  subtask_id: reach_goal
- id: release
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
- id: retract
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
    - 0.25
    tolerance: 0.02
    orientation:
      mode: keep_current

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_object** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.15], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings: none
- **descend_to_grasp** (`descend`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=world_z, distance=0.03, mode=add_to_offset, sign=negative}, tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - grasp_descend_dist: status=consumed; consumers=target.offset_along_axis.distance (replace)
- **grasp** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings: none
  - guards:
    - id=grasp_hold, when=after_phase, predicate=bilateral_grasp, on_failure=retry, threshold=1.0
  - retries: max_attempts=2, strategy=offset_target, offset=[0.0, 0.0, -0.005]
- **lift** (`lift`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.15], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings: none
- **approach_goal** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.15], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings: none
- **descend_place** (`descend`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.03], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - place_xy_offset_x: status=consumed; consumers=target.offset.x (replace)
    - place_xy_offset_y: status=consumed; consumers=target.offset.y (replace)
- **release** (`release`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings: none
- **retract** (`retract`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.25], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings: none

## Design Metrics

- **Composite score**: 0.338
- **task_score** (E): 0.427
- **fitness_score**: 0.668  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.330

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_object | 1.00 | 1.00 | 0.1084 |
| descend_to_grasp | 1.00 | 1.00 | 0.2102 |
| grasp | 1.00 | 1.00 | 0.0000 |
| lift | 1.00 | 1.00 | 0.1305 |
| approach_goal | 1.00 | 1.00 | 0.2852 |
| descend_place | 1.00 | 1.00 | 0.0855 |
| release | 1.00 | 1.00 | 0.0197 |
| retract | 1.00 | 1.00 | 0.1636 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.480, -0.000, 0.198) | (0.479, -0.000, 0.030)→(0.479, -0.000, 0.026) | 0.276→0.278 | 1.00 / 45.000 | 5.008 | 5.863 |
| descend_to_grasp | descend | 1.00 / step_budget | (0.480, -0.000, 0.198)→(0.477, -0.001, -0.012) | (0.479, -0.000, 0.026)→(0.480, -0.000, 0.020) | 0.278→0.280 | 1.00 / 45.000 | 3.258 | 4.069 |
| grasp | grasp | 1.00 / step_budget | (0.481, -0.001, -0.009)→(0.481, -0.001, -0.009) | (0.480, -0.000, 0.020)→(0.479, -0.000, 0.021) | 0.280→0.280 | 1.00 / 40.000 | 0.075 | 3.224 |
| lift | lift | 1.00 / step_budget | (0.481, -0.001, -0.009)→(0.478, -0.001, 0.121) | (0.479, -0.000, 0.021)→(0.484, -0.001, 0.125) | 0.280→0.247 | 1.00 / 6.000 | 0.241 | 2.030 |
| approach_goal | approach | 1.00 / step_budget | (0.478, -0.001, 0.121)→(0.600, 0.193, 0.283) | (0.484, -0.001, 0.125)→(0.603, 0.176, 0.018) | 0.247→0.136 | 1.00 / 8.333 | 3249.708 | 0.231 |
| descend_place | descend | 1.00 / step_budget | (0.600, 0.193, 0.283)→(0.602, 0.206, 0.199) | (0.603, 0.176, 0.018)→(0.604, 0.181, 0.023) | 0.136→0.131 | 1.00 / 4.000 | 0.123 | 0.124 |
| release | release | 1.00 / step_budget | (0.602, 0.206, 0.199)→(0.596, 0.204, 0.217) | (0.604, 0.181, 0.023)→(0.604, 0.181, 0.023) | 0.131→0.131 | 1.00 / 4.000 | 0.123 | 0.123 |
| retract | retract | 1.00 / step_budget | (0.596, 0.204, 0.217)→(0.607, 0.203, 0.380) | (0.604, 0.181, 0.023)→(0.604, 0.181, 0.023) | 0.131→0.131 | 1.00 / 4.000 | 0.123 | 0.138 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 0.000
- place_accuracy: 0.000
- lift_clearance: 0.000
- transport_retention: 0.000
- terminal_score: 0.537
- phase_score: 0.453
- phase_breakdown.reach_goal_score: 0.639
- phase_breakdown.reach_object_score: 0.021
- grasp_place_fitness: 0.721

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.721
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.537
- **Median Q (composite search score)**: 0.334
- **K-run variance**: 0.0017
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 10.0
- **Final σ (mean)**: 0.327


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.91892,"average_solve_count":222.0,"average_success_count":222.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"descend_place.place_xy_offset_x":0.00632,"descend_place.place_xy_offset_y":0.00185,"descend_to_grasp.grasp_descend_dist":0.05702},"optimized_scores":{"best_composite_score":0.33358,"best_fitness_score":0.66358,"best_task_score":0.41716},"replay_outcomes":[{"contacts":{"omitted_contact_groups":7,"reported_contact_groups":[{"body_a":"world","body_b":"right_finger","contact_count":642.0,"contact_point_centroid":[0.49753,0.08553,-0.00399],"force_p95":5.1824,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":5.86599,"mean_force":3.45131,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.4976,0.04333,-0.00392]},{"body_a":"world","body_b":"left_finger","contact_count":634.0,"contact_point_centroid":[0.49755,0.00103,-0.00396],"force_p95":5.13056,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":5.73744,"mean_force":3.43037,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.4976,0.04333,-0.00393]},{"body_a":"world","body_b":"left_finger","contact_count":11000.0,"contact_point_centroid":[0.50159,0.00202,-0.00583],"force_p95":3.4252,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":4.13267,"mean_force":2.3687,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.50177,0.04364,-0.00933]},{"body_a":"world","body_b":"right_finger","contact_count":11000.0,"contact_point_centroid":[0.50161,0.08525,-0.00589],"force_p95":3.45306,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":4.08576,"mean_force":2.39163,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.50177,0.04364,-0.00933]},{"body_a":"world","body_b":"right_finger","contact_count":694.0,"contact_point_centroid":[0.50225,0.08409,-0.00351],"force_p95":2.52618,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":3.18334,"mean_force":0.72776,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.50225,0.04359,-0.00258]},{"body_a":"world","body_b":"left_finger","contact_count":690.0,"contact_point_centroid":[0.50223,0.00307,-0.00348],"force_p95":2.68146,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":3.16803,"mean_force":0.73715,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.50225,0.04359,-0.00263]},{"body_a":"world","body_b":"grasp_target","contact_count":80.0,"contact_point_centroid":[0.55871,0.21437,-0.01363],"force_p95":1.99168,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.13034,"mean_force":1.03964,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.5575,0.23004,0.27712]},{"body_a":"grasp_target","body_b":"hand","contact_count":63.0,"contact_point_centroid":[0.51278,0.043,0.04693],"force_p95":0.84109,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.88389,"mean_force":0.6156,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.4971,0.04311,0.00258]},{"body_a":"grasp_target","body_b":"hand","contact_count":550.0,"contact_point_centroid":[0.50471,0.04521,0.04019],"force_p95":0.68959,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.70052,"mean_force":0.65066,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.50177,0.04364,-0.00933]},{"body_a":"grasp_target","body_b":"hand","contact_count":79.0,"contact_point_centroid":[0.51629,0.05059,0.0476],"force_p95":0.39203,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.62902,"mean_force":0.197,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.50136,0.04351,0.00403]},{"body_a":"world","body_b":"grasp_target","contact_count":412.0,"contact_point_centroid":[0.50006,0.04447,-0.00288],"force_p95":0.25683,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.56842,"mean_force":0.15009,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.50088,0.04348,0.00804]},{"body_a":"world","body_b":"grasp_target","contact_count":1616.0,"contact_point_centroid":[0.50115,0.04506,-0.0022],"force_p95":0.28858,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.41529,"mean_force":0.14557,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.49652,0.03989,0.09156]},{"body_a":"world","body_b":"grasp_target","contact_count":491.0,"contact_point_centroid":[0.5598,0.23051,-0.00296],"force_p95":0.27248,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.36904,"mean_force":0.13939,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.56218,0.23876,0.23301]},{"body_a":"world","body_b":"grasp_target","contact_count":2200.0,"contact_point_centroid":[0.50044,0.04522,-0.00455],"force_p95":0.34367,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.36284,"mean_force":0.28566,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.50177,0.04364,-0.00933]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":10938.0,"contact_point_centroid":[0.52135,0.09563,0.17953],"force_p95":0.13995,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.36005,"mean_force":0.06854,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.51893,0.11428,0.17834]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6310.0,"contact_point_centroid":[0.49871,0.02419,0.07357],"force_p95":0.07978,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.34945,"mean_force":0.04977,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.49857,0.04331,0.07166]}],"total_contact_groups":23},"final_pose_error":0.01999,"key_states":{"actual_goal_position":[0.56442,0.24486,0.14677],"final_object_position":[0.56255,0.23497,0.01602],"final_tcp_position":[0.56308,0.2438,0.37686],"realised_goal_position":[0.56442,0.24486,0.14677],"realised_object_initial_position":[0.50118,0.04505,0.03]},"peak_contact_force":5.86599,"phases":[{"contact_detected":true,"contact_event_count":45.0,"n_steps":210.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.03],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.23992,"object_z_max":0.03,"peak_contact_force":4.99526,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2955.0,"raw_peak_contact_force":5.86599,"subtask_id":"reach_object","tcp_end":[0.49827,0.03619,0.19753],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.17176,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":45.0,"n_steps":404.0,"n_steps_budget":1000.0,"object_pos_end":[0.50256,0.04525,0.02039],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.24422,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"peak_contact_force":3.21089,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":24750.0,"raw_peak_contact_force":4.13267,"subtask_id":"reach_object","tcp_end":[0.49881,0.04356,-0.01139],"tcp_start":[0.49827,0.03619,0.19753],"tcp_to_object_dist_end":0.03204,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":150.0,"n_steps_budget":50.0,"object_pos_end":[0.50186,0.04526,0.02099],"object_pos_start":[0.50256,0.04525,0.02039],"object_to_goal_dist_end":0.24409,"object_to_goal_dist_start":0.24422,"object_z_max":0.021,"peak_contact_force":0.07858,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":14637.0,"raw_peak_contact_force":3.18334,"tcp_end":[0.50272,0.0437,-0.00873],"tcp_start":[0.50268,0.0437,-0.00875],"tcp_to_object_dist_end":0.02977,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":407.0,"n_steps_budget":930.0,"object_pos_end":[0.50657,0.04324,0.12605],"object_pos_start":[0.50167,0.04525,0.021],"object_to_goal_dist_end":0.21078,"object_to_goal_dist_start":0.24414,"object_z_max":0.12577,"peak_contact_force":0.39737,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":20518.0,"raw_peak_contact_force":2.13034,"tcp_end":[0.4988,0.04334,0.12178],"tcp_start":[0.50272,0.0437,-0.00873],"tcp_to_object_dist_end":0.00886,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":840.0,"n_steps_budget":1000.0,"object_pos_end":[0.55752,0.21973,0.00088],"object_pos_start":[0.50657,0.04324,0.12605],"object_to_goal_dist_end":0.14821,"object_to_goal_dist_start":0.21078,"object_z_max":0.23448,"peak_contact_force":0.12568,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1154.0,"raw_peak_contact_force":0.36904,"subtask_id":"reach_goal","tcp_end":[0.559,0.23446,0.28088],"tcp_start":[0.4988,0.04334,0.12178],"tcp_to_object_dist_end":0.28039,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":156.0,"n_steps_budget":1000.0,"object_pos_end":[0.56254,0.23495,0.01607],"object_pos_start":[0.55752,0.21973,0.00088],"object_to_goal_dist_end":0.1311,"object_to_goal_dist_start":0.14821,"object_z_max":0.02165,"peak_contact_force":0.12263,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1023.0,"raw_peak_contact_force":0.12563,"subtask_id":"reach_goal","tcp_end":[0.56518,0.24234,0.1953],"tcp_start":[0.559,0.23446,0.28088],"tcp_to_object_dist_end":0.1794,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.56255,0.23497,0.01602],"object_pos_start":[0.56254,0.23495,0.01607],"object_to_goal_dist_end":0.13114,"object_to_goal_dist_start":0.1311,"object_z_max":0.01607,"peak_contact_force":0.12263,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2416.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.55981,0.23983,0.21505],"tcp_start":[0.56518,0.24234,0.1953],"tcp_to_object_dist_end":0.19911,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":604.0,"n_steps_budget":1000.0,"object_pos_end":[0.56255,0.23497,0.01602],"object_pos_start":[0.56255,0.23497,0.01602],"object_to_goal_dist_end":0.13114,"object_to_goal_dist_start":0.13114,"object_z_max":0.01602,"peak_contact_force":0.12262,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":836.0,"raw_peak_contact_force":0.13845,"tcp_end":[0.56308,0.2438,0.37686],"tcp_start":[0.55981,0.23983,0.21505],"tcp_to_object_dist_end":0.36095,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.92105,"average_solve_count":228.0,"average_success_count":228.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"descend_place.place_xy_offset_x":-0.0077,"descend_place.place_xy_offset_y":0.00631,"descend_to_grasp.grasp_descend_dist":0.05595},"optimized_scores":{"best_composite_score":0.2893,"best_fitness_score":0.6193,"best_task_score":0.32727},"replay_outcomes":[{"contacts":{"omitted_contact_groups":8,"reported_contact_groups":[{"body_a":"world","body_b":"left_finger","contact_count":574.0,"contact_point_centroid":[0.47353,-0.06171,-0.00367],"force_p95":4.90021,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":5.50714,"mean_force":3.28306,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.47355,-0.01947,-0.00308]},{"body_a":"world","body_b":"right_finger","contact_count":574.0,"contact_point_centroid":[0.47347,0.02281,-0.00365],"force_p95":4.84867,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":5.46329,"mean_force":3.26341,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.47355,-0.01947,-0.00308]},{"body_a":"world","body_b":"left_finger","contact_count":11000.0,"contact_point_centroid":[0.47715,-0.0613,-0.00549],"force_p95":3.23643,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":3.98532,"mean_force":2.23087,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.47727,-0.01968,-0.00858]},{"body_a":"world","body_b":"right_finger","contact_count":11000.0,"contact_point_centroid":[0.47706,0.02195,-0.00549],"force_p95":3.23308,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":3.77893,"mean_force":2.22966,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.47727,-0.01968,-0.00858]},{"body_a":"world","body_b":"right_finger","contact_count":650.0,"contact_point_centroid":[0.4775,0.02082,-0.00341],"force_p95":2.56217,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":3.08089,"mean_force":0.70988,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.47754,-0.01969,-0.00232]},{"body_a":"world","body_b":"left_finger","contact_count":650.0,"contact_point_centroid":[0.47758,-0.0602,-0.00341],"force_p95":2.51554,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":3.07357,"mean_force":0.69578,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.47754,-0.01969,-0.00232]},{"body_a":"world","body_b":"grasp_target","contact_count":760.0,"contact_point_centroid":[0.60802,0.1282,-0.00384],"force_p95":0.88324,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.27538,"mean_force":0.22275,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.60464,0.13065,0.29795]},{"body_a":"grasp_target","body_b":"hand","contact_count":60.0,"contact_point_centroid":[0.48982,-0.01887,0.04739],"force_p95":0.80996,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.86078,"mean_force":0.60104,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.47321,-0.01937,0.00333]},{"body_a":"grasp_target","body_b":"hand","contact_count":550.0,"contact_point_centroid":[0.48038,-0.02011,0.0406],"force_p95":0.65827,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.67301,"mean_force":0.63114,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.47727,-0.01968,-0.00858]},{"body_a":"grasp_target","body_b":"hand","contact_count":75.0,"contact_point_centroid":[0.49048,-0.02213,0.04765],"force_p95":0.39715,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.61318,"mean_force":0.1894,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.47671,-0.01968,0.00408]},{"body_a":"world","body_b":"grasp_target","contact_count":404.0,"contact_point_centroid":[0.47462,-0.02006,-0.00284],"force_p95":0.24887,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.56125,"mean_force":0.14381,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.47623,-0.01967,0.00856]},{"body_a":"world","body_b":"grasp_target","contact_count":1632.0,"contact_point_centroid":[0.47613,-0.02016,-0.00218],"force_p95":0.28715,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.40646,"mean_force":0.14376,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.47454,-0.01778,0.09334]},{"body_a":"world","body_b":"grasp_target","contact_count":2200.0,"contact_point_centroid":[0.47499,-0.02026,-0.00447],"force_p95":0.33692,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.35127,"mean_force":0.28056,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.47727,-0.01968,-0.00858]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":9635.0,"contact_point_centroid":[0.5174,0.01113,0.17916],"force_p95":0.13487,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32835,"mean_force":0.07184,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.51496,0.03,0.17769]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":9913.0,"contact_point_centroid":[0.51731,0.04888,0.17902],"force_p95":0.1344,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29423,"mean_force":0.07037,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.51495,0.03,0.17768]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6104.0,"contact_point_centroid":[0.47424,-0.00052,0.07391],"force_p95":0.07278,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2737,"mean_force":0.05003,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.47412,-0.01963,0.07202]}],"total_contact_groups":24},"final_pose_error":0.01993,"key_states":{"actual_goal_position":[0.63142,0.15919,0.19002],"final_object_position":[0.61243,0.13063,0.02602],"final_tcp_position":[0.63029,0.15884,0.42012],"realised_goal_position":[0.63142,0.15919,0.19002],"realised_object_initial_position":[0.47616,-0.02015,0.03]},"peak_contact_force":9748.87473,"phases":[{"contact_detected":true,"contact_event_count":45.0,"n_steps":195.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.03],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28614,"object_z_max":0.03,"peak_contact_force":4.68703,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2840.0,"raw_peak_contact_force":5.50714,"subtask_id":"reach_object","tcp_end":[0.47852,-0.01598,0.19941],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.17346,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":45.0,"n_steps":408.0,"n_steps_budget":1000.0,"object_pos_end":[0.47696,-0.02022,0.02065],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.29109,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":3.07644,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":24750.0,"raw_peak_contact_force":3.98532,"subtask_id":"reach_object","tcp_end":[0.47455,-0.01957,-0.01006],"tcp_start":[0.47852,-0.01598,0.19941],"tcp_to_object_dist_end":0.03081,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":150.0,"n_steps_budget":50.0,"object_pos_end":[0.47652,-0.02026,0.02111],"object_pos_start":[0.47696,-0.02022,0.02065],"object_to_goal_dist_end":0.29108,"object_to_goal_dist_start":0.29109,"object_z_max":0.02112,"peak_contact_force":0.07287,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":14035.0,"raw_peak_contact_force":3.08089,"tcp_end":[0.47806,-0.01974,-0.00813],"tcp_start":[0.47803,-0.01973,-0.00814],"tcp_to_object_dist_end":0.02928,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":393.0,"n_steps_budget":930.0,"object_pos_end":[0.48142,-0.0196,0.12597],"object_pos_start":[0.47632,-0.02027,0.02112],"object_to_goal_dist_end":0.242,"object_to_goal_dist_start":0.29118,"object_z_max":0.12568,"peak_contact_force":0.12864,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":21111.0,"raw_peak_contact_force":2.27538,"tcp_end":[0.4743,-0.01963,0.12231],"tcp_start":[0.47806,-0.01974,-0.00813],"tcp_to_object_dist_end":0.00801,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.61227,0.13056,0.02602],"object_pos_start":[0.48142,-0.0196,0.12597],"object_to_goal_dist_end":0.16757,"object_to_goal_dist_start":0.242,"object_z_max":0.23415,"peak_contact_force":9748.87473,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1175.0,"raw_peak_contact_force":0.12853,"subtask_id":"reach_goal","tcp_end":[0.61966,0.14712,0.31804],"tcp_start":[0.4743,-0.01963,0.12231],"tcp_to_object_dist_end":0.29258,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":141.0,"n_steps_budget":1000.0,"object_pos_end":[0.61243,0.13064,0.02602],"object_pos_start":[0.61227,0.13056,0.02602],"object_to_goal_dist_end":0.16754,"object_to_goal_dist_start":0.16757,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1025.0,"raw_peak_contact_force":0.12268,"subtask_id":"reach_goal","tcp_end":[0.62062,0.15975,0.23879],"tcp_start":[0.61966,0.14712,0.31804],"tcp_to_object_dist_end":0.21491,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.61243,0.13063,0.02602],"object_pos_start":[0.61243,0.13064,0.02602],"object_to_goal_dist_end":0.16754,"object_to_goal_dist_start":0.16754,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2576.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.6158,0.15839,0.25731],"tcp_start":[0.62062,0.15975,0.23879],"tcp_to_object_dist_end":0.23297,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":644.0,"n_steps_budget":1000.0,"object_pos_end":[0.61243,0.13063,0.02602],"object_pos_start":[0.61243,0.13063,0.02602],"object_to_goal_dist_end":0.16754,"object_to_goal_dist_start":0.16754,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":776.0,"raw_peak_contact_force":0.13845,"tcp_end":[0.63029,0.15884,0.42012],"tcp_start":[0.6158,0.15839,0.25731],"tcp_to_object_dist_end":0.39552,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.92373,"average_solve_count":236.0,"average_success_count":236.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"descend_place.place_xy_offset_x":-0.00714,"descend_place.place_xy_offset_y":0.01652,"descend_to_grasp.grasp_descend_dist":0.05953},"optimized_scores":{"best_composite_score":0.39124,"best_fitness_score":0.72124,"best_task_score":0.53657},"replay_outcomes":[{"contacts":{"omitted_contact_groups":8,"reported_contact_groups":[{"body_a":"world","body_b":"left_finger","contact_count":774.0,"contact_point_centroid":[0.45695,-0.06767,-0.00458],"force_p95":5.30373,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":6.21582,"mean_force":3.59437,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.457,-0.02546,-0.00537]},{"body_a":"world","body_b":"right_finger","contact_count":774.0,"contact_point_centroid":[0.45689,0.01681,-0.00455],"force_p95":5.29394,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":6.16805,"mean_force":3.57069,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.457,-0.02546,-0.00537]},{"body_a":"world","body_b":"left_finger","contact_count":11000.0,"contact_point_centroid":[0.46233,-0.06744,-0.00666],"force_p95":3.8174,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":4.09031,"mean_force":2.70113,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.46242,-0.02582,-0.01092]},{"body_a":"world","body_b":"right_finger","contact_count":11000.0,"contact_point_centroid":[0.46223,0.0158,-0.00666],"force_p95":3.81349,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":4.08576,"mean_force":2.70427,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.46242,-0.02582,-0.01092]},{"body_a":"world","body_b":"right_finger","contact_count":746.0,"contact_point_centroid":[0.46324,0.01464,-0.00382],"force_p95":2.63156,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":3.40897,"mean_force":0.76513,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.46333,-0.02585,-0.00342]},{"body_a":"world","body_b":"left_finger","contact_count":746.0,"contact_point_centroid":[0.46335,-0.06634,-0.00381],"force_p95":2.54593,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":3.39403,"mean_force":0.74025,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.46333,-0.02585,-0.00342]},{"body_a":"world","body_b":"grasp_target","contact_count":332.0,"contact_point_centroid":[0.6291,0.17791,-0.00577],"force_p95":1.37958,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.68356,"mean_force":0.31091,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.61256,0.18687,0.24317]},{"body_a":"grasp_target","body_b":"hand","contact_count":70.0,"contact_point_centroid":[0.47193,-0.02467,0.04605],"force_p95":0.88213,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.93523,"mean_force":0.64701,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.4566,-0.02533,0.00105]},{"body_a":"grasp_target","body_b":"hand","contact_count":550.0,"contact_point_centroid":[0.46335,-0.02631,0.03926],"force_p95":0.72933,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.74145,"mean_force":0.68166,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.46242,-0.02582,-0.01092]},{"body_a":"grasp_target","body_b":"hand","contact_count":79.0,"contact_point_centroid":[0.47084,-0.02471,0.04729],"force_p95":0.41929,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.64236,"mean_force":0.19898,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.46255,-0.02583,0.00312]},{"body_a":"world","body_b":"grasp_target","contact_count":420.0,"contact_point_centroid":[0.45663,-0.02619,-0.00291],"force_p95":0.25462,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.52422,"mean_force":0.14762,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.46206,-0.02582,0.00765]},{"body_a":"world","body_b":"grasp_target","contact_count":1680.0,"contact_point_centroid":[0.45851,-0.02633,-0.00224],"force_p95":0.30314,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.43354,"mean_force":0.14867,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.45876,-0.02342,0.09025]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":12079.0,"contact_point_centroid":[0.5174,0.03581,0.16606],"force_p95":0.12397,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.38638,"mean_force":0.06757,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.51546,0.05472,0.16443]},{"body_a":"world","body_b":"grasp_target","contact_count":2200.0,"contact_point_centroid":[0.45713,-0.02647,-0.00467],"force_p95":0.36682,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.37602,"mean_force":0.29351,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.46242,-0.02582,-0.01092]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":12493.0,"contact_point_centroid":[0.51686,0.07303,0.16549],"force_p95":0.1225,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.35017,"mean_force":0.06534,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.51497,0.05408,0.16404]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5904.0,"contact_point_centroid":[0.45995,-0.00665,0.07274],"force_p95":0.07304,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24412,"mean_force":0.04992,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.45984,-0.02576,0.07085]}],"total_contact_groups":24},"final_pose_error":0.01981,"key_states":{"actual_goal_position":[0.63013,0.20822,0.11412],"final_object_position":[0.63605,0.17782,0.02602],"final_tcp_position":[0.62781,0.20786,0.34445],"realised_goal_position":[0.63013,0.20822,0.11412],"realised_object_initial_position":[0.45856,-0.02632,0.03]},"peak_contact_force":6.21582,"phases":[{"contact_detected":true,"contact_event_count":45.0,"n_steps":207.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.03],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30252,"object_z_max":0.03,"peak_contact_force":5.34059,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3298.0,"raw_peak_contact_force":6.21582,"subtask_id":"reach_object","tcp_end":[0.46401,-0.02124,0.19803],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.17218,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":45.0,"n_steps":420.0,"n_steps_budget":1000.0,"object_pos_end":[0.45968,-0.02642,0.01997],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30491,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":3.48619,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":24750.0,"raw_peak_contact_force":4.09031,"subtask_id":"reach_object","tcp_end":[0.45838,-0.02563,-0.01372],"tcp_start":[0.46401,-0.02124,0.19803],"tcp_to_object_dist_end":0.03372,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":150.0,"n_steps_budget":50.0,"object_pos_end":[0.45905,-0.02647,0.02074],"object_pos_start":[0.45968,-0.02642,0.01997],"object_to_goal_dist_end":0.30507,"object_to_goal_dist_start":0.30491,"object_z_max":0.02076,"peak_contact_force":0.07245,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":13862.0,"raw_peak_contact_force":3.40897,"tcp_end":[0.46365,-0.02591,-0.01019],"tcp_start":[0.4636,-0.02591,-0.01021],"tcp_to_object_dist_end":0.03127,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":387.0,"n_steps_budget":960.0,"object_pos_end":[0.4635,-0.02573,0.12399],"object_pos_start":[0.45875,-0.02647,0.02076],"object_to_goal_dist_end":0.28739,"object_to_goal_dist_start":0.30523,"object_z_max":0.12369,"peak_contact_force":0.19703,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":25141.0,"raw_peak_contact_force":1.68356,"tcp_end":[0.45998,-0.02575,0.12017],"tcp_start":[0.46365,-0.02591,-0.01019],"tcp_to_object_dist_end":0.00519,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":987.0,"n_steps_budget":1000.0,"object_pos_end":[0.63806,0.17774,0.02586],"object_pos_start":[0.4635,-0.02573,0.12399],"object_to_goal_dist_end":0.09371,"object_to_goal_dist_start":0.28739,"object_z_max":0.20752,"peak_contact_force":0.12301,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1300.0,"raw_peak_contact_force":0.19552,"subtask_id":"reach_goal","tcp_end":[0.62084,0.19787,0.24993],"tcp_start":[0.45998,-0.02575,0.12017],"tcp_to_object_dist_end":0.22563,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":158.0,"n_steps_budget":1000.0,"object_pos_end":[0.63601,0.17782,0.02602],"object_pos_start":[0.63806,0.17774,0.02586],"object_to_goal_dist_end":0.09338,"object_to_goal_dist_start":0.09371,"object_z_max":0.02604,"peak_contact_force":0.12263,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1016.0,"raw_peak_contact_force":0.12327,"subtask_id":"reach_goal","tcp_end":[0.61929,0.21673,0.16181],"tcp_start":[0.62084,0.19787,0.24993],"tcp_to_object_dist_end":0.14225,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.63605,0.17782,0.02602],"object_pos_start":[0.63601,0.17782,0.02602],"object_to_goal_dist_end":0.09338,"object_to_goal_dist_start":0.09338,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2732.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.61287,0.21448,0.17976],"tcp_start":[0.61929,0.21673,0.16181],"tcp_to_object_dist_end":0.15974,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":683.0,"n_steps_budget":1000.0,"object_pos_end":[0.63605,0.17782,0.02602],"object_pos_start":[0.63605,0.17782,0.02602],"object_to_goal_dist_end":0.09338,"object_to_goal_dist_start":0.09338,"object_z_max":0.02602,"peak_contact_force":0.12262,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":824.0,"raw_peak_contact_force":0.13845,"tcp_end":[0.62781,0.20786,0.34445],"tcp_start":[0.61287,0.21448,0.17976],"tcp_to_object_dist_end":0.31995,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```