## Search State

- **Seed**: 9
- **Iteration**: 12 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 11 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | position_control | position_control | position_control | impedance_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 8 | 0.4748 | 1.00 | ✅ accepted |
| 10 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | position_control | position_control | position_control | impedance_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 8 | 0.4747 | 1.00 | ✅ accepted |
| 9 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | position_control | position_control | position_control | impedance_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 8 | 0.4599 | 1.00 | ❌ rejected |
| 8 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | position_control | position_control | position_control | impedance_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 8 | 0.4747 | 1.00 | ✅ accepted |
| 7 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | position_control | position_control | position_control | impedance_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 8 | 0.4743 | 1.00 | ✅ accepted |

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
- Frozen realised-scene SHA-256: `0143f6b0f71a2b9dc1b332d50c0ca91b210f169a33e3f94f972cb0659a69dba8`
- Frozen object start: [0.5370249203970084, -0.021318279091244466, 0.03]
- Frozen task target: [0.6103148150051562, 0.2277534082920179, 0.2074111944405348]
- Goal object position: (0.6103148150051562, 0.2277534082920179, 0.2074111944405348)
- place_goal_position (task success criterion — final object 3D position must be close to the realised airborne target here): (0.6103148150051562, 0.2277534082920179, 0.2074111944405348)
- Grasp/lift components are optimiser fitness diagnostics only; canonical task_score is final object-to-realised-target proximity.
- Object initial pose: (0.5370249203970084, -0.021318279091244466, 0.03)
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
  frozen_object_start: [0.537, -0.0213, 0.03]
  frozen_task_target: [0.6103, 0.2278, 0.2074]
  frozen_object_starts: {'grasp_target': [0.5370249203970084, -0.021318279091244466, 0.03]}
  frozen_targets: {'place_target': [0.6103148150051562, 0.2277534082920179, 0.2074111944405348]}
  goal_tolerance_m: 0.02
  force_limit_n: 20
  force_scale_n: 5
  realized_scene_sha256: 0143f6b0f71a2b9dc1b332d50c0ca91b210f169a33e3f94f972cb0659a69dba8

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
| `object` | offset from object initial position (0.5370249203970084, -0.021318279091244466, 0.03) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.6103148150051562, 0.2277534082920179, 0.2074111944405348) | final destination targets |
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

## Current Skill (Q=0.475) — your mutation base

```yaml
skill: grasp_place
dsl_version: 2
skill_type: arm_gripper
subtasks:
- id: approach_object
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.1
  weight: 0.2
- id: descend_to_grasp
  anchor: object
  weight: 0.2
- id: lift_object
  anchor: object
  target_entity: object
  offset:
  - 0.0
  - 0.0
  - 0.15
  weight: 0.2
- id: transport_to_goal
  target_entity: object
  metric: goal_progress
  weight: 0.2
- id: final_placement
  target_entity: object
  weight: 0.2
phases:
- id: approach_to_object
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    entity: grasp_target
    offset:
    - 0.0
    - 0.0
    - 0.1
    tolerance: 0.02
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - -1.0
      align_with: world_z
      tolerance: 0.1
  parameters:
    approach_speed:
      type: scalar
      range:
      - 0.05
      - 0.25
      default: 0.12
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: approach_object
- id: descend_to_grasp
  type: descend
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    entity: grasp_target
    offset:
    - 0.0
    - 0.0
    - 0.0
    tolerance: 0.015
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - -1.0
      align_with: world_z
      tolerance: 0.1
  parameters:
    descend_lateral_x:
      type: scalar
      range:
      - 0.0
      - 0.05
      default: 0.025
      binds_to:
      - path: target.offset.x
        mode: add
    descend_speed:
      type: scalar
      range:
      - 0.02
      - 0.15
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: descend_to_grasp
- id: grasp_object
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
    orientation:
      mode: none
  guards:
  - id: grasp_check
    when: after_phase
    predicate: bilateral_grasp
    threshold: 1.0
    on_failure: retry
  retries:
    max_attempts: 3
    strategy: repeat
- id: lift_object
  type: lift
  generator: linear_cartesian
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    entity: grasp_target
    offset:
    - 0.0
    - 0.0
    - 0.15
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    lift_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: lift_check
    when: after_phase
    predicate: object_lifted
    threshold: 0.05
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: repeat
  subtask_id: lift_object
- id: transport_to_goal
  type: approach
  generator: arc_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    entity: place_target
    offset:
    - 0.0
    - 0.0
    - 0.15
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    arc_height:
      type: scalar
      range:
      - 0.05
      - 0.25
      default: 0.12
      binds_to:
      - path: generator.arc_height
        mode: replace
    transport_speed:
      type: scalar
      range:
      - 0.02
      - 0.2
      default: 0.1
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: transport_to_goal
- id: descend_to_place
  type: descend
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    entity: place_target
    offset:
    - 0.0
    - 0.0
    - 0.0
    tolerance: 0.015
    orientation:
      mode: keep_current
  parameters:
    descend_z_offset:
      type: scalar
      range:
      - 0.0
      - 0.05
      default: 0.03
      binds_to:
      - path: target.offset.z
        mode: add
    place_speed:
      type: scalar
      range:
      - 0.01
      - 0.08
      default: 0.03
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: final_placement

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_to_object** (`approach`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.1], tolerance=0.02
  - orientation: mode=align_axis, axis=[0.0, 0.0, -1.0], align_with=world_z, tolerance=0.1
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (replace)
- **descend_to_grasp** (`descend`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.0], tolerance=0.015
  - orientation: mode=align_axis, axis=[0.0, 0.0, -1.0], align_with=world_z, tolerance=0.1
  - parameter_bindings:
    - descend_lateral_x: status=consumed; consumers=target.offset.x (add)
    - descend_speed: status=consumed; consumers=generator.speed (replace)
- **grasp_object** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - orientation: mode=none
  - parameter_bindings: none
  - guards:
    - id=grasp_check, when=after_phase, predicate=bilateral_grasp, on_failure=retry, threshold=1.0
  - retries: max_attempts=3, strategy=repeat
- **lift_object** (`lift`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.15], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - lift_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=lift_check, when=after_phase, predicate=object_lifted, on_failure=retry, threshold=0.05
  - retries: max_attempts=2, strategy=repeat
- **transport_to_goal** (`approach`)
  - target: source=yaml, anchor=task_goal, entity=place_target, offset=[0.0, 0.0, 0.15], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - arc_height: status=consumed; consumers=generator.arc_height (replace)
    - transport_speed: status=consumed; consumers=generator.speed (replace)
- **descend_to_place** (`descend`)
  - target: source=yaml, anchor=task_goal, entity=place_target, offset=[0.0, 0.0, 0.0], tolerance=0.015
  - orientation: mode=keep_current
  - parameter_bindings:
    - descend_z_offset: status=consumed; consumers=target.offset.z (add)
    - place_speed: status=consumed; consumers=generator.speed (replace)

## Design Metrics

- **Composite score**: 0.475
- **task_score** (E): 1.000
- **fitness_score**: 0.995  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Complexity Penalty**: 0.520

## Per-Phase Performance

| Phase | Normal Term. Rate | Mean Displacement (m) |
| ------- | ------------------- | ------------------------ |
| approach_to_object | 1.00 | 0.1576 |
| descend_to_grasp | 1.00 | 0.1105 |
| grasp_object | 1.00 | 0.0129 |
| lift_object | 1.00 | 0.1275 |
| transport_to_goal | 0.67 | 0.2561 |
| descend_to_place | 1.00 | 0.1370 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end |
| --- | --- | --- | --- | --- | --- |
| approach_to_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.510, -0.015, 0.148) | (0.515, -0.017, 0.030)→(0.515, -0.017, 0.026) | 0.268→0.270 |
| descend_to_grasp | descend | 1.00 / step_budget | (0.510, -0.015, 0.148)→(0.524, -0.016, 0.038) | (0.515, -0.017, 0.026)→(0.515, -0.017, 0.026) | 0.270→0.270 |
| grasp_object | grasp | 1.00 / step_budget | (0.524, -0.016, 0.038)→(0.516, -0.016, 0.029) | (0.515, -0.017, 0.026)→(0.515, -0.016, 0.026) | 0.270→0.270 |
| lift_object | lift | 1.00 / step_budget | (0.516, -0.016, 0.029)→(0.511, -0.016, 0.156) | (0.515, -0.016, 0.026)→(0.513, -0.016, 0.152) | 0.270→0.232 |
| transport_to_goal | approach | 0.67 / step_budget | (0.511, -0.016, 0.156)→(0.602, 0.145, 0.326) | (0.513, -0.016, 0.152)→(0.609, 0.145, 0.307) | 0.232→0.146 |
| descend_to_place | descend | 1.00 / step_budget | (0.602, 0.145, 0.326)→(0.612, 0.176, 0.196) | (0.609, 0.145, 0.307)→(0.620, 0.176, 0.174) | 0.146→0.010 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.560
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 1.000
- phase_score: 0.598
- phase_breakdown.final_placement_score: 0.533
- phase_breakdown.transport_to_goal_score: 0.379
- phase_breakdown.approach_object_score: 0.675
- phase_breakdown.lift_object_score: 0.617
- phase_breakdown.descend_to_grasp_score: 0.787
- grasp_place_fitness: 0.997

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.997
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 1.000
- **Median Q (composite search score)**: 0.477
- **K-run variance**: 0.0000
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.233


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `425c48e82220fc6e1b680086671cf7dd2586733ee271dec2149f96a25d69d0c6`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.05,0.05],"goal_z_delta":0.15,"object_xy_delta":[0.05,0.05]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `58e88c03db0a62276863b22a53636bc89fead3e4bc7f4d35fd72d2282ace32bf`; realized-scene SHA-256: `0143f6b0f71a2b9dc1b332d50c0ca91b210f169a33e3f94f972cb0659a69dba8`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.53702,-0.02132,0.03]},{"name":"goal","value":[0.61031,0.22775,0.20741]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.53702,-0.02132,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.61031,0.22775,0.20741]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.48364,"average_solve_count":275.0,"average_success_count":275.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_to_object.approach_speed":0.14911,"descend_to_grasp.descend_lateral_x":0.01781,"descend_to_grasp.descend_speed":0.06066,"descend_to_place.descend_z_offset":0.01353,"descend_to_place.place_speed":0.05905,"lift_object.lift_speed":0.05291,"transport_to_goal.arc_height":0.09895,"transport_to_goal.transport_speed":0.06001},"optimized_scores":{"best_composite_score":0.4768,"best_fitness_score":0.9968,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":101.0,"contact_point_centroid":[0.53235,-0.02034,-0.00152],"force_p95":0.68373,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.71851,"mean_force":0.19889,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.5363,-0.02062,0.02907]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":9400.0,"contact_point_centroid":[0.53347,-0.03972,0.09265],"force_p95":0.07062,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31617,"mean_force":0.05077,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.53336,-0.02057,0.09077]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":9400.0,"contact_point_centroid":[0.53345,-0.00142,0.09269],"force_p95":0.07065,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30573,"mean_force":0.05049,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.53336,-0.02057,0.09077]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53699,-0.02117,-0.00207],"force_p95":0.14166,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.18257,"mean_force":0.12863,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.53883,-0.02066,0.02898]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6182.0,"contact_point_centroid":[0.59475,0.19862,0.29934],"force_p95":0.09127,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16123,"mean_force":0.06278,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.59315,0.17955,0.29754]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":7001.0,"contact_point_centroid":[0.59465,0.16032,0.29952],"force_p95":0.08484,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14654,"mean_force":0.05604,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.59303,0.17915,0.29826]},{"body_a":"world","body_b":"grasp_target","contact_count":1156.0,"contact_point_centroid":[0.53702,-0.02132,-0.00189],"force_p95":0.13644,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12305,"phase_index":0.0,"phase_name":"approach_to_object","phase_type":"approach","tcp_position_centroid":[0.51332,-0.00887,0.22436]},{"body_a":"world","body_b":"grasp_target","contact_count":1128.0,"contact_point_centroid":[0.53702,-0.02132,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.53594,-0.0195,0.09211]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4810.0,"contact_point_centroid":[0.53766,-0.00145,0.02946],"force_p95":0.06998,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10938,"mean_force":0.04476,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.5376,-0.02064,0.02754]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":20171.0,"contact_point_centroid":[0.54651,0.00987,0.28378],"force_p95":0.07298,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09671,"mean_force":0.04981,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.54622,0.02894,0.28186]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":18677.0,"contact_point_centroid":[0.54551,0.04511,0.27993],"force_p95":0.07837,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09641,"mean_force":0.05288,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.54525,0.02596,0.2776]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4924.0,"contact_point_centroid":[0.53769,-0.03986,0.02944],"force_p95":0.0703,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08789,"mean_force":0.04486,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.5376,-0.02064,0.02755]}],"total_contact_groups":12},"final_pose_error":0.01492,"key_states":{"actual_goal_position":[0.61031,0.22775,0.20741],"final_object_position":[0.61519,0.21684,0.21542],"final_tcp_position":[0.6044,0.21688,0.22927],"realised_goal_position":[0.61031,0.22775,0.20741],"realised_object_initial_position":[0.53702,-0.02132,0.03]},"phases":[{"n_steps":290.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.03],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31446,"object_z_max":0.03,"phase_name":"approach_to_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"approach_object","tcp_end":[0.52867,-0.0183,0.14739],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.1217,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":282.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"descend_to_grasp","tcp_end":[0.54631,-0.02078,0.03796],"tcp_start":[0.52867,-0.0183,0.14739],"tcp_to_object_dist_end":0.01513,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53687,-0.02068,0.02571],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31643,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","tcp_end":[0.53757,-0.02063,0.02751],"tcp_start":[0.54631,-0.02078,0.03796],"tcp_to_object_dist_end":0.00193,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":470.0,"n_steps_budget":1000.0,"object_pos_end":[0.53221,-0.0206,0.15237],"object_pos_start":[0.53687,-0.02068,0.02571],"object_to_goal_dist_end":0.2661,"object_to_goal_dist_start":0.31643,"object_z_max":0.1521,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","subtask_id":"lift_object","tcp_end":[0.53315,-0.02058,0.15609],"tcp_start":[0.53757,-0.02063,0.02751],"tcp_to_object_dist_end":0.00384,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.59574,0.14567,0.35534],"object_pos_start":[0.53221,-0.0206,0.15237],"object_to_goal_dist_end":0.1698,"object_to_goal_dist_start":0.2661,"object_z_max":0.35534,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"transport_to_goal","tcp_end":[0.58377,0.14561,0.36533],"tcp_start":[0.53315,-0.02058,0.15609],"tcp_to_object_dist_end":0.01559,"terminated_normally":false,"termination_reason":"step_budget"},{"n_steps":378.0,"n_steps_budget":1000.0,"object_pos_end":[0.61519,0.21684,0.21542],"object_pos_start":[0.59574,0.14567,0.35534],"object_to_goal_dist_end":0.01438,"object_to_goal_dist_start":0.1698,"object_z_max":0.35534,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"final_placement","tcp_end":[0.6044,0.21688,0.22927],"tcp_start":[0.58377,0.14561,0.36533],"tcp_to_object_dist_end":0.01755,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `1e57d18e69439f9d4839513252d085a45363faa5c1c2b52093c9c8149b88bb68`; realized-scene SHA-256: `9bdc6de22965641ffcaccb8421100561fe91fb98e16735236cc25272572d8879`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.5456,-0.02923,0.03]},{"name":"goal","value":[0.63284,0.16493,0.17692]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.5456,-0.02923,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.63284,0.16493,0.17692]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.2717,"average_solve_count":265.0,"average_success_count":265.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_to_object.approach_speed":0.17333,"descend_to_grasp.descend_lateral_x":0.01766,"descend_to_grasp.descend_speed":0.11465,"descend_to_place.descend_z_offset":0.01742,"descend_to_place.place_speed":0.02066,"lift_object.lift_speed":0.04885,"transport_to_goal.arc_height":0.14856,"transport_to_goal.transport_speed":0.15106},"optimized_scores":{"best_composite_score":0.47749,"best_fitness_score":0.99749,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":104.0,"contact_point_centroid":[0.54121,-0.02792,-0.00158],"force_p95":0.66608,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.70564,"mean_force":0.204,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.5444,-0.0282,0.0286]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4389.0,"contact_point_centroid":[0.62967,0.13525,0.27245],"force_p95":0.09292,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.43353,"mean_force":0.06314,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.62532,0.15417,0.27066]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":15956.0,"contact_point_centroid":[0.55421,-0.01966,0.28245],"force_p95":0.10419,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.36756,"mean_force":0.06155,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.55264,-0.00069,0.28086]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4567.0,"contact_point_centroid":[0.62941,0.17279,0.27446],"force_p95":0.08515,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33603,"mean_force":0.0611,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.62524,0.15397,0.27267]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":9680.0,"contact_point_centroid":[0.54173,-0.04728,0.09249],"force_p95":0.07153,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31114,"mean_force":0.05079,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.54163,-0.02813,0.09062]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":15798.0,"contact_point_centroid":[0.55578,0.02118,0.28357],"force_p95":0.09906,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29516,"mean_force":0.06073,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.55407,0.00228,0.28183]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":9680.0,"contact_point_centroid":[0.54171,-0.00898,0.09254],"force_p95":0.0715,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29209,"mean_force":0.05032,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.54163,-0.02813,0.09062]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.54556,-0.02903,-0.00211],"force_p95":0.15061,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.21322,"mean_force":0.13131,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.54697,-0.02827,0.02859]},{"body_a":"world","body_b":"grasp_target","contact_count":1156.0,"contact_point_centroid":[0.5456,-0.02923,-0.00189],"force_p95":0.13644,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12305,"phase_index":0.0,"phase_name":"approach_to_object","phase_type":"approach","tcp_position_centroid":[0.517,-0.01222,0.22387]},{"body_a":"world","body_b":"grasp_target","contact_count":1048.0,"contact_point_centroid":[0.5456,-0.02923,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.54404,-0.02679,0.09167]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4793.0,"contact_point_centroid":[0.54578,-0.00905,0.02903],"force_p95":0.07139,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11665,"mean_force":0.04477,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.54572,-0.02823,0.02711]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4960.0,"contact_point_centroid":[0.54581,-0.04748,0.029],"force_p95":0.07185,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08709,"mean_force":0.04482,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.54573,-0.02823,0.02711]}],"total_contact_groups":12},"final_pose_error":0.01472,"key_states":{"actual_goal_position":[0.63284,0.16493,0.17692],"final_object_position":[0.6377,0.16126,0.18328],"final_tcp_position":[0.6283,0.16119,0.20784],"realised_goal_position":[0.63284,0.16493,0.17692],"realised_object_initial_position":[0.5456,-0.02923,0.03]},"phases":[{"n_steps":290.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.03],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.25864,"object_z_max":0.03,"phase_name":"approach_to_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"approach_object","tcp_end":[0.53616,-0.02517,0.14677],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.12119,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":262.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"descend_to_grasp","tcp_end":[0.55456,-0.02848,0.03788],"tcp_start":[0.53616,-0.02517,0.14677],"tcp_to_object_dist_end":0.01488,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54544,-0.0283,0.02558],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26054,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","tcp_end":[0.54569,-0.02823,0.02707],"tcp_start":[0.55456,-0.02848,0.03788],"tcp_to_object_dist_end":0.00151,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":484.0,"n_steps_budget":1000.0,"object_pos_end":[0.54114,-0.02818,0.15276],"object_pos_start":[0.54544,-0.0283,0.02558],"object_to_goal_dist_end":0.21514,"object_to_goal_dist_start":0.26054,"object_z_max":0.1525,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","subtask_id":"lift_object","tcp_end":[0.54163,-0.02815,0.15617],"tcp_start":[0.54569,-0.02823,0.02707],"tcp_to_object_dist_end":0.00345,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":953.0,"n_steps_budget":1000.0,"object_pos_end":[0.63272,0.14744,0.30945],"object_pos_start":[0.54114,-0.02818,0.15276],"object_to_goal_dist_end":0.13368,"object_to_goal_dist_start":0.21514,"object_z_max":0.3436,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"transport_to_goal","tcp_end":[0.62384,0.14799,0.33195],"tcp_start":[0.54163,-0.02815,0.15617],"tcp_to_object_dist_end":0.02419,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":277.0,"n_steps_budget":1000.0,"object_pos_end":[0.6377,0.16126,0.18328],"object_pos_start":[0.63272,0.14744,0.30945],"object_to_goal_dist_end":0.0088,"object_to_goal_dist_start":0.13368,"object_z_max":0.30945,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"final_placement","tcp_end":[0.6283,0.16119,0.20784],"tcp_start":[0.62384,0.14799,0.33195],"tcp_to_object_dist_end":0.0263,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `5836f8a66456087ed82e2e1accc6472c2a7681a19bf8e3d54637158aadaafc47`; realized-scene SHA-256: `776f3cbcac69f75f44cb26f0b1a492bbf1ced59f3c5fca79400c3f557c2ce565`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.46286,-7e-05,0.03]},{"name":"goal","value":[0.61015,0.15287,0.12219]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.46286,-7e-05,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.61015,0.15287,0.12219]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.62371,"average_solve_count":194.0,"average_success_count":194.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_to_object.approach_speed":0.12144,"descend_to_grasp.descend_lateral_x":0.0145,"descend_to_grasp.descend_speed":0.11405,"descend_to_place.descend_z_offset":0.01556,"descend_to_place.place_speed":0.0447,"lift_object.lift_speed":0.06323,"transport_to_goal.arc_height":0.12248,"transport_to_goal.transport_speed":0.18445},"optimized_scores":{"best_composite_score":0.47014,"best_fitness_score":0.99014,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":82.0,"contact_point_centroid":[0.45966,-0.00017,-0.00141],"force_p95":0.53346,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.62645,"mean_force":0.14539,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.46284,-0.00023,0.03323]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":12029.0,"contact_point_centroid":[0.49399,0.0154,0.26481],"force_p95":0.11445,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.43064,"mean_force":0.07078,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.49171,0.03433,0.26314]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":12527.0,"contact_point_centroid":[0.50099,0.06008,0.2694],"force_p95":0.10753,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33796,"mean_force":0.06579,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.49864,0.04129,0.26755]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4719.0,"contact_point_centroid":[0.60008,0.12603,0.21885],"force_p95":0.09741,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33722,"mean_force":0.06434,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.59985,0.14521,0.21894]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6236.0,"contact_point_centroid":[0.6,0.16419,0.2179],"force_p95":0.07609,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32383,"mean_force":0.04894,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.59995,0.14531,0.21752]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8000.0,"contact_point_centroid":[0.46,0.01891,0.09521],"force_p95":0.07051,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31062,"mean_force":0.05097,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.45993,-0.00024,0.09331]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8000.0,"contact_point_centroid":[0.46002,-0.01938,0.09521],"force_p95":0.07069,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30041,"mean_force":0.05087,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.45993,-0.00024,0.09331]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.46283,-0.0001,-0.00202],"force_p95":0.12944,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.14309,"mean_force":0.12495,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.46503,-0.0002,0.03289]},{"body_a":"world","body_b":"grasp_target","contact_count":1124.0,"contact_point_centroid":[0.46286,-7e-05,-0.00188],"force_p95":0.13644,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12306,"phase_index":0.0,"phase_name":"approach_to_object","phase_type":"approach","tcp_position_centroid":[0.48266,-4e-05,0.22596]},{"body_a":"world","body_b":"grasp_target","contact_count":1076.0,"contact_point_centroid":[0.46286,-7e-05,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.46724,-9e-05,0.09421]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4844.0,"contact_point_centroid":[0.46403,-0.0194,0.03373],"force_p95":0.06796,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09964,"mean_force":0.04479,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.46395,-0.00021,0.03183]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4873.0,"contact_point_centroid":[0.464,0.01899,0.03372],"force_p95":0.06804,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08547,"mean_force":0.04476,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.46396,-0.00021,0.03183]}],"total_contact_groups":12},"final_pose_error":0.01492,"key_states":{"actual_goal_position":[0.61015,0.15287,0.12219],"final_object_position":[0.60588,0.15018,0.12464],"final_tcp_position":[0.60448,0.15007,0.15126],"realised_goal_position":[0.61015,0.15287,0.12219],"realised_object_initial_position":[0.46286,-7e-05,0.03]},"phases":[{"n_steps":282.0,"n_steps_budget":1000.0,"object_pos_end":[0.46286,-7e-05,0.02602],"object_pos_start":[0.46286,-7e-05,0.03],"object_to_goal_dist_end":0.2331,"object_to_goal_dist_start":0.23148,"object_z_max":0.03,"phase_name":"approach_to_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"approach_object","tcp_end":[0.46526,-7e-05,0.14946],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.12346,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":269.0,"n_steps_budget":1000.0,"object_pos_end":[0.46286,-7e-05,0.02602],"object_pos_start":[0.46286,-7e-05,0.02602],"object_to_goal_dist_end":0.2331,"object_to_goal_dist_start":0.2331,"object_z_max":0.02602,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"descend_to_grasp","tcp_end":[0.47165,-0.00012,0.03964],"tcp_start":[0.46526,-7e-05,0.14946],"tcp_to_object_dist_end":0.01621,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.46273,-0.0002,0.02588],"object_pos_start":[0.46286,-7e-05,0.02602],"object_to_goal_dist_end":0.23332,"object_to_goal_dist_start":0.2331,"object_z_max":0.02602,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","tcp_end":[0.46393,-0.00021,0.0318],"tcp_start":[0.47165,-0.00012,0.03964],"tcp_to_object_dist_end":0.00603,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":400.0,"n_steps_budget":1000.0,"object_pos_end":[0.46424,-0.00021,0.14984],"object_pos_start":[0.46273,-0.0002,0.02588],"object_to_goal_dist_end":0.21328,"object_to_goal_dist_start":0.23332,"object_z_max":0.14955,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","subtask_id":"lift_object","tcp_end":[0.45937,-0.00022,0.15639],"tcp_start":[0.46393,-0.00021,0.0318],"tcp_to_object_dist_end":0.00817,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":801.0,"n_steps_budget":1000.0,"object_pos_end":[0.59784,0.14084,0.25648],"object_pos_start":[0.46424,-0.00021,0.14984],"object_to_goal_dist_end":0.13539,"object_to_goal_dist_start":0.21328,"object_z_max":0.30799,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"transport_to_goal","tcp_end":[0.59753,0.14136,0.28192],"tcp_start":[0.45937,-0.00022,0.15639],"tcp_to_object_dist_end":0.02545,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":293.0,"n_steps_budget":1000.0,"object_pos_end":[0.60588,0.15018,0.12464],"object_pos_start":[0.59784,0.14084,0.25648],"object_to_goal_dist_end":0.00561,"object_to_goal_dist_start":0.13539,"object_z_max":0.25648,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"final_placement","tcp_end":[0.60448,0.15007,0.15126],"tcp_start":[0.59753,0.14136,0.28192],"tcp_to_object_dist_end":0.02666,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```