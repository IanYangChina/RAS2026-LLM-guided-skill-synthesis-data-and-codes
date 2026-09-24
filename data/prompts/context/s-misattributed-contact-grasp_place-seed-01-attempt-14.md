## Search State

- **Seed**: 1
- **Iteration**: 15 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 14 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | impedance_control | impedance_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 8 | 0.4499 | 1.00 | ❌ rejected |
| 13 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | impedance_control | impedance_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 8 | 0.4634 | 1.00 | ❌ rejected |
| 12 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | impedance_control | impedance_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 8 | 0.4499 | 1.00 | ❌ rejected |
| 11 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | impedance_control | impedance_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 8 | 0.4636 | 1.00 | ❌ rejected |
| 10 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | impedance_control | impedance_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 8 | 0.4636 | 1.00 | ✅ accepted |

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

## Current Skill (Q=0.450) — your mutation base

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

- **Composite score**: 0.450
- **task_score** (E): 1.000
- **fitness_score**: 0.970  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.520

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_object | 1.00 | 1.00 | 0.0888 |
| descend_to_grasp | 1.00 | 1.00 | 0.1623 |
| grasp | 1.00 | 1.00 | 0.0133 |
| lift | 1.00 | 1.00 | 0.1476 |
| approach_goal | 1.00 | 1.00 | 0.2442 |
| descend_place | 1.00 | 1.00 | 0.1166 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.485, -0.000, 0.217) | (0.479, -0.000, 0.030)→(0.479, -0.000, 0.026) | 0.276→0.278 | 1.00 / 4.000 | 12.675 | 0.123 |
| descend_to_grasp | descend | 1.00 / step_budget | (0.485, -0.000, 0.217)→(0.487, -0.001, 0.055) | (0.479, -0.000, 0.026)→(0.479, -0.000, 0.026) | 0.278→0.278 | 1.00 / 43.333 | 0.188 | 0.204 |
| grasp | grasp | 1.00 / step_budget | (0.487, -0.001, 0.055)→(0.478, -0.001, 0.045) | (0.479, -0.000, 0.026)→(0.479, -0.001, 0.026) | 0.278→0.278 | 1.00 / 41.333 | 0.072 | 0.478 |
| lift | lift | 1.00 / step_budget | (0.478, -0.001, 0.045)→(0.476, -0.001, 0.193) | (0.479, -0.001, 0.026)→(0.476, -0.001, 0.172) | 0.278→0.249 | 1.00 / 37.667 | 0.080 | 0.116 |
| approach_goal | approach | 1.00 / step_budget | (0.476, -0.001, 0.193)→(0.595, 0.185, 0.282) | (0.476, -0.001, 0.172)→(0.597, 0.185, 0.261) | 0.249→0.113 | 1.00 / 37.000 | 0.088 | 0.217 |
| descend_place | descend | 1.00 / step_budget | (0.595, 0.185, 0.282)→(0.607, 0.202, 0.168) | (0.597, 0.185, 0.261)→(0.600, 0.201, 0.145) | 0.113→0.013 | 1.00 / 4.000 | 0.122 | 0.138 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.466
- lift_clearance: 1.000
- transport_retention: 1.000
- terminal_score: 1.000
- phase_score: 0.075
- phase_breakdown.reach_goal_score: 0.072
- phase_breakdown.reach_object_score: 0.081
- grasp_place_fitness: 0.972

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.972
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 1.000
- **Median Q (composite search score)**: 0.449
- **K-run variance**: 0.0000
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.280


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.12963,"average_solve_count":324.0,"average_success_count":324.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.approach_speed":0.0272,"descend_place.place_xy_offset_x":0.00893,"descend_place.place_xy_offset_y":-0.00167,"descend_to_grasp.descend_speed":0.03968,"descend_to_grasp.grasp_xy_offset_x":0.01453,"descend_to_grasp.grasp_xy_offset_y":0.00477,"lift.lift_height":0.14936,"lift.lift_speed":0.06032},"optimized_scores":{"best_composite_score":0.45203,"best_fitness_score":0.97203,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":72.0,"contact_point_centroid":[0.49834,0.04496,-0.00158],"force_p95":0.41316,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.53264,"mean_force":0.17743,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.49934,0.04495,0.04474]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5252.0,"contact_point_centroid":[0.4972,0.06394,0.10472],"force_p95":0.08826,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31489,"mean_force":0.05345,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.49736,0.04473,0.10248]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5305.0,"contact_point_centroid":[0.49732,0.02557,0.10491],"force_p95":0.08662,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27375,"mean_force":0.05245,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.49735,0.04473,0.1024]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50116,0.04504,-0.00203],"force_p95":0.21488,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.21521,"mean_force":0.16346,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.50153,0.04517,0.0449]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3593.0,"contact_point_centroid":[0.56161,0.25009,0.22493],"force_p95":0.09465,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18186,"mean_force":0.06187,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.56083,0.2311,0.22392]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4028.0,"contact_point_centroid":[0.56127,0.21214,0.22328],"force_p95":0.08932,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14089,"mean_force":0.05521,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.56102,0.23132,0.22165]},{"body_a":"world","body_b":"grasp_target","contact_count":408.0,"contact_point_centroid":[0.50118,0.04505,-0.00169],"force_p95":0.13814,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12386,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.50029,0.0134,0.26146]},{"body_a":"world","body_b":"grasp_target","contact_count":956.0,"contact_point_centroid":[0.50118,0.04505,-0.00199],"force_p95":0.12264,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12264,"mean_force":0.12261,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.50376,0.0373,0.13725]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4860.0,"contact_point_centroid":[0.50051,0.06427,0.0455],"force_p95":0.07449,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11769,"mean_force":0.05191,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.50041,0.04506,0.04368]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4863.0,"contact_point_centroid":[0.50071,0.02588,0.04565],"force_p95":0.0728,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11228,"mean_force":0.0506,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.50041,0.04506,0.04368]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":9827.0,"contact_point_centroid":[0.52569,0.11496,0.22014],"force_p95":0.06809,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10896,"mean_force":0.04545,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.52534,0.13397,0.21757]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8317.0,"contact_point_centroid":[0.52594,0.15315,0.22049],"force_p95":0.0769,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09888,"mean_force":0.05248,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.52533,0.1339,0.21753]}],"total_contact_groups":12},"final_pose_error":0.01977,"key_states":{"actual_goal_position":[0.56442,0.24486,0.14677],"final_object_position":[0.55824,0.2371,0.14283],"final_tcp_position":[0.56691,0.23812,0.16476],"realised_goal_position":[0.56442,0.24486,0.14677],"realised_object_initial_position":[0.50118,0.04505,0.03]},"peak_contact_force":37.77898,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":103.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.03],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.23992,"object_z_max":0.03,"peak_contact_force":37.77898,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":956.0,"raw_peak_contact_force":0.12264,"subtask_id":"reach_object","tcp_end":[0.50012,0.02946,0.2162],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.19082,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":239.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"peak_contact_force":0.21413,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":11523.0,"raw_peak_contact_force":0.21521,"subtask_id":"reach_object","tcp_end":[0.50951,0.04581,0.05442],"tcp_start":[0.50012,0.02946,0.2162],"tcp_to_object_dist_end":0.0296,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50108,0.04505,0.02587],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.24199,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"peak_contact_force":0.06745,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10629.0,"raw_peak_contact_force":0.53264,"tcp_end":[0.50038,0.04506,0.04365],"tcp_start":[0.50951,0.04581,0.05442],"tcp_to_object_dist_end":0.0178,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":39.0,"n_steps":250.0,"n_steps_budget":1000.0,"object_pos_end":[0.49844,0.04466,0.14455],"object_pos_start":[0.50108,0.04505,0.02587],"object_to_goal_dist_end":0.2108,"object_to_goal_dist_start":0.24199,"object_z_max":0.14407,"peak_contact_force":0.07983,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":18144.0,"raw_peak_contact_force":0.10896,"tcp_end":[0.49731,0.04472,0.16322],"tcp_start":[0.50038,0.04506,0.04365],"tcp_to_object_dist_end":0.01871,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":456.0,"n_steps_budget":1000.0,"object_pos_end":[0.55805,0.22495,0.25624],"object_pos_start":[0.49844,0.04466,0.14455],"object_to_goal_dist_end":0.11144,"object_to_goal_dist_start":0.2108,"object_z_max":0.256,"peak_contact_force":0.0902,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":7621.0,"raw_peak_contact_force":0.18186,"subtask_id":"reach_goal","tcp_end":[0.55623,0.22492,0.27647],"tcp_start":[0.49731,0.04472,0.16322],"tcp_to_object_dist_end":0.02032,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":205.0,"n_steps_budget":1000.0,"object_pos_end":[0.55824,0.2371,0.14283],"object_pos_start":[0.55805,0.22495,0.25624],"object_to_goal_dist_end":0.01067,"object_to_goal_dist_start":0.11144,"object_z_max":0.2564,"peak_contact_force":0.12229,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":408.0,"raw_peak_contact_force":0.13845,"tcp_end":[0.56691,0.23812,0.16476],"tcp_start":[0.55623,0.22492,0.27647],"tcp_to_object_dist_end":0.0236,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.11295,"average_solve_count":363.0,"average_success_count":363.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.approach_speed":0.02785,"descend_place.place_xy_offset_x":-0.00439,"descend_place.place_xy_offset_y":0.00251,"descend_to_grasp.descend_speed":0.02318,"descend_to_grasp.grasp_xy_offset_x":0.01135,"descend_to_grasp.grasp_xy_offset_y":-0.00138,"lift.lift_height":0.19915,"lift.lift_speed":0.05933},"optimized_scores":{"best_composite_score":0.44946,"best_fitness_score":0.96946,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":72.0,"contact_point_centroid":[0.47338,-0.01979,-0.00156],"force_p95":0.37546,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.4277,"mean_force":0.14758,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.4739,-0.01974,0.04651]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5952.0,"contact_point_centroid":[0.47301,-0.00043,0.12992],"force_p95":0.09513,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29382,"mean_force":0.06224,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.47211,-0.01967,0.12705]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":7409.0,"contact_point_centroid":[0.47266,-0.03866,0.13049],"force_p95":0.08703,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28524,"mean_force":0.0523,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.4721,-0.01967,0.12831]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3349.0,"contact_point_centroid":[0.61967,0.16839,0.26689],"force_p95":0.09484,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21537,"mean_force":0.06304,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.61874,0.14936,0.26634]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3940.0,"contact_point_centroid":[0.61888,0.13026,0.26729],"force_p95":0.08694,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20003,"mean_force":0.05452,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.61874,0.14936,0.26634]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.47615,-0.02004,-0.00205],"force_p95":0.13525,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.16779,"mean_force":0.12659,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.47601,-0.01979,0.04643]},{"body_a":"world","body_b":"grasp_target","contact_count":384.0,"contact_point_centroid":[0.47616,-0.02015,-0.00168],"force_p95":0.13822,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12396,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.49294,-0.0059,0.26243]},{"body_a":"world","body_b":"grasp_target","contact_count":968.0,"contact_point_centroid":[0.47616,-0.02015,-0.00199],"force_p95":0.12264,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12264,"mean_force":0.1226,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.48302,-0.0163,0.13934]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4269.0,"contact_point_centroid":[0.47569,-0.0005,0.04852],"force_p95":0.07499,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11346,"mean_force":0.05022,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.47493,-0.01976,0.04534]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":9800.0,"contact_point_centroid":[0.54303,0.04203,0.26719],"force_p95":0.0723,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10518,"mean_force":0.04843,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.54286,0.06102,0.26588]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8330.0,"contact_point_centroid":[0.54387,0.08016,0.26713],"force_p95":0.08014,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09804,"mean_force":0.05604,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.54286,0.06102,0.26588]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5131.0,"contact_point_centroid":[0.47515,-0.03884,0.04755],"force_p95":0.06589,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0824,"mean_force":0.04281,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.47493,-0.01976,0.04535]}],"total_contact_groups":12},"final_pose_error":0.01946,"key_states":{"actual_goal_position":[0.63142,0.15919,0.19002],"final_object_position":[0.6126,0.15615,0.18492],"final_tcp_position":[0.62215,0.1569,0.20823],"realised_goal_position":[0.63142,0.15919,0.19002],"realised_object_initial_position":[0.47616,-0.02015,0.03]},"peak_contact_force":0.4277,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":97.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02601],"object_pos_start":[0.47616,-0.02015,0.03],"object_to_goal_dist_end":0.28839,"object_to_goal_dist_start":0.28614,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":968.0,"raw_peak_contact_force":0.12264,"subtask_id":"reach_object","tcp_end":[0.4841,-0.01303,0.21783],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.19211,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":242.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.02601],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28839,"object_z_max":0.02602,"peak_contact_force":0.1327,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":11200.0,"raw_peak_contact_force":0.16779,"subtask_id":"reach_object","tcp_end":[0.48367,-0.01991,0.0551],"tcp_start":[0.4841,-0.01303,0.21783],"tcp_to_object_dist_end":0.03004,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.47606,-0.01969,0.0258],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28828,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.07901,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":13433.0,"raw_peak_contact_force":0.4277,"tcp_end":[0.4749,-0.01976,0.04531],"tcp_start":[0.48367,-0.01991,0.0551],"tcp_to_object_dist_end":0.01955,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":345.0,"n_steps_budget":1000.0,"object_pos_end":[0.47449,-0.01956,0.19396],"object_pos_start":[0.47606,-0.01969,0.0258],"object_to_goal_dist_end":0.2379,"object_to_goal_dist_start":0.28828,"object_z_max":0.19348,"peak_contact_force":0.08119,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":18130.0,"raw_peak_contact_force":0.10518,"tcp_end":[0.47237,-0.01967,0.2149],"tcp_start":[0.4749,-0.01976,0.04531],"tcp_to_object_dist_end":0.02105,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":490.0,"n_steps_budget":1000.0,"object_pos_end":[0.61844,0.14235,0.29841],"object_pos_start":[0.47449,-0.01956,0.19396],"object_to_goal_dist_end":0.11047,"object_to_goal_dist_start":0.2379,"object_z_max":0.2982,"peak_contact_force":0.09168,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":7289.0,"raw_peak_contact_force":0.21537,"subtask_id":"reach_goal","tcp_end":[0.61595,0.1425,0.32058],"tcp_start":[0.47237,-0.01967,0.2149],"tcp_to_object_dist_end":0.02231,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":197.0,"n_steps_budget":1000.0,"object_pos_end":[0.6126,0.15615,0.18492],"object_pos_start":[0.61844,0.14235,0.29841],"object_to_goal_dist_end":0.01974,"object_to_goal_dist_start":0.11047,"object_z_max":0.29851,"peak_contact_force":0.12218,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":384.0,"raw_peak_contact_force":0.13845,"tcp_end":[0.62215,0.1569,0.20823],"tcp_start":[0.61595,0.1425,0.32058],"tcp_to_object_dist_end":0.02521,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.11253,"average_solve_count":391.0,"average_success_count":391.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.approach_speed":0.03902,"descend_place.place_xy_offset_x":0.00983,"descend_place.place_xy_offset_y":0.00956,"descend_to_grasp.descend_speed":0.03082,"descend_to_grasp.grasp_xy_offset_x":0.01278,"descend_to_grasp.grasp_xy_offset_y":-0.00394,"lift.lift_height":0.1829,"lift.lift_speed":0.03983},"optimized_scores":{"best_composite_score":0.44823,"best_fitness_score":0.96823,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":83.0,"contact_point_centroid":[0.45562,-0.02736,-0.00173],"force_p95":0.39592,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.47497,"mean_force":0.19777,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.45882,-0.02751,0.04695]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6752.0,"contact_point_centroid":[0.45753,-0.00837,0.12285],"force_p95":0.08699,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28529,"mean_force":0.05211,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.45709,-0.02741,0.12058]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5799.0,"contact_point_centroid":[0.45682,-0.04664,0.1238],"force_p95":0.08978,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28098,"mean_force":0.05915,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.45708,-0.02741,0.12184]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4380.0,"contact_point_centroid":[0.62166,0.21749,0.19245],"force_p95":0.10042,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25433,"mean_force":0.05796,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.62152,0.19854,0.19169]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.45854,-0.02642,-0.00212],"force_p95":0.21853,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.22898,"mean_force":0.16718,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.46089,-0.02759,0.04693]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3723.0,"contact_point_centroid":[0.62079,0.17934,0.19282],"force_p95":0.11656,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20477,"mean_force":0.06516,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.62152,0.19854,0.19169]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4096.0,"contact_point_centroid":[0.45911,-0.04683,0.04766],"force_p95":0.08503,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17887,"mean_force":0.05888,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.45984,-0.02755,0.04591]},{"body_a":"world","body_b":"grasp_target","contact_count":408.0,"contact_point_centroid":[0.45856,-0.02632,-0.00169],"force_p95":0.13814,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12386,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.48736,-0.00799,0.26129]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8963.0,"contact_point_centroid":[0.53352,0.06052,0.22473],"force_p95":0.08128,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13512,"mean_force":0.05629,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.53423,0.07972,0.22336]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":10769.0,"contact_point_centroid":[0.53331,0.0969,0.22435],"force_p95":0.07064,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12395,"mean_force":0.04709,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.53294,0.07794,0.22293]},{"body_a":"world","body_b":"grasp_target","contact_count":964.0,"contact_point_centroid":[0.45856,-0.02632,-0.00199],"force_p95":0.12264,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12264,"mean_force":0.12261,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.46939,-0.02239,0.13853]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5460.0,"contact_point_centroid":[0.46062,-0.00848,0.04842],"force_p95":0.0728,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08038,"mean_force":0.04648,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.45985,-0.02755,0.04592]}],"total_contact_groups":12},"final_pose_error":0.0199,"key_states":{"actual_goal_position":[0.63013,0.20822,0.11412],"final_object_position":[0.62873,0.21039,0.10734],"final_tcp_position":[0.63134,0.21072,0.13061],"realised_goal_position":[0.63013,0.20822,0.11412],"realised_object_initial_position":[0.45856,-0.02632,0.03]},"peak_contact_force":0.47497,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":103.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.03],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30252,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":964.0,"raw_peak_contact_force":0.12264,"subtask_id":"reach_object","tcp_end":[0.47207,-0.01756,0.2158],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.19046,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":241.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.21762,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":11356.0,"raw_peak_contact_force":0.22898,"subtask_id":"reach_object","tcp_end":[0.46836,-0.02781,0.0551],"tcp_start":[0.47207,-0.01756,0.2158],"tcp_to_object_dist_end":0.03072,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.45844,-0.02729,0.02554],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30461,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.07023,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12634.0,"raw_peak_contact_force":0.47497,"tcp_end":[0.45981,-0.02755,0.04588],"tcp_start":[0.46836,-0.02781,0.0551],"tcp_to_object_dist_end":0.02039,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":315.0,"n_steps_budget":1000.0,"object_pos_end":[0.45618,-0.02708,0.17821],"object_pos_start":[0.45844,-0.02729,0.02554],"object_to_goal_dist_end":0.29955,"object_to_goal_dist_start":0.30461,"object_z_max":0.17772,"peak_contact_force":0.07875,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":19732.0,"raw_peak_contact_force":0.13512,"tcp_end":[0.45724,-0.02739,0.19938],"tcp_start":[0.45981,-0.02755,0.04588],"tcp_to_object_dist_end":0.0212,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":527.0,"n_steps_budget":1000.0,"object_pos_end":[0.61456,0.18763,0.22788],"object_pos_start":[0.45618,-0.02708,0.17821],"object_to_goal_dist_end":0.11665,"object_to_goal_dist_start":0.29955,"object_z_max":0.22779,"peak_contact_force":0.0814,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":8103.0,"raw_peak_contact_force":0.25433,"subtask_id":"reach_goal","tcp_end":[0.61377,0.18768,0.25044],"tcp_start":[0.45724,-0.02739,0.19938],"tcp_to_object_dist_end":0.02258,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":219.0,"n_steps_budget":1000.0,"object_pos_end":[0.62873,0.21039,0.10734],"object_pos_start":[0.61456,0.18763,0.22788],"object_to_goal_dist_end":0.00726,"object_to_goal_dist_start":0.11665,"object_z_max":0.22788,"peak_contact_force":0.12229,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":408.0,"raw_peak_contact_force":0.13845,"tcp_end":[0.63134,0.21072,0.13061],"tcp_start":[0.61377,0.18768,0.25044],"tcp_to_object_dist_end":0.02343,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```