## Search State

- **Seed**: 1
- **Iteration**: 15 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 14 | approach → align → grasp → lift → lift | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | 7 | 0.4787 | 0.91 | ✅ accepted |
| 13 | approach → align → grasp → lift → push → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | 9 | 0.0687 | 0.41 | ❌ rejected |
| 12 | approach → align → grasp → lift → lift → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 10 | 0.0623 | 0.61 | ❌ rejected |
| 11 | approach → align → grasp → lift → align → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 8 | 0.3276 | 0.77 | ❌ rejected |
| 10 | approach → align → grasp → lift → lift | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | 7 | 0.4359 | 0.83 | ❌ rejected |

**Proposal policy**: task_score is near-perfect (0.91). Preserve useful working parts and make only evidence-backed refinements. A HOLD is acceptable if you genuinely cannot find a better structure.

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

> ⚠️ **SUBTASK STRUCTURE CAUTION**: The current best task_score is 0.912, which indicates the subtask decomposition is already effective.
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

## Current Skill (Q=0.479) — your mutation base

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

- **Composite score**: 0.479
- **task_score** (E): 0.912
- **fitness_score**: 0.919  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.440

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_object | 1.00 | 1.00 | 0.1863 |
| descend_grasp | 1.00 | 1.00 | 0.0646 |
| grasp | 1.00 | 1.00 | 0.0110 |
| lift_to_clear | 1.00 | 1.00 | 0.1092 |
| transport_to_goal | 1.00 | 1.00 | 0.2429 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.476, -0.000, 0.119) | (0.479, -0.000, 0.030)→(0.479, -0.000, 0.026) | 0.276→0.278 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_grasp | align | 1.00 / step_budget | (0.476, -0.000, 0.119)→(0.474, -0.001, 0.055) | (0.479, -0.000, 0.026)→(0.479, -0.000, 0.026) | 0.278→0.278 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp | grasp | 1.00 / step_budget | (0.474, -0.001, 0.055)→(0.466, -0.001, 0.047) | (0.479, -0.000, 0.026)→(0.479, -0.001, 0.026) | 0.278→0.278 | 1.00 / 44.333 | 0.146 | 0.197 |
| lift_to_clear | lift | 1.00 / step_budget | (0.466, -0.001, 0.047)→(0.463, -0.001, 0.156) | (0.479, -0.001, 0.026)→(0.473, -0.001, 0.128) | 0.278→0.252 | 1.00 / 24.333 | 0.098 | 0.419 |
| transport_to_goal | lift | 1.00 / step_budget | (0.463, -0.001, 0.156)→(0.591, 0.196, 0.170) | (0.473, -0.001, 0.128)→(0.593, 0.198, 0.135) | 0.252→0.027 | 1.00 / 15.333 | 55984.017 | 0.374 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.131
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 1.000
- phase_score: 0.643
- phase_breakdown.lift_object_score: 0.706
- phase_breakdown.reach_object_score: 0.822
- phase_breakdown.grasp_object_score: 0.757
- phase_breakdown.reach_goal_score: 0.475
- grasp_place_fitness: 0.963

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.963
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 1.000
- **Median Q (composite search score)**: 0.523
- **K-run variance**: 0.0039
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.272


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.60265,"average_solve_count":151.0,"average_success_count":151.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_speed":0.13913,"descend_grasp.descend_speed":0.03107,"lift_to_clear.lift_speed":0.10184,"transport_to_goal.place_offset_x":-0.01295,"transport_to_goal.place_offset_y":0.02,"transport_to_goal.place_offset_z":0.0401,"transport_to_goal.transport_speed":0.09984},"optimized_scores":{"best_composite_score":0.52307,"best_fitness_score":0.96307,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":143.0,"contact_point_centroid":[0.49843,0.04213,-0.00124],"force_p95":0.26088,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.43479,"mean_force":0.06578,"phase_index":3.0,"phase_name":"lift_to_clear","phase_type":"lift","tcp_position_centroid":[0.48657,0.04313,0.04749]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":10785.0,"contact_point_centroid":[0.48702,0.06179,0.09288],"force_p95":0.10223,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29903,"mean_force":0.06427,"phase_index":3.0,"phase_name":"lift_to_clear","phase_type":"lift","tcp_position_centroid":[0.48418,0.04292,0.09154]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":9885.0,"contact_point_centroid":[0.48669,0.02401,0.09376],"force_p95":0.10741,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27665,"mean_force":0.06815,"phase_index":3.0,"phase_name":"lift_to_clear","phase_type":"lift","tcp_position_centroid":[0.48415,0.04291,0.09288]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6819.0,"contact_point_centroid":[0.5132,0.15654,0.16249],"force_p95":0.1274,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24636,"mean_force":0.08483,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"lift","tcp_position_centroid":[0.51003,0.13737,0.16242]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50124,0.04492,-0.00215],"force_p95":0.16392,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.22304,"mean_force":0.13348,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.48925,0.04338,0.04683]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6793.0,"contact_point_centroid":[0.51893,0.12077,0.16111],"force_p95":0.12596,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21964,"mean_force":0.08618,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"lift","tcp_position_centroid":[0.51024,0.13804,0.16252]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4330.0,"contact_point_centroid":[0.4884,0.02404,0.04743],"force_p95":0.078,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13955,"mean_force":0.0496,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.48811,0.04327,0.0456]},{"body_a":"world","body_b":"grasp_target","contact_count":2216.0,"contact_point_centroid":[0.50118,0.04505,-0.00194],"force_p95":0.13205,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12285,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.49755,0.02038,0.20875]},{"body_a":"world","body_b":"grasp_target","contact_count":904.0,"contact_point_centroid":[0.50118,0.04505,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"align","tcp_position_centroid":[0.49531,0.04261,0.08625]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5269.0,"contact_point_centroid":[0.48875,0.06245,0.0477],"force_p95":0.07191,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07408,"mean_force":0.04221,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.48812,0.04328,0.04561]}],"total_contact_groups":10},"final_pose_error":0.01974,"key_states":{"actual_goal_position":[0.56442,0.24486,0.14677],"final_object_position":[0.54983,0.25424,0.14566],"final_tcp_position":[0.54385,0.24922,0.17755],"realised_goal_position":[0.56442,0.24486,0.14677],"realised_object_initial_position":[0.50118,0.04505,0.03]},"peak_contact_force":0.43479,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":555.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.03],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.23992,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2216.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.49709,0.0415,0.11818],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.09232,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":226.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":904.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_object","tcp_end":[0.49598,0.04398,0.05423],"tcp_start":[0.49709,0.0415,0.11818],"tcp_to_object_dist_end":0.0287,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50116,0.04379,0.02547],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.24321,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"peak_contact_force":0.16021,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11399.0,"raw_peak_contact_force":0.22304,"subtask_id":"grasp_object","tcp_end":[0.48809,0.04327,0.04557],"tcp_start":[0.49598,0.04398,0.05423],"tcp_to_object_dist_end":0.02398,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":24.0,"n_steps":665.0,"n_steps_budget":750.0,"object_pos_end":[0.49514,0.04346,0.12599],"object_pos_start":[0.50116,0.04379,0.02547],"object_to_goal_dist_end":0.214,"object_to_goal_dist_start":0.24321,"object_z_max":0.12588,"peak_contact_force":0.09986,"phase_name":"lift_to_clear","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":20813.0,"raw_peak_contact_force":0.43479,"subtask_id":"lift_object","tcp_end":[0.48428,0.04293,0.15363],"tcp_start":[0.48809,0.04327,0.04557],"tcp_to_object_dist_end":0.0297,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":13.0,"n_steps":616.0,"n_steps_budget":1000.0,"object_pos_end":[0.54983,0.25424,0.14566],"object_pos_start":[0.49514,0.04346,0.12599],"object_to_goal_dist_end":0.01737,"object_to_goal_dist_start":0.214,"object_z_max":0.14564,"peak_contact_force":0.20489,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":13612.0,"raw_peak_contact_force":0.24636,"subtask_id":"reach_goal","tcp_end":[0.54385,0.24922,0.17755],"tcp_start":[0.48428,0.04293,0.15363],"tcp_to_object_dist_end":0.03283,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.85833,"average_solve_count":120.0,"average_success_count":120.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_speed":0.12024,"descend_grasp.descend_speed":0.05273,"lift_to_clear.lift_speed":0.07952,"transport_to_goal.place_offset_x":-0.00792,"transport_to_goal.place_offset_y":0.00735,"transport_to_goal.place_offset_z":0.03659,"transport_to_goal.transport_speed":0.21664},"optimized_scores":{"best_composite_score":0.52261,"best_fitness_score":0.96261,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"left_finger","body_b":"grasp_target","contact_count":7095.0,"contact_point_centroid":[0.53943,0.04827,0.18128],"force_p95":0.13085,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.39945,"mean_force":0.08884,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"lift","tcp_position_centroid":[0.53249,0.06567,0.1833]},{"body_a":"world","body_b":"grasp_target","contact_count":143.0,"contact_point_centroid":[0.47364,-0.01924,-0.00123],"force_p95":0.25253,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.39288,"mean_force":0.06135,"phase_index":3.0,"phase_name":"lift_to_clear","phase_type":"lift","tcp_position_centroid":[0.46254,-0.01953,0.04847]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6407.0,"contact_point_centroid":[0.53329,0.08307,0.18128],"force_p95":0.13954,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.34035,"mean_force":0.09484,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"lift","tcp_position_centroid":[0.5313,0.06432,0.18282]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":12923.0,"contact_point_centroid":[0.46279,-0.00053,0.09657],"force_p95":0.10244,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27009,"mean_force":0.06699,"phase_index":3.0,"phase_name":"lift_to_clear","phase_type":"lift","tcp_position_centroid":[0.46006,-0.01946,0.09581]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":14102.0,"contact_point_centroid":[0.46257,-0.03832,0.09582],"force_p95":0.09702,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26806,"mean_force":0.06215,"phase_index":3.0,"phase_name":"lift_to_clear","phase_type":"lift","tcp_position_centroid":[0.46006,-0.01946,0.09505]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.47617,-0.02009,-0.00205],"force_p95":0.1375,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.17732,"mean_force":0.1266,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.46512,-0.0196,0.04802]},{"body_a":"world","body_b":"grasp_target","contact_count":2132.0,"contact_point_centroid":[0.47616,-0.02015,-0.00193],"force_p95":0.13221,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12286,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.48635,-0.00905,0.20993]},{"body_a":"world","body_b":"grasp_target","contact_count":912.0,"contact_point_centroid":[0.47616,-0.02015,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"align","tcp_position_centroid":[0.47176,-0.01908,0.08706]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4841.0,"contact_point_centroid":[0.46351,-0.00032,0.04894],"force_p95":0.06789,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09924,"mean_force":0.04499,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.46402,-0.01957,0.04692]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5389.0,"contact_point_centroid":[0.46356,-0.03879,0.04866],"force_p95":0.06501,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08169,"mean_force":0.04101,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.46403,-0.01957,0.04692]}],"total_contact_groups":10},"final_pose_error":0.01998,"key_states":{"actual_goal_position":[0.63142,0.15919,0.19002],"final_object_position":[0.61737,0.15791,0.17914],"final_tcp_position":[0.61152,0.15556,0.21499],"realised_goal_position":[0.63142,0.15919,0.19002],"realised_object_initial_position":[0.47616,-0.02015,0.03]},"peak_contact_force":167951.73011,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":534.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.03],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28614,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2132.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.47415,-0.0185,0.11958],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.0936,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":228.0,"n_steps_budget":870.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":912.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_object","tcp_end":[0.47161,-0.01974,0.0547],"tcp_start":[0.47415,-0.0185,0.11958],"tcp_to_object_dist_end":0.02904,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":46.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.47609,-0.01971,0.02581],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28827,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.13637,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12030.0,"raw_peak_contact_force":0.17732,"subtask_id":"grasp_object","tcp_end":[0.464,-0.01957,0.04689],"tcp_start":[0.47161,-0.01974,0.0547],"tcp_to_object_dist_end":0.0243,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":861.0,"n_steps_budget":960.0,"object_pos_end":[0.46998,-0.01969,0.12808],"object_pos_start":[0.47609,-0.01971,0.02581],"object_to_goal_dist_end":0.24879,"object_to_goal_dist_start":0.28827,"object_z_max":0.12799,"peak_contact_force":0.09966,"phase_name":"lift_to_clear","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":27168.0,"raw_peak_contact_force":0.39288,"subtask_id":"lift_object","tcp_end":[0.46022,-0.01945,0.1569],"tcp_start":[0.464,-0.01957,0.04689],"tcp_to_object_dist_end":0.03043,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":15.0,"n_steps":629.0,"n_steps_budget":750.0,"object_pos_end":[0.61737,0.15791,0.17914],"object_pos_start":[0.46998,-0.01969,0.12808],"object_to_goal_dist_end":0.01781,"object_to_goal_dist_start":0.24879,"object_z_max":0.1791,"peak_contact_force":167951.73011,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":13502.0,"raw_peak_contact_force":0.39945,"subtask_id":"reach_goal","tcp_end":[0.61152,0.15556,0.21499],"tcp_start":[0.46022,-0.01945,0.1569],"tcp_to_object_dist_end":0.0364,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.184,"average_solve_count":125.0,"average_success_count":125.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_speed":0.09949,"descend_grasp.descend_speed":0.10435,"lift_to_clear.lift_speed":0.09303,"transport_to_goal.place_offset_x":0.00057,"transport_to_goal.place_offset_y":-0.01226,"transport_to_goal.place_offset_z":0.01109,"transport_to_goal.transport_speed":0.16417},"optimized_scores":{"best_composite_score":0.39043,"best_fitness_score":0.83043,"best_task_score":0.73711},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"left_finger","body_b":"grasp_target","contact_count":8016.0,"contact_point_centroid":[0.53149,0.05826,0.13365],"force_p95":0.1381,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.47569,"mean_force":0.09028,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"lift","tcp_position_centroid":[0.52648,0.0761,0.1368]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":7565.0,"contact_point_centroid":[0.52549,0.09483,0.13418],"force_p95":0.12658,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.43069,"mean_force":0.09278,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"lift","tcp_position_centroid":[0.52689,0.07658,0.13673]},{"body_a":"world","body_b":"grasp_target","contact_count":135.0,"contact_point_centroid":[0.45619,-0.02504,-0.00113],"force_p95":0.26467,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.43062,"mean_force":0.05585,"phase_index":3.0,"phase_name":"lift_to_clear","phase_type":"lift","tcp_position_centroid":[0.44552,-0.02545,0.04953]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":11323.0,"contact_point_centroid":[0.44527,-0.00636,0.09693],"force_p95":0.10284,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28555,"mean_force":0.06498,"phase_index":3.0,"phase_name":"lift_to_clear","phase_type":"lift","tcp_position_centroid":[0.44313,-0.02534,0.09634]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":12543.0,"contact_point_centroid":[0.44501,-0.04424,0.0964],"force_p95":0.09636,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2631,"mean_force":0.05958,"phase_index":3.0,"phase_name":"lift_to_clear","phase_type":"lift","tcp_position_centroid":[0.44314,-0.02534,0.09577]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.45858,-0.02624,-0.00207],"force_p95":0.14286,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.19114,"mean_force":0.12786,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.44797,-0.02554,0.04873]},{"body_a":"world","body_b":"grasp_target","contact_count":2192.0,"contact_point_centroid":[0.45856,-0.02632,-0.00194],"force_p95":0.13205,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12285,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.4784,-0.01185,0.20979]},{"body_a":"world","body_b":"grasp_target","contact_count":864.0,"contact_point_centroid":[0.45856,-0.02632,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"align","tcp_position_centroid":[0.45518,-0.02493,0.0873]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4354.0,"contact_point_centroid":[0.44709,-0.00626,0.04884],"force_p95":0.0727,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10424,"mean_force":0.04972,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.44691,-0.0255,0.0477]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5407.0,"contact_point_centroid":[0.44631,-0.04465,0.04879],"force_p95":0.06531,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0767,"mean_force":0.04081,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.44692,-0.0255,0.04771]}],"total_contact_groups":10},"final_pose_error":0.01981,"key_states":{"actual_goal_position":[0.63013,0.20822,0.11412],"final_object_position":[0.61225,0.18318,0.08026],"final_tcp_position":[0.61691,0.18324,0.11883],"realised_goal_position":[0.63013,0.20822,0.11412],"realised_object_initial_position":[0.45856,-0.02632,0.03]},"peak_contact_force":0.47569,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":549.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.03],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30252,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2192.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.45796,-0.02419,0.11958],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.09359,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":216.0,"n_steps_budget":600.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":864.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_object","tcp_end":[0.45432,-0.02577,0.05497],"tcp_start":[0.45796,-0.02419,0.11958],"tcp_to_object_dist_end":0.02927,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.4585,-0.0257,0.02575],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30328,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.1411,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11561.0,"raw_peak_contact_force":0.19114,"subtask_id":"grasp_object","tcp_end":[0.44689,-0.0255,0.04768],"tcp_start":[0.45432,-0.02577,0.05497],"tcp_to_object_dist_end":0.02482,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":26.0,"n_steps":723.0,"n_steps_budget":810.0,"object_pos_end":[0.45348,-0.0257,0.12855],"object_pos_start":[0.4585,-0.0257,0.02575],"object_to_goal_dist_end":0.29348,"object_to_goal_dist_start":0.30328,"object_z_max":0.12844,"peak_contact_force":0.09436,"phase_name":"lift_to_clear","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":24001.0,"raw_peak_contact_force":0.43062,"subtask_id":"lift_object","tcp_end":[0.44324,-0.02533,0.157],"tcp_start":[0.44689,-0.0255,0.04768],"tcp_to_object_dist_end":0.03024,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":18.0,"n_steps":698.0,"n_steps_budget":1000.0,"object_pos_end":[0.61225,0.18318,0.08026],"object_pos_start":[0.45348,-0.0257,0.12855],"object_to_goal_dist_end":0.04575,"object_to_goal_dist_start":0.29348,"object_z_max":0.12857,"peak_contact_force":0.11744,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":15581.0,"raw_peak_contact_force":0.47569,"subtask_id":"reach_goal","tcp_end":[0.61691,0.18324,0.11883],"tcp_start":[0.44324,-0.02533,0.157],"tcp_to_object_dist_end":0.03885,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```