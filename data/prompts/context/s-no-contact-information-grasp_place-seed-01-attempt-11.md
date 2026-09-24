## Search State

- **Seed**: 1
- **Iteration**: 12 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 11 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 7 | 0.5097 | 1.00 | ❌ rejected |
| 10 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 7 | 0.5103 | 1.00 | ✅ accepted |
| 9 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | impedance_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 7 | 0.2020 | 0.45 | ✅ accepted |
| 8 | rotate → align → push → align → lift | impedance_motion | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | impedance_control | position_control | position_control | position_control | position_control | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 3 | -0.0465 | 0.16 | ❌ rejected |
| 7 | rotate → align → push → align → lift | impedance_motion | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | impedance_control | position_control | position_control | position_control | position_control | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 3 | -0.0465 | 0.16 | ❌ rejected |

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
| descend_1 | 1.00 | 0.1126 |
| grasp_1 | 1.00 | 0.0111 |
| lift_1 | 1.00 | 0.1431 |
| approach_2 | 1.00 | 0.2478 |
| descend_2 | 1.00 | 0.0702 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end |
| --- | --- | --- | --- | --- | --- |
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.479, -0.000, 0.149) | (0.479, -0.000, 0.030)→(0.479, -0.000, 0.026) | 0.276→0.278 |
| descend_1 | descend | 1.00 / step_budget | (0.479, -0.000, 0.149)→(0.474, -0.001, 0.037) | (0.479, -0.000, 0.026)→(0.479, -0.000, 0.026) | 0.278→0.278 |
| grasp_1 | grasp | 1.00 / step_budget | (0.474, -0.001, 0.037)→(0.466, -0.001, 0.029) | (0.479, -0.000, 0.026)→(0.479, -0.001, 0.026) | 0.278→0.278 |
| lift_1 | lift | 1.00 / step_budget | (0.466, -0.001, 0.029)→(0.474, -0.001, 0.172) | (0.479, -0.001, 0.026)→(0.485, -0.001, 0.165) | 0.278→0.250 |
| approach_2 | approach | 1.00 / step_budget | (0.474, -0.001, 0.172)→(0.599, 0.192, 0.238) | (0.485, -0.001, 0.165)→(0.605, 0.192, 0.220) | 0.250→0.071 |
| descend_2 | descend | 1.00 / step_budget | (0.599, 0.192, 0.238)→(0.603, 0.199, 0.169) | (0.605, 0.192, 0.220)→(0.610, 0.200, 0.148) | 0.071→0.011 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.696
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 1.000
- phase_score: 0.567
- phase_breakdown.pre_grasp_score: 0.672
- phase_breakdown.place_obj_score: 0.672
- phase_breakdown.grasp_obj_score: 0.505
- phase_breakdown.lift_obj_score: 0.395
- grasp_place_fitness: 0.981

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.981
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 1.000
- **Median Q (composite search score)**: 0.509
- **K-run variance**: 0.0000
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Parameters at lower bound**: lift_1.lift_speed
- **Final σ (mean)**: 0.439


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.21613,"average_solve_count":310.0,"average_success_count":310.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.19986,"approach_2.transport_speed":0.06927,"descend_1.descend_speed":0.0387,"descend_1.grasp_offset_z":0.00025,"descend_2.place_speed":0.04597,"lift_1.lift_height":0.19827,"lift_1.lift_speed":0.02},"optimized_scores":{"best_composite_score":0.50919,"best_fitness_score":0.97919,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":96.0,"contact_point_centroid":[0.49723,0.04253,-0.00162],"force_p95":0.55217,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.5744,"mean_force":0.23417,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48705,0.04304,0.02695]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":13394.0,"contact_point_centroid":[0.49029,0.06195,0.11455],"force_p95":0.0749,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2734,"mean_force":0.05011,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49048,0.04283,0.11291]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50126,0.04462,-0.00217],"force_p95":0.17419,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.26255,"mean_force":0.13624,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.48925,0.04327,0.02721]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":12464.0,"contact_point_centroid":[0.49047,0.02365,0.11562],"force_p95":0.07934,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25605,"mean_force":0.05239,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49051,0.04283,0.11329]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3752.0,"contact_point_centroid":[0.48922,0.02397,0.02903],"force_p95":0.08628,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15009,"mean_force":0.05562,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.48808,0.04316,0.02599]},{"body_a":"world","body_b":"grasp_target","contact_count":1096.0,"contact_point_centroid":[0.50118,0.04505,-0.00188],"force_p95":0.1365,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12307,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49838,0.01858,0.22517]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2046.0,"contact_point_centroid":[0.55987,0.25303,0.20513],"force_p95":0.09082,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13302,"mean_force":0.06737,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.55759,0.23388,0.2041]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2315.0,"contact_point_centroid":[0.55988,0.21515,0.20436],"force_p95":0.0859,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12818,"mean_force":0.05956,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.5576,0.23393,0.20372]},{"body_a":"world","body_b":"grasp_target","contact_count":1568.0,"contact_point_centroid":[0.50118,0.04505,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49548,0.04105,0.09051]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":12915.0,"contact_point_centroid":[0.52648,0.11919,0.22005],"force_p95":0.06913,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08885,"mean_force":0.04652,"phase_index":4.0,"phase_name":"approach_2","phase_type":"approach","tcp_position_centroid":[0.52641,0.13832,0.21862]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4955.0,"contact_point_centroid":[0.48875,0.06232,0.02783],"force_p95":0.07649,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08854,"mean_force":0.04552,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.48809,0.04316,0.026]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":12049.0,"contact_point_centroid":[0.52728,0.15966,0.22022],"force_p95":0.07026,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08165,"mean_force":0.0496,"phase_index":4.0,"phase_name":"approach_2","phase_type":"approach","tcp_position_centroid":[0.52711,0.14046,0.219]}],"total_contact_groups":12},"final_pose_error":0.01993,"key_states":{"actual_goal_position":[0.56442,0.24486,0.14677],"final_object_position":[0.57159,0.23919,0.15292],"final_tcp_position":[0.5593,0.23911,0.16515],"realised_goal_position":[0.56442,0.24486,0.14677],"realised_object_initial_position":[0.50118,0.04505,0.03]},"phases":[{"n_steps":275.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.03],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.23992,"object_z_max":0.03,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"pre_grasp","tcp_end":[0.49778,0.03848,0.14809],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.12229,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":392.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"grasp_obj","tcp_end":[0.49619,0.04389,0.03458],"tcp_start":[0.49778,0.03848,0.14809],"tcp_to_object_dist_end":0.00998,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50108,0.04319,0.02543],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.24374,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","subtask_id":"grasp_obj","tcp_end":[0.48806,0.04315,0.02596],"tcp_start":[0.49619,0.04389,0.03458],"tcp_to_object_dist_end":0.01304,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":636.0,"n_steps_budget":1000.0,"object_pos_end":[0.50825,0.04293,0.19908],"object_pos_start":[0.50108,0.04319,0.02543],"object_to_goal_dist_end":0.21603,"object_to_goal_dist_start":0.24374,"object_z_max":0.19881,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","subtask_id":"lift_obj","tcp_end":[0.49694,0.04288,0.20442],"tcp_start":[0.48806,0.04315,0.02596],"tcp_to_object_dist_end":0.01251,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":597.0,"n_steps_budget":1000.0,"object_pos_end":[0.56712,0.22965,0.22573],"object_pos_start":[0.50825,0.04293,0.19908],"object_to_goal_dist_end":0.08045,"object_to_goal_dist_start":0.21603,"object_z_max":0.22569,"phase_name":"approach_2","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"place_obj","tcp_end":[0.55705,0.22971,0.2362],"tcp_start":[0.49694,0.04288,0.20442],"tcp_to_object_dist_end":0.01452,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":139.0,"n_steps_budget":1000.0,"object_pos_end":[0.57159,0.23919,0.15292],"object_pos_start":[0.56712,0.22965,0.22573],"object_to_goal_dist_end":0.01102,"object_to_goal_dist_start":0.08045,"object_z_max":0.22573,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"place_obj","tcp_end":[0.5593,0.23911,0.16515],"tcp_start":[0.55705,0.22971,0.2362],"tcp_to_object_dist_end":0.01735,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.54822,"average_solve_count":197.0,"average_success_count":197.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.15445,"approach_2.transport_speed":0.15521,"descend_1.descend_speed":0.04104,"descend_1.grasp_offset_z":0.00491,"descend_2.place_speed":0.05585,"lift_1.lift_height":0.12749,"lift_1.lift_speed":0.05722},"optimized_scores":{"best_composite_score":0.50832,"best_fitness_score":0.97832,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":82.0,"contact_point_centroid":[0.47355,-0.01934,-0.00138],"force_p95":0.49202,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55021,"mean_force":0.14427,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46316,-0.0195,0.03336]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":7244.0,"contact_point_centroid":[0.46573,-0.03859,0.08297],"force_p95":0.07523,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27551,"mean_force":0.05126,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.4658,-0.01946,0.08095]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6788.0,"contact_point_centroid":[0.46577,-0.00028,0.08301],"force_p95":0.07802,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27526,"mean_force":0.05387,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46577,-0.01946,0.08048]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1193.0,"contact_point_centroid":[0.62943,0.17075,0.24558],"force_p95":0.16367,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27447,"mean_force":0.09705,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.62339,0.15274,0.24727]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":845.0,"contact_point_centroid":[0.62861,0.13417,0.24726],"force_p95":0.20635,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26291,"mean_force":0.12499,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.62323,0.15255,0.24971]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":11251.0,"contact_point_centroid":[0.54557,0.08001,0.20041],"force_p95":0.10543,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20297,"mean_force":0.07122,"phase_index":4.0,"phase_name":"approach_2","phase_type":"approach","tcp_position_centroid":[0.54123,0.06142,0.19909]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":9394.0,"contact_point_centroid":[0.54339,0.04035,0.19903],"force_p95":0.12113,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19679,"mean_force":0.08286,"phase_index":4.0,"phase_name":"approach_2","phase_type":"approach","tcp_position_centroid":[0.53921,0.05919,0.19719]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.47616,-0.02004,-0.00205],"force_p95":0.13931,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.18972,"mean_force":0.12715,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46513,-0.01955,0.03322]},{"body_a":"world","body_b":"grasp_target","contact_count":1080.0,"contact_point_centroid":[0.47616,-0.02015,-0.00188],"force_p95":0.1365,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12308,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.4882,-0.00823,0.22629]},{"body_a":"world","body_b":"grasp_target","contact_count":1524.0,"contact_point_centroid":[0.47616,-0.02015,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.47274,-0.01837,0.0939]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5066.0,"contact_point_centroid":[0.46373,-0.00027,0.03477],"force_p95":0.06615,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09777,"mean_force":0.04294,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46402,-0.01952,0.03212]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5406.0,"contact_point_centroid":[0.4636,-0.03878,0.03426],"force_p95":0.06527,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08076,"mean_force":0.04116,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46402,-0.01952,0.03212]}],"total_contact_groups":12},"final_pose_error":0.0197,"key_states":{"actual_goal_position":[0.63142,0.15919,0.19002],"final_object_position":[0.63328,0.15864,0.17498],"final_tcp_position":[0.62587,0.15569,0.20858],"realised_goal_position":[0.63142,0.15919,0.19002],"realised_object_initial_position":[0.47616,-0.02015,0.03]},"phases":[{"n_steps":271.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.03],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28614,"object_z_max":0.03,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"pre_grasp","tcp_end":[0.47655,-0.01714,0.14942],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.12344,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":381.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"grasp_obj","tcp_end":[0.4718,-0.01969,0.03989],"tcp_start":[0.47655,-0.01714,0.14942],"tcp_to_object_dist_end":0.01455,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.47605,-0.01959,0.02579],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28822,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","subtask_id":"grasp_obj","tcp_end":[0.46399,-0.01952,0.03209],"tcp_start":[0.4718,-0.01969,0.03989],"tcp_to_object_dist_end":0.0136,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":348.0,"n_steps_budget":1000.0,"object_pos_end":[0.48204,-0.0195,0.12484],"object_pos_start":[0.47605,-0.01959,0.02579],"object_to_goal_dist_end":0.24186,"object_to_goal_dist_start":0.28822,"object_z_max":0.12457,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","subtask_id":"lift_obj","tcp_end":[0.47094,-0.01948,0.13395],"tcp_start":[0.46399,-0.01952,0.03209],"tcp_to_object_dist_end":0.01436,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":798.0,"n_steps_budget":1000.0,"object_pos_end":[0.62908,0.15099,0.24653],"object_pos_start":[0.48204,-0.0195,0.12484],"object_to_goal_dist_end":0.05716,"object_to_goal_dist_start":0.24186,"object_z_max":0.24642,"phase_name":"approach_2","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"place_obj","tcp_end":[0.62208,0.15057,0.27467],"tcp_start":[0.47094,-0.01948,0.13395],"tcp_to_object_dist_end":0.029,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":124.0,"n_steps_budget":1000.0,"object_pos_end":[0.63328,0.15864,0.17498],"object_pos_start":[0.62908,0.15099,0.24653],"object_to_goal_dist_end":0.01516,"object_to_goal_dist_start":0.05716,"object_z_max":0.24654,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"place_obj","tcp_end":[0.62587,0.15569,0.20858],"tcp_start":[0.62208,0.15057,0.27467],"tcp_to_object_dist_end":0.03453,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.96221,"average_solve_count":344.0,"average_success_count":344.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.05018,"approach_2.transport_speed":0.12459,"descend_1.descend_speed":0.09489,"descend_1.grasp_offset_z":0.0,"descend_2.place_speed":0.02496,"lift_1.lift_height":0.16995,"lift_1.lift_speed":0.02473},"optimized_scores":{"best_composite_score":0.51144,"best_fitness_score":0.98144,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":95.0,"contact_point_centroid":[0.45504,-0.02523,-0.00153],"force_p95":0.50852,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54738,"mean_force":0.23775,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44616,-0.02544,0.02875]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":10196.0,"contact_point_centroid":[0.44908,-0.04452,0.10243],"force_p95":0.07489,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23254,"mean_force":0.05159,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44887,-0.02537,0.10058]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":10198.0,"contact_point_centroid":[0.44906,-0.00622,0.10248],"force_p95":0.07358,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21962,"mean_force":0.05127,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44887,-0.02537,0.10057]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.45857,-0.02616,-0.00207],"force_p95":0.14415,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.21364,"mean_force":0.12854,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44818,-0.02552,0.02893]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3084.0,"contact_point_centroid":[0.61974,0.21816,0.17259],"force_p95":0.07224,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16838,"mean_force":0.04604,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.62004,0.19906,0.17034]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2580.0,"contact_point_centroid":[0.61918,0.17983,0.17303],"force_p95":0.08057,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15225,"mean_force":0.05342,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.62,0.19899,0.17105]},{"body_a":"world","body_b":"grasp_target","contact_count":1232.0,"contact_point_centroid":[0.45856,-0.02632,-0.00189],"force_p95":0.13606,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12302,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48088,-0.01074,0.22645]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5286.0,"contact_point_centroid":[0.44653,-0.00623,0.02962],"force_p95":0.06558,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13034,"mean_force":0.04114,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.4471,-0.02548,0.02791]},{"body_a":"world","body_b":"grasp_target","contact_count":1480.0,"contact_point_centroid":[0.45856,-0.02632,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.4568,-0.02403,0.09162]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":16977.0,"contact_point_centroid":[0.53654,0.10662,0.19085],"force_p95":0.07403,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11422,"mean_force":0.04709,"phase_index":4.0,"phase_name":"approach_2","phase_type":"approach","tcp_position_centroid":[0.53674,0.08759,0.18864]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":14748.0,"contact_point_centroid":[0.53344,0.06467,0.19016],"force_p95":0.08098,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11187,"mean_force":0.05404,"phase_index":4.0,"phase_name":"approach_2","phase_type":"approach","tcp_position_centroid":[0.53401,0.08391,0.18816]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5436.0,"contact_point_centroid":[0.44653,-0.04477,0.02946],"force_p95":0.06579,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08134,"mean_force":0.04117,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44711,-0.02548,0.02791]}],"total_contact_groups":12},"final_pose_error":0.0199,"key_states":{"actual_goal_position":[0.63013,0.20822,0.11412],"final_object_position":[0.62656,0.2034,0.11514],"final_tcp_position":[0.62316,0.20325,0.13209],"realised_goal_position":[0.63013,0.20822,0.11412],"realised_object_initial_position":[0.45856,-0.02632,0.03]},"phases":[{"n_steps":309.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.03],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30252,"object_z_max":0.03,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"pre_grasp","tcp_end":[0.46144,-0.02245,0.1493],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.12338,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":370.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"grasp_obj","tcp_end":[0.4547,-0.02574,0.03514],"tcp_start":[0.46144,-0.02245,0.1493],"tcp_to_object_dist_end":0.00992,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.45845,-0.02556,0.02574],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30321,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","subtask_id":"grasp_obj","tcp_end":[0.44708,-0.02547,0.02788],"tcp_start":[0.4547,-0.02574,0.03514],"tcp_to_object_dist_end":0.01157,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":509.0,"n_steps_budget":1000.0,"object_pos_end":[0.46381,-0.02542,0.17123],"object_pos_start":[0.45845,-0.02556,0.02574],"object_to_goal_dist_end":0.29242,"object_to_goal_dist_start":0.30321,"object_z_max":0.17095,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","subtask_id":"lift_obj","tcp_end":[0.45413,-0.0254,0.17618],"tcp_start":[0.44708,-0.02547,0.02788],"tcp_to_object_dist_end":0.01087,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":793.0,"n_steps_budget":1000.0,"object_pos_end":[0.61949,0.19584,0.18784],"object_pos_start":[0.46381,-0.02542,0.17123],"object_to_goal_dist_end":0.07551,"object_to_goal_dist_start":0.29242,"object_z_max":0.18784,"phase_name":"approach_2","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"place_obj","tcp_end":[0.61858,0.19568,0.20399],"tcp_start":[0.45413,-0.0254,0.17618],"tcp_to_object_dist_end":0.01617,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":142.0,"n_steps_budget":1000.0,"object_pos_end":[0.62656,0.2034,0.11514],"object_pos_start":[0.61949,0.19584,0.18784],"object_to_goal_dist_end":0.00608,"object_to_goal_dist_start":0.07551,"object_z_max":0.18784,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"place_obj","tcp_end":[0.62316,0.20325,0.13209],"tcp_start":[0.61858,0.19568,0.20399],"tcp_to_object_dist_end":0.01728,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```