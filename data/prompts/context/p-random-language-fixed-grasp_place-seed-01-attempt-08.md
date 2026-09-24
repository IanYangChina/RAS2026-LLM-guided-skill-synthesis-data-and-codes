## Search State

- **Seed**: 1
- **Iteration**: 9 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 8 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 12 | 0.2591 | 1.00 | ❌ rejected |
| 7 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 12 | 0.2591 | 1.00 | ✅ accepted |
| 6 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | impedance_control | position_control | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 8 | 0.1466 | 0.44 | ✅ accepted |
| 5 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | impedance_control | position_control | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 8 | 0.1891 | 0.42 | ✅ accepted |
| 4 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | impedance_control | position_control | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 7 | -0.0465 | 0.16 | ✅ accepted |

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
- Frozen realised-scene SHA-256: `a2ed2c4162d37489f2d2d0fa0373774d72c951d58f2469e0ba2d602ff46b6cfb`
- Frozen object start: [0.5011821624700257, 0.045046369632593536, 0.03]
- Frozen task target: [0.5644159612719634, 0.2448649447137244, 0.1467747178015728]
- Goal object position: (0.5644159612719634, 0.2448649447137244, 0.1467747178015728)
- place_goal_position (task success criterion — final object 3D position must be close to the realised airborne target here): (0.5644159612719634, 0.2448649447137244, 0.1467747178015728)
- Grasp/lift components are optimiser fitness diagnostics only; canonical task_score is final object-to-realised-target proximity.
- Object initial pose: (0.5011821624700257, 0.045046369632593536, 0.03)
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
  frozen_object_start: [0.5012, 0.045, 0.03]
  frozen_task_target: [0.5644, 0.2449, 0.1468]
  frozen_object_starts: {'grasp_target': [0.5011821624700257, 0.045046369632593536, 0.03]}
  frozen_targets: {'place_target': [0.5644159612719634, 0.2448649447137244, 0.1467747178015728]}
  goal_tolerance_m: 0.02
  force_limit_n: 20
  force_scale_n: 5
  realized_scene_sha256: a2ed2c4162d37489f2d2d0fa0373774d72c951d58f2469e0ba2d602ff46b6cfb

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

## Current Skill (Q=0.259) — your mutation base

```yaml
skill: grasp_place
dsl_version: 2
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
    - 0.0
  parameters:
    approach_speed:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.1
      binds_to:
      - path: generator.speed
        mode: scale
    approach_tolerance:
      type: scalar
      range:
      - 0.005
      - 0.03
      default: 0.01
      binds_to:
      - path: termination.pose_tolerance
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
    offset:
    - 0.0
    - 0.0
    - 0.0
  parameters:
    descend_speed:
      type: scalar
      range:
      - 0.02
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: scale
    descend_tolerance:
      type: scalar
      range:
      - 0.003
      - 0.02
      default: 0.008
      binds_to:
      - path: termination.pose_tolerance
        mode: replace
  subtask_id: descend_1
- id: grasp_1
  type: grasp
  control: impedance_control
  termination: grasp_success
  end_effector_action: force_grasp
  target:
    source: yaml
    anchor: current_tcp
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
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.1
      axis: world_z
      mode: add_to_offset
      sign: positive
  parameters:
    lift_height:
      type: scalar
      range:
      - 0.05
      - 0.15
      default: 0.1
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    lift_speed:
      type: scalar
      range:
      - 0.02
      - 0.15
      default: 0.08
      binds_to:
      - path: generator.speed
        mode: scale
    lift_tolerance:
      type: scalar
      range:
      - 0.005
      - 0.03
      default: 0.01
      binds_to:
      - path: termination.pose_tolerance
        mode: replace
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
    - 0.0
  parameters:
    transport_speed:
      type: scalar
      range:
      - 0.05
      - 0.3
      default: 0.15
      binds_to:
      - path: generator.speed
        mode: scale
    transport_tolerance:
      type: scalar
      range:
      - 0.005
      - 0.03
      default: 0.01
      binds_to:
      - path: termination.pose_tolerance
        mode: replace
  subtask_id: transport_arc
- id: descend_place
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
    - 0.01
    offset_along_axis:
      distance: 0.0
      axis: world_z
      mode: add_to_offset
      sign: positive
  parameters:
    place_speed:
      type: scalar
      range:
      - 0.02
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: scale
    place_tolerance:
      type: scalar
      range:
      - 0.003
      - 0.02
      default: 0.008
      binds_to:
      - path: termination.pose_tolerance
        mode: replace
    place_z_offset:
      type: scalar
      range:
      - -0.01
      - 0.03
      default: 0.01
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: release_1

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.0]
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (scale)
    - approach_tolerance: status=consumed; consumers=termination.pose_tolerance (replace)
- **descend_1** (`descend`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.0]
  - parameter_bindings:
    - descend_speed: status=consumed; consumers=generator.speed (scale)
    - descend_tolerance: status=consumed; consumers=termination.pose_tolerance (replace)
- **grasp_1** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings: none
- **lift_1** (`lift`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=world_z, distance=0.1, mode=add_to_offset, sign=positive}
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - lift_speed: status=consumed; consumers=generator.speed (scale)
    - lift_tolerance: status=consumed; consumers=termination.pose_tolerance (replace)
- **transport_1** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0]
  - parameter_bindings:
    - transport_speed: status=consumed; consumers=generator.speed (scale)
    - transport_tolerance: status=consumed; consumers=termination.pose_tolerance (replace)
- **descend_place** (`descend`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.01], offset_along_axis={axis=world_z, distance=0.0, mode=add_to_offset, sign=positive}
  - parameter_bindings:
    - place_speed: status=consumed; consumers=generator.speed (scale)
    - place_tolerance: status=consumed; consumers=termination.pose_tolerance (replace)
    - place_z_offset: status=consumed; consumers=target.offset.z (replace)

## Design Metrics

- **Composite score**: 0.259
- **task_score** (E): 1.000
- **fitness_score**: 0.979  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.720

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.2557 |
| descend_1 | 1.00 | 1.00 | 0.0136 |
| grasp_1 | 1.00 | 1.00 | 0.0119 |
| lift_1 | 1.00 | 1.00 | 0.1170 |
| transport_1 | 1.00 | 1.00 | 0.2402 |
| descend_place | 1.00 | 1.00 | 0.0150 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.477, 0.000, 0.048) | (0.479, -0.000, 0.030)→(0.479, -0.000, 0.026) | 0.276→0.278 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.477, 0.000, 0.048)→(0.474, -0.000, 0.035) | (0.479, -0.000, 0.026)→(0.479, -0.000, 0.026) | 0.278→0.278 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_1 | grasp | 1.00 / step_budget | (0.474, -0.000, 0.035)→(0.466, -0.001, 0.027) | (0.479, -0.000, 0.026)→(0.479, -0.001, 0.025) | 0.278→0.278 | 1.00 / 42.667 | 0.171 | 0.249 |
| lift_1 | lift | 1.00 / step_budget | (0.466, -0.001, 0.027)→(0.462, -0.001, 0.144) | (0.479, -0.001, 0.025)→(0.475, -0.001, 0.137) | 0.278→0.251 | 1.00 / 37.667 | 0.087 | 0.717 |
| transport_1 | approach | 1.00 / step_budget | (0.462, -0.001, 0.144)→(0.597, 0.191, 0.142) | (0.475, -0.001, 0.137)→(0.597, 0.193, 0.131) | 0.251→0.027 | 1.00 / 39.000 | 0.082 | 0.137 |
| descend_place | descend | 1.00 / step_budget | (0.597, 0.191, 0.142)→(0.603, 0.200, 0.153) | (0.597, 0.193, 0.131)→(0.603, 0.202, 0.140) | 0.027→0.014 | 1.00 / 39.000 | 0.081 | 0.242 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.127
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 1.000
- phase_score: 0.709
- phase_breakdown.release_1_score: 0.788
- phase_breakdown.approach_1_score: 0.551
- phase_breakdown.grasp_1_score: 1.000
- phase_breakdown.transport_arc_score: 0.618
- phase_breakdown.descend_1_score: 0.730
- grasp_place_fitness: 0.981

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.981
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 1.000
- **Median Q (composite search score)**: 0.259
- **K-run variance**: 0.0000
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Parameters at lower bound**: lift_1.lift_tolerance
- **Final σ (mean)**: 0.229


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `8110053be9072e64e15984c6424e4a66fe19af4b6c37a60139a43e94cc34ad53`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.05,0.05],"goal_z_delta":0.15,"object_xy_delta":[0.05,0.05]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `46ef03f7b16015a0d14bf26d80c05d326b92c02b0bf759391930f5ab902d1933`; realized-scene SHA-256: `a2ed2c4162d37489f2d2d0fa0373774d72c951d58f2469e0ba2d602ff46b6cfb`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50118,0.04505,0.03]},{"name":"goal","value":[0.56442,0.24486,0.14677]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.50118,0.04505,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.56442,0.24486,0.14677]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.50888,"average_solve_count":169.0,"average_success_count":169.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.14788,"approach_1.approach_tolerance":0.01208,"descend_1.descend_speed":0.04377,"descend_1.descend_tolerance":0.01058,"descend_place.place_speed":0.07521,"descend_place.place_tolerance":0.01328,"descend_place.place_z_offset":0.01104,"lift_1.lift_height":0.13491,"lift_1.lift_speed":0.08407,"lift_1.lift_tolerance":0.01997,"transport_1.transport_speed":0.15776,"transport_1.transport_tolerance":0.01774},"optimized_scores":{"best_composite_score":0.25681,"best_fitness_score":0.97681,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":84.0,"contact_point_centroid":[0.49766,0.04098,-0.00161],"force_p95":0.684,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.78521,"mean_force":0.15624,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48546,0.04178,0.02707]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5896.0,"contact_point_centroid":[0.48405,0.06084,0.08571],"force_p95":0.10414,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.42039,"mean_force":0.06821,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48304,0.04158,0.08281]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":7796.0,"contact_point_centroid":[0.48495,0.0229,0.08274],"force_p95":0.09018,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31867,"mean_force":0.05037,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48303,0.04158,0.08111]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50142,0.04478,-0.0023],"force_p95":0.20721,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.28709,"mean_force":0.14511,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.48809,0.04203,0.02654]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2224.0,"contact_point_centroid":[0.55162,0.25456,0.14596],"force_p95":0.09915,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25493,"mean_force":0.06659,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.5568,0.23637,0.14197]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5158.0,"contact_point_centroid":[0.48846,0.02308,0.02692],"force_p95":0.06828,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20061,"mean_force":0.04112,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.48685,0.04192,0.02524]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2917.0,"contact_point_centroid":[0.56317,0.21856,0.14184],"force_p95":0.08647,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17258,"mean_force":0.04827,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.55681,0.23637,0.14197]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":13147.0,"contact_point_centroid":[0.52393,0.12048,0.1381],"force_p95":0.09148,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15326,"mean_force":0.05352,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.51863,0.13829,0.1377]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":9000.0,"contact_point_centroid":[0.51868,0.15932,0.14056],"force_p95":0.11515,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15216,"mean_force":0.07476,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.51943,0.1402,0.13777]},{"body_a":"world","body_b":"grasp_target","contact_count":2860.0,"contact_point_centroid":[0.50118,0.04505,-0.00195],"force_p95":0.12892,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.1228,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49714,0.02076,0.16973]},{"body_a":"world","body_b":"grasp_target","contact_count":108.0,"contact_point_centroid":[0.50118,0.04505,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49549,0.04223,0.03766]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4178.0,"contact_point_centroid":[0.4876,0.06143,0.02825],"force_p95":0.09353,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10896,"mean_force":0.0573,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.48686,0.04193,0.02526]}],"total_contact_groups":12},"final_pose_error":0.01322,"key_states":{"actual_goal_position":[0.56442,0.24486,0.14677],"final_object_position":[0.56718,0.2444,0.13529],"final_tcp_position":[0.55886,0.24058,0.14661],"realised_goal_position":[0.56442,0.24486,0.14677],"realised_object_initial_position":[0.50118,0.04505,0.03]},"peak_contact_force":0.78521,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":716.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.03],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.23992,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2860.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.49642,0.04201,0.0404],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.01545,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":27.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":108.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.49542,0.04262,0.03429],"tcp_start":[0.49642,0.04201,0.0404],"tcp_to_object_dist_end":0.01036,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.5014,0.04273,0.02497],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.24427,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"peak_contact_force":0.1976,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11136.0,"raw_peak_contact_force":0.28709,"subtask_id":"grasp_1","tcp_end":[0.48682,0.04192,0.02522],"tcp_start":[0.49542,0.04262,0.03429],"tcp_to_object_dist_end":0.0146,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":367.0,"n_steps_budget":840.0,"object_pos_end":[0.49804,0.04236,0.13717],"object_pos_start":[0.5014,0.04273,0.02497],"object_to_goal_dist_end":0.21332,"object_to_goal_dist_start":0.24427,"object_z_max":0.1369,"peak_contact_force":0.10255,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":13776.0,"raw_peak_contact_force":0.78521,"tcp_end":[0.48306,0.04158,0.14057],"tcp_start":[0.48682,0.04192,0.02522],"tcp_to_object_dist_end":0.01538,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":667.0,"n_steps_budget":1000.0,"object_pos_end":[0.56536,0.23547,0.12855],"object_pos_start":[0.49804,0.04236,0.13717],"object_to_goal_dist_end":0.02053,"object_to_goal_dist_start":0.21332,"object_z_max":0.13751,"peak_contact_force":0.10102,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":22147.0,"raw_peak_contact_force":0.15326,"subtask_id":"transport_arc","tcp_end":[0.55585,0.2315,0.13896],"tcp_start":[0.48306,0.04158,0.14057],"tcp_to_object_dist_end":0.01465,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":139.0,"n_steps_budget":1000.0,"object_pos_end":[0.56718,0.2444,0.13529],"object_pos_start":[0.56536,0.23547,0.12855],"object_to_goal_dist_end":0.01182,"object_to_goal_dist_start":0.02053,"object_z_max":0.13523,"peak_contact_force":0.09915,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":5141.0,"raw_peak_contact_force":0.25493,"subtask_id":"release_1","tcp_end":[0.55886,0.24058,0.14661],"tcp_start":[0.55585,0.2315,0.13896],"tcp_to_object_dist_end":0.01455,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `1efc3ad2e58ea1c47cd56203c4986b53dab7b80d759e458b85d233ccc9cc04bd`; realized-scene SHA-256: `67b45068113fe0ef6f199d4981822d51bd0bd66bb4f388f7402a08094b41852a`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.47616,-0.02015,0.03]},{"name":"goal","value":[0.63142,0.15919,0.19002]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.47616,-0.02015,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.63142,0.15919,0.19002]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.54857,"average_solve_count":175.0,"average_success_count":175.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.14064,"approach_1.approach_tolerance":0.01545,"descend_1.descend_speed":0.07534,"descend_1.descend_tolerance":0.01122,"descend_place.place_speed":0.05502,"descend_place.place_tolerance":0.01169,"descend_place.place_z_offset":0.01075,"lift_1.lift_height":0.12521,"lift_1.lift_speed":0.0684,"lift_1.lift_tolerance":0.01616,"transport_1.transport_speed":0.19597,"transport_1.transport_tolerance":0.01694},"optimized_scores":{"best_composite_score":0.25943,"best_fitness_score":0.97943,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":88.0,"contact_point_centroid":[0.47313,-0.01863,-0.00134],"force_p95":0.59273,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.69867,"mean_force":0.13366,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.4622,-0.01896,0.02936]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":7890.0,"contact_point_centroid":[0.45885,-0.0381,0.08408],"force_p95":0.07837,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32239,"mean_force":0.05829,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.45952,-0.0189,0.08145]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":9521.0,"contact_point_centroid":[0.46059,9e-05,0.08413],"force_p95":0.07415,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31632,"mean_force":0.04971,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.45953,-0.0189,0.08243]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.4762,-0.02007,-0.0021],"force_p95":0.15346,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.21867,"mean_force":0.13052,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46461,-0.01899,0.02901]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6520.0,"contact_point_centroid":[0.61932,0.17339,0.18731],"force_p95":0.0689,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19391,"mean_force":0.04754,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.62355,0.1549,0.18423]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6520.0,"contact_point_centroid":[0.62749,0.13607,0.18492],"force_p95":0.07039,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1643,"mean_force":0.04867,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.62355,0.1549,0.18423]},{"body_a":"world","body_b":"grasp_target","contact_count":2316.0,"contact_point_centroid":[0.47616,-0.02015,-0.00194],"force_p95":0.13116,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12284,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48598,-0.00912,0.17309]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5031.0,"contact_point_centroid":[0.46455,0.0001,0.02936],"force_p95":0.06572,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1325,"mean_force":0.04306,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.4634,-0.01897,0.02783]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":17991.0,"contact_point_centroid":[0.54569,0.05198,0.15929],"force_p95":0.07583,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12294,"mean_force":0.05172,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.54322,0.07096,0.15784]},{"body_a":"world","body_b":"grasp_target","contact_count":132.0,"contact_point_centroid":[0.47616,-0.02015,-0.00199],"force_p95":0.12262,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12262,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.47224,-0.0188,0.04096]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":17773.0,"contact_point_centroid":[0.5418,0.09,0.16053],"force_p95":0.07746,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11804,"mean_force":0.05168,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.54339,0.0711,0.15792]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4470.0,"contact_point_centroid":[0.46295,-0.03826,0.03056],"force_p95":0.07665,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0864,"mean_force":0.04912,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46341,-0.01897,0.02783]}],"total_contact_groups":12},"final_pose_error":0.01168,"key_states":{"actual_goal_position":[0.63142,0.15919,0.19002],"final_object_position":[0.62595,0.15806,0.17734],"final_tcp_position":[0.62671,0.15748,0.19022],"realised_goal_position":[0.63142,0.15919,0.19002],"realised_object_initial_position":[0.47616,-0.02015,0.03]},"peak_contact_force":0.69867,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":580.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.03],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28614,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2316.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.4736,-0.01859,0.04509],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.01931,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":33.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.12262,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":132.0,"raw_peak_contact_force":0.12262,"subtask_id":"descend_1","tcp_end":[0.4718,-0.01907,0.03616],"tcp_start":[0.4736,-0.01859,0.04509],"tcp_to_object_dist_end":0.01109,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.47606,-0.01937,0.02564],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28816,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.15154,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11301.0,"raw_peak_contact_force":0.21867,"subtask_id":"grasp_1","tcp_end":[0.46338,-0.01897,0.0278],"tcp_start":[0.4718,-0.01907,0.03616],"tcp_to_object_dist_end":0.01288,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":39.0,"n_steps":447.0,"n_steps_budget":810.0,"object_pos_end":[0.47175,-0.01957,0.13175],"object_pos_start":[0.47606,-0.01937,0.02564],"object_to_goal_dist_end":0.24667,"object_to_goal_dist_start":0.28816,"object_z_max":0.13155,"peak_contact_force":0.07798,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":17499.0,"raw_peak_contact_force":0.69867,"tcp_end":[0.45956,-0.01889,0.13751],"tcp_start":[0.46338,-0.01897,0.0278],"tcp_to_object_dist_end":0.0135,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":923.0,"n_steps_budget":1000.0,"object_pos_end":[0.62038,0.15169,0.16799],"object_pos_start":[0.47175,-0.01957,0.13175],"object_to_goal_dist_end":0.02576,"object_to_goal_dist_start":0.24667,"object_z_max":0.16796,"peak_contact_force":0.06997,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":35764.0,"raw_peak_contact_force":0.12294,"subtask_id":"transport_arc","tcp_end":[0.62085,0.15115,0.17957],"tcp_start":[0.45956,-0.01889,0.13751],"tcp_to_object_dist_end":0.0116,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":326.0,"n_steps_budget":1000.0,"object_pos_end":[0.62595,0.15806,0.17734],"object_pos_start":[0.62038,0.15169,0.16799],"object_to_goal_dist_end":0.01385,"object_to_goal_dist_start":0.02576,"object_z_max":0.17731,"peak_contact_force":0.07045,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":13040.0,"raw_peak_contact_force":0.19391,"subtask_id":"release_1","tcp_end":[0.62671,0.15748,0.19022],"tcp_start":[0.62085,0.15115,0.17957],"tcp_to_object_dist_end":0.01291,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `37495cb43897015e78e007c86af160d11c8460c1ce7249e5c03dce38206c0daf`; realized-scene SHA-256: `5ce27bcdb8582e1d517b17df0f9c2ad7b05701113a75707627744a889253e6a7`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.45856,-0.02632,0.03]},{"name":"goal","value":[0.63013,0.20822,0.11412]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.45856,-0.02632,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.63013,0.20822,0.11412]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.70745,"average_solve_count":188.0,"average_success_count":188.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.13935,"approach_1.approach_tolerance":0.02994,"descend_1.descend_speed":0.05245,"descend_1.descend_tolerance":0.00959,"descend_place.place_speed":0.05821,"descend_place.place_tolerance":0.01774,"descend_place.place_z_offset":0.02177,"lift_1.lift_height":0.137,"lift_1.lift_speed":0.08761,"lift_1.lift_tolerance":0.005,"transport_1.transport_speed":0.21086,"transport_1.transport_tolerance":0.0242},"optimized_scores":{"best_composite_score":0.26097,"best_fitness_score":0.98097,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":207.0,"contact_point_centroid":[0.45476,-0.02397,-0.00132],"force_p95":0.3551,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.66862,"mean_force":0.10564,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44481,-0.02465,0.02876]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":14645.0,"contact_point_centroid":[0.44209,-0.04377,0.09027],"force_p95":0.07819,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29463,"mean_force":0.05585,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.4427,-0.02459,0.08751]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":17495.0,"contact_point_centroid":[0.44394,-0.00558,0.08854],"force_p95":0.07202,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28313,"mean_force":0.04798,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.4427,-0.02459,0.08682]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2500.0,"contact_point_centroid":[0.61222,0.21562,0.11717],"force_p95":0.07067,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27598,"mean_force":0.04948,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.61716,0.19743,0.11344]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.45864,-0.0262,-0.00215],"force_p95":0.16622,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24031,"mean_force":0.13401,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44793,-0.02474,0.02804]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2500.0,"contact_point_centroid":[0.62201,0.17879,0.11349],"force_p95":0.07398,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21294,"mean_force":0.05051,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.61716,0.19743,0.11344]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5242.0,"contact_point_centroid":[0.44757,-0.00563,0.02828],"force_p95":0.0661,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14784,"mean_force":0.0413,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44674,-0.02471,0.02693]},{"body_a":"world","body_b":"grasp_target","contact_count":1348.0,"contact_point_centroid":[0.45856,-0.02632,-0.0019],"force_p95":0.13563,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12299,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48024,-0.01109,0.18192]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":12312.0,"contact_point_centroid":[0.53171,0.06675,0.12955],"force_p95":0.07922,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13529,"mean_force":0.05234,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.52893,0.08571,0.12837]},{"body_a":"world","body_b":"grasp_target","contact_count":328.0,"contact_point_centroid":[0.45856,-0.02632,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.45652,-0.02385,0.04636]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":12365.0,"contact_point_centroid":[0.52658,0.10402,0.13113],"force_p95":0.0741,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.122,"mean_force":0.05124,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.52855,0.08522,0.12849]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4504.0,"contact_point_centroid":[0.446,-0.04402,0.02967],"force_p95":0.07931,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0853,"mean_force":0.04918,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44675,-0.02471,0.02694]},{"body_a":"grasp_target","body_b":"hand","contact_count":18.0,"contact_point_centroid":[0.47422,-0.04447,0.06038],"force_p95":0.0065,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.00739,"mean_force":0.00555,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44383,-0.02463,0.03019]}],"total_contact_groups":13},"final_pose_error":0.01772,"key_states":{"actual_goal_position":[0.63013,0.20822,0.11412],"final_object_position":[0.61502,0.20219,0.10776],"final_tcp_position":[0.62204,0.20292,0.12104],"realised_goal_position":[0.63013,0.20822,0.11412],"realised_object_initial_position":[0.45856,-0.02632,0.03]},"peak_contact_force":0.66862,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":338.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.03],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30252,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1348.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.46038,-0.02289,0.05956],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.03376,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":82.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":328.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.45499,-0.02489,0.03475],"tcp_start":[0.46038,-0.02289,0.05956],"tcp_to_object_dist_end":0.00954,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.4585,-0.02516,0.02548],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30295,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.16292,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11546.0,"raw_peak_contact_force":0.24031,"subtask_id":"grasp_1","tcp_end":[0.44671,-0.02471,0.0269],"tcp_start":[0.45499,-0.02489,0.03475],"tcp_to_object_dist_end":0.01188,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":812.0,"n_steps_budget":870.0,"object_pos_end":[0.45384,-0.02529,0.1435],"object_pos_start":[0.4585,-0.02516,0.02548],"object_to_goal_dist_end":0.29405,"object_to_goal_dist_start":0.30295,"object_z_max":0.14339,"peak_contact_force":0.08027,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":32365.0,"raw_peak_contact_force":0.66862,"tcp_end":[0.44298,-0.02458,0.1527],"tcp_start":[0.44671,-0.02471,0.0269],"tcp_to_object_dist_end":0.01425,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":624.0,"n_steps_budget":1000.0,"object_pos_end":[0.60556,0.19044,0.09582],"object_pos_start":[0.45384,-0.02529,0.1435],"object_to_goal_dist_end":0.03542,"object_to_goal_dist_start":0.29405,"object_z_max":0.14353,"peak_contact_force":0.07587,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":24677.0,"raw_peak_contact_force":0.13529,"subtask_id":"transport_arc","tcp_end":[0.61375,0.19153,0.10838],"tcp_start":[0.44298,-0.02458,0.1527],"tcp_to_object_dist_end":0.01504,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":125.0,"n_steps_budget":1000.0,"object_pos_end":[0.61502,0.20219,0.10776],"object_pos_start":[0.60556,0.19044,0.09582],"object_to_goal_dist_end":0.01747,"object_to_goal_dist_start":0.03542,"object_z_max":0.10765,"peak_contact_force":0.07386,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":5000.0,"raw_peak_contact_force":0.27598,"subtask_id":"release_1","tcp_end":[0.62204,0.20292,0.12104],"tcp_start":[0.61375,0.19153,0.10838],"tcp_to_object_dist_end":0.01505,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```