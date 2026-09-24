## Search State

- **Seed**: 8
- **Iteration**: 6 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 5 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 7 | 0.1213 | 0.30 | ✅ accepted |
| 4 | approach → descend → grasp → approach → descend → release | linear_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 4 | -0.1038 | 0.15 | ❌ rejected |
| 3 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | position_control | impedance_control | position_control | force_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | force_exceeded | time_limit | 9 | -0.3054 | 0.15 | ❌ rejected |
| 2 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 6 | 0.1471 | 0.28 | ❌ rejected |
| 1 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 6 | 0.2688 | 0.29 | ✅ accepted |

**Proposal policy**: task_score is 0.30 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
- task_score stagnant: change coupled targets, parameters, terminations, phase types, controls, subtasks, or ordering when evidence shows they need to change together.
A HOLD wastes an iteration when task_score is below 0.9.

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

## Current Skill (Q=0.121) — your mutation base

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
    - 0.0
  subtask_id: release_1
- id: release_1
  type: release
  control: position_control
  termination: time_limit
  end_effector_action: open
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0
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
  - target: source=yaml, anchor=task_goal, entity=place_target, offset=[0.0, 0.0, 0.0]
  - parameter_bindings: none
- **release_1** (`release`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings: none

## Design Metrics

- **Composite score**: 0.121
- **task_score** (E): 0.296
- **fitness_score**: 0.621  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.500

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1461 |
| descend_1 | 1.00 | 1.00 | 0.1166 |
| grasp_1 | 1.00 | 1.00 | 0.0131 |
| lift_1 | 0.67 | 1.00 | 0.1238 |
| transport_1 | 0.00 | 1.00 | 0.1633 |
| descend_2 | 1.00 | 0.67 | 0.1666 |
| release_1 | 1.00 | 1.00 | 0.0212 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.516, -0.001, 0.161) | (0.522, -0.001, 0.030)→(0.522, -0.001, 0.026) | 0.287→0.289 | 1.00 / 4.000 | 11.248 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.516, -0.001, 0.161)→(0.516, -0.001, 0.045) | (0.522, -0.001, 0.026)→(0.522, -0.001, 0.026) | 0.289→0.289 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_1 | grasp | 1.00 / step_budget | (0.516, -0.001, 0.045)→(0.508, -0.001, 0.035) | (0.522, -0.001, 0.026)→(0.522, -0.001, 0.026) | 0.289→0.290 | 1.00 / 42.667 | 0.144 | 0.180 |
| lift_1 | lift | 0.67 / step_budget | (0.508, -0.001, 0.035)→(0.515, -0.001, 0.159) | (0.522, -0.001, 0.026)→(0.526, -0.001, 0.143) | 0.290→0.236 | 1.00 / 36.667 | 0.085 | 0.574 |
| transport_1 | approach | 0.00 / step_budget | (0.515, -0.001, 0.159)→(0.547, 0.076, 0.295) | (0.526, -0.001, 0.143)→(0.554, 0.078, 0.272) | 0.236→0.156 | 1.00 / 28.667 | 0.109 | 0.245 |
| descend_2 | descend | 1.00 / step_budget | (0.547, 0.076, 0.295)→(0.602, 0.201, 0.200) | (0.554, 0.078, 0.272)→(0.596, 0.198, 0.155) | 0.156→0.053 | 0.67 / 22.667 | 0.054 | 0.261 |
| release_1 | release | 1.00 / step_budget | (0.602, 0.201, 0.200)→(0.597, 0.199, 0.221) | (0.596, 0.198, 0.155)→(0.590, 0.191, 0.022) | 0.053→0.185 | 1.00 / 3.333 | 0.120 | 1.457 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.359
- phase_score: 0.364
- phase_breakdown.grasp_1_score: 1.000
- phase_breakdown.transport_arc_score: 0.045
- phase_breakdown.approach_1_score: 0.072
- phase_breakdown.descend_1_score: 0.848
- phase_breakdown.release_1_score: 0.673
- grasp_place_fitness: 0.654

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.654
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.359
- **Median Q (composite search score)**: 0.120
- **K-run variance**: 0.0007
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Parameters at upper bound**: lift_1.lift_height
- **Final σ (mean)**: 0.466


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.02143,"average_solve_count":140.0,"average_success_count":140.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.12904,"descend_1.grasp_z_offset":0.01177,"grasp_1.grasp_retry_x":-0.00626,"grasp_1.grasp_retry_y":0.018,"lift_1.lift_height":0.12812,"transport_1.arc_height":0.10558,"transport_1.transport_speed":0.20206},"optimized_scores":{"best_composite_score":0.09022,"best_fitness_score":0.59022,"best_task_score":0.23726},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":604.0,"contact_point_centroid":[0.57695,0.20598,-0.00389],"force_p95":0.83256,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.61589,"mean_force":0.20722,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.57138,0.22054,0.22969]},{"body_a":"world","body_b":"grasp_target","contact_count":144.0,"contact_point_centroid":[0.4804,0.04635,-0.00123],"force_p95":0.30936,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.51993,"mean_force":0.06907,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46841,0.04681,0.03984]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":9603.0,"contact_point_centroid":[0.54376,0.14034,0.27648],"force_p95":0.12768,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.37347,"mean_force":0.07673,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.53842,0.15799,0.2793]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":14079.0,"contact_point_centroid":[0.48393,0.03332,0.23473],"force_p95":0.09961,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.36606,"mean_force":0.06937,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.47775,0.05141,0.23357]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8208.0,"contact_point_centroid":[0.53393,0.17441,0.27954],"force_p95":0.13141,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.35905,"mean_force":0.0881,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.53736,0.15613,0.28086]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":11271.0,"contact_point_centroid":[0.47165,0.06617,0.09163],"force_p95":0.08551,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31712,"mean_force":0.05911,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.47184,0.04696,0.08896]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":14176.0,"contact_point_centroid":[0.4737,0.02804,0.09079],"force_p95":0.07877,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28506,"mean_force":0.04838,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.47187,0.04696,0.08919]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":12248.0,"contact_point_centroid":[0.48164,0.07204,0.23911],"force_p95":0.11072,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23253,"mean_force":0.07819,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.4786,0.05283,0.23703]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.48278,0.04869,-0.00215],"force_p95":0.16326,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.2192,"mean_force":0.13349,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47078,0.04706,0.03911]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5222.0,"contact_point_centroid":[0.47117,0.02794,0.03917],"force_p95":0.07151,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1955,"mean_force":0.04157,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46959,0.04695,0.03789]},{"body_a":"world","body_b":"grasp_target","contact_count":1712.0,"contact_point_centroid":[0.4827,0.04873,-0.00192],"force_p95":0.13411,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12291,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.4896,0.02122,0.23379]},{"body_a":"world","body_b":"grasp_target","contact_count":1524.0,"contact_point_centroid":[0.4827,0.04873,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.47799,0.04561,0.10644]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4224.0,"contact_point_centroid":[0.46941,0.06628,0.04033],"force_p95":0.08757,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09239,"mean_force":0.052,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.4696,0.04695,0.0379]}],"total_contact_groups":13},"final_pose_error":0.00993,"key_states":{"actual_goal_position":[0.58187,0.22885,0.23048],"final_object_position":[0.57727,0.20557,0.016],"final_tcp_position":[0.57546,0.22205,0.22714],"realised_goal_position":[0.58187,0.22885,0.23048],"realised_object_initial_position":[0.4827,0.04873,0.03]},"peak_contact_force":1.61589,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":429.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.03],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28719,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1712.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.48069,0.04373,0.16729],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.14138,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":381.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1524.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.47786,0.04775,0.04645],"tcp_start":[0.48069,0.04373,0.16729],"tcp_to_object_dist_end":0.02102,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":42.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.48274,0.04779,0.02549],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.29092,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.16033,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11246.0,"raw_peak_contact_force":0.2192,"subtask_id":"grasp_1","tcp_end":[0.46956,0.04694,0.03786],"tcp_start":[0.47786,0.04775,0.04645],"tcp_to_object_dist_end":0.01809,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":663.0,"n_steps_budget":750.0,"object_pos_end":[0.48812,0.0483,0.12474],"object_pos_start":[0.48274,0.04779,0.02549],"object_to_goal_dist_end":0.22928,"object_to_goal_dist_start":0.29092,"object_z_max":0.12463,"peak_contact_force":0.08215,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":25591.0,"raw_peak_contact_force":0.51993,"tcp_end":[0.47807,0.04737,0.1419],"tcp_start":[0.46956,0.04694,0.03786],"tcp_to_object_dist_end":0.0199,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":24.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51717,0.10474,0.30227],"object_pos_start":[0.48812,0.0483,0.12474],"object_to_goal_dist_end":0.15731,"object_to_goal_dist_start":0.22928,"object_z_max":0.30214,"peak_contact_force":0.09564,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":26327.0,"raw_peak_contact_force":0.36606,"subtask_id":"transport_arc","tcp_end":[0.50818,0.10298,0.32928],"tcp_start":[0.47807,0.04737,0.1419],"tcp_to_object_dist_end":0.02852,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":780.0,"n_steps_budget":1000.0,"object_pos_end":[0.56843,0.21368,0.1493],"object_pos_start":[0.51717,0.10474,0.30227],"object_to_goal_dist_end":0.08368,"object_to_goal_dist_start":0.15731,"object_z_max":0.3023,"peak_contact_force":0.0,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":17811.0,"raw_peak_contact_force":0.37347,"subtask_id":"release_1","tcp_end":[0.57546,0.22205,0.22714],"tcp_start":[0.50818,0.10298,0.32928],"tcp_to_object_dist_end":0.07861,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.57727,0.20557,0.016],"object_pos_start":[0.56843,0.21368,0.1493],"object_to_goal_dist_end":0.21579,"object_to_goal_dist_start":0.08368,"object_z_max":0.1493,"peak_contact_force":0.12278,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":604.0,"raw_peak_contact_force":1.61589,"subtask_id":"release_1","tcp_end":[0.57087,0.22031,0.24826],"tcp_start":[0.57546,0.22205,0.22714],"tcp_to_object_dist_end":0.23281,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.01974,"average_solve_count":152.0,"average_success_count":152.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.1191,"descend_1.grasp_z_offset":0.01024,"grasp_1.grasp_retry_x":0.00661,"grasp_1.grasp_retry_y":-0.01553,"lift_1.lift_height":0.29999,"transport_1.arc_height":0.06228,"transport_1.transport_speed":0.16823},"optimized_scores":{"best_composite_score":0.12003,"best_fitness_score":0.62003,"best_task_score":0.29241},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":213.0,"contact_point_centroid":[0.5825,0.2127,-0.00667],"force_p95":1.27581,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.44927,"mean_force":0.34079,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.59985,0.21906,0.21412]},{"body_a":"world","body_b":"grasp_target","contact_count":142.0,"contact_point_centroid":[0.53397,-0.02089,-0.00112],"force_p95":0.43643,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.60789,"mean_force":0.08677,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52102,-0.02089,0.03572]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":16971.0,"contact_point_centroid":[0.52343,-0.04012,0.11586],"force_p95":0.08334,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33848,"mean_force":0.05955,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52251,-0.02094,0.11324]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":20249.0,"contact_point_centroid":[0.52424,-0.002,0.11408],"force_p95":0.07694,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.3312,"mean_force":0.05095,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52248,-0.02094,0.11248]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":979.0,"contact_point_centroid":[0.59516,0.23797,0.19917],"force_p95":0.0808,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28879,"mean_force":0.05406,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.6033,0.22053,0.19905]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1070.0,"contact_point_centroid":[0.60729,0.20199,0.19582],"force_p95":0.07783,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2209,"mean_force":0.05059,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.60327,0.22052,0.19899]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":15407.0,"contact_point_centroid":[0.57824,0.17154,0.25003],"force_p95":0.08851,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21089,"mean_force":0.05659,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.58154,0.15291,0.24869]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":14920.0,"contact_point_centroid":[0.54268,0.00559,0.257],"force_p95":0.09045,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20159,"mean_force":0.06425,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.53956,0.02442,0.25569]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":15308.0,"contact_point_centroid":[0.58765,0.13801,0.24578],"force_p95":0.08561,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19806,"mean_force":0.05723,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.58274,0.15639,0.24631]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":16409.0,"contact_point_centroid":[0.54075,0.04195,0.25552],"force_p95":0.08319,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16069,"mean_force":0.05904,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.5391,0.02305,0.25441]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53702,-0.02136,-0.00203],"force_p95":0.13423,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.15545,"mean_force":0.12561,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52375,-0.02093,0.03547]},{"body_a":"world","body_b":"grasp_target","contact_count":1928.0,"contact_point_centroid":[0.53702,-0.02132,-0.00193],"force_p95":0.13308,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12288,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51369,-0.00953,0.22757]},{"body_a":"world","body_b":"grasp_target","contact_count":1360.0,"contact_point_centroid":[0.53702,-0.02132,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.52927,-0.02021,0.09949]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5316.0,"contact_point_centroid":[0.52344,-0.00187,0.03625],"force_p95":0.06884,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10158,"mean_force":0.04095,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52249,-0.02091,0.03403]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4157.0,"contact_point_centroid":[0.52337,-0.0402,0.03675],"force_p95":0.08038,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09483,"mean_force":0.05192,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52249,-0.02091,0.03403]}],"total_contact_groups":15},"final_pose_error":0.00995,"key_states":{"actual_goal_position":[0.61031,0.22775,0.20741],"final_object_position":[0.58812,0.21423,0.02481],"final_tcp_position":[0.6049,0.22088,0.20268],"realised_goal_position":[0.61031,0.22775,0.20741],"realised_object_initial_position":[0.53702,-0.02132,0.03]},"peak_contact_force":1.44927,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":483.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.03],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31446,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1928.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.52997,-0.01944,0.15587],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.13005,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":340.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1360.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.53127,-0.02103,0.04422],"tcp_start":[0.52997,-0.01944,0.15587],"tcp_to_object_dist_end":0.01909,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53691,-0.02126,0.02585],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.3168,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.13419,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11273.0,"raw_peak_contact_force":0.15545,"subtask_id":"grasp_1","tcp_end":[0.52246,-0.02091,0.03399],"tcp_start":[0.53127,-0.02103,0.04422],"tcp_to_object_dist_end":0.01659,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":36.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53661,-0.0216,0.17876],"object_pos_start":[0.53691,-0.02126,0.02585],"object_to_goal_dist_end":0.26159,"object_to_goal_dist_start":0.3168,"object_z_max":0.17858,"peak_contact_force":0.09393,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":37362.0,"raw_peak_contact_force":0.60789,"tcp_end":[0.52711,-0.02104,0.19555],"tcp_start":[0.52246,-0.02091,0.03399],"tcp_to_object_dist_end":0.0193,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":32.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5653,0.0834,0.27984],"object_pos_start":[0.53661,-0.0216,0.17876],"object_to_goal_dist_end":0.16766,"object_to_goal_dist_start":0.26159,"object_z_max":0.27979,"peak_contact_force":0.08392,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":31329.0,"raw_peak_contact_force":0.20159,"subtask_id":"transport_arc","tcp_end":[0.55926,0.08216,0.30265],"tcp_start":[0.52711,-0.02104,0.19555],"tcp_to_object_dist_end":0.02363,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":32.0,"n_steps":847.0,"n_steps_budget":1000.0,"object_pos_end":[0.59839,0.2211,0.17231],"object_pos_start":[0.5653,0.0834,0.27984],"object_to_goal_dist_end":0.03767,"object_to_goal_dist_start":0.16766,"object_z_max":0.27984,"peak_contact_force":0.08505,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":30715.0,"raw_peak_contact_force":0.21089,"subtask_id":"release_1","tcp_end":[0.6049,0.22088,0.20268],"tcp_start":[0.55926,0.08216,0.30265],"tcp_to_object_dist_end":0.03106,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.58812,0.21423,0.02481],"object_pos_start":[0.59839,0.2211,0.17231],"object_to_goal_dist_end":0.18444,"object_to_goal_dist_start":0.03767,"object_z_max":0.17231,"peak_contact_force":0.12529,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2262.0,"raw_peak_contact_force":1.44927,"subtask_id":"release_1","tcp_end":[0.5998,0.21905,0.22286],"tcp_start":[0.6049,0.22088,0.20268],"tcp_to_object_dist_end":0.19845,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.0219,"average_solve_count":137.0,"average_success_count":137.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.12557,"descend_1.grasp_z_offset":0.01009,"grasp_1.grasp_retry_x":-0.00988,"grasp_1.grasp_retry_y":-0.00385,"lift_1.lift_height":0.1257,"transport_1.arc_height":0.05924,"transport_1.transport_speed":0.15663},"optimized_scores":{"best_composite_score":0.15356,"best_fitness_score":0.65356,"best_task_score":0.35943},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":248.0,"contact_point_centroid":[0.60309,0.15458,-0.0055],"force_p95":1.13887,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.30537,"mean_force":0.28999,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.62096,0.15818,0.18103]},{"body_a":"world","body_b":"grasp_target","contact_count":146.0,"contact_point_centroid":[0.54261,-0.02822,-0.00113],"force_p95":0.42278,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.59404,"mean_force":0.08649,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52974,-0.02857,0.03536]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":11271.0,"contact_point_centroid":[0.53408,-0.04787,0.08753],"force_p95":0.08268,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33023,"mean_force":0.05918,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.53359,-0.02868,0.0847]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":13653.0,"contact_point_centroid":[0.53498,-0.00971,0.08532],"force_p95":0.07844,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32109,"mean_force":0.05055,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.53346,-0.02868,0.08362]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1052.0,"contact_point_centroid":[0.61878,0.17754,0.16853],"force_p95":0.0753,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24938,"mean_force":0.05033,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.62497,0.15937,0.16747]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1179.0,"contact_point_centroid":[0.6277,0.14046,0.16581],"force_p95":0.07192,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19922,"mean_force":0.04567,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.62497,0.15936,0.16746]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":15674.0,"contact_point_centroid":[0.59854,0.12569,0.20766],"force_p95":0.08093,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19788,"mean_force":0.05272,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.60081,0.10692,0.20605]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":14883.0,"contact_point_centroid":[0.60491,0.08957,0.20523],"force_p95":0.08714,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19773,"mean_force":0.05653,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.60155,0.10841,0.20507]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":15142.0,"contact_point_centroid":[0.55271,-0.01989,0.20111],"force_p95":0.09005,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16784,"mean_force":0.06409,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.5505,-0.0009,0.19944]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.54561,-0.02925,-0.00205],"force_p95":0.13882,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.16482,"mean_force":0.12674,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.5322,-0.02863,0.03516]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":17216.0,"contact_point_centroid":[0.55236,0.01736,0.19965],"force_p95":0.08317,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15148,"mean_force":0.05713,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.55022,-0.00148,0.19866]},{"body_a":"world","body_b":"grasp_target","contact_count":1964.0,"contact_point_centroid":[0.5456,-0.02923,-0.00193],"force_p95":0.13308,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12287,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51766,-0.01314,0.22994]},{"body_a":"world","body_b":"grasp_target","contact_count":1424.0,"contact_point_centroid":[0.5456,-0.02923,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.5375,-0.02773,0.10213]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5299.0,"contact_point_centroid":[0.53204,-0.00956,0.03587],"force_p95":0.07056,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11745,"mean_force":0.04106,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53092,-0.0286,0.03367]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4171.0,"contact_point_centroid":[0.53168,-0.0479,0.03647],"force_p95":0.08156,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09325,"mean_force":0.0519,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53093,-0.0286,0.03367]}],"total_contact_groups":15},"final_pose_error":0.00997,"key_states":{"actual_goal_position":[0.63284,0.16493,0.17692],"final_object_position":[0.60566,0.15445,0.02623],"final_tcp_position":[0.62673,0.15963,0.17109],"realised_goal_position":[0.63284,0.16493,0.17692],"realised_object_initial_position":[0.5456,-0.02923,0.03]},"peak_contact_force":33.49943,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":492.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.03],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.25864,"object_z_max":0.03,"peak_contact_force":33.49943,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1964.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.53795,-0.02673,0.1612],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.13542,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":356.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1424.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.53979,-0.02882,0.04416],"tcp_start":[0.53795,-0.02673,0.1612],"tcp_to_object_dist_end":0.01906,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54549,-0.02902,0.0258],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26093,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.13857,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11270.0,"raw_peak_contact_force":0.16482,"subtask_id":"grasp_1","tcp_end":[0.53089,-0.0286,0.03363],"tcp_start":[0.53979,-0.02882,0.04416],"tcp_to_object_dist_end":0.01657,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":663.0,"n_steps_budget":750.0,"object_pos_end":[0.55183,-0.0295,0.12532],"object_pos_start":[0.54549,-0.02902,0.0258],"object_to_goal_dist_end":0.21686,"object_to_goal_dist_start":0.26093,"object_z_max":0.1252,"peak_contact_force":0.0792,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":25070.0,"raw_peak_contact_force":0.59404,"tcp_end":[0.54052,-0.02887,0.13854],"tcp_start":[0.53089,-0.0286,0.03363],"tcp_to_object_dist_end":0.01741,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":30.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.58036,0.04499,0.233],"object_pos_start":[0.55183,-0.0295,0.12532],"object_to_goal_dist_end":0.14243,"object_to_goal_dist_start":0.21686,"object_z_max":0.23294,"peak_contact_force":0.14751,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":32358.0,"raw_peak_contact_force":0.16784,"subtask_id":"transport_arc","tcp_end":[0.57237,0.04414,0.25381],"tcp_start":[0.54052,-0.02887,0.13854],"tcp_to_object_dist_end":0.02231,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":36.0,"n_steps":824.0,"n_steps_budget":1000.0,"object_pos_end":[0.62077,0.16007,0.14308],"object_pos_start":[0.58036,0.04499,0.233],"object_to_goal_dist_end":0.03626,"object_to_goal_dist_start":0.14243,"object_z_max":0.233,"peak_contact_force":0.07575,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":30557.0,"raw_peak_contact_force":0.19788,"subtask_id":"release_1","tcp_end":[0.62673,0.15963,0.17109],"tcp_start":[0.57237,0.04414,0.25381],"tcp_to_object_dist_end":0.02864,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.60566,0.15445,0.02623],"object_pos_start":[0.62077,0.16007,0.14308],"object_to_goal_dist_end":0.15349,"object_to_goal_dist_start":0.03626,"object_z_max":0.14308,"peak_contact_force":0.1132,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2479.0,"raw_peak_contact_force":1.30537,"subtask_id":"release_1","tcp_end":[0.62089,0.15817,0.19115],"tcp_start":[0.62673,0.15963,0.17109],"tcp_to_object_dist_end":0.16567,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```