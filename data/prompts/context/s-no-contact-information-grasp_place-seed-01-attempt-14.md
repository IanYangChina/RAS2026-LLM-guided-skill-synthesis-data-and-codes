## Search State

- **Seed**: 1
- **Iteration**: 15 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 14 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 7 | 0.5105 | 1.00 | ✅ accepted |
| 13 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 7 | 0.5104 | 1.00 | ✅ accepted |
| 12 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 7 | 0.5090 | 1.00 | ❌ rejected |
| 11 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 7 | 0.5097 | 1.00 | ❌ rejected |
| 10 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 7 | 0.5103 | 1.00 | ✅ accepted |

**Proposal policy**: task_score is near-perfect (1.00). Preserve useful working parts and make only evidence-backed refinements. A HOLD is acceptable if you genuinely cannot find a better structure.

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

> ⚠️ **SUBTASK STRUCTURE CAUTION**: The current best task_score is 1.000, which indicates the subtask decomposition is already effective.
> Preserve the current subtask decomposition unless the evidence shows a subtask change is necessary. Prefer refining phases, parameters, control modes, or termination conditions first.
> Unnecessary subtask redesign when performance is already high often causes regression.

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

## Current Skill (Q=0.510) — your mutation base

```yaml
skill: grasp_place
dsl_version: 2
subtasks:
- id: pre_grasp
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.1
  weight: 0.2
- id: grasp_obj
  anchor: object
  target_entity: object
  offset:
  - 0.0
  - 0.0
  - 0.03
  weight: 0.3
- id: lift_obj
  anchor: object
  target_entity: object
  offset:
  - 0.0
  - 0.0
  - 0.1
  weight: 0.2
- id: place_obj
  target_entity: object
  weight: 0.3
phases:
- id: approach_1
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
    - 0.1
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    approach_speed:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.1
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: approach_tol
    when: after_phase
    predicate: pose_within_tolerance
    threshold: 0.02
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: reduce_speed
  subtask_id: pre_grasp
- id: descend_1
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
    - 0.03
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    descend_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
    grasp_offset_z:
      type: scalar
      range:
      - 0.0
      - 0.05
      default: 0.03
      binds_to:
      - path: target.offset.z
        mode: replace
  guards:
  - id: descend_tol
    when: after_phase
    predicate: pose_within_tolerance
    threshold: 0.01
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.0
    - 0.0
    - 0.005
  subtask_id: grasp_obj
- id: grasp_1
  type: grasp
  control: impedance_control
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
  - id: grasp_check
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
  subtask_id: grasp_obj
- id: lift_1
  type: lift
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
  parameters:
    lift_height:
      type: scalar
      range:
      - 0.1
      - 0.2
      default: 0.15
      binds_to:
      - path: target.offset.z
        mode: replace
    lift_speed:
      type: scalar
      range:
      - 0.02
      - 0.12
      default: 0.06
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: lifted
    when: after_phase
    predicate: object_lifted
    threshold: 0.05
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.0
    - 0.0
    - 0.01
  subtask_id: lift_obj
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
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    transport_speed:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.1
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: approach_goal_tol
    when: after_phase
    predicate: pose_within_tolerance
    threshold: 0.02
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: reduce_speed
  subtask_id: place_obj
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
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    place_speed:
      type: scalar
      range:
      - 0.01
      - 0.08
      default: 0.04
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: descend_goal_tol
    when: after_phase
    predicate: pose_within_tolerance
    threshold: 0.02
    on_failure: retry
  retries:
    max_attempts: 1
    strategy: reduce_speed
  subtask_id: place_obj

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.1], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=approach_tol, when=after_phase, predicate=pose_within_tolerance, on_failure=retry, threshold=0.02
  - retries: max_attempts=2, strategy=reduce_speed
- **descend_1** (`descend`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.03], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - descend_speed: status=consumed; consumers=generator.speed (replace)
    - grasp_offset_z: status=consumed; consumers=target.offset.z (replace)
  - guards:
    - id=descend_tol, when=after_phase, predicate=pose_within_tolerance, on_failure=retry, threshold=0.01
  - retries: max_attempts=2, strategy=offset_target, offset=[0.0, 0.0, 0.005]
- **grasp_1** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings: none
  - guards:
    - id=grasp_check, when=after_phase, predicate=bilateral_grasp, on_failure=retry, threshold=1.0
  - retries: max_attempts=2, strategy=offset_target, offset=[0.0, 0.0, -0.005]
- **lift_1** (`lift`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.15], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset.z (replace)
    - lift_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=lifted, when=after_phase, predicate=object_lifted, on_failure=retry, threshold=0.05
  - retries: max_attempts=2, strategy=offset_target, offset=[0.0, 0.0, 0.01]
- **approach_2** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.1], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - transport_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=approach_goal_tol, when=after_phase, predicate=pose_within_tolerance, on_failure=retry, threshold=0.02
  - retries: max_attempts=2, strategy=reduce_speed
- **descend_2** (`descend`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - place_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=descend_goal_tol, when=after_phase, predicate=pose_within_tolerance, on_failure=retry, threshold=0.02
  - retries: max_attempts=1, strategy=reduce_speed

## Design Metrics

- **Composite score**: 0.510
- **task_score** (E): 1.000
- **fitness_score**: 0.980  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Complexity Penalty**: 0.470

## Per-Phase Performance

| Phase | Normal Term. Rate | Mean Displacement (m) |
| ------- | ------------------- | ------------------------ |
| approach_1 | 1.00 | 0.1565 |
| descend_1 | 1.00 | 0.1141 |
| grasp_1 | 1.00 | 0.0112 |
| lift_1 | 1.00 | 0.1566 |
| approach_2 | 1.00 | 0.2426 |
| descend_2 | 1.00 | 0.0706 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end |
| --- | --- | --- | --- | --- | --- |
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.479, -0.000, 0.149) | (0.479, -0.000, 0.030)→(0.479, -0.000, 0.026) | 0.276→0.278 |
| descend_1 | descend | 1.00 / step_budget | (0.479, -0.000, 0.149)→(0.474, -0.001, 0.035) | (0.479, -0.000, 0.026)→(0.479, -0.000, 0.026) | 0.278→0.278 |
| grasp_1 | grasp | 1.00 / step_budget | (0.474, -0.001, 0.035)→(0.466, -0.001, 0.027) | (0.479, -0.000, 0.026)→(0.479, -0.001, 0.026) | 0.278→0.278 |
| lift_1 | lift | 1.00 / step_budget | (0.466, -0.001, 0.027)→(0.474, -0.001, 0.184) | (0.479, -0.001, 0.026)→(0.485, -0.001, 0.179) | 0.278→0.247 |
| approach_2 | approach | 1.00 / step_budget | (0.474, -0.001, 0.184)→(0.599, 0.192, 0.238) | (0.485, -0.001, 0.179)→(0.606, 0.192, 0.226) | 0.247→0.077 |
| descend_2 | descend | 1.00 / step_budget | (0.599, 0.192, 0.238)→(0.603, 0.199, 0.168) | (0.606, 0.192, 0.226)→(0.612, 0.199, 0.155) | 0.077→0.008 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.705
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 1.000
- phase_score: 0.538
- phase_breakdown.pre_grasp_score: 0.675
- phase_breakdown.place_obj_score: 0.674
- phase_breakdown.grasp_obj_score: 0.509
- phase_breakdown.lift_obj_score: 0.239
- grasp_place_fitness: 0.981

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.981
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 1.000
- **Median Q (composite search score)**: 0.511
- **K-run variance**: 0.0000
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.475


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.96396,"average_solve_count":333.0,"average_success_count":333.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.08983,"approach_2.transport_speed":0.06177,"descend_1.descend_speed":0.09376,"descend_1.grasp_offset_z":1e-05,"descend_2.place_speed":0.02377,"lift_1.lift_height":0.14588,"lift_1.lift_speed":0.02636},"optimized_scores":{"best_composite_score":0.50931,"best_fitness_score":0.97931,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":108.0,"contact_point_centroid":[0.49756,0.04268,-0.00165],"force_p95":0.47979,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55049,"mean_force":0.21788,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48709,0.04305,0.0267]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":9952.0,"contact_point_centroid":[0.48996,0.06194,0.08792],"force_p95":0.07602,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26373,"mean_force":0.05017,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49019,0.04283,0.08617]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50125,0.04462,-0.00217],"force_p95":0.17409,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.26258,"mean_force":0.13624,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.48932,0.04327,0.02703]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":9077.0,"contact_point_centroid":[0.49006,0.02364,0.08723],"force_p95":0.08047,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24507,"mean_force":0.05327,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49006,0.04283,0.0847]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3760.0,"contact_point_centroid":[0.48924,0.02398,0.02884],"force_p95":0.08619,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14947,"mean_force":0.05551,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.48815,0.04317,0.02581]},{"body_a":"world","body_b":"grasp_target","contact_count":1200.0,"contact_point_centroid":[0.50118,0.04505,-0.00189],"force_p95":0.13608,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12303,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49842,0.01853,0.22539]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2358.0,"contact_point_centroid":[0.55997,0.25405,0.20345],"force_p95":0.08361,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12899,"mean_force":0.05939,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.55789,0.23507,0.2033]},{"body_a":"world","body_b":"grasp_target","contact_count":1440.0,"contact_point_centroid":[0.50118,0.04505,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49578,0.04109,0.09046]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2070.0,"contact_point_centroid":[0.56002,0.21611,0.20492],"force_p95":0.09154,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1208,"mean_force":0.06449,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.55789,0.23506,0.20335]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":13885.0,"contact_point_centroid":[0.52737,0.12294,0.19471],"force_p95":0.07567,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10988,"mean_force":0.0509,"phase_index":4.0,"phase_name":"approach_2","phase_type":"approach","tcp_position_centroid":[0.52698,0.14206,0.19287]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4959.0,"contact_point_centroid":[0.4888,0.06233,0.02766],"force_p95":0.07642,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08835,"mean_force":0.04549,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.48816,0.04317,0.02582]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":14077.0,"contact_point_centroid":[0.5276,0.16192,0.1946],"force_p95":0.07392,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08184,"mean_force":0.0505,"phase_index":4.0,"phase_name":"approach_2","phase_type":"approach","tcp_position_centroid":[0.52721,0.14281,0.19318]}],"total_contact_groups":12},"final_pose_error":0.01956,"key_states":{"actual_goal_position":[0.56442,0.24486,0.14677],"final_object_position":[0.57157,0.23934,0.15282],"final_tcp_position":[0.5594,0.2396,0.16493],"realised_goal_position":[0.56442,0.24486,0.14677],"realised_object_initial_position":[0.50118,0.04505,0.03]},"phases":[{"n_steps":301.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.03],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.23992,"object_z_max":0.03,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"pre_grasp","tcp_end":[0.49794,0.03852,0.14817],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.12237,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":360.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"grasp_obj","tcp_end":[0.49627,0.0439,0.03441],"tcp_start":[0.49794,0.03852,0.14817],"tcp_to_object_dist_end":0.0098,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50108,0.04319,0.02543],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.24374,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","subtask_id":"grasp_obj","tcp_end":[0.48812,0.04316,0.02578],"tcp_start":[0.49627,0.0439,0.03441],"tcp_to_object_dist_end":0.01296,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":469.0,"n_steps_budget":1000.0,"object_pos_end":[0.50757,0.04274,0.14837],"object_pos_start":[0.50108,0.04319,0.02543],"object_to_goal_dist_end":0.20998,"object_to_goal_dist_start":0.24374,"object_z_max":0.1481,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","subtask_id":"lift_obj","tcp_end":[0.49615,0.04284,0.15204],"tcp_start":[0.48812,0.04316,0.02578],"tcp_to_object_dist_end":0.012,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":708.0,"n_steps_budget":1000.0,"object_pos_end":[0.56798,0.23166,0.22306],"object_pos_start":[0.50757,0.04274,0.14837],"object_to_goal_dist_end":0.0775,"object_to_goal_dist_start":0.20998,"object_z_max":0.22297,"phase_name":"approach_2","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"place_obj","tcp_end":[0.55763,0.23174,0.23346],"tcp_start":[0.49615,0.04284,0.15204],"tcp_to_object_dist_end":0.01467,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":140.0,"n_steps_budget":1000.0,"object_pos_end":[0.57157,0.23934,0.15282],"object_pos_start":[0.56798,0.23166,0.22306],"object_to_goal_dist_end":0.01087,"object_to_goal_dist_start":0.0775,"object_z_max":0.22308,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"place_obj","tcp_end":[0.5594,0.2396,0.16493],"tcp_start":[0.55763,0.23174,0.23346],"tcp_to_object_dist_end":0.01717,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.34364,"average_solve_count":291.0,"average_success_count":291.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.12532,"approach_2.transport_speed":0.07012,"descend_1.descend_speed":0.08844,"descend_1.grasp_offset_z":0.00029,"descend_2.place_speed":0.04756,"lift_1.lift_height":0.19075,"lift_1.lift_speed":0.02751},"optimized_scores":{"best_composite_score":0.51066,"best_fitness_score":0.98066,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":90.0,"contact_point_centroid":[0.47228,-0.01933,-0.0015],"force_p95":0.52652,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54802,"mean_force":0.24596,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46314,-0.01952,0.02828]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":11818.0,"contact_point_centroid":[0.46634,-0.03861,0.11372],"force_p95":0.07418,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24743,"mean_force":0.05112,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.4662,-0.01947,0.11179]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":11571.0,"contact_point_centroid":[0.46628,-0.00032,0.1123],"force_p95":0.07402,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24362,"mean_force":0.05182,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.4661,-0.01947,0.11025]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.47616,-0.02002,-0.00205],"force_p95":0.13858,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.18978,"mean_force":0.12703,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46521,-0.01957,0.02855]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2221.0,"contact_point_centroid":[0.62427,0.17105,0.24572],"force_p95":0.08482,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13965,"mean_force":0.05971,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.6226,0.15194,0.24507]},{"body_a":"world","body_b":"grasp_target","contact_count":1116.0,"contact_point_centroid":[0.47616,-0.02015,-0.00188],"force_p95":0.13645,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12306,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48817,-0.00823,0.22631]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2195.0,"contact_point_centroid":[0.62403,0.13291,0.24769],"force_p95":0.08761,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1368,"mean_force":0.05782,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.62253,0.15185,0.24615]},{"body_a":"world","body_b":"grasp_target","contact_count":1472.0,"contact_point_centroid":[0.47616,-0.02015,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.47294,-0.01837,0.09179]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5062.0,"contact_point_centroid":[0.46378,-0.00032,0.03004],"force_p95":0.06599,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09523,"mean_force":0.04286,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46409,-0.01954,0.02745]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":16737.0,"contact_point_centroid":[0.54742,0.04859,0.23813],"force_p95":0.06886,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09107,"mean_force":0.04641,"phase_index":4.0,"phase_name":"approach_2","phase_type":"approach","tcp_position_centroid":[0.54752,0.06767,0.2364]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":14652.0,"contact_point_centroid":[0.54888,0.08817,0.23938],"force_p95":0.07674,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0875,"mean_force":0.0519,"phase_index":4.0,"phase_name":"approach_2","phase_type":"approach","tcp_position_centroid":[0.54867,0.06896,0.23703]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5163.0,"contact_point_centroid":[0.46401,-0.0388,0.02943],"force_p95":0.06675,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0817,"mean_force":0.04305,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46409,-0.01954,0.02746]}],"total_contact_groups":12},"final_pose_error":0.01946,"key_states":{"actual_goal_position":[0.63142,0.15919,0.19002],"final_object_position":[0.63624,0.15516,0.19551],"final_tcp_position":[0.62552,0.15532,0.20815],"realised_goal_position":[0.63142,0.15919,0.19002],"realised_object_initial_position":[0.47616,-0.02015,0.03]},"phases":[{"n_steps":280.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.03],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28614,"object_z_max":0.03,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"pre_grasp","tcp_end":[0.4766,-0.01711,0.14973],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.12375,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":368.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"grasp_obj","tcp_end":[0.47191,-0.01971,0.03522],"tcp_start":[0.4766,-0.01711,0.14973],"tcp_to_object_dist_end":0.01014,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.47603,-0.0196,0.0258],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28823,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","subtask_id":"grasp_obj","tcp_end":[0.46406,-0.01954,0.02742],"tcp_start":[0.47191,-0.01971,0.03522],"tcp_to_object_dist_end":0.01208,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":584.0,"n_steps_budget":1000.0,"object_pos_end":[0.48216,-0.0193,0.1919],"object_pos_start":[0.47603,-0.0196,0.0258],"object_to_goal_dist_end":0.23268,"object_to_goal_dist_start":0.28823,"object_z_max":0.19162,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","subtask_id":"lift_obj","tcp_end":[0.47191,-0.01949,0.19719],"tcp_start":[0.46406,-0.01954,0.02742],"tcp_to_object_dist_end":0.01154,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":772.0,"n_steps_budget":1000.0,"object_pos_end":[0.62916,0.14918,0.26546],"object_pos_start":[0.48216,-0.0193,0.1919],"object_to_goal_dist_end":0.07614,"object_to_goal_dist_start":0.23268,"object_z_max":0.26538,"phase_name":"approach_2","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"place_obj","tcp_end":[0.62076,0.14906,0.27656],"tcp_start":[0.47191,-0.01949,0.19719],"tcp_to_object_dist_end":0.01393,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":129.0,"n_steps_budget":1000.0,"object_pos_end":[0.63624,0.15516,0.19551],"object_pos_start":[0.62916,0.14918,0.26546],"object_to_goal_dist_end":0.00834,"object_to_goal_dist_start":0.07614,"object_z_max":0.26546,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"place_obj","tcp_end":[0.62552,0.15532,0.20815],"tcp_start":[0.62076,0.14906,0.27656],"tcp_to_object_dist_end":0.01658,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.3554,"average_solve_count":287.0,"average_success_count":287.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.10735,"approach_2.transport_speed":0.11682,"descend_1.descend_speed":0.08607,"descend_1.grasp_offset_z":0.00052,"descend_2.place_speed":0.03796,"lift_1.lift_height":0.19526,"lift_1.lift_speed":0.02046},"optimized_scores":{"best_composite_score":0.51139,"best_fitness_score":0.98139,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":89.0,"contact_point_centroid":[0.4549,-0.0252,-0.0015],"force_p95":0.54005,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.56517,"mean_force":0.24348,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44622,-0.02545,0.02917]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":11654.0,"contact_point_centroid":[0.44924,-0.04453,0.11555],"force_p95":0.07462,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24435,"mean_force":0.05144,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44903,-0.02538,0.11371]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":11656.0,"contact_point_centroid":[0.44922,-0.00623,0.11561],"force_p95":0.07346,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23115,"mean_force":0.05114,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44903,-0.02538,0.11369]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.45857,-0.02616,-0.00207],"force_p95":0.14402,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.21113,"mean_force":0.1285,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44823,-0.02552,0.02931]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2995.0,"contact_point_centroid":[0.61981,0.21778,0.17311],"force_p95":0.07178,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16807,"mean_force":0.04766,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.61987,0.19871,0.17111]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2520.0,"contact_point_centroid":[0.61924,0.17957,0.17264],"force_p95":0.07897,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1491,"mean_force":0.05471,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.6199,0.19875,0.17068]},{"body_a":"world","body_b":"grasp_target","contact_count":1164.0,"contact_point_centroid":[0.45856,-0.02632,-0.00189],"force_p95":0.13644,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12305,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48087,-0.01083,0.22593]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5287.0,"contact_point_centroid":[0.44656,-0.00624,0.02996],"force_p95":0.0656,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13063,"mean_force":0.04114,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44715,-0.02548,0.0283]},{"body_a":"world","body_b":"grasp_target","contact_count":1484.0,"contact_point_centroid":[0.45856,-0.02632,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.45683,-0.02405,0.09173]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":16234.0,"contact_point_centroid":[0.53698,0.1066,0.20366],"force_p95":0.07236,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11243,"mean_force":0.04749,"phase_index":4.0,"phase_name":"approach_2","phase_type":"approach","tcp_position_centroid":[0.53704,0.08755,0.20166]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":14511.0,"contact_point_centroid":[0.53318,0.06376,0.20339],"force_p95":0.07904,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11165,"mean_force":0.05314,"phase_index":4.0,"phase_name":"approach_2","phase_type":"approach","tcp_position_centroid":[0.53361,0.08298,0.20152]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5434.0,"contact_point_centroid":[0.44657,-0.04478,0.02981],"force_p95":0.06577,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0808,"mean_force":0.04117,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44715,-0.02548,0.0283]}],"total_contact_groups":12},"final_pose_error":0.01976,"key_states":{"actual_goal_position":[0.63013,0.20822,0.11412],"final_object_position":[0.62751,0.20323,0.11585],"final_tcp_position":[0.62314,0.20316,0.1319],"realised_goal_position":[0.63013,0.20822,0.11412],"realised_object_initial_position":[0.45856,-0.02632,0.03]},"phases":[{"n_steps":292.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.03],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30252,"object_z_max":0.03,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"pre_grasp","tcp_end":[0.46147,-0.0225,0.14903],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.12311,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":371.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"grasp_obj","tcp_end":[0.45472,-0.02575,0.03551],"tcp_start":[0.46147,-0.0225,0.14903],"tcp_to_object_dist_end":0.01026,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.45845,-0.02557,0.02574],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30322,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","subtask_id":"grasp_obj","tcp_end":[0.44712,-0.02548,0.02827],"tcp_start":[0.45472,-0.02575,0.03551],"tcp_to_object_dist_end":0.01161,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":582.0,"n_steps_budget":1000.0,"object_pos_end":[0.46405,-0.02544,0.19568],"object_pos_start":[0.45845,-0.02557,0.02574],"object_to_goal_dist_end":0.29804,"object_to_goal_dist_start":0.30322,"object_z_max":0.1954,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","subtask_id":"lift_obj","tcp_end":[0.45447,-0.02542,0.20152],"tcp_start":[0.44712,-0.02548,0.02827],"tcp_to_object_dist_end":0.01122,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":768.0,"n_steps_budget":1000.0,"object_pos_end":[0.62032,0.19492,0.1901],"object_pos_start":[0.46405,-0.02544,0.19568],"object_to_goal_dist_end":0.07776,"object_to_goal_dist_start":0.29804,"object_z_max":0.19593,"phase_name":"approach_2","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"place_obj","tcp_end":[0.61818,0.19505,0.20531],"tcp_start":[0.45447,-0.02542,0.20152],"tcp_to_object_dist_end":0.01536,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":140.0,"n_steps_budget":1000.0,"object_pos_end":[0.62751,0.20323,0.11585],"object_pos_start":[0.62032,0.19492,0.1901],"object_to_goal_dist_end":0.00589,"object_to_goal_dist_start":0.07776,"object_z_max":0.1901,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"place_obj","tcp_end":[0.62314,0.20316,0.1319],"tcp_start":[0.61818,0.19505,0.20531],"tcp_to_object_dist_end":0.01664,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```