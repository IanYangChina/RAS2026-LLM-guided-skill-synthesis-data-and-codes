## Search State

- **Seed**: 9
- **Iteration**: 13 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 12 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 8 | 0.4563 | 1.00 | ❌ rejected |
| 11 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 8 | 0.4576 | 1.00 | ❌ rejected |
| 10 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 8 | 0.4575 | 1.00 | ❌ rejected |
| 9 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | time_limit | time_limit | grasp_success | time_limit | time_limit | time_limit | 13 | -0.0112 | 0.57 | ❌ rejected |
| 8 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 8 | 0.4577 | 1.00 | ✅ accepted |

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

## Current Skill (Q=0.456) — your mutation base

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

- **Composite score**: 0.456
- **task_score** (E): 1.000
- **fitness_score**: 0.976  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.520

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_object | 1.00 | 1.00 | 0.1432 |
| descend_to_grasp | 1.00 | 1.00 | 0.1232 |
| grasp | 1.00 | 1.00 | 0.0133 |
| lift | 1.00 | 1.00 | 0.1594 |
| transport_to_goal | 1.00 | 1.00 | 0.2244 |
| descend_to_place | 1.00 | 1.00 | 0.0764 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.510, -0.015, 0.163) | (0.515, -0.017, 0.030)→(0.515, -0.017, 0.026) | 0.268→0.270 | 1.00 / 4.000 | 12.415 | 0.138 |
| descend_to_grasp | descend | 1.00 / step_budget | (0.510, -0.015, 0.163)→(0.510, -0.017, 0.040) | (0.515, -0.017, 0.026)→(0.515, -0.017, 0.026) | 0.270→0.270 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp | grasp | 1.00 / step_budget | (0.510, -0.017, 0.040)→(0.501, -0.016, 0.030) | (0.515, -0.017, 0.026)→(0.515, -0.017, 0.026) | 0.270→0.270 | 1.00 / 43.667 | 0.136 | 0.166 |
| lift | lift | 1.00 / step_budget | (0.501, -0.016, 0.030)→(0.510, -0.017, 0.189) | (0.515, -0.017, 0.026)→(0.525, -0.017, 0.181) | 0.270→0.227 | 1.00 / 32.667 | 90.521 | 0.622 |
| transport_to_goal | approach | 1.00 / step_budget | (0.510, -0.017, 0.189)→(0.605, 0.162, 0.271) | (0.525, -0.017, 0.181)→(0.615, 0.166, 0.260) | 0.227→0.093 | 1.00 / 29.333 | 0.106 | 0.163 |
| descend_to_place | descend | 1.00 / step_budget | (0.605, 0.162, 0.271)→(0.611, 0.176, 0.197) | (0.615, 0.166, 0.260)→(0.621, 0.179, 0.182) | 0.093→0.016 | 1.00 / 28.333 | 0.107 | 0.368 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.151
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 1.000
- phase_score: 0.603
- phase_breakdown.place_at_goal_score: 0.596
- phase_breakdown.lift_object_score: 0.904
- phase_breakdown.reach_object_score: 0.167
- grasp_place_fitness: 0.978

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.978
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 1.000
- **Median Q (composite search score)**: 0.456
- **K-run variance**: 0.0000
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.426


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.35772,"average_solve_count":246.0,"average_success_count":246.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_height":0.10163,"approach_object.approach_speed":0.06595,"descend_to_grasp.descend_depth":0.00049,"descend_to_place.place_height_z":0.01692,"descend_to_place.place_speed":0.05171,"lift.lift_height":0.23077,"lift.lift_speed":0.1446,"transport_to_goal.transport_speed":0.05729},"optimized_scores":{"best_composite_score":0.45555,"best_fitness_score":0.97555,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":70.0,"contact_point_centroid":[0.53406,-0.02078,-0.00141],"force_p95":0.60308,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.69938,"mean_force":0.15823,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52072,-0.02073,0.0309]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1236.0,"contact_point_centroid":[0.6126,0.19643,0.27352],"force_p95":0.1791,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.51448,"mean_force":0.10775,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.60311,0.21226,0.2773]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1391.0,"contact_point_centroid":[0.60158,0.23044,0.27729],"force_p95":0.156,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.4759,"mean_force":0.09568,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.60301,0.21194,0.2788]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6397.0,"contact_point_centroid":[0.52779,-0.03987,0.12232],"force_p95":0.11105,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.35085,"mean_force":0.07803,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52472,-0.02084,0.11964]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":7708.0,"contact_point_centroid":[0.52806,-0.00223,0.11833],"force_p95":0.1048,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.34711,"mean_force":0.0675,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52451,-0.02083,0.11659]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6257.0,"contact_point_centroid":[0.56776,0.10896,0.27014],"force_p95":0.11173,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21049,"mean_force":0.0779,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.56569,0.09008,0.26854]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6014.0,"contact_point_centroid":[0.57333,0.07404,0.27026],"force_p95":0.11955,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20298,"mean_force":0.08194,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.56623,0.09183,0.26917]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53703,-0.02132,-0.00204],"force_p95":0.13724,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.16717,"mean_force":0.12641,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.52325,-0.02077,0.03112]},{"body_a":"world","body_b":"grasp_target","contact_count":1608.0,"contact_point_centroid":[0.53702,-0.02132,-0.00191],"force_p95":0.13462,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12293,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.51325,-0.0092,0.22252]},{"body_a":"world","body_b":"grasp_target","contact_count":960.0,"contact_point_centroid":[0.53702,-0.02132,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.52895,-0.01988,0.09213]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5300.0,"contact_point_centroid":[0.52307,-0.00171,0.03205],"force_p95":0.06777,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1048,"mean_force":0.04095,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.52198,-0.02075,0.02969]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4169.0,"contact_point_centroid":[0.52304,-0.04005,0.03236],"force_p95":0.0799,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09233,"mean_force":0.052,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.52198,-0.02075,0.02969]}],"total_contact_groups":12},"final_pose_error":0.0199,"key_states":{"actual_goal_position":[0.61031,0.22775,0.20741],"final_object_position":[0.61571,0.2251,0.22103],"final_tcp_position":[0.60545,0.22014,0.24206],"realised_goal_position":[0.61031,0.22775,0.20741],"realised_object_initial_position":[0.53702,-0.02132,0.03]},"peak_contact_force":0.69938,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":403.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.03],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31446,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1608.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.52919,-0.01896,0.14381],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.11808,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":240.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.12262,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":960.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.53103,-0.02086,0.04015],"tcp_start":[0.52919,-0.01896,0.14381],"tcp_to_object_dist_end":0.01535,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.5369,-0.0211,0.02582],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31669,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.13689,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11269.0,"raw_peak_contact_force":0.16717,"tcp_end":[0.52195,-0.02075,0.02965],"tcp_start":[0.53103,-0.02086,0.04015],"tcp_to_object_dist_end":0.01544,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":486.0,"n_steps_budget":990.0,"object_pos_end":[0.54956,-0.0216,0.22067],"object_pos_start":[0.5369,-0.0211,0.02582],"object_to_goal_dist_end":0.25699,"object_to_goal_dist_start":0.31669,"object_z_max":0.22031,"peak_contact_force":0.10489,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":14175.0,"raw_peak_contact_force":0.69938,"subtask_id":"lift_object","tcp_end":[0.53289,-0.02101,0.23226],"tcp_start":[0.52195,-0.02075,0.02965],"tcp_to_object_dist_end":0.02031,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":20.0,"n_steps":489.0,"n_steps_budget":1000.0,"object_pos_end":[0.61602,0.20998,0.29427],"object_pos_start":[0.54956,-0.0216,0.22067],"object_to_goal_dist_end":0.08884,"object_to_goal_dist_start":0.25699,"object_z_max":0.29414,"peak_contact_force":0.14831,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":12271.0,"raw_peak_contact_force":0.21049,"subtask_id":"place_at_goal","tcp_end":[0.60168,0.20472,0.31065],"tcp_start":[0.53289,-0.02101,0.23226],"tcp_to_object_dist_end":0.0224,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":20.0,"n_steps":135.0,"n_steps_budget":1000.0,"object_pos_end":[0.61571,0.2251,0.22103],"object_pos_start":[0.61602,0.20998,0.29427],"object_to_goal_dist_end":0.01489,"object_to_goal_dist_start":0.08884,"object_z_max":0.29431,"peak_contact_force":0.13242,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2627.0,"raw_peak_contact_force":0.51448,"subtask_id":"place_at_goal","tcp_end":[0.60545,0.22014,0.24206],"tcp_start":[0.60168,0.20472,0.31065],"tcp_to_object_dist_end":0.02392,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.17986,"average_solve_count":278.0,"average_success_count":278.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_height":0.14293,"approach_object.approach_speed":0.02418,"descend_to_grasp.descend_depth":0.00012,"descend_to_place.place_height_z":0.00699,"descend_to_place.place_speed":0.04708,"lift.lift_height":0.15247,"lift.lift_speed":0.13002,"transport_to_goal.transport_speed":0.08451},"optimized_scores":{"best_composite_score":0.45554,"best_fitness_score":0.97554,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":69.0,"contact_point_centroid":[0.5424,-0.02847,-0.00145],"force_p95":0.62503,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.70958,"mean_force":0.17384,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52941,-0.02838,0.02996]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5065.0,"contact_point_centroid":[0.53504,-0.04772,0.09209],"force_p95":0.10952,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.41558,"mean_force":0.06713,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.53344,-0.02852,0.08892]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1935.0,"contact_point_centroid":[0.62461,0.17169,0.24464],"force_p95":0.10896,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.36256,"mean_force":0.07583,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.6241,0.15273,0.24161]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1608.0,"contact_point_centroid":[0.63262,0.13541,0.2428],"force_p95":0.12181,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.35751,"mean_force":0.08853,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.62416,0.15283,0.24104]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6478.0,"contact_point_centroid":[0.53528,-0.00985,0.09047],"force_p95":0.0882,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.34259,"mean_force":0.0541,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.53343,-0.02852,0.08884]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.54565,-0.02924,-0.00207],"force_p95":0.14329,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.18711,"mean_force":0.12812,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.5318,-0.02844,0.03025]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5728.0,"contact_point_centroid":[0.58833,0.04629,0.21815],"force_p95":0.11218,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15636,"mean_force":0.08123,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.58255,0.06461,0.21646]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6880.0,"contact_point_centroid":[0.57933,0.07292,0.21101],"force_p95":0.1047,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13939,"mean_force":0.06965,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.5776,0.05416,0.2091]},{"body_a":"world","body_b":"grasp_target","contact_count":1380.0,"contact_point_centroid":[0.5456,-0.02923,-0.0019],"force_p95":0.1356,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12298,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.51635,-0.01208,0.24273]},{"body_a":"world","body_b":"grasp_target","contact_count":1320.0,"contact_point_centroid":[0.5456,-0.02923,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.53666,-0.02689,0.11161]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5284.0,"contact_point_centroid":[0.53174,-0.00949,0.03109],"force_p95":0.06966,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1216,"mean_force":0.04081,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.53052,-0.0284,0.02877]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4252.0,"contact_point_centroid":[0.5314,-0.04773,0.03139],"force_p95":0.09216,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09427,"mean_force":0.05377,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.53053,-0.0284,0.02878]}],"total_contact_groups":12},"final_pose_error":0.01948,"key_states":{"actual_goal_position":[0.63284,0.16493,0.17692],"final_object_position":[0.64306,0.16349,0.18778],"final_tcp_position":[0.62708,0.15923,0.20162],"realised_goal_position":[0.63284,0.16493,0.17692],"realised_object_initial_position":[0.5456,-0.02923,0.03]},"peak_contact_force":271.38654,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":346.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.03],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.25864,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1380.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.53608,-0.02526,0.18365],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.15797,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":330.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1320.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.53966,-0.02862,0.03952],"tcp_start":[0.53608,-0.02526,0.18365],"tcp_to_object_dist_end":0.01476,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54564,-0.02889,0.02574],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26082,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.14294,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11336.0,"raw_peak_contact_force":0.18711,"tcp_end":[0.53049,-0.0284,0.02874],"tcp_start":[0.53966,-0.02862,0.03952],"tcp_to_object_dist_end":0.01544,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":33.0,"n_steps":316.0,"n_steps_budget":750.0,"object_pos_end":[0.55631,-0.02944,0.14709],"object_pos_start":[0.54564,-0.02889,0.02574],"object_to_goal_dist_end":0.21101,"object_to_goal_dist_start":0.26082,"object_z_max":0.14673,"peak_contact_force":271.38654,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":11612.0,"raw_peak_contact_force":0.70958,"subtask_id":"lift_object","tcp_end":[0.54016,-0.02872,0.1539],"tcp_start":[0.53049,-0.0284,0.02874],"tcp_to_object_dist_end":0.01754,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":28.0,"n_steps":462.0,"n_steps_budget":1000.0,"object_pos_end":[0.63878,0.151,0.26553],"object_pos_start":[0.55631,-0.02944,0.14709],"object_to_goal_dist_end":0.08989,"object_to_goal_dist_start":0.21101,"object_z_max":0.26528,"peak_contact_force":0.09859,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":12608.0,"raw_peak_contact_force":0.15636,"subtask_id":"place_at_goal","tcp_end":[0.62238,0.14703,0.27575],"tcp_start":[0.54016,-0.02872,0.1539],"tcp_to_object_dist_end":0.01973,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":25.0,"n_steps":144.0,"n_steps_budget":1000.0,"object_pos_end":[0.64306,0.16349,0.18778],"object_pos_start":[0.63878,0.151,0.26553],"object_to_goal_dist_end":0.01498,"object_to_goal_dist_start":0.08989,"object_z_max":0.26572,"peak_contact_force":0.1165,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3543.0,"raw_peak_contact_force":0.36256,"subtask_id":"place_at_goal","tcp_end":[0.62708,0.15923,0.20162],"tcp_start":[0.62238,0.14703,0.27575],"tcp_to_object_dist_end":0.02157,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.47391,"average_solve_count":230.0,"average_success_count":230.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_height":0.1173,"approach_object.approach_speed":0.07852,"descend_to_grasp.descend_depth":0.00021,"descend_to_place.place_height_z":0.0067,"descend_to_place.place_speed":0.06487,"lift.lift_height":0.18023,"lift.lift_speed":0.03993,"transport_to_goal.transport_speed":0.1253},"optimized_scores":{"best_composite_score":0.45768,"best_fitness_score":0.97768,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":75.0,"contact_point_centroid":[0.46008,-0.00052,-0.00148],"force_p95":0.44133,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.45738,"mean_force":0.21732,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.44952,-0.00031,0.03318]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3220.0,"contact_point_centroid":[0.59171,0.15982,0.19162],"force_p95":0.0695,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22675,"mean_force":0.04982,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.59561,0.14124,0.18867]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8478.0,"contact_point_centroid":[0.45247,-0.01955,0.10706],"force_p95":0.06941,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22416,"mean_force":0.04789,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.45248,-0.00034,0.1054]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8486.0,"contact_point_centroid":[0.45243,0.01887,0.107],"force_p95":0.06976,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22392,"mean_force":0.04793,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.45248,-0.00034,0.10536]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3220.0,"contact_point_centroid":[0.59943,0.12239,0.18951],"force_p95":0.07106,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16616,"mean_force":0.05006,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.59561,0.14124,0.18867]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.46284,-0.00014,-0.00202],"force_p95":0.12981,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.14398,"mean_force":0.12469,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.45151,-0.00027,0.03358]},{"body_a":"world","body_b":"grasp_target","contact_count":1308.0,"contact_point_centroid":[0.46286,-7e-05,-0.0019],"force_p95":0.13564,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.123,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.48193,-6e-05,0.23221]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":7280.0,"contact_point_centroid":[0.52617,0.04838,0.20494],"force_p95":0.07422,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12342,"mean_force":0.05063,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.52395,0.06743,0.20344]},{"body_a":"world","body_b":"grasp_target","contact_count":1164.0,"contact_point_centroid":[0.46286,-7e-05,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.4604,-0.00014,0.10146]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":7359.0,"contact_point_centroid":[0.52148,0.08581,0.20551],"force_p95":0.07112,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11083,"mean_force":0.04927,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.52339,0.06686,0.20325]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4850.0,"contact_point_centroid":[0.45127,-0.0195,0.03451],"force_p95":0.06667,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09,"mean_force":0.04484,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.45035,-0.00029,0.03247]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5125.0,"contact_point_centroid":[0.45097,0.01892,0.03418],"force_p95":0.06497,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08311,"mean_force":0.04292,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.45035,-0.00029,0.03247]}],"total_contact_groups":12},"final_pose_error":0.01981,"key_states":{"actual_goal_position":[0.61015,0.15287,0.12219],"final_object_position":[0.60405,0.14866,0.13747],"final_tcp_position":[0.60193,0.14769,0.14615],"realised_goal_position":[0.61015,0.15287,0.12219],"realised_object_initial_position":[0.46286,-7e-05,0.03]},"peak_contact_force":37.00086,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":328.0,"n_steps_budget":1000.0,"object_pos_end":[0.46286,-7e-05,0.02602],"object_pos_start":[0.46286,-7e-05,0.03],"object_to_goal_dist_end":0.2331,"object_to_goal_dist_start":0.23148,"object_z_max":0.03,"peak_contact_force":37.00086,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1308.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.46418,-0.00011,0.16203],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.13602,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":291.0,"n_steps_budget":1000.0,"object_pos_end":[0.46286,-7e-05,0.02602],"object_pos_start":[0.46286,-7e-05,0.02602],"object_to_goal_dist_end":0.2331,"object_to_goal_dist_start":0.2331,"object_z_max":0.02602,"peak_contact_force":0.12262,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1164.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.45872,-0.00015,0.04062],"tcp_start":[0.46418,-0.00011,0.16203],"tcp_to_object_dist_end":0.01517,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":45.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.46273,-0.00029,0.0259],"object_pos_start":[0.46286,-7e-05,0.02602],"object_to_goal_dist_end":0.23337,"object_to_goal_dist_start":0.2331,"object_z_max":0.02602,"peak_contact_force":0.12919,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11775.0,"raw_peak_contact_force":0.14398,"tcp_end":[0.45032,-0.00029,0.03244],"tcp_start":[0.45872,-0.00015,0.04062],"tcp_to_object_dist_end":0.01403,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":42.0,"n_steps":386.0,"n_steps_budget":1000.0,"object_pos_end":[0.46996,-0.00031,0.17499],"object_pos_start":[0.46273,-0.00029,0.0259],"object_to_goal_dist_end":0.21425,"object_to_goal_dist_start":0.23337,"object_z_max":0.17461,"peak_contact_force":0.07147,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":17039.0,"raw_peak_contact_force":0.45738,"subtask_id":"lift_object","tcp_end":[0.45816,-0.00033,0.1819],"tcp_start":[0.45032,-0.00029,0.03244],"tcp_to_object_dist_end":0.01367,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":362.0,"n_steps_budget":1000.0,"object_pos_end":[0.59123,0.13567,0.22005],"object_pos_start":[0.46996,-0.00031,0.17499],"object_to_goal_dist_end":0.10115,"object_to_goal_dist_start":0.21425,"object_z_max":0.21994,"peak_contact_force":0.07012,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":14639.0,"raw_peak_contact_force":0.12342,"subtask_id":"place_at_goal","tcp_end":[0.59101,0.13535,0.22796],"tcp_start":[0.45816,-0.00033,0.1819],"tcp_to_object_dist_end":0.00792,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":161.0,"n_steps_budget":1000.0,"object_pos_end":[0.60405,0.14866,0.13747],"object_pos_start":[0.59123,0.13567,0.22005],"object_to_goal_dist_end":0.01698,"object_to_goal_dist_start":0.10115,"object_z_max":0.22008,"peak_contact_force":0.07125,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":6440.0,"raw_peak_contact_force":0.22675,"subtask_id":"place_at_goal","tcp_end":[0.60193,0.14769,0.14615],"tcp_start":[0.59101,0.13535,0.22796],"tcp_to_object_dist_end":0.00899,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```