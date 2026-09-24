## Search State

- **Seed**: 1
- **Iteration**: 11 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 10 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | admittance_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 5 | 0.2160 | 0.37 | ❌ rejected |
| 9 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | admittance_control | position_control | position_control | impedance_control | admittance_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 6 | 0.2929 | 0.38 | ❌ rejected |
| 8 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | admittance_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 5 | 0.1161 | 0.17 | ❌ rejected |
| 7 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | position_control | admittance_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 7 | 0.1617 | 0.34 | ❌ rejected |
| 6 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | admittance_control | position_control | position_control | impedance_control | admittance_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 7 | 0.2287 | 0.35 | ❌ rejected |

**Proposal policy**: task_score is 0.37 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.216) — your mutation base

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
    - 0.2
    tolerance: 0.02
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - -1.0
      align_with: world_z
      tolerance: 0.1
  parameters:
    approach_height:
      type: scalar
      range:
      - 0.05
      - 0.3
      default: 0.2
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: approach_1
- id: descend_1
  type: descend
  generator: linear_cartesian
  control: admittance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    entity: grasp_target
    offset:
    - 0.0
    - 0.0
    - 0.02
    tolerance: 0.02
    orientation:
      mode: keep_current
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
    - 0.2
    tolerance: 0.02
    orientation:
      mode: keep_current
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
- id: transport_arc
  type: approach
  generator: arc_cartesian
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
      mode: keep_current
  parameters:
    transport_arc_height:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.15
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: transport_arc
- id: descend_2
  type: descend
  generator: linear_cartesian
  control: admittance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.01
    tolerance: 0.02
    orientation:
      mode: keep_current
- id: release_1
  type: release
  control: position_control
  termination: pose_tolerance
  end_effector_action: open
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0
  subtask_id: release_1
- id: retract_1
  type: retract
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
      mode: keep_current

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.2], tolerance=0.02
  - orientation: mode=align_axis, axis=[0.0, 0.0, -1.0], align_with=world_z, tolerance=0.1
  - parameter_bindings:
    - approach_height: status=consumed; consumers=target.offset.z (replace)
- **descend_1** (`descend`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.02], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - grasp_z_offset: status=consumed; consumers=target.offset.z (replace)
- **grasp_1** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings: none
- **lift_1** (`lift`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.2], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset.z (replace)
- **transport_arc** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.15], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - transport_arc_height: status=consumed; consumers=target.offset.z (replace)
- **descend_2** (`descend`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.01], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings: none
- **release_1** (`release`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings: none
- **retract_1** (`retract`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.15], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings: none

## Design Metrics

- **Composite score**: 0.216
- **task_score** (E): 0.370
- **fitness_score**: 0.646  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.430

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1260 |
| descend_1 | 1.00 | 1.00 | 0.1254 |
| grasp_1 | 1.00 | 1.00 | 0.0116 |
| lift_1 | 1.00 | 1.00 | 0.1438 |
| transport_to_goal | 1.00 | 1.00 | 0.2446 |
| descend_to_place | 1.00 | 1.00 | 0.0914 |
| release_1 | 1.00 | 1.00 | 0.0205 |
| retract_1 | 1.00 | 1.00 | 0.0909 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.481, 0.000, 0.182) | (0.479, -0.000, 0.030)→(0.479, -0.000, 0.026) | 0.276→0.278 | 1.00 / 4.000 | 11.479 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.481, 0.000, 0.182)→(0.475, -0.000, 0.057) | (0.479, -0.000, 0.026)→(0.479, -0.000, 0.026) | 0.278→0.278 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_1 | grasp | 1.00 / step_budget | (0.475, -0.000, 0.057)→(0.467, -0.000, 0.048) | (0.479, -0.000, 0.026)→(0.479, -0.000, 0.025) | 0.278→0.278 | 1.00 / 41.333 | 0.165 | 0.214 |
| lift_1 | lift | 1.00 / step_budget | (0.467, -0.000, 0.048)→(0.474, -0.000, 0.192) | (0.479, -0.000, 0.025)→(0.488, -0.001, 0.164) | 0.278→0.245 | 1.00 / 23.667 | 0.116 | 0.389 |
| transport_to_goal | approach | 1.00 / step_budget | (0.474, -0.000, 0.192)→(0.599, 0.192, 0.262) | (0.488, -0.001, 0.164)→(0.581, 0.138, 0.011) | 0.245→0.161 | 1.00 / 7.000 | 94253.499 | 1.946 |
| descend_to_place | descend | 1.00 / step_budget | (0.599, 0.192, 0.262)→(0.603, 0.201, 0.171) | (0.581, 0.138, 0.011)→(0.581, 0.137, 0.016) | 0.161→0.157 | 1.00 / 8.000 | 3249.660 | 0.144 |
| release_1 | release | 1.00 / step_budget | (0.603, 0.201, 0.171)→(0.598, 0.199, 0.190) | (0.581, 0.137, 0.016)→(0.581, 0.137, 0.016) | 0.157→0.157 | 1.00 / 4.000 | 0.123 | 0.123 |
| retract_1 | retract | 1.00 / step_budget | (0.598, 0.199, 0.190)→(0.605, 0.203, 0.281) | (0.581, 0.137, 0.016)→(0.581, 0.137, 0.016) | 0.157→0.157 | 1.00 / 4.000 | 0.123 | 0.123 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.518
- phase_score: 0.310
- phase_breakdown.descend_1_score: 0.884
- phase_breakdown.transport_arc_score: 0.000
- phase_breakdown.grasp_1_score: 1.000
- phase_breakdown.release_1_score: 0.476
- phase_breakdown.approach_1_score: 0.011
- grasp_place_fitness: 0.721

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.721
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.518
- **Median Q (composite search score)**: 0.210
- **K-run variance**: 0.0035
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.320


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.92188,"average_solve_count":192.0,"average_success_count":192.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.14022,"descend_1.grasp_z_offset":0.01057,"descend_to_place.place_z_offset":0.01025,"lift_1.lift_height":0.17992,"transport_to_goal.transport_height":0.13895},"optimized_scores":{"best_composite_score":0.21046,"best_fitness_score":0.64046,"best_task_score":0.35679},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":1208.0,"contact_point_centroid":[0.54484,0.16472,-0.00293],"force_p95":0.47324,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.10005,"mean_force":0.16141,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.54394,0.19117,0.25257]},{"body_a":"world","body_b":"grasp_target","contact_count":81.0,"contact_point_centroid":[0.49935,0.04226,-0.00151],"force_p95":0.37318,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.41382,"mean_force":0.08127,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.4878,0.04253,0.04832]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2837.0,"contact_point_centroid":[0.51214,0.05892,0.19848],"force_p95":0.16355,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31381,"mean_force":0.08899,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.50607,0.07753,0.19885]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":7058.0,"contact_point_centroid":[0.49325,0.06156,0.10917],"force_p95":0.11077,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29604,"mean_force":0.06967,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49047,0.04265,0.10793]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6682.0,"contact_point_centroid":[0.49279,0.02377,0.1089],"force_p95":0.11123,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27314,"mean_force":0.07105,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49047,0.04265,0.10803]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50125,0.0449,-0.00219],"force_p95":0.17552,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.23287,"mean_force":0.13647,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.48998,0.04275,0.04791]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3135.0,"contact_point_centroid":[0.51384,0.10043,0.20052],"force_p95":0.12917,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21086,"mean_force":0.08245,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.5075,0.08207,0.20087]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4208.0,"contact_point_centroid":[0.48904,0.02349,0.04827],"force_p95":0.07991,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15764,"mean_force":0.05068,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.48889,0.04265,0.04673]},{"body_a":"world","body_b":"grasp_target","contact_count":900.0,"contact_point_centroid":[0.50118,0.04505,-0.00186],"force_p95":0.13709,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12317,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49863,0.01757,0.24502]},{"body_a":"world","body_b":"grasp_target","contact_count":1008.0,"contact_point_centroid":[0.50118,0.04505,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49678,0.03994,0.12234]},{"body_a":"world","body_b":"grasp_target","contact_count":1188.0,"contact_point_centroid":[0.54484,0.16475,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.55826,0.23626,0.21901]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.54484,0.16475,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.55592,0.2396,0.16603]},{"body_a":"world","body_b":"grasp_target","contact_count":1384.0,"contact_point_centroid":[0.54484,0.16475,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":7.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.55669,0.24049,0.2311]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4881.0,"contact_point_centroid":[0.48945,0.06188,0.04824],"force_p95":0.07897,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08069,"mean_force":0.04556,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.4889,0.04265,0.04674]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1088.0,"contact_point_centroid":[0.54644,0.19756,0.25797],"force_p95":0.01208,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01584,"mean_force":0.01066,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.54611,0.19753,0.25564]},{"body_a":"left_finger","body_b":"right_finger","contact_count":217.0,"contact_point_centroid":[0.55879,0.24084,0.16375],"force_p95":0.01106,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01279,"mean_force":0.01027,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.55838,0.2408,0.16164]}],"total_contact_groups":17},"final_pose_error":0.01999,"key_states":{"actual_goal_position":[0.56442,0.24486,0.14677],"final_object_position":[0.54484,0.16475,0.01602],"final_tcp_position":[0.56104,0.24302,0.27716],"realised_goal_position":[0.56442,0.24486,0.14677],"realised_object_initial_position":[0.50118,0.04505,0.03]},"peak_contact_force":9748.73525,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":226.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.03],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.23992,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":900.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.49824,0.03676,0.18794],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.16216,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":252.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"peak_contact_force":0.12262,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1008.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.49705,0.04335,0.05591],"tcp_start":[0.49824,0.03676,0.18794],"tcp_to_object_dist_end":0.03022,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50117,0.04347,0.02532],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.24354,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"peak_contact_force":0.17017,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10889.0,"raw_peak_contact_force":0.23287,"subtask_id":"grasp_1","tcp_end":[0.48886,0.04265,0.0467],"tcp_start":[0.49705,0.04335,0.05591],"tcp_to_object_dist_end":0.02469,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":25.0,"n_steps":449.0,"n_steps_budget":990.0,"object_pos_end":[0.51107,0.0438,0.15947],"object_pos_start":[0.50117,0.04347,0.02532],"object_to_goal_dist_end":0.20841,"object_to_goal_dist_start":0.24354,"object_z_max":0.15921,"peak_contact_force":0.10508,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":13821.0,"raw_peak_contact_force":0.41382,"tcp_end":[0.49671,0.04307,0.18596],"tcp_start":[0.48886,0.04265,0.0467],"tcp_to_object_dist_end":0.03014,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":666.0,"n_steps_budget":1000.0,"object_pos_end":[0.54484,0.16475,0.01602],"object_pos_start":[0.51107,0.0438,0.15947],"object_to_goal_dist_end":0.15459,"object_to_goal_dist_start":0.20841,"object_z_max":0.18743,"peak_contact_force":9748.70348,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":8268.0,"raw_peak_contact_force":2.10005,"tcp_end":[0.55794,0.23195,0.2722],"tcp_start":[0.49671,0.04307,0.18596],"tcp_to_object_dist_end":0.26517,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":7.0,"n_steps":297.0,"n_steps_budget":1000.0,"object_pos_end":[0.54484,0.16475,0.01602],"object_pos_start":[0.54484,0.16475,0.01602],"object_to_goal_dist_end":0.15459,"object_to_goal_dist_start":0.15459,"object_z_max":0.01602,"peak_contact_force":9748.73525,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2442.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.56015,0.24152,0.16519],"tcp_start":[0.55794,0.23195,0.2722],"tcp_to_object_dist_end":0.16846,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54484,0.16475,0.01602],"object_pos_start":[0.54484,0.16475,0.01602],"object_to_goal_dist_end":0.15459,"object_to_goal_dist_start":0.15459,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1017.0,"raw_peak_contact_force":0.12263,"subtask_id":"release_1","tcp_end":[0.55444,0.23887,0.186],"tcp_start":[0.56015,0.24152,0.16519],"tcp_to_object_dist_end":0.18568,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":346.0,"n_steps_budget":720.0,"object_pos_end":[0.54484,0.16475,0.01602],"object_pos_start":[0.54484,0.16475,0.01602],"object_to_goal_dist_end":0.15459,"object_to_goal_dist_start":0.15459,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1384.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.56104,0.24302,0.27716],"tcp_start":[0.55444,0.23887,0.186],"tcp_to_object_dist_end":0.2731,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.81959,"average_solve_count":194.0,"average_success_count":194.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.05055,"descend_1.grasp_z_offset":0.01289,"descend_to_place.place_z_offset":0.01995,"lift_1.lift_height":0.18221,"transport_to_goal.transport_height":0.09201},"optimized_scores":{"best_composite_score":0.14624,"best_fitness_score":0.57624,"best_task_score":0.23495},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":1698.0,"contact_point_centroid":[0.56167,0.04933,-0.00263],"force_p95":0.27749,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.76644,"mean_force":0.14997,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.57943,0.10381,0.24583]},{"body_a":"world","body_b":"grasp_target","contact_count":80.0,"contact_point_centroid":[0.47451,-0.01796,-0.00156],"force_p95":0.32302,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.36888,"mean_force":0.07098,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46386,-0.01898,0.05147]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2843.0,"contact_point_centroid":[0.50191,-0.00784,0.19913],"force_p95":0.11423,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.3312,"mean_force":0.07612,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.49568,0.0099,0.19935]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6266.0,"contact_point_centroid":[0.46799,-0.0,0.10815],"force_p95":0.1398,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32572,"mean_force":0.07302,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46605,-0.01901,0.10852]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":7130.0,"contact_point_centroid":[0.46836,-0.03734,0.11139],"force_p95":0.11309,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2691,"mean_force":0.06598,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46623,-0.01902,0.11107]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1624.0,"contact_point_centroid":[0.49911,0.02553,0.19573],"force_p95":0.1778,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25621,"mean_force":0.12668,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.49321,0.007,0.19808]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.47621,-0.02018,-0.00214],"force_p95":0.16836,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.20053,"mean_force":0.13316,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46599,-0.01904,0.05091]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4241.0,"contact_point_centroid":[0.46561,0.00021,0.05043],"force_p95":0.0994,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14215,"mean_force":0.05655,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46494,-0.01901,0.04985]},{"body_a":"world","body_b":"grasp_target","contact_count":1508.0,"contact_point_centroid":[0.47616,-0.02015,-0.00191],"force_p95":0.13496,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12295,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48741,-0.00865,0.20107]},{"body_a":"world","body_b":"grasp_target","contact_count":344.0,"contact_point_centroid":[0.47616,-0.02015,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.47369,-0.01845,0.0798]},{"body_a":"world","body_b":"grasp_target","contact_count":604.0,"contact_point_centroid":[0.56171,0.04935,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.6224,0.15209,0.2436]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.56171,0.04935,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.6218,0.1546,0.21683]},{"body_a":"world","body_b":"grasp_target","contact_count":1372.0,"contact_point_centroid":[0.56171,0.04935,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":7.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.62364,0.15588,0.27798]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4949.0,"contact_point_centroid":[0.46498,-0.03788,0.05038],"force_p95":0.07084,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07408,"mean_force":0.0427,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46494,-0.01901,0.04985]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1590.0,"contact_point_centroid":[0.58476,0.10957,0.251],"force_p95":0.01221,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01649,"mean_force":0.01061,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.58464,0.10957,0.24874]},{"body_a":"left_finger","body_b":"right_finger","contact_count":648.0,"contact_point_centroid":[0.62271,0.15212,0.2458],"force_p95":0.01105,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01284,"mean_force":0.01041,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.62242,0.15211,0.24351]}],"total_contact_groups":17},"final_pose_error":0.0198,"key_states":{"actual_goal_position":[0.63142,0.15919,0.19002],"final_object_position":[0.56171,0.04935,0.01602],"final_tcp_position":[0.62847,0.15801,0.32047],"realised_goal_position":[0.63142,0.15919,0.19002],"realised_object_initial_position":[0.47616,-0.02015,0.03]},"peak_contact_force":273011.58841,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":378.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.03],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28614,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1508.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.47551,-0.01779,0.09999],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.07401,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":86.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.12262,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":344.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.47277,-0.01918,0.05812],"tcp_start":[0.47551,-0.01779,0.09999],"tcp_to_object_dist_end":0.0323,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":42.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.47615,-0.01928,0.02523],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.2883,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.17487,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10990.0,"raw_peak_contact_force":0.20053,"subtask_id":"grasp_1","tcp_end":[0.46491,-0.01901,0.04982],"tcp_start":[0.47277,-0.01918,0.05812],"tcp_to_object_dist_end":0.02704,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":21.0,"n_steps":430.0,"n_steps_budget":990.0,"object_pos_end":[0.4838,-0.02073,0.15819],"object_pos_start":[0.47615,-0.01928,0.02523],"object_to_goal_dist_end":0.2349,"object_to_goal_dist_start":0.2883,"object_z_max":0.15792,"peak_contact_force":0.14351,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":13476.0,"raw_peak_contact_force":0.36888,"tcp_end":[0.47187,-0.01914,0.18814],"tcp_start":[0.46491,-0.01901,0.04982],"tcp_to_object_dist_end":0.03228,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":749.0,"n_steps_budget":1000.0,"object_pos_end":[0.56171,0.04935,0.01602],"object_pos_start":[0.4838,-0.02073,0.15819],"object_to_goal_dist_end":0.21726,"object_to_goal_dist_start":0.2349,"object_z_max":0.17772,"peak_contact_force":273011.58841,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":7755.0,"raw_peak_contact_force":1.76644,"tcp_end":[0.6206,0.14905,0.26893],"tcp_start":[0.47187,-0.01914,0.18814],"tcp_to_object_dist_end":0.27816,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":151.0,"n_steps_budget":1000.0,"object_pos_end":[0.56171,0.04935,0.01602],"object_pos_start":[0.56171,0.04935,0.01602],"object_to_goal_dist_end":0.21726,"object_to_goal_dist_start":0.21726,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1252.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.62559,0.15565,0.21714],"tcp_start":[0.6206,0.14905,0.26893],"tcp_to_object_dist_end":0.23628,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.56171,0.04935,0.01602],"object_pos_start":[0.56171,0.04935,0.01602],"object_to_goal_dist_end":0.21726,"object_to_goal_dist_start":0.21726,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1028.0,"raw_peak_contact_force":0.12263,"subtask_id":"release_1","tcp_end":[0.6205,0.15417,0.23626],"tcp_start":[0.62559,0.15565,0.21714],"tcp_to_object_dist_end":0.2509,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":343.0,"n_steps_budget":660.0,"object_pos_end":[0.56171,0.04935,0.01602],"object_pos_start":[0.56171,0.04935,0.01602],"object_to_goal_dist_end":0.21726,"object_to_goal_dist_start":0.21726,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1372.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.62847,0.15801,0.32047],"tcp_start":[0.6205,0.15417,0.23626],"tcp_to_object_dist_end":0.33008,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.92991,"average_solve_count":214.0,"average_success_count":214.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.21305,"descend_1.grasp_z_offset":0.01014,"descend_to_place.place_z_offset":0.00832,"lift_1.lift_height":0.19513,"transport_to_goal.transport_height":0.14053},"optimized_scores":{"best_composite_score":0.29144,"best_fitness_score":0.72144,"best_task_score":0.51774},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":116.0,"contact_point_centroid":[0.63414,0.19797,-0.00957],"force_p95":1.60274,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.97235,"mean_force":0.61948,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.61614,0.19215,0.24286]},{"body_a":"world","body_b":"grasp_target","contact_count":75.0,"contact_point_centroid":[0.45645,-0.02467,-0.00142],"force_p95":0.34672,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.38435,"mean_force":0.08206,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44765,-0.02496,0.04936]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":7809.0,"contact_point_centroid":[0.52506,0.04507,0.21532],"force_p95":0.12562,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.3111,"mean_force":0.08408,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.51904,0.06362,0.21611]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8154.0,"contact_point_centroid":[0.4512,-0.04393,0.11701],"force_p95":0.10343,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2769,"mean_force":0.06251,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44953,-0.025,0.11609]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":7314.0,"contact_point_centroid":[0.4516,-0.00599,0.11786],"force_p95":0.10756,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27688,"mean_force":0.06809,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44958,-0.02501,0.11711]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.45859,-0.02623,-0.00211],"force_p95":0.15413,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.2101,"mean_force":0.13089,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44973,-0.02503,0.04886]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8152.0,"contact_point_centroid":[0.52759,0.08543,0.21624],"force_p95":0.12198,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19451,"mean_force":0.07976,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.52153,0.06694,0.21678]},{"body_a":"world","body_b":"grasp_target","contact_count":1212.0,"contact_point_centroid":[0.63493,0.19804,-0.00226],"force_p95":0.12525,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.18812,"mean_force":0.11613,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.62077,0.20003,0.18692]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4095.0,"contact_point_centroid":[0.4496,-0.00578,0.04884],"force_p95":0.08002,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14779,"mean_force":0.05215,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44871,-0.025,0.04788]},{"body_a":"world","body_b":"grasp_target","contact_count":432.0,"contact_point_centroid":[0.45856,-0.02632,-0.00171],"force_p95":0.13814,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12378,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48563,-0.00828,0.27952]},{"body_a":"world","body_b":"grasp_target","contact_count":1544.0,"contact_point_centroid":[0.45856,-0.02632,-0.00199],"force_p95":0.12264,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12264,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.46241,-0.02153,0.1565]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.63495,0.19807,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.61948,0.20328,0.12931]},{"body_a":"world","body_b":"grasp_target","contact_count":1608.0,"contact_point_centroid":[0.63495,0.19807,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":7.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.62071,0.20416,0.19626]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4971.0,"contact_point_centroid":[0.44878,-0.04409,0.04901],"force_p95":0.07159,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07389,"mean_force":0.04411,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44871,-0.025,0.04788]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1199.0,"contact_point_centroid":[0.62118,0.20028,0.18558],"force_p95":0.01267,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01561,"mean_force":0.0108,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.62089,0.20026,0.18337]},{"body_a":"left_finger","body_b":"right_finger","contact_count":218.0,"contact_point_centroid":[0.62268,0.20443,0.12802],"force_p95":0.01099,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01099,"mean_force":0.01018,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.62246,0.20441,0.12586]}],"total_contact_groups":16},"final_pose_error":0.02,"key_states":{"actual_goal_position":[0.63013,0.20822,0.11412],"final_object_position":[0.63495,0.19807,0.01602],"final_tcp_position":[0.62623,0.20658,0.24457],"realised_goal_position":[0.63013,0.20822,0.11412],"realised_object_initial_position":[0.45856,-0.02632,0.03]},"peak_contact_force":34.19131,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":109.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.03],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30252,"object_z_max":0.03,"peak_contact_force":34.19131,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":432.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.4699,-0.01796,0.25696],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.23137,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":386.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.12262,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1544.0,"raw_peak_contact_force":0.12264,"subtask_id":"descend_1","tcp_end":[0.45638,-0.02525,0.05566],"tcp_start":[0.4699,-0.01796,0.25696],"tcp_to_object_dist_end":0.02975,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.45851,-0.02538,0.02559],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30308,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.15088,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10866.0,"raw_peak_contact_force":0.2101,"subtask_id":"grasp_1","tcp_end":[0.44868,-0.02499,0.04785],"tcp_start":[0.45638,-0.02525,0.05566],"tcp_to_object_dist_end":0.02433,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":25.0,"n_steps":467.0,"n_steps_budget":1000.0,"object_pos_end":[0.46899,-0.02568,0.1747],"object_pos_start":[0.45851,-0.02538,0.02559],"object_to_goal_dist_end":0.29042,"object_to_goal_dist_start":0.30308,"object_z_max":0.17442,"peak_contact_force":0.10006,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":15543.0,"raw_peak_contact_force":0.38435,"tcp_end":[0.45458,-0.02519,0.20118],"tcp_start":[0.44868,-0.02499,0.04785],"tcp_to_object_dist_end":0.03015,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":822.0,"n_steps_budget":1000.0,"object_pos_end":[0.63576,0.20025,0.00193],"object_pos_start":[0.46899,-0.02568,0.1747],"object_to_goal_dist_end":0.11261,"object_to_goal_dist_start":0.29042,"object_z_max":0.20262,"peak_contact_force":0.2059,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":16077.0,"raw_peak_contact_force":1.97235,"tcp_end":[0.61904,0.19592,0.24373],"tcp_start":[0.45458,-0.02519,0.20118],"tcp_to_object_dist_end":0.24242,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":303.0,"n_steps_budget":1000.0,"object_pos_end":[0.63495,0.19807,0.01602],"object_pos_start":[0.63576,0.20025,0.00193],"object_to_goal_dist_end":0.09874,"object_to_goal_dist_start":0.11261,"object_z_max":0.01673,"peak_contact_force":0.12263,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2411.0,"raw_peak_contact_force":0.18812,"tcp_end":[0.62448,0.20504,0.12993],"tcp_start":[0.61904,0.19592,0.24373],"tcp_to_object_dist_end":0.1146,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.63495,0.19807,0.01602],"object_pos_start":[0.63495,0.19807,0.01602],"object_to_goal_dist_end":0.09874,"object_to_goal_dist_start":0.09874,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1018.0,"raw_peak_contact_force":0.12263,"subtask_id":"release_1","tcp_end":[0.61768,0.20259,0.14865],"tcp_start":[0.62448,0.20504,0.12993],"tcp_to_object_dist_end":0.13382,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":402.0,"n_steps_budget":750.0,"object_pos_end":[0.63495,0.19807,0.01602],"object_pos_start":[0.63495,0.19807,0.01602],"object_to_goal_dist_end":0.09874,"object_to_goal_dist_start":0.09874,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1608.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.62623,0.20658,0.24457],"tcp_start":[0.61768,0.20259,0.14865],"tcp_to_object_dist_end":0.22888,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```