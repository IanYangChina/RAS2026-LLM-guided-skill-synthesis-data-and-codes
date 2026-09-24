## Search State

- **Seed**: 9
- **Iteration**: 11 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 10 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 8 | 0.4575 | 1.00 | ❌ rejected |
| 9 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | time_limit | time_limit | grasp_success | time_limit | time_limit | time_limit | 13 | -0.0112 | 0.57 | ❌ rejected |
| 8 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 8 | 0.4577 | 1.00 | ✅ accepted |
| 7 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 8 | 0.4577 | 1.00 | ✅ accepted |
| 6 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 9 | 0.4026 | 1.00 | ❌ rejected |

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
| approach_object | 1.00 | 1.00 | 0.1503 |
| descend_to_grasp | 1.00 | 1.00 | 0.1198 |
| grasp | 1.00 | 1.00 | 0.0130 |
| lift | 1.00 | 1.00 | 0.1640 |
| transport_to_goal | 0.33 | 1.00 | 0.2063 |
| descend_to_place | 1.00 | 1.00 | 0.0746 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.510, -0.015, 0.156) | (0.515, -0.017, 0.030)→(0.515, -0.017, 0.026) | 0.268→0.270 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_to_grasp | descend | 1.00 / step_budget | (0.510, -0.015, 0.156)→(0.510, -0.017, 0.036) | (0.515, -0.017, 0.026)→(0.515, -0.017, 0.026) | 0.270→0.270 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp | grasp | 1.00 / step_budget | (0.510, -0.017, 0.036)→(0.501, -0.017, 0.027) | (0.515, -0.017, 0.026)→(0.515, -0.017, 0.026) | 0.270→0.270 | 1.00 / 43.667 | 0.134 | 0.155 |
| lift | lift | 1.00 / step_budget | (0.501, -0.017, 0.027)→(0.511, -0.017, 0.190) | (0.515, -0.017, 0.026)→(0.523, -0.017, 0.182) | 0.270→0.236 | 1.00 / 37.000 | 0.081 | 0.665 |
| transport_to_goal | approach | 0.33 / step_budget | (0.511, -0.017, 0.190)→(0.599, 0.143, 0.258) | (0.523, -0.017, 0.182)→(0.604, 0.145, 0.242) | 0.236→0.087 | 1.00 / 38.667 | 0.074 | 0.125 |
| descend_to_place | descend | 1.00 / step_budget | (0.599, 0.143, 0.258)→(0.611, 0.173, 0.195) | (0.604, 0.145, 0.242)→(0.615, 0.176, 0.178) | 0.087→0.013 | 1.00 / 34.333 | 0.056 | 0.190 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.346
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 1.000
- phase_score: 0.425
- phase_breakdown.place_at_goal_score: 0.622
- phase_breakdown.lift_object_score: 0.281
- phase_breakdown.reach_object_score: 0.149
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
- **Final σ (mean)**: 0.344


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.48815,"average_solve_count":211.0,"average_success_count":211.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_height":0.13529,"approach_object.approach_speed":0.0557,"descend_to_grasp.descend_depth":0.0022,"descend_to_place.place_height_z":0.02601,"descend_to_place.place_speed":0.04215,"lift.lift_height":0.16793,"lift.lift_speed":0.07517,"transport_to_goal.transport_speed":0.11929},"optimized_scores":{"best_composite_score":0.45694,"best_fitness_score":0.97694,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":101.0,"contact_point_centroid":[0.53304,-0.02083,-0.00122],"force_p95":0.56779,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.68574,"mean_force":0.12609,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52135,-0.02091,0.02767]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":14122.0,"contact_point_centroid":[0.52582,-0.04019,0.10514],"force_p95":0.08152,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31376,"mean_force":0.05914,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52527,-0.021,0.10238]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":16981.0,"contact_point_centroid":[0.52659,-0.00203,0.10287],"force_p95":0.07716,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.3088,"mean_force":0.05083,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52516,-0.021,0.10114]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53702,-0.02135,-0.00203],"force_p95":0.13426,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.15336,"mean_force":0.1255,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.52369,-0.02094,0.02767]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3159.0,"contact_point_centroid":[0.59119,0.20557,0.26076],"force_p95":0.09345,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15115,"mean_force":0.06535,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.5943,0.18667,0.2589]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3923.0,"contact_point_centroid":[0.60144,0.17022,0.25667],"force_p95":0.08192,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14212,"mean_force":0.05552,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.59464,0.18787,0.2577]},{"body_a":"world","body_b":"grasp_target","contact_count":1908.0,"contact_point_centroid":[0.53702,-0.02132,-0.00193],"force_p95":0.13338,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12288,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.5135,-0.00942,0.23551]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":17269.0,"contact_point_centroid":[0.55777,0.08989,0.22929],"force_p95":0.08423,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1256,"mean_force":0.05739,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.5584,0.07097,0.22793]},{"body_a":"world","body_b":"grasp_target","contact_count":1644.0,"contact_point_centroid":[0.53702,-0.02132,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.52919,-0.02013,0.10342]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":17415.0,"contact_point_centroid":[0.56432,0.05937,0.23283],"force_p95":0.08859,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12169,"mean_force":0.05787,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.56061,0.07799,0.232]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5314.0,"contact_point_centroid":[0.52338,-0.00188,0.02846],"force_p95":0.06877,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09865,"mean_force":0.04093,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.5224,-0.02092,0.02623]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4157.0,"contact_point_centroid":[0.52332,-0.04022,0.02894],"force_p95":0.08031,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09725,"mean_force":0.05197,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.52241,-0.02092,0.02623]}],"total_contact_groups":12},"final_pose_error":0.01495,"key_states":{"actual_goal_position":[0.61031,0.22775,0.20741],"final_object_position":[0.61261,0.21913,0.21813],"final_tcp_position":[0.60323,0.21463,0.23451],"realised_goal_position":[0.61031,0.22775,0.20741],"realised_object_initial_position":[0.53702,-0.02132,0.03]},"peak_contact_force":0.68574,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":478.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.03],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31446,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1908.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.52981,-0.01927,0.17175],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.14593,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":411.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1644.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.53132,-0.02104,0.03642],"tcp_start":[0.52981,-0.01927,0.17175],"tcp_to_object_dist_end":0.01187,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53688,-0.02123,0.02586],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31677,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.13425,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11271.0,"raw_peak_contact_force":0.15336,"tcp_end":[0.52237,-0.02092,0.02619],"tcp_start":[0.53132,-0.02104,0.03642],"tcp_to_object_dist_end":0.01452,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":828.0,"n_steps_budget":1000.0,"object_pos_end":[0.54484,-0.02171,0.17193],"object_pos_start":[0.53688,-0.02123,0.02586],"object_to_goal_dist_end":0.26035,"object_to_goal_dist_start":0.31677,"object_z_max":0.17178,"peak_contact_force":0.08052,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":31204.0,"raw_peak_contact_force":0.68574,"subtask_id":"lift_object","tcp_end":[0.53245,-0.02114,0.1795],"tcp_start":[0.52237,-0.02092,0.02619],"tcp_to_object_dist_end":0.01452,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":38.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.59814,0.16737,0.26762],"object_pos_start":[0.54484,-0.02171,0.17193],"object_to_goal_dist_end":0.08614,"object_to_goal_dist_start":0.26035,"object_z_max":0.26752,"peak_contact_force":0.07243,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":34684.0,"raw_peak_contact_force":0.1256,"subtask_id":"place_at_goal","tcp_end":[0.58809,0.16414,0.28226],"tcp_start":[0.53245,-0.02114,0.1795],"tcp_to_object_dist_end":0.01805,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":30.0,"n_steps":213.0,"n_steps_budget":1000.0,"object_pos_end":[0.61261,0.21913,0.21813],"object_pos_start":[0.59814,0.16737,0.26762],"object_to_goal_dist_end":0.01394,"object_to_goal_dist_start":0.08614,"object_z_max":0.26763,"peak_contact_force":0.094,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":7082.0,"raw_peak_contact_force":0.15115,"subtask_id":"place_at_goal","tcp_end":[0.60323,0.21463,0.23451],"tcp_start":[0.58809,0.16414,0.28226],"tcp_to_object_dist_end":0.01941,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.89172,"average_solve_count":157.0,"average_success_count":157.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_height":0.10948,"approach_object.approach_speed":0.13491,"descend_to_grasp.descend_depth":0.00332,"descend_to_place.place_height_z":0.02198,"descend_to_place.place_speed":0.07367,"lift.lift_height":0.13653,"lift.lift_speed":0.07278,"transport_to_goal.transport_speed":0.10035},"optimized_scores":{"best_composite_score":0.45627,"best_fitness_score":0.97627,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":107.0,"contact_point_centroid":[0.54236,-0.02842,-0.00125],"force_p95":0.50464,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.64951,"mean_force":0.11665,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52967,-0.02857,0.02806]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":11628.0,"contact_point_centroid":[0.53442,-0.04789,0.08999],"force_p95":0.08373,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.35831,"mean_force":0.05965,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.53366,-0.0287,0.08721]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":13998.0,"contact_point_centroid":[0.5352,-0.00975,0.08779],"force_p95":0.08117,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29854,"mean_force":0.05126,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.53356,-0.02869,0.08615]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.54563,-0.02925,-0.00205],"force_p95":0.13917,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.16845,"mean_force":0.12686,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.532,-0.02863,0.02812]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2289.0,"contact_point_centroid":[0.62214,0.1179,0.23035],"force_p95":0.11296,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16539,"mean_force":0.07215,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.61565,0.13588,0.2312]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2429.0,"contact_point_centroid":[0.6148,0.15512,0.23214],"force_p95":0.10243,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15659,"mean_force":0.06709,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.61575,0.13611,0.23079]},{"body_a":"world","body_b":"grasp_target","contact_count":2064.0,"contact_point_centroid":[0.5456,-0.02923,-0.00193],"force_p95":0.13251,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12286,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.51781,-0.01323,0.2222]},{"body_a":"world","body_b":"grasp_target","contact_count":1320.0,"contact_point_centroid":[0.5456,-0.02923,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.53751,-0.0278,0.09088]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":15720.0,"contact_point_centroid":[0.57794,0.03079,0.20292],"force_p95":0.09231,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11641,"mean_force":0.06298,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.57489,0.04967,0.20193]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5293.0,"contact_point_centroid":[0.53187,-0.00965,0.02889],"force_p95":0.07075,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10919,"mean_force":0.04088,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.5307,-0.0286,0.02663]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":18362.0,"contact_point_centroid":[0.57471,0.068,0.20262],"force_p95":0.08155,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10073,"mean_force":0.0545,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.57463,0.04916,0.20153]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4142.0,"contact_point_centroid":[0.53164,-0.0479,0.02944],"force_p95":0.09076,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09488,"mean_force":0.05488,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.53071,-0.0286,0.02664]}],"total_contact_groups":12},"final_pose_error":0.01471,"key_states":{"actual_goal_position":[0.63284,0.16493,0.17692],"final_object_position":[0.63473,0.15737,0.18742],"final_tcp_position":[0.6243,0.15408,0.20395],"realised_goal_position":[0.63284,0.16493,0.17692],"realised_object_initial_position":[0.5456,-0.02923,0.03]},"peak_contact_force":0.64951,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":517.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.03],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.25864,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2064.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.53811,-0.02688,0.14563],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.11987,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":330.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1320.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.53967,-0.02882,0.0371],"tcp_start":[0.53811,-0.02688,0.14563],"tcp_to_object_dist_end":0.01257,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54561,-0.02904,0.0258],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26091,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.13918,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11235.0,"raw_peak_contact_force":0.16845,"tcp_end":[0.53067,-0.0286,0.02659],"tcp_start":[0.53967,-0.02882,0.0371],"tcp_to_object_dist_end":0.01496,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":684.0,"n_steps_budget":1000.0,"object_pos_end":[0.55375,-0.02947,0.14111],"object_pos_start":[0.54561,-0.02904,0.0258],"object_to_goal_dist_end":0.2129,"object_to_goal_dist_start":0.26091,"object_z_max":0.14097,"peak_contact_force":0.08058,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":25733.0,"raw_peak_contact_force":0.64951,"subtask_id":"lift_object","tcp_end":[0.54069,-0.0289,0.14823],"tcp_start":[0.53067,-0.0286,0.02659],"tcp_to_object_dist_end":0.01488,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":38.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.61969,0.12384,0.24101],"object_pos_start":[0.55375,-0.02947,0.14111],"object_to_goal_dist_end":0.07726,"object_to_goal_dist_start":0.2129,"object_z_max":0.24092,"peak_contact_force":0.07385,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":34082.0,"raw_peak_contact_force":0.11641,"subtask_id":"place_at_goal","tcp_end":[0.60946,0.12133,0.25589],"tcp_start":[0.54069,-0.0289,0.14823],"tcp_to_object_dist_end":0.01823,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":29.0,"n_steps":163.0,"n_steps_budget":1000.0,"object_pos_end":[0.63473,0.15737,0.18742],"object_pos_start":[0.61969,0.12384,0.24101],"object_to_goal_dist_end":0.01308,"object_to_goal_dist_start":0.07726,"object_z_max":0.24102,"peak_contact_force":0.0,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4718.0,"raw_peak_contact_force":0.16539,"subtask_id":"place_at_goal","tcp_end":[0.6243,0.15408,0.20395],"tcp_start":[0.60946,0.12133,0.25589],"tcp_to_object_dist_end":0.01982,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.73892,"average_solve_count":203.0,"average_success_count":203.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_height":0.1105,"approach_object.approach_speed":0.08272,"descend_to_grasp.descend_depth":0.0002,"descend_to_place.place_height_z":0.0093,"descend_to_place.place_speed":0.0547,"lift.lift_height":0.23185,"lift.lift_speed":0.10889,"transport_to_goal.transport_speed":0.08359},"optimized_scores":{"best_composite_score":0.45944,"best_fitness_score":0.97944,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":85.0,"contact_point_centroid":[0.45986,-0.00051,-0.00128],"force_p95":0.50102,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.65906,"mean_force":0.12923,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.44891,-0.00031,0.02852]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":18417.0,"contact_point_centroid":[0.45368,-0.01947,0.13508],"force_p95":0.07758,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29466,"mean_force":0.05324,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.45238,-0.00034,0.13292]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":18904.0,"contact_point_centroid":[0.45344,0.01877,0.13332],"force_p95":0.07712,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2895,"mean_force":0.05217,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.45229,-0.00034,0.13133]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4084.0,"contact_point_centroid":[0.59802,0.16626,0.19246],"force_p95":0.07488,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25295,"mean_force":0.05103,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.60138,0.1475,0.18895]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4532.0,"contact_point_centroid":[0.60557,0.12866,0.19224],"force_p95":0.06912,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19606,"mean_force":0.04709,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.60129,0.1474,0.19077]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.46284,-0.00015,-0.00202],"force_p95":0.1296,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.14451,"mean_force":0.12463,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.45111,-0.00027,0.02828]},{"body_a":"world","body_b":"grasp_target","contact_count":1820.0,"contact_point_centroid":[0.46286,-7e-05,-0.00192],"force_p95":0.1336,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12289,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.48086,-6e-05,0.22592]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":16378.0,"contact_point_centroid":[0.53487,0.05713,0.23822],"force_p95":0.07841,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13415,"mean_force":0.0512,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.53222,0.0761,0.2367]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":16215.0,"contact_point_centroid":[0.52913,0.09379,0.23914],"force_p95":0.07688,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12975,"mean_force":0.05129,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.531,0.07487,0.23673]},{"body_a":"world","body_b":"grasp_target","contact_count":1480.0,"contact_point_centroid":[0.46286,-7e-05,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.45908,-0.00015,0.09236]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4850.0,"contact_point_centroid":[0.45094,-0.0195,0.02922],"force_p95":0.06673,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08766,"mean_force":0.04482,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.44993,-0.00029,0.02716]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5125.0,"contact_point_centroid":[0.45064,0.01892,0.02889],"force_p95":0.06493,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08387,"mean_force":0.04295,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.44993,-0.00029,0.02716]}],"total_contact_groups":12},"final_pose_error":0.015,"key_states":{"actual_goal_position":[0.61015,0.15287,0.12219],"final_object_position":[0.59837,0.15016,0.12722],"final_tcp_position":[0.60427,0.15031,0.14504],"realised_goal_position":[0.61015,0.15287,0.12219],"realised_object_initial_position":[0.46286,-7e-05,0.03]},"peak_contact_force":0.65906,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":456.0,"n_steps_budget":1000.0,"object_pos_end":[0.46286,-7e-05,0.02602],"object_pos_start":[0.46286,-7e-05,0.03],"object_to_goal_dist_end":0.2331,"object_to_goal_dist_start":0.23148,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1820.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.46256,-0.00011,0.15042],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.1244,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":370.0,"n_steps_budget":1000.0,"object_pos_end":[0.46286,-7e-05,0.02602],"object_pos_start":[0.46286,-7e-05,0.02602],"object_to_goal_dist_end":0.2331,"object_to_goal_dist_start":0.2331,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1480.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.45819,-0.00015,0.03506],"tcp_start":[0.46256,-0.00011,0.15042],"tcp_to_object_dist_end":0.01017,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":45.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.46272,-0.0003,0.02591],"object_pos_start":[0.46286,-7e-05,0.02602],"object_to_goal_dist_end":0.23338,"object_to_goal_dist_start":0.2331,"object_z_max":0.02602,"peak_contact_force":0.12898,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11775.0,"raw_peak_contact_force":0.14451,"tcp_end":[0.4499,-0.00029,0.02713],"tcp_start":[0.45819,-0.00015,0.03506],"tcp_to_object_dist_end":0.01288,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":956.0,"n_steps_budget":1000.0,"object_pos_end":[0.47172,-0.00031,0.23294],"object_pos_start":[0.46272,-0.0003,0.02591],"object_to_goal_dist_end":0.23429,"object_to_goal_dist_start":0.23338,"object_z_max":0.23276,"peak_contact_force":0.0809,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":37406.0,"raw_peak_contact_force":0.65906,"subtask_id":"lift_object","tcp_end":[0.45926,-0.00033,0.24334],"tcp_start":[0.4499,-0.00029,0.02713],"tcp_to_object_dist_end":0.01623,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":822.0,"n_steps_budget":1000.0,"object_pos_end":[0.59276,0.14438,0.21739],"object_pos_start":[0.47172,-0.00031,0.23294],"object_to_goal_dist_end":0.09714,"object_to_goal_dist_start":0.23429,"object_z_max":0.23305,"peak_contact_force":0.07632,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":32593.0,"raw_peak_contact_force":0.13415,"subtask_id":"place_at_goal","tcp_end":[0.60012,0.14503,0.23439],"tcp_start":[0.45926,-0.00033,0.24334],"tcp_to_object_dist_end":0.01853,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":206.0,"n_steps_budget":1000.0,"object_pos_end":[0.59837,0.15016,0.12722],"object_pos_start":[0.59276,0.14438,0.21739],"object_to_goal_dist_end":0.01309,"object_to_goal_dist_start":0.09714,"object_z_max":0.21739,"peak_contact_force":0.07282,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":8616.0,"raw_peak_contact_force":0.25295,"subtask_id":"place_at_goal","tcp_end":[0.60427,0.15031,0.14504],"tcp_start":[0.60012,0.14503,0.23439],"tcp_to_object_dist_end":0.01878,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```