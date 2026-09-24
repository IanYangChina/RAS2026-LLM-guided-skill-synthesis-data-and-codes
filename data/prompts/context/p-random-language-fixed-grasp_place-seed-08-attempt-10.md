## Search State

- **Seed**: 8
- **Iteration**: 11 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 10 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 8 | 0.4538 | 1.00 | ❌ rejected |
| 9 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 10 | 0.3538 | 1.00 | ❌ rejected |
| 8 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 8 | 0.4537 | 1.00 | ❌ rejected |
| 7 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 8 | 0.4538 | 1.00 | ❌ rejected |
| 6 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 8 | 0.4539 | 1.00 | ✅ accepted |

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

## Current Skill (Q=0.454) — your mutation base

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

- **Composite score**: 0.454
- **task_score** (E): 1.000
- **fitness_score**: 0.974  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.520

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1273 |
| descend_1 | 1.00 | 1.00 | 0.1371 |
| grasp_1 | 1.00 | 1.00 | 0.0131 |
| lift_1 | 0.67 | 1.00 | 0.1470 |
| transport_1 | 0.33 | 1.00 | 0.2217 |
| descend_2 | 1.00 | 1.00 | 0.1206 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.516, -0.001, 0.181) | (0.522, -0.001, 0.030)→(0.522, -0.001, 0.026) | 0.287→0.289 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.516, -0.001, 0.181)→(0.516, -0.001, 0.044) | (0.522, -0.001, 0.026)→(0.522, -0.001, 0.026) | 0.289→0.289 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_1 | grasp | 1.00 / step_budget | (0.516, -0.001, 0.044)→(0.508, -0.001, 0.035) | (0.522, -0.001, 0.026)→(0.522, -0.001, 0.026) | 0.289→0.290 | 1.00 / 42.667 | 0.145 | 0.180 |
| lift_1 | lift | 0.67 / step_budget | (0.508, -0.001, 0.035)→(0.515, -0.001, 0.181) | (0.522, -0.001, 0.026)→(0.525, -0.001, 0.165) | 0.290→0.232 | 1.00 / 36.667 | 0.087 | 0.589 |
| transport_1 | approach | 0.33 / step_budget | (0.515, -0.001, 0.181)→(0.576, 0.145, 0.325) | (0.525, -0.001, 0.165)→(0.581, 0.147, 0.298) | 0.232→0.119 | 1.00 / 31.000 | 0.099 | 0.395 |
| descend_2 | descend | 1.00 / step_budget | (0.576, 0.145, 0.325)→(0.603, 0.201, 0.228) | (0.581, 0.147, 0.298)→(0.602, 0.203, 0.196) | 0.119→0.012 | 1.00 / 26.333 | 0.111 | 0.371 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.670
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 1.000
- phase_score: 0.340
- phase_breakdown.grasp_1_score: 1.000
- phase_breakdown.transport_arc_score: 0.039
- phase_breakdown.approach_1_score: 0.066
- phase_breakdown.descend_1_score: 0.849
- phase_breakdown.release_1_score: 0.539
- grasp_place_fitness: 0.974

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.974
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 1.000
- **Median Q (composite search score)**: 0.454
- **K-run variance**: 0.0000
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Parameters at lower bound**: descend_1.grasp_z_offset
- **Final σ (mean)**: 0.405


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.02174,"average_solve_count":138.0,"average_success_count":138.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.13396,"descend_1.grasp_z_offset":0.01,"descend_2.descend_z_offset":0.02248,"grasp_1.grasp_retry_x":-0.01396,"grasp_1.grasp_retry_y":-0.01979,"lift_1.lift_height":0.14025,"transport_1.arc_height":0.09301,"transport_1.transport_speed":0.21581},"optimized_scores":{"best_composite_score":0.45341,"best_fitness_score":0.97341,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":144.0,"contact_point_centroid":[0.48008,0.04631,-0.00123],"force_p95":0.33221,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54641,"mean_force":0.07431,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46835,0.04682,0.03795]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":9495.0,"contact_point_centroid":[0.54309,0.1913,0.2878],"force_p95":0.10605,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.4111,"mean_force":0.06947,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.5472,0.17285,0.2878]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":10822.0,"contact_point_centroid":[0.55387,0.15668,0.28465],"force_p95":0.09241,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.36865,"mean_force":0.06157,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.54819,0.17456,0.28643]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":14782.0,"contact_point_centroid":[0.49107,0.04557,0.24821],"force_p95":0.0979,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.34253,"mean_force":0.06695,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.485,0.06354,0.24716]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":12801.0,"contact_point_centroid":[0.47167,0.06615,0.09675],"force_p95":0.08516,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31985,"mean_force":0.05892,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.47186,0.04695,0.09406]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":15966.0,"contact_point_centroid":[0.47374,0.02803,0.09543],"force_p95":0.07884,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29103,"mean_force":0.04862,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.47184,0.04694,0.09385]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":12279.0,"contact_point_centroid":[0.48753,0.08347,0.24962],"force_p95":0.11104,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24365,"mean_force":0.07848,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.48543,0.06427,0.2475]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.48278,0.04868,-0.00215],"force_p95":0.16387,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.22088,"mean_force":0.13361,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47077,0.04708,0.03722]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5195.0,"contact_point_centroid":[0.47119,0.02795,0.03728],"force_p95":0.07133,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1971,"mean_force":0.04175,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46957,0.04696,0.036]},{"body_a":"world","body_b":"grasp_target","contact_count":1660.0,"contact_point_centroid":[0.4827,0.04873,-0.00192],"force_p95":0.13462,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12292,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48965,0.02115,0.23616]},{"body_a":"world","body_b":"grasp_target","contact_count":1612.0,"contact_point_centroid":[0.4827,0.04873,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.47804,0.04555,0.10786]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4226.0,"contact_point_centroid":[0.46941,0.06629,0.03844],"force_p95":0.08742,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09338,"mean_force":0.05202,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46958,0.04696,0.03601]}],"total_contact_groups":12},"final_pose_error":0.00994,"key_states":{"actual_goal_position":[0.58187,0.22885,0.23048],"final_object_position":[0.5699,0.22193,0.21666],"final_tcp_position":[0.5756,0.22199,0.24946],"realised_goal_position":[0.58187,0.22885,0.23048],"realised_object_initial_position":[0.4827,0.04873,0.03]},"peak_contact_force":0.54641,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":416.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.03],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28719,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1660.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.48079,0.04359,0.17215],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.14624,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":403.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1612.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.47787,0.04776,0.04456],"tcp_start":[0.48079,0.04359,0.17215],"tcp_to_object_dist_end":0.01918,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":42.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.48273,0.04776,0.02548],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.29095,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.16086,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11221.0,"raw_peak_contact_force":0.22088,"subtask_id":"grasp_1","tcp_end":[0.46955,0.04696,0.03597],"tcp_start":[0.47787,0.04776,0.04456],"tcp_to_object_dist_end":0.01687,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":753.0,"n_steps_budget":840.0,"object_pos_end":[0.48818,0.04827,0.1381],"object_pos_start":[0.48273,0.04776,0.02548],"object_to_goal_dist_end":0.22344,"object_to_goal_dist_start":0.29095,"object_z_max":0.13799,"peak_contact_force":0.08151,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":28911.0,"raw_peak_contact_force":0.54641,"tcp_end":[0.47825,0.04735,0.15402],"tcp_start":[0.46955,0.04696,0.03597],"tcp_to_object_dist_end":0.01879,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":29.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.52835,0.12522,0.30654],"object_pos_start":[0.48818,0.04827,0.1381],"object_to_goal_dist_end":0.13925,"object_to_goal_dist_start":0.22344,"object_z_max":0.30644,"peak_contact_force":0.09349,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":27061.0,"raw_peak_contact_force":0.34253,"subtask_id":"transport_arc","tcp_end":[0.51987,0.12307,0.33186],"tcp_start":[0.47825,0.04735,0.15402],"tcp_to_object_dist_end":0.02679,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":22.0,"n_steps":643.0,"n_steps_budget":1000.0,"object_pos_end":[0.5699,0.22193,0.21666],"object_pos_start":[0.52835,0.12522,0.30654],"object_to_goal_dist_end":0.01955,"object_to_goal_dist_start":0.13925,"object_z_max":0.30654,"peak_contact_force":0.12975,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":20317.0,"raw_peak_contact_force":0.4111,"subtask_id":"release_1","tcp_end":[0.5756,0.22199,0.24946],"tcp_start":[0.51987,0.12307,0.33186],"tcp_to_object_dist_end":0.03329,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.1338,"average_solve_count":142.0,"average_success_count":142.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.12895,"descend_1.grasp_z_offset":0.01004,"descend_2.descend_z_offset":0.02441,"grasp_1.grasp_retry_x":-0.00725,"grasp_1.grasp_retry_y":-0.00071,"lift_1.lift_height":0.29855,"transport_1.arc_height":0.1436,"transport_1.transport_speed":0.29376},"optimized_scores":{"best_composite_score":0.45396,"best_fitness_score":0.97396,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":143.0,"contact_point_centroid":[0.53384,-0.02076,-0.00112],"force_p95":0.43382,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.60972,"mean_force":0.08691,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52106,-0.02089,0.03562]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":10844.0,"contact_point_centroid":[0.54794,0.01393,0.31276],"force_p95":0.14318,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.54345,"mean_force":0.09033,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.54309,0.03212,0.31305]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3635.0,"contact_point_centroid":[0.59771,0.21655,0.29958],"force_p95":0.1226,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.48024,"mean_force":0.09708,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.59758,0.19726,0.30086]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3823.0,"contact_point_centroid":[0.60849,0.18242,0.29499],"force_p95":0.12561,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.45472,"mean_force":0.0938,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.59786,0.19817,0.2983]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":12175.0,"contact_point_centroid":[0.54509,0.04661,0.31001],"force_p95":0.12772,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.43578,"mean_force":0.0807,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.54173,0.02817,0.31021]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":16987.0,"contact_point_centroid":[0.52344,-0.04013,0.11546],"force_p95":0.08266,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33853,"mean_force":0.05938,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52254,-0.02094,0.11282]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":20266.0,"contact_point_centroid":[0.52424,-0.002,0.11358],"force_p95":0.07687,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.3312,"mean_force":0.05091,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.5225,-0.02094,0.11197]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53702,-0.02136,-0.00203],"force_p95":0.13423,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.15537,"mean_force":0.12561,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.5238,-0.02093,0.03537]},{"body_a":"world","body_b":"grasp_target","contact_count":1816.0,"contact_point_centroid":[0.53702,-0.02132,-0.00192],"force_p95":0.1336,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.1229,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51364,-0.00946,0.23245]},{"body_a":"world","body_b":"grasp_target","contact_count":1476.0,"contact_point_centroid":[0.53702,-0.02132,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.52924,-0.02015,0.10428]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5316.0,"contact_point_centroid":[0.52347,-0.00187,0.03613],"force_p95":0.06885,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10155,"mean_force":0.04096,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52253,-0.02091,0.03392]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4157.0,"contact_point_centroid":[0.5234,-0.0402,0.03665],"force_p95":0.0804,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09487,"mean_force":0.05191,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52253,-0.02091,0.03392]}],"total_contact_groups":12},"final_pose_error":0.00977,"key_states":{"actual_goal_position":[0.61031,0.22775,0.20741],"final_object_position":[0.61021,0.22529,0.20128],"final_tcp_position":[0.60544,0.22123,0.23722],"realised_goal_position":[0.61031,0.22775,0.20741],"realised_object_initial_position":[0.53702,-0.02132,0.03]},"peak_contact_force":0.60972,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":455.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.03],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31446,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1816.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.52987,-0.01933,0.1656],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.13978,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":369.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1476.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.53133,-0.02103,0.04412],"tcp_start":[0.52987,-0.01933,0.1656],"tcp_to_object_dist_end":0.01898,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53691,-0.02127,0.02585],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.3168,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.1342,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11273.0,"raw_peak_contact_force":0.15537,"subtask_id":"grasp_1","tcp_end":[0.5225,-0.02091,0.03388],"tcp_start":[0.53133,-0.02103,0.04412],"tcp_to_object_dist_end":0.0165,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":36.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53661,-0.02163,0.17803],"object_pos_start":[0.53691,-0.02127,0.02585],"object_to_goal_dist_end":0.26171,"object_to_goal_dist_start":0.3168,"object_z_max":0.17784,"peak_contact_force":0.09405,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":37396.0,"raw_peak_contact_force":0.60972,"tcp_end":[0.52712,-0.02104,0.19468],"tcp_start":[0.5225,-0.02091,0.03388],"tcp_to_object_dist_end":0.01918,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":21.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.59551,0.17911,0.32791],"object_pos_start":[0.53661,-0.02163,0.17803],"object_to_goal_dist_end":0.13079,"object_to_goal_dist_start":0.26171,"object_z_max":0.35746,"peak_contact_force":0.13782,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":23019.0,"raw_peak_contact_force":0.54345,"subtask_id":"transport_arc","tcp_end":[0.59202,0.17709,0.36046],"tcp_start":[0.52712,-0.02104,0.19468],"tcp_to_object_dist_end":0.0328,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":18.0,"n_steps":379.0,"n_steps_budget":1000.0,"object_pos_end":[0.61021,0.22529,0.20128],"object_pos_start":[0.59551,0.17911,0.32791],"object_to_goal_dist_end":0.00661,"object_to_goal_dist_start":0.13079,"object_z_max":0.32791,"peak_contact_force":0.11951,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":7458.0,"raw_peak_contact_force":0.48024,"subtask_id":"release_1","tcp_end":[0.60544,0.22123,0.23722],"tcp_start":[0.59202,0.17709,0.36046],"tcp_to_object_dist_end":0.03649,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.01471,"average_solve_count":136.0,"average_success_count":136.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.17215,"descend_1.grasp_z_offset":0.01019,"descend_2.descend_z_offset":0.01395,"grasp_1.grasp_retry_x":0.00499,"grasp_1.grasp_retry_y":0.00467,"lift_1.lift_height":0.21173,"transport_1.arc_height":0.05568,"transport_1.transport_speed":0.25269},"optimized_scores":{"best_composite_score":0.45391,"best_fitness_score":0.97391,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":147.0,"contact_point_centroid":[0.5419,-0.02837,-0.00116],"force_p95":0.44071,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.61215,"mean_force":0.09299,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52969,-0.02857,0.03556]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":17000.0,"contact_point_centroid":[0.53348,-0.04784,0.11592],"force_p95":0.08186,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.3407,"mean_force":0.05881,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.53291,-0.02866,0.11311]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":20319.0,"contact_point_centroid":[0.5346,-0.00971,0.11364],"force_p95":0.07788,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33215,"mean_force":0.05082,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.53284,-0.02866,0.11203]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":17182.0,"contact_point_centroid":[0.57683,0.02935,0.2641],"force_p95":0.08791,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29996,"mean_force":0.05846,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.57398,0.04821,0.26281]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":17714.0,"contact_point_centroid":[0.5717,0.0616,0.2615],"force_p95":0.08171,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25348,"mean_force":0.05625,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.5713,0.04269,0.26023]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4977.0,"contact_point_centroid":[0.61752,0.16519,0.24378],"force_p95":0.08288,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22078,"mean_force":0.05533,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.62024,0.14625,0.24029]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5924.0,"contact_point_centroid":[0.62472,0.12793,0.23976],"force_p95":0.07874,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18962,"mean_force":0.04733,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.62038,0.14656,0.23921]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.54561,-0.02926,-0.00205],"force_p95":0.13878,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.16469,"mean_force":0.12671,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53237,-0.02864,0.0354]},{"body_a":"world","body_b":"grasp_target","contact_count":1468.0,"contact_point_centroid":[0.5456,-0.02923,-0.00191],"force_p95":0.13511,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12296,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51744,-0.01275,0.25249]},{"body_a":"world","body_b":"grasp_target","contact_count":1948.0,"contact_point_centroid":[0.5456,-0.02923,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.53732,-0.02737,0.12476]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5301.0,"contact_point_centroid":[0.53217,-0.00957,0.03606],"force_p95":0.07059,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11826,"mean_force":0.04106,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.5311,-0.02861,0.03391]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4169.0,"contact_point_centroid":[0.53179,-0.0479,0.03673],"force_p95":0.08164,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09315,"mean_force":0.05189,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.5311,-0.02861,0.03392]}],"total_contact_groups":12},"final_pose_error":0.00996,"key_states":{"actual_goal_position":[0.63284,0.16493,0.17692],"final_object_position":[0.62692,0.16104,0.17148],"final_tcp_position":[0.62679,0.15943,0.19656],"realised_goal_position":[0.63284,0.16493,0.17692],"realised_object_initial_position":[0.5456,-0.02923,0.03]},"peak_contact_force":0.61215,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":368.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.03],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.25864,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1468.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.53737,-0.02601,0.20645],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.18065,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":487.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1948.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.53997,-0.02883,0.04442],"tcp_start":[0.53737,-0.02601,0.20645],"tcp_to_object_dist_end":0.01925,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54549,-0.02903,0.0258],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26094,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.13857,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11270.0,"raw_peak_contact_force":0.16469,"subtask_id":"grasp_1","tcp_end":[0.53107,-0.02861,0.03388],"tcp_start":[0.53997,-0.02883,0.04442],"tcp_to_object_dist_end":0.01654,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.54874,-0.02952,0.17929],"object_pos_start":[0.54549,-0.02903,0.0258],"object_to_goal_dist_end":0.21187,"object_to_goal_dist_start":0.26094,"object_z_max":0.17911,"peak_contact_force":0.08403,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":37466.0,"raw_peak_contact_force":0.61215,"tcp_end":[0.53931,-0.02884,0.19552],"tcp_start":[0.53107,-0.02861,0.03388],"tcp_to_object_dist_end":0.01878,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.61836,0.13642,0.259],"object_pos_start":[0.54874,-0.02952,0.17929],"object_to_goal_dist_end":0.08809,"object_to_goal_dist_start":0.21187,"object_z_max":0.26798,"peak_contact_force":0.06711,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":34896.0,"raw_peak_contact_force":0.29996,"subtask_id":"transport_arc","tcp_end":[0.61605,0.13518,0.28262],"tcp_start":[0.53931,-0.02884,0.19552],"tcp_to_object_dist_end":0.02376,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":39.0,"n_steps":260.0,"n_steps_budget":1000.0,"object_pos_end":[0.62692,0.16104,0.17148],"object_pos_start":[0.61836,0.13642,0.259],"object_to_goal_dist_end":0.00894,"object_to_goal_dist_start":0.08809,"object_z_max":0.259,"peak_contact_force":0.08312,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":10901.0,"raw_peak_contact_force":0.22078,"subtask_id":"release_1","tcp_end":[0.62679,0.15943,0.19656],"tcp_start":[0.61605,0.13518,0.28262],"tcp_to_object_dist_end":0.02514,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```