## Search State

- **Seed**: 1
- **Iteration**: 14 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 13 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | impedance_control | impedance_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 8 | 0.4634 | 1.00 | ❌ rejected |
| 12 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | impedance_control | impedance_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 8 | 0.4499 | 1.00 | ❌ rejected |
| 11 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | impedance_control | impedance_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 8 | 0.4636 | 1.00 | ❌ rejected |
| 10 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | impedance_control | impedance_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 8 | 0.4636 | 1.00 | ✅ accepted |
| 9 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | impedance_control | impedance_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 10 | 0.0256 | 0.44 | ✅ accepted |

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

## Current Skill (Q=0.463) — your mutation base

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
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    descend_speed:
      type: scalar
      range:
      - 0.01
      - 0.05
      default: 0.03
      binds_to:
      - path: generator.speed
        mode: replace
    grasp_xy_offset_x:
      type: scalar
      range:
      - -0.02
      - 0.02
      default: 0.0
      binds_to:
      - path: target.offset.x
        mode: replace
    grasp_xy_offset_y:
      type: scalar
      range:
      - -0.02
      - 0.02
      default: 0.0
      binds_to:
      - path: target.offset.y
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
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.18
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    lift_height:
      type: scalar
      range:
      - 0.1
      - 0.25
      default: 0.18
      binds_to:
      - path: target.offset.z
        mode: replace
    lift_speed:
      type: scalar
      range:
      - 0.02
      - 0.08
      default: 0.04
      binds_to:
      - path: generator.speed
        mode: replace
- id: approach_goal
  type: approach
  generator: linear_cartesian
  control: impedance_control
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
  parameters:
    approach_speed:
      type: scalar
      range:
      - 0.01
      - 0.05
      default: 0.03
      binds_to:
      - path: generator.speed
        mode: replace
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
    - 0.0
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
  guards:
  - id: place_pos
    when: after_phase
    predicate: pose_within_tolerance
    threshold: 0.02
    on_failure: retry
  retries:
    max_attempts: 1
    strategy: offset_target
    offset:
    - 0.005
    - 0.005
    - 0.0

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_object** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.15], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings: none
- **descend_to_grasp** (`descend`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.0], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - descend_speed: status=consumed; consumers=generator.speed (replace)
    - grasp_xy_offset_x: status=consumed; consumers=target.offset.x (replace)
    - grasp_xy_offset_y: status=consumed; consumers=target.offset.y (replace)
- **grasp** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings: none
  - guards:
    - id=grasp_hold, when=after_phase, predicate=bilateral_grasp, on_failure=retry, threshold=1.0
  - retries: max_attempts=2, strategy=offset_target, offset=[0.0, 0.0, -0.005]
- **lift** (`lift`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.18], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset.z (replace)
    - lift_speed: status=consumed; consumers=generator.speed (replace)
- **approach_goal** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.15], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (replace)
- **descend_place** (`descend`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - place_xy_offset_x: status=consumed; consumers=target.offset.x (replace)
    - place_xy_offset_y: status=consumed; consumers=target.offset.y (replace)
  - guards:
    - id=place_pos, when=after_phase, predicate=pose_within_tolerance, on_failure=retry, threshold=0.02
  - retries: max_attempts=1, strategy=offset_target, offset=[0.005, 0.005, 0.0]

## Design Metrics

- **Composite score**: 0.463
- **task_score** (E): 1.000
- **fitness_score**: 0.983  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.520

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_object | 1.00 | 1.00 | 0.1084 |
| descend_to_grasp | 1.00 | 1.00 | 0.1538 |
| grasp | 1.00 | 1.00 | 0.0122 |
| lift | 1.00 | 1.00 | 0.1619 |
| approach_goal | 1.00 | 1.00 | 0.2520 |
| descend_place | 1.00 | 1.00 | 0.1189 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.480, -0.000, 0.198) | (0.479, -0.000, 0.030)→(0.479, -0.000, 0.026) | 0.276→0.278 | 1.00 / 4.000 | 38.530 | 0.123 |
| descend_to_grasp | descend | 1.00 / step_budget | (0.480, -0.000, 0.198)→(0.487, -0.000, 0.045) | (0.479, -0.000, 0.026)→(0.479, -0.000, 0.026) | 0.278→0.278 | 1.00 / 44.000 | 0.141 | 0.187 |
| grasp | grasp | 1.00 / step_budget | (0.487, -0.000, 0.045)→(0.479, -0.000, 0.036) | (0.479, -0.000, 0.026)→(0.479, -0.000, 0.026) | 0.278→0.278 | 1.00 / 40.000 | 0.070 | 0.561 |
| lift | lift | 1.00 / step_budget | (0.479, -0.000, 0.036)→(0.476, -0.000, 0.198) | (0.479, -0.000, 0.026)→(0.476, -0.000, 0.186) | 0.278→0.252 | 1.00 / 40.000 | 0.070 | 0.091 |
| approach_goal | approach | 1.00 / step_budget | (0.476, -0.000, 0.198)→(0.600, 0.193, 0.287) | (0.476, -0.000, 0.186)→(0.602, 0.193, 0.272) | 0.252→0.122 | 1.00 / 40.000 | 0.080 | 0.153 |
| descend_place | descend | 1.00 / step_budget | (0.600, 0.193, 0.287)→(0.608, 0.200, 0.169) | (0.602, 0.193, 0.272)→(0.599, 0.199, 0.152) | 0.122→0.013 | 1.00 / 4.000 | 0.123 | 0.138 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.377
- lift_clearance: 1.000
- transport_retention: 1.000
- terminal_score: 1.000
- phase_score: 0.064
- phase_breakdown.reach_goal_score: 0.064
- phase_breakdown.reach_object_score: 0.066
- grasp_place_fitness: 0.985

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.985
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 1.000
- **Median Q (composite search score)**: 0.463
- **K-run variance**: 0.0000
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.12139,"average_solve_count":346.0,"average_success_count":346.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.approach_speed":0.03532,"descend_place.place_xy_offset_x":0.00424,"descend_place.place_xy_offset_y":0.01281,"descend_to_grasp.descend_speed":0.03631,"descend_to_grasp.grasp_xy_offset_x":0.01642,"descend_to_grasp.grasp_xy_offset_y":0.00196,"lift.lift_height":0.19524,"lift.lift_speed":0.05487},"optimized_scores":{"best_composite_score":0.46518,"best_fitness_score":0.98518,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":93.0,"contact_point_centroid":[0.49814,0.04403,-0.00148],"force_p95":0.506,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.59399,"mean_force":0.12907,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.50092,0.0442,0.03623]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":12240.0,"contact_point_centroid":[0.49876,0.06313,0.12348],"force_p95":0.07171,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32956,"mean_force":0.05059,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.49855,0.04398,0.12168]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":12240.0,"contact_point_centroid":[0.49879,0.02485,0.12365],"force_p95":0.07134,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29034,"mean_force":0.05008,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.49855,0.04398,0.12168]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50115,0.04493,-0.00207],"force_p95":0.14172,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.17967,"mean_force":0.12842,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.50335,0.04444,0.03611]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4320.0,"contact_point_centroid":[0.56073,0.25964,0.22741],"force_p95":0.0786,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14387,"mean_force":0.05252,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.56049,0.24068,0.22579]},{"body_a":"world","body_b":"grasp_target","contact_count":836.0,"contact_point_centroid":[0.50118,0.04505,-0.00185],"force_p95":0.13728,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12321,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.49872,0.0172,0.25009]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4320.0,"contact_point_centroid":[0.56079,0.22137,0.22795],"force_p95":0.07818,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12361,"mean_force":0.05206,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.56049,0.24068,0.22579]},{"body_a":"world","body_b":"grasp_target","contact_count":1268.0,"contact_point_centroid":[0.50118,0.04505,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.50315,0.04045,0.12202]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4818.0,"contact_point_centroid":[0.50241,0.02515,0.03681],"force_p95":0.07071,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11385,"mean_force":0.04475,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.50219,0.04433,0.03484]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":13900.0,"contact_point_centroid":[0.52803,0.12013,0.24754],"force_p95":0.06967,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08599,"mean_force":0.04797,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.52776,0.13925,0.2455]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":13900.0,"contact_point_centroid":[0.52799,0.1584,0.24723],"force_p95":0.06972,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08589,"mean_force":0.04799,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.52776,0.13925,0.2455]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4922.0,"contact_point_centroid":[0.50238,0.06356,0.03666],"force_p95":0.07112,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08228,"mean_force":0.0448,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.50219,0.04433,0.03485]}],"total_contact_groups":12},"final_pose_error":0.01972,"key_states":{"actual_goal_position":[0.56442,0.24486,0.14677],"final_object_position":[0.55347,0.25007,0.14971],"final_tcp_position":[0.56377,0.25122,0.16476],"realised_goal_position":[0.56442,0.24486,0.14677],"realised_object_initial_position":[0.50118,0.04505,0.03]},"peak_contact_force":34.3241,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":210.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.03],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.23992,"object_z_max":0.03,"peak_contact_force":34.3241,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1268.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.49827,0.03619,0.19753],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.17176,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":317.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"peak_contact_force":0.13865,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":11540.0,"raw_peak_contact_force":0.17967,"subtask_id":"reach_object","tcp_end":[0.51073,0.04509,0.04454],"tcp_start":[0.49827,0.03619,0.19753],"tcp_to_object_dist_end":0.02084,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50104,0.04445,0.02571],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.24257,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"peak_contact_force":0.06996,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":24573.0,"raw_peak_contact_force":0.59399,"tcp_end":[0.50216,0.04432,0.03481],"tcp_start":[0.51073,0.04509,0.04454],"tcp_to_object_dist_end":0.00917,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":612.0,"n_steps_budget":1000.0,"object_pos_end":[0.49933,0.04403,0.199],"object_pos_start":[0.50104,0.04445,0.02571],"object_to_goal_dist_end":0.21748,"object_to_goal_dist_start":0.24257,"object_z_max":0.19873,"peak_contact_force":0.06978,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":27800.0,"raw_peak_contact_force":0.08599,"tcp_end":[0.49897,0.04402,0.21031],"tcp_start":[0.50216,0.04432,0.03481],"tcp_to_object_dist_end":0.01132,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":695.0,"n_steps_budget":1000.0,"object_pos_end":[0.55937,0.23129,0.26985],"object_pos_start":[0.49933,0.04403,0.199],"object_to_goal_dist_end":0.12392,"object_to_goal_dist_start":0.21748,"object_z_max":0.26976,"peak_contact_force":0.08123,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":8640.0,"raw_peak_contact_force":0.14387,"subtask_id":"reach_goal","tcp_end":[0.5582,0.23142,0.28368],"tcp_start":[0.49897,0.04402,0.21031],"tcp_to_object_dist_end":0.01388,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":216.0,"n_steps_budget":1000.0,"object_pos_end":[0.55347,0.25007,0.14971],"object_pos_start":[0.55937,0.23129,0.26985],"object_to_goal_dist_end":0.01247,"object_to_goal_dist_start":0.12392,"object_z_max":0.26985,"peak_contact_force":0.12262,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":836.0,"raw_peak_contact_force":0.13845,"tcp_end":[0.56377,0.25122,0.16476],"tcp_start":[0.5582,0.23142,0.28368],"tcp_to_object_dist_end":0.01827,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.00824,"average_solve_count":364.0,"average_success_count":364.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.approach_speed":0.01969,"descend_place.place_xy_offset_x":0.00756,"descend_place.place_xy_offset_y":-0.00968,"descend_to_grasp.descend_speed":0.02557,"descend_to_grasp.grasp_xy_offset_x":0.01393,"descend_to_grasp.grasp_xy_offset_y":0.00048,"lift.lift_height":0.17137,"lift.lift_speed":0.05112},"optimized_scores":{"best_composite_score":0.46306,"best_fitness_score":0.98306,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":92.0,"contact_point_centroid":[0.47278,-0.01882,-0.00153],"force_p95":0.49726,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55883,"mean_force":0.14254,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.47508,-0.01889,0.03755]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":10220.0,"contact_point_centroid":[0.47298,-0.03797,0.11293],"force_p95":0.07337,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30353,"mean_force":0.0512,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.47275,-0.01883,0.11106]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":10220.0,"contact_point_centroid":[0.47295,0.00032,0.11296],"force_p95":0.07215,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29088,"mean_force":0.05078,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.47275,-0.01883,0.11106]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.47613,-0.02,-0.00212],"force_p95":0.15426,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.21453,"mean_force":0.13188,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.47737,-0.01894,0.03722]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3980.0,"contact_point_centroid":[0.62757,0.16889,0.27048],"force_p95":0.07918,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15088,"mean_force":0.05309,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.62731,0.14987,0.26869]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3980.0,"contact_point_centroid":[0.62759,0.13061,0.27066],"force_p95":0.07877,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1466,"mean_force":0.05268,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.62731,0.14987,0.26869]},{"body_a":"world","body_b":"grasp_target","contact_count":776.0,"contact_point_centroid":[0.47616,-0.02015,-0.00183],"force_p95":0.13759,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12326,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.48942,-0.00754,0.25146]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4798.0,"contact_point_centroid":[0.47645,0.00027,0.038],"force_p95":0.0721,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12873,"mean_force":0.04483,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.47626,-0.01892,0.03609]},{"body_a":"world","body_b":"grasp_target","contact_count":1304.0,"contact_point_centroid":[0.47616,-0.02015,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.48025,-0.01745,0.12364]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":18740.0,"contact_point_centroid":[0.5487,0.0492,0.25812],"force_p95":0.0699,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0916,"mean_force":0.04825,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.54844,0.06834,0.25623]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":18740.0,"contact_point_centroid":[0.54868,0.08748,0.25811],"force_p95":0.06955,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08702,"mean_force":0.04798,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.54844,0.06834,0.25623]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4978.0,"contact_point_centroid":[0.47647,-0.03816,0.03798],"force_p95":0.07255,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08042,"mean_force":0.04462,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.47626,-0.01892,0.0361]}],"total_contact_groups":12},"final_pose_error":0.01978,"key_states":{"actual_goal_position":[0.63142,0.15919,0.19002],"final_object_position":[0.62208,0.14831,0.19193],"final_tcp_position":[0.63295,0.14892,0.20884],"realised_goal_position":[0.63142,0.15919,0.19002],"realised_object_initial_position":[0.47616,-0.02015,0.03]},"peak_contact_force":81.14225,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":195.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.03],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28614,"object_z_max":0.03,"peak_contact_force":81.14225,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1304.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.47852,-0.01598,0.19941],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.17346,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":326.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.14916,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":11576.0,"raw_peak_contact_force":0.21453,"subtask_id":"reach_object","tcp_end":[0.48448,-0.01907,0.04481],"tcp_start":[0.47852,-0.01598,0.19941],"tcp_to_object_dist_end":0.02058,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.47603,-0.01916,0.02554],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28811,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.07101,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":20532.0,"raw_peak_contact_force":0.55883,"tcp_end":[0.47623,-0.01891,0.03606],"tcp_start":[0.48448,-0.01907,0.04481],"tcp_to_object_dist_end":0.01052,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":511.0,"n_steps_budget":1000.0,"object_pos_end":[0.4735,-0.01891,0.17548],"object_pos_start":[0.47603,-0.01916,0.02554],"object_to_goal_dist_end":0.23848,"object_to_goal_dist_start":0.28811,"object_z_max":0.17519,"peak_contact_force":0.06964,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":37480.0,"raw_peak_contact_force":0.0916,"tcp_end":[0.47294,-0.01882,0.18784],"tcp_start":[0.47623,-0.01891,0.03606],"tcp_to_object_dist_end":0.01238,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":937.0,"n_steps_budget":1000.0,"object_pos_end":[0.62393,0.15047,0.30875],"object_pos_start":[0.4735,-0.01891,0.17548],"object_to_goal_dist_end":0.11929,"object_to_goal_dist_start":0.23848,"object_z_max":0.30864,"peak_contact_force":0.08074,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":7960.0,"raw_peak_contact_force":0.15088,"subtask_id":"reach_goal","tcp_end":[0.62261,0.15053,0.32445],"tcp_start":[0.47294,-0.01882,0.18784],"tcp_to_object_dist_end":0.01575,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":199.0,"n_steps_budget":1000.0,"object_pos_end":[0.62208,0.14831,0.19193],"object_pos_start":[0.62393,0.15047,0.30875],"object_to_goal_dist_end":0.01447,"object_to_goal_dist_start":0.11929,"object_z_max":0.30875,"peak_contact_force":0.12263,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":776.0,"raw_peak_contact_force":0.13845,"tcp_end":[0.63295,0.14892,0.20884],"tcp_start":[0.62261,0.15053,0.32445],"tcp_to_object_dist_end":0.02012,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.12607,"average_solve_count":349.0,"average_success_count":349.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.approach_speed":0.01603,"descend_place.place_xy_offset_x":0.00438,"descend_place.place_xy_offset_y":-0.00587,"descend_to_grasp.descend_speed":0.03423,"descend_to_grasp.grasp_xy_offset_x":0.0125,"descend_to_grasp.grasp_xy_offset_y":-0.00072,"lift.lift_height":0.17796,"lift.lift_speed":0.05228},"optimized_scores":{"best_composite_score":0.46195,"best_fitness_score":0.98195,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":84.0,"contact_point_centroid":[0.45551,-0.02562,-0.00144],"force_p95":0.45694,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.52945,"mean_force":0.12935,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.45714,-0.02578,0.03833]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":10420.0,"contact_point_centroid":[0.45507,-0.04482,0.11727],"force_p95":0.07185,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29557,"mean_force":0.051,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.45484,-0.02567,0.11541]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":10420.0,"contact_point_centroid":[0.45504,-0.00653,0.11734],"force_p95":0.07092,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28246,"mean_force":0.05079,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.45484,-0.02567,0.11541]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.45854,-0.02624,-0.00205],"force_p95":0.13588,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.16572,"mean_force":0.12655,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.4593,-0.02585,0.03811]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4120.0,"contact_point_centroid":[0.6232,0.21705,0.19583],"force_p95":0.08133,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16391,"mean_force":0.0542,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.62299,0.19801,0.19406]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4120.0,"contact_point_centroid":[0.62331,0.17877,0.19605],"force_p95":0.08218,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16025,"mean_force":0.05352,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.62299,0.19801,0.19406]},{"body_a":"world","body_b":"grasp_target","contact_count":824.0,"contact_point_centroid":[0.45856,-0.02632,-0.00184],"force_p95":0.13728,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12322,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.48245,-0.01007,0.25052]},{"body_a":"world","body_b":"grasp_target","contact_count":1280.0,"contact_point_centroid":[0.45856,-0.02632,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.464,-0.02354,0.12289]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4829.0,"contact_point_centroid":[0.45841,-0.00663,0.039],"force_p95":0.0693,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10914,"mean_force":0.04476,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.45823,-0.02581,0.03707]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":18320.0,"contact_point_centroid":[0.53829,0.06917,0.22475],"force_p95":0.06986,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09398,"mean_force":0.04823,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.53803,0.08831,0.22286]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4902.0,"contact_point_centroid":[0.45843,-0.04503,0.03894],"force_p95":0.06958,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09076,"mean_force":0.04479,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.45823,-0.02581,0.03707]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":18320.0,"contact_point_centroid":[0.53826,0.10745,0.22474],"force_p95":0.06962,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08776,"mean_force":0.04801,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.53803,0.08831,0.22286]}],"total_contact_groups":12},"final_pose_error":0.01974,"key_states":{"actual_goal_position":[0.63013,0.20822,0.11412],"final_object_position":[0.62092,0.19918,0.11518],"final_tcp_position":[0.62784,0.19984,0.13253],"realised_goal_position":[0.63013,0.20822,0.11412],"realised_object_initial_position":[0.45856,-0.02632,0.03]},"peak_contact_force":0.52945,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":207.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.03],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30252,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1280.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.46401,-0.02124,0.19803],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.17218,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":320.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.13419,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":11531.0,"raw_peak_contact_force":0.16572,"subtask_id":"reach_object","tcp_end":[0.46623,-0.02607,0.04521],"tcp_start":[0.46401,-0.02124,0.19803],"tcp_to_object_dist_end":0.02066,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.45844,-0.02591,0.02581],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30346,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.0698,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":20924.0,"raw_peak_contact_force":0.52945,"tcp_end":[0.4582,-0.02581,0.03704],"tcp_start":[0.46623,-0.02607,0.04521],"tcp_to_object_dist_end":0.01124,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":521.0,"n_steps_budget":1000.0,"object_pos_end":[0.4562,-0.02569,0.18254],"object_pos_start":[0.45844,-0.02591,0.02581],"object_to_goal_dist_end":0.2994,"object_to_goal_dist_start":0.30346,"object_z_max":0.18225,"peak_contact_force":0.06982,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":36640.0,"raw_peak_contact_force":0.09398,"tcp_end":[0.45504,-0.02567,0.19549],"tcp_start":[0.4582,-0.02581,0.03704],"tcp_to_object_dist_end":0.013,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":916.0,"n_steps_budget":1000.0,"object_pos_end":[0.62128,0.19634,0.2359],"object_pos_start":[0.4562,-0.02569,0.18254],"object_to_goal_dist_end":0.12268,"object_to_goal_dist_start":0.2994,"object_z_max":0.23586,"peak_contact_force":0.07879,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":8240.0,"raw_peak_contact_force":0.16391,"subtask_id":"reach_goal","tcp_end":[0.61951,0.19641,0.25214],"tcp_start":[0.45504,-0.02567,0.19549],"tcp_to_object_dist_end":0.01633,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":206.0,"n_steps_budget":1000.0,"object_pos_end":[0.62092,0.19918,0.11518],"object_pos_start":[0.62128,0.19634,0.2359],"object_to_goal_dist_end":0.01294,"object_to_goal_dist_start":0.12268,"object_z_max":0.2359,"peak_contact_force":0.12262,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":824.0,"raw_peak_contact_force":0.13845,"tcp_end":[0.62784,0.19984,0.13253],"tcp_start":[0.61951,0.19641,0.25214],"tcp_to_object_dist_end":0.01869,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```