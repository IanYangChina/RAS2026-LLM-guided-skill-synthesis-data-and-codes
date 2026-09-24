## Search State

- **Seed**: 1
- **Iteration**: 4 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 3 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | admittance_control | position_control | position_control | position_control | admittance_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 4 | 0.2735 | 0.38 | ✅ accepted |
| 2 | approach → descend → grasp → lift → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | position_control | admittance_control | position_control | position_control | admittance_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | 4 | 0.3448 | 0.34 | ✅ accepted |
| 1 | approach → descend → grasp → lift → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | position_control | admittance_control | position_control | position_control | admittance_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | 4 | 0.3429 | 0.34 | ❌ rejected |
| 0 | approach → descend → grasp → lift → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | position_control | admittance_control | position_control | position_control | admittance_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | 4 | 0.3438 | 0.34 | ✅ accepted |

**Proposal policy**: task_score is 0.38 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.274) — your mutation base

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

- **Composite score**: 0.274
- **task_score** (E): 0.383
- **fitness_score**: 0.654  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.380

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.0250 |
| descend_1 | 1.00 | 1.00 | 0.2469 |
| grasp_1 | 1.00 | 1.00 | 0.0116 |
| lift_1 | 1.00 | 1.00 | 0.1173 |
| transport_arc | 1.00 | 0.67 | 0.2434 |
| descend_2 | 1.00 | 1.00 | 0.0497 |
| release_1 | 1.00 | 1.00 | 0.0199 |
| retract_1 | 1.00 | 1.00 | 0.0854 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.487, 0.001, 0.302) | (0.479, -0.000, 0.030)→(0.479, -0.000, 0.026) | 0.276→0.278 | 1.00 / 4.000 | 0.126 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.487, 0.001, 0.302)→(0.476, -0.000, 0.056) | (0.479, -0.000, 0.026)→(0.479, -0.000, 0.026) | 0.278→0.278 | 1.00 / 4.000 | 0.123 | 0.127 |
| grasp_1 | grasp | 1.00 / step_budget | (0.476, -0.000, 0.056)→(0.468, -0.000, 0.048) | (0.479, -0.000, 0.026)→(0.479, -0.000, 0.025) | 0.278→0.278 | 1.00 / 41.333 | 0.160 | 0.220 |
| lift_1 | lift | 1.00 / step_budget | (0.468, -0.000, 0.048)→(0.474, -0.000, 0.165) | (0.479, -0.000, 0.025)→(0.488, -0.000, 0.139) | 0.278→0.246 | 1.00 / 25.667 | 0.104 | 0.388 |
| transport_arc | approach | 1.00 / step_budget | (0.474, -0.000, 0.165)→(0.597, 0.190, 0.226) | (0.488, -0.000, 0.139)→(0.582, 0.160, 0.040) | 0.246→0.129 | 0.67 / 4.000 | 0.364 | 1.306 |
| descend_2 | descend | 1.00 / step_budget | (0.597, 0.190, 0.226)→(0.602, 0.197, 0.177) | (0.582, 0.160, 0.040)→(0.586, 0.161, 0.016) | 0.129→0.153 | 1.00 / 8.333 | 91005.358 | 0.936 |
| release_1 | release | 1.00 / step_budget | (0.602, 0.197, 0.177)→(0.596, 0.195, 0.196) | (0.586, 0.161, 0.016)→(0.586, 0.160, 0.016) | 0.153→0.153 | 1.00 / 4.000 | 0.123 | 0.129 |
| retract_1 | retract | 1.00 / step_budget | (0.596, 0.195, 0.196)→(0.605, 0.202, 0.281) | (0.586, 0.160, 0.016)→(0.586, 0.160, 0.016) | 0.153→0.153 | 1.00 / 4.000 | 0.123 | 0.123 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: 1.000
- terminal_score: 0.516
- phase_score: 0.379
- phase_breakdown.descend_1_score: 0.885
- phase_breakdown.transport_arc_score: 0.151
- phase_breakdown.grasp_1_score: 1.000
- phase_breakdown.release_1_score: 0.380
- phase_breakdown.approach_1_score: 0.004
- grasp_place_fitness: 0.721

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.721
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.516
- **Median Q (composite search score)**: 0.289
- **K-run variance**: 0.0039
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.428


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.72396,"average_solve_count":192.0,"average_success_count":192.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.28133,"descend_1.grasp_z_offset":0.01128,"lift_1.lift_height":0.15978,"transport_arc.transport_arc_height":0.05027},"optimized_scores":{"best_composite_score":0.28898,"best_fitness_score":0.66898,"best_task_score":0.4157},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":36.0,"contact_point_centroid":[0.57175,0.23616,-0.00673],"force_p95":1.71402,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.7657,"mean_force":1.07149,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.55529,0.22535,0.19328]},{"body_a":"world","body_b":"grasp_target","contact_count":196.0,"contact_point_centroid":[0.57325,0.23101,-0.00651],"force_p95":0.68619,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.9215,"mean_force":0.21541,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.55658,0.23078,0.18399]},{"body_a":"world","body_b":"grasp_target","contact_count":83.0,"contact_point_centroid":[0.49942,0.04184,-0.00151],"force_p95":0.35335,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.39207,"mean_force":0.07674,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48802,0.04226,0.04916]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4947.0,"contact_point_centroid":[0.52224,0.09148,0.18638],"force_p95":0.14318,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.34021,"mean_force":0.08905,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.51651,0.11009,0.18645]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6304.0,"contact_point_centroid":[0.49282,0.06134,0.10083],"force_p95":0.10972,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29193,"mean_force":0.06734,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49055,0.04241,0.09973]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5829.0,"contact_point_centroid":[0.49249,0.02347,0.10076],"force_p95":0.1111,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28377,"mean_force":0.07001,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49057,0.04241,0.10003]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50127,0.0449,-0.00221],"force_p95":0.1819,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.2382,"mean_force":0.13791,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49019,0.04247,0.0487]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5624.0,"contact_point_centroid":[0.5248,0.13478,0.18751],"force_p95":0.11163,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22794,"mean_force":0.07971,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.51865,0.11652,0.18758]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4124.0,"contact_point_centroid":[0.48934,0.02313,0.04885],"force_p95":0.08058,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14018,"mean_force":0.05189,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.4891,0.04237,0.04752]},{"body_a":"world","body_b":"grasp_target","contact_count":324.0,"contact_point_centroid":[0.50118,0.04505,-0.00161],"force_p95":0.13823,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.1243,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.4989,0.01262,0.3008]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.57346,0.23232,-0.00193],"force_p95":0.1311,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13363,"mean_force":0.11995,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.55353,0.23302,0.17266]},{"body_a":"world","body_b":"grasp_target","contact_count":1860.0,"contact_point_centroid":[0.50118,0.04505,-0.00199],"force_p95":0.12264,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12264,"mean_force":0.1226,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49739,0.03518,0.18037]},{"body_a":"world","body_b":"grasp_target","contact_count":1304.0,"contact_point_centroid":[0.57346,0.23231,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12264,"mean_force":0.12263,"phase_index":7.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.55547,0.23701,0.23456]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5367.0,"contact_point_centroid":[0.4888,0.06158,0.04919],"force_p95":0.07461,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07757,"mean_force":0.04169,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.48911,0.04237,0.04753]},{"body_a":"left_finger","body_b":"right_finger","contact_count":16.0,"contact_point_centroid":[0.55796,0.23431,0.17557],"force_p95":0.01633,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01633,"mean_force":0.01568,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.55777,0.23429,0.17348]},{"body_a":"left_finger","body_b":"right_finger","contact_count":219.0,"contact_point_centroid":[0.55655,0.23426,0.17022],"force_p95":0.01311,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01493,"mean_force":0.01103,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.55591,0.23422,0.16805]}],"total_contact_groups":16},"final_pose_error":0.01995,"key_states":{"actual_goal_position":[0.56442,0.24486,0.14677],"final_object_position":[0.57346,0.23231,0.01602],"final_tcp_position":[0.56072,0.24228,0.27734],"realised_goal_position":[0.56442,0.24486,0.14677],"realised_object_initial_position":[0.50118,0.04505,0.03]},"peak_contact_force":273015.82274,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":82.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02597],"object_pos_start":[0.50118,0.04505,0.03],"object_to_goal_dist_end":0.24191,"object_to_goal_dist_start":0.23992,"object_z_max":0.03,"peak_contact_force":0.12213,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":324.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.49874,0.02754,0.30255],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.27715,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":465.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.02597],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.24191,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1860.0,"raw_peak_contact_force":0.12264,"subtask_id":"descend_1","tcp_end":[0.49728,0.04306,0.05674],"tcp_start":[0.49874,0.02754,0.30255],"tcp_to_object_dist_end":0.03103,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":42.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50119,0.04327,0.02524],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.24374,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"peak_contact_force":0.17647,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11291.0,"raw_peak_contact_force":0.2382,"subtask_id":"grasp_1","tcp_end":[0.48907,0.04237,0.04749],"tcp_start":[0.49728,0.04306,0.05674],"tcp_to_object_dist_end":0.02535,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":26.0,"n_steps":383.0,"n_steps_budget":870.0,"object_pos_end":[0.51032,0.04367,0.13931],"object_pos_start":[0.50119,0.04327,0.02524],"object_to_goal_dist_end":0.20848,"object_to_goal_dist_start":0.24374,"object_z_max":0.13905,"peak_contact_force":0.10364,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":12216.0,"raw_peak_contact_force":0.39207,"tcp_end":[0.49643,0.04285,0.16583],"tcp_start":[0.48907,0.04237,0.04749],"tcp_to_object_dist_end":0.02995,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":566.0,"n_steps_budget":1000.0,"object_pos_end":[0.57387,0.23878,-0.00013],"object_pos_start":[0.51032,0.04367,0.13931],"object_to_goal_dist_end":0.14734,"object_to_goal_dist_start":0.20848,"object_z_max":0.16661,"peak_contact_force":0.96941,"phase_name":"transport_arc","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":10607.0,"raw_peak_contact_force":1.7657,"subtask_id":"transport_arc","tcp_end":[0.55594,0.22739,0.19285],"tcp_start":[0.49643,0.04285,0.16583],"tcp_to_object_dist_end":0.19415,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":49.0,"n_steps_budget":1000.0,"object_pos_end":[0.5737,0.23422,0.01557],"object_pos_start":[0.57387,0.23878,-0.00013],"object_to_goal_dist_end":0.13196,"object_to_goal_dist_start":0.14734,"object_z_max":0.01539,"peak_contact_force":273015.82274,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":212.0,"raw_peak_contact_force":0.9215,"tcp_end":[0.55792,0.23471,0.17229],"tcp_start":[0.55594,0.22739,0.19285],"tcp_to_object_dist_end":0.15752,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.57346,0.23231,0.01602],"object_pos_start":[0.5737,0.23422,0.01557],"object_to_goal_dist_end":0.13167,"object_to_goal_dist_start":0.13196,"object_z_max":0.01683,"peak_contact_force":0.12264,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1019.0,"raw_peak_contact_force":0.13363,"subtask_id":"release_1","tcp_end":[0.5521,0.2323,0.19273],"tcp_start":[0.55792,0.23471,0.17229],"tcp_to_object_dist_end":0.17799,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":326.0,"n_steps_budget":690.0,"object_pos_end":[0.57346,0.23231,0.01602],"object_pos_start":[0.57346,0.23231,0.01602],"object_to_goal_dist_end":0.13167,"object_to_goal_dist_start":0.13167,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1304.0,"raw_peak_contact_force":0.12264,"tcp_end":[0.56072,0.24228,0.27734],"tcp_start":[0.5521,0.2323,0.19273],"tcp_to_object_dist_end":0.26182,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.82323,"average_solve_count":198.0,"average_success_count":198.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.26076,"descend_1.grasp_z_offset":0.01041,"lift_1.lift_height":0.13719,"transport_arc.transport_arc_height":0.09957},"optimized_scores":{"best_composite_score":0.19076,"best_fitness_score":0.57076,"best_task_score":0.21649},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":1941.0,"contact_point_centroid":[0.54132,0.03967,-0.00252],"force_p95":0.21496,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.86196,"mean_force":0.14757,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.56991,0.09339,0.25403]},{"body_a":"world","body_b":"grasp_target","contact_count":79.0,"contact_point_centroid":[0.47417,-0.01802,-0.00142],"force_p95":0.32945,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.3877,"mean_force":0.07523,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46496,-0.01864,0.04925]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6059.0,"contact_point_centroid":[0.46771,-0.03779,0.09523],"force_p95":0.08951,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27259,"mean_force":0.05599,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46701,-0.01876,0.09415]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5440.0,"contact_point_centroid":[0.46796,0.00038,0.09555],"force_p95":0.09691,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27255,"mean_force":0.06089,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46704,-0.01876,0.09466]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3354.0,"contact_point_centroid":[0.49409,-0.01518,0.17368],"force_p95":0.1265,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27158,"mean_force":0.08181,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.48848,0.00325,0.17341]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2856.0,"contact_point_centroid":[0.49317,0.02064,0.17214],"force_p95":0.13894,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21915,"mean_force":0.09092,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.48732,0.00195,0.17174]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.47619,-0.02005,-0.00213],"force_p95":0.158,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.21403,"mean_force":0.13193,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46704,-0.01868,0.04879]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4091.0,"contact_point_centroid":[0.46688,0.00056,0.04868],"force_p95":0.08063,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15052,"mean_force":0.05216,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46598,-0.01865,0.04772]},{"body_a":"world","body_b":"grasp_target","contact_count":136.0,"contact_point_centroid":[0.47616,-0.02015,-0.00104],"force_p95":0.13842,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12175,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.4959,-0.00248,0.29796]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.47616,-0.02015,-0.002],"force_p95":0.12508,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13462,"mean_force":0.12296,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.48156,-0.01276,0.17572]},{"body_a":"world","body_b":"grasp_target","contact_count":444.0,"contact_point_centroid":[0.54128,0.03968,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.62196,0.15096,0.25014]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.54128,0.03968,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.62115,0.15361,0.21678]},{"body_a":"world","body_b":"grasp_target","contact_count":1376.0,"contact_point_centroid":[0.54128,0.03968,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":7.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.62332,0.15537,0.27799]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4989.0,"contact_point_centroid":[0.46609,-0.03776,0.04891],"force_p95":0.07181,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07475,"mean_force":0.04404,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46598,-0.01865,0.04773]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1873.0,"contact_point_centroid":[0.57487,0.0986,0.25978],"force_p95":0.01161,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0156,"mean_force":0.0105,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.57466,0.0986,0.25744]},{"body_a":"left_finger","body_b":"right_finger","contact_count":473.0,"contact_point_centroid":[0.62218,0.15101,0.25214],"force_p95":0.011,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01102,"mean_force":0.01047,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.62199,0.151,0.24981]}],"total_contact_groups":17},"final_pose_error":0.01983,"key_states":{"actual_goal_position":[0.63142,0.15919,0.19002],"final_object_position":[0.54128,0.03968,0.01602],"final_tcp_position":[0.62843,0.15791,0.32046],"realised_goal_position":[0.63142,0.15919,0.19002],"realised_object_initial_position":[0.47616,-0.02015,0.03]},"peak_contact_force":1.86196,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":35.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02624],"object_pos_start":[0.47616,-0.02015,0.03],"object_to_goal_dist_end":0.28826,"object_to_goal_dist_start":0.28614,"object_z_max":0.03,"peak_contact_force":0.13511,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":136.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.49035,-0.00685,0.29459],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.26905,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":450.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.02624],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28826,"object_z_max":0.02624,"peak_contact_force":0.12262,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1800.0,"raw_peak_contact_force":0.13462,"subtask_id":"descend_1","tcp_end":[0.47391,-0.0188,0.05609],"tcp_start":[0.49035,-0.00685,0.29459],"tcp_to_object_dist_end":0.03018,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.47611,-0.0191,0.02554],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28803,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.15439,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10880.0,"raw_peak_contact_force":0.21403,"subtask_id":"grasp_1","tcp_end":[0.46595,-0.01865,0.04769],"tcp_start":[0.47391,-0.0188,0.05609],"tcp_to_object_dist_end":0.02437,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":28.0,"n_steps":303.0,"n_steps_budget":750.0,"object_pos_end":[0.48549,-0.01933,0.11909],"object_pos_start":[0.47611,-0.0191,0.02554],"object_to_goal_dist_end":0.24123,"object_to_goal_dist_start":0.28803,"object_z_max":0.11882,"peak_contact_force":0.10242,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":11578.0,"raw_peak_contact_force":0.3877,"tcp_end":[0.47124,-0.01893,0.14351],"tcp_start":[0.46595,-0.01865,0.04769],"tcp_to_object_dist_end":0.02828,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":848.0,"n_steps_budget":1000.0,"object_pos_end":[0.54128,0.03968,0.01602],"object_pos_start":[0.48549,-0.01933,0.11909],"object_to_goal_dist_end":0.22953,"object_to_goal_dist_start":0.24123,"object_z_max":0.17202,"peak_contact_force":0.12263,"phase_name":"transport_arc","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":10024.0,"raw_peak_contact_force":1.86196,"subtask_id":"transport_arc","tcp_end":[0.61945,0.1475,0.27886],"tcp_start":[0.47124,-0.01893,0.14351],"tcp_to_object_dist_end":0.29465,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":111.0,"n_steps_budget":1000.0,"object_pos_end":[0.54128,0.03968,0.01602],"object_pos_start":[0.54128,0.03968,0.01602],"object_to_goal_dist_end":0.22953,"object_to_goal_dist_start":0.22953,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":917.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.62516,0.15468,0.21798],"tcp_start":[0.61945,0.1475,0.27886],"tcp_to_object_dist_end":0.24708,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54128,0.03968,0.01602],"object_pos_start":[0.54128,0.03968,0.01602],"object_to_goal_dist_end":0.22953,"object_to_goal_dist_start":0.22953,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1027.0,"raw_peak_contact_force":0.12263,"subtask_id":"release_1","tcp_end":[0.61986,0.15318,0.23628],"tcp_start":[0.62516,0.15468,0.21798],"tcp_to_object_dist_end":0.25995,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":344.0,"n_steps_budget":660.0,"object_pos_end":[0.54128,0.03968,0.01602],"object_pos_start":[0.54128,0.03968,0.01602],"object_to_goal_dist_end":0.22953,"object_to_goal_dist_start":0.22953,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1376.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.62843,0.15791,0.32046],"tcp_start":[0.61986,0.15318,0.23628],"tcp_to_object_dist_end":0.33802,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.83962,"average_solve_count":212.0,"average_success_count":212.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.29174,"descend_1.grasp_z_offset":0.01002,"lift_1.lift_height":0.17862,"transport_arc.transport_arc_height":0.09641},"optimized_scores":{"best_composite_score":0.34084,"best_fitness_score":0.72084,"best_task_score":0.51643},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":334.0,"contact_point_centroid":[0.64404,0.20856,-0.00552],"force_p95":1.29536,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.76412,"mean_force":0.27884,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.62017,0.19906,0.16588]},{"body_a":"world","body_b":"grasp_target","contact_count":74.0,"contact_point_centroid":[0.45666,-0.02493,-0.00143],"force_p95":0.34311,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.38292,"mean_force":0.08291,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44759,-0.02504,0.04922]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8266.0,"contact_point_centroid":[0.52632,0.04708,0.21003],"force_p95":0.1276,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29103,"mean_force":0.08398,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.52043,0.06564,0.21059]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6727.0,"contact_point_centroid":[0.45122,-0.00603,0.11087],"force_p95":0.10707,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27632,"mean_force":0.06662,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44951,-0.02507,0.11005]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":7546.0,"contact_point_centroid":[0.45088,-0.04403,0.11054],"force_p95":0.10141,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27524,"mean_force":0.0608,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44949,-0.02507,0.10957]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8748.0,"contact_point_centroid":[0.53083,0.08988,0.21075],"force_p95":0.12147,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22085,"mean_force":0.07932,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.52475,0.07138,0.21116]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.45859,-0.02622,-0.00211],"force_p95":0.15243,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.20863,"mean_force":0.13048,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44964,-0.02511,0.0488]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4096.0,"contact_point_centroid":[0.44952,-0.00586,0.04881],"force_p95":0.07981,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14761,"mean_force":0.05214,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44862,-0.02507,0.04781]},{"body_a":"world","body_b":"grasp_target","contact_count":352.0,"contact_point_centroid":[0.45856,-0.02632,-0.00165],"force_p95":0.13823,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12413,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48596,-0.00785,0.30417]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.64432,0.20828,-0.00197],"force_p95":0.12832,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.1305,"mean_force":0.12297,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.6177,0.20084,0.14022]},{"body_a":"world","body_b":"grasp_target","contact_count":1948.0,"contact_point_centroid":[0.45856,-0.02632,-0.00199],"force_p95":0.12264,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12264,"mean_force":0.12261,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.46348,-0.02102,0.18355]},{"body_a":"world","body_b":"grasp_target","contact_count":1448.0,"contact_point_centroid":[0.64432,0.20827,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":7.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.61989,0.20293,0.20182]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4966.0,"contact_point_centroid":[0.4487,-0.04417,0.04898],"force_p95":0.07122,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07351,"mean_force":0.04413,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44862,-0.02507,0.04782]},{"body_a":"left_finger","body_b":"right_finger","contact_count":131.0,"contact_point_centroid":[0.62206,0.20119,0.15294],"force_p95":0.01571,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01617,"mean_force":0.01238,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.62178,0.20118,0.15066]},{"body_a":"left_finger","body_b":"right_finger","contact_count":220.0,"contact_point_centroid":[0.62081,0.20196,0.13867],"force_p95":0.01121,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01124,"mean_force":0.01018,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.62049,0.20194,0.13644]}],"total_contact_groups":15},"final_pose_error":0.01994,"key_states":{"actual_goal_position":[0.63013,0.20822,0.11412],"final_object_position":[0.64432,0.20827,0.01602],"final_tcp_position":[0.62596,0.2063,0.24472],"realised_goal_position":[0.63013,0.20822,0.11412],"realised_object_initial_position":[0.45856,-0.02632,0.03]},"peak_contact_force":1.76412,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":89.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02599],"object_pos_start":[0.45856,-0.02632,0.03],"object_to_goal_dist_end":0.30366,"object_to_goal_dist_start":0.30252,"object_z_max":0.03,"peak_contact_force":0.12209,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":352.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.4716,-0.01687,0.30994],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.28441,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":487.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.02599],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30366,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1948.0,"raw_peak_contact_force":0.12264,"subtask_id":"descend_1","tcp_end":[0.45628,-0.02533,0.05558],"tcp_start":[0.4716,-0.01687,0.30994],"tcp_to_object_dist_end":0.02967,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.45851,-0.02542,0.02562],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30311,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.14936,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10862.0,"raw_peak_contact_force":0.20863,"subtask_id":"grasp_1","tcp_end":[0.44859,-0.02507,0.04779],"tcp_start":[0.45628,-0.02533,0.05558],"tcp_to_object_dist_end":0.02429,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":419.0,"n_steps_budget":990.0,"object_pos_end":[0.46891,-0.02563,0.15919],"object_pos_start":[0.45851,-0.02542,0.02562],"object_to_goal_dist_end":0.28759,"object_to_goal_dist_start":0.30311,"object_z_max":0.15892,"peak_contact_force":0.10575,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":14347.0,"raw_peak_contact_force":0.38292,"tcp_end":[0.45438,-0.02523,0.18488],"tcp_start":[0.44859,-0.02507,0.04779],"tcp_to_object_dist_end":0.02952,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":788.0,"n_steps_budget":1000.0,"object_pos_end":[0.63162,0.20283,0.10534],"object_pos_start":[0.46891,-0.02563,0.15919],"object_to_goal_dist_end":0.0104,"object_to_goal_dist_start":0.28759,"object_z_max":0.19013,"peak_contact_force":0.0,"phase_name":"transport_arc","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":17014.0,"raw_peak_contact_force":0.29103,"subtask_id":"transport_arc","tcp_end":[0.61706,0.19366,0.20659],"tcp_start":[0.45438,-0.02523,0.18488],"tcp_to_object_dist_end":0.1027,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":118.0,"n_steps_budget":1000.0,"object_pos_end":[0.64429,0.20814,0.0167],"object_pos_start":[0.63162,0.20283,0.10534],"object_to_goal_dist_end":0.09844,"object_to_goal_dist_start":0.0104,"object_z_max":0.10534,"peak_contact_force":0.12899,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":465.0,"raw_peak_contact_force":1.76412,"tcp_end":[0.62287,0.20255,0.14176],"tcp_start":[0.61706,0.19366,0.20659],"tcp_to_object_dist_end":0.127,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.64432,0.20827,0.01602],"object_pos_start":[0.64429,0.20814,0.0167],"object_to_goal_dist_end":0.09912,"object_to_goal_dist_start":0.09844,"object_z_max":0.0167,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1020.0,"raw_peak_contact_force":0.1305,"subtask_id":"release_1","tcp_end":[0.61599,0.20018,0.15967],"tcp_start":[0.62287,0.20255,0.14176],"tcp_to_object_dist_end":0.14664,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":362.0,"n_steps_budget":690.0,"object_pos_end":[0.64432,0.20827,0.01602],"object_pos_start":[0.64432,0.20827,0.01602],"object_to_goal_dist_end":0.09912,"object_to_goal_dist_start":0.09912,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1448.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.62596,0.2063,0.24472],"tcp_start":[0.61599,0.20018,0.15967],"tcp_to_object_dist_end":0.22944,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```