## Search State

- **Seed**: 1
- **Iteration**: 10 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 9 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | impedance_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 7 | 0.2020 | 0.45 | ✅ accepted |
| 8 | rotate → align → push → align → lift | impedance_motion | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | impedance_control | position_control | position_control | position_control | position_control | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 3 | -0.0465 | 0.16 | ❌ rejected |
| 7 | rotate → align → push → align → lift | impedance_motion | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | impedance_control | position_control | position_control | position_control | position_control | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 3 | -0.0465 | 0.16 | ❌ rejected |
| 6 | approach → descend → grasp → lift → approach → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | — | position_control | force_threshold_switch | position_control | position_control | position_control | position_control | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | time_limit | 8 | -0.1857 | 0.16 | ❌ rejected |
| 5 | rotate → align → push → align → lift | impedance_motion | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | impedance_control | position_control | position_control | position_control | position_control | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 3 | -0.0465 | 0.16 | ❌ rejected |

**Proposal policy**: task_score is 0.45 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.202) — your mutation base

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
    tolerance: 0.01
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
    threshold: 0.01
    on_failure: retry
  retries:
    max_attempts: 1
    strategy: reduce_speed
  subtask_id: place_obj
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
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - place_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=descend_goal_tol, when=after_phase, predicate=pose_within_tolerance, on_failure=retry, threshold=0.01
  - retries: max_attempts=1, strategy=reduce_speed
- **release_1** (`release`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings: none

## Design Metrics

- **Composite score**: 0.202
- **task_score** (E): 0.447
- **fitness_score**: 0.702  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Complexity Penalty**: 0.500

## Per-Phase Performance

| Phase | Normal Term. Rate | Mean Displacement (m) |
| ------- | ------------------- | ------------------------ |
| approach_1 | 1.00 | 0.1565 |
| descend_1 | 1.00 | 0.1102 |
| grasp_1 | 1.00 | 0.0111 |
| lift_1 | 1.00 | 0.1339 |
| approach_2 | 1.00 | 0.2458 |
| descend_2 | 1.00 | 0.0804 |
| release_1 | 1.00 | 0.0205 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end |
| --- | --- | --- | --- | --- | --- |
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.479, -0.000, 0.149) | (0.479, -0.000, 0.030)→(0.479, -0.000, 0.026) | 0.276→0.278 |
| descend_1 | descend | 1.00 / step_budget | (0.479, -0.000, 0.149)→(0.474, -0.001, 0.039) | (0.479, -0.000, 0.026)→(0.479, -0.000, 0.026) | 0.278→0.278 |
| grasp_1 | grasp | 1.00 / step_budget | (0.474, -0.001, 0.039)→(0.466, -0.001, 0.031) | (0.479, -0.000, 0.026)→(0.479, -0.001, 0.026) | 0.278→0.278 |
| lift_1 | lift | 1.00 / step_budget | (0.466, -0.001, 0.031)→(0.474, -0.001, 0.165) | (0.479, -0.001, 0.026)→(0.484, -0.001, 0.157) | 0.278→0.244 |
| approach_2 | approach | 1.00 / step_budget | (0.474, -0.001, 0.165)→(0.599, 0.193, 0.237) | (0.484, -0.001, 0.157)→(0.605, 0.193, 0.221) | 0.244→0.072 |
| descend_2 | descend | 1.00 / step_budget | (0.599, 0.193, 0.237)→(0.603, 0.201, 0.158) | (0.605, 0.193, 0.221)→(0.608, 0.200, 0.139) | 0.072→0.012 |
| release_1 | release | 1.00 / step_budget | (0.603, 0.201, 0.158)→(0.597, 0.198, 0.177) | (0.608, 0.200, 0.139)→(0.597, 0.197, 0.027) | 0.012→0.124 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.564
- phase_score: 0.598
- phase_breakdown.pre_grasp_score: 0.674
- phase_breakdown.place_obj_score: 0.559
- phase_breakdown.grasp_obj_score: 0.579
- phase_breakdown.lift_obj_score: 0.610
- grasp_place_fitness: 0.759

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.759
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.564
- **Median Q (composite search score)**: 0.201
- **K-run variance**: 0.0021
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Parameters at lower bound**: descend_1.grasp_offset_z
- **Final σ (mean)**: 0.392


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.96815,"average_solve_count":314.0,"average_success_count":314.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.0932,"approach_2.transport_speed":0.05546,"descend_1.descend_speed":0.06113,"descend_1.grasp_offset_z":0.00506,"descend_2.place_speed":0.06485,"lift_1.lift_height":0.14422,"lift_1.lift_speed":0.02144},"optimized_scores":{"best_composite_score":0.20101,"best_fitness_score":0.70101,"best_task_score":0.44676},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":142.0,"contact_point_centroid":[0.55362,0.24376,-0.00869],"force_p95":1.23746,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.49164,"mean_force":0.51015,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.55369,0.23825,0.16441]},{"body_a":"world","body_b":"grasp_target","contact_count":113.0,"contact_point_centroid":[0.498,0.04266,-0.00167],"force_p95":0.41649,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.47598,"mean_force":0.19416,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48715,0.04302,0.0319]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":9567.0,"contact_point_centroid":[0.4899,0.06198,0.08971],"force_p95":0.07608,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25346,"mean_force":0.04985,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49025,0.04284,0.08802]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50125,0.04469,-0.00217],"force_p95":0.17225,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24929,"mean_force":0.13558,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.48939,0.04324,0.03228]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8824.0,"contact_point_centroid":[0.49004,0.02364,0.0891],"force_p95":0.07981,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23567,"mean_force":0.05234,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49012,0.04284,0.08668]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3788.0,"contact_point_centroid":[0.48926,0.02394,0.03408],"force_p95":0.08619,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15436,"mean_force":0.05524,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.48823,0.04314,0.03106]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1323.0,"contact_point_centroid":[0.55735,0.22093,0.15295],"force_p95":0.06534,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15305,"mean_force":0.04035,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.55757,0.24012,0.15041]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1347.0,"contact_point_centroid":[0.55733,0.25939,0.15223],"force_p95":0.06716,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14946,"mean_force":0.04035,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.55755,0.2401,0.15037]},{"body_a":"world","body_b":"grasp_target","contact_count":1196.0,"contact_point_centroid":[0.50118,0.04505,-0.00189],"force_p95":0.13615,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12304,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49841,0.01853,0.2254]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4874.0,"contact_point_centroid":[0.55789,0.25502,0.19518],"force_p95":0.07544,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13574,"mean_force":0.05001,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.55771,0.23588,0.19359]},{"body_a":"world","body_b":"grasp_target","contact_count":1460.0,"contact_point_centroid":[0.50118,0.04505,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49566,0.04106,0.09308]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4920.0,"contact_point_centroid":[0.55785,0.21655,0.19688],"force_p95":0.07344,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12039,"mean_force":0.04937,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.55766,0.23572,0.19502]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":15858.0,"contact_point_centroid":[0.526,0.12084,0.19272],"force_p95":0.06815,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08773,"mean_force":0.04548,"phase_index":4.0,"phase_name":"approach_2","phase_type":"approach","tcp_position_centroid":[0.52623,0.13999,0.19112]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5007.0,"contact_point_centroid":[0.48877,0.06229,0.03301],"force_p95":0.07643,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08438,"mean_force":0.04496,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.48824,0.04314,0.03107]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":14943.0,"contact_point_centroid":[0.52568,0.15793,0.19171],"force_p95":0.06895,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08117,"mean_force":0.04838,"phase_index":4.0,"phase_name":"approach_2","phase_type":"approach","tcp_position_centroid":[0.5258,0.13872,0.19054]}],"total_contact_groups":15},"final_pose_error":0.00977,"key_states":{"actual_goal_position":[0.56442,0.24486,0.14677],"final_object_position":[0.55412,0.23389,0.02686],"final_tcp_position":[0.55955,0.24089,0.15426],"realised_goal_position":[0.56442,0.24486,0.14677],"realised_object_initial_position":[0.50118,0.04505,0.03]},"phases":[{"n_steps":300.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.03],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.23992,"object_z_max":0.03,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"pre_grasp","tcp_end":[0.49792,0.0385,0.1482],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.1224,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":365.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"grasp_obj","tcp_end":[0.49627,0.04386,0.03966],"tcp_start":[0.49792,0.0385,0.1482],"tcp_to_object_dist_end":0.01455,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50111,0.04326,0.02544],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.24367,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","subtask_id":"grasp_obj","tcp_end":[0.4882,0.04313,0.03103],"tcp_start":[0.49627,0.04386,0.03966],"tcp_to_object_dist_end":0.01406,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":446.0,"n_steps_budget":1000.0,"object_pos_end":[0.50676,0.04284,0.14203],"object_pos_start":[0.50111,0.04326,0.02544],"object_to_goal_dist_end":0.21015,"object_to_goal_dist_start":0.24367,"object_z_max":0.14177,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","subtask_id":"lift_obj","tcp_end":[0.49612,0.0429,0.15054],"tcp_start":[0.4882,0.04313,0.03103],"tcp_to_object_dist_end":0.01363,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":724.0,"n_steps_budget":1000.0,"object_pos_end":[0.56579,0.23175,0.21941],"object_pos_start":[0.50676,0.04284,0.14203],"object_to_goal_dist_end":0.07382,"object_to_goal_dist_start":0.21015,"object_z_max":0.21931,"phase_name":"approach_2","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"place_obj","tcp_end":[0.55763,0.23177,0.23338],"tcp_start":[0.49612,0.0429,0.15054],"tcp_to_object_dist_end":0.01618,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":236.0,"n_steps_budget":1000.0,"object_pos_end":[0.56296,0.24042,0.13875],"object_pos_start":[0.56579,0.23175,0.21941],"object_to_goal_dist_end":0.00929,"object_to_goal_dist_start":0.07382,"object_z_max":0.21942,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"place_obj","tcp_end":[0.55955,0.24089,0.15426],"tcp_start":[0.55763,0.23177,0.23338],"tcp_to_object_dist_end":0.01589,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.55412,0.23389,0.02686],"object_pos_start":[0.56296,0.24042,0.13875],"object_to_goal_dist_end":0.12086,"object_to_goal_dist_start":0.00929,"object_z_max":0.13875,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","subtask_id":"place_obj","tcp_end":[0.55361,0.23821,0.17497],"tcp_start":[0.55955,0.24089,0.15426],"tcp_to_object_dist_end":0.14818,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.25448,"average_solve_count":279.0,"average_success_count":279.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.11335,"approach_2.transport_speed":0.19994,"descend_1.descend_speed":0.05005,"descend_1.grasp_offset_z":0.0,"descend_2.place_speed":0.03668,"lift_1.lift_height":0.18297,"lift_1.lift_speed":0.02555},"optimized_scores":{"best_composite_score":0.14635,"best_fitness_score":0.64635,"best_task_score":0.33149},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":178.0,"contact_point_centroid":[0.6111,0.15372,-0.00834],"force_p95":1.38105,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.49394,"mean_force":0.41838,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.62055,0.1547,0.20772]},{"body_a":"world","body_b":"grasp_target","contact_count":92.0,"contact_point_centroid":[0.47275,-0.01933,-0.0015],"force_p95":0.52304,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54452,"mean_force":0.24285,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46304,-0.01952,0.02784]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":11328.0,"contact_point_centroid":[0.46626,-0.0386,0.1095],"force_p95":0.07445,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24252,"mean_force":0.05117,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46612,-0.01946,0.10757]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":11094.0,"contact_point_centroid":[0.46619,-0.00031,0.10818],"force_p95":0.07398,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24049,"mean_force":0.05186,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46601,-0.01946,0.10612]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.47616,-0.02001,-0.00205],"force_p95":0.13867,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.18972,"mean_force":0.12702,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46512,-0.01957,0.02813]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4911.0,"contact_point_centroid":[0.62247,0.1714,0.23898],"force_p95":0.07325,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18612,"mean_force":0.04709,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.62256,0.15239,0.23725]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1202.0,"contact_point_centroid":[0.62493,0.13661,0.19623],"force_p95":0.07362,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16585,"mean_force":0.04399,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.62415,0.15585,0.19315]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1331.0,"contact_point_centroid":[0.6241,0.175,0.19476],"force_p95":0.07392,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1585,"mean_force":0.04188,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.62418,0.15585,0.19321]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3889.0,"contact_point_centroid":[0.62186,0.13313,0.23965],"force_p95":0.0844,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14775,"mean_force":0.05729,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.62252,0.15235,0.23772]},{"body_a":"world","body_b":"grasp_target","contact_count":1128.0,"contact_point_centroid":[0.47616,-0.02015,-0.00188],"force_p95":0.13644,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12306,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48818,-0.00824,0.2262]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":14044.0,"contact_point_centroid":[0.54829,0.08775,0.23563],"force_p95":0.07205,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13519,"mean_force":0.04727,"phase_index":4.0,"phase_name":"approach_2","phase_type":"approach","tcp_position_centroid":[0.54862,0.06871,0.23329]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":12105.0,"contact_point_centroid":[0.54445,0.04573,0.23315],"force_p95":0.08034,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12538,"mean_force":0.05435,"phase_index":4.0,"phase_name":"approach_2","phase_type":"approach","tcp_position_centroid":[0.54531,0.06495,0.23135]},{"body_a":"world","body_b":"grasp_target","contact_count":1592.0,"contact_point_centroid":[0.47616,-0.02015,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.47282,-0.01838,0.09139]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5061.0,"contact_point_centroid":[0.46372,-0.0003,0.0297],"force_p95":0.06599,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09545,"mean_force":0.04293,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.464,-0.01955,0.02703]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5407.0,"contact_point_centroid":[0.46358,-0.0388,0.02919],"force_p95":0.06508,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0818,"mean_force":0.04119,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.464,-0.01955,0.02703]}],"total_contact_groups":15},"final_pose_error":0.00976,"key_states":{"actual_goal_position":[0.63142,0.15919,0.19002],"final_object_position":[0.61896,0.15433,0.02493],"final_tcp_position":[0.62603,0.1563,0.19762],"realised_goal_position":[0.63142,0.15919,0.19002],"realised_object_initial_position":[0.47616,-0.02015,0.03]},"phases":[{"n_steps":283.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.03],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28614,"object_z_max":0.03,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"pre_grasp","tcp_end":[0.47658,-0.01714,0.14946],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.12348,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":398.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"grasp_obj","tcp_end":[0.47179,-0.01971,0.03476],"tcp_start":[0.47658,-0.01714,0.14946],"tcp_to_object_dist_end":0.00979,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.47603,-0.01958,0.02581],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28822,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","subtask_id":"grasp_obj","tcp_end":[0.46397,-0.01954,0.027],"tcp_start":[0.47179,-0.01971,0.03476],"tcp_to_object_dist_end":0.01212,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":560.0,"n_steps_budget":1000.0,"object_pos_end":[0.48223,-0.01928,0.18475],"object_pos_start":[0.47603,-0.01958,0.02581],"object_to_goal_dist_end":0.23268,"object_to_goal_dist_start":0.28822,"object_z_max":0.18447,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","subtask_id":"lift_obj","tcp_end":[0.47181,-0.01947,0.18948],"tcp_start":[0.46397,-0.01954,0.027],"tcp_to_object_dist_end":0.01145,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":652.0,"n_steps_budget":1000.0,"object_pos_end":[0.62445,0.14953,0.25705],"object_pos_start":[0.48223,-0.01928,0.18475],"object_to_goal_dist_end":0.06809,"object_to_goal_dist_start":0.23268,"object_z_max":0.25698,"phase_name":"approach_2","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"place_obj","tcp_end":[0.62088,0.14917,0.27635],"tcp_start":[0.47181,-0.01947,0.18948],"tcp_to_object_dist_end":0.01963,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":228.0,"n_steps_budget":1000.0,"object_pos_end":[0.63044,0.15653,0.17695],"object_pos_start":[0.62445,0.14953,0.25705],"object_to_goal_dist_end":0.01337,"object_to_goal_dist_start":0.06809,"object_z_max":0.25705,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"place_obj","tcp_end":[0.62603,0.1563,0.19762],"tcp_start":[0.62088,0.14917,0.27635],"tcp_to_object_dist_end":0.02114,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.61896,0.15433,0.02493],"object_pos_start":[0.63044,0.15653,0.17695],"object_to_goal_dist_end":0.16562,"object_to_goal_dist_start":0.01337,"object_z_max":0.17695,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","subtask_id":"place_obj","tcp_end":[0.62051,0.15469,0.21655],"tcp_start":[0.62603,0.1563,0.19762],"tcp_to_object_dist_end":0.19162,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.34307,"average_solve_count":274.0,"average_success_count":274.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.14527,"approach_2.transport_speed":0.08771,"descend_1.descend_speed":0.04352,"descend_1.grasp_offset_z":0.00732,"descend_2.place_speed":0.03772,"lift_1.lift_height":0.14779,"lift_1.lift_speed":0.03849},"optimized_scores":{"best_composite_score":0.25858,"best_fitness_score":0.75858,"best_task_score":0.56411},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":173.0,"contact_point_centroid":[0.62044,0.20199,-0.0068],"force_p95":0.94777,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.00014,"mean_force":0.39963,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.617,0.20223,0.12683]},{"body_a":"world","body_b":"grasp_target","contact_count":85.0,"contact_point_centroid":[0.45503,-0.02523,-0.00148],"force_p95":0.48878,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.51202,"mean_force":0.20397,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44626,-0.02541,0.03612]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1042.0,"contact_point_centroid":[0.6223,0.18468,0.11808],"force_p95":0.08754,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27148,"mean_force":0.05312,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.62156,0.20393,0.11614]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8054.0,"contact_point_centroid":[0.44906,-0.04453,0.09526],"force_p95":0.0761,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25905,"mean_force":0.05263,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44885,-0.02538,0.09341]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8054.0,"contact_point_centroid":[0.44904,-0.00622,0.09533],"force_p95":0.07433,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24386,"mean_force":0.05228,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44885,-0.02538,0.09341]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1324.0,"contact_point_centroid":[0.62184,0.22288,0.1172],"force_p95":0.07134,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23288,"mean_force":0.04242,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.62158,0.20394,0.11619]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.45858,-0.0262,-0.00207],"force_p95":0.14452,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.2069,"mean_force":0.12855,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44819,-0.02548,0.03622]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4810.0,"contact_point_centroid":[0.62123,0.21909,0.16398],"force_p95":0.07303,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16913,"mean_force":0.05088,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.62015,0.20008,0.16255]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4081.0,"contact_point_centroid":[0.62143,0.18099,0.16457],"force_p95":0.08427,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16225,"mean_force":0.05881,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.62017,0.2001,0.1622]},{"body_a":"world","body_b":"grasp_target","contact_count":1120.0,"contact_point_centroid":[0.45856,-0.02632,-0.00188],"force_p95":0.13644,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12306,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48086,-0.01082,0.22594]},{"body_a":"world","body_b":"grasp_target","contact_count":1504.0,"contact_point_centroid":[0.45856,-0.02632,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.45672,-0.02402,0.09526]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5297.0,"contact_point_centroid":[0.44654,-0.00619,0.03688],"force_p95":0.06582,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11075,"mean_force":0.04115,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44712,-0.02544,0.0352]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":17523.0,"contact_point_centroid":[0.53678,0.06899,0.17921],"force_p95":0.072,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10916,"mean_force":0.0493,"phase_index":4.0,"phase_name":"approach_2","phase_type":"approach","tcp_position_centroid":[0.53686,0.08814,0.17736]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":17811.0,"contact_point_centroid":[0.5398,0.11124,0.18027],"force_p95":0.07147,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10077,"mean_force":0.04819,"phase_index":4.0,"phase_name":"approach_2","phase_type":"approach","tcp_position_centroid":[0.53984,0.09209,0.17829]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5432.0,"contact_point_centroid":[0.44655,-0.04473,0.03674],"force_p95":0.06598,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07527,"mean_force":0.04111,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44712,-0.02544,0.0352]}],"total_contact_groups":15},"final_pose_error":0.00978,"key_states":{"actual_goal_position":[0.63013,0.20822,0.11412],"final_object_position":[0.61763,0.20204,0.02938],"final_tcp_position":[0.62386,0.20465,0.12071],"realised_goal_position":[0.63013,0.20822,0.11412],"realised_object_initial_position":[0.45856,-0.02632,0.03]},"phases":[{"n_steps":281.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.03],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30252,"object_z_max":0.03,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"pre_grasp","tcp_end":[0.46145,-0.02247,0.14913],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.1232,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":376.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"grasp_obj","tcp_end":[0.45464,-0.0257,0.04244],"tcp_start":[0.46145,-0.02247,0.14913],"tcp_to_object_dist_end":0.01689,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.45847,-0.02561,0.02573],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30324,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","subtask_id":"grasp_obj","tcp_end":[0.44709,-0.02544,0.03517],"tcp_start":[0.45464,-0.0257,0.04244],"tcp_to_object_dist_end":0.01479,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":402.0,"n_steps_budget":1000.0,"object_pos_end":[0.46286,-0.0255,0.14285],"object_pos_start":[0.45847,-0.02561,0.02573],"object_to_goal_dist_end":0.28884,"object_to_goal_dist_start":0.30324,"object_z_max":0.14257,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","subtask_id":"lift_obj","tcp_end":[0.45382,-0.02544,0.15422],"tcp_start":[0.44709,-0.02544,0.03517],"tcp_to_object_dist_end":0.01452,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":861.0,"n_steps_budget":1000.0,"object_pos_end":[0.62549,0.19643,0.18562],"object_pos_start":[0.46286,-0.0255,0.14285],"object_to_goal_dist_end":0.07262,"object_to_goal_dist_start":0.28884,"object_z_max":0.18559,"phase_name":"approach_2","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"place_obj","tcp_end":[0.61895,0.19666,0.20259],"tcp_start":[0.45382,-0.02544,0.15422],"tcp_to_object_dist_end":0.01819,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":243.0,"n_steps_budget":1000.0,"object_pos_end":[0.63068,0.20439,0.10214],"object_pos_start":[0.62549,0.19643,0.18562],"object_to_goal_dist_end":0.01259,"object_to_goal_dist_start":0.07262,"object_z_max":0.18562,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"place_obj","tcp_end":[0.62386,0.20465,0.12071],"tcp_start":[0.61895,0.19666,0.20259],"tcp_to_object_dist_end":0.01979,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.61763,0.20204,0.02938],"object_pos_start":[0.63068,0.20439,0.10214],"object_to_goal_dist_end":0.08588,"object_to_goal_dist_start":0.01259,"object_z_max":0.10214,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","subtask_id":"place_obj","tcp_end":[0.61687,0.20218,0.13934],"tcp_start":[0.62386,0.20465,0.12071],"tcp_to_object_dist_end":0.10996,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```