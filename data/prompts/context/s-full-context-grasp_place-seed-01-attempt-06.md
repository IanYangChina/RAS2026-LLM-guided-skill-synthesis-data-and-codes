## Search State

- **Seed**: 1
- **Iteration**: 7 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 6 | approach → align → grasp → lift → lift | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | 7 | 0.4727 | 0.90 | ✅ accepted |
| 5 | approach → align → grasp → lift → lift → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 9 | 0.0791 | 0.43 | ✅ accepted |
| 4 | approach → align → grasp → lift → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | time_limit | pose_tolerance | 8 | -0.0507 | 0.35 | ✅ accepted |
| 3 | approach → align → grasp → lift → approach → align → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 4 | 0.2022 | 0.20 | ✅ accepted |
| 2 | rotate → align → push → align → lift | impedance_motion | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | impedance_control | position_control | position_control | position_control | position_control | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 3 | -0.0465 | 0.16 | ❌ rejected |

**Proposal policy**: task_score is near-perfect (0.90). Preserve useful working parts and make only evidence-backed refinements. A HOLD is acceptable if you genuinely cannot find a better structure.

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

> ⚠️ **SUBTASK STRUCTURE CAUTION**: The current best task_score is 0.900, which indicates the subtask decomposition is already effective.
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

## Current Skill (Q=0.473) — your mutation base

```yaml
skill: grasp_place
dsl_version: 2
subtasks:
- id: reach_object
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.08
  weight: 0.15
- id: grasp_object
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.02
  weight: 0.25
- id: lift_object
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.12
  weight: 0.2
- id: reach_goal
  weight: 0.4
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
    - 0.08
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    approach_speed:
      type: scalar
      range:
      - 0.01
      - 0.2
      default: 0.08
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: reach_object
- id: descend_grasp
  type: align
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.0
    - 0.02
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    descend_speed:
      type: scalar
      range:
      - 0.01
      - 0.2
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: grasp_object
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
  - id: grasp_check
    when: after_phase
    predicate: bilateral_grasp
    threshold: 0.5
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.0
    - 0.0
    - -0.003
  subtask_id: grasp_object
- id: lift_to_clear
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
    - 0.12
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    lift_speed:
      type: scalar
      range:
      - 0.02
      - 0.2
      default: 0.08
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: lift_object
- id: transport_to_goal
  type: lift
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
      mode: none
  parameters:
    place_offset_x:
      type: scalar
      range:
      - -0.02
      - 0.02
      default: 0.0
      binds_to:
      - path: target.offset.x
        mode: replace
    place_offset_y:
      type: scalar
      range:
      - -0.02
      - 0.02
      default: 0.0
      binds_to:
      - path: target.offset.y
        mode: replace
    place_offset_z:
      type: scalar
      range:
      - 0.0
      - 0.05
      default: 0.03
      binds_to:
      - path: target.offset.z
        mode: replace
    transport_speed:
      type: scalar
      range:
      - 0.05
      - 0.25
      default: 0.12
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: reach_goal

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_object** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.08], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (replace)
- **descend_grasp** (`align`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.02], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - descend_speed: status=consumed; consumers=generator.speed (replace)
- **grasp** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings: none
  - guards:
    - id=grasp_check, when=after_phase, predicate=bilateral_grasp, on_failure=retry, threshold=0.5
  - retries: max_attempts=2, strategy=offset_target, offset=[0.0, 0.0, -0.003]
- **lift_to_clear** (`lift`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.12], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - lift_speed: status=consumed; consumers=generator.speed (replace)
- **transport_to_goal** (`lift`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.03], tolerance=0.02
  - orientation: mode=none
  - parameter_bindings:
    - place_offset_x: status=consumed; consumers=target.offset.x (replace)
    - place_offset_y: status=consumed; consumers=target.offset.y (replace)
    - place_offset_z: status=consumed; consumers=target.offset.z (replace)
    - transport_speed: status=consumed; consumers=generator.speed (replace)

## Design Metrics

- **Composite score**: 0.473
- **task_score** (E): 0.900
- **fitness_score**: 0.913  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.440

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_object | 1.00 | 1.00 | 0.1864 |
| descend_grasp | 1.00 | 1.00 | 0.0645 |
| grasp | 1.00 | 1.00 | 0.0110 |
| lift_to_clear | 1.00 | 1.00 | 0.1044 |
| transport_to_goal | 1.00 | 0.67 | 0.2501 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.476, -0.000, 0.119) | (0.479, -0.000, 0.030)→(0.479, -0.000, 0.026) | 0.276→0.278 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_grasp | align | 1.00 / step_budget | (0.476, -0.000, 0.119)→(0.474, -0.001, 0.055) | (0.479, -0.000, 0.026)→(0.479, -0.000, 0.026) | 0.278→0.278 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp | grasp | 1.00 / step_budget | (0.474, -0.001, 0.055)→(0.466, -0.001, 0.047) | (0.479, -0.000, 0.026)→(0.479, -0.001, 0.026) | 0.278→0.278 | 1.00 / 44.333 | 0.146 | 0.197 |
| lift_to_clear | lift | 1.00 / step_budget | (0.466, -0.001, 0.047)→(0.462, -0.001, 0.151) | (0.479, -0.001, 0.026)→(0.470, -0.001, 0.123) | 0.278→0.255 | 1.00 / 30.333 | 0.092 | 0.396 |
| transport_to_goal | lift | 1.00 / step_budget | (0.462, -0.001, 0.151)→(0.601, 0.197, 0.176) | (0.470, -0.001, 0.123)→(0.602, 0.197, 0.136) | 0.255→0.026 | 0.67 / 17.333 | 0.073 | 0.369 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.441
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 1.000
- phase_score: 0.634
- phase_breakdown.lift_object_score: 0.701
- phase_breakdown.reach_object_score: 0.823
- phase_breakdown.grasp_object_score: 0.757
- phase_breakdown.reach_goal_score: 0.454
- grasp_place_fitness: 0.963

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.963
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 1.000
- **Median Q (composite search score)**: 0.523
- **K-run variance**: 0.0050
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.319


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.88235,"average_solve_count":136.0,"average_success_count":136.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_speed":0.06817,"descend_grasp.descend_speed":0.11734,"lift_to_clear.lift_speed":0.08549,"transport_to_goal.place_offset_x":-0.00385,"transport_to_goal.place_offset_y":0.0037,"transport_to_goal.place_offset_z":0.04552,"transport_to_goal.transport_speed":0.17334},"optimized_scores":{"best_composite_score":0.52308,"best_fitness_score":0.96308,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":167.0,"contact_point_centroid":[0.49859,0.04248,-0.00128],"force_p95":0.24759,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.42681,"mean_force":0.06614,"phase_index":3.0,"phase_name":"lift_to_clear","phase_type":"lift","tcp_position_centroid":[0.48643,0.04312,0.04743]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6291.0,"contact_point_centroid":[0.52317,0.11878,0.16426],"force_p95":0.12644,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33216,"mean_force":0.08819,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"lift","tcp_position_centroid":[0.51637,0.13646,0.16647]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":13176.0,"contact_point_centroid":[0.48697,0.06176,0.09316],"force_p95":0.10033,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29472,"mean_force":0.06346,"phase_index":3.0,"phase_name":"lift_to_clear","phase_type":"lift","tcp_position_centroid":[0.48405,0.04291,0.09192]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":11918.0,"contact_point_centroid":[0.48676,0.024,0.09458],"force_p95":0.10601,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27762,"mean_force":0.06797,"phase_index":3.0,"phase_name":"lift_to_clear","phase_type":"lift","tcp_position_centroid":[0.48404,0.04291,0.09365]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6171.0,"contact_point_centroid":[0.51764,0.15408,0.16563],"force_p95":0.11992,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26465,"mean_force":0.08361,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"lift","tcp_position_centroid":[0.51592,0.13525,0.16627]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50124,0.04492,-0.00215],"force_p95":0.16387,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.22297,"mean_force":0.13347,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.48925,0.04338,0.04682]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4330.0,"contact_point_centroid":[0.48841,0.02404,0.04743],"force_p95":0.078,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1396,"mean_force":0.0496,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.48812,0.04328,0.04559]},{"body_a":"world","body_b":"grasp_target","contact_count":2420.0,"contact_point_centroid":[0.50118,0.04505,-0.00194],"force_p95":0.13067,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12283,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.49743,0.0204,0.20862]},{"body_a":"world","body_b":"grasp_target","contact_count":832.0,"contact_point_centroid":[0.50118,0.04505,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"align","tcp_position_centroid":[0.49543,0.04264,0.08599]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5267.0,"contact_point_centroid":[0.48875,0.06246,0.04769],"force_p95":0.07189,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07407,"mean_force":0.04223,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.48813,0.04328,0.0456]}],"total_contact_groups":10},"final_pose_error":0.02,"key_states":{"actual_goal_position":[0.56442,0.24486,0.14677],"final_object_position":[0.55691,0.23688,0.14902],"final_tcp_position":[0.55214,0.23328,0.18252],"realised_goal_position":[0.56442,0.24486,0.14677],"realised_object_initial_position":[0.50118,0.04505,0.03]},"peak_contact_force":0.42681,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":606.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.03],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.23992,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2420.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.49708,0.04151,0.11811],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.09225,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":208.0,"n_steps_budget":600.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":832.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_object","tcp_end":[0.496,0.04399,0.05423],"tcp_start":[0.49708,0.04151,0.11811],"tcp_to_object_dist_end":0.0287,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50115,0.04379,0.02547],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.2432,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"peak_contact_force":0.16016,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11397.0,"raw_peak_contact_force":0.22297,"subtask_id":"grasp_object","tcp_end":[0.48809,0.04328,0.04556],"tcp_start":[0.496,0.04399,0.05423],"tcp_to_object_dist_end":0.02397,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":24.0,"n_steps":810.0,"n_steps_budget":900.0,"object_pos_end":[0.49449,0.04336,0.12664],"object_pos_start":[0.50115,0.04379,0.02547],"object_to_goal_dist_end":0.21424,"object_to_goal_dist_start":0.2432,"object_z_max":0.12654,"peak_contact_force":0.09853,"phase_name":"lift_to_clear","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":25261.0,"raw_peak_contact_force":0.42681,"subtask_id":"lift_object","tcp_end":[0.48423,0.04293,0.15476],"tcp_start":[0.48809,0.04328,0.04556],"tcp_to_object_dist_end":0.02993,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":24.0,"n_steps":533.0,"n_steps_budget":810.0,"object_pos_end":[0.55691,0.23688,0.14902],"object_pos_start":[0.49449,0.04336,0.12664],"object_to_goal_dist_end":0.01118,"object_to_goal_dist_start":0.21424,"object_z_max":0.14898,"peak_contact_force":0.12583,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":12462.0,"raw_peak_contact_force":0.33216,"subtask_id":"reach_goal","tcp_end":[0.55214,0.23328,0.18252],"tcp_start":[0.48423,0.04293,0.15476],"tcp_to_object_dist_end":0.03404,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.26736,"average_solve_count":288.0,"average_success_count":288.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_speed":0.01223,"descend_grasp.descend_speed":0.06201,"lift_to_clear.lift_speed":0.03477,"transport_to_goal.place_offset_x":0.01974,"transport_to_goal.place_offset_y":0.00727,"transport_to_goal.place_offset_z":0.04283,"transport_to_goal.transport_speed":0.07062},"optimized_scores":{"best_composite_score":0.52258,"best_fitness_score":0.96258,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":170.0,"contact_point_centroid":[0.4716,-0.0192,-0.0012],"force_p95":0.32429,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.37068,"mean_force":0.08966,"phase_index":3.0,"phase_name":"lift_to_clear","phase_type":"lift","tcp_position_centroid":[0.46235,-0.01953,0.04832]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":21765.0,"contact_point_centroid":[0.4595,-0.03855,0.09516],"force_p95":0.07019,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24549,"mean_force":0.04715,"phase_index":3.0,"phase_name":"lift_to_clear","phase_type":"lift","tcp_position_centroid":[0.45993,-0.01946,0.09432]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":18903.0,"contact_point_centroid":[0.45975,-0.00026,0.09545],"force_p95":0.07607,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24543,"mean_force":0.05372,"phase_index":3.0,"phase_name":"lift_to_clear","phase_type":"lift","tcp_position_centroid":[0.45993,-0.01946,0.09439]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":14788.0,"contact_point_centroid":[0.54029,0.08353,0.17545],"force_p95":0.09243,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18948,"mean_force":0.05959,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"lift","tcp_position_centroid":[0.5439,0.0648,0.17695]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":16314.0,"contact_point_centroid":[0.54931,0.0493,0.17688],"force_p95":0.08575,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17924,"mean_force":0.05472,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"lift","tcp_position_centroid":[0.54724,0.06803,0.17847]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.47617,-0.02009,-0.00205],"force_p95":0.13749,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.17731,"mean_force":0.1266,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.46501,-0.01959,0.04798]},{"body_a":"world","body_b":"grasp_target","contact_count":2376.0,"contact_point_centroid":[0.47616,-0.02015,-0.00194],"force_p95":0.13103,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12283,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.48616,-0.00906,0.20977]},{"body_a":"world","body_b":"grasp_target","contact_count":892.0,"contact_point_centroid":[0.47616,-0.02015,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"align","tcp_position_centroid":[0.47169,-0.01909,0.08697]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4840.0,"contact_point_centroid":[0.46344,-0.00032,0.04901],"force_p95":0.06786,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09913,"mean_force":0.045,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.46392,-0.01957,0.04688]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5389.0,"contact_point_centroid":[0.46349,-0.03878,0.04871],"force_p95":0.06504,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0818,"mean_force":0.04102,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.46392,-0.01957,0.04688]}],"total_contact_groups":10},"final_pose_error":0.01976,"key_states":{"actual_goal_position":[0.63142,0.15919,0.19002],"final_object_position":[0.64552,0.15908,0.18799],"final_tcp_position":[0.63926,0.15712,0.22013],"realised_goal_position":[0.63142,0.15919,0.19002],"realised_object_initial_position":[0.47616,-0.02015,0.03]},"peak_contact_force":0.37068,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":595.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.03],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28614,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2376.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.47405,-0.01852,0.1194],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.09342,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":223.0,"n_steps_budget":750.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":892.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_object","tcp_end":[0.47155,-0.01974,0.05468],"tcp_start":[0.47405,-0.01852,0.1194],"tcp_to_object_dist_end":0.02903,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":46.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.47609,-0.01971,0.02581],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28827,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.13634,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12029.0,"raw_peak_contact_force":0.17731,"subtask_id":"grasp_object","tcp_end":[0.46389,-0.01957,0.04685],"tcp_start":[0.47155,-0.01974,0.05468],"tcp_to_object_dist_end":0.02432,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":42.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.46341,-0.01957,0.11391],"object_pos_start":[0.47609,-0.01971,0.02581],"object_to_goal_dist_end":0.25686,"object_to_goal_dist_start":0.28827,"object_z_max":0.11381,"peak_contact_force":0.07957,"phase_name":"lift_to_clear","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":40838.0,"raw_peak_contact_force":0.37068,"subtask_id":"lift_object","tcp_end":[0.45999,-0.01945,0.14122],"tcp_start":[0.46389,-0.01957,0.04685],"tcp_to_object_dist_end":0.02753,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":28.0,"n_steps":861.0,"n_steps_budget":1000.0,"object_pos_end":[0.64552,0.15908,0.18799],"object_pos_start":[0.46341,-0.01957,0.11391],"object_to_goal_dist_end":0.01424,"object_to_goal_dist_start":0.25686,"object_z_max":0.18792,"peak_contact_force":0.09243,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":31102.0,"raw_peak_contact_force":0.18948,"subtask_id":"reach_goal","tcp_end":[0.63926,0.15712,0.22013],"tcp_start":[0.45999,-0.01945,0.14122],"tcp_to_object_dist_end":0.0328,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.13514,"average_solve_count":111.0,"average_success_count":111.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_speed":0.12172,"descend_grasp.descend_speed":0.11813,"lift_to_clear.lift_speed":0.08898,"transport_to_goal.place_offset_x":-0.007,"transport_to_goal.place_offset_y":0.00582,"transport_to_goal.place_offset_z":0.01693,"transport_to_goal.transport_speed":0.21539},"optimized_scores":{"best_composite_score":0.37237,"best_fitness_score":0.81237,"best_task_score":0.70096},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"right_finger","body_b":"grasp_target","contact_count":7007.0,"contact_point_centroid":[0.51739,0.09582,0.13842],"force_p95":0.15193,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.58576,"mean_force":0.09557,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"lift","tcp_position_centroid":[0.51787,0.07743,0.14059]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":7511.0,"contact_point_centroid":[0.52405,0.06038,0.13778],"force_p95":0.14195,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.54943,"mean_force":0.09255,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"lift","tcp_position_centroid":[0.51826,0.07797,0.14051]},{"body_a":"world","body_b":"grasp_target","contact_count":140.0,"contact_point_centroid":[0.45642,-0.02522,-0.00114],"force_p95":0.28515,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.39115,"mean_force":0.05666,"phase_index":3.0,"phase_name":"lift_to_clear","phase_type":"lift","tcp_position_centroid":[0.44549,-0.02545,0.04949]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":11664.0,"contact_point_centroid":[0.44534,-0.00637,0.09689],"force_p95":0.10285,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28421,"mean_force":0.06545,"phase_index":3.0,"phase_name":"lift_to_clear","phase_type":"lift","tcp_position_centroid":[0.4431,-0.02534,0.09632]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":12976.0,"contact_point_centroid":[0.44505,-0.04424,0.09645],"force_p95":0.0962,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26286,"mean_force":0.05976,"phase_index":3.0,"phase_name":"lift_to_clear","phase_type":"lift","tcp_position_centroid":[0.4431,-0.02534,0.09583]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.45858,-0.02624,-0.00207],"force_p95":0.14284,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.1911,"mean_force":0.12785,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.44796,-0.02554,0.04871]},{"body_a":"world","body_b":"grasp_target","contact_count":2152.0,"contact_point_centroid":[0.45856,-0.02632,-0.00193],"force_p95":0.13212,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12285,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.47841,-0.01184,0.20989]},{"body_a":"world","body_b":"grasp_target","contact_count":864.0,"contact_point_centroid":[0.45856,-0.02632,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"align","tcp_position_centroid":[0.45515,-0.02493,0.08725]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4354.0,"contact_point_centroid":[0.44708,-0.00626,0.04884],"force_p95":0.07271,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1042,"mean_force":0.04972,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.4469,-0.0255,0.04769]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5407.0,"contact_point_centroid":[0.4463,-0.04465,0.04879],"force_p95":0.06532,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0767,"mean_force":0.0408,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.4469,-0.0255,0.04769]}],"total_contact_groups":10},"final_pose_error":0.01983,"key_states":{"actual_goal_position":[0.63013,0.20822,0.11412],"final_object_position":[0.60299,0.19506,0.07018],"final_tcp_position":[0.61015,0.20045,0.12469],"realised_goal_position":[0.63013,0.20822,0.11412],"realised_object_initial_position":[0.45856,-0.02632,0.03]},"peak_contact_force":0.58576,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":539.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.03],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30252,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2152.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.45789,-0.0242,0.11949],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.0935,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":216.0,"n_steps_budget":600.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":864.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_object","tcp_end":[0.45431,-0.02577,0.05496],"tcp_start":[0.45789,-0.0242,0.11949],"tcp_to_object_dist_end":0.02925,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.4585,-0.0257,0.02575],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30328,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.14109,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11561.0,"raw_peak_contact_force":0.1911,"subtask_id":"grasp_object","tcp_end":[0.44688,-0.0255,0.04766],"tcp_start":[0.45431,-0.02577,0.05496],"tcp_to_object_dist_end":0.02481,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":25.0,"n_steps":752.0,"n_steps_budget":840.0,"object_pos_end":[0.45325,-0.02567,0.12854],"object_pos_start":[0.4585,-0.0257,0.02575],"object_to_goal_dist_end":0.2936,"object_to_goal_dist_start":0.30328,"object_z_max":0.12844,"peak_contact_force":0.09658,"phase_name":"lift_to_clear","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":24780.0,"raw_peak_contact_force":0.39115,"subtask_id":"lift_object","tcp_end":[0.44321,-0.02534,0.15721],"tcp_start":[0.44688,-0.0255,0.04766],"tcp_to_object_dist_end":0.03038,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":683.0,"n_steps_budget":870.0,"object_pos_end":[0.60299,0.19506,0.07018],"object_pos_start":[0.45325,-0.02567,0.12854],"object_to_goal_dist_end":0.0533,"object_to_goal_dist_start":0.2936,"object_z_max":0.12856,"peak_contact_force":0.0,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":14518.0,"raw_peak_contact_force":0.58576,"subtask_id":"reach_goal","tcp_end":[0.61015,0.20045,0.12469],"tcp_start":[0.44321,-0.02534,0.15721],"tcp_to_object_dist_end":0.05525,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```