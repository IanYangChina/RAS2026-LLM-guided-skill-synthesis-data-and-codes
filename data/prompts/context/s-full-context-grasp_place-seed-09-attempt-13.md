## Search State

- **Seed**: 9
- **Iteration**: 14 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 13 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 8 | 0.4478 | 1.00 | ❌ rejected |
| 12 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 8 | 0.4563 | 1.00 | ❌ rejected |
| 11 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 8 | 0.4576 | 1.00 | ❌ rejected |
| 10 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 8 | 0.4575 | 1.00 | ❌ rejected |
| 9 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | time_limit | time_limit | grasp_success | time_limit | time_limit | time_limit | 13 | -0.0112 | 0.57 | ❌ rejected |

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

## Current Skill (Q=0.448) — your mutation base

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

- **Composite score**: 0.448
- **task_score** (E): 1.000
- **fitness_score**: 0.968  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.520

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_object | 1.00 | 1.00 | 0.1484 |
| descend_to_grasp | 1.00 | 1.00 | 0.1062 |
| grasp | 1.00 | 1.00 | 0.0143 |
| lift | 1.00 | 1.00 | 0.1897 |
| transport_to_goal | 1.00 | 1.00 | 0.2170 |
| descend_to_place | 1.00 | 1.00 | 0.0711 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.510, -0.014, 0.157) | (0.515, -0.017, 0.030)→(0.515, -0.017, 0.026) | 0.268→0.270 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_to_grasp | descend | 1.00 / step_budget | (0.510, -0.014, 0.157)→(0.510, -0.016, 0.051) | (0.515, -0.017, 0.026)→(0.515, -0.017, 0.026) | 0.270→0.270 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp | grasp | 1.00 / step_budget | (0.510, -0.016, 0.051)→(0.501, -0.016, 0.040) | (0.515, -0.017, 0.026)→(0.515, -0.017, 0.026) | 0.270→0.270 | 1.00 / 43.000 | 0.144 | 0.190 |
| lift | lift | 1.00 / step_budget | (0.501, -0.016, 0.040)→(0.511, -0.017, 0.230) | (0.515, -0.017, 0.026)→(0.526, -0.017, 0.211) | 0.270→0.229 | 1.00 / 34.333 | 97.074 | 0.464 |
| transport_to_goal | approach | 1.00 / step_budget | (0.511, -0.017, 0.230)→(0.606, 0.165, 0.276) | (0.526, -0.017, 0.211)→(0.619, 0.169, 0.254) | 0.229→0.086 | 1.00 / 27.667 | 0.102 | 0.208 |
| descend_to_place | descend | 1.00 / step_budget | (0.606, 0.165, 0.276)→(0.612, 0.176, 0.206) | (0.619, 0.169, 0.254)→(0.624, 0.180, 0.181) | 0.086→0.015 | 1.00 / 23.333 | 0.120 | 0.452 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.604
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 1.000
- phase_score: 0.584
- phase_breakdown.place_at_goal_score: 0.593
- phase_breakdown.lift_object_score: 0.823
- phase_breakdown.reach_object_score: 0.201
- grasp_place_fitness: 0.968

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.968
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 1.000
- **Median Q (composite search score)**: 0.448
- **K-run variance**: 0.0000
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.375


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.41259,"average_solve_count":286.0,"average_success_count":286.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_height":0.08073,"approach_object.approach_speed":0.11841,"descend_to_grasp.descend_depth":2e-05,"descend_to_place.place_height_z":0.01674,"descend_to_place.place_speed":0.05923,"lift.lift_height":0.29938,"lift.lift_speed":0.03637,"transport_to_goal.transport_speed":0.07158},"optimized_scores":{"best_composite_score":0.44792,"best_fitness_score":0.96792,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"left_finger","body_b":"grasp_target","contact_count":1060.0,"contact_point_centroid":[0.61415,0.19652,0.28683],"force_p95":0.15415,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.47178,"mean_force":0.10629,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.60346,0.21279,0.28711]},{"body_a":"world","body_b":"grasp_target","contact_count":80.0,"contact_point_centroid":[0.53451,-0.02048,-0.00153],"force_p95":0.37003,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.42523,"mean_force":0.15726,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52023,-0.02027,0.03971]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1444.0,"contact_point_centroid":[0.60234,0.23172,0.28897],"force_p95":0.13128,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.41815,"mean_force":0.0811,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.6035,0.21294,0.28629]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":11985.0,"contact_point_centroid":[0.52646,-0.03969,0.16827],"force_p95":0.10841,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30088,"mean_force":0.06285,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52525,-0.02051,0.16603]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":14418.0,"contact_point_centroid":[0.5269,-0.00183,0.16785],"force_p95":0.08553,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23982,"mean_force":0.05171,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52527,-0.02051,0.1661]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53708,-0.02136,-0.00209],"force_p95":0.14825,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.20157,"mean_force":0.1294,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.52241,-0.02029,0.04017]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":7075.0,"contact_point_centroid":[0.57417,0.077,0.30817],"force_p95":0.11287,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18297,"mean_force":0.07602,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.56795,0.09519,0.30661]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8219.0,"contact_point_centroid":[0.56651,0.10881,0.30749],"force_p95":0.09766,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15036,"mean_force":0.0644,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.56642,0.09018,0.3062]},{"body_a":"world","body_b":"grasp_target","contact_count":1096.0,"contact_point_centroid":[0.53702,-0.02132,-0.00188],"force_p95":0.1365,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12307,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.51306,-0.00869,0.21837]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4811.0,"contact_point_centroid":[0.5231,-0.00138,0.04017],"force_p95":0.06936,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13272,"mean_force":0.04467,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.52119,-0.02027,0.03878]},{"body_a":"world","body_b":"grasp_target","contact_count":532.0,"contact_point_centroid":[0.53702,-0.02132,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.52863,-0.01919,0.09264]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3978.0,"contact_point_centroid":[0.5229,-0.03953,0.04182],"force_p95":0.0893,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09323,"mean_force":0.05605,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.52119,-0.02027,0.03879]}],"total_contact_groups":12},"final_pose_error":0.0246,"key_states":{"actual_goal_position":[0.61031,0.22775,0.20741],"final_object_position":[0.61702,0.22573,0.2239],"final_tcp_position":[0.60572,0.22024,0.24712],"realised_goal_position":[0.61031,0.22775,0.20741],"realised_object_initial_position":[0.53702,-0.02132,0.03]},"peak_contact_force":291.00858,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":275.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.03],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31446,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1096.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.52805,-0.01804,0.13357],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.10797,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":133.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":532.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.53074,-0.02038,0.05022],"tcp_start":[0.52805,-0.01804,0.13357],"tcp_to_object_dist_end":0.02502,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53707,-0.02091,0.02568],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31658,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.14746,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10589.0,"raw_peak_contact_force":0.20157,"tcp_end":[0.52116,-0.02027,0.03875],"tcp_start":[0.53074,-0.02038,0.05022],"tcp_to_object_dist_end":0.0206,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":33.0,"n_steps":708.0,"n_steps_budget":1000.0,"object_pos_end":[0.5478,-0.02136,0.2831],"object_pos_start":[0.53707,-0.02091,0.02568],"object_to_goal_dist_end":0.26776,"object_to_goal_dist_start":0.31658,"object_z_max":0.28274,"peak_contact_force":291.00858,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":26483.0,"raw_peak_contact_force":0.42523,"subtask_id":"lift_object","tcp_end":[0.5338,-0.02081,0.30045],"tcp_start":[0.52116,-0.02027,0.03875],"tcp_to_object_dist_end":0.0223,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":29.0,"n_steps":520.0,"n_steps_budget":1000.0,"object_pos_end":[0.61473,0.21166,0.29624],"object_pos_start":[0.5478,-0.02136,0.2831],"object_to_goal_dist_end":0.09038,"object_to_goal_dist_start":0.26776,"object_z_max":0.29621,"peak_contact_force":0.10685,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":15294.0,"raw_peak_contact_force":0.18297,"subtask_id":"place_at_goal","tcp_end":[0.60237,0.20689,0.31702],"tcp_start":[0.5338,-0.02081,0.30045],"tcp_to_object_dist_end":0.02464,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":19.0,"n_steps":116.0,"n_steps_budget":1000.0,"object_pos_end":[0.61702,0.22573,0.2239],"object_pos_start":[0.61473,0.21166,0.29624],"object_to_goal_dist_end":0.01791,"object_to_goal_dist_start":0.09038,"object_z_max":0.29624,"peak_contact_force":0.15355,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2504.0,"raw_peak_contact_force":0.47178,"subtask_id":"place_at_goal","tcp_end":[0.60572,0.22024,0.24712],"tcp_start":[0.60237,0.20689,0.31702],"tcp_to_object_dist_end":0.0264,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.53112,"average_solve_count":241.0,"average_success_count":241.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_height":0.10341,"approach_object.approach_speed":0.08888,"descend_to_grasp.descend_depth":5e-05,"descend_to_place.place_height_z":0.00132,"descend_to_place.place_speed":0.02908,"lift.lift_height":0.187,"lift.lift_speed":0.07241,"transport_to_goal.transport_speed":0.09878},"optimized_scores":{"best_composite_score":0.44802,"best_fitness_score":0.96802,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":76.0,"contact_point_centroid":[0.54253,-0.02777,-0.00151],"force_p95":0.4175,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.49315,"mean_force":0.14847,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52861,-0.02778,0.03951]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1798.0,"contact_point_centroid":[0.63243,0.1361,0.2472],"force_p95":0.11027,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.39535,"mean_force":0.07342,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.6247,0.15376,0.24603]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":7095.0,"contact_point_centroid":[0.53418,-0.04727,0.11575],"force_p95":0.10274,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.35292,"mean_force":0.06154,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.53333,-0.02806,0.11334]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1822.0,"contact_point_centroid":[0.62447,0.17267,0.24872],"force_p95":0.10456,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.34477,"mean_force":0.07421,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.62471,0.15376,0.24611]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8106.0,"contact_point_centroid":[0.53487,-0.00935,0.11228],"force_p95":0.08803,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28079,"mean_force":0.05358,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.53309,-0.02805,0.11064]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.54567,-0.02926,-0.00212],"force_p95":0.1572,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.21226,"mean_force":0.13171,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.53078,-0.02783,0.03973]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6708.0,"contact_point_centroid":[0.58804,0.04595,0.23547],"force_p95":0.11315,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20039,"mean_force":0.07896,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.58261,0.06449,0.23401]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8934.0,"contact_point_centroid":[0.58007,0.07643,0.23184],"force_p95":0.09377,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16735,"mean_force":0.05988,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.57948,0.05785,0.23049]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4798.0,"contact_point_centroid":[0.53166,-0.00892,0.03963],"force_p95":0.07182,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14423,"mean_force":0.04473,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.52954,-0.02779,0.0383]},{"body_a":"world","body_b":"grasp_target","contact_count":1004.0,"contact_point_centroid":[0.5456,-0.02923,-0.00187],"force_p95":0.13691,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12311,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.51628,-0.01161,0.22937]},{"body_a":"world","body_b":"grasp_target","contact_count":668.0,"contact_point_centroid":[0.5456,-0.02923,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.53614,-0.0261,0.10342]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3993.0,"contact_point_centroid":[0.53115,-0.04707,0.04146],"force_p95":0.08995,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09474,"mean_force":0.05495,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.52955,-0.02779,0.03831]}],"total_contact_groups":12},"final_pose_error":0.02485,"key_states":{"actual_goal_position":[0.63284,0.16493,0.17692],"final_object_position":[0.63986,0.16334,0.18023],"final_tcp_position":[0.62733,0.15943,0.20184],"realised_goal_position":[0.63284,0.16493,0.17692],"realised_object_initial_position":[0.5456,-0.02923,0.03]},"peak_contact_force":0.49315,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":252.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.03],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.25864,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1004.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.53493,-0.02425,0.15539],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.1299,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":167.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":668.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.53918,-0.028,0.05006],"tcp_start":[0.53493,-0.02425,0.15539],"tcp_to_object_dist_end":0.02491,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54564,-0.02859,0.02558],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26069,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.15547,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10591.0,"raw_peak_contact_force":0.21226,"tcp_end":[0.52951,-0.02779,0.03826],"tcp_start":[0.53918,-0.028,0.05006],"tcp_to_object_dist_end":0.02053,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":39.0,"n_steps":397.0,"n_steps_budget":1000.0,"object_pos_end":[0.55519,-0.02923,0.17277],"object_pos_start":[0.54564,-0.02859,0.02558],"object_to_goal_dist_end":0.20915,"object_to_goal_dist_start":0.26069,"object_z_max":0.17241,"peak_contact_force":0.11141,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":15277.0,"raw_peak_contact_force":0.49315,"subtask_id":"lift_object","tcp_end":[0.5406,-0.0284,0.1883],"tcp_start":[0.52951,-0.02779,0.03826],"tcp_to_object_dist_end":0.02132,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":29.0,"n_steps":522.0,"n_steps_budget":1000.0,"object_pos_end":[0.63715,0.15279,0.26121],"object_pos_start":[0.55519,-0.02923,0.17277],"object_to_goal_dist_end":0.08527,"object_to_goal_dist_start":0.20915,"object_z_max":0.26105,"peak_contact_force":0.10516,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":15642.0,"raw_peak_contact_force":0.20039,"subtask_id":"place_at_goal","tcp_end":[0.62332,0.1492,0.28002],"tcp_start":[0.5406,-0.0284,0.1883],"tcp_to_object_dist_end":0.02362,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":25.0,"n_steps":134.0,"n_steps_budget":1000.0,"object_pos_end":[0.63986,0.16334,0.18023],"object_pos_start":[0.63715,0.15279,0.26121],"object_to_goal_dist_end":0.00792,"object_to_goal_dist_start":0.08527,"object_z_max":0.26126,"peak_contact_force":0.11473,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3620.0,"raw_peak_contact_force":0.39535,"subtask_id":"place_at_goal","tcp_end":[0.62733,0.15943,0.20184],"tcp_start":[0.62332,0.1492,0.28002],"tcp_to_object_dist_end":0.02529,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.13214,"average_solve_count":280.0,"average_success_count":280.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_height":0.12813,"approach_object.approach_speed":0.01193,"descend_to_grasp.descend_depth":0.00188,"descend_to_place.place_height_z":0.02388,"descend_to_place.place_speed":0.04986,"lift.lift_height":0.19881,"lift.lift_speed":0.14011,"transport_to_goal.transport_speed":0.07064},"optimized_scores":{"best_composite_score":0.44745,"best_fitness_score":0.96745,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"right_finger","body_b":"grasp_target","contact_count":1392.0,"contact_point_centroid":[0.59905,0.16208,0.2038],"force_p95":0.11939,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.48978,"mean_force":0.08079,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.59717,0.14266,0.20197]},{"body_a":"world","body_b":"grasp_target","contact_count":66.0,"contact_point_centroid":[0.46051,-0.00028,-0.00137],"force_p95":0.43095,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.47244,"mean_force":0.12213,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.45028,-0.00031,0.04475]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1385.0,"contact_point_centroid":[0.60669,0.12552,0.20149],"force_p95":0.11702,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.42453,"mean_force":0.08004,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.59718,0.14268,0.20183]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":7442.0,"contact_point_centroid":[0.45436,0.01879,0.1185],"force_p95":0.08683,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29418,"mean_force":0.05432,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.45296,-0.00036,0.11595]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":7031.0,"contact_point_centroid":[0.45441,-0.01953,0.11941],"force_p95":0.08913,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27269,"mean_force":0.05667,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.45301,-0.00036,0.11699]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5221.0,"contact_point_centroid":[0.53311,0.05208,0.21396],"force_p95":0.14423,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24163,"mean_force":0.09119,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.52631,0.07008,0.21397]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5691.0,"contact_point_centroid":[0.52936,0.08907,0.21507],"force_p95":0.1328,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22207,"mean_force":0.08359,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.52636,0.07012,0.21398]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.46285,-0.00013,-0.00203],"force_p95":0.13097,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.15652,"mean_force":0.12505,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.45254,-0.00026,0.04455]},{"body_a":"world","body_b":"grasp_target","contact_count":848.0,"contact_point_centroid":[0.46286,-7e-05,-0.00185],"force_p95":0.13728,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.1232,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.48463,-4e-05,0.24518]},{"body_a":"world","body_b":"grasp_target","contact_count":844.0,"contact_point_centroid":[0.46286,-7e-05,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.46326,-0.00012,0.11823]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5092.0,"contact_point_centroid":[0.45096,-0.0196,0.04603],"force_p95":0.06557,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09332,"mean_force":0.04304,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.45141,-0.00028,0.04347]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5847.0,"contact_point_centroid":[0.45124,0.01894,0.04597],"force_p95":0.05987,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07744,"mean_force":0.03796,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.45141,-0.00028,0.04347]}],"total_contact_groups":12},"final_pose_error":0.02464,"key_states":{"actual_goal_position":[0.61015,0.15287,0.12219],"final_object_position":[0.61369,0.15171,0.14003],"final_tcp_position":[0.60179,0.1473,0.16857],"realised_goal_position":[0.61015,0.15287,0.12219],"realised_object_initial_position":[0.46286,-7e-05,0.03]},"peak_contact_force":0.48978,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":213.0,"n_steps_budget":1000.0,"object_pos_end":[0.46286,-7e-05,0.02602],"object_pos_start":[0.46286,-7e-05,0.03],"object_to_goal_dist_end":0.2331,"object_to_goal_dist_start":0.23148,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":848.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.46761,-9e-05,0.18209],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.15615,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":211.0,"n_steps_budget":1000.0,"object_pos_end":[0.46286,-7e-05,0.02602],"object_pos_start":[0.46286,-7e-05,0.02602],"object_to_goal_dist_end":0.2331,"object_to_goal_dist_start":0.2331,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":844.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.46019,-0.00014,0.05248],"tcp_start":[0.46761,-9e-05,0.18209],"tcp_to_object_dist_end":0.02659,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":49.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.46276,-0.00033,0.02588],"object_pos_start":[0.46286,-7e-05,0.02602],"object_to_goal_dist_end":0.23339,"object_to_goal_dist_start":0.2331,"object_z_max":0.02602,"peak_contact_force":0.13031,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12739.0,"raw_peak_contact_force":0.15652,"tcp_end":[0.45138,-0.00028,0.04344],"tcp_start":[0.46019,-0.00014,0.05248],"tcp_to_object_dist_end":0.02092,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":31.0,"n_steps":356.0,"n_steps_budget":810.0,"object_pos_end":[0.47552,-0.00034,0.17741],"object_pos_start":[0.46276,-0.00033,0.02588],"object_to_goal_dist_end":0.21131,"object_to_goal_dist_start":0.23339,"object_z_max":0.17703,"peak_contact_force":0.10276,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":14539.0,"raw_peak_contact_force":0.47244,"subtask_id":"lift_object","tcp_end":[0.45862,-0.00037,0.20005],"tcp_start":[0.45138,-0.00028,0.04344],"tcp_to_object_dist_end":0.02824,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":25.0,"n_steps":464.0,"n_steps_budget":1000.0,"object_pos_end":[0.60578,0.14228,0.20387],"object_pos_start":[0.47552,-0.00034,0.17741],"object_to_goal_dist_end":0.08248,"object_to_goal_dist_start":0.21131,"object_z_max":0.20381,"peak_contact_force":0.09509,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":10912.0,"raw_peak_contact_force":0.24163,"subtask_id":"place_at_goal","tcp_end":[0.59378,0.13846,0.2307],"tcp_start":[0.45862,-0.00037,0.20005],"tcp_to_object_dist_end":0.02964,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":26.0,"n_steps":108.0,"n_steps_budget":1000.0,"object_pos_end":[0.61369,0.15171,0.14003],"object_pos_start":[0.60578,0.14228,0.20387],"object_to_goal_dist_end":0.01823,"object_to_goal_dist_start":0.08248,"object_z_max":0.20387,"peak_contact_force":0.09126,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2777.0,"raw_peak_contact_force":0.48978,"subtask_id":"place_at_goal","tcp_end":[0.60179,0.1473,0.16857],"tcp_start":[0.59378,0.13846,0.2307],"tcp_to_object_dist_end":0.03123,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```