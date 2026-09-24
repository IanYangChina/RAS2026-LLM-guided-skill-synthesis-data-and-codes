## Search State

- **Seed**: 8
- **Iteration**: 13 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 12 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 5 | 0.5823 | 0.96 | ❌ rejected |
| 11 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 8 | 0.4536 | 1.00 | ❌ rejected |
| 10 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 8 | 0.4538 | 1.00 | ❌ rejected |
| 9 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 10 | 0.3538 | 1.00 | ❌ rejected |
| 8 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 8 | 0.4537 | 1.00 | ❌ rejected |

**Proposal policy**: task_score is near-perfect (0.96). Preserve useful working parts and make only evidence-backed refinements. A HOLD is acceptable if you genuinely cannot find a better structure.

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
- Frozen realised-scene SHA-256: `f44a4a1356de6cb8b5dec75995af4354e38cafd01c85526c1c2a33c8dd2e5b1c`
- Frozen object start: [0.48269722766055606, 0.048727684333792556, 0.03]
- Frozen task target: [0.5818710838485517, 0.2288548935820029, 0.2304844767544324]
- Goal object position: (0.5818710838485517, 0.2288548935820029, 0.2304844767544324)
- place_goal_position (task success criterion — final object 3D position must be close to the realised airborne target here): (0.5818710838485517, 0.2288548935820029, 0.2304844767544324)
- Grasp/lift components are optimiser fitness diagnostics only; canonical task_score is final object-to-realised-target proximity.
- Object initial pose: (0.48269722766055606, 0.048727684333792556, 0.03)
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
  frozen_object_start: [0.4827, 0.0487, 0.03]
  frozen_task_target: [0.5819, 0.2289, 0.2305]
  frozen_object_starts: {'grasp_target': [0.48269722766055606, 0.048727684333792556, 0.03]}
  frozen_targets: {'place_target': [0.5818710838485517, 0.2288548935820029, 0.2304844767544324]}
  goal_tolerance_m: 0.02
  force_limit_n: 20
  force_scale_n: 5
  realized_scene_sha256: f44a4a1356de6cb8b5dec75995af4354e38cafd01c85526c1c2a33c8dd2e5b1c

## Subtask Layer

**Mode**: fixed (subtask targets are defined by the task configuration)

Available subtask IDs for phase binding:
| Subtask ID | Anchor | Target offset (m) | Metric | CMA-ES offset param |
|---|---|---|---|---|
| approach_1 | object | (0.00, 0.00, 0.00) | distance | approach_height |
| descend_1 | object | (0.00, 0.00, 0.02) | distance | grasp_z_offset |
| grasp_1 | object | (0.00, 0.00, 0.02) | contact | — |
| transport_arc | goal | (0.00, 0.00, 0.00) | distance | — |
| release_1 | goal | (0.00, 0.00, 0.00) | distance | — |

Annotate phases with `subtask_id: <id>` to bind them to a subtask target.
- A phase bound to a subtask receives a navigation waypoint computed from that subtask's anchor and offset.
- Only the **last phase** bound to a given subtask is used for subtask scoring.
- Phases without `subtask_id` are not scored against subtasks but still execute normally.

## Current Skill (Q=0.582) — your mutation base

```yaml
skill: grasp_place
dsl_version: 2
skill_type: arm_gripper
subtasks:
- id: approach_1
  anchor: object
- id: descend_1
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.02
- id: grasp_1
  anchor: object
  metric: contact
- id: transport_arc
- id: release_1
phases:
- id: approach_1
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
  parameters:
    approach_height:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.1
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: approach_1
- id: descend_1
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
    - 0.02
  parameters:
    grasp_z_offset:
      type: scalar
      range:
      - 0.01
      - 0.05
      default: 0.02
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: descend_1
- id: grasp_1
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
  parameters:
    grasp_retry_x:
      type: scalar
      range:
      - -0.02
      - 0.02
      default: 0.0
      binds_to:
      - path: retry.offset.x
        mode: replace
    grasp_retry_y:
      type: scalar
      range:
      - -0.02
      - 0.02
      default: 0.0
      binds_to:
      - path: retry.offset.y
        mode: replace
  guards:
  - id: grasp_check
    when: after_phase
    predicate: bilateral_grasp
    threshold: 0.8
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.0
    - 0.0
    - 0.0
  subtask_id: grasp_1
- id: lift_1
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
    - 0.15
  parameters:
    lift_height:
      type: scalar
      range:
      - 0.1
      - 0.3
      default: 0.15
      binds_to:
      - path: target.offset.z
        mode: replace
- id: transport_1
  type: approach
  generator: arc_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    entity: place_target
    offset:
    - 0.0
    - 0.0
    - 0.1
  parameters:
    arc_height:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.1
      binds_to:
      - path: generator.arc_height
        mode: replace
    transport_speed:
      type: scalar
      range:
      - 0.05
      - 0.3
      default: 0.15
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: transport_arc
- id: descend_2
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
  parameters:
    descend_z_offset:
      type: scalar
      range:
      - -0.02
      - 0.06
      default: 0.02
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: release_1

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.1]
  - parameter_bindings:
    - approach_height: status=consumed; consumers=target.offset.z (replace)
- **descend_1** (`descend`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.02]
  - parameter_bindings:
    - grasp_z_offset: status=consumed; consumers=target.offset.z (replace)
- **grasp_1** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings:
    - grasp_retry_x: status=consumed; consumers=retry.offset.x (replace)
    - grasp_retry_y: status=consumed; consumers=retry.offset.y (replace)
  - guards:
    - id=grasp_check, when=after_phase, predicate=bilateral_grasp, on_failure=retry, threshold=0.8
  - retries: max_attempts=2, strategy=offset_target, offset=[0.0, 0.0, 0.0]
- **lift_1** (`lift`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.15]
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset.z (replace)
- **transport_1** (`approach`)
  - target: source=yaml, anchor=task_goal, entity=place_target, offset=[0.0, 0.0, 0.1]
  - parameter_bindings:
    - arc_height: status=consumed; consumers=generator.arc_height (replace)
    - transport_speed: status=consumed; consumers=generator.speed (replace)
- **descend_2** (`descend`)
  - target: source=yaml, anchor=task_goal, entity=place_target, offset=[0.0, 0.0, 0.02]
  - parameter_bindings:
    - descend_z_offset: status=consumed; consumers=target.offset.z (replace)

## Design Metrics

- **Composite score**: 0.582
- **task_score** (E): 0.957
- **fitness_score**: 0.952  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.370

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1131 |
| descend_1 | 1.00 | 1.00 | 0.1516 |
| grasp_1 | 1.00 | 1.00 | 0.0131 |
| lift_1 | 0.67 | 1.00 | 0.1612 |
| transport_1 | 0.33 | 1.00 | 0.1974 |
| descend_2 | 1.00 | 1.00 | 0.1256 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.516, -0.001, 0.196) | (0.522, -0.001, 0.030)→(0.522, -0.001, 0.026) | 0.287→0.289 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.516, -0.001, 0.196)→(0.516, -0.001, 0.045) | (0.522, -0.001, 0.026)→(0.522, -0.001, 0.026) | 0.289→0.289 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_1 | grasp | 1.00 / step_budget | (0.516, -0.001, 0.045)→(0.508, -0.001, 0.035) | (0.522, -0.001, 0.026)→(0.522, -0.001, 0.026) | 0.289→0.290 | 1.00 / 43.000 | 0.145 | 0.180 |
| lift_1 | lift | 0.67 / step_budget | (0.508, -0.001, 0.035)→(0.516, -0.001, 0.196) | (0.522, -0.001, 0.026)→(0.525, -0.001, 0.179) | 0.290→0.227 | 1.00 / 35.333 | 0.092 | 0.587 |
| transport_1 | approach | 0.33 / step_budget | (0.516, -0.001, 0.196)→(0.579, 0.136, 0.321) | (0.525, -0.001, 0.179)→(0.582, 0.137, 0.293) | 0.227→0.124 | 1.00 / 31.333 | 0.099 | 0.379 |
| descend_2 | descend | 1.00 / step_budget | (0.579, 0.136, 0.321)→(0.603, 0.201, 0.227) | (0.582, 0.137, 0.293)→(0.600, 0.202, 0.193) | 0.124→0.016 | 1.00 / 22.000 | 0.124 | 0.338 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.576
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 1.000
- phase_score: 0.361
- phase_breakdown.grasp_1_score: 1.000
- phase_breakdown.transport_arc_score: 0.070
- phase_breakdown.approach_1_score: 0.040
- phase_breakdown.descend_1_score: 0.847
- phase_breakdown.release_1_score: 0.575
- grasp_place_fitness: 0.974

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.974
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 1.000
- **Median Q (composite search score)**: 0.604
- **K-run variance**: 0.0009
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Parameters at lower bound**: descend_1.grasp_z_offset
- **Final σ (mean)**: 0.467


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `2cbd02033d1f1347f2ac2d0b012406a96501e6b48f5b172bd88b34d6c745630c`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.05,0.05],"goal_z_delta":0.15,"object_xy_delta":[0.05,0.05]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `5745d7c2d025a63f908a4bf0f58182445bb06541d436718f39304ac5569d60c0`; realized-scene SHA-256: `f44a4a1356de6cb8b5dec75995af4354e38cafd01c85526c1c2a33c8dd2e5b1c`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.4827,0.04873,0.03]},{"name":"goal","value":[0.58187,0.22885,0.23048]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.4827,0.04873,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.58187,0.22885,0.23048]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.13669,"average_solve_count":139.0,"average_success_count":139.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.17006,"descend_1.grasp_z_offset":0.01,"lift_1.lift_height":0.20934,"transport_1.arc_height":0.16055,"transport_1.transport_speed":0.24938},"optimized_scores":{"best_composite_score":0.60357,"best_fitness_score":0.97357,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":140.0,"contact_point_centroid":[0.48004,0.04625,-0.00123],"force_p95":0.30754,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55883,"mean_force":0.07144,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46835,0.04681,0.03794]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":16601.0,"contact_point_centroid":[0.50557,0.07226,0.30339],"force_p95":0.09543,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.42079,"mean_force":0.06159,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.50022,0.09038,0.303]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":13975.0,"contact_point_centroid":[0.50139,0.11159,0.30596],"force_p95":0.10962,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33556,"mean_force":0.0714,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.50152,0.09259,0.30451]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4515.0,"contact_point_centroid":[0.56664,0.1816,0.30571],"force_p95":0.13814,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32985,"mean_force":0.07542,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.56273,0.19974,0.30918]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":17000.0,"contact_point_centroid":[0.47131,0.06613,0.11935],"force_p95":0.0847,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32474,"mean_force":0.05865,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.47134,0.04692,0.11664]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3983.0,"contact_point_centroid":[0.55508,0.21708,0.30758],"force_p95":0.13879,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31574,"mean_force":0.08289,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.56272,0.1997,0.30938]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":20835.0,"contact_point_centroid":[0.47344,0.02802,0.11682],"force_p95":0.07903,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29483,"mean_force":0.0493,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.47124,0.04691,0.11528]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.48278,0.04868,-0.00215],"force_p95":0.16393,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.22108,"mean_force":0.13364,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47087,0.04708,0.03717]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5251.0,"contact_point_centroid":[0.47118,0.02795,0.03723],"force_p95":0.07131,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19689,"mean_force":0.04134,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46967,0.04696,0.03596]},{"body_a":"world","body_b":"grasp_target","contact_count":1272.0,"contact_point_centroid":[0.4827,0.04873,-0.0019],"force_p95":0.13583,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12301,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49022,0.02025,0.25401]},{"body_a":"world","body_b":"grasp_target","contact_count":2044.0,"contact_point_centroid":[0.4827,0.04873,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.47856,0.04489,0.12523]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4226.0,"contact_point_centroid":[0.46947,0.06629,0.03837],"force_p95":0.08753,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09347,"mean_force":0.05203,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46968,0.04696,0.03596]}],"total_contact_groups":12},"final_pose_error":0.00988,"key_states":{"actual_goal_position":[0.58187,0.22885,0.23048],"final_object_position":[0.5685,0.22176,0.22024],"final_tcp_position":[0.57583,0.22241,0.2549],"realised_goal_position":[0.58187,0.22885,0.23048],"realised_object_initial_position":[0.4827,0.04873,0.03]},"peak_contact_force":0.55883,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":319.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.03],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28719,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1272.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.4816,0.04224,0.20749],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.18159,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":511.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2044.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.47797,0.04776,0.04451],"tcp_start":[0.4816,0.04224,0.20749],"tcp_to_object_dist_end":0.01911,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.48273,0.04777,0.02548],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.29094,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.16086,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11277.0,"raw_peak_contact_force":0.22108,"subtask_id":"grasp_1","tcp_end":[0.46965,0.04696,0.03593],"tcp_start":[0.47797,0.04776,0.04451],"tcp_to_object_dist_end":0.01676,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.48608,0.04823,0.18101],"object_pos_start":[0.48273,0.04777,0.02548],"object_to_goal_dist_end":0.21036,"object_to_goal_dist_start":0.29094,"object_z_max":0.18081,"peak_contact_force":0.08184,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":37975.0,"raw_peak_contact_force":0.55883,"tcp_end":[0.47723,0.04729,0.19923],"tcp_start":[0.46965,0.04696,0.03593],"tcp_to_object_dist_end":0.02028,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":36.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.55396,0.18468,0.3214],"object_pos_start":[0.48608,0.04823,0.18101],"object_to_goal_dist_end":0.10486,"object_to_goal_dist_start":0.21036,"object_z_max":0.3305,"peak_contact_force":0.07581,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":30576.0,"raw_peak_contact_force":0.42079,"subtask_id":"transport_arc","tcp_end":[0.55465,0.18419,0.35172],"tcp_start":[0.47723,0.04729,0.19923],"tcp_to_object_dist_end":0.03033,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":14.0,"n_steps":332.0,"n_steps_budget":1000.0,"object_pos_end":[0.5685,0.22176,0.22024],"object_pos_start":[0.55396,0.18468,0.3214],"object_to_goal_dist_end":0.01828,"object_to_goal_dist_start":0.10486,"object_z_max":0.3214,"peak_contact_force":0.1697,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":8498.0,"raw_peak_contact_force":0.32985,"subtask_id":"release_1","tcp_end":[0.57583,0.22241,0.2549],"tcp_start":[0.55465,0.18419,0.35172],"tcp_to_object_dist_end":0.03543,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `2b35d39beba75b46a5edd8e67b975c00ef2c88fb75a3753bdd32db5918adf9e2`; realized-scene SHA-256: `0143f6b0f71a2b9dc1b332d50c0ca91b210f169a33e3f94f972cb0659a69dba8`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.53702,-0.02132,0.03]},{"name":"goal","value":[0.61031,0.22775,0.20741]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.53702,-0.02132,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.61031,0.22775,0.20741]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.02027,"average_solve_count":148.0,"average_success_count":148.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.15475,"descend_1.grasp_z_offset":0.01135,"lift_1.lift_height":0.18146,"transport_1.arc_height":0.06475,"transport_1.transport_speed":0.17378},"optimized_scores":{"best_composite_score":0.53928,"best_fitness_score":0.90928,"best_task_score":0.87234},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":142.0,"contact_point_centroid":[0.53394,-0.02091,-0.00111],"force_p95":0.41419,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.58164,"mean_force":0.08618,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52135,-0.0209,0.0369]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":16881.0,"contact_point_centroid":[0.52603,-0.0402,0.11622],"force_p95":0.08122,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33311,"mean_force":0.05868,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52544,-0.02102,0.11345]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":20270.0,"contact_point_centroid":[0.52682,-0.00206,0.11386],"force_p95":0.07602,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32453,"mean_force":0.05042,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52533,-0.02102,0.11216]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":14388.0,"contact_point_centroid":[0.58108,0.17553,0.26028],"force_p95":0.08391,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19876,"mean_force":0.05873,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.58466,0.1569,0.25879]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":16380.0,"contact_point_centroid":[0.58888,0.13662,0.25933],"force_p95":0.07804,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19232,"mean_force":0.05283,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.58404,0.155,0.25986]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":15823.0,"contact_point_centroid":[0.54732,0.00596,0.25903],"force_p95":0.08779,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18034,"mean_force":0.06128,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.54436,0.02478,0.25737]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":16570.0,"contact_point_centroid":[0.54528,0.04199,0.25672],"force_p95":0.08233,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15685,"mean_force":0.0587,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.54381,0.02305,0.25549]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53702,-0.02137,-0.00203],"force_p95":0.13423,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.15549,"mean_force":0.12562,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52392,-0.02094,0.03667]},{"body_a":"world","body_b":"grasp_target","contact_count":1528.0,"contact_point_centroid":[0.53702,-0.02132,-0.00191],"force_p95":0.13468,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12295,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51353,-0.0093,0.24491]},{"body_a":"world","body_b":"grasp_target","contact_count":1760.0,"contact_point_centroid":[0.53702,-0.02132,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.52917,-0.02,0.11744]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5316.0,"contact_point_centroid":[0.52356,-0.00187,0.0374],"force_p95":0.06888,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10205,"mean_force":0.04098,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52266,-0.02092,0.03522]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4156.0,"contact_point_centroid":[0.52347,-0.04021,0.03796],"force_p95":0.08046,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09445,"mean_force":0.0519,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52266,-0.02092,0.03522]}],"total_contact_groups":12},"final_pose_error":0.00997,"key_states":{"actual_goal_position":[0.61031,0.22775,0.20741],"final_object_position":[0.59925,0.22111,0.1915],"final_tcp_position":[0.60527,0.22106,0.22202],"realised_goal_position":[0.61031,0.22775,0.20741],"realised_object_initial_position":[0.53702,-0.02132,0.03]},"peak_contact_force":0.58164,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":383.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.03],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31446,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1528.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.52957,-0.01903,0.1907],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.16487,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":440.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1760.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.53143,-0.02104,0.04542],"tcp_start":[0.52957,-0.01903,0.1907],"tcp_to_object_dist_end":0.0202,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53691,-0.02128,0.02585],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31681,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.13422,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11272.0,"raw_peak_contact_force":0.15549,"subtask_id":"grasp_1","tcp_end":[0.52263,-0.02092,0.03518],"tcp_start":[0.53143,-0.02104,0.04542],"tcp_to_object_dist_end":0.01707,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":993.0,"n_steps_budget":1000.0,"object_pos_end":[0.5421,-0.02175,0.17752],"object_pos_start":[0.53691,-0.02128,0.02585],"object_to_goal_dist_end":0.26039,"object_to_goal_dist_start":0.31681,"object_z_max":0.1774,"peak_contact_force":0.07916,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":37293.0,"raw_peak_contact_force":0.58164,"tcp_end":[0.53277,-0.02119,0.19445],"tcp_start":[0.52263,-0.02092,0.03518],"tcp_to_object_dist_end":0.01934,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":36.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.56984,0.08628,0.28285],"object_pos_start":[0.5421,-0.02175,0.17752],"object_to_goal_dist_end":0.16536,"object_to_goal_dist_start":0.26039,"object_z_max":0.2828,"peak_contact_force":0.07573,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":32393.0,"raw_peak_contact_force":0.18034,"subtask_id":"transport_arc","tcp_end":[0.56356,0.08509,0.30598],"tcp_start":[0.53277,-0.02119,0.19445],"tcp_to_object_dist_end":0.024,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":33.0,"n_steps":832.0,"n_steps_budget":1000.0,"object_pos_end":[0.59925,0.22111,0.1915],"object_pos_start":[0.56984,0.08628,0.28285],"object_to_goal_dist_end":0.02049,"object_to_goal_dist_start":0.16536,"object_z_max":0.28285,"peak_contact_force":0.08163,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":30768.0,"raw_peak_contact_force":0.19876,"subtask_id":"release_1","tcp_end":[0.60527,0.22106,0.22202],"tcp_start":[0.56356,0.08509,0.30598],"tcp_to_object_dist_end":0.03111,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `530652a2467d9ac78fab654e7ed7fc5283ca1649270bc8f158e04c16074f9f95`; realized-scene SHA-256: `9bdc6de22965641ffcaccb8421100561fe91fb98e16735236cc25272572d8879`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.5456,-0.02923,0.03]},{"name":"goal","value":[0.63284,0.16493,0.17692]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.5456,-0.02923,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.63284,0.16493,0.17692]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.13768,"average_solve_count":138.0,"average_success_count":138.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.15537,"descend_1.grasp_z_offset":0.01,"lift_1.lift_height":0.2487,"transport_1.arc_height":0.10764,"transport_1.transport_speed":0.27216},"optimized_scores":{"best_composite_score":0.60412,"best_fitness_score":0.97412,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":147.0,"contact_point_centroid":[0.54254,-0.02837,-0.00114],"force_p95":0.42629,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.62051,"mean_force":0.08544,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52955,-0.02857,0.03521]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":9188.0,"contact_point_centroid":[0.56427,0.00173,0.28108],"force_p95":0.16016,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.53544,"mean_force":0.10339,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.55924,0.02015,0.28136]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2832.0,"contact_point_centroid":[0.62253,0.16768,0.25161],"force_p95":0.1388,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.48531,"mean_force":0.09833,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.62149,0.14862,0.25325]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2804.0,"contact_point_centroid":[0.62979,0.13119,0.25355],"force_p95":0.1291,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.44483,"mean_force":0.09865,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.62114,0.14787,0.25669]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":13201.0,"contact_point_centroid":[0.56239,0.0383,0.28279],"force_p95":0.12376,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.4126,"mean_force":0.07738,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.55924,0.02012,0.2826]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":16425.0,"contact_point_centroid":[0.53293,-0.04782,0.11094],"force_p95":0.11336,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.34206,"mean_force":0.06468,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.53167,-0.02863,0.10895]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":20177.0,"contact_point_centroid":[0.53373,-0.01002,0.11275],"force_p95":0.08494,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.3339,"mean_force":0.05046,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.53184,-0.02863,0.11121]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.54561,-0.02926,-0.00205],"force_p95":0.13874,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.16455,"mean_force":0.1267,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53231,-0.02864,0.03499]},{"body_a":"world","body_b":"grasp_target","contact_count":1640.0,"contact_point_centroid":[0.5456,-0.02923,-0.00192],"force_p95":0.13462,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12292,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51747,-0.01291,0.24443]},{"body_a":"world","body_b":"grasp_target","contact_count":1760.0,"contact_point_centroid":[0.5456,-0.02923,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.53736,-0.02751,0.11651]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5300.0,"contact_point_centroid":[0.53212,-0.00957,0.03566],"force_p95":0.07059,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11776,"mean_force":0.04106,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53103,-0.02861,0.03349]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4169.0,"contact_point_centroid":[0.53175,-0.04791,0.0363],"force_p95":0.08167,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0933,"mean_force":0.0519,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53103,-0.02861,0.0335]}],"total_contact_groups":12},"final_pose_error":0.00989,"key_states":{"actual_goal_position":[0.63284,0.16493,0.17692],"final_object_position":[0.63174,0.16345,0.16865],"final_tcp_position":[0.62731,0.16024,0.20364],"realised_goal_position":[0.63284,0.16493,0.17692],"realised_object_initial_position":[0.5456,-0.02923,0.03]},"peak_contact_force":0.62051,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":411.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.03],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.25864,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1640.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.53751,-0.02627,0.19034],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.16455,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":440.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1760.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.5399,-0.02883,0.04399],"tcp_start":[0.53751,-0.02627,0.19034],"tcp_to_object_dist_end":0.01885,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54549,-0.02903,0.0258],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26093,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.13852,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11269.0,"raw_peak_contact_force":0.16455,"subtask_id":"grasp_1","tcp_end":[0.531,-0.02861,0.03346],"tcp_start":[0.5399,-0.02883,0.04399],"tcp_to_object_dist_end":0.01639,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":32.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5481,-0.02903,0.17714],"object_pos_start":[0.54549,-0.02903,0.0258],"object_to_goal_dist_end":0.21167,"object_to_goal_dist_start":0.26093,"object_z_max":0.17696,"peak_contact_force":0.11628,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":36749.0,"raw_peak_contact_force":0.62051,"tcp_end":[0.53734,-0.02878,0.19389],"tcp_start":[0.531,-0.02861,0.03346],"tcp_to_object_dist_end":0.01991,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":22.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.62086,0.14027,0.2741],"object_pos_start":[0.5481,-0.02903,0.17714],"object_to_goal_dist_end":0.10097,"object_to_goal_dist_start":0.21167,"object_z_max":0.30945,"peak_contact_force":0.14584,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":22389.0,"raw_peak_contact_force":0.53544,"subtask_id":"transport_arc","tcp_end":[0.61738,0.13773,0.3061],"tcp_start":[0.53734,-0.02878,0.19389],"tcp_to_object_dist_end":0.03229,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":19.0,"n_steps":293.0,"n_steps_budget":1000.0,"object_pos_end":[0.63174,0.16345,0.16865],"object_pos_start":[0.62086,0.14027,0.2741],"object_to_goal_dist_end":0.00847,"object_to_goal_dist_start":0.10097,"object_z_max":0.2741,"peak_contact_force":0.1207,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":5636.0,"raw_peak_contact_force":0.48531,"subtask_id":"release_1","tcp_end":[0.62731,0.16024,0.20364],"tcp_start":[0.61738,0.13773,0.3061],"tcp_to_object_dist_end":0.03542,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```