## Search State

- **Seed**: 5
- **Iteration**: 14 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 13 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | impedance_control | impedance_control | impedance_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 10 | 0.3250 | 0.95 | ✅ accepted |
| 12 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | impedance_control | impedance_control | impedance_control | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 12 | -0.1095 | 0.41 | ❌ rejected |
| 11 | approach → descend → grasp → lift → approach → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | impedance_control | impedance_control | impedance_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 10 | -0.0727 | 0.22 | ❌ rejected |
| 10 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | impedance_control | impedance_control | impedance_control | impedance_control | impedance_control | impedance_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 12 | -0.1121 | 0.40 | ❌ rejected |
| 9 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | impedance_control | impedance_control | impedance_control | impedance_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 13 | -0.0441 | 0.39 | ❌ rejected |

**Proposal policy**: task_score is near-perfect (0.95). Preserve useful working parts and make only evidence-backed refinements. A HOLD is acceptable if you genuinely cannot find a better structure.

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
- Frozen realised-scene SHA-256: `ca83b0c5488ee900ee32f323a4fc38ffcc2f5381fd3d2b180044b561c962382d`
- Frozen object start: [0.530500292374538, 0.030794078973649372, 0.03]
- Frozen task target: [0.6015325561042142, 0.17858013800881417, 0.10808960535724847]
- Goal object position: (0.6015325561042142, 0.17858013800881417, 0.10808960535724847)
- place_goal_position (task success criterion — final object 3D position must be close to the realised airborne target here): (0.6015325561042142, 0.17858013800881417, 0.10808960535724847)
- Grasp/lift components are optimiser fitness diagnostics only; canonical task_score is final object-to-realised-target proximity.
- Object initial pose: (0.530500292374538, 0.030794078973649372, 0.03)
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
  frozen_object_start: [0.5305, 0.0308, 0.03]
  frozen_task_target: [0.6015, 0.1786, 0.1081]
  frozen_object_starts: {'grasp_target': [0.530500292374538, 0.030794078973649372, 0.03]}
  frozen_targets: {'place_target': [0.6015325561042142, 0.17858013800881417, 0.10808960535724847]}
  goal_tolerance_m: 0.02
  force_limit_n: 20
  force_scale_n: 5
  realized_scene_sha256: ca83b0c5488ee900ee32f323a4fc38ffcc2f5381fd3d2b180044b561c962382d

> ⚠️ **SUBTASK STRUCTURE CAUTION**: The current best task_score is 0.953, which indicates the subtask decomposition is already effective.
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
| `object` | offset from object initial position (0.530500292374538, 0.030794078973649372, 0.03) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.6015325561042142, 0.17858013800881417, 0.10808960535724847) | final destination targets |
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

## Current Skill (Q=0.325) — your mutation base

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
  - 0.03
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
  parameters:
    approach_height:
      type: scalar
      range:
      - 0.1
      - 0.25
      default: 0.15
      binds_to:
      - path: target.offset.z
        mode: replace
    approach_speed:
      type: scalar
      range:
      - 0.05
      - 0.15
      default: 0.1
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: reach_object
- id: descend_to_grasp
  type: descend
  generator: linear_cartesian
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.0
    - 0.03
    tolerance: 0.015
    orientation:
      mode: keep_current
  parameters:
    descend_speed:
      type: scalar
      range:
      - 0.02
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
    grasp_offset_z:
      type: scalar
      range:
      - 0.01
      - 0.08
      default: 0.03
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: reach_object
- id: grasp_1
  type: grasp
  control: impedance_control
  termination: time_limit
  end_effector_action: force_grasp
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0
    tolerance: 0.03
    orientation:
      mode: keep_current
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
- id: lift_1
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
    - 0.0
    offset_along_axis:
      distance: 0.15
      axis: world_z
      mode: add_to_offset
      sign: positive
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    lift_height:
      type: scalar
      range:
      - 0.08
      - 0.25
      default: 0.15
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    lift_speed:
      type: scalar
      range:
      - 0.03
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: lift_check
    when: after_phase
    predicate: object_lifted
    threshold: 0.02
    on_failure: retry
  retries:
    max_attempts: 1
    strategy: offset_target
    offset:
    - 0.0
    - 0.0
    - 0.01
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
    approach_goal_height:
      type: scalar
      range:
      - 0.1
      - 0.25
      default: 0.15
      binds_to:
      - path: target.offset.z
        mode: replace
    approach_goal_speed:
      type: scalar
      range:
      - 0.03
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: reach_goal
- id: descend_to_goal
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
    descend_goal_speed:
      type: scalar
      range:
      - 0.01
      - 0.05
      default: 0.02
      binds_to:
      - path: generator.speed
        mode: replace
    descend_goal_z_adjust:
      type: scalar
      range:
      - -0.01
      - 0.05
      default: 0.02
      binds_to:
      - path: target.offset.z
        mode: add
  subtask_id: reach_goal

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_object** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.15], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_height: status=consumed; consumers=target.offset.z (replace)
    - approach_speed: status=consumed; consumers=generator.speed (replace)
- **descend_to_grasp** (`descend`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.03], tolerance=0.015
  - orientation: mode=keep_current
  - parameter_bindings:
    - descend_speed: status=consumed; consumers=generator.speed (replace)
    - grasp_offset_z: status=consumed; consumers=target.offset.z (replace)
- **grasp_1** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], tolerance=0.03
  - orientation: mode=keep_current
  - parameter_bindings: none
  - guards:
    - id=grasp_check, when=after_phase, predicate=bilateral_grasp, on_failure=retry, threshold=1.0
  - retries: max_attempts=2, strategy=offset_target, offset=[0.0, 0.0, -0.005]
- **lift_1** (`lift`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=world_z, distance=0.15, mode=add_to_offset, sign=positive}, tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - lift_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=lift_check, when=after_phase, predicate=object_lifted, on_failure=retry, threshold=0.02
  - retries: max_attempts=1, strategy=offset_target, offset=[0.0, 0.0, 0.01]
- **approach_goal** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.15], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_goal_height: status=consumed; consumers=target.offset.z (replace)
    - approach_goal_speed: status=consumed; consumers=generator.speed (replace)
- **descend_to_goal** (`descend`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - descend_goal_speed: status=consumed; consumers=generator.speed (replace)
    - descend_goal_z_adjust: status=consumed; consumers=target.offset.z (add)

## Design Metrics

- **Composite score**: 0.325
- **task_score** (E): 0.953
- **fitness_score**: 0.945  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Complexity Penalty**: 0.620

## Per-Phase Performance

| Phase | Normal Term. Rate | Mean Displacement (m) |
| ------- | ------------------- | ------------------------ |
| approach_object | 1.00 | 0.0668 |
| descend_to_grasp | 1.00 | 0.1884 |
| grasp_1 | 1.00 | 0.0126 |
| lift_1 | 1.00 | 0.1403 |
| approach_goal | 0.67 | 0.2279 |
| descend_to_goal | 1.00 | 0.1273 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end |
| --- | --- | --- | --- | --- | --- |
| approach_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.509, 0.016, 0.238) | (0.516, 0.018, 0.030)→(0.516, 0.018, 0.026) | 0.234→0.236 |
| descend_to_grasp | descend | 1.00 / step_budget | (0.509, 0.016, 0.238)→(0.511, 0.018, 0.050) | (0.516, 0.018, 0.026)→(0.516, 0.018, 0.026) | 0.236→0.236 |
| grasp_1 | grasp | 1.00 / step_budget | (0.511, 0.018, 0.050)→(0.502, 0.017, 0.041) | (0.516, 0.018, 0.026)→(0.516, 0.018, 0.026) | 0.236→0.237 |
| lift_1 | lift | 1.00 / step_budget | (0.502, 0.017, 0.041)→(0.499, 0.017, 0.181) | (0.516, 0.018, 0.026)→(0.510, 0.017, 0.162) | 0.237→0.194 |
| approach_goal | approach | 0.67 / step_budget | (0.499, 0.017, 0.181)→(0.595, 0.164, 0.321) | (0.510, 0.017, 0.162)→(0.601, 0.164, 0.297) | 0.194→0.131 |
| descend_to_goal | descend | 1.00 / step_budget | (0.595, 0.164, 0.321)→(0.601, 0.177, 0.195) | (0.601, 0.164, 0.297)→(0.606, 0.176, 0.167) | 0.131→0.015 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.300
- lift_clearance: 1.000
- transport_retention: 1.000
- terminal_score: 1.000
- phase_score: 0.530
- phase_breakdown.reach_object_score: 0.790
- phase_breakdown.reach_goal_score: 0.419
- grasp_place_fitness: 0.969

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.969
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 1.000
- **Median Q (composite search score)**: 0.348
- **K-run variance**: 0.0011
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.348


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `181fdad61feb8a6d3dd6561c82dc2730a5598964bf30fa08b43615687239c379`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.05,0.05],"goal_z_delta":0.15,"object_xy_delta":[0.05,0.05]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `eed1fc17ff57094d5189888f0dc8540ea7c165c4c73333e7487a550c7ded377e`; realized-scene SHA-256: `ca83b0c5488ee900ee32f323a4fc38ffcc2f5381fd3d2b180044b561c962382d`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.5305,0.03079,0.03]},{"name":"goal","value":[0.60153,0.17858,0.10809]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.5305,0.03079,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.60153,0.17858,0.10809]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.10453,"average_solve_count":287.0,"average_success_count":287.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.approach_goal_height":0.15873,"approach_goal.approach_goal_speed":0.04352,"approach_object.approach_height":0.18326,"approach_object.approach_speed":0.12177,"descend_to_goal.descend_goal_speed":0.03704,"descend_to_goal.descend_goal_z_adjust":0.03533,"descend_to_grasp.descend_speed":0.05767,"descend_to_grasp.grasp_offset_z":0.01005,"lift_1.lift_height":0.15109,"lift_1.lift_speed":0.0695},"optimized_scores":{"best_composite_score":0.34894,"best_fitness_score":0.96894,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":86.0,"contact_point_centroid":[0.52731,0.0286,-0.00145],"force_p95":0.43008,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.50042,"mean_force":0.12215,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51529,0.02909,0.04116]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":7652.0,"contact_point_centroid":[0.51491,0.04783,0.09866],"force_p95":0.1055,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31587,"mean_force":0.06482,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51272,0.02893,0.09694]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":7144.0,"contact_point_centroid":[0.51486,0.00996,0.10217],"force_p95":0.10682,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31384,"mean_force":0.06779,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51269,0.02892,0.1]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2396.0,"contact_point_centroid":[0.59864,0.15262,0.2059],"force_p95":0.16638,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26407,"mean_force":0.11276,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.59343,0.17095,0.20692]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2915.0,"contact_point_centroid":[0.59919,0.18904,0.20577],"force_p95":0.13695,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26002,"mean_force":0.09392,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.59342,0.17094,0.20713]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53055,0.03057,-0.00214],"force_p95":0.1615,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.22551,"mean_force":0.13293,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51774,0.02926,0.04113]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4077.0,"contact_point_centroid":[0.51739,0.00998,0.04253],"force_p95":0.08102,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15251,"mean_force":0.05188,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51655,0.02919,0.03978]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8110.0,"contact_point_centroid":[0.55597,0.07961,0.21063],"force_p95":0.1076,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14611,"mean_force":0.07422,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.55137,0.09823,0.20959]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8076.0,"contact_point_centroid":[0.55802,0.11987,0.21284],"force_p95":0.10146,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13948,"mean_force":0.07396,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.55313,0.10119,0.2114]},{"body_a":"world","body_b":"grasp_target","contact_count":624.0,"contact_point_centroid":[0.5305,0.03079,-0.0018],"force_p95":0.13787,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12341,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.50958,0.01097,0.26536]},{"body_a":"world","body_b":"grasp_target","contact_count":1752.0,"contact_point_centroid":[0.5305,0.03079,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12264,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.5217,0.02637,0.1389]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5012.0,"contact_point_centroid":[0.51734,0.04834,0.04158],"force_p95":0.07387,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0784,"mean_force":0.04445,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51656,0.02919,0.03978]}],"total_contact_groups":12},"final_pose_error":0.0098,"key_states":{"actual_goal_position":[0.60153,0.17858,0.10809],"final_object_position":[0.60114,0.17581,0.12181],"final_tcp_position":[0.59634,0.17573,0.15123],"realised_goal_position":[0.60153,0.17858,0.10809],"realised_object_initial_position":[0.5305,0.03079,0.03]},"phases":[{"n_steps":157.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.03],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18162,"object_z_max":0.03,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"reach_object","tcp_end":[0.52073,0.02319,0.22864],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.203,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":438.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"reach_object","tcp_end":[0.52502,0.02973,0.04964],"tcp_start":[0.52073,0.02319,0.22864],"tcp_to_object_dist_end":0.02428,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53045,0.02946,0.02553],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18468,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","tcp_end":[0.51652,0.02918,0.03974],"tcp_start":[0.52502,0.02973,0.04964],"tcp_to_object_dist_end":0.0199,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":455.0,"n_steps_budget":1000.0,"object_pos_end":[0.52705,0.02919,0.15172],"object_pos_start":[0.53045,0.02946,0.02553],"object_to_goal_dist_end":0.17253,"object_to_goal_dist_start":0.18468,"object_z_max":0.15146,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","tcp_end":[0.51282,0.02894,0.17137],"tcp_start":[0.51652,0.02918,0.03974],"tcp_to_object_dist_end":0.02427,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":641.0,"n_steps_budget":1000.0,"object_pos_end":[0.60046,0.16778,0.22668],"object_pos_start":[0.52705,0.02919,0.15172],"object_to_goal_dist_end":0.11909,"object_to_goal_dist_start":0.17253,"object_z_max":0.22657,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"reach_goal","tcp_end":[0.593,0.16781,0.25239],"tcp_start":[0.51282,0.02894,0.17137],"tcp_to_object_dist_end":0.02677,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":300.0,"n_steps_budget":1000.0,"object_pos_end":[0.60114,0.17581,0.12181],"object_pos_start":[0.60046,0.16778,0.22668],"object_to_goal_dist_end":0.014,"object_to_goal_dist_start":0.11909,"object_z_max":0.2267,"phase_name":"descend_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"reach_goal","tcp_end":[0.59634,0.17573,0.15123],"tcp_start":[0.593,0.16781,0.25239],"tcp_to_object_dist_end":0.02981,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `5dcdc1a4e2a8d4c3bb30f9ac92fb306bea0b16a8f449f4d02b0333754e50f910`; realized-scene SHA-256: `584133b5261cffac0dd4282704ff39e97bf4d452e60b02507679bbdea5a4de22`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50382,-0.01567,0.03]},{"name":"goal","value":[0.58691,0.18745,0.24812]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.50382,-0.01567,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.58691,0.18745,0.24812]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.97327,"average_solve_count":449.0,"average_success_count":449.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.approach_goal_height":0.22439,"approach_goal.approach_goal_speed":0.05506,"approach_object.approach_height":0.22839,"approach_object.approach_speed":0.13899,"descend_to_goal.descend_goal_speed":0.01814,"descend_to_goal.descend_goal_z_adjust":-0.00353,"descend_to_grasp.descend_speed":0.05964,"descend_to_grasp.grasp_offset_z":0.01072,"lift_1.lift_height":0.1965,"lift_1.lift_speed":0.03345},"optimized_scores":{"best_composite_score":0.27797,"best_fitness_score":0.89797,"best_task_score":0.85902},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":92.0,"contact_point_centroid":[0.49993,-0.01493,-0.00152],"force_p95":0.40419,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.41732,"mean_force":0.18215,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49004,-0.01488,0.04242]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":12971.0,"contact_point_centroid":[0.4874,-0.03399,0.12976],"force_p95":0.07352,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24787,"mean_force":0.05032,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48762,-0.01483,0.12809]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":12741.0,"contact_point_centroid":[0.48731,0.00436,0.12802],"force_p95":0.07437,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24642,"mean_force":0.05078,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48761,-0.01483,0.12621]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50383,-0.01559,-0.00207],"force_p95":0.14246,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.1915,"mean_force":0.1281,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.4923,-0.0149,0.04281]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":7669.0,"contact_point_centroid":[0.57976,0.18892,0.34487],"force_p95":0.0881,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18364,"mean_force":0.06586,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.57709,0.16993,0.34492]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8791.0,"contact_point_centroid":[0.57941,0.1511,0.34507],"force_p95":0.07984,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16027,"mean_force":0.05746,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.57708,0.16992,0.34496]},{"body_a":"world","body_b":"grasp_target","contact_count":228.0,"contact_point_centroid":[0.50382,-0.01567,-0.00143],"force_p95":0.13836,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12484,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.5001,-0.00321,0.28991]},{"body_a":"world","body_b":"grasp_target","contact_count":2216.0,"contact_point_centroid":[0.50382,-0.01567,-0.00199],"force_p95":0.12264,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12481,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.49881,-0.01128,0.16262]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":21273.0,"contact_point_centroid":[0.53045,0.05415,0.3253],"force_p95":0.06865,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10976,"mean_force":0.0467,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.52945,0.07323,0.3232]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":18498.0,"contact_point_centroid":[0.53101,0.09288,0.3263],"force_p95":0.07524,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10197,"mean_force":0.05288,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.52968,0.0737,0.32377]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5072.0,"contact_point_centroid":[0.491,0.00436,0.0447],"force_p95":0.0674,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10189,"mean_force":0.04294,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49116,-0.01489,0.04159]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5410.0,"contact_point_centroid":[0.49088,-0.03414,0.04419],"force_p95":0.06588,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07611,"mean_force":0.04112,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49116,-0.01489,0.04159]}],"total_contact_groups":12},"final_pose_error":0.00985,"key_states":{"actual_goal_position":[0.58691,0.18745,0.24812],"final_object_position":[0.58737,0.18365,0.22565],"final_tcp_position":[0.58296,0.18387,0.25287],"realised_goal_position":[0.58691,0.18745,0.24812],"realised_object_initial_position":[0.50382,-0.01567,0.03]},"phases":[{"n_steps":58.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02586],"object_pos_start":[0.50382,-0.01567,0.03],"object_to_goal_dist_end":0.31235,"object_to_goal_dist_start":0.30942,"object_z_max":0.03,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"reach_object","tcp_end":[0.50043,-0.00764,0.27612],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.25041,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":554.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.02586],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.31235,"object_z_max":0.02602,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"reach_object","tcp_end":[0.49931,-0.01497,0.05051],"tcp_start":[0.50043,-0.00764,0.27612],"tcp_to_object_dist_end":0.02491,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50374,-0.01508,0.02574],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31207,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","tcp_end":[0.49113,-0.01489,0.04156],"tcp_start":[0.49931,-0.01497,0.05051],"tcp_to_object_dist_end":0.02023,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":617.0,"n_steps_budget":1000.0,"object_pos_end":[0.49618,-0.01488,0.19896],"object_pos_start":[0.50374,-0.01508,0.02574],"object_to_goal_dist_end":0.22712,"object_to_goal_dist_start":0.31207,"object_z_max":0.19868,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","tcp_end":[0.48802,-0.01483,0.21839],"tcp_start":[0.49113,-0.01489,0.04156],"tcp_to_object_dist_end":0.02107,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5771,0.15821,0.40462],"object_pos_start":[0.49618,-0.01488,0.19896],"object_to_goal_dist_end":0.15951,"object_to_goal_dist_start":0.22712,"object_z_max":0.40443,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"reach_goal","tcp_end":[0.57246,0.15831,0.42875],"tcp_start":[0.48802,-0.01483,0.21839],"tcp_to_object_dist_end":0.02457,"terminated_normally":false,"termination_reason":"step_budget"},{"n_steps":520.0,"n_steps_budget":1000.0,"object_pos_end":[0.58737,0.18365,0.22565],"object_pos_start":[0.5771,0.15821,0.40462],"object_to_goal_dist_end":0.0228,"object_to_goal_dist_start":0.15951,"object_z_max":0.40469,"phase_name":"descend_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"reach_goal","tcp_end":[0.58296,0.18387,0.25287],"tcp_start":[0.57246,0.15831,0.42875],"tcp_to_object_dist_end":0.02758,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `53da4dc33bcb1151bde99c46f4ec5d44dda63d23acc62ec623c12d4d0fb32574`; realized-scene SHA-256: `8a4edc50bf1a337961423afe5cdf858aa28147f944f8fcd30a2ce1adc75d1bd6`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.51251,0.03972,0.03]},{"name":"goal","value":[0.62757,0.17252,0.14502]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.51251,0.03972,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.62757,0.17252,0.14502]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.93413,"average_solve_count":334.0,"average_success_count":334.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.approach_goal_height":0.15272,"approach_goal.approach_goal_speed":0.05802,"approach_object.approach_height":0.16354,"approach_object.approach_speed":0.08104,"descend_to_goal.descend_goal_speed":0.02807,"descend_to_goal.descend_goal_z_adjust":0.02622,"descend_to_grasp.descend_speed":0.04558,"descend_to_grasp.grasp_offset_z":0.01034,"lift_1.lift_height":0.13192,"lift_1.lift_speed":0.04328},"optimized_scores":{"best_composite_score":0.3482,"best_fitness_score":0.9682,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":92.0,"contact_point_centroid":[0.5088,0.03748,-0.00155],"force_p95":0.43661,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.44643,"mean_force":0.16297,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49813,0.03765,0.04219]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8364.0,"contact_point_centroid":[0.49546,0.05659,0.09725],"force_p95":0.07806,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28444,"mean_force":0.052,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49562,0.03745,0.09536]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":7756.0,"contact_point_centroid":[0.49563,0.01825,0.09685],"force_p95":0.0803,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27592,"mean_force":0.05444,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49562,0.03745,0.09426]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.51257,0.03946,-0.00216],"force_p95":0.16891,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.23194,"mean_force":0.13477,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.50041,0.03784,0.04227]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5274.0,"contact_point_centroid":[0.62195,0.18609,0.2331],"force_p95":0.07736,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19593,"mean_force":0.05616,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.61961,0.1671,0.23256]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4729.0,"contact_point_centroid":[0.6219,0.14809,0.23449],"force_p95":0.08423,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18928,"mean_force":0.06109,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.61958,0.16707,0.23323]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3872.0,"contact_point_centroid":[0.50024,0.01855,0.04393],"force_p95":0.08562,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1562,"mean_force":0.05436,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49926,0.03775,0.04101]},{"body_a":"world","body_b":"grasp_target","contact_count":752.0,"contact_point_centroid":[0.51251,0.03972,-0.00183],"force_p95":0.13759,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12328,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.50285,0.01467,0.25663]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":16075.0,"contact_point_centroid":[0.55924,0.08424,0.22029],"force_p95":0.07266,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13091,"mean_force":0.0502,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.55771,0.10334,0.21778]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":16347.0,"contact_point_centroid":[0.56255,0.12609,0.22378],"force_p95":0.07543,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12293,"mean_force":0.04941,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.56126,0.10695,0.22151]},{"body_a":"world","body_b":"grasp_target","contact_count":1596.0,"contact_point_centroid":[0.51251,0.03972,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.50603,0.03462,0.13024]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4989.0,"contact_point_centroid":[0.49993,0.0569,0.04284],"force_p95":0.07592,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08016,"mean_force":0.04479,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49927,0.03775,0.04101]}],"total_contact_groups":12},"final_pose_error":0.00998,"key_states":{"actual_goal_position":[0.62757,0.17252,0.14502],"final_object_position":[0.62842,0.16998,0.15424],"final_tcp_position":[0.62258,0.1702,0.17957],"realised_goal_position":[0.62757,0.17252,0.14502],"realised_object_initial_position":[0.51251,0.03972,0.03]},"phases":[{"n_steps":189.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.03],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21001,"object_z_max":0.03,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"reach_object","tcp_end":[0.50701,0.03108,0.2105],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.18477,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":399.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"reach_object","tcp_end":[0.50751,0.0384,0.05027],"tcp_start":[0.50701,0.03108,0.2105],"tcp_to_object_dist_end":0.0248,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51247,0.03814,0.02545],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21355,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","tcp_end":[0.49923,0.03775,0.04097],"tcp_start":[0.50751,0.0384,0.05027],"tcp_to_object_dist_end":0.02041,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":395.0,"n_steps_budget":1000.0,"object_pos_end":[0.50543,0.03748,0.1351],"object_pos_start":[0.51247,0.03814,0.02545],"object_to_goal_dist_end":0.18235,"object_to_goal_dist_start":0.21355,"object_z_max":0.13483,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","tcp_end":[0.49556,0.03744,0.15334],"tcp_start":[0.49923,0.03775,0.04097],"tcp_to_object_dist_end":0.02074,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":820.0,"n_steps_budget":1000.0,"object_pos_end":[0.62469,0.16472,0.25829],"object_pos_start":[0.50543,0.03748,0.1351],"object_to_goal_dist_end":0.11357,"object_to_goal_dist_start":0.18235,"object_z_max":0.25817,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"reach_goal","tcp_end":[0.61864,0.16492,0.28173],"tcp_start":[0.49556,0.03744,0.15334],"tcp_to_object_dist_end":0.02421,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":297.0,"n_steps_budget":1000.0,"object_pos_end":[0.62842,0.16998,0.15424],"object_pos_start":[0.62469,0.16472,0.25829],"object_to_goal_dist_end":0.0096,"object_to_goal_dist_start":0.11357,"object_z_max":0.25832,"phase_name":"descend_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"reach_goal","tcp_end":[0.62258,0.1702,0.17957],"tcp_start":[0.61864,0.16492,0.28173],"tcp_to_object_dist_end":0.026,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```