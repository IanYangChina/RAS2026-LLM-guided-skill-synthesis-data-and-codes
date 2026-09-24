## Search State

- **Seed**: 9
- **Iteration**: 15 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 14 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 6 | 0.5572 | 1.00 | ❌ rejected |
| 13 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 6 | 0.5572 | 1.00 | ❌ rejected |
| 12 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 6 | 0.5572 | 1.00 | ❌ rejected |
| 11 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 6 | 0.5572 | 1.00 | ❌ rejected |
| 10 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | time_limit | pose_tolerance | 7 | 0.4860 | 0.96 | ❌ rejected |

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
| approach_above | 1.00 | 1.00 | 0.1573 |
| descend_to_grasp | 1.00 | 1.00 | 0.1141 |
| grasp_object | 1.00 | 1.00 | 0.0130 |
| lift_up | 1.00 | 1.00 | 0.1723 |
| transport_above_goal | 1.00 | 1.00 | 0.2461 |
| descend_to_place | 1.00 | 1.00 | 0.1263 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_above | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.510, -0.015, 0.148) | (0.515, -0.017, 0.030)→(0.515, -0.017, 0.026) | 0.268→0.270 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_to_grasp | descend | 1.00 / step_budget | (0.510, -0.015, 0.148)→(0.510, -0.017, 0.034) | (0.515, -0.017, 0.026)→(0.515, -0.017, 0.026) | 0.270→0.270 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_object | grasp | 1.00 / step_budget | (0.510, -0.017, 0.034)→(0.501, -0.016, 0.025) | (0.515, -0.017, 0.026)→(0.515, -0.017, 0.026) | 0.270→0.270 | 1.00 / 42.667 | 0.136 | 0.164 |
| lift_up | lift | 1.00 / step_budget | (0.501, -0.016, 0.025)→(0.511, -0.017, 0.197) | (0.515, -0.017, 0.026)→(0.526, -0.017, 0.189) | 0.270→0.236 | 1.00 / 31.667 | 0.095 | 0.617 |
| transport_above_goal | approach | 1.00 / step_budget | (0.511, -0.017, 0.197)→(0.609, 0.168, 0.303) | (0.526, -0.017, 0.189)→(0.620, 0.172, 0.290) | 0.236→0.121 | 1.00 / 34.000 | 0.105 | 0.198 |
| descend_to_place | descend | 1.00 / step_budget | (0.609, 0.168, 0.303)→(0.613, 0.179, 0.177) | (0.620, 0.172, 0.290)→(0.621, 0.183, 0.159) | 0.121→0.011 | 1.00 / 28.333 | 0.095 | 0.240 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.356
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 1.000
- phase_score: 0.777
- phase_breakdown.approach_object_score: 0.671
- phase_breakdown.reach_goal_score: 0.822
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
- **Final σ (mean)**: 0.269


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.38298,"average_solve_count":235.0,"average_success_count":235.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above.approach_speed":0.12248,"descend_to_grasp.descend_speed":0.04541,"descend_to_place.descend_place_speed":0.061,"lift_up.lift_height":0.13693,"lift_up.lift_speed":0.05865,"transport_above_goal.transport_speed":0.1166},"optimized_scores":{"best_composite_score":0.5562,"best_fitness_score":0.9762,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":89.0,"contact_point_centroid":[0.53409,-0.02065,-0.00136],"force_p95":0.53733,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.65604,"mean_force":0.15924,"phase_index":3.0,"phase_name":"lift_up","phase_type":"lift","tcp_position_centroid":[0.52104,-0.02078,0.02493]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":9393.0,"contact_point_centroid":[0.52636,-0.0019,0.08354],"force_p95":0.07999,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28241,"mean_force":0.05197,"phase_index":3.0,"phase_name":"lift_up","phase_type":"lift","tcp_position_centroid":[0.52475,-0.02087,0.08192]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":7786.0,"contact_point_centroid":[0.52593,-0.04006,0.0857],"force_p95":0.08231,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2806,"mean_force":0.06038,"phase_index":3.0,"phase_name":"lift_up","phase_type":"lift","tcp_position_centroid":[0.52485,-0.02087,0.08306]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5218.0,"contact_point_centroid":[0.5998,0.23441,0.27768],"force_p95":0.08644,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1792,"mean_force":0.06306,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.60378,0.21596,0.2767]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53702,-0.0213,-0.00204],"force_p95":0.13625,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.15861,"mean_force":0.12608,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.52334,-0.02081,0.02522]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4710.0,"contact_point_centroid":[0.61118,0.19834,0.27663],"force_p95":0.0986,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15682,"mean_force":0.07052,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.60374,0.21578,0.27835]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":16094.0,"contact_point_centroid":[0.57115,0.0785,0.23952],"force_p95":0.09249,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14179,"mean_force":0.06301,"phase_index":4.0,"phase_name":"transport_above_goal","phase_type":"approach","tcp_position_centroid":[0.56631,0.09695,0.23855]},{"body_a":"world","body_b":"grasp_target","contact_count":1196.0,"contact_point_centroid":[0.53702,-0.02132,-0.00189],"force_p95":0.13615,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12304,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.5131,-0.00883,0.22505]},{"body_a":"world","body_b":"grasp_target","contact_count":1524.0,"contact_point_centroid":[0.53702,-0.02132,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.52816,-0.01957,0.08975]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":17772.0,"contact_point_centroid":[0.56429,0.1121,0.23706],"force_p95":0.08497,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12152,"mean_force":0.05704,"phase_index":4.0,"phase_name":"transport_above_goal","phase_type":"approach","tcp_position_centroid":[0.56511,0.09325,0.23543]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5297.0,"contact_point_centroid":[0.52313,-0.00175,0.0261],"force_p95":0.06802,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1017,"mean_force":0.04094,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.52205,-0.02079,0.02378]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4172.0,"contact_point_centroid":[0.5231,-0.04009,0.02646],"force_p95":0.07968,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09379,"mean_force":0.052,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.52205,-0.02079,0.02378]}],"total_contact_groups":12},"final_pose_error":0.00982,"key_states":{"actual_goal_position":[0.61031,0.22775,0.20741],"final_object_position":[0.61589,0.22868,0.19894],"final_tcp_position":[0.60623,0.22413,0.21558],"realised_goal_position":[0.61031,0.22775,0.20741],"realised_object_initial_position":[0.53702,-0.02132,0.03]},"peak_contact_force":0.65604,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":300.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.03],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31446,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_above","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1196.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_object","tcp_end":[0.52855,-0.0183,0.14781],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.12212,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":381.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1524.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.53098,-0.0209,0.03393],"tcp_start":[0.52855,-0.0183,0.14781],"tcp_to_object_dist_end":0.00996,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53688,-0.02109,0.02584],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31668,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.13605,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11269.0,"raw_peak_contact_force":0.15861,"tcp_end":[0.52202,-0.02079,0.02374],"tcp_start":[0.53098,-0.0209,0.03393],"tcp_to_object_dist_end":0.01501,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":458.0,"n_steps_budget":1000.0,"object_pos_end":[0.5462,-0.02143,0.1404],"object_pos_start":[0.53688,-0.02109,0.02584],"object_to_goal_dist_end":0.26589,"object_to_goal_dist_start":0.31668,"object_z_max":0.14017,"peak_contact_force":0.07998,"phase_name":"lift_up","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":17268.0,"raw_peak_contact_force":0.65604,"tcp_end":[0.53151,-0.02101,0.14374],"tcp_start":[0.52202,-0.02079,0.02374],"tcp_to_object_dist_end":0.01506,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":38.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.61582,0.2142,0.32286],"object_pos_start":[0.5462,-0.02143,0.1404],"object_to_goal_dist_end":0.11637,"object_to_goal_dist_start":0.26589,"object_z_max":0.32268,"peak_contact_force":0.12004,"phase_name":"transport_above_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":33866.0,"raw_peak_contact_force":0.14179,"subtask_id":"reach_goal","tcp_end":[0.60293,0.20936,0.33382],"tcp_start":[0.53151,-0.02101,0.14374],"tcp_to_object_dist_end":0.0176,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":28.0,"n_steps":335.0,"n_steps_budget":1000.0,"object_pos_end":[0.61589,0.22868,0.19894],"object_pos_start":[0.61582,0.2142,0.32286],"object_to_goal_dist_end":0.01018,"object_to_goal_dist_start":0.11637,"object_z_max":0.32292,"peak_contact_force":0.09381,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":9928.0,"raw_peak_contact_force":0.1792,"subtask_id":"reach_goal","tcp_end":[0.60623,0.22413,0.21558],"tcp_start":[0.60293,0.20936,0.33382],"tcp_to_object_dist_end":0.01977,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.22063,"average_solve_count":349.0,"average_success_count":349.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above.approach_speed":0.11766,"descend_to_grasp.descend_speed":0.04275,"descend_to_place.descend_place_speed":0.03457,"lift_up.lift_height":0.18785,"lift_up.lift_speed":0.01071,"transport_above_goal.transport_speed":0.08725},"optimized_scores":{"best_composite_score":0.55554,"best_fitness_score":0.97554,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":100.0,"contact_point_centroid":[0.5417,-0.02809,-0.00149],"force_p95":0.51086,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.57316,"mean_force":0.21724,"phase_index":3.0,"phase_name":"lift_up","phase_type":"lift","tcp_position_centroid":[0.52926,-0.02839,0.02417]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":11285.0,"contact_point_centroid":[0.53426,-0.04767,0.11028],"force_p95":0.08393,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28501,"mean_force":0.06014,"phase_index":3.0,"phase_name":"lift_up","phase_type":"lift","tcp_position_centroid":[0.53354,-0.02849,0.1075]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":13733.0,"contact_point_centroid":[0.53491,-0.00953,0.10729],"force_p95":0.08117,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24546,"mean_force":0.05129,"phase_index":3.0,"phase_name":"lift_up","phase_type":"lift","tcp_position_centroid":[0.53339,-0.02848,0.10567]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.54564,-0.0292,-0.00206],"force_p95":0.14413,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.1903,"mean_force":0.12784,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.53169,-0.02846,0.02488]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6438.0,"contact_point_centroid":[0.62359,0.17661,0.25254],"force_p95":0.07877,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.171,"mean_force":0.05507,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.62627,0.15792,0.25162]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5404.0,"contact_point_centroid":[0.63212,0.13975,0.24945],"force_p95":0.09577,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16915,"mean_force":0.06479,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.62627,0.15798,0.25047]},{"body_a":"world","body_b":"grasp_target","contact_count":1232.0,"contact_point_centroid":[0.5456,-0.02923,-0.00189],"force_p95":0.13606,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12302,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.51677,-0.01217,0.22449]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":11649.0,"contact_point_centroid":[0.58445,0.04152,0.2496],"force_p95":0.09506,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13248,"mean_force":0.06723,"phase_index":4.0,"phase_name":"transport_above_goal","phase_type":"approach","tcp_position_centroid":[0.58082,0.06031,0.24843]},{"body_a":"world","body_b":"grasp_target","contact_count":1508.0,"contact_point_centroid":[0.5456,-0.02923,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.53613,-0.02688,0.08924]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":14094.0,"contact_point_centroid":[0.58205,0.08188,0.25159],"force_p95":0.08522,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11563,"mean_force":0.05614,"phase_index":4.0,"phase_name":"transport_above_goal","phase_type":"approach","tcp_position_centroid":[0.58214,0.06307,0.25028]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4812.0,"contact_point_centroid":[0.53225,-0.00952,0.0248],"force_p95":0.07331,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11158,"mean_force":0.04456,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.53039,-0.02842,0.02339]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4251.0,"contact_point_centroid":[0.53131,-0.04766,0.026],"force_p95":0.09138,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09345,"mean_force":0.05345,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.53039,-0.02842,0.0234]}],"total_contact_groups":12},"final_pose_error":0.00995,"key_states":{"actual_goal_position":[0.63284,0.16493,0.17692],"final_object_position":[0.63847,0.16582,0.16959],"final_tcp_position":[0.62838,0.16258,0.18549],"realised_goal_position":[0.63284,0.16493,0.17692],"realised_object_initial_position":[0.5456,-0.02923,0.03]},"peak_contact_force":0.57316,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":309.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.03],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.25864,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_above","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1232.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_object","tcp_end":[0.53612,-0.02521,0.1469],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.12132,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":377.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1508.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.53939,-0.02863,0.03383],"tcp_start":[0.53612,-0.02521,0.1469],"tcp_to_object_dist_end":0.01,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54561,-0.02878,0.02577],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26073,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.1443,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10863.0,"raw_peak_contact_force":0.1903,"tcp_end":[0.53036,-0.02842,0.02336],"tcp_start":[0.53939,-0.02863,0.03383],"tcp_to_object_dist_end":0.01545,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":664.0,"n_steps_budget":1000.0,"object_pos_end":[0.55481,-0.02918,0.18962],"object_pos_start":[0.54561,-0.02878,0.02577],"object_to_goal_dist_end":0.20959,"object_to_goal_dist_start":0.26073,"object_z_max":0.18938,"peak_contact_force":0.08173,"phase_name":"lift_up","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":25118.0,"raw_peak_contact_force":0.57316,"tcp_end":[0.54107,-0.02867,0.19418],"tcp_start":[0.53036,-0.02842,0.02336],"tcp_to_object_dist_end":0.01449,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":32.0,"n_steps":778.0,"n_steps_budget":1000.0,"object_pos_end":[0.63909,0.15753,0.30089],"object_pos_start":[0.55481,-0.02918,0.18962],"object_to_goal_dist_end":0.12434,"object_to_goal_dist_start":0.20959,"object_z_max":0.30076,"peak_contact_force":0.099,"phase_name":"transport_above_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":25743.0,"raw_peak_contact_force":0.13248,"subtask_id":"reach_goal","tcp_end":[0.62602,0.15435,0.31141],"tcp_start":[0.54107,-0.02867,0.19418],"tcp_to_object_dist_end":0.01707,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":28.0,"n_steps":356.0,"n_steps_budget":1000.0,"object_pos_end":[0.63847,0.16582,0.16959],"object_pos_start":[0.63909,0.15753,0.30089],"object_to_goal_dist_end":0.00928,"object_to_goal_dist_start":0.12434,"object_z_max":0.30091,"peak_contact_force":0.09857,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":11842.0,"raw_peak_contact_force":0.171,"subtask_id":"reach_goal","tcp_end":[0.62838,0.16258,0.18549],"tcp_start":[0.62602,0.15435,0.31141],"tcp_to_object_dist_end":0.01911,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.18149,"average_solve_count":281.0,"average_success_count":281.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above.approach_speed":0.17341,"descend_to_grasp.descend_speed":0.01007,"descend_to_place.descend_place_speed":0.05813,"lift_up.lift_height":0.24576,"lift_up.lift_speed":0.07678,"transport_above_goal.transport_speed":0.19622},"optimized_scores":{"best_composite_score":0.55976,"best_fitness_score":0.97976,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":74.0,"contact_point_centroid":[0.46042,-0.00027,-0.00133],"force_p95":0.56934,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.62242,"mean_force":0.16009,"phase_index":3.0,"phase_name":"lift_up","phase_type":"lift","tcp_position_centroid":[0.44911,-0.00031,0.02816]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5122.0,"contact_point_centroid":[0.59844,0.16462,0.19876],"force_p95":0.09446,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.3692,"mean_force":0.07301,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.59948,0.14559,0.19623]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6825.0,"contact_point_centroid":[0.54126,0.05986,0.25575],"force_p95":0.12613,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32073,"mean_force":0.07731,"phase_index":4.0,"phase_name":"transport_above_goal","phase_type":"approach","tcp_position_centroid":[0.53438,0.07774,0.25617]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":11214.0,"contact_point_centroid":[0.45468,-0.01931,0.12512],"force_p95":0.10609,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27338,"mean_force":0.066,"phase_index":3.0,"phase_name":"lift_up","phase_type":"lift","tcp_position_centroid":[0.45169,-0.00035,0.12357]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":11651.0,"contact_point_centroid":[0.45436,0.01859,0.12355],"force_p95":0.10636,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27306,"mean_force":0.06378,"phase_index":3.0,"phase_name":"lift_up","phase_type":"lift","tcp_position_centroid":[0.4516,-0.00035,0.12208]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5941.0,"contact_point_centroid":[0.53336,0.09305,0.25683],"force_p95":0.12645,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26122,"mean_force":0.08573,"phase_index":4.0,"phase_name":"transport_above_goal","phase_type":"approach","tcp_position_centroid":[0.53081,0.07412,0.25578]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6643.0,"contact_point_centroid":[0.60598,0.12774,0.1963],"force_p95":0.08219,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23114,"mean_force":0.0589,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.59943,0.14554,0.19707]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.46284,-0.00015,-0.00202],"force_p95":0.12959,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.14446,"mean_force":0.12463,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.45131,-0.00027,0.02803]},{"body_a":"world","body_b":"grasp_target","contact_count":1072.0,"contact_point_centroid":[0.46286,-7e-05,-0.00188],"force_p95":0.1365,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12308,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.48254,-5e-05,0.22636]},{"body_a":"world","body_b":"grasp_target","contact_count":1680.0,"contact_point_centroid":[0.46286,-7e-05,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.46017,-0.00015,0.09182]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4850.0,"contact_point_centroid":[0.4511,-0.0195,0.02896],"force_p95":0.06671,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08756,"mean_force":0.04482,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.45012,-0.00029,0.02691]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5125.0,"contact_point_centroid":[0.45079,0.01892,0.02863],"force_p95":0.06492,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08383,"mean_force":0.04295,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.45012,-0.00029,0.02691]}],"total_contact_groups":12},"final_pose_error":0.00981,"key_states":{"actual_goal_position":[0.61015,0.15287,0.12219],"final_object_position":[0.60927,0.15311,0.10934],"final_tcp_position":[0.60439,0.15052,0.12978],"realised_goal_position":[0.61015,0.15287,0.12219],"realised_object_initial_position":[0.46286,-7e-05,0.03]},"peak_contact_force":0.62242,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":269.0,"n_steps_budget":1000.0,"object_pos_end":[0.46286,-7e-05,0.02602],"object_pos_start":[0.46286,-7e-05,0.03],"object_to_goal_dist_end":0.2331,"object_to_goal_dist_start":0.23148,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_above","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1072.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_object","tcp_end":[0.46501,-0.00011,0.14983],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.12383,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":420.0,"n_steps_budget":1000.0,"object_pos_end":[0.46286,-7e-05,0.02602],"object_pos_start":[0.46286,-7e-05,0.02602],"object_to_goal_dist_end":0.2331,"object_to_goal_dist_start":0.2331,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1680.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.45837,-0.00015,0.03479],"tcp_start":[0.46501,-0.00011,0.14983],"tcp_to_object_dist_end":0.00985,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":45.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.46271,-0.0003,0.02591],"object_pos_start":[0.46286,-7e-05,0.02602],"object_to_goal_dist_end":0.23338,"object_to_goal_dist_start":0.2331,"object_z_max":0.02602,"peak_contact_force":0.12896,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11775.0,"raw_peak_contact_force":0.14446,"tcp_end":[0.45009,-0.00029,0.02688],"tcp_start":[0.45837,-0.00015,0.03479],"tcp_to_object_dist_end":0.01266,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":21.0,"n_steps":716.0,"n_steps_budget":1000.0,"object_pos_end":[0.47766,-0.00027,0.23671],"object_pos_start":[0.46271,-0.0003,0.02591],"object_to_goal_dist_end":0.23264,"object_to_goal_dist_start":0.23338,"object_z_max":0.23645,"peak_contact_force":0.12188,"phase_name":"lift_up","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":22939.0,"raw_peak_contact_force":0.62242,"tcp_end":[0.45918,-0.00035,0.25198],"tcp_start":[0.45009,-0.00029,0.02688],"tcp_to_object_dist_end":0.02398,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":32.0,"n_steps":504.0,"n_steps_budget":1000.0,"object_pos_end":[0.60411,0.14404,0.24534],"object_pos_start":[0.47766,-0.00027,0.23671],"object_to_goal_dist_end":0.12362,"object_to_goal_dist_start":0.23264,"object_z_max":0.24533,"peak_contact_force":0.09533,"phase_name":"transport_above_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":12766.0,"raw_peak_contact_force":0.32073,"subtask_id":"reach_goal","tcp_end":[0.59697,0.14143,0.2627],"tcp_start":[0.45918,-0.00035,0.25198],"tcp_to_object_dist_end":0.01895,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":29.0,"n_steps":394.0,"n_steps_budget":1000.0,"object_pos_end":[0.60927,0.15311,0.10934],"object_pos_start":[0.60411,0.14404,0.24534],"object_to_goal_dist_end":0.01288,"object_to_goal_dist_start":0.12362,"object_z_max":0.24534,"peak_contact_force":0.09401,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":11765.0,"raw_peak_contact_force":0.3692,"subtask_id":"reach_goal","tcp_end":[0.60439,0.15052,0.12978],"tcp_start":[0.59697,0.14143,0.2627],"tcp_to_object_dist_end":0.02117,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```