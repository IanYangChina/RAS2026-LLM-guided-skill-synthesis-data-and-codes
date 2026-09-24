## Search State

- **Seed**: 8
- **Iteration**: 10 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 9 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 10 | 0.3538 | 1.00 | ❌ rejected |
| 8 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 8 | 0.4537 | 1.00 | ❌ rejected |
| 7 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 8 | 0.4538 | 1.00 | ❌ rejected |
| 6 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 8 | 0.4539 | 1.00 | ✅ accepted |
| 5 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 7 | 0.1213 | 0.30 | ✅ accepted |

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

## Current Skill (Q=0.354) — your mutation base

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

- **Composite score**: 0.354
- **task_score** (E): 1.000
- **fitness_score**: 0.974  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.620

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1287 |
| descend_1 | 1.00 | 1.00 | 0.1362 |
| grasp_1 | 1.00 | 1.00 | 0.0131 |
| lift_1 | 1.00 | 1.00 | 0.1523 |
| transport_1 | 0.33 | 1.00 | 0.2248 |
| descend_2 | 1.00 | 1.00 | 0.1080 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.516, -0.001, 0.180) | (0.522, -0.001, 0.030)→(0.522, -0.001, 0.026) | 0.287→0.289 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.516, -0.001, 0.180)→(0.516, -0.001, 0.044) | (0.522, -0.001, 0.026)→(0.522, -0.001, 0.026) | 0.289→0.289 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_1 | grasp | 1.00 / step_budget | (0.516, -0.001, 0.044)→(0.508, -0.001, 0.034) | (0.522, -0.001, 0.026)→(0.522, -0.001, 0.026) | 0.289→0.290 | 1.00 / 43.000 | 0.145 | 0.180 |
| lift_1 | lift | 1.00 / step_budget | (0.508, -0.001, 0.034)→(0.517, -0.001, 0.186) | (0.522, -0.001, 0.026)→(0.531, -0.001, 0.177) | 0.290→0.226 | 1.00 / 38.000 | 70.060 | 0.590 |
| transport_1 | approach | 0.33 / step_budget | (0.517, -0.001, 0.186)→(0.590, 0.160, 0.322) | (0.531, -0.001, 0.177)→(0.604, 0.164, 0.308) | 0.226→0.112 | 1.00 / 33.667 | 0.095 | 0.382 |
| descend_2 | descend | 1.00 / step_budget | (0.590, 0.160, 0.322)→(0.603, 0.201, 0.224) | (0.604, 0.164, 0.308)→(0.610, 0.204, 0.204) | 0.112→0.008 | 1.00 / 37.333 | 0.087 | 0.399 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.574
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 1.000
- phase_score: 0.377
- phase_breakdown.grasp_1_score: 1.000
- phase_breakdown.transport_arc_score: 0.107
- phase_breakdown.approach_1_score: 0.030
- phase_breakdown.descend_1_score: 0.850
- phase_breakdown.release_1_score: 0.544
- grasp_place_fitness: 0.974

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.974
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 1.000
- **Median Q (composite search score)**: 0.354
- **K-run variance**: 0.0000
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Parameters at lower bound**: descend_1.grasp_z_offset
- **Final σ (mean)**: 0.321


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.07097,"average_solve_count":155.0,"average_success_count":155.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.16693,"descend_1.grasp_z_offset":0.01004,"descend_2.descend_z_offset":0.00454,"grasp_1.grasp_retry_x":-0.00091,"grasp_1.grasp_retry_y":0.00029,"lift_1.lift_height":0.21423,"lift_1.lift_pose_tolerance":0.04934,"transport_1.arc_height":0.15311,"transport_1.transport_pose_tolerance":0.06041,"transport_1.transport_speed":0.19647},"optimized_scores":{"best_composite_score":0.35343,"best_fitness_score":0.97343,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":60.0,"contact_point_centroid":[0.47946,0.04722,-0.00166],"force_p95":0.48878,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55706,"mean_force":0.28268,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46852,0.04684,0.03716]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6885.0,"contact_point_centroid":[0.57164,0.18272,0.28598],"force_p95":0.11065,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.36678,"mean_force":0.06151,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.56548,0.2006,0.2853]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6139.0,"contact_point_centroid":[0.55974,0.21726,0.29235],"force_p95":0.1101,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.35063,"mean_force":0.0662,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.56479,0.19918,0.28854]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3605.0,"contact_point_centroid":[0.5039,0.06271,0.2858],"force_p95":0.14598,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.34231,"mean_force":0.07342,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.49922,0.08094,0.2836]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3201.0,"contact_point_centroid":[0.47145,0.0662,0.10963],"force_p95":0.09981,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32471,"mean_force":0.06502,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.47206,0.04696,0.10715]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3953.0,"contact_point_centroid":[0.47349,0.02796,0.1086],"force_p95":0.09548,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29479,"mean_force":0.05474,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.47208,0.04696,0.10738]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2831.0,"contact_point_centroid":[0.49958,0.09987,0.28691],"force_p95":0.12875,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26043,"mean_force":0.0809,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.49904,0.08063,0.28363]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.48278,0.04868,-0.00215],"force_p95":0.16385,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.22087,"mean_force":0.13362,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47086,0.04708,0.03731]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5251.0,"contact_point_centroid":[0.47118,0.02795,0.03737],"force_p95":0.07133,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19695,"mean_force":0.04134,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46966,0.04696,0.0361]},{"body_a":"world","body_b":"grasp_target","contact_count":1308.0,"contact_point_centroid":[0.4827,0.04873,-0.0019],"force_p95":0.13564,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.123,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49014,0.02041,0.25234]},{"body_a":"world","body_b":"grasp_target","contact_count":2004.0,"contact_point_centroid":[0.4827,0.04873,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.47849,0.04498,0.12382]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4225.0,"contact_point_centroid":[0.46947,0.06629,0.03852],"force_p95":0.08753,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09331,"mean_force":0.05203,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46967,0.04696,0.0361]}],"total_contact_groups":12},"final_pose_error":0.0099,"key_states":{"actual_goal_position":[0.58187,0.22885,0.23048],"final_object_position":[0.58398,0.22604,0.22187],"final_tcp_position":[0.57598,0.22199,0.23904],"realised_goal_position":[0.58187,0.22885,0.23048],"realised_object_initial_position":[0.4827,0.04873,0.03]},"peak_contact_force":0.55706,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":328.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.03],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28719,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1308.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.4815,0.04243,0.20436],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.17846,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":501.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2004.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.47796,0.04776,0.04466],"tcp_start":[0.4815,0.04243,0.20436],"tcp_to_object_dist_end":0.01925,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.48273,0.04777,0.02548],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.29094,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.1608,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11276.0,"raw_peak_contact_force":0.22087,"subtask_id":"grasp_1","tcp_end":[0.46964,0.04696,0.03607],"tcp_start":[0.47796,0.04776,0.04466],"tcp_to_object_dist_end":0.01686,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":38.0,"n_steps":181.0,"n_steps_budget":1000.0,"object_pos_end":[0.49307,0.0484,0.18128],"object_pos_start":[0.48273,0.04777,0.02548],"object_to_goal_dist_end":0.20706,"object_to_goal_dist_start":0.29094,"object_z_max":0.18037,"peak_contact_force":0.08799,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":7214.0,"raw_peak_contact_force":0.55706,"tcp_end":[0.47854,0.04736,0.19071],"tcp_start":[0.46964,0.04696,0.03607],"tcp_to_object_dist_end":0.01735,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":31.0,"n_steps":215.0,"n_steps_budget":1000.0,"object_pos_end":[0.57409,0.18194,0.3323],"object_pos_start":[0.49307,0.0484,0.18128],"object_to_goal_dist_end":0.11237,"object_to_goal_dist_start":0.20706,"object_z_max":0.338,"peak_contact_force":0.11762,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":6436.0,"raw_peak_contact_force":0.34231,"subtask_id":"transport_arc","tcp_end":[0.5553,0.17703,0.34159],"tcp_start":[0.47854,0.04736,0.19071],"tcp_to_object_dist_end":0.02153,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":350.0,"n_steps_budget":1000.0,"object_pos_end":[0.58398,0.22604,0.22187],"object_pos_start":[0.57409,0.18194,0.3323],"object_to_goal_dist_end":0.00931,"object_to_goal_dist_start":0.11237,"object_z_max":0.3323,"peak_contact_force":0.07898,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":13024.0,"raw_peak_contact_force":0.36678,"subtask_id":"release_1","tcp_end":[0.57598,0.22199,0.23904],"tcp_start":[0.5553,0.17703,0.34159],"tcp_to_object_dist_end":0.01937,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.09259,"average_solve_count":162.0,"average_success_count":162.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.09524,"descend_1.grasp_z_offset":0.01004,"descend_2.descend_z_offset":0.01534,"grasp_1.grasp_retry_x":-0.00383,"grasp_1.grasp_retry_y":-0.0083,"lift_1.lift_height":0.21721,"lift_1.lift_pose_tolerance":0.02291,"transport_1.arc_height":0.16691,"transport_1.transport_pose_tolerance":0.07814,"transport_1.transport_speed":0.18824},"optimized_scores":{"best_composite_score":0.35385,"best_fitness_score":0.97385,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":75.0,"contact_point_centroid":[0.53453,-0.02118,-0.00138],"force_p95":0.51721,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.60709,"mean_force":0.12801,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52126,-0.02088,0.03495]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5162.0,"contact_point_centroid":[0.59816,0.20966,0.28024],"force_p95":0.12667,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.4826,"mean_force":0.07857,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.59905,0.19082,0.27685]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4227.0,"contact_point_centroid":[0.60837,0.17466,0.27653],"force_p95":0.13467,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.41071,"mean_force":0.09075,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.59924,0.19165,0.2754]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":9104.0,"contact_point_centroid":[0.5264,-0.04019,0.12936],"force_p95":0.08399,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.3363,"mean_force":0.06117,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52553,-0.021,0.12666]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":10856.0,"contact_point_centroid":[0.52703,-0.00204,0.1263],"force_p95":0.08001,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32906,"mean_force":0.05248,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.5254,-0.021,0.12459]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2326.0,"contact_point_centroid":[0.55796,0.01993,0.30147],"force_p95":0.14989,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32337,"mean_force":0.08835,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.55333,0.03846,0.29865]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2565.0,"contact_point_centroid":[0.55532,0.05617,0.29997],"force_p95":0.12988,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26087,"mean_force":0.07681,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.55292,0.03732,0.29761]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53702,-0.02136,-0.00203],"force_p95":0.13444,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.15574,"mean_force":0.12567,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.5236,-0.02091,0.03516]},{"body_a":"world","body_b":"grasp_target","contact_count":2216.0,"contact_point_centroid":[0.53702,-0.02132,-0.00194],"force_p95":0.13205,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12285,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51382,-0.00969,0.21553]},{"body_a":"world","body_b":"grasp_target","contact_count":1084.0,"contact_point_centroid":[0.53702,-0.02132,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.52933,-0.02032,0.08759]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5314.0,"contact_point_centroid":[0.52333,-0.00185,0.03597],"force_p95":0.06874,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10209,"mean_force":0.04096,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52234,-0.02089,0.03371]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4157.0,"contact_point_centroid":[0.52327,-0.04019,0.03642],"force_p95":0.08023,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09491,"mean_force":0.05194,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52234,-0.02089,0.03371]}],"total_contact_groups":12},"final_pose_error":0.00982,"key_states":{"actual_goal_position":[0.61031,0.22775,0.20741],"final_object_position":[0.61543,0.22461,0.2048],"final_tcp_position":[0.60558,0.21975,0.22592],"realised_goal_position":[0.61031,0.22775,0.20741],"realised_object_initial_position":[0.53702,-0.02132,0.03]},"peak_contact_force":0.60709,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":555.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.03],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31446,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2216.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.53017,-0.01969,0.13203],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.10625,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":271.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1084.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.53112,-0.02101,0.04389],"tcp_start":[0.53017,-0.01969,0.13203],"tcp_to_object_dist_end":0.01882,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53691,-0.02125,0.02585],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31679,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.13438,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11271.0,"raw_peak_contact_force":0.15574,"subtask_id":"grasp_1","tcp_end":[0.52231,-0.02089,0.03367],"tcp_start":[0.53112,-0.02101,0.04389],"tcp_to_object_dist_end":0.01657,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":38.0,"n_steps":532.0,"n_steps_budget":1000.0,"object_pos_end":[0.54677,-0.02175,0.20907],"object_pos_start":[0.53691,-0.02125,0.02585],"object_to_goal_dist_end":0.25748,"object_to_goal_dist_start":0.31679,"object_z_max":0.20875,"peak_contact_force":0.09868,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":20035.0,"raw_peak_contact_force":0.60709,"tcp_end":[0.53271,-0.02116,0.22077],"tcp_start":[0.52231,-0.02089,0.03367],"tcp_to_object_dist_end":0.0183,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":25.0,"n_steps":179.0,"n_steps_budget":1000.0,"object_pos_end":[0.61256,0.16362,0.32556],"object_pos_start":[0.54677,-0.02175,0.20907],"object_to_goal_dist_end":0.13445,"object_to_goal_dist_start":0.25748,"object_z_max":0.34004,"peak_contact_force":0.10055,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4891.0,"raw_peak_contact_force":0.32337,"subtask_id":"transport_arc","tcp_end":[0.5937,0.1589,0.33877],"tcp_start":[0.53271,-0.02116,0.22077],"tcp_to_object_dist_end":0.0235,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":28.0,"n_steps":376.0,"n_steps_budget":1000.0,"object_pos_end":[0.61543,0.22461,0.2048],"object_pos_start":[0.61256,0.16362,0.32556],"object_to_goal_dist_end":0.00655,"object_to_goal_dist_start":0.13445,"object_z_max":0.32556,"peak_contact_force":0.11509,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":9389.0,"raw_peak_contact_force":0.4826,"subtask_id":"release_1","tcp_end":[0.60558,0.21975,0.22592],"tcp_start":[0.5937,0.1589,0.33877],"tcp_to_object_dist_end":0.02381,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.17692,"average_solve_count":130.0,"average_success_count":130.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.17032,"descend_1.grasp_z_offset":0.01,"descend_2.descend_z_offset":0.02274,"grasp_1.grasp_retry_x":0.00335,"grasp_1.grasp_retry_y":0.00429,"lift_1.lift_height":0.15352,"lift_1.lift_pose_tolerance":0.03251,"transport_1.arc_height":0.13549,"transport_1.transport_pose_tolerance":0.02489,"transport_1.transport_speed":0.33662},"optimized_scores":{"best_composite_score":0.35405,"best_fitness_score":0.97405,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":65.0,"contact_point_centroid":[0.54263,-0.02904,-0.00148],"force_p95":0.52963,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.60578,"mean_force":0.21529,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.53012,-0.02859,0.03471]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":7863.0,"contact_point_centroid":[0.56824,0.008,0.26485],"force_p95":0.12291,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.48102,"mean_force":0.07899,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.56489,0.02689,0.2625]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5046.0,"contact_point_centroid":[0.61976,0.17114,0.2493],"force_p95":0.06956,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.34691,"mean_force":0.04571,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.62384,0.15258,0.24583]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3795.0,"contact_point_centroid":[0.53312,-0.04791,0.09151],"force_p95":0.08485,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33608,"mean_force":0.06314,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.53366,-0.0287,0.08862]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4738.0,"contact_point_centroid":[0.53461,-0.00968,0.09086],"force_p95":0.08122,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32709,"mean_force":0.05262,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.5337,-0.0287,0.08892]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":9223.0,"contact_point_centroid":[0.56649,0.04469,0.264],"force_p95":0.10609,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28907,"mean_force":0.06719,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.56452,0.02612,0.26195]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4599.0,"contact_point_centroid":[0.62791,0.13363,0.24765],"force_p95":0.07365,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25347,"mean_force":0.04938,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.62384,0.1526,0.24576]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.54561,-0.02926,-0.00205],"force_p95":0.13878,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.16465,"mean_force":0.12671,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53236,-0.02864,0.03518]},{"body_a":"world","body_b":"grasp_target","contact_count":1476.0,"contact_point_centroid":[0.5456,-0.02923,-0.00191],"force_p95":0.13511,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12296,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51753,-0.01279,0.25154]},{"body_a":"world","body_b":"grasp_target","contact_count":1928.0,"contact_point_centroid":[0.5456,-0.02923,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.53733,-0.02738,0.12381]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5300.0,"contact_point_centroid":[0.53215,-0.00957,0.03584],"force_p95":0.07059,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11796,"mean_force":0.04107,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53108,-0.02861,0.03369]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4169.0,"contact_point_centroid":[0.53178,-0.04791,0.0365],"force_p95":0.08166,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09323,"mean_force":0.0519,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53109,-0.02861,0.03369]}],"total_contact_groups":12},"final_pose_error":0.00975,"key_states":{"actual_goal_position":[0.63284,0.16493,0.17692],"final_object_position":[0.63098,0.16257,0.1849],"final_tcp_position":[0.6276,0.16056,0.20663],"realised_goal_position":[0.63284,0.16493,0.17692],"realised_object_initial_position":[0.5456,-0.02923,0.03]},"peak_contact_force":209.99406,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":370.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.03],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.25864,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1476.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.53739,-0.02603,0.20474],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.17893,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":482.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1928.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.53995,-0.02883,0.04419],"tcp_start":[0.53739,-0.02603,0.20474],"tcp_to_object_dist_end":0.01903,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54549,-0.02903,0.0258],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26093,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.13857,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11269.0,"raw_peak_contact_force":0.16465,"subtask_id":"grasp_1","tcp_end":[0.53105,-0.02861,0.03365],"tcp_start":[0.53995,-0.02883,0.04419],"tcp_to_object_dist_end":0.01644,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":38.0,"n_steps":219.0,"n_steps_budget":930.0,"object_pos_end":[0.55375,-0.02944,0.13946],"object_pos_start":[0.54549,-0.02903,0.0258],"object_to_goal_dist_end":0.21317,"object_to_goal_dist_start":0.26093,"object_z_max":0.13895,"peak_contact_force":209.99406,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":8598.0,"raw_peak_contact_force":0.60578,"tcp_end":[0.53962,-0.02886,0.14786],"tcp_start":[0.53105,-0.02861,0.03365],"tcp_to_object_dist_end":0.01645,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":45.0,"n_steps":585.0,"n_steps_budget":1000.0,"object_pos_end":[0.62662,0.14695,0.26533],"object_pos_start":[0.55375,-0.02944,0.13946],"object_to_goal_dist_end":0.09043,"object_to_goal_dist_start":0.21317,"object_z_max":0.30257,"peak_contact_force":0.06612,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":17086.0,"raw_peak_contact_force":0.48102,"subtask_id":"transport_arc","tcp_end":[0.62202,0.14526,0.28644],"tcp_start":[0.53962,-0.02886,0.14786],"tcp_to_object_dist_end":0.02167,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":219.0,"n_steps_budget":1000.0,"object_pos_end":[0.63098,0.16257,0.1849],"object_pos_start":[0.62662,0.14695,0.26533],"object_to_goal_dist_end":0.00853,"object_to_goal_dist_start":0.09043,"object_z_max":0.26533,"peak_contact_force":0.06682,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":9645.0,"raw_peak_contact_force":0.34691,"subtask_id":"release_1","tcp_end":[0.6276,0.16056,0.20663],"tcp_start":[0.62202,0.14526,0.28644],"tcp_to_object_dist_end":0.02208,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```