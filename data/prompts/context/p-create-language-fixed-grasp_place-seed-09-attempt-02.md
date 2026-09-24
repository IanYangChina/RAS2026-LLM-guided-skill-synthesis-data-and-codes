## Search State

- **Seed**: 9
- **Iteration**: 3 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 2 | approach → descend → contact → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | force_threshold_switch | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 3 | 0.2773 | 0.28 | ✅ accepted |
| 1 | approach → descend → contact → grasp → lift → approach → release → retract | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | — | linear_cartesian | position_control | position_control | force_threshold_switch | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | time_limit | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 3 | 0.2489 | 0.23 | ✅ accepted |
| 0 | approach → descend → contact → grasp → lift → approach → release → retract | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | — | linear_cartesian | position_control | position_control | force_threshold_switch | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | time_limit | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 3 | 0.2442 | 0.22 | ✅ accepted |

**Proposal policy**: task_score is 0.28 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.277) — your mutation base

```yaml
skill: grasp_place
dsl_version: 2
skill_type: arm_gripper
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
    - 0.08
    tolerance: 0.005
    orientation:
      mode: keep_current
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
    tolerance: 0.005
    orientation:
      mode: keep_current
  subtask_id: descend_1
- id: contact_1
  type: contact
  generator: linear_cartesian
  control: force_threshold_switch
  termination: force_exceeded
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - -0.015
    orientation:
      mode: keep_current
  parameters:
    contact_force:
      type: scalar
      range:
      - 1.0
      - 20.0
      default: 5.0
      binds_to:
      - path: termination.force_threshold
        mode: replace
  subtask_id: grasp_1
- id: grasp_1
  type: grasp
  control: position_control
  termination: time_limit
  end_effector_action: force_grasp
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0
    orientation:
      mode: keep_current
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
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    lift_height:
      type: scalar
      range:
      - 0.05
      - 0.3
      default: 0.12
      binds_to:
      - path: target.offset_along_axis.distance
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
    - 0.1
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    transport_speed:
      type: scalar
      range:
      - 0.1
      - 1.0
      default: 0.3
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: transport_arc
- id: place_descend
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
    tolerance: 0.005
    orientation:
      mode: keep_current
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
    orientation:
      mode: keep_current
  subtask_id: release_1

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.08], tolerance=0.005
  - orientation: mode=keep_current
  - parameter_bindings: none
- **descend_1** (`descend`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.02], tolerance=0.005
  - orientation: mode=keep_current
  - parameter_bindings: none
- **contact_1** (`contact`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, -0.015]
  - orientation: mode=keep_current
  - parameter_bindings:
    - contact_force: status=consumed; consumers=termination.force_threshold (replace)
- **grasp_1** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings: none
- **lift_1** (`lift`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=world_z, distance=0.1, mode=add_to_offset, sign=positive}, tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset_along_axis.distance (replace)
- **transport_1** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.1], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - transport_speed: status=consumed; consumers=generator.speed (replace)
- **place_descend** (`descend`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], tolerance=0.005
  - orientation: mode=keep_current
  - parameter_bindings: none
- **release_1** (`release`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings: none

## Design Metrics

- **Composite score**: 0.277
- **task_score** (E): 0.284
- **fitness_score**: 0.524  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.083
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.330

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 0.67 | 1.00 | 0.1633 |
| descend_1 | 1.00 | 1.00 | 0.0912 |
| contact_1 | 0.67 | 1.00 | 0.0041 |
| grasp_1 | 1.00 | 1.00 | 0.0120 |
| lift_1 | 1.00 | 1.00 | 0.0802 |
| transport_1 | 0.67 | 1.00 | 0.2429 |
| place_descend | 1.00 | 1.00 | 0.0841 |
| release_1 | 1.00 | 1.00 | 0.0208 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 0.67 / step_budget | (0.500, -0.000, 0.301)→(0.504, -0.012, 0.141) | (0.515, -0.017, 0.030)→(0.515, -0.017, 0.026) | 0.268→0.270 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.504, -0.012, 0.141)→(0.509, -0.016, 0.050) | (0.515, -0.017, 0.026)→(0.515, -0.017, 0.026) | 0.270→0.270 | 1.00 / 4.000 | 0.123 | 0.123 |
| contact_1 | contact | 0.67 / force_exceeded | (0.509, -0.016, 0.050)→(0.508, -0.016, 0.047) | (0.515, -0.017, 0.026)→(0.515, -0.017, 0.026) | 0.270→0.270 | 1.00 / 4.000 | 122.006 | 0.123 |
| grasp_1 | grasp | 1.00 / step_budget | (0.508, -0.016, 0.047)→(0.500, -0.016, 0.038) | (0.515, -0.017, 0.026)→(0.515, -0.016, 0.026) | 0.270→0.270 | 1.00 / 38.000 | 0.148 | 0.182 |
| lift_1 | lift | 1.00 / step_budget | (0.500, -0.016, 0.038)→(0.496, -0.016, 0.118) | (0.515, -0.016, 0.026)→(0.508, -0.016, 0.097) | 0.270→0.247 | 1.00 / 21.333 | 0.132 | 0.507 |
| transport_1 | approach | 0.67 / step_budget | (0.496, -0.016, 0.118)→(0.600, 0.156, 0.241) | (0.508, -0.016, 0.097)→(0.568, 0.066, 0.011) | 0.247→0.212 | 1.00 / 7.000 | 91003.998 | 1.447 |
| place_descend | descend | 1.00 / step_budget | (0.600, 0.156, 0.241)→(0.613, 0.180, 0.162) | (0.568, 0.066, 0.011)→(0.568, 0.064, 0.016) | 0.212→0.207 | 1.00 / 8.000 | 3249.688 | 0.191 |
| release_1 | release | 1.00 / step_budget | (0.613, 0.180, 0.162)→(0.607, 0.178, 0.182) | (0.568, 0.064, 0.016)→(0.568, 0.064, 0.016) | 0.207→0.207 | 1.00 / 4.000 | 0.123 | 0.123 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.490
- phase_score: 0.446
- phase_breakdown.approach_1_score: 0.185
- phase_breakdown.grasp_1_score: 1.000
- phase_breakdown.transport_arc_score: 0.171
- phase_breakdown.descend_1_score: 0.903
- phase_breakdown.release_1_score: 0.679
- grasp_place_fitness: 0.715

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.715
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.490
- **Median Q (composite search score)**: 0.333
- **K-run variance**: 0.0469
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 10.0
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.67669,"average_solve_count":133.0,"average_success_count":133.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"contact_1.contact_force":9.89688,"lift_1.lift_height":0.05098,"transport_1.transport_speed":0.65501},"optimized_scores":{"best_composite_score":-0.01114,"best_fitness_score":0.31886,"best_task_score":0.19459},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":2310.0,"contact_point_centroid":[0.54951,0.08641,-0.00229],"force_p95":0.14504,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.28723,"mean_force":0.13978,"phase_index":5.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.56927,0.12845,0.20319]},{"body_a":"world","body_b":"grasp_target","contact_count":202.0,"contact_point_centroid":[0.53241,-0.02057,-0.00117],"force_p95":0.48569,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.68455,"mean_force":0.12378,"phase_index":4.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51758,-0.02081,0.02354]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4235.0,"contact_point_centroid":[0.52774,0.02881,0.08857],"force_p95":0.17816,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.43413,"mean_force":0.09183,"phase_index":5.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.5232,0.01048,0.089]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6706.0,"contact_point_centroid":[0.51824,-0.0021,0.04392],"force_p95":0.10915,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.40396,"mean_force":0.07329,"phase_index":4.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51512,-0.02075,0.04225]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6707.0,"contact_point_centroid":[0.51856,-0.03938,0.04307],"force_p95":0.10658,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.38197,"mean_force":0.07375,"phase_index":4.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51511,-0.02075,0.04197]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3631.0,"contact_point_centroid":[0.52635,-0.01184,0.08556],"force_p95":0.17523,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30289,"mean_force":0.09565,"phase_index":5.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.52185,0.00674,0.08551]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53701,-0.02114,-0.00206],"force_p95":0.13773,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.18017,"mean_force":0.12775,"phase_index":3.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52078,-0.02087,0.02336]},{"body_a":"world","body_b":"grasp_target","contact_count":3996.0,"contact_point_centroid":[0.53702,-0.02132,-0.00196],"force_p95":0.12459,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12275,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51307,-0.00943,0.21064]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.53702,-0.02132,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.52721,-0.01914,0.08479]},{"body_a":"world","body_b":"grasp_target","contact_count":252.0,"contact_point_centroid":[0.53702,-0.02132,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.52966,-0.02104,0.03761]},{"body_a":"world","body_b":"grasp_target","contact_count":3972.0,"contact_point_centroid":[0.54927,0.08659,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.59996,0.20987,0.226]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.54927,0.08659,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":7.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.60275,0.22382,0.20026]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3672.0,"contact_point_centroid":[0.52225,-0.00195,0.02547],"force_p95":0.09793,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11081,"mean_force":0.05778,"phase_index":3.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51953,-0.02084,0.02197]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3852.0,"contact_point_centroid":[0.5227,-0.03974,0.02429],"force_p95":0.09094,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09361,"mean_force":0.05619,"phase_index":3.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51953,-0.02084,0.02197]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2179.0,"contact_point_centroid":[0.57279,0.13623,0.21303],"force_p95":0.01117,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01643,"mean_force":0.01053,"phase_index":5.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.57236,0.13623,0.21076]},{"body_a":"left_finger","body_b":"right_finger","contact_count":4261.0,"contact_point_centroid":[0.60056,0.20996,0.2281],"force_p95":0.01098,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01286,"mean_force":0.0104,"phase_index":6.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.59999,0.20994,0.22588]}],"total_contact_groups":17},"final_pose_error":0.00864,"key_states":{"actual_goal_position":[0.61031,0.22775,0.20741],"final_object_position":[0.54927,0.08659,0.01602],"final_tcp_position":[0.60638,0.22531,0.20011],"realised_goal_position":[0.61031,0.22775,0.20741],"realised_object_initial_position":[0.53702,-0.02132,0.03]},"peak_contact_force":273011.52073,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.03],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31446,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3996.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.5248,-0.01661,0.1456],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.1203,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.5316,-0.02108,0.04305],"tcp_start":[0.5248,-0.01661,0.1456],"tcp_to_object_dist_end":0.01787,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":63.0,"n_steps_budget":600.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":252.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_1","tcp_end":[0.52804,-0.02101,0.0315],"tcp_start":[0.5316,-0.02108,0.04305],"tcp_to_object_dist_end":0.01053,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":34.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53721,-0.02076,0.02571],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31641,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.13762,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":9324.0,"raw_peak_contact_force":0.18017,"tcp_end":[0.5195,-0.02084,0.02193],"tcp_start":[0.52804,-0.02101,0.0315],"tcp_to_object_dist_end":0.01811,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":27.0,"n_steps":469.0,"n_steps_budget":600.0,"object_pos_end":[0.53224,-0.02072,0.05823],"object_pos_start":[0.53721,-0.02076,0.02571],"object_to_goal_dist_end":0.30015,"object_to_goal_dist_start":0.31641,"object_z_max":0.05818,"peak_contact_force":0.10669,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":13615.0,"raw_peak_contact_force":0.68455,"tcp_end":[0.51476,-0.02074,0.06313],"tcp_start":[0.5195,-0.02084,0.02193],"tcp_to_object_dist_end":0.01816,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.54927,0.08659,0.01602],"object_pos_start":[0.53224,-0.02072,0.05823],"object_to_goal_dist_end":0.24553,"object_to_goal_dist_start":0.30015,"object_z_max":0.10507,"peak_contact_force":273011.52073,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":12355.0,"raw_peak_contact_force":1.28723,"subtask_id":"transport_arc","tcp_end":[0.59454,0.19191,0.26476],"tcp_start":[0.51476,-0.02074,0.06313],"tcp_to_object_dist_end":0.27388,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":993.0,"n_steps_budget":1000.0,"object_pos_end":[0.54927,0.08659,0.01602],"object_pos_start":[0.54927,0.08659,0.01602],"object_to_goal_dist_end":0.24553,"object_to_goal_dist_start":0.24553,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"place_descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":8233.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.60638,0.22531,0.20011],"tcp_start":[0.59454,0.19191,0.26476],"tcp_to_object_dist_end":0.23748,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54927,0.08659,0.01602],"object_pos_start":[0.54927,0.08659,0.01602],"object_to_goal_dist_end":0.24553,"object_to_goal_dist_start":0.24553,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1019.0,"raw_peak_contact_force":0.12263,"subtask_id":"release_1","tcp_end":[0.60139,0.22321,0.21957],"tcp_start":[0.60638,0.22531,0.20011],"tcp_to_object_dist_end":0.25062,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.0,"average_solve_count":115.0,"average_success_count":115.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"contact_1.contact_force":18.74771,"lift_1.lift_height":0.1074,"transport_1.transport_speed":0.39951},"optimized_scores":{"best_composite_score":0.33278,"best_fitness_score":0.53778,"best_task_score":0.16664},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":3681.0,"contact_point_centroid":[0.54927,-0.03357,-0.00219],"force_p95":0.12636,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.29601,"mean_force":0.13322,"phase_index":5.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.57299,0.06367,0.20071]},{"body_a":"world","body_b":"grasp_target","contact_count":159.0,"contact_point_centroid":[0.54312,-0.02573,-0.00136],"force_p95":0.22919,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.36357,"mean_force":0.06195,"phase_index":4.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52757,-0.02717,0.05251]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5088.0,"contact_point_centroid":[0.52993,-0.00876,0.08874],"force_p95":0.14631,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.35929,"mean_force":0.1096,"phase_index":4.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52527,-0.02709,0.09126]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6531.0,"contact_point_centroid":[0.5293,-0.04515,0.08856],"force_p95":0.13743,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.3096,"mean_force":0.09193,"phase_index":4.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52527,-0.02709,0.08979]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.54568,-0.02918,-0.00219],"force_p95":0.17662,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.2235,"mean_force":0.13615,"phase_index":3.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53055,-0.02726,0.05197]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":66.0,"contact_point_centroid":[0.53244,-0.00878,0.14063],"force_p95":0.17874,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20766,"mean_force":0.11787,"phase_index":5.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.52543,-0.02668,0.14551]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":159.0,"contact_point_centroid":[0.53189,-0.04235,0.14138],"force_p95":0.14101,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19345,"mean_force":0.06788,"phase_index":5.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.52558,-0.02581,0.14558]},{"body_a":"world","body_b":"grasp_target","contact_count":3996.0,"contact_point_centroid":[0.5456,-0.02923,-0.00196],"force_p95":0.12459,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12275,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51493,-0.01166,0.21886]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3889.0,"contact_point_centroid":[0.5316,-0.0082,0.04952],"force_p95":0.11402,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13215,"mean_force":0.05675,"phase_index":3.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52934,-0.02723,0.05052]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.5456,-0.02923,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.53152,-0.02415,0.10345]},{"body_a":"world","body_b":"grasp_target","contact_count":4.0,"contact_point_centroid":[0.5456,-0.02923,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.53761,-0.02746,0.06052]},{"body_a":"world","body_b":"grasp_target","contact_count":3688.0,"contact_point_centroid":[0.54939,-0.03354,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.62238,0.15311,0.20207]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.54939,-0.03354,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":7.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.62418,0.16186,0.17016]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4643.0,"contact_point_centroid":[0.53119,-0.04595,0.05106],"force_p95":0.08204,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08659,"mean_force":0.04697,"phase_index":3.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52935,-0.02723,0.05053]},{"body_a":"left_finger","body_b":"right_finger","contact_count":3585.0,"contact_point_centroid":[0.57715,0.07049,0.20758],"force_p95":0.01112,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01641,"mean_force":0.01056,"phase_index":5.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.57684,0.07049,0.20526]},{"body_a":"left_finger","body_b":"right_finger","contact_count":3919.0,"contact_point_centroid":[0.6227,0.15308,0.20444],"force_p95":0.01102,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01285,"mean_force":0.01049,"phase_index":6.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.62236,0.15307,0.2022]}],"total_contact_groups":17},"final_pose_error":0.00838,"key_states":{"actual_goal_position":[0.63284,0.16493,0.17692],"final_object_position":[0.54939,-0.03354,0.01602],"final_tcp_position":[0.62838,0.16308,0.17007],"realised_goal_position":[0.63284,0.16493,0.17692],"realised_object_initial_position":[0.5456,-0.02923,0.03]},"peak_contact_force":9748.81999,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.03],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.25864,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3996.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.52722,-0.01997,0.16384],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.13934,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.53761,-0.02746,0.06052],"tcp_start":[0.52722,-0.01997,0.16384],"tcp_to_object_dist_end":0.03546,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1.0,"n_steps_budget":600.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":160.34347,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":4.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_1","tcp_end":[0.53752,-0.02746,0.0604],"tcp_start":[0.53761,-0.02746,0.06052],"tcp_to_object_dist_end":0.03536,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54578,-0.02774,0.02522],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26022,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.17787,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10332.0,"raw_peak_contact_force":0.2235,"tcp_end":[0.52932,-0.02722,0.05049],"tcp_start":[0.53752,-0.02746,0.0604],"tcp_to_object_dist_end":0.03016,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":14.0,"n_steps":603.0,"n_steps_budget":690.0,"object_pos_end":[0.53189,-0.02737,0.1102],"object_pos_start":[0.54578,-0.02774,0.02522],"object_to_goal_dist_end":0.2272,"object_to_goal_dist_start":0.26022,"object_z_max":0.1101,"peak_contact_force":0.17739,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":11778.0,"raw_peak_contact_force":0.36357,"tcp_end":[0.52525,-0.02709,0.14531],"tcp_start":[0.52932,-0.02722,0.05049],"tcp_to_object_dist_end":0.03573,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.54939,-0.03354,0.01602],"object_pos_start":[0.53189,-0.02737,0.1102],"object_to_goal_dist_end":0.26879,"object_to_goal_dist_start":0.2272,"object_z_max":0.11025,"peak_contact_force":0.12263,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":7491.0,"raw_peak_contact_force":1.29601,"subtask_id":"transport_arc","tcp_end":[0.61684,0.14034,0.25218],"tcp_start":[0.52525,-0.02709,0.14531],"tcp_to_object_dist_end":0.30093,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":922.0,"n_steps_budget":1000.0,"object_pos_end":[0.54939,-0.03354,0.01602],"object_pos_start":[0.54939,-0.03354,0.01602],"object_to_goal_dist_end":0.26879,"object_to_goal_dist_start":0.26879,"object_z_max":0.01602,"peak_contact_force":9748.81999,"phase_name":"place_descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":7607.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.62838,0.16308,0.17007],"tcp_start":[0.61684,0.14034,0.25218],"tcp_to_object_dist_end":0.26198,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54939,-0.03354,0.01602],"object_pos_start":[0.54939,-0.03354,0.01602],"object_to_goal_dist_end":0.26879,"object_to_goal_dist_start":0.26879,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1026.0,"raw_peak_contact_force":0.12263,"subtask_id":"release_1","tcp_end":[0.62256,0.16135,0.18944],"tcp_start":[0.62838,0.16308,0.17007],"tcp_to_object_dist_end":0.27095,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.992,"average_solve_count":125.0,"average_success_count":125.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"contact_1.contact_force":7.94729,"lift_1.lift_height":0.11506,"transport_1.transport_speed":0.78024},"optimized_scores":{"best_composite_score":0.51029,"best_fitness_score":0.71529,"best_task_score":0.48991},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":98.0,"contact_point_centroid":[0.60303,0.1411,-0.0081],"force_p95":1.57039,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.75675,"mean_force":0.64338,"phase_index":5.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.58691,0.13335,0.2051]},{"body_a":"world","body_b":"grasp_target","contact_count":125.0,"contact_point_centroid":[0.46013,0.00013,-0.00107],"force_p95":0.30853,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.47377,"mean_force":0.06181,"phase_index":4.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44944,-0.00022,0.04233]},{"body_a":"world","body_b":"grasp_target","contact_count":3888.0,"contact_point_centroid":[0.60474,0.14042,-0.00209],"force_p95":0.12335,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.32824,"mean_force":0.12164,"phase_index":6.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.59666,0.14392,0.1533]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":10208.0,"contact_point_centroid":[0.44925,0.01873,0.0893],"force_p95":0.10188,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30996,"mean_force":0.06597,"phase_index":4.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44698,-0.00023,0.08721]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":9607.0,"contact_point_centroid":[0.51065,0.03804,0.1689],"force_p95":0.1334,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28221,"mean_force":0.08692,"phase_index":5.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.50471,0.05664,0.16836]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":10865.0,"contact_point_centroid":[0.44926,-0.01909,0.08703],"force_p95":0.10105,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2735,"mean_force":0.06263,"phase_index":4.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.447,-0.00023,0.08544]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":10482.0,"contact_point_centroid":[0.51209,0.07642,0.16922],"force_p95":0.12573,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26935,"mean_force":0.08022,"phase_index":5.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.50613,0.05798,0.16899]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.46285,-4e-05,-0.00202],"force_p95":0.12794,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.14259,"mean_force":0.12443,"phase_index":3.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.45186,-0.00019,0.04164]},{"body_a":"world","body_b":"grasp_target","contact_count":3216.0,"contact_point_centroid":[0.46286,-7e-05,-0.00195],"force_p95":0.12703,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12278,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.47924,-5e-05,0.20559]},{"body_a":"world","body_b":"grasp_target","contact_count":1588.0,"contact_point_centroid":[0.46286,-7e-05,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.45797,-0.00011,0.07929]},{"body_a":"world","body_b":"grasp_target","contact_count":4.0,"contact_point_centroid":[0.46286,-7e-05,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.45822,-0.00012,0.04787]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.60475,0.14044,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":7.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.60004,0.14983,0.11724]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4226.0,"contact_point_centroid":[0.45088,0.01909,0.04268],"force_p95":0.07598,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09429,"mean_force":0.0512,"phase_index":3.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.45079,-0.0002,0.0406]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5332.0,"contact_point_centroid":[0.45035,-0.01926,0.04273],"force_p95":0.06295,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08752,"mean_force":0.0408,"phase_index":3.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.45078,-0.0002,0.0406]},{"body_a":"left_finger","body_b":"right_finger","contact_count":3989.0,"contact_point_centroid":[0.59741,0.1442,0.15383],"force_p95":0.01105,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01642,"mean_force":0.01056,"phase_index":6.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.59692,0.14419,0.15156]},{"body_a":"left_finger","body_b":"right_finger","contact_count":220.0,"contact_point_centroid":[0.60381,0.15074,0.11556],"force_p95":0.01101,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01102,"mean_force":0.01013,"phase_index":7.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.60325,0.15072,0.11337]}],"total_contact_groups":16},"final_pose_error":0.00805,"key_states":{"actual_goal_position":[0.61015,0.15287,0.12219],"final_object_position":[0.60475,0.14044,0.01602],"final_tcp_position":[0.60491,0.15114,0.11633],"realised_goal_position":[0.61015,0.15287,0.12219],"realised_object_initial_position":[0.46286,-7e-05,0.03]},"peak_contact_force":205.55248,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":805.0,"n_steps_budget":1000.0,"object_pos_end":[0.46286,-7e-05,0.02602],"object_pos_start":[0.46286,-7e-05,0.03],"object_to_goal_dist_end":0.2331,"object_to_goal_dist_start":0.23148,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3216.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.46064,-9e-05,0.11433],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.08834,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":397.0,"n_steps_budget":1000.0,"object_pos_end":[0.46286,-7e-05,0.02602],"object_pos_start":[0.46286,-7e-05,0.02602],"object_to_goal_dist_end":0.2331,"object_to_goal_dist_start":0.2331,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1588.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.45822,-0.00012,0.04787],"tcp_start":[0.46064,-9e-05,0.11433],"tcp_to_object_dist_end":0.02234,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1.0,"n_steps_budget":600.0,"object_pos_end":[0.46286,-7e-05,0.02602],"object_pos_start":[0.46286,-7e-05,0.02602],"object_to_goal_dist_end":0.2331,"object_to_goal_dist_start":0.2331,"object_z_max":0.02602,"peak_contact_force":205.55248,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":4.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_1","tcp_end":[0.45813,-0.00012,0.04775],"tcp_start":[0.45822,-0.00012,0.04787],"tcp_to_object_dist_end":0.02224,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.46276,1e-05,0.02591],"object_pos_start":[0.46286,-7e-05,0.02602],"object_to_goal_dist_end":0.23314,"object_to_goal_dist_start":0.2331,"object_z_max":0.02602,"peak_contact_force":0.12783,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11358.0,"raw_peak_contact_force":0.14259,"tcp_end":[0.45076,-0.0002,0.04057],"tcp_start":[0.45813,-0.00012,0.04775],"tcp_to_object_dist_end":0.01895,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":663.0,"n_steps_budget":750.0,"object_pos_end":[0.45986,-0.00022,0.12247],"object_pos_start":[0.46276,1e-05,0.02591],"object_to_goal_dist_end":0.21453,"object_to_goal_dist_start":0.23314,"object_z_max":0.12236,"peak_contact_force":0.11144,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":21198.0,"raw_peak_contact_force":0.47377,"tcp_end":[0.44703,-0.00022,0.1447],"tcp_start":[0.45076,-0.0002,0.04057],"tcp_to_object_dist_end":0.02567,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.60647,0.14445,0.00167],"object_pos_start":[0.45986,-0.00022,0.12247],"object_to_goal_dist_end":0.12086,"object_to_goal_dist_start":0.21453,"object_z_max":0.16316,"peak_contact_force":0.3511,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":20187.0,"raw_peak_contact_force":1.75675,"subtask_id":"transport_arc","tcp_end":[0.58941,0.1356,0.2062],"tcp_start":[0.44703,-0.00022,0.1447],"tcp_to_object_dist_end":0.20542,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":972.0,"n_steps_budget":1000.0,"object_pos_end":[0.60475,0.14044,0.01602],"object_pos_start":[0.60647,0.14445,0.00167],"object_to_goal_dist_end":0.10703,"object_to_goal_dist_start":0.12086,"object_z_max":0.01668,"peak_contact_force":0.12263,"phase_name":"place_descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":7877.0,"raw_peak_contact_force":0.32824,"tcp_end":[0.60491,0.15114,0.11633],"tcp_start":[0.58941,0.1356,0.2062],"tcp_to_object_dist_end":0.10088,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.60475,0.14044,0.01602],"object_pos_start":[0.60475,0.14044,0.01602],"object_to_goal_dist_end":0.10703,"object_to_goal_dist_start":0.10703,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1020.0,"raw_peak_contact_force":0.12263,"subtask_id":"release_1","tcp_end":[0.59811,0.14928,0.13693],"tcp_start":[0.60491,0.15114,0.11633],"tcp_to_object_dist_end":0.12141,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```