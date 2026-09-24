## Search State

- **Seed**: 9
- **Iteration**: 15 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 14 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 8 | 0.4577 | 1.00 | ❌ rejected |
| 13 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 8 | 0.4478 | 1.00 | ❌ rejected |
| 12 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 8 | 0.4563 | 1.00 | ❌ rejected |
| 11 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 8 | 0.4576 | 1.00 | ❌ rejected |
| 10 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 8 | 0.4575 | 1.00 | ❌ rejected |

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

## Current Skill (Q=0.458) — your mutation base

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

- **Composite score**: 0.458
- **task_score** (E): 1.000
- **fitness_score**: 0.978  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.520

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_object | 1.00 | 1.00 | 0.1437 |
| descend_to_grasp | 1.00 | 1.00 | 0.1276 |
| grasp | 1.00 | 1.00 | 0.0130 |
| lift | 0.67 | 1.00 | 0.1823 |
| transport_to_goal | 0.67 | 1.00 | 0.2080 |
| descend_to_place | 1.00 | 1.00 | 0.0829 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.510, -0.015, 0.163) | (0.515, -0.017, 0.030)→(0.515, -0.017, 0.026) | 0.268→0.270 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_to_grasp | descend | 1.00 / step_budget | (0.510, -0.015, 0.163)→(0.510, -0.017, 0.035) | (0.515, -0.017, 0.026)→(0.515, -0.017, 0.026) | 0.270→0.270 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp | grasp | 1.00 / step_budget | (0.510, -0.017, 0.035)→(0.501, -0.017, 0.026) | (0.515, -0.017, 0.026)→(0.515, -0.017, 0.026) | 0.270→0.270 | 1.00 / 43.667 | 0.134 | 0.155 |
| lift | lift | 0.67 / step_budget | (0.501, -0.017, 0.026)→(0.509, -0.017, 0.208) | (0.515, -0.017, 0.026)→(0.521, -0.017, 0.200) | 0.270→0.233 | 1.00 / 37.000 | 0.081 | 0.669 |
| transport_to_goal | approach | 0.67 / step_budget | (0.509, -0.017, 0.208)→(0.603, 0.151, 0.267) | (0.521, -0.017, 0.200)→(0.612, 0.154, 0.252) | 0.233→0.093 | 1.00 / 38.667 | 0.079 | 0.112 |
| descend_to_place | descend | 1.00 / step_budget | (0.603, 0.151, 0.267)→(0.612, 0.175, 0.193) | (0.612, 0.154, 0.252)→(0.620, 0.178, 0.176) | 0.093→0.009 | 1.00 / 32.667 | 0.084 | 0.194 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.623
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 1.000
- phase_score: 0.472
- phase_breakdown.place_at_goal_score: 0.646
- phase_breakdown.lift_object_score: 0.398
- phase_breakdown.reach_object_score: 0.148
- grasp_place_fitness: 0.979

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.979
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 1.000
- **Median Q (composite search score)**: 0.457
- **K-run variance**: 0.0000
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Parameters at lower bound**: descend_to_grasp.descend_depth
- **Final σ (mean)**: 0.417


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.56828,"average_solve_count":227.0,"average_success_count":227.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_height":0.13801,"approach_object.approach_speed":0.08859,"descend_to_grasp.descend_depth":0.0018,"descend_to_place.place_height_z":0.02514,"descend_to_place.place_speed":0.03833,"lift.lift_height":0.1949,"lift.lift_speed":0.08725,"transport_to_goal.transport_speed":0.06596},"optimized_scores":{"best_composite_score":0.45696,"best_fitness_score":0.97696,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":102.0,"contact_point_centroid":[0.53358,-0.02103,-0.00122],"force_p95":0.61141,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.73617,"mean_force":0.13455,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52134,-0.02092,0.02706]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":16414.0,"contact_point_centroid":[0.52586,-0.04019,0.1178],"force_p95":0.08129,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33136,"mean_force":0.05878,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52534,-0.02101,0.11502]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":19612.0,"contact_point_centroid":[0.5267,-0.00203,0.1157],"force_p95":0.07671,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32628,"mean_force":0.05079,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52527,-0.021,0.11398]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3193.0,"contact_point_centroid":[0.59114,0.20398,0.26105],"force_p95":0.0947,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18704,"mean_force":0.07062,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.59379,0.18497,0.25998]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4052.0,"contact_point_centroid":[0.60033,0.16765,0.25787],"force_p95":0.08344,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1529,"mean_force":0.05877,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.59385,0.18524,0.25967]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53701,-0.02134,-0.00203],"force_p95":0.13406,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.1526,"mean_force":0.12542,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.5237,-0.02095,0.02709]},{"body_a":"world","body_b":"grasp_target","contact_count":1736.0,"contact_point_centroid":[0.53702,-0.02132,-0.00192],"force_p95":0.13411,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12291,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.51362,-0.00941,0.23687]},{"body_a":"world","body_b":"grasp_target","contact_count":1688.0,"contact_point_centroid":[0.53702,-0.02132,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.52921,-0.02012,0.10452]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":16908.0,"contact_point_centroid":[0.55759,0.08802,0.24506],"force_p95":0.08536,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10468,"mean_force":0.0582,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.55816,0.06906,0.24385]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":17785.0,"contact_point_centroid":[0.56388,0.05718,0.2476],"force_p95":0.08679,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10168,"mean_force":0.05659,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.56026,0.0758,0.24702]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5312.0,"contact_point_centroid":[0.52339,-0.00189,0.02786],"force_p95":0.06881,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09827,"mean_force":0.04094,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.52241,-0.02093,0.02564]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4156.0,"contact_point_centroid":[0.52333,-0.04022,0.02835],"force_p95":0.08037,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0977,"mean_force":0.05198,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.52241,-0.02093,0.02564]}],"total_contact_groups":12},"final_pose_error":0.01476,"key_states":{"actual_goal_position":[0.61031,0.22775,0.20741],"final_object_position":[0.61211,0.21909,0.21669],"final_tcp_position":[0.60332,0.21481,0.23374],"realised_goal_position":[0.61031,0.22775,0.20741],"realised_object_initial_position":[0.53702,-0.02132,0.03]},"peak_contact_force":0.73617,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":435.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.03],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31446,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1736.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.52984,-0.01925,0.17438],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.14855,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":422.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1688.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.53134,-0.02105,0.03583],"tcp_start":[0.52984,-0.01925,0.17438],"tcp_to_object_dist_end":0.01134,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53688,-0.02123,0.02587],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31677,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.13406,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11268.0,"raw_peak_contact_force":0.1526,"tcp_end":[0.52238,-0.02093,0.0256],"tcp_start":[0.53134,-0.02105,0.03583],"tcp_to_object_dist_end":0.0145,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":958.0,"n_steps_budget":1000.0,"object_pos_end":[0.54497,-0.02175,0.19845],"object_pos_start":[0.53688,-0.02123,0.02587],"object_to_goal_dist_end":0.25807,"object_to_goal_dist_start":0.31677,"object_z_max":0.1983,"peak_contact_force":0.08074,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":36128.0,"raw_peak_contact_force":0.73617,"subtask_id":"lift_object","tcp_end":[0.53281,-0.02115,0.20633],"tcp_start":[0.52238,-0.02093,0.0256],"tcp_to_object_dist_end":0.0145,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":32.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.59628,0.16261,0.27168],"object_pos_start":[0.54497,-0.02175,0.19845],"object_to_goal_dist_end":0.09259,"object_to_goal_dist_start":0.25807,"object_z_max":0.27162,"peak_contact_force":0.0936,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":34693.0,"raw_peak_contact_force":0.10468,"subtask_id":"place_at_goal","tcp_end":[0.58667,0.15929,0.28671],"tcp_start":[0.53281,-0.02115,0.20633],"tcp_to_object_dist_end":0.01814,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":28.0,"n_steps":235.0,"n_steps_budget":1000.0,"object_pos_end":[0.61211,0.21909,0.21669],"object_pos_start":[0.59628,0.16261,0.27168],"object_to_goal_dist_end":0.01282,"object_to_goal_dist_start":0.09259,"object_z_max":0.27168,"peak_contact_force":0.09233,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":7245.0,"raw_peak_contact_force":0.18704,"subtask_id":"place_at_goal","tcp_end":[0.60332,0.21481,0.23374],"tcp_start":[0.58667,0.15929,0.28671],"tcp_to_object_dist_end":0.01965,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.67801,"average_solve_count":382.0,"average_success_count":382.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_height":0.13838,"approach_object.approach_speed":0.02057,"descend_to_grasp.descend_depth":0.00172,"descend_to_place.place_height_z":0.01176,"descend_to_place.place_speed":0.01421,"lift.lift_height":0.29963,"lift.lift_speed":0.02019,"transport_to_goal.transport_speed":0.12954},"optimized_scores":{"best_composite_score":0.45666,"best_fitness_score":0.97666,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":115.0,"contact_point_centroid":[0.54147,-0.02837,-0.00128],"force_p95":0.55239,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.60022,"mean_force":0.14243,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52955,-0.02858,0.02661]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":17000.0,"contact_point_centroid":[0.53135,-0.04777,0.11085],"force_p95":0.08181,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26896,"mean_force":0.05903,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.53088,-0.02859,0.10802]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":20399.0,"contact_point_centroid":[0.5325,-0.00964,0.10835],"force_p95":0.07824,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26298,"mean_force":0.05091,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.53082,-0.02859,0.10672]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3771.0,"contact_point_centroid":[0.62085,0.17234,0.2455],"force_p95":0.0709,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20592,"mean_force":0.05028,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.62383,0.15354,0.24365]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3712.0,"contact_point_centroid":[0.62928,0.13523,0.24303],"force_p95":0.07263,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18347,"mean_force":0.05173,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.62386,0.15361,0.24309]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.5456,-0.02922,-0.00205],"force_p95":0.13881,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.16846,"mean_force":0.12666,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.5321,-0.02865,0.02682]},{"body_a":"world","body_b":"grasp_target","contact_count":2076.0,"contact_point_centroid":[0.5456,-0.02923,-0.00193],"force_p95":0.1323,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12286,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.51737,-0.01297,0.23644]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":19051.0,"contact_point_centroid":[0.57915,0.08405,0.23699],"force_p95":0.07728,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13612,"mean_force":0.05286,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.57998,0.06518,0.23603]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":17509.0,"contact_point_centroid":[0.58459,0.04943,0.23831],"force_p95":0.08983,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1344,"mean_force":0.05771,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.58155,0.06828,0.23766]},{"body_a":"world","body_b":"grasp_target","contact_count":1672.0,"contact_point_centroid":[0.5456,-0.02923,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.5374,-0.02763,0.10422]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5291.0,"contact_point_centroid":[0.53196,-0.00958,0.02755],"force_p95":0.07047,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10879,"mean_force":0.04103,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.53081,-0.02862,0.02533]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4173.0,"contact_point_centroid":[0.53162,-0.04792,0.02812],"force_p95":0.0818,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09297,"mean_force":0.05198,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.53081,-0.02862,0.02533]}],"total_contact_groups":12},"final_pose_error":0.01474,"key_states":{"actual_goal_position":[0.63284,0.16493,0.17692],"final_object_position":[0.63332,0.1627,0.18402],"final_tcp_position":[0.62724,0.16027,0.20148],"realised_goal_position":[0.63284,0.16493,0.17692],"realised_object_initial_position":[0.5456,-0.02923,0.03]},"peak_contact_force":0.60022,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":520.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.03],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.25864,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2076.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.53778,-0.02652,0.17387],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.14808,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":418.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1672.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.53981,-0.02884,0.03581],"tcp_start":[0.53778,-0.02652,0.17387],"tcp_to_object_dist_end":0.01139,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54546,-0.02896,0.02581],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26088,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.13861,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11264.0,"raw_peak_contact_force":0.16846,"tcp_end":[0.53078,-0.02861,0.02529],"tcp_start":[0.53981,-0.02884,0.03581],"tcp_to_object_dist_end":0.0147,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.54742,-0.02941,0.18355],"object_pos_start":[0.54546,-0.02896,0.02581],"object_to_goal_dist_end":0.21239,"object_to_goal_dist_start":0.26088,"object_z_max":0.18339,"peak_contact_force":0.0805,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":37514.0,"raw_peak_contact_force":0.60022,"subtask_id":"lift_object","tcp_end":[0.53557,-0.02869,0.19191],"tcp_start":[0.53078,-0.02861,0.02529],"tcp_to_object_dist_end":0.01452,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":42.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.62878,0.1505,0.26403],"object_pos_start":[0.54742,-0.02941,0.18355],"object_to_goal_dist_end":0.08839,"object_to_goal_dist_start":0.21239,"object_z_max":0.26394,"peak_contact_force":0.07393,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":36560.0,"raw_peak_contact_force":0.13612,"subtask_id":"place_at_goal","tcp_end":[0.62236,0.14843,0.27997],"tcp_start":[0.53557,-0.02869,0.19191],"tcp_to_object_dist_end":0.0173,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":38.0,"n_steps":195.0,"n_steps_budget":1000.0,"object_pos_end":[0.63332,0.1627,0.18402],"object_pos_start":[0.62878,0.1505,0.26403],"object_to_goal_dist_end":0.00746,"object_to_goal_dist_start":0.08839,"object_z_max":0.26403,"peak_contact_force":0.07053,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":7483.0,"raw_peak_contact_force":0.20592,"subtask_id":"place_at_goal","tcp_end":[0.62724,0.16027,0.20148],"tcp_start":[0.62236,0.14843,0.27997],"tcp_to_object_dist_end":0.01865,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.50719,"average_solve_count":278.0,"average_success_count":278.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_height":0.10095,"approach_object.approach_speed":0.07139,"descend_to_grasp.descend_depth":0.0,"descend_to_place.place_height_z":0.00771,"descend_to_place.place_speed":0.07372,"lift.lift_height":0.21436,"lift.lift_speed":0.08187,"transport_to_goal.transport_speed":0.03657},"optimized_scores":{"best_composite_score":0.4594,"best_fitness_score":0.9794,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":87.0,"contact_point_centroid":[0.45988,-0.00051,-0.00127],"force_p95":0.54921,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.67018,"mean_force":0.1347,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.44893,-0.00031,0.02817]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":18523.0,"contact_point_centroid":[0.45305,-0.01949,0.12784],"force_p95":0.073,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2954,"mean_force":0.05065,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.45235,-0.00035,0.12562]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":18652.0,"contact_point_centroid":[0.45286,0.0188,0.12572],"force_p95":0.07338,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29374,"mean_force":0.0504,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.45222,-0.00035,0.12362]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3555.0,"contact_point_centroid":[0.59849,0.16636,0.19464],"force_p95":0.08656,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18764,"mean_force":0.05709,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.60145,0.14757,0.19264]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3913.0,"contact_point_centroid":[0.60618,0.12925,0.18974],"force_p95":0.07794,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16589,"mean_force":0.05329,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.60154,0.14767,0.19062]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.46284,-0.00015,-0.00202],"force_p95":0.1296,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.14466,"mean_force":0.12463,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.45107,-0.00027,0.02797]},{"body_a":"world","body_b":"grasp_target","contact_count":1956.0,"contact_point_centroid":[0.46286,-7e-05,-0.00193],"force_p95":0.13308,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12288,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.48061,-6e-05,0.22089]},{"body_a":"world","body_b":"grasp_target","contact_count":1360.0,"contact_point_centroid":[0.46286,-7e-05,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.45891,-0.00015,0.08729]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":18880.0,"contact_point_centroid":[0.53599,0.05836,0.22914],"force_p95":0.07611,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0957,"mean_force":0.05159,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.53302,0.07724,0.22801]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":18309.0,"contact_point_centroid":[0.53133,0.09615,0.23029],"force_p95":0.07707,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09006,"mean_force":0.0523,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.53297,0.07719,0.22799]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4850.0,"contact_point_centroid":[0.45091,-0.0195,0.02891],"force_p95":0.06674,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08751,"mean_force":0.04481,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.44988,-0.00029,0.02685]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5125.0,"contact_point_centroid":[0.4506,0.01892,0.02858],"force_p95":0.06493,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08394,"mean_force":0.04295,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.44988,-0.00029,0.02685]}],"total_contact_groups":12},"final_pose_error":0.01465,"key_states":{"actual_goal_position":[0.61015,0.15287,0.12219],"final_object_position":[0.61402,0.15366,0.12861],"final_tcp_position":[0.60439,0.15044,0.14314],"realised_goal_position":[0.61015,0.15287,0.12219],"realised_object_initial_position":[0.46286,-7e-05,0.03]},"peak_contact_force":0.67018,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":490.0,"n_steps_budget":1000.0,"object_pos_end":[0.46286,-7e-05,0.02602],"object_pos_start":[0.46286,-7e-05,0.03],"object_to_goal_dist_end":0.2331,"object_to_goal_dist_start":0.23148,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1956.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.46225,-0.00011,0.14075],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.11473,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":340.0,"n_steps_budget":1000.0,"object_pos_end":[0.46286,-7e-05,0.02602],"object_pos_start":[0.46286,-7e-05,0.02602],"object_to_goal_dist_end":0.2331,"object_to_goal_dist_start":0.2331,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1360.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.45814,-0.00015,0.03474],"tcp_start":[0.46225,-0.00011,0.14075],"tcp_to_object_dist_end":0.00991,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":45.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.46271,-0.0003,0.02591],"object_pos_start":[0.46286,-7e-05,0.02602],"object_to_goal_dist_end":0.23338,"object_to_goal_dist_start":0.2331,"object_z_max":0.02602,"peak_contact_force":0.12897,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11775.0,"raw_peak_contact_force":0.14466,"tcp_end":[0.44985,-0.00029,0.02682],"tcp_start":[0.45814,-0.00015,0.03474],"tcp_to_object_dist_end":0.0129,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":919.0,"n_steps_budget":1000.0,"object_pos_end":[0.47077,-0.00032,0.21905],"object_pos_start":[0.46271,-0.0003,0.02591],"object_to_goal_dist_end":0.22864,"object_to_goal_dist_start":0.23338,"object_z_max":0.21887,"peak_contact_force":0.08034,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":37262.0,"raw_peak_contact_force":0.67018,"subtask_id":"lift_object","tcp_end":[0.45904,-0.00033,0.22586],"tcp_start":[0.44985,-0.00029,0.02682],"tcp_to_object_dist_end":0.01356,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":42.0,"n_steps":960.0,"n_steps_budget":1000.0,"object_pos_end":[0.61051,0.14835,0.22157],"object_pos_start":[0.47077,-0.00032,0.21905],"object_to_goal_dist_end":0.09948,"object_to_goal_dist_start":0.22864,"object_z_max":0.22156,"peak_contact_force":0.06998,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":37189.0,"raw_peak_contact_force":0.0957,"subtask_id":"place_at_goal","tcp_end":[0.60051,0.14552,0.23356],"tcp_start":[0.45904,-0.00033,0.22586],"tcp_to_object_dist_end":0.01587,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":32.0,"n_steps":201.0,"n_steps_budget":1000.0,"object_pos_end":[0.61402,0.15366,0.12861],"object_pos_start":[0.61051,0.14835,0.22157],"object_to_goal_dist_end":0.00753,"object_to_goal_dist_start":0.09948,"object_z_max":0.22157,"peak_contact_force":0.08902,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":7468.0,"raw_peak_contact_force":0.18764,"subtask_id":"place_at_goal","tcp_end":[0.60439,0.15044,0.14314],"tcp_start":[0.60051,0.14552,0.23356],"tcp_to_object_dist_end":0.01773,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```