## Search State

- **Seed**: 9
- **Iteration**: 6 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 5 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 6 | 0.5572 | 1.00 | ✅ accepted |
| 4 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 6 | 0.1876 | 0.38 | ✅ accepted |
| 3 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | force_threshold_switch | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 7 | -0.1922 | 0.17 | ✅ accepted |
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
| descend_to_grasp | 1.00 | 1.00 | 0.1140 |
| grasp_object | 1.00 | 1.00 | 0.0130 |
| lift_up | 1.00 | 1.00 | 0.1382 |
| transport_above_goal | 1.00 | 1.00 | 0.2647 |
| descend_to_place | 1.00 | 1.00 | 0.1270 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_above | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.510, -0.015, 0.148) | (0.515, -0.017, 0.030)→(0.515, -0.017, 0.026) | 0.268→0.270 | 1.00 / 4.000 | 20.858 | 0.138 |
| descend_to_grasp | descend | 1.00 / step_budget | (0.510, -0.015, 0.148)→(0.510, -0.017, 0.034) | (0.515, -0.017, 0.026)→(0.515, -0.017, 0.026) | 0.270→0.270 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_object | grasp | 1.00 / step_budget | (0.510, -0.017, 0.034)→(0.501, -0.016, 0.025) | (0.515, -0.017, 0.026)→(0.515, -0.017, 0.026) | 0.270→0.270 | 1.00 / 42.667 | 0.136 | 0.164 |
| lift_up | lift | 1.00 / step_budget | (0.501, -0.016, 0.025)→(0.510, -0.017, 0.163) | (0.515, -0.017, 0.026)→(0.523, -0.017, 0.160) | 0.270→0.234 | 1.00 / 38.333 | 0.079 | 0.574 |
| transport_above_goal | approach | 1.00 / step_budget | (0.510, -0.017, 0.163)→(0.610, 0.172, 0.304) | (0.523, -0.017, 0.160)→(0.622, 0.176, 0.296) | 0.234→0.127 | 1.00 / 35.333 | 0.089 | 0.130 |
| descend_to_place | descend | 1.00 / step_budget | (0.610, 0.172, 0.304)→(0.613, 0.180, 0.177) | (0.622, 0.176, 0.296)→(0.623, 0.183, 0.164) | 0.127→0.007 | 1.00 / 35.667 | 0.084 | 0.188 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.742
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 1.000
- phase_score: 0.777
- phase_breakdown.approach_object_score: 0.671
- phase_breakdown.reach_goal_score: 0.823
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
- **Final σ (mean)**: 0.318


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.28302,"average_solve_count":318.0,"average_success_count":318.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above.approach_speed":0.16071,"descend_to_grasp.descend_speed":0.03171,"descend_to_place.descend_place_speed":0.04199,"lift_up.lift_height":0.16471,"lift_up.lift_speed":0.0371,"transport_above_goal.transport_speed":0.11065},"optimized_scores":{"best_composite_score":0.55621,"best_fitness_score":0.97621,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":93.0,"contact_point_centroid":[0.53297,-0.02068,-0.00143],"force_p95":0.5545,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.59394,"mean_force":0.22526,"phase_index":3.0,"phase_name":"lift_up","phase_type":"lift","tcp_position_centroid":[0.52102,-0.02078,0.02462]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":9869.0,"contact_point_centroid":[0.5253,-0.04006,0.09869],"force_p95":0.08158,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25416,"mean_force":0.05914,"phase_index":3.0,"phase_name":"lift_up","phase_type":"lift","tcp_position_centroid":[0.52489,-0.02087,0.09591]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":11901.0,"contact_point_centroid":[0.52603,-0.00188,0.09674],"force_p95":0.07801,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25385,"mean_force":0.05083,"phase_index":3.0,"phase_name":"lift_up","phase_type":"lift","tcp_position_centroid":[0.52481,-0.02087,0.09496]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4954.0,"contact_point_centroid":[0.60144,0.23914,0.28646],"force_p95":0.09418,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20873,"mean_force":0.06762,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.60535,0.2205,0.28359]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53702,-0.0213,-0.00204],"force_p95":0.13622,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.15849,"mean_force":0.12607,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.52334,-0.02081,0.02525]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6624.0,"contact_point_centroid":[0.61272,0.20335,0.279],"force_p95":0.07603,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15297,"mean_force":0.05395,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.60537,0.22068,0.28028]},{"body_a":"world","body_b":"grasp_target","contact_count":1144.0,"contact_point_centroid":[0.53702,-0.02132,-0.00188],"force_p95":0.13644,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12305,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.5133,-0.00885,0.22491]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":17254.0,"contact_point_centroid":[0.5646,0.11327,0.25314],"force_p95":0.08616,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13462,"mean_force":0.05689,"phase_index":4.0,"phase_name":"transport_above_goal","phase_type":"approach","tcp_position_centroid":[0.56591,0.09442,0.25115]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":16938.0,"contact_point_centroid":[0.57307,0.08443,0.25836],"force_p95":0.08585,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13156,"mean_force":0.05887,"phase_index":4.0,"phase_name":"transport_above_goal","phase_type":"approach","tcp_position_centroid":[0.56864,0.1029,0.25738]},{"body_a":"world","body_b":"grasp_target","contact_count":1532.0,"contact_point_centroid":[0.53702,-0.02132,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.52814,-0.01959,0.08972]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5297.0,"contact_point_centroid":[0.52313,-0.00176,0.02612],"force_p95":0.06803,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10166,"mean_force":0.04094,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.52205,-0.02079,0.0238]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4171.0,"contact_point_centroid":[0.52309,-0.0401,0.02648],"force_p95":0.07967,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09372,"mean_force":0.05201,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.52205,-0.02079,0.0238]}],"total_contact_groups":12},"final_pose_error":0.00978,"key_states":{"actual_goal_position":[0.61031,0.22775,0.20741],"final_object_position":[0.61603,0.23,0.20087],"final_tcp_position":[0.6066,0.22518,0.21608],"realised_goal_position":[0.61031,0.22775,0.20741],"realised_object_initial_position":[0.53702,-0.02132,0.03]},"peak_contact_force":62.32785,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":287.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.03],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31446,"object_z_max":0.03,"peak_contact_force":62.32785,"phase_name":"approach_above","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1144.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_object","tcp_end":[0.52858,-0.01834,0.14748],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.12179,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":383.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1532.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.53098,-0.0209,0.03396],"tcp_start":[0.52858,-0.01834,0.14748],"tcp_to_object_dist_end":0.00998,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53688,-0.02109,0.02584],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31668,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.13602,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11268.0,"raw_peak_contact_force":0.15849,"tcp_end":[0.52202,-0.02079,0.02376],"tcp_start":[0.53098,-0.0209,0.03396],"tcp_to_object_dist_end":0.015,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":569.0,"n_steps_budget":1000.0,"object_pos_end":[0.54553,-0.02147,0.1679],"object_pos_start":[0.53688,-0.02109,0.02584],"object_to_goal_dist_end":0.26052,"object_to_goal_dist_start":0.31668,"object_z_max":0.16766,"peak_contact_force":0.08054,"phase_name":"lift_up","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":21863.0,"raw_peak_contact_force":0.59394,"tcp_end":[0.532,-0.02102,0.17137],"tcp_start":[0.52202,-0.02079,0.02376],"tcp_to_object_dist_end":0.01398,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":32.0,"n_steps":974.0,"n_steps_budget":1000.0,"object_pos_end":[0.61792,0.22205,0.33154],"object_pos_start":[0.54553,-0.02147,0.1679],"object_to_goal_dist_end":0.1245,"object_to_goal_dist_start":0.26052,"object_z_max":0.33141,"peak_contact_force":0.09332,"phase_name":"transport_above_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":34192.0,"raw_peak_contact_force":0.13462,"subtask_id":"reach_goal","tcp_end":[0.60551,0.21711,0.34146],"tcp_start":[0.532,-0.02102,0.17137],"tcp_to_object_dist_end":0.01664,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":30.0,"n_steps":352.0,"n_steps_budget":1000.0,"object_pos_end":[0.61603,0.23,0.20087],"object_pos_start":[0.61792,0.22205,0.33154],"object_to_goal_dist_end":0.00897,"object_to_goal_dist_start":0.1245,"object_z_max":0.33157,"peak_contact_force":0.09534,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":11578.0,"raw_peak_contact_force":0.20873,"subtask_id":"reach_goal","tcp_end":[0.6066,0.22518,0.21608],"tcp_start":[0.60551,0.21711,0.34146],"tcp_to_object_dist_end":0.01853,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.34034,"average_solve_count":238.0,"average_success_count":238.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above.approach_speed":0.12208,"descend_to_grasp.descend_speed":0.03378,"descend_to_place.descend_place_speed":0.05597,"lift_up.lift_height":0.10535,"lift_up.lift_speed":0.04226,"transport_above_goal.transport_speed":0.1976},"optimized_scores":{"best_composite_score":0.55554,"best_fitness_score":0.97554,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":94.0,"contact_point_centroid":[0.54207,-0.02802,-0.00144],"force_p95":0.54057,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.60262,"mean_force":0.20072,"phase_index":3.0,"phase_name":"lift_up","phase_type":"lift","tcp_position_centroid":[0.52946,-0.0284,0.02432]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5999.0,"contact_point_centroid":[0.53382,-0.04769,0.06942],"force_p95":0.08481,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30299,"mean_force":0.06133,"phase_index":3.0,"phase_name":"lift_up","phase_type":"lift","tcp_position_centroid":[0.53313,-0.02848,0.06663]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":7467.0,"contact_point_centroid":[0.53428,-0.00952,0.06742],"force_p95":0.08237,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25796,"mean_force":0.05123,"phase_index":3.0,"phase_name":"lift_up","phase_type":"lift","tcp_position_centroid":[0.53299,-0.02847,0.06561]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.54564,-0.0292,-0.00206],"force_p95":0.14414,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.19032,"mean_force":0.12784,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.53169,-0.02845,0.02488]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":14171.0,"contact_point_centroid":[0.58531,0.04657,0.21167],"force_p95":0.09185,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15442,"mean_force":0.06235,"phase_index":4.0,"phase_name":"transport_above_goal","phase_type":"approach","tcp_position_centroid":[0.58207,0.06547,0.20994]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5421.0,"contact_point_centroid":[0.63165,0.14102,0.24604],"force_p95":0.09387,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14875,"mean_force":0.06455,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.62702,0.15958,0.24683]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":16711.0,"contact_point_centroid":[0.58138,0.08457,0.21207],"force_p95":0.08076,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14211,"mean_force":0.05296,"phase_index":4.0,"phase_name":"transport_above_goal","phase_type":"approach","tcp_position_centroid":[0.58221,0.06577,0.21026]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6717.0,"contact_point_centroid":[0.62356,0.1779,0.25062],"force_p95":0.07687,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13971,"mean_force":0.05229,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.62696,0.15946,0.249]},{"body_a":"world","body_b":"grasp_target","contact_count":1232.0,"contact_point_centroid":[0.5456,-0.02923,-0.00189],"force_p95":0.13606,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12302,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.51685,-0.01219,0.22445]},{"body_a":"world","body_b":"grasp_target","contact_count":1520.0,"contact_point_centroid":[0.5456,-0.02923,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.53611,-0.02687,0.08933]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4812.0,"contact_point_centroid":[0.53225,-0.00952,0.0248],"force_p95":0.0733,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11158,"mean_force":0.04455,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.53039,-0.02842,0.02339]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4251.0,"contact_point_centroid":[0.53131,-0.04766,0.026],"force_p95":0.09138,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09345,"mean_force":0.05345,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.53039,-0.02842,0.0234]}],"total_contact_groups":12},"final_pose_error":0.0097,"key_states":{"actual_goal_position":[0.63284,0.16493,0.17692],"final_object_position":[0.63863,0.16631,0.17236],"final_tcp_position":[0.62851,0.1629,0.18536],"realised_goal_position":[0.63284,0.16493,0.17692],"realised_object_initial_position":[0.5456,-0.02923,0.03]},"peak_contact_force":0.60262,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":309.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.03],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.25864,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_above","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1232.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_object","tcp_end":[0.53611,-0.0252,0.14695],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.12137,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":380.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1520.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.53939,-0.02863,0.03383],"tcp_start":[0.53611,-0.0252,0.14695],"tcp_to_object_dist_end":0.01,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54561,-0.02878,0.02577],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26073,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.14431,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10863.0,"raw_peak_contact_force":0.19032,"tcp_end":[0.53036,-0.02842,0.02336],"tcp_start":[0.53939,-0.02863,0.03383],"tcp_to_object_dist_end":0.01545,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":353.0,"n_steps_budget":1000.0,"object_pos_end":[0.55391,-0.02895,0.11111],"object_pos_start":[0.54561,-0.02878,0.02577],"object_to_goal_dist_end":0.21943,"object_to_goal_dist_start":0.26073,"object_z_max":0.11088,"peak_contact_force":0.08325,"phase_name":"lift_up","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":13560.0,"raw_peak_contact_force":0.60262,"tcp_end":[0.53948,-0.02863,0.11217],"tcp_start":[0.53036,-0.02842,0.02336],"tcp_to_object_dist_end":0.01447,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":856.0,"n_steps_budget":1000.0,"object_pos_end":[0.63909,0.15966,0.30223],"object_pos_start":[0.55391,-0.02895,0.11111],"object_to_goal_dist_end":0.12558,"object_to_goal_dist_start":0.21943,"object_z_max":0.30208,"peak_contact_force":0.09366,"phase_name":"transport_above_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":30882.0,"raw_peak_contact_force":0.15442,"subtask_id":"reach_goal","tcp_end":[0.62707,0.15673,0.30987],"tcp_start":[0.53948,-0.02863,0.11217],"tcp_to_object_dist_end":0.01454,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":38.0,"n_steps":348.0,"n_steps_budget":1000.0,"object_pos_end":[0.63863,0.16631,0.17236],"object_pos_start":[0.63909,0.15966,0.30223],"object_to_goal_dist_end":0.0075,"object_to_goal_dist_start":0.12558,"object_z_max":0.30229,"peak_contact_force":0.07776,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":12138.0,"raw_peak_contact_force":0.14875,"subtask_id":"reach_goal","tcp_end":[0.62851,0.1629,0.18536],"tcp_start":[0.62707,0.15673,0.30987],"tcp_to_object_dist_end":0.01683,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.90047,"average_solve_count":422.0,"average_success_count":422.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above.approach_speed":0.16816,"descend_to_grasp.descend_speed":0.02294,"descend_to_place.descend_place_speed":0.03745,"lift_up.lift_height":0.19758,"lift_up.lift_speed":0.01418,"transport_above_goal.transport_speed":0.04837},"optimized_scores":{"best_composite_score":0.55977,"best_fitness_score":0.97977,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":83.0,"contact_point_centroid":[0.45949,-0.00052,-0.00144],"force_p95":0.50425,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.52515,"mean_force":0.24526,"phase_index":3.0,"phase_name":"lift_up","phase_type":"lift","tcp_position_centroid":[0.4492,-0.00031,0.02749]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":13228.0,"contact_point_centroid":[0.45248,-0.01956,0.11473],"force_p95":0.06913,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2278,"mean_force":0.04792,"phase_index":3.0,"phase_name":"lift_up","phase_type":"lift","tcp_position_centroid":[0.45228,-0.00035,0.11298]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":13374.0,"contact_point_centroid":[0.45246,0.01885,0.11538],"force_p95":0.06917,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22745,"mean_force":0.04752,"phase_index":3.0,"phase_name":"lift_up","phase_type":"lift","tcp_position_centroid":[0.45234,-0.00035,0.11371]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":7273.0,"contact_point_centroid":[0.59666,0.1649,0.19989],"force_p95":0.07713,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20664,"mean_force":0.0528,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.60007,0.14625,0.19643]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8178.0,"contact_point_centroid":[0.60403,0.12769,0.19331],"force_p95":0.07099,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18773,"mean_force":0.04903,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.60022,0.14643,0.19321]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.46284,-0.00015,-0.00202],"force_p95":0.12959,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.14449,"mean_force":0.12463,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.4513,-0.00027,0.02794]},{"body_a":"world","body_b":"grasp_target","contact_count":1072.0,"contact_point_centroid":[0.46286,-7e-05,-0.00188],"force_p95":0.1365,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12308,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.48254,-5e-05,0.22636]},{"body_a":"world","body_b":"grasp_target","contact_count":1672.0,"contact_point_centroid":[0.46286,-7e-05,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.46017,-0.00015,0.09173]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":13990.0,"contact_point_centroid":[0.52969,0.05222,0.23158],"force_p95":0.07452,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09988,"mean_force":0.05084,"phase_index":4.0,"phase_name":"transport_above_goal","phase_type":"approach","tcp_position_centroid":[0.52708,0.07117,0.22994]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":13336.0,"contact_point_centroid":[0.52436,0.0889,0.23244],"force_p95":0.07665,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09492,"mean_force":0.05217,"phase_index":4.0,"phase_name":"transport_above_goal","phase_type":"approach","tcp_position_centroid":[0.52588,0.06994,0.22945]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4850.0,"contact_point_centroid":[0.4511,-0.0195,0.02887],"force_p95":0.06671,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08752,"mean_force":0.04482,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.45012,-0.00029,0.02682]},{"body_a":"grasp_target","body_b":"hand","contact_count":94.0,"contact_point_centroid":[0.47828,0.01968,0.07086],"force_p95":0.05388,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08742,"mean_force":0.02982,"phase_index":3.0,"phase_name":"lift_up","phase_type":"lift","tcp_position_centroid":[0.44805,-0.00034,0.04051]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5125.0,"contact_point_centroid":[0.45079,0.01892,0.02854],"force_p95":0.06492,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08384,"mean_force":0.04295,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.45012,-0.00029,0.02682]}],"total_contact_groups":13},"final_pose_error":0.00974,"key_states":{"actual_goal_position":[0.61015,0.15287,0.12219],"final_object_position":[0.61386,0.15354,0.11865],"final_tcp_position":[0.6045,0.15065,0.12981],"realised_goal_position":[0.61015,0.15287,0.12219],"realised_object_initial_position":[0.46286,-7e-05,0.03]},"peak_contact_force":0.52515,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":269.0,"n_steps_budget":1000.0,"object_pos_end":[0.46286,-7e-05,0.02602],"object_pos_start":[0.46286,-7e-05,0.03],"object_to_goal_dist_end":0.2331,"object_to_goal_dist_start":0.23148,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_above","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1072.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_object","tcp_end":[0.46501,-0.00011,0.14983],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.12383,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":418.0,"n_steps_budget":1000.0,"object_pos_end":[0.46286,-7e-05,0.02602],"object_pos_start":[0.46286,-7e-05,0.02602],"object_to_goal_dist_end":0.2331,"object_to_goal_dist_start":0.2331,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1672.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.45837,-0.00015,0.03471],"tcp_start":[0.46501,-0.00011,0.14983],"tcp_to_object_dist_end":0.00978,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":45.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.46271,-0.0003,0.02591],"object_pos_start":[0.46286,-7e-05,0.02602],"object_to_goal_dist_end":0.23338,"object_to_goal_dist_start":0.2331,"object_z_max":0.02602,"peak_contact_force":0.12896,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11775.0,"raw_peak_contact_force":0.14449,"tcp_end":[0.45009,-0.00029,0.02679],"tcp_start":[0.45837,-0.00015,0.03471],"tcp_to_object_dist_end":0.01266,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":612.0,"n_steps_budget":1000.0,"object_pos_end":[0.46975,-0.0004,0.19951],"object_pos_start":[0.46271,-0.0003,0.02591],"object_to_goal_dist_end":0.22177,"object_to_goal_dist_start":0.23338,"object_z_max":0.19924,"peak_contact_force":0.07189,"phase_name":"lift_up","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":26779.0,"raw_peak_contact_force":0.52515,"tcp_end":[0.45862,-0.00035,0.20397],"tcp_start":[0.45009,-0.00029,0.02679],"tcp_to_object_dist_end":0.01199,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":698.0,"n_steps_budget":1000.0,"object_pos_end":[0.6096,0.14555,0.25337],"object_pos_start":[0.46975,-0.0004,0.19951],"object_to_goal_dist_end":0.13139,"object_to_goal_dist_start":0.22177,"object_z_max":0.2533,"peak_contact_force":0.08,"phase_name":"transport_above_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":27326.0,"raw_peak_contact_force":0.09988,"subtask_id":"reach_goal","tcp_end":[0.59811,0.14274,0.25995],"tcp_start":[0.45862,-0.00035,0.20397],"tcp_to_object_dist_end":0.01353,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":39.0,"n_steps":390.0,"n_steps_budget":1000.0,"object_pos_end":[0.61386,0.15354,0.11865],"object_pos_start":[0.6096,0.14555,0.25337],"object_to_goal_dist_end":0.00517,"object_to_goal_dist_start":0.13139,"object_z_max":0.25337,"peak_contact_force":0.07822,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":15451.0,"raw_peak_contact_force":0.20664,"subtask_id":"reach_goal","tcp_end":[0.6045,0.15065,0.12981],"tcp_start":[0.59811,0.14274,0.25995],"tcp_to_object_dist_end":0.01484,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```