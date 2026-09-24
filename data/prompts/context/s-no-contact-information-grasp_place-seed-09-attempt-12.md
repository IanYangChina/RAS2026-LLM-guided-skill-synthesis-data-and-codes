## Search State

- **Seed**: 9
- **Iteration**: 13 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 12 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | position_control | position_control | position_control | impedance_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 8 | 0.4747 | 1.00 | ❌ rejected |
| 11 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | position_control | position_control | position_control | impedance_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 8 | 0.4748 | 1.00 | ✅ accepted |
| 10 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | position_control | position_control | position_control | impedance_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 8 | 0.4747 | 1.00 | ✅ accepted |
| 9 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | position_control | position_control | position_control | impedance_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 8 | 0.4599 | 1.00 | ❌ rejected |
| 8 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | position_control | position_control | position_control | impedance_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 8 | 0.4747 | 1.00 | ✅ accepted |

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
| descend_to_grasp | 1.00 | 0.1104 |
| grasp_object | 1.00 | 0.0129 |
| lift_object | 1.00 | 0.1275 |
| transport_to_goal | 0.33 | 0.2560 |
| descend_to_place | 1.00 | 0.1523 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end |
| --- | --- | --- | --- | --- | --- |
| approach_to_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.510, -0.015, 0.148) | (0.515, -0.017, 0.030)→(0.515, -0.017, 0.026) | 0.268→0.270 |
| descend_to_grasp | descend | 1.00 / step_budget | (0.510, -0.015, 0.148)→(0.524, -0.016, 0.039) | (0.515, -0.017, 0.026)→(0.515, -0.017, 0.026) | 0.270→0.270 |
| grasp_object | grasp | 1.00 / step_budget | (0.524, -0.016, 0.039)→(0.515, -0.016, 0.029) | (0.515, -0.017, 0.026)→(0.515, -0.016, 0.026) | 0.270→0.270 |
| lift_object | lift | 1.00 / step_budget | (0.515, -0.016, 0.029)→(0.511, -0.016, 0.156) | (0.515, -0.016, 0.026)→(0.511, -0.016, 0.152) | 0.270→0.233 |
| transport_to_goal | approach | 0.33 / step_budget | (0.511, -0.016, 0.156)→(0.595, 0.128, 0.341) | (0.511, -0.016, 0.152)→(0.607, 0.128, 0.326) | 0.233→0.169 |
| descend_to_place | descend | 1.00 / step_budget | (0.595, 0.128, 0.341)→(0.612, 0.175, 0.200) | (0.607, 0.128, 0.326)→(0.620, 0.175, 0.179) | 0.169→0.013 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.415
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 1.000
- phase_score: 0.574
- phase_breakdown.final_placement_score: 0.561
- phase_breakdown.transport_to_goal_score: 0.230
- phase_breakdown.approach_object_score: 0.675
- phase_breakdown.lift_object_score: 0.616
- phase_breakdown.descend_to_grasp_score: 0.789
- grasp_place_fitness: 0.998

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.998
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 1.000
- **Median Q (composite search score)**: 0.476
- **K-run variance**: 0.0000
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.263


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.28152,"average_solve_count":341.0,"average_success_count":341.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_to_object.approach_speed":0.15357,"descend_to_grasp.descend_lateral_x":0.01826,"descend_to_grasp.descend_speed":0.06551,"descend_to_place.descend_z_offset":0.02996,"descend_to_place.place_speed":0.03692,"lift_object.lift_speed":0.0213,"transport_to_goal.arc_height":0.14718,"transport_to_goal.transport_speed":0.10567},"optimized_scores":{"best_composite_score":0.47648,"best_fitness_score":0.99648,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":124.0,"contact_point_centroid":[0.53265,-0.02061,-0.00167],"force_p95":0.50191,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.57818,"mean_force":0.21575,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.5365,-0.02061,0.02858]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":9920.0,"contact_point_centroid":[0.53363,-0.03971,0.09186],"force_p95":0.07084,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25426,"mean_force":0.05078,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.53352,-0.02057,0.08998]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":9920.0,"contact_point_centroid":[0.53361,-0.00143,0.09189],"force_p95":0.07123,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24501,"mean_force":0.05049,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.53352,-0.02057,0.08998]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4803.0,"contact_point_centroid":[0.59402,0.18334,0.32492],"force_p95":0.14633,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23198,"mean_force":0.09238,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.58918,0.1652,0.3261]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":17412.0,"contact_point_centroid":[0.53605,-0.02725,0.29209],"force_p95":0.09975,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22552,"mean_force":0.05745,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.53488,-0.0082,0.29004]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4062.0,"contact_point_centroid":[0.59418,0.14789,0.32349],"force_p95":0.16547,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21086,"mean_force":0.10383,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.58949,0.16624,0.32442]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":17571.0,"contact_point_centroid":[0.5366,0.01216,0.29337],"force_p95":0.09748,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20966,"mean_force":0.05711,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.53532,-0.00684,0.2914]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53699,-0.02117,-0.00207],"force_p95":0.1417,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.18239,"mean_force":0.12866,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.53922,-0.02066,0.02901]},{"body_a":"world","body_b":"grasp_target","contact_count":1140.0,"contact_point_centroid":[0.53702,-0.02132,-0.00188],"force_p95":0.13644,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12306,"phase_index":0.0,"phase_name":"approach_to_object","phase_type":"approach","tcp_position_centroid":[0.51331,-0.00885,0.22444]},{"body_a":"world","body_b":"grasp_target","contact_count":1120.0,"contact_point_centroid":[0.53702,-0.02132,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.53613,-0.01949,0.09222]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4810.0,"contact_point_centroid":[0.53805,-0.00145,0.02949],"force_p95":0.06999,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10943,"mean_force":0.04476,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.53799,-0.02063,0.02757]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4924.0,"contact_point_centroid":[0.53807,-0.03986,0.02947],"force_p95":0.07031,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08787,"mean_force":0.04486,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.53799,-0.02063,0.02757]}],"total_contact_groups":12},"final_pose_error":0.01482,"key_states":{"actual_goal_position":[0.61031,0.22775,0.20741],"final_object_position":[0.61182,0.21648,0.22161],"final_tcp_position":[0.60445,0.21627,0.24467],"realised_goal_position":[0.61031,0.22775,0.20741],"realised_object_initial_position":[0.53702,-0.02132,0.03]},"phases":[{"n_steps":286.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.03],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31446,"object_z_max":0.03,"phase_name":"approach_to_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"approach_object","tcp_end":[0.52865,-0.01828,0.14756],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.12187,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":280.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"descend_to_grasp","tcp_end":[0.54672,-0.02078,0.03803],"tcp_start":[0.52865,-0.01828,0.14756],"tcp_to_object_dist_end":0.01544,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53687,-0.02068,0.02571],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31643,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","tcp_end":[0.53796,-0.02063,0.02753],"tcp_start":[0.54672,-0.02078,0.03803],"tcp_to_object_dist_end":0.00213,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":496.0,"n_steps_budget":1000.0,"object_pos_end":[0.53157,-0.0206,0.15273],"object_pos_start":[0.53687,-0.02068,0.02571],"object_to_goal_dist_end":0.26621,"object_to_goal_dist_start":0.31643,"object_z_max":0.15246,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","subtask_id":"lift_object","tcp_end":[0.53315,-0.02058,0.15618],"tcp_start":[0.53796,-0.02063,0.02753],"tcp_to_object_dist_end":0.00381,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.59399,0.12316,0.38601],"object_pos_start":[0.53157,-0.0206,0.15273],"object_to_goal_dist_end":0.20761,"object_to_goal_dist_start":0.26621,"object_z_max":0.38716,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"transport_to_goal","tcp_end":[0.57725,0.1231,0.39901],"tcp_start":[0.53315,-0.02058,0.15618],"tcp_to_object_dist_end":0.02119,"terminated_normally":false,"termination_reason":"step_budget"},{"n_steps":457.0,"n_steps_budget":1000.0,"object_pos_end":[0.61182,0.21648,0.22161],"object_pos_start":[0.59399,0.12316,0.38601],"object_to_goal_dist_end":0.01819,"object_to_goal_dist_start":0.20761,"object_z_max":0.38601,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"final_placement","tcp_end":[0.60445,0.21627,0.24467],"tcp_start":[0.57725,0.1231,0.39901],"tcp_to_object_dist_end":0.02421,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.13681,"average_solve_count":307.0,"average_success_count":307.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_to_object.approach_speed":0.19138,"descend_to_grasp.descend_lateral_x":0.01764,"descend_to_grasp.descend_speed":0.06145,"descend_to_place.descend_z_offset":0.01576,"descend_to_place.place_speed":0.01826,"lift_object.lift_speed":0.04557,"transport_to_goal.arc_height":0.15161,"transport_to_goal.transport_speed":0.08822},"optimized_scores":{"best_composite_score":0.47752,"best_fitness_score":0.99752,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":106.0,"contact_point_centroid":[0.54087,-0.02793,-0.00157],"force_p95":0.64383,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.68131,"mean_force":0.20502,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.54432,-0.02819,0.0286]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3394.0,"contact_point_centroid":[0.62319,0.11956,0.27948],"force_p95":0.14315,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.38776,"mean_force":0.09716,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.6178,0.13815,0.2788]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4169.0,"contact_point_centroid":[0.6228,0.15615,0.2808],"force_p95":0.12105,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.38712,"mean_force":0.0828,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.6176,0.13772,0.28048]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":9640.0,"contact_point_centroid":[0.54171,-0.04728,0.09236],"force_p95":0.07163,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30043,"mean_force":0.0508,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.5416,-0.02812,0.09049]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":9640.0,"contact_point_centroid":[0.54169,-0.00898,0.09241],"force_p95":0.07155,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28183,"mean_force":0.05034,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.5416,-0.02812,0.09049]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":17290.0,"contact_point_centroid":[0.54893,-0.02941,0.27796],"force_p95":0.10177,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2388,"mean_force":0.05768,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.5477,-0.01039,0.27601]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":17344.0,"contact_point_centroid":[0.54985,0.01033,0.27887],"force_p95":0.09784,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22046,"mean_force":0.0578,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.54853,-0.00868,0.277]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.54556,-0.02903,-0.00211],"force_p95":0.15074,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.21338,"mean_force":0.13135,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.54692,-0.02827,0.02858]},{"body_a":"world","body_b":"grasp_target","contact_count":1144.0,"contact_point_centroid":[0.5456,-0.02923,-0.00188],"force_p95":0.13644,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12305,"phase_index":0.0,"phase_name":"approach_to_object","phase_type":"approach","tcp_position_centroid":[0.51704,-0.01224,0.22372]},{"body_a":"world","body_b":"grasp_target","contact_count":1120.0,"contact_point_centroid":[0.5456,-0.02923,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.54374,-0.02677,0.09175]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4791.0,"contact_point_centroid":[0.54573,-0.00905,0.02902],"force_p95":0.07142,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11669,"mean_force":0.04479,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.54567,-0.02823,0.0271]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4960.0,"contact_point_centroid":[0.54576,-0.04747,0.02898],"force_p95":0.07186,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08723,"mean_force":0.04482,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.54567,-0.02823,0.0271]}],"total_contact_groups":12},"final_pose_error":0.01475,"key_states":{"actual_goal_position":[0.63284,0.16493,0.17692],"final_object_position":[0.63811,0.1582,0.18491],"final_tcp_position":[0.62681,0.15818,0.20433],"realised_goal_position":[0.63284,0.16493,0.17692],"realised_object_initial_position":[0.5456,-0.02923,0.03]},"phases":[{"n_steps":287.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.03],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.25864,"object_z_max":0.03,"phase_name":"approach_to_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"approach_object","tcp_end":[0.53615,-0.02517,0.14675],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.12117,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":280.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"descend_to_grasp","tcp_end":[0.55449,-0.02848,0.03784],"tcp_start":[0.53615,-0.02517,0.14675],"tcp_to_object_dist_end":0.01481,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54544,-0.02829,0.02558],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26053,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","tcp_end":[0.54564,-0.02823,0.02706],"tcp_start":[0.55449,-0.02848,0.03784],"tcp_to_object_dist_end":0.0015,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":482.0,"n_steps_budget":1000.0,"object_pos_end":[0.54117,-0.02818,0.15279],"object_pos_start":[0.54544,-0.02829,0.02558],"object_to_goal_dist_end":0.21512,"object_to_goal_dist_start":0.26053,"object_z_max":0.15253,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","subtask_id":"lift_object","tcp_end":[0.54163,-0.02815,0.15617],"tcp_start":[0.54564,-0.02823,0.02706],"tcp_to_object_dist_end":0.00341,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.62689,0.12108,0.33644],"object_pos_start":[0.54117,-0.02818,0.15279],"object_to_goal_dist_end":0.16554,"object_to_goal_dist_start":0.21512,"object_z_max":0.34923,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"transport_to_goal","tcp_end":[0.61111,0.12097,0.34896],"tcp_start":[0.54163,-0.02815,0.15617],"tcp_to_object_dist_end":0.02015,"terminated_normally":false,"termination_reason":"step_budget"},{"n_steps":348.0,"n_steps_budget":1000.0,"object_pos_end":[0.63811,0.1582,0.18491],"object_pos_start":[0.62689,0.12108,0.33644],"object_to_goal_dist_end":0.0117,"object_to_goal_dist_start":0.16554,"object_z_max":0.33644,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"final_placement","tcp_end":[0.62681,0.15818,0.20433],"tcp_start":[0.61111,0.12097,0.34896],"tcp_to_object_dist_end":0.02247,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.57258,"average_solve_count":248.0,"average_success_count":248.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_to_object.approach_speed":0.16338,"descend_to_grasp.descend_lateral_x":0.01274,"descend_to_grasp.descend_speed":0.09631,"descend_to_place.descend_z_offset":0.01626,"descend_to_place.place_speed":0.04142,"lift_object.lift_speed":0.03278,"transport_to_goal.arc_height":0.08472,"transport_to_goal.transport_speed":0.12393},"optimized_scores":{"best_composite_score":0.47018,"best_fitness_score":0.99018,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":94.0,"contact_point_centroid":[0.45872,-0.00017,-0.00155],"force_p95":0.51072,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.5334,"mean_force":0.2159,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.46144,-0.00023,0.03293]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6151.0,"contact_point_centroid":[0.59861,0.16339,0.21643],"force_p95":0.07138,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28959,"mean_force":0.04734,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.59893,0.14438,0.21397]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8320.0,"contact_point_centroid":[0.45932,0.01891,0.09451],"force_p95":0.07193,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26308,"mean_force":0.05127,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.45925,-0.00023,0.09261]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8320.0,"contact_point_centroid":[0.45934,-0.01938,0.09451],"force_p95":0.0715,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25562,"mean_force":0.05114,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.45925,-0.00023,0.09261]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4827.0,"contact_point_centroid":[0.59824,0.12511,0.21673],"force_p95":0.08305,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2469,"mean_force":0.05853,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.59889,0.14433,0.2146]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":15160.0,"contact_point_centroid":[0.50545,0.06751,0.25613],"force_p95":0.07348,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22147,"mean_force":0.05044,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.50535,0.04838,0.25426]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":15167.0,"contact_point_centroid":[0.50551,0.02928,0.2562],"force_p95":0.07315,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22,"mean_force":0.0504,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.50539,0.04842,0.25427]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.46283,-0.0001,-0.00202],"force_p95":0.12938,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.14328,"mean_force":0.12489,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.4636,-0.0002,0.03297]},{"body_a":"world","body_b":"grasp_target","contact_count":1072.0,"contact_point_centroid":[0.46286,-7e-05,-0.00188],"force_p95":0.1365,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12308,"phase_index":0.0,"phase_name":"approach_to_object","phase_type":"approach","tcp_position_centroid":[0.48266,-4e-05,0.22588]},{"body_a":"world","body_b":"grasp_target","contact_count":1088.0,"contact_point_centroid":[0.46286,-7e-05,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.46651,-9e-05,0.09422]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4844.0,"contact_point_centroid":[0.4626,-0.0194,0.03382],"force_p95":0.06797,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09973,"mean_force":0.04479,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.46252,-0.00021,0.03192]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4872.0,"contact_point_centroid":[0.46257,0.01899,0.03381],"force_p95":0.06804,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08533,"mean_force":0.04477,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.46253,-0.00021,0.03192]}],"total_contact_groups":12},"final_pose_error":0.01497,"key_states":{"actual_goal_position":[0.61015,0.15287,0.12219],"final_object_position":[0.60871,0.14977,0.13059],"final_tcp_position":[0.60413,0.14974,0.1518],"realised_goal_position":[0.61015,0.15287,0.12219],"realised_object_initial_position":[0.46286,-7e-05,0.03]},"phases":[{"n_steps":269.0,"n_steps_budget":1000.0,"object_pos_end":[0.46286,-7e-05,0.02602],"object_pos_start":[0.46286,-7e-05,0.03],"object_to_goal_dist_end":0.2331,"object_to_goal_dist_start":0.23148,"object_z_max":0.03,"phase_name":"approach_to_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"approach_object","tcp_end":[0.46524,-7e-05,0.14934],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.12335,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":272.0,"n_steps_budget":1000.0,"object_pos_end":[0.46286,-7e-05,0.02602],"object_pos_start":[0.46286,-7e-05,0.02602],"object_to_goal_dist_end":0.2331,"object_to_goal_dist_start":0.2331,"object_z_max":0.02602,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"descend_to_grasp","tcp_end":[0.4702,-0.00011,0.03969],"tcp_start":[0.46524,-7e-05,0.14934],"tcp_to_object_dist_end":0.01552,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.46273,-0.00019,0.02588],"object_pos_start":[0.46286,-7e-05,0.02602],"object_to_goal_dist_end":0.23331,"object_to_goal_dist_start":0.2331,"object_z_max":0.02602,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","tcp_end":[0.4625,-0.00021,0.03189],"tcp_start":[0.4702,-0.00011,0.03969],"tcp_to_object_dist_end":0.00601,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":416.0,"n_steps_budget":1000.0,"object_pos_end":[0.45892,-0.00021,0.14919],"object_pos_start":[0.46273,-0.00019,0.02588],"object_to_goal_dist_end":0.21687,"object_to_goal_dist_start":0.23331,"object_z_max":0.1489,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","subtask_id":"lift_object","tcp_end":[0.45931,-0.00021,0.15632],"tcp_start":[0.4625,-0.00021,0.03189],"tcp_to_object_dist_end":0.00714,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":758.0,"n_steps_budget":1000.0,"object_pos_end":[0.60024,0.13987,0.25602],"object_pos_start":[0.45892,-0.00021,0.14919],"object_to_goal_dist_end":0.13483,"object_to_goal_dist_start":0.21687,"object_z_max":0.2813,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"transport_to_goal","tcp_end":[0.59582,0.13973,0.27564],"tcp_start":[0.45931,-0.00021,0.15632],"tcp_to_object_dist_end":0.02011,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":282.0,"n_steps_budget":1000.0,"object_pos_end":[0.60871,0.14977,0.13059],"object_pos_start":[0.60024,0.13987,0.25602],"object_to_goal_dist_end":0.00907,"object_to_goal_dist_start":0.13483,"object_z_max":0.25602,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"final_placement","tcp_end":[0.60413,0.14974,0.1518],"tcp_start":[0.59582,0.13973,0.27564],"tcp_to_object_dist_end":0.0217,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```