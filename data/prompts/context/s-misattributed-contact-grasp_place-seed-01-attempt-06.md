## Search State

- **Seed**: 1
- **Iteration**: 7 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 6 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 3 | 0.3531 | 0.41 | ❌ rejected |
| 5 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | impedance_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 3 | 0.2507 | 0.20 | ❌ rejected |
| 4 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 3 | 0.3380 | 0.43 | ✅ accepted |
| 3 | rotate → align → push → align → lift | impedance_motion | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | impedance_control | position_control | position_control | position_control | position_control | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 3 | -0.0465 | 0.16 | ❌ rejected |
| 2 | rotate → align → push → align → lift | impedance_motion | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | impedance_control | position_control | position_control | position_control | position_control | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 3 | -0.0465 | 0.16 | ❌ rejected |

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

## Current Skill (Q=0.353) — your mutation base

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

- **Composite score**: 0.353
- **task_score** (E): 0.412
- **fitness_score**: 0.683  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.330

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_object | 1.00 | 1.00 | 0.0787 |
| descend_to_grasp | 1.00 | 1.00 | 0.1964 |
| grasp | 1.00 | 1.00 | 0.0184 |
| lift | 1.00 | 0.67 | 0.1006 |
| approach_goal | 1.00 | 1.00 | 0.2654 |
| descend_place | 1.00 | 1.00 | 0.0633 |
| release | 1.00 | 1.00 | 0.0185 |
| retract | 1.00 | 1.00 | 0.1285 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.488, -0.000, 0.226) | (0.479, -0.000, 0.030)→(0.479, -0.000, 0.026) | 0.276→0.278 | 1.00 / 4.000 | 0.123 | 0.123 |
| descend_to_grasp | descend | 1.00 / step_budget | (0.488, -0.000, 0.226)→(0.479, -0.000, 0.030) | (0.479, -0.000, 0.026)→(0.479, -0.000, 0.026) | 0.278→0.278 | 1.00 / 44.333 | 0.227 | 0.408 |
| grasp | grasp | 1.00 / step_budget | (0.479, -0.000, 0.030)→(0.467, -0.001, 0.016) | (0.479, -0.000, 0.026)→(0.478, -0.001, 0.024) | 0.278→0.279 | 1.00 / 36.667 | 0.131 | 0.990 |
| lift | lift | 1.00 / step_budget | (0.467, -0.001, 0.016)→(0.466, -0.001, 0.117) | (0.478, -0.001, 0.024)→(0.480, -0.001, 0.124) | 0.279→0.249 | 0.67 / 4.000 | 0.384 | 1.659 |
| approach_goal | approach | 1.00 / step_budget | (0.466, -0.001, 0.117)→(0.588, 0.175, 0.267) | (0.480, -0.001, 0.124)→(0.640, 0.169, 0.019) | 0.249→0.141 | 1.00 / 8.000 | 0.151 | 1.103 |
| descend_place | descend | 1.00 / step_budget | (0.588, 0.175, 0.267)→(0.598, 0.190, 0.207) | (0.640, 0.169, 0.019)→(0.638, 0.180, 0.020) | 0.141→0.137 | 1.00 / 4.000 | 0.123 | 0.227 |
| release | release | 1.00 / step_budget | (0.598, 0.190, 0.207)→(0.593, 0.188, 0.224) | (0.638, 0.180, 0.020)→(0.636, 0.179, 0.019) | 0.137→0.137 | 1.00 / 4.000 | 0.123 | 0.123 |
| retract | retract | 1.00 / step_budget | (0.593, 0.188, 0.224)→(0.606, 0.200, 0.351) | (0.636, 0.179, 0.019)→(0.636, 0.179, 0.019) | 0.137→0.137 | 1.00 / 4.000 | 0.122 | 0.138 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: 0.000
- terminal_score: 0.527
- phase_score: 0.364
- phase_breakdown.reach_goal_score: 0.504
- phase_breakdown.reach_object_score: 0.036
- grasp_place_fitness: 0.743

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.743
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.527
- **Median Q (composite search score)**: 0.342
- **K-run variance**: 0.0020
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 10.0
- **Final σ (mean)**: 0.208


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.92035,"average_solve_count":226.0,"average_success_count":226.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"descend_place.place_xy_offset_x":-0.00847,"descend_place.place_xy_offset_y":-0.0032,"descend_to_grasp.grasp_descend_dist":0.05193},"optimized_scores":{"best_composite_score":0.34195,"best_fitness_score":0.67195,"best_task_score":0.4062},"replay_outcomes":[{"contacts":{"omitted_contact_groups":2,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":162.0,"contact_point_centroid":[0.60911,0.21651,-0.00939],"force_p95":1.74009,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.15404,"mean_force":0.57466,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.55248,0.22166,0.23462]},{"body_a":"world","body_b":"grasp_target","contact_count":76.0,"contact_point_centroid":[0.49776,0.04005,-0.00233],"force_p95":1.06329,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.15432,"mean_force":0.49383,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.48505,0.03959,0.01024]},{"body_a":"grasp_target","body_b":"hand","contact_count":179.0,"contact_point_centroid":[0.52414,0.09765,0.19613],"force_p95":0.49428,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.77906,"mean_force":0.29392,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.50543,0.09443,0.15605]},{"body_a":"grasp_target","body_b":"hand","contact_count":444.0,"contact_point_centroid":[0.50562,0.04676,0.0506],"force_p95":0.33616,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.62778,"mean_force":0.24845,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.48808,0.03988,0.00943]},{"body_a":"grasp_target","body_b":"hand","contact_count":120.0,"contact_point_centroid":[0.5022,0.03776,0.09431],"force_p95":0.37306,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.47923,"mean_force":0.26249,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.48398,0.03944,0.05319]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50097,0.04266,-0.00298],"force_p95":0.33916,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.46081,"mean_force":0.2301,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.48822,0.03989,0.00959]},{"body_a":"world","body_b":"grasp_target","contact_count":797.0,"contact_point_centroid":[0.59716,0.23467,-0.002],"force_p95":0.19935,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.33575,"mean_force":0.12757,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.54835,0.22833,0.20308]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1972.0,"contact_point_centroid":[0.48576,0.02029,0.0544],"force_p95":0.13003,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28125,"mean_force":0.07179,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.48396,0.03944,0.05153]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2462.0,"contact_point_centroid":[0.48456,0.05844,0.05385],"force_p95":0.11797,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25797,"mean_force":0.06099,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.48397,0.03944,0.05196]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1143.0,"contact_point_centroid":[0.5025,0.05266,0.1389],"force_p95":0.1307,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21224,"mean_force":0.09709,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.49676,0.07133,0.13645]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1963.0,"contact_point_centroid":[0.50823,0.10361,0.15035],"force_p95":0.11551,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20156,"mean_force":0.08139,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.5024,0.08639,0.1492]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3443.0,"contact_point_centroid":[0.48816,0.02064,0.01126],"force_p95":0.09,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17949,"mean_force":0.05913,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.48705,0.03979,0.00849]},{"body_a":"world","body_b":"grasp_target","contact_count":308.0,"contact_point_centroid":[0.50118,0.04505,-0.00159],"force_p95":0.13829,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12441,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.50089,0.01139,0.26739]},{"body_a":"world","body_b":"grasp_target","contact_count":732.0,"contact_point_centroid":[0.50118,0.04505,-0.00199],"force_p95":0.12264,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12264,"mean_force":0.12254,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.50025,0.0331,0.12731]},{"body_a":"world","body_b":"grasp_target","contact_count":620.0,"contact_point_centroid":[0.59698,0.23466,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12264,"mean_force":0.12262,"phase_index":7.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.55289,0.23351,0.28114]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5861.0,"contact_point_centroid":[0.4868,0.05974,0.01067],"force_p95":0.08435,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11789,"mean_force":0.05288,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.48709,0.0398,0.00853]}],"total_contact_groups":18},"final_pose_error":0.04954,"key_states":{"actual_goal_position":[0.56442,0.24486,0.14677],"final_object_position":[0.59698,0.23466,0.01602],"final_tcp_position":[0.5606,0.24063,0.34756],"realised_goal_position":[0.56442,0.24486,0.14677],"realised_object_initial_position":[0.50118,0.04505,0.03]},"peak_contact_force":2.15404,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":78.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02595],"object_pos_start":[0.50118,0.04505,0.03],"object_to_goal_dist_end":0.24192,"object_to_goal_dist_start":0.23992,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":732.0,"raw_peak_contact_force":0.12264,"subtask_id":"reach_object","tcp_end":[0.501,0.02596,0.22601],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.20097,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":183.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.02595],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.24192,"object_z_max":0.02602,"peak_contact_force":0.27031,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":11548.0,"raw_peak_contact_force":0.62778,"subtask_id":"reach_object","tcp_end":[0.49962,0.04064,0.02356],"tcp_start":[0.501,0.02596,0.22601],"tcp_to_object_dist_end":0.00528,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":33.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50012,0.04036,0.02355],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.24727,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"peak_contact_force":0.2126,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":4630.0,"raw_peak_contact_force":1.15432,"subtask_id":"reach_object","tcp_end":[0.48704,0.03976,0.00848],"tcp_start":[0.49962,0.04064,0.02356],"tcp_to_object_dist_end":0.01996,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":120.0,"n_steps_budget":930.0,"object_pos_end":[0.50259,0.03993,0.12279],"object_pos_start":[0.50012,0.04036,0.02355],"object_to_goal_dist_end":0.2154,"object_to_goal_dist_start":0.24727,"object_z_max":0.12189,"peak_contact_force":0.0,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":3285.0,"raw_peak_contact_force":0.77906,"tcp_end":[0.48488,0.03946,0.10869],"tcp_start":[0.48704,0.03976,0.00848],"tcp_to_object_dist_end":0.02265,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":7.0,"n_steps":271.0,"n_steps_budget":1000.0,"object_pos_end":[0.59814,0.20308,0.03977],"object_pos_start":[0.50259,0.03993,0.12279],"object_to_goal_dist_end":0.11972,"object_to_goal_dist_start":0.2154,"object_z_max":0.21078,"peak_contact_force":0.13969,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":522.0,"raw_peak_contact_force":2.15404,"subtask_id":"reach_goal","tcp_end":[0.55158,0.21297,0.26067],"tcp_start":[0.48488,0.03946,0.10869],"tcp_to_object_dist_end":0.22597,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":86.0,"n_steps_budget":1000.0,"object_pos_end":[0.59932,0.23346,0.01804],"object_pos_start":[0.59814,0.20308,0.03977],"object_to_goal_dist_end":0.13387,"object_to_goal_dist_start":0.11972,"object_z_max":0.03977,"peak_contact_force":0.12264,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1024.0,"raw_peak_contact_force":0.33575,"subtask_id":"reach_goal","tcp_end":[0.55269,0.22984,0.2039],"tcp_start":[0.55158,0.21297,0.26067],"tcp_to_object_dist_end":0.19165,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.59698,0.23467,0.01602],"object_pos_start":[0.59932,0.23346,0.01804],"object_to_goal_dist_end":0.13514,"object_to_goal_dist_start":0.13387,"object_z_max":0.01804,"peak_contact_force":0.12263,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":620.0,"raw_peak_contact_force":0.12264,"tcp_end":[0.54711,0.22768,0.22324],"tcp_start":[0.55269,0.22984,0.2039],"tcp_to_object_dist_end":0.21325,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":155.0,"n_steps_budget":1000.0,"object_pos_end":[0.59698,0.23466,0.01602],"object_pos_start":[0.59698,0.23467,0.01602],"object_to_goal_dist_end":0.13514,"object_to_goal_dist_start":0.13514,"object_z_max":0.01602,"peak_contact_force":0.12225,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":308.0,"raw_peak_contact_force":0.13845,"tcp_end":[0.5606,0.24063,0.34756],"tcp_start":[0.54711,0.22768,0.22324],"tcp_to_object_dist_end":0.33359,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.92174,"average_solve_count":230.0,"average_success_count":230.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"descend_place.place_xy_offset_x":0.00892,"descend_place.place_xy_offset_y":-0.00068,"descend_to_grasp.grasp_descend_dist":0.03608},"optimized_scores":{"best_composite_score":0.30478,"best_fitness_score":0.63478,"best_task_score":0.30265},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":154.0,"contact_point_centroid":[0.65623,0.12335,-0.00886],"force_p95":1.4263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.22053,"mean_force":0.51017,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.59907,0.12463,0.29113]},{"body_a":"world","body_b":"grasp_target","contact_count":64.0,"contact_point_centroid":[0.47277,-0.01789,-0.00173],"force_p95":0.68678,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.72789,"mean_force":0.33537,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.46424,-0.01791,0.02706]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2489.0,"contact_point_centroid":[0.46306,-0.03709,0.07331],"force_p95":0.11626,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31298,"mean_force":0.05841,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.46308,-0.01787,0.07142]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2400.0,"contact_point_centroid":[0.46312,0.00134,0.07212],"force_p95":0.1217,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30314,"mean_force":0.05966,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.46306,-0.01787,0.06998]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.47623,-0.01978,-0.00222],"force_p95":0.18379,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.26867,"mean_force":0.13941,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.46688,-0.01796,0.02678]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1792.0,"contact_point_centroid":[0.49715,0.03154,0.16395],"force_p95":0.13816,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23281,"mean_force":0.0855,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.49284,0.01263,0.16137]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2283.0,"contact_point_centroid":[0.50125,-0.00156,0.16766],"force_p95":0.1223,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1899,"mean_force":0.07748,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.49686,0.01693,0.16621]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4730.0,"contact_point_centroid":[0.46601,0.00125,0.02774],"force_p95":0.07605,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15743,"mean_force":0.04499,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.4658,-0.01794,0.02581]},{"body_a":"world","body_b":"grasp_target","contact_count":292.0,"contact_point_centroid":[0.47616,-0.02015,-0.00157],"force_p95":0.13832,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12453,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.49463,-0.00503,0.26815]},{"body_a":"world","body_b":"grasp_target","contact_count":360.0,"contact_point_centroid":[0.65616,0.12379,-0.00228],"force_p95":0.12491,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12509,"mean_force":0.10321,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.61778,0.1418,0.27756]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.65618,0.12378,-0.00199],"force_p95":0.12313,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12397,"mean_force":0.12267,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.62331,0.14822,0.24225]},{"body_a":"world","body_b":"grasp_target","contact_count":680.0,"contact_point_centroid":[0.47616,-0.02015,-0.00199],"force_p95":0.12264,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12264,"mean_force":0.12253,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.48246,-0.01474,0.13617]},{"body_a":"world","body_b":"grasp_target","contact_count":648.0,"contact_point_centroid":[0.65618,0.12378,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":7.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.62558,0.15187,0.32176]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5085.0,"contact_point_centroid":[0.466,-0.03729,0.02772],"force_p95":0.07645,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08951,"mean_force":0.04479,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.46581,-0.01794,0.02582]},{"body_a":"left_finger","body_b":"right_finger","contact_count":20.0,"contact_point_centroid":[0.6076,0.13312,0.3033],"force_p95":0.01643,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01643,"mean_force":0.01558,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.60731,0.13312,0.30122]},{"body_a":"left_finger","body_b":"right_finger","contact_count":389.0,"contact_point_centroid":[0.61797,0.14177,0.28003],"force_p95":0.01301,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01454,"mean_force":0.0108,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.61775,0.14177,0.2777]}],"total_contact_groups":17},"final_pose_error":0.04923,"key_states":{"actual_goal_position":[0.63142,0.15919,0.19002],"final_object_position":[0.65618,0.12378,0.01602],"final_tcp_position":[0.63074,0.15679,0.39085],"realised_goal_position":[0.63142,0.15919,0.19002],"realised_object_initial_position":[0.47616,-0.02015,0.03]},"peak_contact_force":2.22053,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":74.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02593],"object_pos_start":[0.47616,-0.02015,0.03],"object_to_goal_dist_end":0.28843,"object_to_goal_dist_start":0.28614,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":680.0,"raw_peak_contact_force":0.12264,"subtask_id":"reach_object","tcp_end":[0.48701,-0.01156,0.22717],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.20171,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":170.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.02593],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28843,"object_z_max":0.02602,"peak_contact_force":0.17427,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":11615.0,"raw_peak_contact_force":0.26867,"subtask_id":"reach_object","tcp_end":[0.47747,-0.01809,0.03966],"tcp_start":[0.48701,-0.01156,0.22717],"tcp_to_object_dist_end":0.01386,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.47603,-0.01811,0.02523],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28764,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.08422,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":4953.0,"raw_peak_contact_force":0.72789,"subtask_id":"reach_object","tcp_end":[0.46577,-0.01793,0.02578],"tcp_start":[0.47747,-0.01809,0.03966],"tcp_to_object_dist_end":0.01027,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":119.0,"n_steps_budget":960.0,"object_pos_end":[0.4781,-0.01791,0.12544],"object_pos_start":[0.47603,-0.01811,0.02523],"object_to_goal_dist_end":0.24299,"object_to_goal_dist_start":0.28764,"object_z_max":0.12454,"peak_contact_force":0.08128,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":4249.0,"raw_peak_contact_force":2.22053,"tcp_end":[0.46403,-0.01785,0.12632],"tcp_start":[0.46577,-0.01793,0.02578],"tcp_to_object_dist_end":0.0141,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":308.0,"n_steps_budget":1000.0,"object_pos_end":[0.6568,0.12299,0.00841],"object_pos_start":[0.4781,-0.01791,0.12544],"object_to_goal_dist_end":0.18691,"object_to_goal_dist_start":0.24299,"object_z_max":0.20967,"peak_contact_force":0.12404,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":749.0,"raw_peak_contact_force":0.12509,"subtask_id":"reach_goal","tcp_end":[0.60887,0.13465,0.30308],"tcp_start":[0.46403,-0.01785,0.12632],"tcp_to_object_dist_end":0.29878,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":90.0,"n_steps_budget":1000.0,"object_pos_end":[0.65618,0.12379,0.01601],"object_pos_start":[0.6568,0.12299,0.00841],"object_to_goal_dist_end":0.17929,"object_to_goal_dist_start":0.18691,"object_z_max":0.0167,"peak_contact_force":0.12263,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1023.0,"raw_peak_contact_force":0.12397,"subtask_id":"reach_goal","tcp_end":[0.62718,0.1491,0.24527],"tcp_start":[0.60887,0.13465,0.30308],"tcp_to_object_dist_end":0.23247,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.65618,0.12378,0.01602],"object_pos_start":[0.65618,0.12379,0.01601],"object_to_goal_dist_end":0.17928,"object_to_goal_dist_start":0.17929,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":648.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.62221,0.14782,0.26178],"tcp_start":[0.62718,0.1491,0.24527],"tcp_to_object_dist_end":0.24926,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":162.0,"n_steps_budget":1000.0,"object_pos_end":[0.65618,0.12378,0.01602],"object_pos_start":[0.65618,0.12378,0.01602],"object_to_goal_dist_end":0.17928,"object_to_goal_dist_start":0.17928,"object_z_max":0.01602,"peak_contact_force":0.12248,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":292.0,"raw_peak_contact_force":0.13845,"tcp_end":[0.63074,0.15679,0.39085],"tcp_start":[0.62221,0.14782,0.26178],"tcp_to_object_dist_end":0.37714,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.92373,"average_solve_count":236.0,"average_success_count":236.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"descend_place.place_xy_offset_x":-0.00527,"descend_place.place_xy_offset_y":-0.00653,"descend_to_grasp.grasp_descend_dist":0.04771},"optimized_scores":{"best_composite_score":0.41267,"best_fitness_score":0.74267,"best_task_score":0.52682},"replay_outcomes":[{"contacts":{"omitted_contact_groups":3,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":46.0,"contact_point_centroid":[0.65842,0.17961,-0.00666],"force_p95":1.57149,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.97616,"mean_force":0.96882,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.60156,0.17202,0.23349]},{"body_a":"world","body_b":"grasp_target","contact_count":68.0,"contact_point_centroid":[0.45515,-0.02384,-0.00195],"force_p95":0.99941,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.08809,"mean_force":0.45724,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.44785,-0.02359,0.01563]},{"body_a":"world","body_b":"grasp_target","contact_count":277.0,"contact_point_centroid":[0.66175,0.18519,-0.00574],"force_p95":0.60788,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.02885,"mean_force":0.20673,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.60971,0.1834,0.21004]},{"body_a":"grasp_target","body_b":"hand","contact_count":118.0,"contact_point_centroid":[0.46497,-0.03974,0.09847],"force_p95":0.31876,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.44938,"mean_force":0.13987,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.44689,-0.02354,0.05934]},{"body_a":"grasp_target","body_b":"hand","contact_count":206.0,"contact_point_centroid":[0.51606,0.05414,0.19107],"force_p95":0.28466,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33739,"mean_force":0.14648,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.4976,0.03981,0.15283]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.45834,-0.02517,-0.00247],"force_p95":0.25815,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.32844,"mean_force":0.19115,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.45065,-0.02368,0.01508]},{"body_a":"grasp_target","body_b":"hand","contact_count":424.0,"contact_point_centroid":[0.46784,-0.03872,0.05389],"force_p95":0.22869,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30747,"mean_force":0.11653,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.45032,-0.02367,0.01477]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2251.0,"contact_point_centroid":[0.44704,-0.00438,0.05967],"force_p95":0.10941,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27608,"mean_force":0.06042,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.44685,-0.02354,0.05767]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2421.0,"contact_point_centroid":[0.44693,-0.0427,0.06201],"force_p95":0.10594,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26691,"mean_force":0.0583,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.44691,-0.02354,0.06024]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.65615,0.17987,-0.00202],"force_p95":0.17551,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.22121,"mean_force":0.12448,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.61033,0.1904,0.16753]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2774.0,"contact_point_centroid":[0.4912,0.00803,0.14701],"force_p95":0.10533,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18711,"mean_force":0.06949,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.48751,0.02672,0.14528]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2515.0,"contact_point_centroid":[0.49393,0.04875,0.14959],"force_p95":0.11084,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15157,"mean_force":0.07647,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.48991,0.02983,0.14709]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4420.0,"contact_point_centroid":[0.44981,-0.00453,0.01613],"force_p95":0.07715,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1495,"mean_force":0.05257,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.4496,-0.02365,0.01419]},{"body_a":"world","body_b":"grasp_target","contact_count":312.0,"contact_point_centroid":[0.45856,-0.02632,-0.0016],"force_p95":0.13827,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12438,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.48963,-0.00689,0.26679]},{"body_a":"world","body_b":"grasp_target","contact_count":660.0,"contact_point_centroid":[0.65611,0.17985,-0.00199],"force_p95":0.123,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12325,"mean_force":0.12262,"phase_index":7.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.61582,0.19618,0.24676]},{"body_a":"world","body_b":"grasp_target","contact_count":720.0,"contact_point_centroid":[0.45856,-0.02632,-0.00199],"force_p95":0.12264,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12264,"mean_force":0.12254,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.4689,-0.0197,0.12888]}],"total_contact_groups":19},"final_pose_error":0.04923,"key_states":{"actual_goal_position":[0.63013,0.20822,0.11412],"final_object_position":[0.65611,0.17985,0.02602],"final_tcp_position":[0.62536,0.20386,0.31532],"realised_goal_position":[0.63013,0.20822,0.11412],"realised_object_initial_position":[0.45856,-0.02632,0.03]},"peak_contact_force":1.97616,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":79.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02595],"object_pos_start":[0.45856,-0.02632,0.03],"object_to_goal_dist_end":0.30367,"object_to_goal_dist_start":0.30252,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":720.0,"raw_peak_contact_force":0.12264,"subtask_id":"reach_object","tcp_end":[0.47599,-0.01573,0.22474],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.19983,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":45.0,"n_steps":180.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.02595],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30367,"object_z_max":0.02602,"peak_contact_force":0.23685,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":11788.0,"raw_peak_contact_force":0.32844,"subtask_id":"reach_object","tcp_end":[0.4613,-0.02392,0.02719],"tcp_start":[0.47599,-0.01573,0.22474],"tcp_to_object_dist_end":0.00382,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.45731,-0.02376,0.02461],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30281,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.09564,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":4858.0,"raw_peak_contact_force":1.08809,"subtask_id":"reach_object","tcp_end":[0.44958,-0.02364,0.01417],"tcp_start":[0.4613,-0.02392,0.02719],"tcp_to_object_dist_end":0.01299,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":118.0,"n_steps_budget":930.0,"object_pos_end":[0.46027,-0.02352,0.12526],"object_pos_start":[0.45731,-0.02376,0.02461],"object_to_goal_dist_end":0.28753,"object_to_goal_dist_start":0.30281,"object_z_max":0.12435,"peak_contact_force":1.07214,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":5541.0,"raw_peak_contact_force":1.97616,"tcp_end":[0.44801,-0.02352,0.11502],"tcp_start":[0.44958,-0.02364,0.01417],"tcp_to_object_dist_end":0.01598,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":312.0,"n_steps_budget":1000.0,"object_pos_end":[0.6648,0.18228,0.00759],"object_pos_start":[0.46027,-0.02352,0.12526],"object_to_goal_dist_end":0.11499,"object_to_goal_dist_start":0.28753,"object_z_max":0.19792,"peak_contact_force":0.19057,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":563.0,"raw_peak_contact_force":1.02885,"subtask_id":"reach_goal","tcp_end":[0.60484,0.17613,0.23604],"tcp_start":[0.44801,-0.02352,0.11502],"tcp_to_object_dist_end":0.23627,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":96.0,"n_steps_budget":1000.0,"object_pos_end":[0.6591,0.18129,0.02597],"object_pos_start":[0.6648,0.18228,0.00759],"object_to_goal_dist_end":0.09662,"object_to_goal_dist_start":0.11499,"object_z_max":0.02829,"peak_contact_force":0.12322,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1022.0,"raw_peak_contact_force":0.22121,"subtask_id":"reach_goal","tcp_end":[0.6156,0.19186,0.1705],"tcp_start":[0.60484,0.17613,0.23604],"tcp_to_object_dist_end":0.1513,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.65612,0.17985,0.02602],"object_pos_start":[0.6591,0.18129,0.02597],"object_to_goal_dist_end":0.09613,"object_to_goal_dist_start":0.09662,"object_z_max":0.02603,"peak_contact_force":0.12263,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":660.0,"raw_peak_contact_force":0.12325,"tcp_end":[0.60879,0.18979,0.18713],"tcp_start":[0.6156,0.19186,0.1705],"tcp_to_object_dist_end":0.16821,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":165.0,"n_steps_budget":1000.0,"object_pos_end":[0.65611,0.17985,0.02602],"object_pos_start":[0.65612,0.17985,0.02602],"object_to_goal_dist_end":0.09613,"object_to_goal_dist_start":0.09613,"object_z_max":0.02602,"peak_contact_force":0.12221,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":312.0,"raw_peak_contact_force":0.13845,"tcp_end":[0.62536,0.20386,0.31532],"tcp_start":[0.60879,0.18979,0.18713],"tcp_to_object_dist_end":0.29192,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```