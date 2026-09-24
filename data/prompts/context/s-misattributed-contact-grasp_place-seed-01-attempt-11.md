## Search State

- **Seed**: 1
- **Iteration**: 12 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 11 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | impedance_control | impedance_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 8 | 0.4636 | 1.00 | ❌ rejected |
| 10 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | impedance_control | impedance_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 8 | 0.4636 | 1.00 | ✅ accepted |
| 9 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | impedance_control | impedance_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 10 | 0.0256 | 0.44 | ✅ accepted |
| 8 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 5 | 0.0121 | 0.19 | ❌ rejected |
| 7 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 4 | 0.2785 | 0.41 | ❌ rejected |

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
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.520

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_object | 1.00 | 1.00 | 0.1084 |
| descend_to_grasp | 1.00 | 1.00 | 0.1538 |
| grasp | 1.00 | 1.00 | 0.0122 |
| lift | 1.00 | 1.00 | 0.1426 |
| approach_goal | 1.00 | 1.00 | 0.2601 |
| descend_place | 1.00 | 1.00 | 0.1184 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.480, -0.000, 0.198) | (0.479, -0.000, 0.030)→(0.479, -0.000, 0.026) | 0.276→0.278 | 1.00 / 4.000 | 37.870 | 0.123 |
| descend_to_grasp | descend | 1.00 / step_budget | (0.480, -0.000, 0.198)→(0.488, -0.001, 0.045) | (0.479, -0.000, 0.026)→(0.479, -0.000, 0.026) | 0.278→0.278 | 1.00 / 44.000 | 0.132 | 0.157 |
| grasp | grasp | 1.00 / step_budget | (0.488, -0.001, 0.045)→(0.479, -0.001, 0.036) | (0.479, -0.000, 0.026)→(0.479, -0.001, 0.026) | 0.278→0.278 | 1.00 / 40.000 | 0.070 | 0.559 |
| lift | lift | 1.00 / step_budget | (0.479, -0.001, 0.036)→(0.476, -0.001, 0.179) | (0.479, -0.001, 0.026)→(0.479, -0.001, 0.167) | 0.278→0.248 | 1.00 / 40.000 | 0.070 | 0.090 |
| approach_goal | approach | 1.00 / step_budget | (0.476, -0.001, 0.179)→(0.600, 0.193, 0.286) | (0.479, -0.001, 0.167)→(0.603, 0.193, 0.271) | 0.248→0.121 | 1.00 / 39.333 | 0.079 | 0.153 |
| descend_place | descend | 1.00 / step_budget | (0.600, 0.193, 0.286)→(0.612, 0.199, 0.169) | (0.603, 0.193, 0.271)→(0.605, 0.198, 0.152) | 0.121→0.011 | 1.00 / 4.000 | 0.123 | 0.138 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.203
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
- **Final σ (mean)**: 0.398


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.07625,"average_solve_count":341.0,"average_success_count":341.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.approach_speed":0.02515,"descend_place.place_xy_offset_x":0.01991,"descend_place.place_xy_offset_y":-0.01295,"descend_to_grasp.descend_speed":0.02945,"descend_to_grasp.grasp_xy_offset_x":0.01657,"descend_to_grasp.grasp_xy_offset_y":0.00267,"lift.lift_height":0.14098,"lift.lift_speed":0.06282},"optimized_scores":{"best_composite_score":0.46518,"best_fitness_score":0.98518,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":88.0,"contact_point_centroid":[0.49766,0.04488,-0.00143],"force_p95":0.49719,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.59078,"mean_force":0.15074,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.5011,0.04479,0.03643]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8280.0,"contact_point_centroid":[0.49872,0.06372,0.09655],"force_p95":0.07176,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32776,"mean_force":0.05158,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.49851,0.04455,0.09475]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8280.0,"contact_point_centroid":[0.49875,0.02542,0.09673],"force_p95":0.07141,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28995,"mean_force":0.05115,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.49851,0.04455,0.09475]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50116,0.04501,-0.00203],"force_p95":0.12962,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.14371,"mean_force":0.12523,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.50347,0.04503,0.03624]},{"body_a":"world","body_b":"grasp_target","contact_count":836.0,"contact_point_centroid":[0.50118,0.04505,-0.00185],"force_p95":0.13728,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12321,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.49872,0.0172,0.25009]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4240.0,"contact_point_centroid":[0.56695,0.25114,0.22649],"force_p95":0.07845,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13725,"mean_force":0.05279,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.56664,0.23216,0.22488]},{"body_a":"world","body_b":"grasp_target","contact_count":1288.0,"contact_point_centroid":[0.50118,0.04505,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.50313,0.0407,0.12254]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4240.0,"contact_point_centroid":[0.56688,0.21287,0.22704],"force_p95":0.07936,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12037,"mean_force":0.05206,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.56664,0.23216,0.22488]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4852.0,"contact_point_centroid":[0.50252,0.02573,0.03695],"force_p95":0.06865,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0901,"mean_force":0.04468,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.50231,0.04492,0.03498]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4868.0,"contact_point_centroid":[0.50249,0.06413,0.03679],"force_p95":0.06878,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08613,"mean_force":0.04483,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.50231,0.04492,0.03498]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":16440.0,"contact_point_centroid":[0.52799,0.16029,0.22019],"force_p95":0.0695,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08578,"mean_force":0.04825,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.52776,0.14113,0.21846]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":16440.0,"contact_point_centroid":[0.52802,0.12201,0.22049],"force_p95":0.07012,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08422,"mean_force":0.04819,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.52776,0.14113,0.21846]}],"total_contact_groups":12},"final_pose_error":0.01987,"key_states":{"actual_goal_position":[0.56442,0.24486,0.14677],"final_object_position":[0.56909,0.22992,0.14976],"final_tcp_position":[0.57627,0.23079,0.16491],"realised_goal_position":[0.56442,0.24486,0.14677],"realised_object_initial_position":[0.50118,0.04505,0.03]},"peak_contact_force":32.34483,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":210.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.03],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.23992,"object_z_max":0.03,"peak_contact_force":32.34483,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1288.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.49827,0.03619,0.19753],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.17176,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":322.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"peak_contact_force":0.12884,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":11520.0,"raw_peak_contact_force":0.14371,"subtask_id":"reach_object","tcp_end":[0.51083,0.04569,0.04466],"tcp_start":[0.49827,0.03619,0.19753],"tcp_to_object_dist_end":0.021,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50105,0.04493,0.02586],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.24209,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"peak_contact_force":0.07039,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":16648.0,"raw_peak_contact_force":0.59078,"tcp_end":[0.50228,0.04491,0.03494],"tcp_start":[0.51083,0.04569,0.04466],"tcp_to_object_dist_end":0.00916,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":414.0,"n_steps_budget":1000.0,"object_pos_end":[0.50222,0.04458,0.14599],"object_pos_start":[0.50105,0.04493,0.02586],"object_to_goal_dist_end":0.20972,"object_to_goal_dist_start":0.24209,"object_z_max":0.14571,"peak_contact_force":0.06975,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":32880.0,"raw_peak_contact_force":0.08578,"tcp_end":[0.49849,0.04455,0.15646],"tcp_start":[0.50228,0.04491,0.03494],"tcp_to_object_dist_end":0.01111,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":822.0,"n_steps_budget":1000.0,"object_pos_end":[0.56204,0.2332,0.26758],"object_pos_start":[0.50222,0.04458,0.14599],"object_to_goal_dist_end":0.12139,"object_to_goal_dist_start":0.20972,"object_z_max":0.26745,"peak_contact_force":0.07959,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":8480.0,"raw_peak_contact_force":0.13725,"subtask_id":"reach_goal","tcp_end":[0.55876,0.23333,0.2816],"tcp_start":[0.49849,0.04455,0.15646],"tcp_to_object_dist_end":0.0144,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":212.0,"n_steps_budget":1000.0,"object_pos_end":[0.56909,0.22992,0.14976],"object_pos_start":[0.56204,0.2332,0.26758],"object_to_goal_dist_end":0.01594,"object_to_goal_dist_start":0.12139,"object_z_max":0.26761,"peak_contact_force":0.12262,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":836.0,"raw_peak_contact_force":0.13845,"tcp_end":[0.57627,0.23079,0.16491],"tcp_start":[0.55876,0.23333,0.2816],"tcp_to_object_dist_end":0.01679,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.06197,"average_solve_count":355.0,"average_success_count":355.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.approach_speed":0.03407,"descend_place.place_xy_offset_x":0.00508,"descend_place.place_xy_offset_y":0.00313,"descend_to_grasp.descend_speed":0.02945,"descend_to_grasp.grasp_xy_offset_x":0.01458,"descend_to_grasp.grasp_xy_offset_y":-0.00072,"lift.lift_height":0.17937,"lift.lift_speed":0.06098},"optimized_scores":{"best_composite_score":0.4633,"best_fitness_score":0.9833,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":85.0,"contact_point_centroid":[0.47294,-0.01981,-0.00141],"force_p95":0.43496,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55567,"mean_force":0.12802,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.47568,-0.0199,0.03766]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":10600.0,"contact_point_centroid":[0.47346,-0.03897,0.11718],"force_p95":0.07168,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30137,"mean_force":0.05104,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.47323,-0.01982,0.11532]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":10600.0,"contact_point_centroid":[0.47344,-0.00068,0.11723],"force_p95":0.07108,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29623,"mean_force":0.05094,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.47323,-0.01982,0.11532]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3996.0,"contact_point_centroid":[0.62658,0.17343,0.2706],"force_p95":0.07958,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15888,"mean_force":0.05299,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.62633,0.1544,0.26881]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.62664,0.13515,0.27072],"force_p95":0.07883,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15473,"mean_force":0.05264,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.62633,0.1544,0.26875]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.47614,-0.02011,-0.00203],"force_p95":0.13127,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.14816,"mean_force":0.12544,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.47793,-0.01995,0.03736]},{"body_a":"world","body_b":"grasp_target","contact_count":776.0,"contact_point_centroid":[0.47616,-0.02015,-0.00183],"force_p95":0.13759,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12326,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.48942,-0.00754,0.25146]},{"body_a":"world","body_b":"grasp_target","contact_count":1304.0,"contact_point_centroid":[0.47616,-0.02015,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.48052,-0.01794,0.12366]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4843.0,"contact_point_centroid":[0.477,-0.00073,0.03814],"force_p95":0.06836,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10323,"mean_force":0.04476,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.47682,-0.01992,0.03623]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":18340.0,"contact_point_centroid":[0.54883,0.04851,0.26208],"force_p95":0.07045,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08881,"mean_force":0.04845,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.54857,0.06765,0.2602]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4881.0,"contact_point_centroid":[0.47703,-0.03913,0.03809],"force_p95":0.0685,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08782,"mean_force":0.04476,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.47682,-0.01992,0.03623]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":18340.0,"contact_point_centroid":[0.54881,0.08678,0.26207],"force_p95":0.06975,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07896,"mean_force":0.04828,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.54857,0.06765,0.2602]}],"total_contact_groups":12},"final_pose_error":0.01994,"key_states":{"actual_goal_position":[0.63142,0.15919,0.19002],"final_object_position":[0.62277,0.15837,0.19156],"final_tcp_position":[0.63094,0.15899,0.20887],"realised_goal_position":[0.63142,0.15919,0.19002],"realised_object_initial_position":[0.47616,-0.02015,0.03]},"peak_contact_force":81.14225,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":195.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.03],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28614,"object_z_max":0.03,"peak_contact_force":81.14225,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1304.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.47852,-0.01598,0.19941],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.17346,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":326.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.1304,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":11524.0,"raw_peak_contact_force":0.14816,"subtask_id":"reach_object","tcp_end":[0.48504,-0.02009,0.04495],"tcp_start":[0.47852,-0.01598,0.19941],"tcp_to_object_dist_end":0.02091,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.47604,-0.01996,0.02586],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28843,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.07022,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":21285.0,"raw_peak_contact_force":0.55567,"tcp_end":[0.47679,-0.01992,0.0362],"tcp_start":[0.48504,-0.02009,0.04495],"tcp_to_object_dist_end":0.01037,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":530.0,"n_steps_budget":1000.0,"object_pos_end":[0.47846,-0.01983,0.1838],"object_pos_start":[0.47604,-0.01996,0.02586],"object_to_goal_dist_end":0.23556,"object_to_goal_dist_start":0.28843,"object_z_max":0.18353,"peak_contact_force":0.06982,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":36680.0,"raw_peak_contact_force":0.08881,"tcp_end":[0.47344,-0.01982,0.19593],"tcp_start":[0.47679,-0.01992,0.0362],"tcp_to_object_dist_end":0.01312,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":38.0,"n_steps":917.0,"n_steps_budget":1000.0,"object_pos_end":[0.62634,0.1503,0.30866],"object_pos_start":[0.47846,-0.01983,0.1838],"object_to_goal_dist_end":0.11908,"object_to_goal_dist_start":0.23556,"object_z_max":0.30855,"peak_contact_force":0.07892,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":7996.0,"raw_peak_contact_force":0.15888,"subtask_id":"reach_goal","tcp_end":[0.62251,0.15035,0.32472],"tcp_start":[0.47344,-0.01982,0.19593],"tcp_to_object_dist_end":0.01651,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":200.0,"n_steps_budget":1000.0,"object_pos_end":[0.62277,0.15837,0.19156],"object_pos_start":[0.62634,0.1503,0.30866],"object_to_goal_dist_end":0.00882,"object_to_goal_dist_start":0.11908,"object_z_max":0.30866,"peak_contact_force":0.12263,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":776.0,"raw_peak_contact_force":0.13845,"tcp_end":[0.63094,0.15899,0.20887],"tcp_start":[0.62251,0.15035,0.32472],"tcp_to_object_dist_end":0.01915,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.12903,"average_solve_count":341.0,"average_success_count":341.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.approach_speed":0.01741,"descend_place.place_xy_offset_x":0.00534,"descend_place.place_xy_offset_y":0.00345,"descend_to_grasp.descend_speed":0.03736,"descend_to_grasp.grasp_xy_offset_x":0.01316,"descend_to_grasp.grasp_xy_offset_y":-0.00208,"lift.lift_height":0.16616,"lift.lift_speed":0.04877},"optimized_scores":{"best_composite_score":0.46223,"best_fitness_score":0.98223,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":87.0,"contact_point_centroid":[0.45536,-0.02725,-0.00148],"force_p95":0.47836,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.53194,"mean_force":0.13209,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.45763,-0.02693,0.03809]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":9680.0,"contact_point_centroid":[0.4556,-0.04598,0.11093],"force_p95":0.07081,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29077,"mean_force":0.05091,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.45537,-0.02683,0.10909]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":9680.0,"contact_point_centroid":[0.45558,-0.00769,0.11102],"force_p95":0.07167,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29063,"mean_force":0.051,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.45537,-0.02683,0.10909]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.45854,-0.0264,-0.00206],"force_p95":0.14021,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.17934,"mean_force":0.12779,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.45986,-0.02702,0.03788]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4160.0,"contact_point_centroid":[0.62373,0.22064,0.19514],"force_p95":0.08153,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16362,"mean_force":0.05426,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.62349,0.2016,0.19337]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4160.0,"contact_point_centroid":[0.6238,0.18237,0.19536],"force_p95":0.08287,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15768,"mean_force":0.05368,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.62349,0.2016,0.19337]},{"body_a":"world","body_b":"grasp_target","contact_count":824.0,"contact_point_centroid":[0.45856,-0.02632,-0.00184],"force_p95":0.13728,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12322,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.48245,-0.01007,0.25052]},{"body_a":"world","body_b":"grasp_target","contact_count":1280.0,"contact_point_centroid":[0.45856,-0.02632,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.46429,-0.02411,0.12262]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4824.0,"contact_point_centroid":[0.45899,-0.04617,0.03869],"force_p95":0.06948,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10946,"mean_force":0.04481,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.45879,-0.02698,0.03683]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":18800.0,"contact_point_centroid":[0.53873,0.06895,0.21862],"force_p95":0.06965,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09537,"mean_force":0.04813,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.53848,0.0881,0.21673]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":18800.0,"contact_point_centroid":[0.53871,0.10723,0.21862],"force_p95":0.06948,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09105,"mean_force":0.04803,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.53848,0.0881,0.21673]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4920.0,"contact_point_centroid":[0.45897,-0.00776,0.03876],"force_p95":0.06978,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07807,"mean_force":0.04469,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.45879,-0.02698,0.03683]}],"total_contact_groups":12},"final_pose_error":0.0195,"key_states":{"actual_goal_position":[0.63013,0.20822,0.11412],"final_object_position":[0.62239,0.20672,0.1148],"final_tcp_position":[0.6287,0.20734,0.13188],"realised_goal_position":[0.63013,0.20822,0.11412],"realised_object_initial_position":[0.45856,-0.02632,0.03]},"peak_contact_force":0.53194,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":207.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.03],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30252,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1280.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.46401,-0.02124,0.19803],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.17218,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":320.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.13801,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":11544.0,"raw_peak_contact_force":0.17934,"subtask_id":"reach_object","tcp_end":[0.4668,-0.02725,0.04498],"tcp_start":[0.46401,-0.02124,0.19803],"tcp_to_object_dist_end":0.02069,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.45844,-0.02684,0.02575],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.3042,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.06991,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":19447.0,"raw_peak_contact_force":0.53194,"tcp_end":[0.45876,-0.02698,0.0368],"tcp_start":[0.4668,-0.02725,0.04498],"tcp_to_object_dist_end":0.01106,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":484.0,"n_steps_budget":1000.0,"object_pos_end":[0.45619,-0.02674,0.17065],"object_pos_start":[0.45844,-0.02684,0.02575],"object_to_goal_dist_end":0.29775,"object_to_goal_dist_start":0.3042,"object_z_max":0.17036,"peak_contact_force":0.06951,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":37600.0,"raw_peak_contact_force":0.09537,"tcp_end":[0.4555,-0.02682,0.18327],"tcp_start":[0.45876,-0.02698,0.0368],"tcp_to_object_dist_end":0.01265,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":940.0,"n_steps_budget":1000.0,"object_pos_end":[0.62126,0.19657,0.23559],"object_pos_start":[0.45619,-0.02674,0.17065],"object_to_goal_dist_end":0.12234,"object_to_goal_dist_start":0.29775,"object_z_max":0.23553,"peak_contact_force":0.07763,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":8320.0,"raw_peak_contact_force":0.16362,"subtask_id":"reach_goal","tcp_end":[0.61971,0.19661,0.25164],"tcp_start":[0.4555,-0.02682,0.18327],"tcp_to_object_dist_end":0.01613,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":208.0,"n_steps_budget":1000.0,"object_pos_end":[0.62239,0.20672,0.1148],"object_pos_start":[0.62126,0.19657,0.23559],"object_to_goal_dist_end":0.00791,"object_to_goal_dist_start":0.12234,"object_z_max":0.23559,"peak_contact_force":0.12262,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":824.0,"raw_peak_contact_force":0.13845,"tcp_end":[0.6287,0.20734,0.13188],"tcp_start":[0.61971,0.19661,0.25164],"tcp_to_object_dist_end":0.01822,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```