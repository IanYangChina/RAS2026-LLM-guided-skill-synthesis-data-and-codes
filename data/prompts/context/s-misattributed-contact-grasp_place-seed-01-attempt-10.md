## Search State

- **Seed**: 1
- **Iteration**: 11 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 10 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | impedance_control | impedance_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 8 | 0.4636 | 1.00 | ✅ accepted |
| 9 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | impedance_control | impedance_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 10 | 0.0256 | 0.44 | ✅ accepted |
| 8 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 5 | 0.0121 | 0.19 | ❌ rejected |
| 7 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 4 | 0.2785 | 0.41 | ❌ rejected |
| 6 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 3 | 0.3531 | 0.41 | ❌ rejected |

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

## Current Skill (Q=0.464) — your mutation base

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

- **Composite score**: 0.464
- **task_score** (E): 1.000
- **fitness_score**: 0.984  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.520

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_object | 1.00 | 1.00 | 0.1084 |
| descend_to_grasp | 1.00 | 1.00 | 0.1541 |
| grasp | 1.00 | 1.00 | 0.0122 |
| lift | 1.00 | 1.00 | 0.1388 |
| approach_goal | 1.00 | 1.00 | 0.2635 |
| descend_place | 1.00 | 1.00 | 0.1171 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.480, -0.000, 0.198) | (0.479, -0.000, 0.030)→(0.479, -0.000, 0.026) | 0.276→0.278 | 1.00 / 4.000 | 0.123 | 0.123 |
| descend_to_grasp | descend | 1.00 / step_budget | (0.480, -0.000, 0.198)→(0.488, -0.001, 0.045) | (0.479, -0.000, 0.026)→(0.479, -0.000, 0.026) | 0.278→0.278 | 1.00 / 44.000 | 0.136 | 0.171 |
| grasp | grasp | 1.00 / step_budget | (0.488, -0.001, 0.045)→(0.480, -0.001, 0.036) | (0.479, -0.000, 0.026)→(0.479, -0.001, 0.026) | 0.278→0.278 | 1.00 / 40.000 | 0.070 | 0.555 |
| lift | lift | 1.00 / step_budget | (0.480, -0.001, 0.036)→(0.477, -0.001, 0.175) | (0.479, -0.001, 0.026)→(0.478, -0.001, 0.163) | 0.278→0.250 | 1.00 / 40.000 | 0.070 | 0.093 |
| approach_goal | approach | 1.00 / step_budget | (0.477, -0.001, 0.175)→(0.600, 0.194, 0.286) | (0.478, -0.001, 0.163)→(0.602, 0.193, 0.271) | 0.250→0.121 | 1.00 / 39.667 | 0.083 | 0.150 |
| descend_place | descend | 1.00 / step_budget | (0.600, 0.194, 0.286)→(0.607, 0.198, 0.169) | (0.602, 0.193, 0.271)→(0.597, 0.197, 0.153) | 0.121→0.014 | 1.00 / 4.000 | 0.123 | 0.138 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.279
- lift_clearance: 1.000
- transport_retention: 1.000
- terminal_score: 1.000
- phase_score: 0.067
- phase_breakdown.reach_goal_score: 0.067
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
- **Final σ (mean)**: 0.232


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.0113,"average_solve_count":354.0,"average_success_count":354.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.approach_speed":0.03579,"descend_place.place_xy_offset_x":0.0059,"descend_place.place_xy_offset_y":-0.00486,"descend_to_grasp.descend_speed":0.02728,"descend_to_grasp.grasp_xy_offset_x":0.01758,"descend_to_grasp.grasp_xy_offset_y":0.00346,"lift.lift_height":0.13192,"lift.lift_speed":0.04631},"optimized_scores":{"best_composite_score":0.46496,"best_fitness_score":0.98496,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":98.0,"contact_point_centroid":[0.49688,0.04553,-0.00151],"force_p95":0.54144,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.56604,"mean_force":0.16972,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.50196,0.04546,0.03629]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":7940.0,"contact_point_centroid":[0.49967,0.06438,0.09154],"force_p95":0.07051,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.3067,"mean_force":0.05178,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.49946,0.04522,0.08974]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":7940.0,"contact_point_centroid":[0.4997,0.02608,0.09173],"force_p95":0.07008,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27669,"mean_force":0.05142,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.49946,0.04522,0.08974]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50115,0.04511,-0.00206],"force_p95":0.13916,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.1758,"mean_force":0.12767,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.50433,0.0457,0.03612]},{"body_a":"world","body_b":"grasp_target","contact_count":836.0,"contact_point_centroid":[0.50118,0.04505,-0.00185],"force_p95":0.13728,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12321,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.49872,0.0172,0.25009]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3930.0,"contact_point_centroid":[0.56197,0.25427,0.22871],"force_p95":0.08139,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12995,"mean_force":0.0553,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.56138,0.2353,0.22715]},{"body_a":"world","body_b":"grasp_target","contact_count":1292.0,"contact_point_centroid":[0.50118,0.04505,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.50355,0.04103,0.12247]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4248.0,"contact_point_centroid":[0.56203,0.21611,0.22618],"force_p95":0.07683,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10799,"mean_force":0.05119,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.56156,0.23539,0.22407]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4825.0,"contact_point_centroid":[0.50335,0.06478,0.03667],"force_p95":0.06867,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10683,"mean_force":0.04486,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.50317,0.04559,0.03485]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":16900.0,"contact_point_centroid":[0.52849,0.16087,0.21558],"force_p95":0.06973,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09597,"mean_force":0.04811,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.52825,0.14171,0.21385]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":16900.0,"contact_point_centroid":[0.52852,0.1226,0.21589],"force_p95":0.06973,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09518,"mean_force":0.04818,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.52825,0.14171,0.21385]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4906.0,"contact_point_centroid":[0.50338,0.02638,0.03683],"force_p95":0.06884,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09052,"mean_force":0.0447,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.50317,0.04559,0.03485]}],"total_contact_groups":12},"final_pose_error":0.01962,"key_states":{"actual_goal_position":[0.56442,0.24486,0.14677],"final_object_position":[0.55321,0.23644,0.15012],"final_tcp_position":[0.56511,0.23734,0.1655],"realised_goal_position":[0.56442,0.24486,0.14677],"realised_object_initial_position":[0.50118,0.04505,0.03]},"peak_contact_force":0.56604,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":210.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.03],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.23992,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1292.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.49827,0.03619,0.19753],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.17176,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":323.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"peak_contact_force":0.13726,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":11531.0,"raw_peak_contact_force":0.1758,"subtask_id":"reach_object","tcp_end":[0.5117,0.04637,0.04457],"tcp_start":[0.49827,0.03619,0.19753],"tcp_to_object_dist_end":0.02137,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50104,0.04549,0.02575],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.24169,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"peak_contact_force":0.06903,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":15978.0,"raw_peak_contact_force":0.56604,"tcp_end":[0.50314,0.04558,0.03482],"tcp_start":[0.5117,0.04637,0.04457],"tcp_to_object_dist_end":0.00931,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":397.0,"n_steps_budget":1000.0,"object_pos_end":[0.49752,0.04515,0.13651],"object_pos_start":[0.50104,0.04549,0.02575],"object_to_goal_dist_end":0.21087,"object_to_goal_dist_start":0.24169,"object_z_max":0.13624,"peak_contact_force":0.06969,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":33800.0,"raw_peak_contact_force":0.09597,"tcp_end":[0.4994,0.04522,0.14718],"tcp_start":[0.50314,0.04558,0.03482],"tcp_to_object_dist_end":0.01084,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":39.0,"n_steps":845.0,"n_steps_budget":1000.0,"object_pos_end":[0.55868,0.23348,0.26733],"object_pos_start":[0.49752,0.04515,0.13651],"object_to_goal_dist_end":0.12123,"object_to_goal_dist_start":0.21087,"object_z_max":0.26719,"peak_contact_force":0.08915,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":8178.0,"raw_peak_contact_force":0.12995,"subtask_id":"reach_goal","tcp_end":[0.55888,0.23362,0.2813],"tcp_start":[0.4994,0.04522,0.14718],"tcp_to_object_dist_end":0.01397,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":206.0,"n_steps_budget":1000.0,"object_pos_end":[0.55321,0.23644,0.15012],"object_pos_start":[0.55868,0.23348,0.26733],"object_to_goal_dist_end":0.01442,"object_to_goal_dist_start":0.12123,"object_z_max":0.26736,"peak_contact_force":0.12262,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":836.0,"raw_peak_contact_force":0.13845,"tcp_end":[0.56511,0.23734,0.1655],"tcp_start":[0.55888,0.23362,0.2813],"tcp_to_object_dist_end":0.01947,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.06628,"average_solve_count":347.0,"average_success_count":347.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.approach_speed":0.03435,"descend_place.place_xy_offset_x":0.00444,"descend_place.place_xy_offset_y":-0.00389,"descend_to_grasp.descend_speed":0.02935,"descend_to_grasp.grasp_xy_offset_x":0.01614,"descend_to_grasp.grasp_xy_offset_y":-0.00177,"lift.lift_height":0.16067,"lift.lift_speed":0.06281},"optimized_scores":{"best_composite_score":0.46338,"best_fitness_score":0.98338,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":86.0,"contact_point_centroid":[0.47315,-0.02134,-0.00146],"force_p95":0.47518,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.5691,"mean_force":0.12508,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.47699,-0.0208,0.03734]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":9320.0,"contact_point_centroid":[0.47472,-0.00158,0.10756],"force_p95":0.07187,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30322,"mean_force":0.05115,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.47451,-0.02072,0.10564]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":9320.0,"contact_point_centroid":[0.47474,-0.03987,0.10749],"force_p95":0.07134,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30052,"mean_force":0.05101,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.47451,-0.02072,0.10564]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.47613,-0.02024,-0.00207],"force_p95":0.14077,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.17919,"mean_force":0.12808,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.47927,-0.02085,0.03701]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3960.0,"contact_point_centroid":[0.62656,0.17108,0.27027],"force_p95":0.07698,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15688,"mean_force":0.05229,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.62634,0.15206,0.26847]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3960.0,"contact_point_centroid":[0.62668,0.13281,0.27043],"force_p95":0.07703,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15202,"mean_force":0.05189,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.62634,0.15206,0.26847]},{"body_a":"world","body_b":"grasp_target","contact_count":776.0,"contact_point_centroid":[0.47616,-0.02015,-0.00183],"force_p95":0.13759,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12326,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.48942,-0.00754,0.25146]},{"body_a":"world","body_b":"grasp_target","contact_count":1308.0,"contact_point_centroid":[0.47616,-0.02015,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.48117,-0.01837,0.12348]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4820.0,"contact_point_centroid":[0.47836,-0.04001,0.03772],"force_p95":0.06962,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11195,"mean_force":0.04483,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.47815,-0.02082,0.03587]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":19360.0,"contact_point_centroid":[0.54965,0.04846,0.25277],"force_p95":0.07018,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08768,"mean_force":0.04838,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.54939,0.0676,0.25088]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":19360.0,"contact_point_centroid":[0.54962,0.08673,0.25277],"force_p95":0.06955,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08227,"mean_force":0.0483,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.54939,0.0676,0.25088]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4920.0,"contact_point_centroid":[0.47834,-0.00161,0.03779],"force_p95":0.06993,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07943,"mean_force":0.04472,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.47816,-0.02082,0.03587]}],"total_contact_groups":12},"final_pose_error":0.01952,"key_states":{"actual_goal_position":[0.63142,0.15919,0.19002],"final_object_position":[0.62097,0.15279,0.19181],"final_tcp_position":[0.63069,0.15356,0.20876],"realised_goal_position":[0.63142,0.15919,0.19002],"realised_object_initial_position":[0.47616,-0.02015,0.03]},"peak_contact_force":0.5691,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":195.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.03],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28614,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1308.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.47852,-0.01598,0.19941],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.17346,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":327.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.13824,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":11540.0,"raw_peak_contact_force":0.17919,"subtask_id":"reach_object","tcp_end":[0.4864,-0.021,0.04464],"tcp_start":[0.47852,-0.01598,0.19941],"tcp_to_object_dist_end":0.02126,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.47603,-0.02069,0.02573],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28896,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.07035,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":18726.0,"raw_peak_contact_force":0.5691,"tcp_end":[0.47812,-0.02082,0.03584],"tcp_start":[0.4864,-0.021,0.04464],"tcp_to_object_dist_end":0.01032,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":466.0,"n_steps_budget":1000.0,"object_pos_end":[0.47909,-0.02066,0.16544],"object_pos_start":[0.47603,-0.02069,0.02573],"object_to_goal_dist_end":0.23697,"object_to_goal_dist_start":0.28896,"object_z_max":0.16515,"peak_contact_force":0.06952,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":38720.0,"raw_peak_contact_force":0.08768,"tcp_end":[0.47456,-0.02071,0.17701],"tcp_start":[0.47812,-0.02082,0.03584],"tcp_to_object_dist_end":0.01243,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":968.0,"n_steps_budget":1000.0,"object_pos_end":[0.62647,0.15065,0.30844],"object_pos_start":[0.47909,-0.02066,0.16544],"object_to_goal_dist_end":0.11883,"object_to_goal_dist_start":0.23697,"object_z_max":0.30832,"peak_contact_force":0.07922,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":7920.0,"raw_peak_contact_force":0.15688,"subtask_id":"reach_goal","tcp_end":[0.62287,0.15068,0.32415],"tcp_start":[0.47456,-0.02071,0.17701],"tcp_to_object_dist_end":0.01612,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":198.0,"n_steps_budget":1000.0,"object_pos_end":[0.62097,0.15279,0.19181],"object_pos_start":[0.62647,0.15065,0.30844],"object_to_goal_dist_end":0.01238,"object_to_goal_dist_start":0.11883,"object_z_max":0.30844,"peak_contact_force":0.12263,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":776.0,"raw_peak_contact_force":0.13845,"tcp_end":[0.63069,0.15356,0.20876],"tcp_start":[0.62287,0.15068,0.32415],"tcp_to_object_dist_end":0.01955,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.11989,"average_solve_count":367.0,"average_success_count":367.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.approach_speed":0.02883,"descend_place.place_xy_offset_x":-0.00065,"descend_place.place_xy_offset_y":-0.00156,"descend_to_grasp.descend_speed":0.03105,"descend_to_grasp.grasp_xy_offset_x":0.01336,"descend_to_grasp.grasp_xy_offset_y":-0.00164,"lift.lift_height":0.18253,"lift.lift_speed":0.04777},"optimized_scores":{"best_composite_score":0.46251,"best_fitness_score":0.98251,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":86.0,"contact_point_centroid":[0.455,-0.02687,-0.00147],"force_p95":0.47894,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.53016,"mean_force":0.15085,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.45786,-0.02657,0.03797]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":10760.0,"contact_point_centroid":[0.45579,-0.04561,0.11908],"force_p95":0.07009,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29178,"mean_force":0.05096,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.45557,-0.02646,0.11724]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":10760.0,"contact_point_centroid":[0.45577,-0.00732,0.11917],"force_p95":0.0706,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28872,"mean_force":0.05095,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.45557,-0.02646,0.11724]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4100.0,"contact_point_centroid":[0.62138,0.21859,0.19616],"force_p95":0.08055,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16234,"mean_force":0.05388,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.62115,0.19956,0.19439]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4100.0,"contact_point_centroid":[0.62146,0.18031,0.19638],"force_p95":0.08118,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15833,"mean_force":0.05325,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.62115,0.19956,0.19439]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.45854,-0.02636,-0.00204],"force_p95":0.13266,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.15696,"mean_force":0.1257,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.46003,-0.02665,0.03779]},{"body_a":"world","body_b":"grasp_target","contact_count":824.0,"contact_point_centroid":[0.45856,-0.02632,-0.00184],"force_p95":0.13728,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12322,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.48245,-0.01007,0.25052]},{"body_a":"world","body_b":"grasp_target","contact_count":1288.0,"contact_point_centroid":[0.45856,-0.02632,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.46435,-0.02392,0.12285]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4840.0,"contact_point_centroid":[0.45916,-0.0458,0.03859],"force_p95":0.06824,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10427,"mean_force":0.0448,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.45896,-0.02661,0.03674]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":18180.0,"contact_point_centroid":[0.53865,0.06871,0.22681],"force_p95":0.0696,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09451,"mean_force":0.04817,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.5384,0.08786,0.22493]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":18180.0,"contact_point_centroid":[0.53862,0.10699,0.22681],"force_p95":0.06961,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08914,"mean_force":0.04802,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.5384,0.08786,0.22493]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4884.0,"contact_point_centroid":[0.45914,-0.00741,0.03867],"force_p95":0.06837,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08812,"mean_force":0.04473,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.45896,-0.02661,0.03674]}],"total_contact_groups":12},"final_pose_error":0.01995,"key_states":{"actual_goal_position":[0.63013,0.20822,0.11412],"final_object_position":[0.61584,0.20256,0.11585],"final_tcp_position":[0.62383,0.20324,0.13295],"realised_goal_position":[0.63013,0.20822,0.11412],"realised_object_initial_position":[0.45856,-0.02632,0.03]},"peak_contact_force":0.53016,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":207.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.03],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30252,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1288.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.46401,-0.02124,0.19803],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.17218,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":322.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.13178,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":11524.0,"raw_peak_contact_force":0.15696,"subtask_id":"reach_object","tcp_end":[0.46697,-0.02688,0.0449],"tcp_start":[0.46401,-0.02124,0.19803],"tcp_to_object_dist_end":0.02067,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.45844,-0.02655,0.02584],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30395,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.06923,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":21606.0,"raw_peak_contact_force":0.53016,"tcp_end":[0.45893,-0.02661,0.03671],"tcp_start":[0.46697,-0.02688,0.0449],"tcp_to_object_dist_end":0.01088,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":538.0,"n_steps_budget":1000.0,"object_pos_end":[0.4561,-0.02642,0.18684],"object_pos_start":[0.45844,-0.02655,0.02584],"object_to_goal_dist_end":0.30104,"object_to_goal_dist_start":0.30395,"object_z_max":0.18655,"peak_contact_force":0.0697,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":36360.0,"raw_peak_contact_force":0.09451,"tcp_end":[0.45579,-0.02646,0.19957],"tcp_start":[0.45893,-0.02661,0.03671],"tcp_to_object_dist_end":0.01273,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":909.0,"n_steps_budget":1000.0,"object_pos_end":[0.62086,0.19632,0.23642],"object_pos_start":[0.4561,-0.02642,0.18684],"object_to_goal_dist_end":0.12323,"object_to_goal_dist_start":0.30104,"object_z_max":0.23638,"peak_contact_force":0.07958,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":8200.0,"raw_peak_contact_force":0.16234,"subtask_id":"reach_goal","tcp_end":[0.61954,0.19637,0.25233],"tcp_start":[0.45579,-0.02646,0.19957],"tcp_to_object_dist_end":0.01596,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":205.0,"n_steps_budget":1000.0,"object_pos_end":[0.61584,0.20256,0.11585],"object_pos_start":[0.62086,0.19632,0.23642],"object_to_goal_dist_end":0.01547,"object_to_goal_dist_start":0.12323,"object_z_max":0.23642,"peak_contact_force":0.12262,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":824.0,"raw_peak_contact_force":0.13845,"tcp_end":[0.62383,0.20324,0.13295],"tcp_start":[0.61954,0.19637,0.25233],"tcp_to_object_dist_end":0.01889,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```