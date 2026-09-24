## Search State

- **Seed**: 9
- **Iteration**: 14 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 13 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 14 | 0.1535 | 1.00 | ✅ accepted |
| 12 | approach → descend → grasp → lift → approach → descend | arc_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 7 | 0.2650 | 0.54 | ❌ rejected |
| 11 | approach → descend → grasp → lift → approach → descend | arc_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 15 | 0.1034 | 1.00 | ❌ rejected |
| 10 | approach → descend → grasp → lift → approach → descend | arc_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 15 | 0.1044 | 1.00 | ❌ rejected |
| 9 | approach → descend → grasp → lift → approach → descend | arc_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 15 | 0.1049 | 1.00 | ✅ accepted |

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

## Current Skill (Q=0.153) — your mutation base

```yaml
skill: grasp_place
dsl_version: 2
skill_type: arm_gripper
subtasks:
- id: reach_object_approach
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.1
  weight: 0.3
- id: lift_clearance
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.15
  weight: 0.25
- id: approach_goal
  offset:
  - 0.0
  - 0.0
  - 0.1
  weight: 0.2
- id: place_goal
  target_entity: object
  metric: goal_progress
  weight: 0.25
phases:
- id: approach_1
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
    tolerance: 0.05
    orientation:
      mode: keep_current
  parameters:
    approach_height:
      type: scalar
      range:
      - 0.05
      - 0.3
      default: 0.15
      binds_to:
      - path: target.offset.z
        mode: replace
    approach_tolerance:
      type: scalar
      range:
      - 0.02
      - 0.08
      default: 0.05
      binds_to:
      - path: termination.pose_tolerance
        mode: replace
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: reach_object_approach
- id: descend_1
  type: descend
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
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    descend_height:
      type: scalar
      range:
      - 0.0
      - 0.06
      default: 0.02
      binds_to:
      - path: target.offset.z
        mode: replace
    descend_speed:
      type: scalar
      range:
      - 0.01
      - 0.05
      default: 0.03
      binds_to:
      - path: generator.speed
        mode: replace
    descend_tolerance:
      type: scalar
      range:
      - 0.01
      - 0.04
      default: 0.02
      binds_to:
      - path: termination.pose_tolerance
        mode: replace
  subtask_id: reach_object_approach
- id: grasp_1
  type: grasp
  control: position_control
  termination: time_limit
  end_effector_action: force_grasp
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.0
    - 0.0
    orientation:
      mode: keep_current
  guards:
  - id: check_grasp
    when: after_phase
    predicate: bilateral_grasp
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: repeat
- id: lift_1
  type: lift
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
    lift_height:
      type: scalar
      range:
      - 0.05
      - 0.3
      default: 0.15
      binds_to:
      - path: target.offset.z
        mode: replace
    lift_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: lift_clearance
- id: transport_1
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.1
    tolerance: 0.05
    orientation:
      mode: keep_current
  parameters:
    transport_height:
      type: scalar
      range:
      - 0.05
      - 0.25
      default: 0.1
      binds_to:
      - path: target.offset.z
        mode: replace
    transport_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
    transport_tolerance:
      type: scalar
      range:
      - 0.03
      - 0.1
      default: 0.05
      binds_to:
      - path: termination.pose_tolerance
        mode: replace
  subtask_id: approach_goal
- id: descend_to_place
  type: descend
  generator: linear_cartesian
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.023
    tolerance: 0.015
    orientation:
      mode: keep_current
  parameters:
    descend_speed_place:
      type: scalar
      range:
      - 0.01
      - 0.08
      default: 0.03
      binds_to:
      - path: generator.speed
        mode: replace
    place_height:
      type: scalar
      range:
      - 0.0
      - 0.05
      default: 0.023
      binds_to:
      - path: target.offset.z
        mode: replace
    place_tolerance:
      type: scalar
      range:
      - 0.005
      - 0.03
      default: 0.015
      binds_to:
      - path: termination.pose_tolerance
        mode: replace
  subtask_id: place_goal

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.15], tolerance=0.05
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_height: status=consumed; consumers=target.offset.z (replace)
    - approach_tolerance: status=consumed; consumers=termination.pose_tolerance (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
- **descend_1** (`descend`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.02], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - descend_height: status=consumed; consumers=target.offset.z (replace)
    - descend_speed: status=consumed; consumers=generator.speed (replace)
    - descend_tolerance: status=consumed; consumers=termination.pose_tolerance (replace)
- **grasp_1** (`grasp`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings: none
  - guards:
    - id=check_grasp, when=after_phase, predicate=bilateral_grasp, on_failure=retry
  - retries: max_attempts=2, strategy=repeat
- **lift_1** (`lift`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.15], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset.z (replace)
    - lift_speed: status=consumed; consumers=generator.speed (replace)
- **transport_1** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.1], tolerance=0.05
  - orientation: mode=keep_current
  - parameter_bindings:
    - transport_height: status=consumed; consumers=target.offset.z (replace)
    - transport_speed: status=consumed; consumers=generator.speed (replace)
    - transport_tolerance: status=consumed; consumers=termination.pose_tolerance (replace)
- **descend_to_place** (`descend`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.023], tolerance=0.015
  - orientation: mode=keep_current
  - parameter_bindings:
    - descend_speed_place: status=consumed; consumers=generator.speed (replace)
    - place_height: status=consumed; consumers=target.offset.z (replace)
    - place_tolerance: status=consumed; consumers=termination.pose_tolerance (replace)

## Design Metrics

- **Composite score**: 0.153
- **task_score** (E): 1.000
- **fitness_score**: 0.973  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.820

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.0937 |
| descend_1 | 1.00 | 1.00 | 0.1673 |
| grasp_1 | 1.00 | 1.00 | 0.0130 |
| lift_1 | 1.00 | 1.00 | 0.1545 |
| transport_1 | 1.00 | 1.00 | 0.2177 |
| descend_to_place | 1.00 | 1.00 | 0.0934 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.506, -0.009, 0.211) | (0.515, -0.017, 0.030)→(0.515, -0.017, 0.026) | 0.268→0.270 | 1.00 / 4.000 | 27.133 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.506, -0.009, 0.211)→(0.510, -0.016, 0.045) | (0.515, -0.017, 0.026)→(0.515, -0.017, 0.026) | 0.270→0.270 | 1.00 / 4.000 | 27.129 | 0.125 |
| grasp_1 | grasp | 1.00 / step_budget | (0.510, -0.016, 0.045)→(0.501, -0.016, 0.035) | (0.515, -0.017, 0.026)→(0.515, -0.016, 0.026) | 0.270→0.270 | 1.00 / 42.000 | 0.148 | 0.209 |
| lift_1 | lift | 1.00 / step_budget | (0.501, -0.016, 0.035)→(0.511, -0.016, 0.189) | (0.515, -0.016, 0.026)→(0.523, -0.016, 0.174) | 0.270→0.229 | 1.00 / 32.333 | 95.333 | 0.493 |
| transport_1 | approach | 1.00 / step_budget | (0.511, -0.016, 0.189)→(0.599, 0.148, 0.290) | (0.523, -0.016, 0.174)→(0.612, 0.148, 0.273) | 0.229→0.111 | 1.00 / 25.667 | 71.754 | 0.134 |
| descend_to_place | descend | 1.00 / step_budget | (0.599, 0.148, 0.290)→(0.611, 0.174, 0.202) | (0.612, 0.148, 0.273)→(0.622, 0.174, 0.182) | 0.111→0.017 | 1.00 / 23.333 | 0.123 | 0.323 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.034
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 1.000
- phase_score: 0.472
- phase_breakdown.reach_object_approach_score: 0.184
- phase_breakdown.approach_goal_score: 0.212
- phase_breakdown.lift_clearance_score: 0.625
- phase_breakdown.place_goal_score: 0.872
- grasp_place_fitness: 0.976

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.976
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 1.000
- **Median Q (composite search score)**: 0.153
- **K-run variance**: 0.0000
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Parameters at lower bound**: descend_1.descend_tolerance, descend_1.descend_height
- **Final σ (mean)**: 0.292


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.16203,"average_solve_count":395.0,"average_success_count":395.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.19791,"approach_1.approach_tolerance":0.06023,"approach_1.speed":0.05163,"descend_1.descend_height":5e-05,"descend_1.descend_speed":0.02295,"descend_1.descend_tolerance":0.02947,"descend_to_place.descend_speed_place":0.03855,"descend_to_place.place_height":0.02359,"descend_to_place.place_tolerance":0.01692,"lift_1.lift_height":0.21774,"lift_1.lift_speed":0.01945,"transport_1.transport_height":0.11584,"transport_1.transport_speed":0.07288,"transport_1.transport_tolerance":0.05779},"optimized_scores":{"best_composite_score":0.15257,"best_fitness_score":0.97257,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":98.0,"contact_point_centroid":[0.53301,-0.01929,-0.00157],"force_p95":0.45234,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.46694,"mean_force":0.17582,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.5206,-0.01978,0.03485]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2409.0,"contact_point_centroid":[0.60426,0.21951,0.27115],"force_p95":0.0975,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.34875,"mean_force":0.0714,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.60053,0.20069,0.27052]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":12758.0,"contact_point_centroid":[0.52632,-0.00069,0.13236],"force_p95":0.08321,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26161,"mean_force":0.0573,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52534,-0.0198,0.12996]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":13608.0,"contact_point_centroid":[0.52598,-0.03884,0.12753],"force_p95":0.08033,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25987,"mean_force":0.05484,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52501,-0.0198,0.12549]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53709,-0.02107,-0.00214],"force_p95":0.16293,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.23569,"mean_force":0.13314,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52288,-0.01982,0.03528]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2292.0,"contact_point_centroid":[0.60413,0.18226,0.27098],"force_p95":0.09917,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19351,"mean_force":0.07287,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.60063,0.20107,0.26967]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4071.0,"contact_point_centroid":[0.52298,-0.00059,0.03661],"force_p95":0.08102,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15154,"mean_force":0.05192,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52168,-0.0198,0.03392]},{"body_a":"world","body_b":"grasp_target","contact_count":184.0,"contact_point_centroid":[0.53702,-0.02132,-0.00128],"force_p95":0.13839,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12438,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50564,-0.00284,0.28924]},{"body_a":"world","body_b":"grasp_target","contact_count":1756.0,"contact_point_centroid":[0.53702,-0.02132,-0.002],"force_p95":0.12287,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12867,"mean_force":0.12272,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.52172,-0.014,0.15491]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4729.0,"contact_point_centroid":[0.56385,0.05569,0.25771],"force_p95":0.08253,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10922,"mean_force":0.05539,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.56224,0.07462,0.25654]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4041.0,"contact_point_centroid":[0.56418,0.09416,0.25859],"force_p95":0.08901,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10119,"mean_force":0.06095,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.56239,0.0751,0.25672]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5006.0,"contact_point_centroid":[0.52291,-0.03895,0.03571],"force_p95":0.07345,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07976,"mean_force":0.04454,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52169,-0.0198,0.03393]}],"total_contact_groups":12},"final_pose_error":0.01499,"key_states":{"actual_goal_position":[0.61031,0.22775,0.20741],"final_object_position":[0.61548,0.21627,0.22125],"final_tcp_position":[0.6047,0.21656,0.23924],"realised_goal_position":[0.61031,0.22775,0.20741],"realised_object_initial_position":[0.53702,-0.02132,0.03]},"peak_contact_force":0.46694,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":47.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02591],"object_pos_start":[0.53702,-0.02132,0.03],"object_to_goal_dist_end":0.31678,"object_to_goal_dist_start":0.31446,"object_z_max":0.03,"peak_contact_force":0.12911,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":184.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object_approach","tcp_end":[0.51504,-0.00805,0.26959],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.24503,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":439.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.02591],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31678,"object_z_max":0.02602,"peak_contact_force":0.12262,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1756.0,"raw_peak_contact_force":0.12867,"subtask_id":"reach_object_approach","tcp_end":[0.5305,-0.01991,0.04431],"tcp_start":[0.51504,-0.00805,0.26959],"tcp_to_object_dist_end":0.01947,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53695,-0.01995,0.02554],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31594,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.15527,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10877.0,"raw_peak_contact_force":0.23569,"tcp_end":[0.52165,-0.0198,0.03389],"tcp_start":[0.5305,-0.01991,0.04431],"tcp_to_object_dist_end":0.01743,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":712.0,"n_steps_budget":1000.0,"object_pos_end":[0.54288,-0.01991,0.20895],"object_pos_start":[0.53695,-0.01995,0.02554],"object_to_goal_dist_end":0.25668,"object_to_goal_dist_start":0.31594,"object_z_max":0.20869,"peak_contact_force":0.08006,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":26464.0,"raw_peak_contact_force":0.46694,"subtask_id":"lift_clearance","tcp_end":[0.53281,-0.01988,0.22372],"tcp_start":[0.52165,-0.0198,0.03389],"tcp_to_object_dist_end":0.01788,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":30.0,"n_steps":255.0,"n_steps_budget":1000.0,"object_pos_end":[0.60845,0.18619,0.28285],"object_pos_start":[0.54288,-0.01991,0.20895],"object_to_goal_dist_end":0.08615,"object_to_goal_dist_start":0.25668,"object_z_max":0.28254,"peak_contact_force":0.09005,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":8770.0,"raw_peak_contact_force":0.10922,"subtask_id":"approach_goal","tcp_end":[0.59784,0.1863,0.29905],"tcp_start":[0.53281,-0.01988,0.22372],"tcp_to_object_dist_end":0.01937,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":28.0,"n_steps":166.0,"n_steps_budget":1000.0,"object_pos_end":[0.61548,0.21627,0.22125],"object_pos_start":[0.60845,0.18619,0.28285],"object_to_goal_dist_end":0.01871,"object_to_goal_dist_start":0.08615,"object_z_max":0.28316,"peak_contact_force":0.09964,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4701.0,"raw_peak_contact_force":0.34875,"subtask_id":"place_goal","tcp_end":[0.6047,0.21656,0.23924],"tcp_start":[0.59784,0.1863,0.29905],"tcp_to_object_dist_end":0.02097,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.02906,"average_solve_count":413.0,"average_success_count":413.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.11672,"approach_1.approach_tolerance":0.04458,"approach_1.speed":0.02827,"descend_1.descend_height":6e-05,"descend_1.descend_speed":0.03351,"descend_1.descend_tolerance":0.01933,"descend_to_place.descend_speed_place":0.03175,"descend_to_place.place_height":0.01602,"descend_to_place.place_tolerance":0.01267,"lift_1.lift_height":0.13455,"lift_1.lift_speed":0.05278,"transport_1.transport_height":0.14328,"transport_1.transport_speed":0.07047,"transport_1.transport_tolerance":0.07144},"optimized_scores":{"best_composite_score":0.15194,"best_fitness_score":0.97194,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":97.0,"contact_point_centroid":[0.54324,-0.02677,-0.00151],"force_p95":0.44909,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.51454,"mean_force":0.10617,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52886,-0.02737,0.03506]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":7114.0,"contact_point_centroid":[0.53482,-0.00818,0.08677],"force_p95":0.11127,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.34174,"mean_force":0.06213,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.533,-0.02734,0.08494]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8208.0,"contact_point_centroid":[0.53463,-0.04598,0.08794],"force_p95":0.08659,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28856,"mean_force":0.05458,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.53318,-0.02735,0.08627]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1810.0,"contact_point_centroid":[0.6276,0.16377,0.24954],"force_p95":0.14348,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27077,"mean_force":0.10553,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.62166,0.14503,0.24751]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.5457,-0.02892,-0.00216],"force_p95":0.17034,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24431,"mean_force":0.13517,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53114,-0.02745,0.03523]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2385.0,"contact_point_centroid":[0.62776,0.12719,0.24712],"force_p95":0.11197,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22719,"mean_force":0.08098,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.62181,0.14541,0.24607]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4458.0,"contact_point_centroid":[0.57676,0.02645,0.20352],"force_p95":0.09827,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16261,"mean_force":0.06337,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.57421,0.04494,0.20291]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3911.0,"contact_point_centroid":[0.53164,-0.00823,0.03644],"force_p95":0.08927,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15261,"mean_force":0.05655,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52992,-0.02741,0.03382]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3212.0,"contact_point_centroid":[0.57815,0.06363,0.20401],"force_p95":0.11393,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14336,"mean_force":0.08122,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.57409,0.04468,0.20268]},{"body_a":"world","body_b":"grasp_target","contact_count":524.0,"contact_point_centroid":[0.5456,-0.02923,-0.00176],"force_p95":0.13797,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12356,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.5118,-0.00766,0.25625]},{"body_a":"world","body_b":"grasp_target","contact_count":1156.0,"contact_point_centroid":[0.5456,-0.02923,-0.00199],"force_p95":0.12264,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12264,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.53288,-0.0234,0.11718]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5040.0,"contact_point_centroid":[0.53124,-0.0465,0.03558],"force_p95":0.07488,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08275,"mean_force":0.04432,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52993,-0.02741,0.03383]}],"total_contact_groups":12},"final_pose_error":0.01475,"key_states":{"actual_goal_position":[0.63284,0.16493,0.17692],"final_object_position":[0.63896,0.15741,0.18411],"final_tcp_position":[0.62662,0.15745,0.20402],"realised_goal_position":[0.63284,0.16493,0.17692],"realised_object_initial_position":[0.5456,-0.02923,0.03]},"peak_contact_force":285.81629,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":132.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.03],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.25864,"object_z_max":0.03,"peak_contact_force":0.12261,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":524.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object_approach","tcp_end":[0.52981,-0.01927,0.19261],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.16763,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":289.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":81.14225,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1156.0,"raw_peak_contact_force":0.12264,"subtask_id":"reach_object_approach","tcp_end":[0.53887,-0.02762,0.04457],"tcp_start":[0.52981,-0.01927,0.19261],"tcp_to_object_dist_end":0.0198,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54568,-0.02755,0.02546],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.25997,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.16055,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10751.0,"raw_peak_contact_force":0.24431,"tcp_end":[0.52989,-0.02741,0.03379],"tcp_start":[0.53887,-0.02762,0.04457],"tcp_to_object_dist_end":0.01786,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":33.0,"n_steps":412.0,"n_steps_budget":1000.0,"object_pos_end":[0.5536,-0.0275,0.12724],"object_pos_start":[0.54568,-0.02755,0.02546],"object_to_goal_dist_end":0.21395,"object_to_goal_dist_start":0.25997,"object_z_max":0.127,"peak_contact_force":285.81629,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":15419.0,"raw_peak_contact_force":0.51454,"subtask_id":"lift_clearance","tcp_end":[0.5401,-0.02741,0.14095],"tcp_start":[0.52989,-0.02741,0.03379],"tcp_to_object_dist_end":0.01924,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":24.0,"n_steps":270.0,"n_steps_budget":1000.0,"object_pos_end":[0.63213,0.13436,0.26711],"object_pos_start":[0.5536,-0.0275,0.12724],"object_to_goal_dist_end":0.09523,"object_to_goal_dist_start":0.21395,"object_z_max":0.26657,"peak_contact_force":0.11129,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":7670.0,"raw_peak_contact_force":0.16261,"subtask_id":"approach_goal","tcp_end":[0.61854,0.13476,0.28407],"tcp_start":[0.5401,-0.02741,0.14095],"tcp_to_object_dist_end":0.02174,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":20.0,"n_steps":198.0,"n_steps_budget":1000.0,"object_pos_end":[0.63896,0.15741,0.18411],"object_pos_start":[0.63213,0.13436,0.26711],"object_to_goal_dist_end":0.01206,"object_to_goal_dist_start":0.09523,"object_z_max":0.26825,"peak_contact_force":0.15862,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4195.0,"raw_peak_contact_force":0.27077,"subtask_id":"place_goal","tcp_end":[0.62662,0.15745,0.20402],"tcp_start":[0.61854,0.13476,0.28407],"tcp_to_object_dist_end":0.02343,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.91139,"average_solve_count":474.0,"average_success_count":474.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.09412,"approach_1.approach_tolerance":0.02083,"approach_1.speed":0.03283,"descend_1.descend_height":0.0,"descend_1.descend_speed":0.02097,"descend_1.descend_tolerance":0.01,"descend_to_place.descend_speed_place":0.04631,"descend_to_place.place_height":0.0292,"descend_to_place.place_tolerance":0.02213,"lift_1.lift_height":0.19662,"lift_1.lift_speed":0.06301,"transport_1.transport_height":0.19383,"transport_1.transport_speed":0.03159,"transport_1.transport_tolerance":0.07657},"optimized_scores":{"best_composite_score":0.15588,"best_fitness_score":0.97588,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":77.0,"contact_point_centroid":[0.46041,-0.00041,-0.00136],"force_p95":0.43085,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.49708,"mean_force":0.12607,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.45198,-0.00022,0.03877]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3472.0,"contact_point_centroid":[0.59656,0.15331,0.22947],"force_p95":0.12499,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.34831,"mean_force":0.08846,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.59081,0.13469,0.22803]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":9620.0,"contact_point_centroid":[0.45473,0.0189,0.11918],"force_p95":0.08979,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28499,"mean_force":0.05882,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.45392,-0.00022,0.11705]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":10421.0,"contact_point_centroid":[0.45466,-0.01924,0.11814],"force_p95":0.08534,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.281,"mean_force":0.05507,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.45386,-0.00022,0.11637]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3492.0,"contact_point_centroid":[0.59681,0.1164,0.22832],"force_p95":0.12545,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2805,"mean_force":0.08572,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.59098,0.13489,0.22681]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.46284,-9e-05,-0.00202],"force_p95":0.12879,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.14604,"mean_force":0.12448,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.45396,-0.00019,0.03853]},{"body_a":"world","body_b":"grasp_target","contact_count":548.0,"contact_point_centroid":[0.46286,-7e-05,-0.00177],"force_p95":0.13795,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12352,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48896,-3e-05,0.246]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2870.0,"contact_point_centroid":[0.51702,0.07321,0.24081],"force_p95":0.10976,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12978,"mean_force":0.07723,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.51329,0.05453,0.23978]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3294.0,"contact_point_centroid":[0.51956,0.03847,0.24197],"force_p95":0.10247,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12698,"mean_force":0.07281,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.51578,0.05703,0.24153]},{"body_a":"world","body_b":"grasp_target","contact_count":1044.0,"contact_point_centroid":[0.46286,-7e-05,-0.00199],"force_p95":0.12264,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12264,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.46624,-9e-05,0.10909]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4864.0,"contact_point_centroid":[0.45308,0.019,0.0394],"force_p95":0.06805,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08914,"mean_force":0.04481,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.4529,-0.0002,0.03752]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4848.0,"contact_point_centroid":[0.45311,-0.01939,0.03942],"force_p95":0.06799,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08698,"mean_force":0.04477,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.4529,-0.0002,0.03752]}],"total_contact_groups":12},"final_pose_error":0.01471,"key_states":{"actual_goal_position":[0.61015,0.15287,0.12219],"final_object_position":[0.61288,0.14749,0.14055],"final_tcp_position":[0.60241,0.14763,0.16276],"realised_goal_position":[0.61015,0.15287,0.12219],"realised_object_initial_position":[0.46286,-7e-05,0.03]},"peak_contact_force":215.06119,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":138.0,"n_steps_budget":1000.0,"object_pos_end":[0.46286,-7e-05,0.02602],"object_pos_start":[0.46286,-7e-05,0.03],"object_to_goal_dist_end":0.2331,"object_to_goal_dist_start":0.23148,"object_z_max":0.03,"peak_contact_force":81.14715,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":548.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object_approach","tcp_end":[0.47392,-6e-05,0.17214],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.14654,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":261.0,"n_steps_budget":1000.0,"object_pos_end":[0.46286,-7e-05,0.02602],"object_pos_start":[0.46286,-7e-05,0.02602],"object_to_goal_dist_end":0.2331,"object_to_goal_dist_start":0.2331,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1044.0,"raw_peak_contact_force":0.12264,"subtask_id":"reach_object_approach","tcp_end":[0.46083,-0.00011,0.04545],"tcp_start":[0.47392,-6e-05,0.17214],"tcp_to_object_dist_end":0.01953,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.46275,-0.00017,0.02591],"object_pos_start":[0.46286,-7e-05,0.02602],"object_to_goal_dist_end":0.23328,"object_to_goal_dist_start":0.2331,"object_z_max":0.02602,"peak_contact_force":0.12855,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11512.0,"raw_peak_contact_force":0.14604,"tcp_end":[0.45287,-0.0002,0.03749],"tcp_start":[0.46083,-0.00011,0.04545],"tcp_to_object_dist_end":0.01522,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":27.0,"n_steps":537.0,"n_steps_budget":1000.0,"object_pos_end":[0.4732,-3e-05,0.18699],"object_pos_start":[0.46275,-0.00017,0.02591],"object_to_goal_dist_end":0.21525,"object_to_goal_dist_start":0.23328,"object_z_max":0.18671,"peak_contact_force":0.10359,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":20118.0,"raw_peak_contact_force":0.49708,"subtask_id":"lift_clearance","tcp_end":[0.45874,-0.0002,0.20312],"tcp_start":[0.45287,-0.0002,0.03749],"tcp_to_object_dist_end":0.02166,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":230.0,"n_steps_budget":1000.0,"object_pos_end":[0.5947,0.12343,0.26948],"object_pos_start":[0.4732,-3e-05,0.18699],"object_to_goal_dist_end":0.151,"object_to_goal_dist_start":0.21525,"object_z_max":0.26907,"peak_contact_force":215.06119,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":6164.0,"raw_peak_contact_force":0.12978,"subtask_id":"approach_goal","tcp_end":[0.58184,0.12338,0.28809],"tcp_start":[0.45874,-0.0002,0.20312],"tcp_to_object_dist_end":0.02262,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":22.0,"n_steps":310.0,"n_steps_budget":1000.0,"object_pos_end":[0.61288,0.14749,0.14055],"object_pos_start":[0.5947,0.12343,0.26948],"object_to_goal_dist_end":0.01933,"object_to_goal_dist_start":0.151,"object_z_max":0.27017,"peak_contact_force":0.10959,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":6964.0,"raw_peak_contact_force":0.34831,"subtask_id":"place_goal","tcp_end":[0.60241,0.14763,0.16276],"tcp_start":[0.58184,0.12338,0.28809],"tcp_to_object_dist_end":0.02455,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```