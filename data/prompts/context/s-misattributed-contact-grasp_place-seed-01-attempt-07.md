## Search State

- **Seed**: 1
- **Iteration**: 8 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 7 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 4 | 0.2785 | 0.41 | ❌ rejected |
| 6 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 3 | 0.3531 | 0.41 | ❌ rejected |
| 5 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | impedance_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 3 | 0.2507 | 0.20 | ❌ rejected |
| 4 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 3 | 0.3380 | 0.43 | ✅ accepted |
| 3 | rotate → align → push → align → lift | impedance_motion | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | impedance_control | position_control | position_control | position_control | position_control | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 3 | -0.0465 | 0.16 | ❌ rejected |

**Proposal policy**: task_score is 0.41 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.279) — your mutation base

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

- **Composite score**: 0.279
- **task_score** (E): 0.409
- **fitness_score**: 0.659  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.380

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_object | 1.00 | 1.00 | 0.1084 |
| descend_to_grasp | 1.00 | 1.00 | 0.2115 |
| grasp | 1.00 | 1.00 | 0.0000 |
| lift | 1.00 | 0.67 | 0.2305 |
| approach_goal | 1.00 | 1.00 | 0.2878 |
| descend_place | 1.00 | 1.00 | 0.1629 |
| release | 1.00 | 1.00 | 0.0195 |
| retract | 1.00 | 1.00 | 0.1901 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.480, -0.000, 0.198) | (0.479, -0.000, 0.030)→(0.479, -0.000, 0.026) | 0.276→0.278 | 1.00 / 45.000 | 5.253 | 6.108 |
| descend_to_grasp | descend | 1.00 / step_budget | (0.480, -0.000, 0.198)→(0.478, -0.001, -0.013) | (0.479, -0.000, 0.026)→(0.480, -0.000, 0.020) | 0.278→0.280 | 1.00 / 45.000 | 3.388 | 4.068 |
| grasp | grasp | 1.00 / step_budget | (0.482, -0.001, -0.010)→(0.482, -0.001, -0.010) | (0.480, -0.000, 0.020)→(0.479, -0.000, 0.021) | 0.280→0.280 | 1.00 / 39.000 | 55983.964 | 3.327 |
| lift | lift | 1.00 / step_budget | (0.482, -0.001, -0.010)→(0.479, -0.001, 0.221) | (0.479, -0.000, 0.021)→(0.492, -0.001, 0.224) | 0.280→0.252 | 0.67 / 6.000 | 91004.181 | 1.563 |
| approach_goal | approach | 1.00 / step_budget | (0.479, -0.001, 0.221)→(0.602, 0.194, 0.384) | (0.492, -0.001, 0.224)→(0.595, 0.160, 0.048) | 0.252→0.113 | 1.00 / 8.333 | 91003.183 | 0.781 |
| descend_place | descend | 1.00 / step_budget | (0.602, 0.194, 0.384)→(0.604, 0.203, 0.222) | (0.595, 0.160, 0.048)→(0.594, 0.162, 0.023) | 0.113→0.137 | 1.00 / 4.000 | 0.123 | 0.123 |
| release | release | 1.00 / step_budget | (0.604, 0.203, 0.222)→(0.599, 0.201, 0.241) | (0.594, 0.162, 0.023)→(0.594, 0.162, 0.023) | 0.137→0.137 | 1.00 / 4.000 | 0.123 | 0.123 |
| retract | retract | 1.00 / step_budget | (0.599, 0.201, 0.241)→(0.608, 0.204, 0.430) | (0.594, 0.162, 0.023)→(0.594, 0.162, 0.023) | 0.137→0.137 | 1.00 / 4.000 | 0.123 | 0.138 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 0.000
- place_accuracy: 0.000
- lift_clearance: 0.000
- transport_retention: 1.000
- terminal_score: 0.517
- phase_score: 0.382
- phase_breakdown.reach_goal_score: 0.537
- phase_breakdown.reach_object_score: 0.022
- grasp_place_fitness: 0.713

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.713
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.517
- **Median Q (composite search score)**: 0.276
- **K-run variance**: 0.0019
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.370


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.93284,"average_solve_count":268.0,"average_success_count":268.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"descend_place.place_descend_dist":0.2066,"descend_place.place_xy_offset_x":-0.00035,"descend_place.place_xy_offset_y":0.0077,"descend_to_grasp.grasp_descend_dist":0.05971},"optimized_scores":{"best_composite_score":0.27642,"best_fitness_score":0.65642,"best_task_score":0.406},"replay_outcomes":[{"contacts":{"omitted_contact_groups":8,"reported_contact_groups":[{"body_a":"world","body_b":"right_finger","contact_count":780.0,"contact_point_centroid":[0.49756,0.08546,-0.00463],"force_p95":5.50113,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":6.36172,"mean_force":3.76416,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.49764,0.04329,-0.00545]},{"body_a":"world","body_b":"left_finger","contact_count":768.0,"contact_point_centroid":[0.49752,0.00101,-0.00461],"force_p95":5.46899,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":6.2397,"mean_force":3.75442,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.49765,0.04329,-0.00557]},{"body_a":"world","body_b":"left_finger","contact_count":11000.0,"contact_point_centroid":[0.50282,0.00211,-0.00664],"force_p95":3.8661,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":4.23856,"mean_force":2.69443,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.50298,0.04373,-0.01093]},{"body_a":"world","body_b":"right_finger","contact_count":11000.0,"contact_point_centroid":[0.50284,0.08533,-0.00669],"force_p95":3.89198,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":4.23002,"mean_force":2.71402,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.50298,0.04373,-0.01093]},{"body_a":"world","body_b":"right_finger","contact_count":758.0,"contact_point_centroid":[0.5038,0.08417,-0.0038],"force_p95":2.5794,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":3.39497,"mean_force":0.76839,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.50384,0.04369,-0.00332]},{"body_a":"world","body_b":"left_finger","contact_count":757.0,"contact_point_centroid":[0.50378,0.00322,-0.00376],"force_p95":2.70267,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":3.38455,"mean_force":0.78254,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.50384,0.04369,-0.00333]},{"body_a":"world","body_b":"grasp_target","contact_count":803.0,"contact_point_centroid":[0.56435,0.18464,-0.00415],"force_p95":0.84903,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.37455,"mean_force":0.22127,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.55191,0.2092,0.3587]},{"body_a":"grasp_target","body_b":"hand","contact_count":70.0,"contact_point_centroid":[0.51215,0.04294,0.04608],"force_p95":0.89456,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.91806,"mean_force":0.64365,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.49712,0.04307,0.00111]},{"body_a":"grasp_target","body_b":"hand","contact_count":550.0,"contact_point_centroid":[0.50604,0.04523,0.03916],"force_p95":0.74346,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.75858,"mean_force":0.68571,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.50298,0.04373,-0.01093]},{"body_a":"world","body_b":"grasp_target","contact_count":424.0,"contact_point_centroid":[0.49957,0.04453,-0.00292],"force_p95":0.26912,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.65764,"mean_force":0.15297,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.50249,0.04358,0.0074]},{"body_a":"grasp_target","body_b":"hand","contact_count":82.0,"contact_point_centroid":[0.51332,0.05115,0.04737],"force_p95":0.41615,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.64872,"mean_force":0.20065,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.50296,0.04362,0.00338]},{"body_a":"world","body_b":"grasp_target","contact_count":1644.0,"contact_point_centroid":[0.50113,0.04506,-0.00225],"force_p95":0.31171,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.44859,"mean_force":0.14914,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.49651,0.0399,0.08984]},{"body_a":"world","body_b":"grasp_target","contact_count":2200.0,"contact_point_centroid":[0.50011,0.04524,-0.00469],"force_p95":0.3653,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.38544,"mean_force":0.29459,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.50298,0.04373,-0.01093]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6394.0,"contact_point_centroid":[0.51788,0.07324,0.25871],"force_p95":0.15038,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.37568,"mean_force":0.07904,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.51411,0.09182,0.25787]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":12570.0,"contact_point_centroid":[0.50053,0.06261,0.12062],"force_p95":0.07862,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33336,"mean_force":0.0512,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.50038,0.04344,0.11865]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":12652.0,"contact_point_centroid":[0.50053,0.02433,0.12324],"force_p95":0.07787,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31051,"mean_force":0.0495,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.50038,0.04344,0.12133]}],"total_contact_groups":24},"final_pose_error":0.01995,"key_states":{"actual_goal_position":[0.56442,0.24486,0.14677],"final_object_position":[0.56837,0.18417,0.02602],"final_tcp_position":[0.56365,0.24445,0.42684],"realised_goal_position":[0.56442,0.24486,0.14677],"realised_object_initial_position":[0.50118,0.04505,0.03]},"peak_contact_force":273012.41984,"phases":[{"contact_detected":true,"contact_event_count":45.0,"n_steps":210.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.03],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.23992,"object_z_max":0.03,"peak_contact_force":5.50419,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3262.0,"raw_peak_contact_force":6.36172,"subtask_id":"reach_object","tcp_end":[0.49827,0.03619,0.19753],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.17176,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":45.0,"n_steps":411.0,"n_steps_budget":1000.0,"object_pos_end":[0.50268,0.04527,0.01987],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.24445,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"peak_contact_force":3.48019,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":24750.0,"raw_peak_contact_force":4.23856,"subtask_id":"reach_object","tcp_end":[0.49912,0.04356,-0.01404],"tcp_start":[0.49827,0.03619,0.19753],"tcp_to_object_dist_end":0.03414,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":150.0,"n_steps_budget":50.0,"object_pos_end":[0.50205,0.04528,0.02072],"object_pos_start":[0.50268,0.04527,0.01987],"object_to_goal_dist_end":0.24416,"object_to_goal_dist_start":0.24445,"object_z_max":0.02074,"peak_contact_force":0.08301,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":27243.0,"raw_peak_contact_force":3.39497,"tcp_end":[0.50426,0.04381,-0.0101],"tcp_start":[0.50421,0.04381,-0.01012],"tcp_to_object_dist_end":0.03093,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":726.0,"n_steps_budget":1000.0,"object_pos_end":[0.51452,0.04367,0.22335],"object_pos_start":[0.50178,0.04528,0.02074],"object_to_goal_dist_end":0.22099,"object_to_goal_dist_start":0.24422,"object_z_max":0.22308,"peak_contact_force":273012.41984,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":13897.0,"raw_peak_contact_force":2.37455,"tcp_end":[0.50113,0.04351,0.22032],"tcp_start":[0.50426,0.04381,-0.0101],"tcp_to_object_dist_end":0.01373,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":822.0,"n_steps_budget":1000.0,"object_pos_end":[0.56831,0.18417,0.02603],"object_pos_start":[0.51452,0.04367,0.22335],"object_to_goal_dist_end":0.1352,"object_to_goal_dist_start":0.22099,"object_z_max":0.29298,"peak_contact_force":273009.30346,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2482.0,"raw_peak_contact_force":0.12791,"subtask_id":"reach_goal","tcp_end":[0.56023,0.23449,0.38049],"tcp_start":[0.50113,0.04351,0.22032],"tcp_to_object_dist_end":0.35811,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":300.0,"n_steps_budget":1000.0,"object_pos_end":[0.56837,0.18417,0.02602],"object_pos_start":[0.56831,0.18417,0.02603],"object_to_goal_dist_end":0.13521,"object_to_goal_dist_start":0.1352,"object_z_max":0.02603,"peak_contact_force":0.12263,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1021.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_goal","tcp_end":[0.56122,0.24874,0.20908],"tcp_start":[0.56023,0.23449,0.38049],"tcp_to_object_dist_end":0.19424,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.56837,0.18417,0.02602],"object_pos_start":[0.56837,0.18417,0.02602],"object_to_goal_dist_end":0.13521,"object_to_goal_dist_start":0.13521,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2924.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.55618,0.24628,0.22901],"tcp_start":[0.56122,0.24874,0.20908],"tcp_to_object_dist_end":0.21263,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":731.0,"n_steps_budget":1000.0,"object_pos_end":[0.56837,0.18417,0.02602],"object_pos_start":[0.56837,0.18417,0.02602],"object_to_goal_dist_end":0.13521,"object_to_goal_dist_start":0.13521,"object_z_max":0.02602,"peak_contact_force":0.12262,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":836.0,"raw_peak_contact_force":0.13845,"tcp_end":[0.56365,0.24445,0.42684],"tcp_start":[0.55618,0.24628,0.22901],"tcp_to_object_dist_end":0.40536,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.93156,"average_solve_count":263.0,"average_success_count":263.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"descend_place.place_descend_dist":0.17625,"descend_place.place_xy_offset_x":-0.00021,"descend_place.place_xy_offset_y":0.0027,"descend_to_grasp.grasp_descend_dist":0.05903},"optimized_scores":{"best_composite_score":0.22625,"best_fitness_score":0.60625,"best_task_score":0.30526},"replay_outcomes":[{"contacts":{"omitted_contact_groups":8,"reported_contact_groups":[{"body_a":"world","body_b":"left_finger","contact_count":742.0,"contact_point_centroid":[0.47384,-0.06168,-0.00445],"force_p95":5.28121,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":6.12325,"mean_force":3.57557,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.47388,-0.01946,-0.00511]},{"body_a":"world","body_b":"right_finger","contact_count":740.0,"contact_point_centroid":[0.47377,0.02281,-0.00444],"force_p95":5.26502,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":6.08138,"mean_force":3.55995,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.47388,-0.01946,-0.00512]},{"body_a":"world","body_b":"left_finger","contact_count":11000.0,"contact_point_centroid":[0.4791,-0.06136,-0.00643],"force_p95":3.71645,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":4.05067,"mean_force":2.60972,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.47921,-0.01974,-0.01047]},{"body_a":"world","body_b":"right_finger","contact_count":11000.0,"contact_point_centroid":[0.47901,0.02189,-0.00643],"force_p95":3.71473,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":3.98425,"mean_force":2.61126,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.47921,-0.01974,-0.01047]},{"body_a":"world","body_b":"right_finger","contact_count":728.0,"contact_point_centroid":[0.47983,0.02073,-0.00376],"force_p95":2.62626,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":3.33748,"mean_force":0.77048,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.47994,-0.01977,-0.00327]},{"body_a":"world","body_b":"left_finger","contact_count":728.0,"contact_point_centroid":[0.47992,-0.06027,-0.00375],"force_p95":2.57823,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":3.32731,"mean_force":0.75471,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.47994,-0.01977,-0.00327]},{"body_a":"world","body_b":"grasp_target","contact_count":1568.0,"contact_point_centroid":[0.59198,0.10131,-0.00297],"force_p95":0.41196,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.00824,"mean_force":0.16518,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.59462,0.11731,0.38176]},{"body_a":"grasp_target","body_b":"hand","contact_count":68.0,"contact_point_centroid":[0.48885,-0.01904,0.04623],"force_p95":0.87416,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.91593,"mean_force":0.64126,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.47344,-0.01936,0.00136]},{"body_a":"grasp_target","body_b":"hand","contact_count":550.0,"contact_point_centroid":[0.48122,-0.02019,0.03947],"force_p95":0.71986,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.73066,"mean_force":0.67179,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.47921,-0.01974,-0.01047]},{"body_a":"grasp_target","body_b":"hand","contact_count":78.0,"contact_point_centroid":[0.48801,-0.01927,0.04732],"force_p95":0.40695,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.64567,"mean_force":0.20336,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.47917,-0.01976,0.00321]},{"body_a":"world","body_b":"grasp_target","contact_count":416.0,"contact_point_centroid":[0.47415,-0.02008,-0.0029],"force_p95":0.26323,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.52092,"mean_force":0.14586,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.47868,-0.01975,0.00771]},{"body_a":"world","body_b":"grasp_target","contact_count":1668.0,"contact_point_centroid":[0.47611,-0.02016,-0.00223],"force_p95":0.29974,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.4283,"mean_force":0.14786,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.47456,-0.01779,0.09126]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":12255.0,"contact_point_centroid":[0.47676,-0.00058,0.12353],"force_p95":0.07207,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.37551,"mean_force":0.04948,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.47667,-0.01971,0.12164]},{"body_a":"world","body_b":"grasp_target","contact_count":2200.0,"contact_point_centroid":[0.47479,-0.02026,-0.00463],"force_p95":0.36302,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.37073,"mean_force":0.29099,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.47921,-0.01974,-0.01047]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6327.0,"contact_point_centroid":[0.50937,-0.00274,0.26097],"force_p95":0.14208,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.35617,"mean_force":0.07851,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.50591,0.01601,0.25977]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":12301.0,"contact_point_centroid":[0.4768,-0.03884,0.12319],"force_p95":0.07283,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.35568,"mean_force":0.0498,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.47667,-0.01971,0.1213]}],"total_contact_groups":24},"final_pose_error":0.01999,"key_states":{"actual_goal_position":[0.63142,0.15919,0.19002],"final_object_position":[0.59248,0.10201,0.02602],"final_tcp_position":[0.6318,0.15903,0.47003],"realised_goal_position":[0.63142,0.15919,0.19002],"realised_object_initial_position":[0.47616,-0.02015,0.03]},"peak_contact_force":167951.73011,"phases":[{"contact_detected":true,"contact_event_count":45.0,"n_steps":195.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.03],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28614,"object_z_max":0.03,"peak_contact_force":5.27315,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3218.0,"raw_peak_contact_force":6.12325,"subtask_id":"reach_object","tcp_end":[0.47852,-0.01598,0.19941],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.17346,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":45.0,"n_steps":417.0,"n_steps_budget":1000.0,"object_pos_end":[0.47734,-0.02022,0.02005],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.29123,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":3.39985,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":24750.0,"raw_peak_contact_force":4.05067,"subtask_id":"reach_object","tcp_end":[0.47525,-0.01958,-0.01325],"tcp_start":[0.47852,-0.01598,0.19941],"tcp_to_object_dist_end":0.03337,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":150.0,"n_steps_budget":50.0,"object_pos_end":[0.47673,-0.02026,0.02081],"object_pos_start":[0.47734,-0.02022,0.02005],"object_to_goal_dist_end":0.29114,"object_to_goal_dist_start":0.29123,"object_z_max":0.02083,"peak_contact_force":167951.73011,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":26506.0,"raw_peak_contact_force":3.33748,"tcp_end":[0.48037,-0.01982,-0.00975],"tcp_start":[0.48033,-0.01981,-0.00978],"tcp_to_object_dist_end":0.03078,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":702.0,"n_steps_budget":1000.0,"object_pos_end":[0.48916,-0.01972,0.22384],"object_pos_start":[0.47643,-0.02028,0.02083],"object_to_goal_dist_end":0.23107,"object_to_goal_dist_start":0.2913,"object_z_max":0.22356,"peak_contact_force":0.12266,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":15590.0,"raw_peak_contact_force":2.00824,"tcp_end":[0.47733,-0.01972,0.2207],"tcp_start":[0.48037,-0.01982,-0.00975],"tcp_to_object_dist_end":0.01224,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":984.0,"n_steps_budget":1000.0,"object_pos_end":[0.59248,0.10201,0.02602],"object_pos_start":[0.48916,-0.01972,0.22384],"object_to_goal_dist_end":0.17799,"object_to_goal_dist_start":0.23107,"object_z_max":0.29878,"peak_contact_force":0.12263,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1952.0,"raw_peak_contact_force":0.12266,"subtask_id":"reach_goal","tcp_end":[0.62486,0.15137,0.42295],"tcp_start":[0.47733,-0.01972,0.2207],"tcp_to_object_dist_end":0.4013,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":237.0,"n_steps_budget":1000.0,"object_pos_end":[0.59248,0.10201,0.02602],"object_pos_start":[0.59248,0.10201,0.02602],"object_to_goal_dist_end":0.17799,"object_to_goal_dist_start":0.17799,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1023.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_goal","tcp_end":[0.62871,0.15944,0.28309],"tcp_start":[0.62486,0.15137,0.42295],"tcp_to_object_dist_end":0.26589,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.59248,0.10201,0.02602],"object_pos_start":[0.59248,0.10201,0.02602],"object_to_goal_dist_end":0.17799,"object_to_goal_dist_start":0.17799,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2616.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.62501,0.15817,0.30134],"tcp_start":[0.62871,0.15944,0.28309],"tcp_to_object_dist_end":0.28287,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":654.0,"n_steps_budget":1000.0,"object_pos_end":[0.59248,0.10201,0.02602],"object_pos_start":[0.59248,0.10201,0.02602],"object_to_goal_dist_end":0.17799,"object_to_goal_dist_start":0.17799,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":776.0,"raw_peak_contact_force":0.13845,"tcp_end":[0.6318,0.15903,0.47003],"tcp_start":[0.62501,0.15817,0.30134],"tcp_to_object_dist_end":0.44938,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.93548,"average_solve_count":279.0,"average_success_count":279.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"descend_place.place_descend_dist":0.2101,"descend_place.place_xy_offset_x":-0.00502,"descend_place.place_xy_offset_y":-0.00446,"descend_to_grasp.grasp_descend_dist":0.05759},"optimized_scores":{"best_composite_score":0.33285,"best_fitness_score":0.71285,"best_task_score":0.51721},"replay_outcomes":[{"contacts":{"omitted_contact_groups":6,"reported_contact_groups":[{"body_a":"world","body_b":"left_finger","contact_count":680.0,"contact_point_centroid":[0.4569,-0.06769,-0.00413],"force_p95":5.00782,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":5.84017,"mean_force":3.36768,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.45698,-0.02547,-0.00424]},{"body_a":"world","body_b":"right_finger","contact_count":680.0,"contact_point_centroid":[0.45683,0.0168,-0.0041],"force_p95":4.98683,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":5.79105,"mean_force":3.34684,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.45698,-0.02547,-0.00424]},{"body_a":"world","body_b":"left_finger","contact_count":11000.0,"contact_point_centroid":[0.46148,-0.0674,-0.00608],"force_p95":3.51231,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":3.9136,"mean_force":2.46807,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.46158,-0.02578,-0.00976]},{"body_a":"world","body_b":"right_finger","contact_count":11000.0,"contact_point_centroid":[0.46138,0.01585,-0.00608],"force_p95":3.50808,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":3.8088,"mean_force":2.46955,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.46158,-0.02578,-0.00976]},{"body_a":"world","body_b":"right_finger","contact_count":694.0,"contact_point_centroid":[0.46208,0.01472,-0.00364],"force_p95":2.60034,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":3.24727,"mean_force":0.77657,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.46216,-0.0258,-0.00301]},{"body_a":"world","body_b":"left_finger","contact_count":694.0,"contact_point_centroid":[0.46218,-0.06631,-0.00364],"force_p95":2.51378,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":3.23482,"mean_force":0.74878,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.46216,-0.0258,-0.00301]},{"body_a":"world","body_b":"grasp_target","contact_count":1112.0,"contact_point_centroid":[0.62099,0.19966,-0.00342],"force_p95":0.65641,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.09106,"mean_force":0.17836,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.62146,0.1994,0.25843]},{"body_a":"grasp_target","body_b":"hand","contact_count":66.0,"contact_point_centroid":[0.47254,-0.02518,0.04673],"force_p95":0.84378,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.89434,"mean_force":0.62313,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.45656,-0.02534,0.00224]},{"body_a":"grasp_target","body_b":"hand","contact_count":550.0,"contact_point_centroid":[0.46385,-0.02623,0.03987],"force_p95":0.69284,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.70305,"mean_force":0.65458,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.46158,-0.02578,-0.00976]},{"body_a":"grasp_target","body_b":"hand","contact_count":75.0,"contact_point_centroid":[0.47021,-0.02941,0.04741],"force_p95":0.39717,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.62571,"mean_force":0.19846,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.46148,-0.02578,0.00337]},{"body_a":"world","body_b":"grasp_target","contact_count":408.0,"contact_point_centroid":[0.45653,-0.02616,-0.00287],"force_p95":0.25925,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.50425,"mean_force":0.14531,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.46101,-0.02577,0.00818]},{"body_a":"world","body_b":"grasp_target","contact_count":1660.0,"contact_point_centroid":[0.45852,-0.02632,-0.00221],"force_p95":0.29555,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.4133,"mean_force":0.14638,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.45876,-0.02342,0.09137]},{"body_a":"world","body_b":"grasp_target","contact_count":2200.0,"contact_point_centroid":[0.45708,-0.02645,-0.00456],"force_p95":0.35483,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.35991,"mean_force":0.28657,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.46158,-0.02578,-0.00976]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":11987.0,"contact_point_centroid":[0.45911,-0.00658,0.12397],"force_p95":0.07248,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.35931,"mean_force":0.04962,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.45903,-0.02571,0.12205]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":12082.0,"contact_point_centroid":[0.45916,-0.04484,0.1238],"force_p95":0.07323,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.34716,"mean_force":0.04984,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.45903,-0.02571,0.1219]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":12226.0,"contact_point_centroid":[0.52332,0.04201,0.26942],"force_p95":0.13358,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.3049,"mean_force":0.07131,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.52056,0.06073,0.26862]}],"total_contact_groups":22},"final_pose_error":0.01985,"key_states":{"actual_goal_position":[0.63013,0.20822,0.11412],"final_object_position":[0.62095,0.19968,0.01602],"final_tcp_position":[0.62892,0.20731,0.39432],"realised_goal_position":[0.63013,0.20822,0.11412],"realised_object_initial_position":[0.45856,-0.02632,0.03]},"peak_contact_force":5.84017,"phases":[{"contact_detected":true,"contact_event_count":45.0,"n_steps":207.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.03],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30252,"object_z_max":0.03,"peak_contact_force":4.98022,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3086.0,"raw_peak_contact_force":5.84017,"subtask_id":"reach_object","tcp_end":[0.46401,-0.02124,0.19803],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.17218,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":45.0,"n_steps":415.0,"n_steps_budget":1000.0,"object_pos_end":[0.45955,-0.0264,0.02031],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30486,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":3.28436,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":24750.0,"raw_peak_contact_force":3.9136,"subtask_id":"reach_object","tcp_end":[0.45818,-0.02562,-0.01189],"tcp_start":[0.46401,-0.02124,0.19803],"tcp_to_object_dist_end":0.03224,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":150.0,"n_steps_budget":50.0,"object_pos_end":[0.45901,-0.02646,0.02092],"object_pos_start":[0.45955,-0.0264,0.02031],"object_to_goal_dist_end":0.30502,"object_to_goal_dist_start":0.30486,"object_z_max":0.02093,"peak_contact_force":0.08013,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":25940.0,"raw_peak_contact_force":3.24727,"tcp_end":[0.46259,-0.02586,-0.00918],"tcp_start":[0.46255,-0.02586,-0.0092],"tcp_to_object_dist_end":0.03032,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":688.0,"n_steps_budget":1000.0,"object_pos_end":[0.4719,-0.02568,0.22368],"object_pos_start":[0.45871,-0.02646,0.02094],"object_to_goal_dist_end":0.3029,"object_to_goal_dist_start":0.30519,"object_z_max":0.2234,"peak_contact_force":0.0,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":23262.0,"raw_peak_contact_force":0.3049,"tcp_end":[0.45963,-0.02572,0.22132],"tcp_start":[0.46259,-0.02586,-0.00918],"tcp_to_object_dist_end":0.01249,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":938.0,"n_steps_budget":1000.0,"object_pos_end":[0.62427,0.19501,0.09281],"object_pos_start":[0.4719,-0.02568,0.22368],"object_to_goal_dist_end":0.02575,"object_to_goal_dist_start":0.3029,"object_z_max":0.3126,"peak_contact_force":0.12263,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2176.0,"raw_peak_contact_force":2.09106,"subtask_id":"reach_goal","tcp_end":[0.62158,0.19727,0.3498],"tcp_start":[0.45963,-0.02572,0.22132],"tcp_to_object_dist_end":0.25701,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":295.0,"n_steps_budget":1000.0,"object_pos_end":[0.62095,0.19968,0.01602],"object_pos_start":[0.62427,0.19501,0.09281],"object_to_goal_dist_end":0.0989,"object_to_goal_dist_start":0.02575,"object_z_max":0.09281,"peak_contact_force":0.12263,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1018.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_goal","tcp_end":[0.62147,0.20157,0.17326],"tcp_start":[0.62158,0.19727,0.3498],"tcp_to_object_dist_end":0.15726,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.62095,0.19968,0.01602],"object_pos_start":[0.62095,0.19968,0.01602],"object_to_goal_dist_end":0.0989,"object_to_goal_dist_start":0.0989,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":3296.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.61534,0.19929,0.1913],"tcp_start":[0.62147,0.20157,0.17326],"tcp_to_object_dist_end":0.17537,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":824.0,"n_steps_budget":1000.0,"object_pos_end":[0.62095,0.19968,0.01602],"object_pos_start":[0.62095,0.19968,0.01602],"object_to_goal_dist_end":0.0989,"object_to_goal_dist_start":0.0989,"object_z_max":0.01602,"peak_contact_force":0.12262,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":824.0,"raw_peak_contact_force":0.13845,"tcp_end":[0.62892,0.20731,0.39432],"tcp_start":[0.61534,0.19929,0.1913],"tcp_to_object_dist_end":0.37846,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```