## Search State

- **Seed**: 9
- **Iteration**: 7 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 6 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 9 | 0.4026 | 1.00 | ❌ rejected |
| 5 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 8 | 0.4576 | 1.00 | ✅ accepted |
| 4 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 8 | 0.0884 | 0.39 | ✅ accepted |
| 3 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | force_threshold_switch | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 9 | -0.3576 | 0.17 | ✅ accepted |
| 2 | rotate → pull → push → descend → descend → grasp → approach | impedance_motion | arc_cartesian | impedance_motion | linear_cartesian | linear_cartesian | — | linear_cartesian | impedance_control | impedance_control | impedance_control | admittance_control | position_control | position_control | position_control | pose_tolerance | time_limit | time_limit | pose_tolerance | contact_detected | grasp_success | pose_tolerance | 6 | -0.1650 | 0.13 | ❌ rejected |

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

## Current Skill (Q=0.403) — your mutation base

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
  - 0.1
  weight: 0.2
- id: lift_object
  anchor: object
  target_entity: object
  offset:
  - 0.0
  - 0.0
  - 0.15
  weight: 0.3
- id: place_at_goal
  target_entity: object
  weight: 0.5
phases:
- id: approach_object
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
    - 0.12
    tolerance: 0.01
    orientation:
      mode: none
  parameters:
    approach_height:
      type: scalar
      range:
      - 0.08
      - 0.15
      default: 0.12
      binds_to:
      - path: target.offset.z
        mode: replace
    approach_speed:
      type: scalar
      range:
      - 0.01
      - 0.15
      default: 0.08
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: reach_object
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
    - 0.06
    tolerance: 0.01
    orientation:
      mode: none
  parameters:
    descend_depth:
      type: scalar
      range:
      - 0.0
      - 0.1
      default: 0.06
      binds_to:
      - path: target.offset.z
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
- id: lift
  type: lift
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
    - 0.2
    tolerance: 0.015
    orientation:
      mode: none
  parameters:
    lift_height:
      type: scalar
      range:
      - 0.1
      - 0.3
      default: 0.2
      binds_to:
      - path: target.offset.z
        mode: replace
    lift_speed:
      type: scalar
      range:
      - 0.02
      - 0.15
      default: 0.08
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: lift_object
- id: transport_to_goal
  type: approach
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
    - 0.12
    tolerance: 0.015
    orientation:
      mode: none
  parameters:
    transport_speed:
      type: scalar
      range:
      - 0.02
      - 0.15
      default: 0.08
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: place_at_goal
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
    - 0.02
    tolerance: 0.015
    orientation:
      mode: none
  parameters:
    place_height_z:
      type: scalar
      range:
      - 0.0
      - 0.05
      default: 0.02
      binds_to:
      - path: target.offset.z
        mode: replace
    place_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: place_at_goal

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_object** (`approach`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.12], tolerance=0.01
  - orientation: mode=none
  - parameter_bindings:
    - approach_height: status=consumed; consumers=target.offset.z (replace)
    - approach_speed: status=consumed; consumers=generator.speed (replace)
- **descend_to_grasp** (`descend`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.06], tolerance=0.01
  - orientation: mode=none
  - parameter_bindings:
    - descend_depth: status=consumed; consumers=target.offset.z (replace)
- **grasp** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings: none
- **lift** (`lift`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.2], tolerance=0.015
  - orientation: mode=none
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset.z (replace)
    - lift_speed: status=consumed; consumers=generator.speed (replace)
- **transport_to_goal** (`approach`)
  - target: source=yaml, anchor=task_goal, entity=place_target, offset=[0.0, 0.0, 0.12], tolerance=0.015
  - orientation: mode=none
  - parameter_bindings:
    - transport_speed: status=consumed; consumers=generator.speed (replace)
- **descend_to_place** (`descend`)
  - target: source=yaml, anchor=task_goal, entity=place_target, offset=[0.0, 0.0, 0.02], tolerance=0.015
  - orientation: mode=none
  - parameter_bindings:
    - place_height_z: status=consumed; consumers=target.offset.z (replace)
    - place_speed: status=consumed; consumers=generator.speed (replace)

## Design Metrics

- **Composite score**: 0.403
- **task_score** (E): 1.000
- **fitness_score**: 0.973  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.570

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_object | 1.00 | 1.00 | 0.1351 |
| descend_to_grasp | 1.00 | 1.00 | 0.1253 |
| grasp | 1.00 | 1.00 | 0.0136 |
| lift | 1.00 | 1.00 | 0.1576 |
| transport_to_goal | 1.00 | 1.00 | 0.2214 |
| descend_to_place | 1.00 | 1.00 | 0.0762 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.510, -0.014, 0.171) | (0.515, -0.017, 0.030)→(0.515, -0.017, 0.026) | 0.268→0.270 | 1.00 / 4.000 | 28.827 | 0.138 |
| descend_to_grasp | descend | 1.00 / step_budget | (0.510, -0.014, 0.171)→(0.510, -0.016, 0.045) | (0.515, -0.017, 0.026)→(0.515, -0.017, 0.026) | 0.270→0.270 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp | grasp | 1.00 / step_budget | (0.510, -0.016, 0.045)→(0.501, -0.016, 0.035) | (0.515, -0.017, 0.026)→(0.515, -0.017, 0.026) | 0.270→0.270 | 1.00 / 42.667 | 0.142 | 0.184 |
| lift | lift | 1.00 / step_budget | (0.501, -0.016, 0.035)→(0.510, -0.017, 0.193) | (0.515, -0.017, 0.026)→(0.525, -0.017, 0.180) | 0.270→0.226 | 1.00 / 36.000 | 0.096 | 0.539 |
| transport_to_goal | approach | 1.00 / step_budget | (0.510, -0.017, 0.193)→(0.605, 0.162, 0.272) | (0.525, -0.017, 0.180)→(0.620, 0.166, 0.256) | 0.226→0.089 | 1.00 / 26.667 | 0.105 | 0.223 |
| descend_to_place | descend | 1.00 / step_budget | (0.605, 0.162, 0.272)→(0.611, 0.176, 0.197) | (0.620, 0.166, 0.256)→(0.625, 0.180, 0.178) | 0.089→0.012 | 1.00 / 25.667 | 0.111 | 0.414 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.460
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 1.000
- phase_score: 0.548
- phase_breakdown.place_at_goal_score: 0.520
- phase_breakdown.lift_object_score: 0.834
- phase_breakdown.reach_object_score: 0.188
- grasp_place_fitness: 0.973

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.973
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 1.000
- **Median Q (composite search score)**: 0.403
- **K-run variance**: 0.0000
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.395


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.80863,"average_solve_count":371.0,"average_success_count":371.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_height":0.10081,"approach_object.approach_speed":0.0125,"descend_to_grasp.descend_depth":2e-05,"descend_to_grasp.descend_speed":0.10922,"descend_to_place.place_height_z":0.00526,"descend_to_place.place_speed":0.01345,"lift.lift_height":0.18593,"lift.lift_speed":0.06305,"transport_to_goal.transport_speed":0.12842},"optimized_scores":{"best_composite_score":0.40251,"best_fitness_score":0.97251,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":75.0,"contact_point_centroid":[0.53403,-0.02069,-0.00148],"force_p95":0.44076,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.53736,"mean_force":0.17588,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.5207,-0.02046,0.03489]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2264.0,"contact_point_centroid":[0.61221,0.196,0.27393],"force_p95":0.1082,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.38805,"mean_force":0.07597,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.6032,0.21314,0.27284]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6983.0,"contact_point_centroid":[0.52578,-0.03984,0.11185],"force_p95":0.08425,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.35104,"mean_force":0.06153,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52496,-0.02064,0.10912]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2549.0,"contact_point_centroid":[0.60032,0.23155,0.27533],"force_p95":0.0915,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.34777,"mean_force":0.06408,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.60321,0.21314,0.27286]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8530.0,"contact_point_centroid":[0.52617,-0.00168,0.10918],"force_p95":0.08195,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27989,"mean_force":0.05217,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52481,-0.02063,0.10736]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":7523.0,"contact_point_centroid":[0.56846,0.0665,0.24236],"force_p95":0.1086,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22394,"mean_force":0.07051,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.56348,0.08492,0.24104]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53707,-0.02135,-0.00207],"force_p95":0.14492,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.19501,"mean_force":0.12835,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.52286,-0.02048,0.03526]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8811.0,"contact_point_centroid":[0.56391,0.10631,0.24417],"force_p95":0.09005,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18122,"mean_force":0.05914,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.56433,0.08766,0.2425]},{"body_a":"world","body_b":"grasp_target","contact_count":1068.0,"contact_point_centroid":[0.53702,-0.02132,-0.00188],"force_p95":0.1365,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12308,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.51231,-0.00828,0.22991]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4815.0,"contact_point_centroid":[0.5234,-0.00155,0.03526],"force_p95":0.07022,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12572,"mean_force":0.04465,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.52161,-0.02046,0.03385]},{"body_a":"world","body_b":"grasp_target","contact_count":812.0,"contact_point_centroid":[0.53702,-0.02132,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.52818,-0.01912,0.09907]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4122.0,"contact_point_centroid":[0.52294,-0.0397,0.03659],"force_p95":0.08974,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09304,"mean_force":0.05489,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.52162,-0.02046,0.03385]}],"total_contact_groups":12},"final_pose_error":0.01984,"key_states":{"actual_goal_position":[0.61031,0.22775,0.20741],"final_object_position":[0.61876,0.22647,0.21384],"final_tcp_position":[0.60559,0.22108,0.23075],"realised_goal_position":[0.61031,0.22775,0.20741],"realised_object_initial_position":[0.53702,-0.02132,0.03]},"peak_contact_force":0.53736,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":268.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.03],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31446,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1068.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.52762,-0.0177,0.15327],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.12765,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":203.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.12262,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":812.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.53082,-0.02057,0.04468],"tcp_start":[0.52762,-0.0177,0.15327],"tcp_to_object_dist_end":0.01968,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53707,-0.02097,0.02573],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.3166,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.14464,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10737.0,"raw_peak_contact_force":0.19501,"tcp_end":[0.52158,-0.02046,0.03381],"tcp_start":[0.53082,-0.02057,0.04468],"tcp_to_object_dist_end":0.01748,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":411.0,"n_steps_budget":1000.0,"object_pos_end":[0.5464,-0.02131,0.17686],"object_pos_start":[0.53707,-0.02097,0.02573],"object_to_goal_dist_end":0.25894,"object_to_goal_dist_start":0.3166,"object_z_max":0.1765,"peak_contact_force":0.08268,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":15588.0,"raw_peak_contact_force":0.53736,"subtask_id":"lift_object","tcp_end":[0.53211,-0.02085,0.18739],"tcp_start":[0.52158,-0.02046,0.03381],"tcp_to_object_dist_end":0.01775,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":29.0,"n_steps":504.0,"n_steps_budget":1000.0,"object_pos_end":[0.61639,0.21167,0.2938],"object_pos_start":[0.5464,-0.02131,0.17686],"object_to_goal_dist_end":0.08808,"object_to_goal_dist_start":0.25894,"object_z_max":0.29359,"peak_contact_force":0.10806,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":16334.0,"raw_peak_contact_force":0.22394,"subtask_id":"place_at_goal","tcp_end":[0.60231,0.2068,0.30778],"tcp_start":[0.53211,-0.02085,0.18739],"tcp_to_object_dist_end":0.02043,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":30.0,"n_steps":163.0,"n_steps_budget":1000.0,"object_pos_end":[0.61876,0.22647,0.21384],"object_pos_start":[0.61639,0.21167,0.2938],"object_to_goal_dist_end":0.01069,"object_to_goal_dist_start":0.08808,"object_z_max":0.29393,"peak_contact_force":0.10779,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4813.0,"raw_peak_contact_force":0.38805,"subtask_id":"place_at_goal","tcp_end":[0.60559,0.22108,0.23075],"tcp_start":[0.60231,0.2068,0.30778],"tcp_to_object_dist_end":0.0221,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.66216,"average_solve_count":222.0,"average_success_count":222.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_height":0.12642,"approach_object.approach_speed":0.06512,"descend_to_grasp.descend_depth":0.0005,"descend_to_grasp.descend_speed":0.0963,"descend_to_place.place_height_z":0.01248,"descend_to_place.place_speed":0.05395,"lift.lift_height":0.21694,"lift.lift_speed":0.07164,"transport_to_goal.transport_speed":0.10667},"optimized_scores":{"best_composite_score":0.40214,"best_fitness_score":0.97214,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":74.0,"contact_point_centroid":[0.54237,-0.02826,-0.00152],"force_p95":0.48165,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55723,"mean_force":0.17623,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52907,-0.02799,0.03507]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1686.0,"contact_point_centroid":[0.63131,0.13277,0.24823],"force_p95":0.12064,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.40383,"mean_force":0.08417,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.62307,0.15027,0.24628]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1875.0,"contact_point_centroid":[0.62333,0.16934,0.24835],"force_p95":0.11699,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.37396,"mean_force":0.07935,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.62311,0.15038,0.2456]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8559.0,"contact_point_centroid":[0.53464,-0.04741,0.12938],"force_p95":0.10435,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.36494,"mean_force":0.06217,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.53382,-0.0282,0.12688]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":9935.0,"contact_point_centroid":[0.53512,-0.0095,0.12451],"force_p95":0.0873,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29339,"mean_force":0.05235,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.53351,-0.02819,0.12279]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4729.0,"contact_point_centroid":[0.58751,0.04274,0.25018],"force_p95":0.11671,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22187,"mean_force":0.08091,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.58195,0.06128,0.24844]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.54567,-0.02924,-0.0021],"force_p95":0.15344,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.21076,"mean_force":0.13065,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.53129,-0.02804,0.0354]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6224.0,"contact_point_centroid":[0.57925,0.07213,0.24679],"force_p95":0.10055,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1798,"mean_force":0.06338,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.57833,0.05353,0.24556]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4797.0,"contact_point_centroid":[0.53201,-0.00913,0.0353],"force_p95":0.07124,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13943,"mean_force":0.04472,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.53003,-0.02801,0.03395]},{"body_a":"world","body_b":"grasp_target","contact_count":892.0,"contact_point_centroid":[0.5456,-0.02923,-0.00185],"force_p95":0.13709,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12317,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.51572,-0.01119,0.24077]},{"body_a":"world","body_b":"grasp_target","contact_count":992.0,"contact_point_centroid":[0.5456,-0.02923,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.53556,-0.02587,0.11153]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3993.0,"contact_point_centroid":[0.53148,-0.04728,0.03711],"force_p95":0.0909,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09472,"mean_force":0.05621,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.53004,-0.02801,0.03395]}],"total_contact_groups":12},"final_pose_error":0.01968,"key_states":{"actual_goal_position":[0.63284,0.16493,0.17692],"final_object_position":[0.64112,0.16228,0.19001],"final_tcp_position":[0.62669,0.1582,0.20685],"realised_goal_position":[0.63284,0.16493,0.17692],"realised_object_initial_position":[0.5456,-0.02923,0.03]},"peak_contact_force":43.8638,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":224.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.03],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.25864,"object_z_max":0.03,"peak_contact_force":43.8638,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":892.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.53405,-0.02361,0.17772],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.15225,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":248.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.12262,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":992.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.53931,-0.02821,0.04509],"tcp_start":[0.53405,-0.02361,0.17772],"tcp_to_object_dist_end":0.02011,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54566,-0.02864,0.02563],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26069,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.15232,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10590.0,"raw_peak_contact_force":0.21076,"tcp_end":[0.53,-0.02801,0.03391],"tcp_start":[0.53931,-0.02821,0.04509],"tcp_to_object_dist_end":0.01772,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":38.0,"n_steps":483.0,"n_steps_budget":1000.0,"object_pos_end":[0.55596,-0.02916,0.20653],"object_pos_start":[0.54566,-0.02864,0.02563],"object_to_goal_dist_end":0.21085,"object_to_goal_dist_start":0.26069,"object_z_max":0.20616,"peak_contact_force":0.1139,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":18568.0,"raw_peak_contact_force":0.55723,"subtask_id":"lift_object","tcp_end":[0.54122,-0.02848,0.21809],"tcp_start":[0.53,-0.02801,0.03391],"tcp_to_object_dist_end":0.01875,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":28.0,"n_steps":376.0,"n_steps_budget":1000.0,"object_pos_end":[0.63632,0.14706,0.26617],"object_pos_start":[0.55596,-0.02916,0.20653],"object_to_goal_dist_end":0.09109,"object_to_goal_dist_start":0.21085,"object_z_max":0.26602,"peak_contact_force":0.10456,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":10953.0,"raw_peak_contact_force":0.22187,"subtask_id":"place_at_goal","tcp_end":[0.62084,0.1433,0.28003],"tcp_start":[0.54122,-0.02848,0.21809],"tcp_to_object_dist_end":0.02111,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":25.0,"n_steps":143.0,"n_steps_budget":1000.0,"object_pos_end":[0.64112,0.16228,0.19001],"object_pos_start":[0.63632,0.14706,0.26617],"object_to_goal_dist_end":0.01571,"object_to_goal_dist_start":0.09109,"object_z_max":0.26624,"peak_contact_force":0.11422,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3561.0,"raw_peak_contact_force":0.40383,"subtask_id":"place_at_goal","tcp_end":[0.62669,0.1582,0.20685],"tcp_start":[0.62084,0.1433,0.28003],"tcp_to_object_dist_end":0.02254,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.83415,"average_solve_count":205.0,"average_success_count":205.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_height":0.12695,"approach_object.approach_speed":0.07111,"descend_to_grasp.descend_depth":0.00105,"descend_to_grasp.descend_speed":0.07286,"descend_to_place.place_height_z":0.0143,"descend_to_place.place_speed":0.06434,"lift.lift_height":0.17064,"lift.lift_speed":0.12938,"transport_to_goal.transport_speed":0.07616},"optimized_scores":{"best_composite_score":0.40327,"best_fitness_score":0.97327,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":63.0,"contact_point_centroid":[0.46063,-0.0005,-0.00141],"force_p95":0.49685,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.52389,"mean_force":0.14615,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.44983,-0.00031,0.03924]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1739.0,"contact_point_centroid":[0.5968,0.16029,0.19687],"force_p95":0.13781,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.45087,"mean_force":0.08824,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.59555,0.1412,0.19335]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1751.0,"contact_point_centroid":[0.60445,0.12404,0.19365],"force_p95":0.13465,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.4214,"mean_force":0.08649,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.59575,0.14141,0.19187]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6115.0,"contact_point_centroid":[0.45361,0.01883,0.10168],"force_p95":0.08753,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28959,"mean_force":0.05596,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.45247,-0.00032,0.0995]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6080.0,"contact_point_centroid":[0.45395,-0.01945,0.10293],"force_p95":0.08457,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2842,"mean_force":0.05612,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.45257,-0.00032,0.10069]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4744.0,"contact_point_centroid":[0.52779,0.04687,0.19835],"force_p95":0.13131,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22345,"mean_force":0.08485,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.52114,0.06488,0.19696]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4608.0,"contact_point_centroid":[0.52425,0.08437,0.19992],"force_p95":0.12893,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20494,"mean_force":0.08529,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.52163,0.06539,0.19716]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.46285,-0.00011,-0.00202],"force_p95":0.13008,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.14511,"mean_force":0.12476,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.45205,-0.00027,0.03915]},{"body_a":"world","body_b":"grasp_target","contact_count":796.0,"contact_point_centroid":[0.46286,-7e-05,-0.00184],"force_p95":0.13736,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12324,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.4842,-4e-05,0.24277]},{"body_a":"world","body_b":"grasp_target","contact_count":1052.0,"contact_point_centroid":[0.46286,-7e-05,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.46257,-0.00013,0.11416]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5332.0,"contact_point_centroid":[0.45106,-0.01954,0.03978],"force_p95":0.06338,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09261,"mean_force":0.04111,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.45091,-0.00028,0.03805]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5368.0,"contact_point_centroid":[0.45104,0.01898,0.03977],"force_p95":0.06354,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08216,"mean_force":0.04112,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.45091,-0.00028,0.03805]}],"total_contact_groups":12},"final_pose_error":0.01953,"key_states":{"actual_goal_position":[0.61015,0.15287,0.12219],"final_object_position":[0.61601,0.15189,0.1312],"final_tcp_position":[0.60178,0.14755,0.1533],"realised_goal_position":[0.61015,0.15287,0.12219],"realised_object_initial_position":[0.46286,-7e-05,0.03]},"peak_contact_force":42.49502,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":200.0,"n_steps_budget":1000.0,"object_pos_end":[0.46286,-7e-05,0.02602],"object_pos_start":[0.46286,-7e-05,0.03],"object_to_goal_dist_end":0.2331,"object_to_goal_dist_start":0.23148,"object_z_max":0.03,"peak_contact_force":42.49502,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":796.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.4676,-9e-05,0.18088],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.15493,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":263.0,"n_steps_budget":1000.0,"object_pos_end":[0.46286,-7e-05,0.02602],"object_pos_start":[0.46286,-7e-05,0.02602],"object_to_goal_dist_end":0.2331,"object_to_goal_dist_start":0.2331,"object_z_max":0.02602,"peak_contact_force":0.12262,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1052.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.45946,-0.00014,0.04658],"tcp_start":[0.4676,-9e-05,0.18088],"tcp_to_object_dist_end":0.02084,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":48.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.46274,-0.00024,0.0259],"object_pos_start":[0.46286,-7e-05,0.02602],"object_to_goal_dist_end":0.23333,"object_to_goal_dist_start":0.2331,"object_z_max":0.02602,"peak_contact_force":0.12975,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12500.0,"raw_peak_contact_force":0.14511,"tcp_end":[0.45088,-0.00028,0.03802],"tcp_start":[0.45946,-0.00014,0.04658],"tcp_to_object_dist_end":0.01696,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":33.0,"n_steps":311.0,"n_steps_budget":780.0,"object_pos_end":[0.47411,-0.00012,0.15612],"object_pos_start":[0.46274,-0.00024,0.0259],"object_to_goal_dist_end":0.20751,"object_to_goal_dist_start":0.23333,"object_z_max":0.15573,"peak_contact_force":0.09014,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":12258.0,"raw_peak_contact_force":0.52389,"subtask_id":"lift_object","tcp_end":[0.45816,-0.00029,0.17223],"tcp_start":[0.45088,-0.00028,0.03802],"tcp_to_object_dist_end":0.02267,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":386.0,"n_steps_budget":1000.0,"object_pos_end":[0.6073,0.1399,0.20823],"object_pos_start":[0.47411,-0.00012,0.15612],"object_to_goal_dist_end":0.08706,"object_to_goal_dist_start":0.20751,"object_z_max":0.20809,"peak_contact_force":0.10188,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":9352.0,"raw_peak_contact_force":0.22345,"subtask_id":"place_at_goal","tcp_end":[0.59132,0.13582,0.22704],"tcp_start":[0.45816,-0.00029,0.17223],"tcp_to_object_dist_end":0.02502,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":22.0,"n_steps":147.0,"n_steps_budget":1000.0,"object_pos_end":[0.61601,0.15189,0.1312],"object_pos_start":[0.6073,0.1399,0.20823],"object_to_goal_dist_end":0.01079,"object_to_goal_dist_start":0.08706,"object_z_max":0.20834,"peak_contact_force":0.11077,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3490.0,"raw_peak_contact_force":0.45087,"subtask_id":"place_at_goal","tcp_end":[0.60178,0.14755,0.1533],"tcp_start":[0.59132,0.13582,0.22704],"tcp_to_object_dist_end":0.02665,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```