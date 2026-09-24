## Search State

- **Seed**: 9
- **Iteration**: 12 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 11 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 6 | 0.5572 | 1.00 | ❌ rejected |
| 10 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | time_limit | pose_tolerance | 7 | 0.4860 | 0.96 | ❌ rejected |
| 9 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 6 | 0.4871 | 0.87 | ❌ rejected |
| 8 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 6 | 0.5572 | 1.00 | ✅ accepted |
| 7 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 6 | 0.5572 | 1.00 | ✅ accepted |

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

## Current Skill (Q=0.557) — your mutation base

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
  weight: 0.3
- id: reach_goal
  target_entity: object
  weight: 0.7
phases:
- id: approach_above
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
      mode: none
  parameters:
    approach_speed:
      type: scalar
      range:
      - 0.02
      - 0.2
      default: 0.1
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
    tolerance: 0.01
    orientation:
      mode: none
  parameters:
    descend_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
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
- id: lift_up
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
    - 0.0
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
- id: transport_above_goal
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
    - 0.15
    tolerance: 0.02
    orientation:
      mode: none
  parameters:
    transport_speed:
      type: scalar
      range:
      - 0.02
      - 0.2
      default: 0.1
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: reach_goal
- id: descend_to_place
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
      mode: none
  parameters:
    descend_place_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.03
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: reach_goal

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_above** (`approach`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.1], tolerance=0.02
  - orientation: mode=none
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (replace)
- **descend_to_grasp** (`descend`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.0], tolerance=0.01
  - orientation: mode=none
  - parameter_bindings:
    - descend_speed: status=consumed; consumers=generator.speed (replace)
- **grasp_object** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings: none
- **lift_up** (`lift`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.0], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset.z (replace)
    - lift_speed: status=consumed; consumers=generator.speed (replace)
- **transport_above_goal** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.15], tolerance=0.02
  - orientation: mode=none
  - parameter_bindings:
    - transport_speed: status=consumed; consumers=generator.speed (replace)
- **descend_to_place** (`descend`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], tolerance=0.01
  - orientation: mode=none
  - parameter_bindings:
    - descend_place_speed: status=consumed; consumers=generator.speed (replace)

## Design Metrics

- **Composite score**: 0.557
- **task_score** (E): 1.000
- **fitness_score**: 0.977  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.420

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_above | 1.00 | 1.00 | 0.1574 |
| descend_to_grasp | 1.00 | 1.00 | 0.1141 |
| grasp_object | 1.00 | 1.00 | 0.0129 |
| lift_up | 1.00 | 1.00 | 0.1700 |
| transport_above_goal | 1.00 | 1.00 | 0.2479 |
| descend_to_place | 1.00 | 1.00 | 0.1277 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_above | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.510, -0.015, 0.148) | (0.515, -0.017, 0.030)→(0.515, -0.017, 0.026) | 0.268→0.270 | 1.00 / 4.000 | 39.632 | 0.138 |
| descend_to_grasp | descend | 1.00 / step_budget | (0.510, -0.015, 0.148)→(0.510, -0.017, 0.034) | (0.515, -0.017, 0.026)→(0.515, -0.017, 0.026) | 0.270→0.270 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_object | grasp | 1.00 / step_budget | (0.510, -0.017, 0.034)→(0.501, -0.016, 0.025) | (0.515, -0.017, 0.026)→(0.515, -0.017, 0.026) | 0.270→0.270 | 1.00 / 42.667 | 0.136 | 0.164 |
| lift_up | lift | 1.00 / step_budget | (0.501, -0.016, 0.025)→(0.511, -0.017, 0.194) | (0.515, -0.017, 0.026)→(0.523, -0.017, 0.190) | 0.270→0.233 | 1.00 / 38.333 | 0.079 | 0.556 |
| transport_above_goal | approach | 1.00 / step_budget | (0.511, -0.017, 0.194)→(0.610, 0.171, 0.305) | (0.523, -0.017, 0.190)→(0.617, 0.174, 0.296) | 0.233→0.127 | 1.00 / 38.667 | 0.074 | 0.121 |
| descend_to_place | descend | 1.00 / step_budget | (0.610, 0.171, 0.305)→(0.613, 0.179, 0.177) | (0.617, 0.174, 0.296)→(0.619, 0.182, 0.165) | 0.127→0.009 | 1.00 / 33.667 | 0.089 | 0.164 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.587
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 1.000
- phase_score: 0.775
- phase_breakdown.approach_object_score: 0.671
- phase_breakdown.reach_goal_score: 0.819
- grasp_place_fitness: 0.980

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.980
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 1.000
- **Median Q (composite search score)**: 0.556
- **K-run variance**: 0.0000
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.360


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.39932,"average_solve_count":293.0,"average_success_count":293.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above.approach_speed":0.15403,"descend_to_grasp.descend_speed":0.0396,"descend_to_place.descend_place_speed":0.09851,"lift_up.lift_height":0.20653,"lift_up.lift_speed":0.03496,"transport_above_goal.transport_speed":0.10809},"optimized_scores":{"best_composite_score":0.55621,"best_fitness_score":0.97621,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":94.0,"contact_point_centroid":[0.53318,-0.0209,-0.00145],"force_p95":0.54838,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.58662,"mean_force":0.23108,"phase_index":3.0,"phase_name":"lift_up","phase_type":"lift","tcp_position_centroid":[0.52097,-0.02078,0.02456]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":12507.0,"contact_point_centroid":[0.52555,-0.04006,0.11898],"force_p95":0.08144,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25107,"mean_force":0.05876,"phase_index":3.0,"phase_name":"lift_up","phase_type":"lift","tcp_position_centroid":[0.52507,-0.02088,0.11621]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":14964.0,"contact_point_centroid":[0.52631,-0.00188,0.11695],"force_p95":0.07756,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25089,"mean_force":0.05084,"phase_index":3.0,"phase_name":"lift_up","phase_type":"lift","tcp_position_centroid":[0.52501,-0.02087,0.11523]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4775.0,"contact_point_centroid":[0.60131,0.23833,0.28815],"force_p95":0.09411,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17524,"mean_force":0.06613,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.60524,0.21974,0.28507]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53702,-0.0213,-0.00204],"force_p95":0.13622,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.15851,"mean_force":0.12607,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.52334,-0.02081,0.02526]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6251.0,"contact_point_centroid":[0.61261,0.20267,0.27881],"force_p95":0.07515,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15187,"mean_force":0.05375,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.6053,0.22007,0.28005]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":14751.0,"contact_point_centroid":[0.57345,0.08321,0.27837],"force_p95":0.09037,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13951,"mean_force":0.06061,"phase_index":4.0,"phase_name":"transport_above_goal","phase_type":"approach","tcp_position_centroid":[0.56884,0.10165,0.27747]},{"body_a":"world","body_b":"grasp_target","contact_count":1152.0,"contact_point_centroid":[0.53702,-0.02132,-0.00189],"force_p95":0.13644,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12305,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.51331,-0.00886,0.22483]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":15286.0,"contact_point_centroid":[0.56532,0.11272,0.27483],"force_p95":0.08614,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13708,"mean_force":0.05748,"phase_index":4.0,"phase_name":"transport_above_goal","phase_type":"approach","tcp_position_centroid":[0.56637,0.09387,0.27307]},{"body_a":"world","body_b":"grasp_target","contact_count":1524.0,"contact_point_centroid":[0.53702,-0.02132,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.52816,-0.01959,0.08964]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5297.0,"contact_point_centroid":[0.52312,-0.00176,0.02614],"force_p95":0.06802,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10168,"mean_force":0.04094,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.52205,-0.02079,0.02381]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4171.0,"contact_point_centroid":[0.52309,-0.0401,0.02649],"force_p95":0.07967,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09372,"mean_force":0.05201,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.52205,-0.02079,0.02381]}],"total_contact_groups":12},"final_pose_error":0.00978,"key_states":{"actual_goal_position":[0.61031,0.22775,0.20741],"final_object_position":[0.61499,0.22969,0.20056],"final_tcp_position":[0.60659,0.22503,0.21603],"realised_goal_position":[0.61031,0.22775,0.20741],"realised_object_initial_position":[0.53702,-0.02132,0.03]},"peak_contact_force":61.08426,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":289.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.03],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31446,"object_z_max":0.03,"peak_contact_force":61.08426,"phase_name":"approach_above","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1152.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_object","tcp_end":[0.52858,-0.01834,0.14751],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.12182,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":381.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1524.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.53098,-0.0209,0.03396],"tcp_start":[0.52858,-0.01834,0.14751],"tcp_to_object_dist_end":0.00999,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53688,-0.02109,0.02584],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31668,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.13602,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11268.0,"raw_peak_contact_force":0.15851,"tcp_end":[0.52202,-0.02079,0.02378],"tcp_start":[0.53098,-0.0209,0.03396],"tcp_to_object_dist_end":0.015,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":721.0,"n_steps_budget":1000.0,"object_pos_end":[0.54581,-0.02154,0.20797],"object_pos_start":[0.53688,-0.02109,0.02584],"object_to_goal_dist_end":0.25751,"object_to_goal_dist_start":0.31668,"object_z_max":0.20773,"peak_contact_force":0.08098,"phase_name":"lift_up","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":27565.0,"raw_peak_contact_force":0.58662,"tcp_end":[0.53267,-0.02103,0.213],"tcp_start":[0.52202,-0.02079,0.02378],"tcp_to_object_dist_end":0.01407,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":38.0,"n_steps":876.0,"n_steps_budget":1000.0,"object_pos_end":[0.61652,0.2204,0.33141],"object_pos_start":[0.54581,-0.02154,0.20797],"object_to_goal_dist_end":0.12437,"object_to_goal_dist_start":0.25751,"object_z_max":0.3313,"peak_contact_force":0.07388,"phase_name":"transport_above_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":30037.0,"raw_peak_contact_force":0.13951,"subtask_id":"reach_goal","tcp_end":[0.60525,0.21591,0.34242],"tcp_start":[0.53267,-0.02103,0.213],"tcp_to_object_dist_end":0.01638,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":32.0,"n_steps":329.0,"n_steps_budget":1000.0,"object_pos_end":[0.61499,0.22969,0.20056],"object_pos_start":[0.61652,0.2204,0.33141],"object_to_goal_dist_end":0.00852,"object_to_goal_dist_start":0.12437,"object_z_max":0.33142,"peak_contact_force":0.09429,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":11026.0,"raw_peak_contact_force":0.17524,"subtask_id":"reach_goal","tcp_end":[0.60659,0.22503,0.21603],"tcp_start":[0.60525,0.21591,0.34242],"tcp_to_object_dist_end":0.01822,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.7791,"average_solve_count":421.0,"average_success_count":421.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above.approach_speed":0.13147,"descend_to_grasp.descend_speed":0.02291,"descend_to_place.descend_place_speed":0.06289,"lift_up.lift_height":0.13985,"lift_up.lift_speed":0.02096,"transport_above_goal.transport_speed":0.03024},"optimized_scores":{"best_composite_score":0.55553,"best_fitness_score":0.97553,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":114.0,"contact_point_centroid":[0.54208,-0.02858,-0.00155],"force_p95":0.4579,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.5364,"mean_force":0.20462,"phase_index":3.0,"phase_name":"lift_up","phase_type":"lift","tcp_position_centroid":[0.52922,-0.02839,0.02402]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8546.0,"contact_point_centroid":[0.53391,-0.04767,0.086],"force_p95":0.08439,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26529,"mean_force":0.06049,"phase_index":3.0,"phase_name":"lift_up","phase_type":"lift","tcp_position_centroid":[0.53321,-0.02848,0.08321]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":10513.0,"contact_point_centroid":[0.53446,-0.00952,0.08343],"force_p95":0.08237,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2329,"mean_force":0.05119,"phase_index":3.0,"phase_name":"lift_up","phase_type":"lift","tcp_position_centroid":[0.53306,-0.02847,0.08172]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.54564,-0.0292,-0.00206],"force_p95":0.14424,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.19034,"mean_force":0.12787,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.53169,-0.02845,0.02486]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6258.0,"contact_point_centroid":[0.62391,0.17764,0.25153],"force_p95":0.07797,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15032,"mean_force":0.05458,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.62668,0.15886,0.25048]},{"body_a":"world","body_b":"grasp_target","contact_count":1220.0,"contact_point_centroid":[0.5456,-0.02923,-0.00189],"force_p95":0.13606,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12303,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.51693,-0.0122,0.22434]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5724.0,"contact_point_centroid":[0.63226,0.14047,0.25124],"force_p95":0.0885,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1378,"mean_force":0.05967,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.62662,0.15873,0.25241]},{"body_a":"world","body_b":"grasp_target","contact_count":1580.0,"contact_point_centroid":[0.5456,-0.02923,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.53603,-0.02685,0.08959]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4813.0,"contact_point_centroid":[0.53225,-0.00951,0.02478],"force_p95":0.07328,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11205,"mean_force":0.04455,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.53039,-0.02842,0.02337]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":15461.0,"contact_point_centroid":[0.5841,0.04315,0.22551],"force_p95":0.09283,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10794,"mean_force":0.06431,"phase_index":4.0,"phase_name":"transport_above_goal","phase_type":"approach","tcp_position_centroid":[0.5808,0.06201,0.22418]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4253.0,"contact_point_centroid":[0.53131,-0.04766,0.02598],"force_p95":0.09136,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09347,"mean_force":0.05343,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.53039,-0.02842,0.02338]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":18704.0,"contact_point_centroid":[0.58141,0.08318,0.22781],"force_p95":0.08042,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09331,"mean_force":0.05368,"phase_index":4.0,"phase_name":"transport_above_goal","phase_type":"approach","tcp_position_centroid":[0.58195,0.06438,0.22636]}],"total_contact_groups":12},"final_pose_error":0.00999,"key_states":{"actual_goal_position":[0.63284,0.16493,0.17692],"final_object_position":[0.63884,0.16603,0.1701],"final_tcp_position":[0.62847,0.16277,0.18564],"realised_goal_position":[0.63284,0.16493,0.17692],"realised_object_initial_position":[0.5456,-0.02923,0.03]},"peak_contact_force":57.68882,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":306.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.03],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.25864,"object_z_max":0.03,"peak_contact_force":57.68882,"phase_name":"approach_above","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1220.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_object","tcp_end":[0.53607,-0.02519,0.14701],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.12143,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":395.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1580.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.53938,-0.02863,0.0338],"tcp_start":[0.53607,-0.02519,0.14701],"tcp_to_object_dist_end":0.00998,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54561,-0.02878,0.02577],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26073,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.14441,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10866.0,"raw_peak_contact_force":0.19034,"tcp_end":[0.53036,-0.02842,0.02334],"tcp_start":[0.53938,-0.02863,0.0338],"tcp_to_object_dist_end":0.01545,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":503.0,"n_steps_budget":1000.0,"object_pos_end":[0.55434,-0.02906,0.14377],"object_pos_start":[0.54561,-0.02878,0.02577],"object_to_goal_dist_end":0.21188,"object_to_goal_dist_start":0.26073,"object_z_max":0.14354,"peak_contact_force":0.0832,"phase_name":"lift_up","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":19173.0,"raw_peak_contact_force":0.5364,"tcp_end":[0.54021,-0.02864,0.14637],"tcp_start":[0.53036,-0.02842,0.02334],"tcp_to_object_dist_end":0.01438,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":38.0,"n_steps":987.0,"n_steps_budget":1000.0,"object_pos_end":[0.63938,0.15913,0.29993],"object_pos_start":[0.55434,-0.02906,0.14377],"object_to_goal_dist_end":0.12332,"object_to_goal_dist_start":0.21188,"object_z_max":0.29978,"peak_contact_force":0.07803,"phase_name":"transport_above_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":34165.0,"raw_peak_contact_force":0.10794,"subtask_id":"reach_goal","tcp_end":[0.62664,0.15583,0.31037],"tcp_start":[0.54021,-0.02864,0.14637],"tcp_to_object_dist_end":0.0168,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":29.0,"n_steps":341.0,"n_steps_budget":1000.0,"object_pos_end":[0.63884,0.16603,0.1701],"object_pos_start":[0.63938,0.15913,0.29993],"object_to_goal_dist_end":0.00915,"object_to_goal_dist_start":0.12332,"object_z_max":0.29997,"peak_contact_force":0.10078,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":11982.0,"raw_peak_contact_force":0.15032,"subtask_id":"reach_goal","tcp_end":[0.62847,0.16277,0.18564],"tcp_start":[0.62664,0.15583,0.31037],"tcp_to_object_dist_end":0.01896,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.13694,"average_solve_count":314.0,"average_success_count":314.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above.approach_speed":0.17027,"descend_to_grasp.descend_speed":0.02399,"descend_to_place.descend_place_speed":0.09315,"lift_up.lift_height":0.21699,"lift_up.lift_speed":0.01521,"transport_above_goal.transport_speed":0.13035},"optimized_scores":{"best_composite_score":0.55976,"best_fitness_score":0.97976,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":80.0,"contact_point_centroid":[0.45966,-0.00028,-0.00142],"force_p95":0.52353,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54504,"mean_force":0.25039,"phase_index":3.0,"phase_name":"lift_up","phase_type":"lift","tcp_position_centroid":[0.44921,-0.00031,0.02751]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":14462.0,"contact_point_centroid":[0.4526,-0.01956,0.12402],"force_p95":0.06974,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23764,"mean_force":0.04824,"phase_index":3.0,"phase_name":"lift_up","phase_type":"lift","tcp_position_centroid":[0.45236,-0.00035,0.12224]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":14697.0,"contact_point_centroid":[0.45259,0.01884,0.12505],"force_p95":0.06938,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23743,"mean_force":0.04762,"phase_index":3.0,"phase_name":"lift_up","phase_type":"lift","tcp_position_centroid":[0.45243,-0.00035,0.12337]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":7280.0,"contact_point_centroid":[0.59642,0.16469,0.19891],"force_p95":0.06966,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16548,"mean_force":0.04858,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.59998,0.14609,0.19565]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.46284,-0.00015,-0.00202],"force_p95":0.12959,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.1445,"mean_force":0.12463,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.4513,-0.00027,0.02795]},{"body_a":"world","body_b":"grasp_target","contact_count":1072.0,"contact_point_centroid":[0.46286,-7e-05,-0.00188],"force_p95":0.1365,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12308,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.48254,-5e-05,0.22636]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":7280.0,"contact_point_centroid":[0.60396,0.12726,0.19616],"force_p95":0.07183,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13733,"mean_force":0.04985,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.59998,0.14609,0.19565]},{"body_a":"world","body_b":"grasp_target","contact_count":1656.0,"contact_point_centroid":[0.46286,-7e-05,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.46018,-0.00015,0.09171]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":11857.0,"contact_point_centroid":[0.53088,0.05299,0.24193],"force_p95":0.07077,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11527,"mean_force":0.04922,"phase_index":4.0,"phase_name":"transport_above_goal","phase_type":"approach","tcp_position_centroid":[0.52839,0.072,0.24066]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":11721.0,"contact_point_centroid":[0.52741,0.09172,0.24328],"force_p95":0.07007,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10147,"mean_force":0.04897,"phase_index":4.0,"phase_name":"transport_above_goal","phase_type":"approach","tcp_position_centroid":[0.52913,0.07277,0.24085]},{"body_a":"grasp_target","body_b":"hand","contact_count":95.0,"contact_point_centroid":[0.47816,0.01968,0.07131],"force_p95":0.05491,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09332,"mean_force":0.03023,"phase_index":3.0,"phase_name":"lift_up","phase_type":"lift","tcp_position_centroid":[0.44797,-0.00034,0.04096]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4850.0,"contact_point_centroid":[0.45109,-0.0195,0.02888],"force_p95":0.06671,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08752,"mean_force":0.04482,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.45011,-0.00029,0.02682]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5125.0,"contact_point_centroid":[0.45079,0.01892,0.02854],"force_p95":0.06492,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08385,"mean_force":0.04295,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.45011,-0.00029,0.02683]}],"total_contact_groups":13},"final_pose_error":0.00999,"key_states":{"actual_goal_position":[0.61015,0.15287,0.12219],"final_object_position":[0.60224,0.15068,0.12303],"final_tcp_position":[0.60446,0.15059,0.13008],"realised_goal_position":[0.61015,0.15287,0.12219],"realised_object_initial_position":[0.46286,-7e-05,0.03]},"peak_contact_force":0.54504,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":269.0,"n_steps_budget":1000.0,"object_pos_end":[0.46286,-7e-05,0.02602],"object_pos_start":[0.46286,-7e-05,0.03],"object_to_goal_dist_end":0.2331,"object_to_goal_dist_start":0.23148,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_above","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1072.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_object","tcp_end":[0.46501,-0.00011,0.14983],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.12383,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":414.0,"n_steps_budget":1000.0,"object_pos_end":[0.46286,-7e-05,0.02602],"object_pos_start":[0.46286,-7e-05,0.02602],"object_to_goal_dist_end":0.2331,"object_to_goal_dist_start":0.2331,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1656.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.45836,-0.00015,0.03471],"tcp_start":[0.46501,-0.00011,0.14983],"tcp_to_object_dist_end":0.00978,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":45.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.46271,-0.0003,0.02591],"object_pos_start":[0.46286,-7e-05,0.02602],"object_to_goal_dist_end":0.23338,"object_to_goal_dist_start":0.2331,"object_z_max":0.02602,"peak_contact_force":0.12896,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11775.0,"raw_peak_contact_force":0.1445,"tcp_end":[0.45008,-0.00029,0.02679],"tcp_start":[0.45836,-0.00015,0.03471],"tcp_to_object_dist_end":0.01266,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":675.0,"n_steps_budget":1000.0,"object_pos_end":[0.46998,-0.0004,0.21856],"object_pos_start":[0.46271,-0.0003,0.02591],"object_to_goal_dist_end":0.22897,"object_to_goal_dist_start":0.23338,"object_z_max":0.21829,"peak_contact_force":0.07134,"phase_name":"lift_up","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":29334.0,"raw_peak_contact_force":0.54504,"tcp_end":[0.4589,-0.00035,0.22354],"tcp_start":[0.45008,-0.00029,0.02679],"tcp_to_object_dist_end":0.01214,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":587.0,"n_steps_budget":1000.0,"object_pos_end":[0.59537,0.14207,0.25552],"object_pos_start":[0.46998,-0.0004,0.21856],"object_to_goal_dist_end":0.13459,"object_to_goal_dist_start":0.22897,"object_z_max":0.25548,"peak_contact_force":0.07024,"phase_name":"transport_above_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":23578.0,"raw_peak_contact_force":0.11527,"subtask_id":"reach_goal","tcp_end":[0.59775,0.1423,0.26101],"tcp_start":[0.4589,-0.00035,0.22354],"tcp_to_object_dist_end":0.00598,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":364.0,"n_steps_budget":1000.0,"object_pos_end":[0.60224,0.15068,0.12303],"object_pos_start":[0.59537,0.14207,0.25552],"object_to_goal_dist_end":0.00825,"object_to_goal_dist_start":0.13459,"object_z_max":0.25552,"peak_contact_force":0.07204,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":14560.0,"raw_peak_contact_force":0.16548,"subtask_id":"reach_goal","tcp_end":[0.60446,0.15059,0.13008],"tcp_start":[0.59775,0.1423,0.26101],"tcp_to_object_dist_end":0.00739,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```