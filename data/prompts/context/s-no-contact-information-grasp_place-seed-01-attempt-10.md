## Search State

- **Seed**: 1
- **Iteration**: 11 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 10 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 7 | 0.5103 | 1.00 | ✅ accepted |
| 9 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | impedance_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 7 | 0.2020 | 0.45 | ✅ accepted |
| 8 | rotate → align → push → align → lift | impedance_motion | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | impedance_control | position_control | position_control | position_control | position_control | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 3 | -0.0465 | 0.16 | ❌ rejected |
| 7 | rotate → align → push → align → lift | impedance_motion | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | impedance_control | position_control | position_control | position_control | position_control | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 3 | -0.0465 | 0.16 | ❌ rejected |
| 6 | approach → descend → grasp → lift → approach → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | — | position_control | force_threshold_switch | position_control | position_control | position_control | position_control | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | time_limit | 8 | -0.1857 | 0.16 | ❌ rejected |

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
| approach_1 | 1.00 | 0.1567 |
| descend_1 | 1.00 | 0.1138 |
| grasp_1 | 1.00 | 0.0112 |
| lift_1 | 1.00 | 0.1297 |
| approach_2 | 1.00 | 0.2493 |
| descend_2 | 1.00 | 0.0691 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end |
| --- | --- | --- | --- | --- | --- |
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.479, -0.000, 0.149) | (0.479, -0.000, 0.030)→(0.479, -0.000, 0.026) | 0.276→0.278 |
| descend_1 | descend | 1.00 / step_budget | (0.479, -0.000, 0.149)→(0.474, -0.001, 0.035) | (0.479, -0.000, 0.026)→(0.479, -0.000, 0.026) | 0.278→0.278 |
| grasp_1 | grasp | 1.00 / step_budget | (0.474, -0.001, 0.035)→(0.466, -0.001, 0.027) | (0.479, -0.000, 0.026)→(0.479, -0.001, 0.026) | 0.278→0.278 |
| lift_1 | lift | 1.00 / step_budget | (0.466, -0.001, 0.027)→(0.474, -0.001, 0.157) | (0.479, -0.001, 0.026)→(0.485, -0.001, 0.152) | 0.278→0.245 |
| approach_2 | approach | 1.00 / step_budget | (0.474, -0.001, 0.157)→(0.599, 0.193, 0.237) | (0.485, -0.001, 0.152)→(0.606, 0.193, 0.218) | 0.245→0.069 |
| descend_2 | descend | 1.00 / step_budget | (0.599, 0.193, 0.237)→(0.603, 0.199, 0.169) | (0.606, 0.193, 0.218)→(0.609, 0.199, 0.148) | 0.069→0.006 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.729
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 1.000
- phase_score: 0.610
- phase_breakdown.pre_grasp_score: 0.674
- phase_breakdown.place_obj_score: 0.673
- phase_breakdown.grasp_obj_score: 0.504
- phase_breakdown.lift_obj_score: 0.611
- grasp_place_fitness: 0.981

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.981
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 1.000
- **Median Q (composite search score)**: 0.510
- **K-run variance**: 0.0000
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Parameters at lower bound**: lift_1.lift_speed, descend_1.grasp_offset_z
- **Final σ (mean)**: 0.518


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.30213,"average_solve_count":235.0,"average_success_count":235.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.16713,"approach_2.transport_speed":0.17027,"descend_1.descend_speed":0.06567,"descend_1.grasp_offset_z":3e-05,"descend_2.place_speed":0.0796,"lift_1.lift_height":0.15004,"lift_1.lift_speed":0.02378},"optimized_scores":{"best_composite_score":0.50928,"best_fitness_score":0.97928,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":110.0,"contact_point_centroid":[0.4976,0.04233,-0.00165],"force_p95":0.47251,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.53965,"mean_force":0.21686,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48706,0.04304,0.02684]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50125,0.04462,-0.00217],"force_p95":0.17423,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.26262,"mean_force":0.13627,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.48931,0.04327,0.02717]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":10231.0,"contact_point_centroid":[0.48998,0.06194,0.08997],"force_p95":0.07608,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26004,"mean_force":0.0502,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.4902,0.04282,0.08821]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1536.0,"contact_point_centroid":[0.56214,0.21631,0.20209],"force_p95":0.14284,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25324,"mean_force":0.09466,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.55828,0.23533,0.20143]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":9330.0,"contact_point_centroid":[0.49008,0.02363,0.08924],"force_p95":0.08048,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24113,"mean_force":0.05331,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49007,0.04282,0.0867]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1997.0,"contact_point_centroid":[0.56206,0.25371,0.20045],"force_p95":0.11573,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23926,"mean_force":0.07182,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.55831,0.23547,0.20008]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":7707.0,"contact_point_centroid":[0.52599,0.11004,0.19135],"force_p95":0.1177,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1919,"mean_force":0.07585,"phase_index":4.0,"phase_name":"approach_2","phase_type":"approach","tcp_position_centroid":[0.52277,0.12892,0.18956]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3751.0,"contact_point_centroid":[0.48926,0.02397,0.02899],"force_p95":0.08628,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1499,"mean_force":0.05563,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.48814,0.04316,0.02595]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":9064.0,"contact_point_centroid":[0.52707,0.1504,0.19188],"force_p95":0.10181,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.147,"mean_force":0.06689,"phase_index":4.0,"phase_name":"approach_2","phase_type":"approach","tcp_position_centroid":[0.52369,0.1317,0.19072]},{"body_a":"world","body_b":"grasp_target","contact_count":1116.0,"contact_point_centroid":[0.50118,0.04505,-0.00188],"force_p95":0.13645,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12306,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49839,0.01857,0.22523]},{"body_a":"world","body_b":"grasp_target","contact_count":1508.0,"contact_point_centroid":[0.50118,0.04505,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49556,0.04107,0.09041]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4956.0,"contact_point_centroid":[0.48879,0.06232,0.02779],"force_p95":0.07649,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08859,"mean_force":0.04552,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.48815,0.04316,0.02596]}],"total_contact_groups":12},"final_pose_error":0.01999,"key_states":{"actual_goal_position":[0.56442,0.24486,0.14677],"final_object_position":[0.5666,0.23873,0.14635],"final_tcp_position":[0.55956,0.23957,0.16543],"realised_goal_position":[0.56442,0.24486,0.14677],"realised_object_initial_position":[0.50118,0.04505,0.03]},"phases":[{"n_steps":280.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.03],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.23992,"object_z_max":0.03,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"pre_grasp","tcp_end":[0.4978,0.03849,0.1481],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.1223,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":377.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"grasp_obj","tcp_end":[0.49626,0.04389,0.03456],"tcp_start":[0.4978,0.03849,0.1481],"tcp_to_object_dist_end":0.00992,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50108,0.04318,0.02543],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.24374,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","subtask_id":"grasp_obj","tcp_end":[0.48811,0.04315,0.02592],"tcp_start":[0.49626,0.04389,0.03456],"tcp_to_object_dist_end":0.01298,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":483.0,"n_steps_budget":1000.0,"object_pos_end":[0.50762,0.04273,0.15224],"object_pos_start":[0.50108,0.04318,0.02543],"object_to_goal_dist_end":0.21003,"object_to_goal_dist_start":0.24374,"object_z_max":0.15198,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","subtask_id":"lift_obj","tcp_end":[0.49621,0.04284,0.15617],"tcp_start":[0.48811,0.04315,0.02592],"tcp_to_object_dist_end":0.01206,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":591.0,"n_steps_budget":1000.0,"object_pos_end":[0.56947,0.23146,0.21648],"object_pos_start":[0.50762,0.04273,0.15224],"object_to_goal_dist_end":0.07116,"object_to_goal_dist_start":0.21003,"object_z_max":0.21639,"phase_name":"approach_2","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"place_obj","tcp_end":[0.55773,0.23149,0.23388],"tcp_start":[0.49621,0.04284,0.15617],"tcp_to_object_dist_end":0.02099,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":128.0,"n_steps_budget":1000.0,"object_pos_end":[0.5666,0.23873,0.14635],"object_pos_start":[0.56947,0.23146,0.21648],"object_to_goal_dist_end":0.00653,"object_to_goal_dist_start":0.07116,"object_z_max":0.21649,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"place_obj","tcp_end":[0.55956,0.23957,0.16543],"tcp_start":[0.55773,0.23149,0.23388],"tcp_to_object_dist_end":0.02036,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.98062,"average_solve_count":258.0,"average_success_count":258.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.1658,"approach_2.transport_speed":0.1999,"descend_1.descend_speed":0.09299,"descend_1.grasp_offset_z":0.00107,"descend_2.place_speed":0.01334,"lift_1.lift_height":0.15334,"lift_1.lift_speed":0.05225},"optimized_scores":{"best_composite_score":0.51046,"best_fitness_score":0.98046,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":82.0,"contact_point_centroid":[0.47348,-0.01931,-0.00141],"force_p95":0.52137,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.60834,"mean_force":0.17147,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46314,-0.01952,0.0293]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":9072.0,"contact_point_centroid":[0.46586,-0.0386,0.09288],"force_p95":0.07571,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27927,"mean_force":0.05187,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46585,-0.01947,0.0908]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8696.0,"contact_point_centroid":[0.46598,-0.00032,0.0938],"force_p95":0.07746,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27747,"mean_force":0.05354,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.4659,-0.01947,0.09136]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2194.0,"contact_point_centroid":[0.62552,0.17085,0.24874],"force_p95":0.08997,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20944,"mean_force":0.06196,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.62264,0.15216,0.24837]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1772.0,"contact_point_centroid":[0.62577,0.13329,0.24838],"force_p95":0.10996,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19885,"mean_force":0.07305,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.62269,0.15222,0.24761]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.47616,-0.02002,-0.00205],"force_p95":0.1386,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.18962,"mean_force":0.12703,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.4652,-0.01957,0.02928]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":12027.0,"contact_point_centroid":[0.54736,0.04724,0.21913],"force_p95":0.09093,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15636,"mean_force":0.06,"phase_index":4.0,"phase_name":"approach_2","phase_type":"approach","tcp_position_centroid":[0.54618,0.06639,0.21675]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":14066.0,"contact_point_centroid":[0.54872,0.08718,0.21979],"force_p95":0.07761,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14821,"mean_force":0.05194,"phase_index":4.0,"phase_name":"approach_2","phase_type":"approach","tcp_position_centroid":[0.5478,0.06823,0.218]},{"body_a":"world","body_b":"grasp_target","contact_count":1068.0,"contact_point_centroid":[0.47616,-0.02015,-0.00188],"force_p95":0.1365,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12308,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48819,-0.00824,0.22625]},{"body_a":"world","body_b":"grasp_target","contact_count":1452.0,"contact_point_centroid":[0.47616,-0.02015,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.47289,-0.01839,0.09185]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5063.0,"contact_point_centroid":[0.46378,-0.00032,0.03077],"force_p95":0.06601,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09423,"mean_force":0.04287,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46408,-0.01954,0.02818]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5200.0,"contact_point_centroid":[0.46395,-0.0388,0.03018],"force_p95":0.06663,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08152,"mean_force":0.04275,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46409,-0.01954,0.02819]}],"total_contact_groups":12},"final_pose_error":0.01997,"key_states":{"actual_goal_position":[0.63142,0.15919,0.19002],"final_object_position":[0.63466,0.15573,0.1853],"final_tcp_position":[0.6256,0.15549,0.20876],"realised_goal_position":[0.63142,0.15919,0.19002],"realised_object_initial_position":[0.47616,-0.02015,0.03]},"phases":[{"n_steps":268.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.03],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28614,"object_z_max":0.03,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"pre_grasp","tcp_end":[0.47652,-0.01715,0.14931],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.12333,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":363.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"grasp_obj","tcp_end":[0.4719,-0.01971,0.03595],"tcp_start":[0.47652,-0.01715,0.14931],"tcp_to_object_dist_end":0.01081,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.47603,-0.01959,0.0258],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28823,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","subtask_id":"grasp_obj","tcp_end":[0.46406,-0.01954,0.02815],"tcp_start":[0.4719,-0.01971,0.03595],"tcp_to_object_dist_end":0.01221,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":448.0,"n_steps_budget":1000.0,"object_pos_end":[0.48278,-0.01949,0.15381],"object_pos_start":[0.47603,-0.01959,0.0258],"object_to_goal_dist_end":0.23523,"object_to_goal_dist_start":0.28823,"object_z_max":0.15353,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","subtask_id":"lift_obj","tcp_end":[0.47141,-0.01948,0.15988],"tcp_start":[0.46406,-0.01954,0.02815],"tcp_to_object_dist_end":0.01289,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":711.0,"n_steps_budget":1000.0,"object_pos_end":[0.62851,0.15043,0.25338],"object_pos_start":[0.48278,-0.01949,0.15381],"object_to_goal_dist_end":0.06403,"object_to_goal_dist_start":0.23523,"object_z_max":0.25329,"phase_name":"approach_2","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"place_obj","tcp_end":[0.62163,0.1501,0.27539],"tcp_start":[0.47141,-0.01948,0.15988],"tcp_to_object_dist_end":0.02307,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":141.0,"n_steps_budget":1000.0,"object_pos_end":[0.63466,0.15573,0.1853],"object_pos_start":[0.62851,0.15043,0.25338],"object_to_goal_dist_end":0.00668,"object_to_goal_dist_start":0.06403,"object_z_max":0.25338,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"place_obj","tcp_end":[0.6256,0.15549,0.20876],"tcp_start":[0.62163,0.1501,0.27539],"tcp_to_object_dist_end":0.02515,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.13475,"average_solve_count":282.0,"average_success_count":282.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.07729,"approach_2.transport_speed":0.13409,"descend_1.descend_speed":0.06915,"descend_1.grasp_offset_z":0.0,"descend_2.place_speed":0.05846,"lift_1.lift_height":0.14769,"lift_1.lift_speed":0.02},"optimized_scores":{"best_composite_score":0.5113,"best_fitness_score":0.9813,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":101.0,"contact_point_centroid":[0.45519,-0.0252,-0.00155],"force_p95":0.45969,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.52684,"mean_force":0.23069,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44602,-0.02544,0.02854]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8840.0,"contact_point_centroid":[0.44889,-0.04449,0.09101],"force_p95":0.07532,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23216,"mean_force":0.05176,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44869,-0.02535,0.08916]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8836.0,"contact_point_centroid":[0.44888,-0.0062,0.09111],"force_p95":0.07344,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2288,"mean_force":0.05147,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44869,-0.02535,0.08919]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.45857,-0.02613,-0.00207],"force_p95":0.14425,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.21371,"mean_force":0.12853,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44806,-0.02551,0.02877]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2820.0,"contact_point_centroid":[0.62048,0.21853,0.17153],"force_p95":0.07991,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18896,"mean_force":0.05012,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.62044,0.19947,0.16963]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2276.0,"contact_point_centroid":[0.61996,0.18027,0.17157],"force_p95":0.08585,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16067,"mean_force":0.05902,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.62044,0.19948,0.16956]},{"body_a":"world","body_b":"grasp_target","contact_count":1176.0,"contact_point_centroid":[0.45856,-0.02632,-0.00189],"force_p95":0.13644,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12304,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48072,-0.01078,0.22611]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4808.0,"contact_point_centroid":[0.44696,-0.00624,0.03002],"force_p95":0.0686,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13043,"mean_force":0.04495,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44698,-0.02547,0.02776]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":13912.0,"contact_point_centroid":[0.53744,0.06886,0.17976],"force_p95":0.09023,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12848,"mean_force":0.06056,"phase_index":4.0,"phase_name":"approach_2","phase_type":"approach","tcp_position_centroid":[0.5368,0.08809,0.17747]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":17226.0,"contact_point_centroid":[0.5371,0.10722,0.17926],"force_p95":0.07884,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12473,"mean_force":0.04868,"phase_index":4.0,"phase_name":"approach_2","phase_type":"approach","tcp_position_centroid":[0.53697,0.08831,0.17751]},{"body_a":"world","body_b":"grasp_target","contact_count":1548.0,"contact_point_centroid":[0.45856,-0.02632,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.45663,-0.02404,0.09135]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5436.0,"contact_point_centroid":[0.44643,-0.04472,0.0294],"force_p95":0.06563,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08163,"mean_force":0.04114,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44698,-0.02547,0.02776]}],"total_contact_groups":12},"final_pose_error":0.01979,"key_states":{"actual_goal_position":[0.63013,0.20822,0.11412],"final_object_position":[0.62719,0.20372,0.1134],"final_tcp_position":[0.62329,0.20339,0.13205],"realised_goal_position":[0.63013,0.20822,0.11412],"realised_object_initial_position":[0.45856,-0.02632,0.03]},"phases":[{"n_steps":295.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.03],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30252,"object_z_max":0.03,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"pre_grasp","tcp_end":[0.46129,-0.02246,0.14912],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.12319,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":387.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"grasp_obj","tcp_end":[0.45458,-0.02574,0.03498],"tcp_start":[0.46129,-0.02246,0.14912],"tcp_to_object_dist_end":0.00982,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.45845,-0.02551,0.02574],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30317,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","subtask_id":"grasp_obj","tcp_end":[0.44695,-0.02547,0.02773],"tcp_start":[0.45458,-0.02574,0.03498],"tcp_to_object_dist_end":0.01166,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":441.0,"n_steps_budget":1000.0,"object_pos_end":[0.46368,-0.02538,0.14986],"object_pos_start":[0.45845,-0.02551,0.02574],"object_to_goal_dist_end":0.28905,"object_to_goal_dist_start":0.30317,"object_z_max":0.14958,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","subtask_id":"lift_obj","tcp_end":[0.45383,-0.02535,0.15418],"tcp_start":[0.44695,-0.02547,0.02773],"tcp_to_object_dist_end":0.01076,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":817.0,"n_steps_budget":1000.0,"object_pos_end":[0.62098,0.1964,0.1851],"object_pos_start":[0.46368,-0.02538,0.14986],"object_to_goal_dist_end":0.07254,"object_to_goal_dist_start":0.28905,"object_z_max":0.18508,"phase_name":"approach_2","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"place_obj","tcp_end":[0.61887,0.19614,0.20291],"tcp_start":[0.45383,-0.02535,0.15418],"tcp_to_object_dist_end":0.01794,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":133.0,"n_steps_budget":1000.0,"object_pos_end":[0.62719,0.20372,0.1134],"object_pos_start":[0.62098,0.1964,0.1851],"object_to_goal_dist_end":0.00542,"object_to_goal_dist_start":0.07254,"object_z_max":0.1851,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"place_obj","tcp_end":[0.62329,0.20339,0.13205],"tcp_start":[0.61887,0.19614,0.20291],"tcp_to_object_dist_end":0.01906,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```