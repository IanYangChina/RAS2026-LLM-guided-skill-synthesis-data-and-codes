## Search State

- **Seed**: 9
- **Iteration**: 6 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 5 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 8 | 0.4576 | 1.00 | ✅ accepted |
| 4 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 8 | 0.0884 | 0.39 | ✅ accepted |
| 3 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | force_threshold_switch | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 9 | -0.3576 | 0.17 | ✅ accepted |
| 2 | rotate → pull → push → descend → descend → grasp → approach | impedance_motion | arc_cartesian | impedance_motion | linear_cartesian | linear_cartesian | — | linear_cartesian | impedance_control | impedance_control | impedance_control | admittance_control | position_control | position_control | position_control | pose_tolerance | time_limit | time_limit | pose_tolerance | contact_detected | grasp_success | pose_tolerance | 6 | -0.1650 | 0.13 | ❌ rejected |
| 1 | rotate → pull → push → descend → descend → grasp → approach | impedance_motion | arc_cartesian | impedance_motion | linear_cartesian | linear_cartesian | — | linear_cartesian | impedance_control | impedance_control | impedance_control | admittance_control | position_control | position_control | position_control | pose_tolerance | time_limit | time_limit | pose_tolerance | contact_detected | grasp_success | pose_tolerance | 6 | -0.1646 | 0.13 | ✅ accepted |

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
| approach_object | 1.00 | 1.00 | 0.1374 |
| descend_to_grasp | 1.00 | 1.00 | 0.1328 |
| grasp | 1.00 | 1.00 | 0.0130 |
| lift | 1.00 | 1.00 | 0.1569 |
| transport_to_goal | 0.33 | 1.00 | 0.2030 |
| descend_to_place | 1.00 | 1.00 | 0.0788 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.511, -0.015, 0.169) | (0.515, -0.017, 0.030)→(0.515, -0.017, 0.026) | 0.268→0.270 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_to_grasp | descend | 1.00 / step_budget | (0.511, -0.015, 0.169)→(0.510, -0.017, 0.036) | (0.515, -0.017, 0.026)→(0.515, -0.017, 0.026) | 0.270→0.270 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp | grasp | 1.00 / step_budget | (0.510, -0.017, 0.036)→(0.501, -0.017, 0.027) | (0.515, -0.017, 0.026)→(0.515, -0.017, 0.026) | 0.270→0.270 | 1.00 / 43.667 | 0.134 | 0.155 |
| lift | lift | 1.00 / step_budget | (0.501, -0.017, 0.027)→(0.509, -0.017, 0.184) | (0.515, -0.017, 0.026)→(0.521, -0.017, 0.176) | 0.270→0.237 | 1.00 / 37.000 | 0.080 | 0.626 |
| transport_to_goal | approach | 0.33 / step_budget | (0.509, -0.017, 0.184)→(0.598, 0.138, 0.254) | (0.521, -0.017, 0.176)→(0.602, 0.140, 0.240) | 0.237→0.091 | 1.00 / 38.667 | 0.073 | 0.123 |
| descend_to_place | descend | 1.00 / step_budget | (0.598, 0.138, 0.254)→(0.611, 0.173, 0.193) | (0.602, 0.140, 0.240)→(0.615, 0.176, 0.178) | 0.091→0.013 | 1.00 / 33.000 | 0.088 | 0.157 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.277
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 1.000
- phase_score: 0.455
- phase_breakdown.place_at_goal_score: 0.646
- phase_breakdown.lift_object_score: 0.343
- phase_breakdown.reach_object_score: 0.149
- grasp_place_fitness: 0.980

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.980
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 1.000
- **Median Q (composite search score)**: 0.457
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.15878,"average_solve_count":296.0,"average_success_count":296.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_height":0.13171,"approach_object.approach_speed":0.06175,"descend_to_grasp.descend_depth":0.00185,"descend_to_place.place_height_z":0.03032,"descend_to_place.place_speed":0.06409,"lift.lift_height":0.21311,"lift.lift_speed":0.02717,"transport_to_goal.transport_speed":0.02526},"optimized_scores":{"best_composite_score":0.45693,"best_fitness_score":0.97693,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":120.0,"contact_point_centroid":[0.53317,-0.02076,-0.00131],"force_p95":0.48624,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.52595,"mean_force":0.14375,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52114,-0.02091,0.02694]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":17116.0,"contact_point_centroid":[0.52458,-0.04016,0.10999],"force_p95":0.08134,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23775,"mean_force":0.05857,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52408,-0.02098,0.1072]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":20489.0,"contact_point_centroid":[0.52543,-0.002,0.10786],"force_p95":0.07666,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23389,"mean_force":0.05056,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52401,-0.02098,0.10613]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53701,-0.02134,-0.00203],"force_p95":0.13425,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.15326,"mean_force":0.12549,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.52367,-0.02094,0.02732]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3873.0,"contact_point_centroid":[0.58819,0.19661,0.25503],"force_p95":0.09472,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14562,"mean_force":0.06989,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.59083,0.17762,0.25339]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5017.0,"contact_point_centroid":[0.59754,0.16091,0.25144],"force_p95":0.08771,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14098,"mean_force":0.05703,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.5911,0.17859,0.25274]},{"body_a":"world","body_b":"grasp_target","contact_count":1912.0,"contact_point_centroid":[0.53702,-0.02132,-0.00193],"force_p95":0.13329,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12288,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.51353,-0.00944,0.23378]},{"body_a":"world","body_b":"grasp_target","contact_count":1612.0,"contact_point_centroid":[0.53702,-0.02132,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.52919,-0.02015,0.10158]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":17967.0,"contact_point_centroid":[0.55882,0.04797,0.23328],"force_p95":0.0841,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10761,"mean_force":0.05574,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.55571,0.06678,0.23273]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5313.0,"contact_point_centroid":[0.52337,-0.00188,0.0281],"force_p95":0.06877,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09845,"mean_force":0.04093,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.52239,-0.02092,0.02587]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4157.0,"contact_point_centroid":[0.52331,-0.04022,0.02858],"force_p95":0.08031,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09736,"mean_force":0.05197,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.52239,-0.02092,0.02587]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":18745.0,"contact_point_centroid":[0.55436,0.08423,0.23285],"force_p95":0.07611,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09368,"mean_force":0.05299,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.55522,0.06528,0.23192]}],"total_contact_groups":12},"final_pose_error":0.01483,"key_states":{"actual_goal_position":[0.61031,0.22775,0.20741],"final_object_position":[0.612,0.21941,0.21766],"final_tcp_position":[0.60328,0.2151,0.23453],"realised_goal_position":[0.61031,0.22775,0.20741],"realised_object_initial_position":[0.53702,-0.02132,0.03]},"peak_contact_force":0.52595,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":479.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.03],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31446,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1912.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.52985,-0.01931,0.16822],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.1424,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":403.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1612.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.53131,-0.02105,0.03606],"tcp_start":[0.52985,-0.01931,0.16822],"tcp_to_object_dist_end":0.01156,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53688,-0.02123,0.02586],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31677,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.13424,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11270.0,"raw_peak_contact_force":0.15326,"tcp_end":[0.52236,-0.02092,0.02583],"tcp_start":[0.53131,-0.02105,0.03606],"tcp_to_object_dist_end":0.01453,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.54203,-0.02169,0.18247],"object_pos_start":[0.53688,-0.02123,0.02586],"object_to_goal_dist_end":0.25982,"object_to_goal_dist_start":0.31677,"object_z_max":0.18232,"peak_contact_force":0.08067,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":37725.0,"raw_peak_contact_force":0.52595,"subtask_id":"lift_object","tcp_end":[0.53036,-0.0211,0.19083],"tcp_start":[0.52236,-0.02092,0.02583],"tcp_to_object_dist_end":0.01436,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":38.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.59046,0.14706,0.25945],"object_pos_start":[0.54203,-0.02169,0.18247],"object_to_goal_dist_end":0.09805,"object_to_goal_dist_start":0.25982,"object_z_max":0.25937,"peak_contact_force":0.07193,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":36712.0,"raw_peak_contact_force":0.10761,"subtask_id":"place_at_goal","tcp_end":[0.58102,0.14435,0.27444],"tcp_start":[0.53036,-0.0211,0.19083],"tcp_to_object_dist_end":0.01793,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":30.0,"n_steps":279.0,"n_steps_budget":1000.0,"object_pos_end":[0.612,0.21941,0.21766],"object_pos_start":[0.59046,0.14706,0.25945],"object_to_goal_dist_end":0.01332,"object_to_goal_dist_start":0.09805,"object_z_max":0.25945,"peak_contact_force":0.09435,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":8890.0,"raw_peak_contact_force":0.14562,"subtask_id":"place_at_goal","tcp_end":[0.60328,0.2151,0.23453],"tcp_start":[0.58102,0.14435,0.27444],"tcp_to_object_dist_end":0.01948,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.47727,"average_solve_count":176.0,"average_success_count":176.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_height":0.12063,"approach_object.approach_speed":0.05696,"descend_to_grasp.descend_depth":0.00446,"descend_to_place.place_height_z":0.01923,"descend_to_place.place_speed":0.04326,"lift.lift_height":0.11479,"lift.lift_speed":0.10347,"transport_to_goal.transport_speed":0.14908},"optimized_scores":{"best_composite_score":0.45638,"best_fitness_score":0.97638,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":100.0,"contact_point_centroid":[0.5424,-0.02847,-0.00128],"force_p95":0.4839,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.69884,"mean_force":0.11134,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52982,-0.02858,0.0294]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":9044.0,"contact_point_centroid":[0.53428,-0.04785,0.08003],"force_p95":0.08312,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33762,"mean_force":0.05973,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.53362,-0.02866,0.07723]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":10915.0,"contact_point_centroid":[0.53513,-0.0097,0.07796],"force_p95":0.07962,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33113,"mean_force":0.0513,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.53352,-0.02866,0.0763]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.54561,-0.02923,-0.00205],"force_p95":0.13908,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.16758,"mean_force":0.12674,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.53207,-0.02864,0.0295]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":15633.0,"contact_point_centroid":[0.5775,0.03061,0.19033],"force_p95":0.09239,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14273,"mean_force":0.06384,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.5744,0.04949,0.18896]},{"body_a":"world","body_b":"grasp_target","contact_count":2196.0,"contact_point_centroid":[0.5456,-0.02923,-0.00194],"force_p95":0.13205,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12285,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.51756,-0.01315,0.22761]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2543.0,"contact_point_centroid":[0.61587,0.15785,0.23181],"force_p95":0.08691,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13057,"mean_force":0.06267,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.61693,0.13883,0.22933]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2483.0,"contact_point_centroid":[0.62352,0.12071,0.22985],"force_p95":0.09495,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1239,"mean_force":0.06521,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.61689,0.13872,0.22957]},{"body_a":"world","body_b":"grasp_target","contact_count":1436.0,"contact_point_centroid":[0.5456,-0.02923,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.53745,-0.02774,0.097]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":18427.0,"contact_point_centroid":[0.57468,0.0688,0.1907],"force_p95":0.08266,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1209,"mean_force":0.05455,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.57463,0.04996,0.18937]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5295.0,"contact_point_centroid":[0.53194,-0.00957,0.03024],"force_p95":0.07041,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11123,"mean_force":0.04103,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.53078,-0.0286,0.02801]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4173.0,"contact_point_centroid":[0.5316,-0.04791,0.0308],"force_p95":0.08172,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09135,"mean_force":0.05195,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.53079,-0.0286,0.02802]}],"total_contact_groups":12},"final_pose_error":0.01494,"key_states":{"actual_goal_position":[0.63284,0.16493,0.17692],"final_object_position":[0.635,0.15781,0.18621],"final_tcp_position":[0.6244,0.15443,0.20261],"realised_goal_position":[0.63284,0.16493,0.17692],"realised_object_initial_position":[0.5456,-0.02923,0.03]},"peak_contact_force":0.69884,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":550.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.03],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.25864,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2196.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.53796,-0.02675,0.15654],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.13077,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":359.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1436.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.53974,-0.02882,0.03849],"tcp_start":[0.53796,-0.02675,0.15654],"tcp_to_object_dist_end":0.01379,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54547,-0.02897,0.02581],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26089,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.13883,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11268.0,"raw_peak_contact_force":0.16758,"tcp_end":[0.53075,-0.0286,0.02798],"tcp_start":[0.53974,-0.02882,0.03849],"tcp_to_object_dist_end":0.01488,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":532.0,"n_steps_budget":690.0,"object_pos_end":[0.55358,-0.02941,0.11967],"object_pos_start":[0.54547,-0.02897,0.02581],"object_to_goal_dist_end":0.21755,"object_to_goal_dist_start":0.26089,"object_z_max":0.11953,"peak_contact_force":0.08,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":20059.0,"raw_peak_contact_force":0.69884,"subtask_id":"lift_object","tcp_end":[0.54024,-0.02882,0.12668],"tcp_start":[0.53075,-0.0286,0.02798],"tcp_to_object_dist_end":0.01509,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":38.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.62192,0.12833,0.24012],"object_pos_start":[0.55358,-0.02941,0.11967],"object_to_goal_dist_end":0.07384,"object_to_goal_dist_start":0.21755,"object_z_max":0.24001,"peak_contact_force":0.0737,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":34060.0,"raw_peak_contact_force":0.14273,"subtask_id":"place_at_goal","tcp_end":[0.61148,0.12571,0.25491],"tcp_start":[0.54024,-0.02882,0.12668],"tcp_to_object_dist_end":0.01829,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":29.0,"n_steps":162.0,"n_steps_budget":1000.0,"object_pos_end":[0.635,0.15781,0.18621],"object_pos_start":[0.62192,0.12833,0.24012],"object_to_goal_dist_end":0.0119,"object_to_goal_dist_start":0.07384,"object_z_max":0.24015,"peak_contact_force":0.09311,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":5026.0,"raw_peak_contact_force":0.13057,"subtask_id":"place_at_goal","tcp_end":[0.6244,0.15443,0.20261],"tcp_start":[0.61148,0.12571,0.25491],"tcp_to_object_dist_end":0.01981,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.57534,"average_solve_count":219.0,"average_success_count":219.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_height":0.14324,"approach_object.approach_speed":0.10223,"descend_to_grasp.descend_depth":6e-05,"descend_to_place.place_height_z":0.00744,"descend_to_place.place_speed":0.05065,"lift.lift_height":0.24849,"lift.lift_speed":0.06354,"transport_to_goal.transport_speed":0.09861},"optimized_scores":{"best_composite_score":0.45962,"best_fitness_score":0.97962,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":91.0,"contact_point_centroid":[0.4589,-0.00049,-0.00124],"force_p95":0.5334,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.65276,"mean_force":0.14505,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.44907,-0.00031,0.0283]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":20396.0,"contact_point_centroid":[0.45227,-0.0195,0.13103],"force_p95":0.07204,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28842,"mean_force":0.04992,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.45175,-0.00034,0.12889]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":20462.0,"contact_point_centroid":[0.45212,0.01881,0.12919],"force_p95":0.07225,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28694,"mean_force":0.04982,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.45165,-0.00034,0.12715]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4200.0,"contact_point_centroid":[0.59735,0.16612,0.19268],"force_p95":0.07211,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1963,"mean_force":0.04945,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.60138,0.14758,0.18965]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4200.0,"contact_point_centroid":[0.60528,0.12875,0.19041],"force_p95":0.07331,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16162,"mean_force":0.05029,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.60138,0.14758,0.18965]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.46284,-0.00015,-0.00202],"force_p95":0.12959,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.14447,"mean_force":0.12463,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.45122,-0.00027,0.02813]},{"body_a":"world","body_b":"grasp_target","contact_count":1404.0,"contact_point_centroid":[0.46286,-7e-05,-0.0019],"force_p95":0.1356,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12297,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.48162,-6e-05,0.24218]},{"body_a":"world","body_b":"grasp_target","contact_count":1892.0,"contact_point_centroid":[0.46286,-7e-05,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.45971,-0.00014,0.10826]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":16573.0,"contact_point_centroid":[0.53301,0.05622,0.23314],"force_p95":0.07171,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11896,"mean_force":0.04977,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.53058,0.07523,0.23167]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":16552.0,"contact_point_centroid":[0.52856,0.09425,0.23403],"force_p95":0.07055,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10958,"mean_force":0.04933,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.53069,0.07534,0.23167]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4850.0,"contact_point_centroid":[0.45103,-0.0195,0.02907],"force_p95":0.06672,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0876,"mean_force":0.04482,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.45003,-0.00029,0.02701]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5125.0,"contact_point_centroid":[0.45072,0.01892,0.02873],"force_p95":0.06493,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08383,"mean_force":0.04295,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.45003,-0.00029,0.02701]}],"total_contact_groups":12},"final_pose_error":0.01491,"key_states":{"actual_goal_position":[0.61015,0.15287,0.12219],"final_object_position":[0.59828,0.14995,0.1299],"final_tcp_position":[0.6043,0.15039,0.14312],"realised_goal_position":[0.61015,0.15287,0.12219],"realised_object_initial_position":[0.46286,-7e-05,0.03]},"peak_contact_force":0.65276,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":352.0,"n_steps_budget":1000.0,"object_pos_end":[0.46286,-7e-05,0.02602],"object_pos_start":[0.46286,-7e-05,0.03],"object_to_goal_dist_end":0.2331,"object_to_goal_dist_start":0.23148,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1404.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.4637,-0.0001,0.18294],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.15692,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":473.0,"n_steps_budget":1000.0,"object_pos_end":[0.46286,-7e-05,0.02602],"object_pos_start":[0.46286,-7e-05,0.02602],"object_to_goal_dist_end":0.2331,"object_to_goal_dist_start":0.2331,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1892.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.4583,-0.00015,0.03491],"tcp_start":[0.4637,-0.0001,0.18294],"tcp_to_object_dist_end":0.00999,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":45.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.46271,-0.0003,0.02591],"object_pos_start":[0.46286,-7e-05,0.02602],"object_to_goal_dist_end":0.23338,"object_to_goal_dist_start":0.2331,"object_z_max":0.02602,"peak_contact_force":0.12897,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11775.0,"raw_peak_contact_force":0.14447,"tcp_end":[0.45,-0.00029,0.02698],"tcp_start":[0.4583,-0.00015,0.03491],"tcp_to_object_dist_end":0.01276,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.46882,-0.00035,0.22623],"object_pos_start":[0.46271,-0.0003,0.02591],"object_to_goal_dist_end":0.23297,"object_to_goal_dist_start":0.23338,"object_z_max":0.22603,"peak_contact_force":0.08022,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":40949.0,"raw_peak_contact_force":0.65276,"subtask_id":"lift_object","tcp_end":[0.45777,-0.00033,0.23327],"tcp_start":[0.45,-0.00029,0.02698],"tcp_to_object_dist_end":0.0131,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":830.0,"n_steps_budget":1000.0,"object_pos_end":[0.59282,0.14425,0.22148],"object_pos_start":[0.46882,-0.00035,0.22623],"object_to_goal_dist_end":0.10116,"object_to_goal_dist_start":0.23297,"object_z_max":0.22639,"peak_contact_force":0.07294,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":33125.0,"raw_peak_contact_force":0.11896,"subtask_id":"place_at_goal","tcp_end":[0.60029,0.14531,0.23391],"tcp_start":[0.45777,-0.00033,0.23327],"tcp_to_object_dist_end":0.01454,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":210.0,"n_steps_budget":1000.0,"object_pos_end":[0.59828,0.14995,0.1299],"object_pos_start":[0.59282,0.14425,0.22148],"object_to_goal_dist_end":0.01445,"object_to_goal_dist_start":0.10116,"object_z_max":0.22148,"peak_contact_force":0.07568,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":8400.0,"raw_peak_contact_force":0.1963,"subtask_id":"place_at_goal","tcp_end":[0.6043,0.15039,0.14312],"tcp_start":[0.60029,0.14531,0.23391],"tcp_to_object_dist_end":0.01453,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```