## Search State

- **Seed**: 1
- **Iteration**: 8 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 7 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | position_control | admittance_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 7 | 0.1617 | 0.34 | ❌ rejected |
| 6 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | admittance_control | position_control | position_control | impedance_control | admittance_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 7 | 0.2287 | 0.35 | ❌ rejected |
| 5 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | admittance_control | position_control | position_control | position_control | admittance_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 4 | 0.2014 | 0.24 | ❌ rejected |
| 4 | approach → descend → grasp → lift → approach → grasp | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | — | position_control | admittance_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | time_limit | 6 | 0.0520 | 0.20 | ❌ rejected |
| 3 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | admittance_control | position_control | position_control | position_control | admittance_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 4 | 0.2735 | 0.38 | ✅ accepted |

**Proposal policy**: task_score is 0.34 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.162) — your mutation base

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

- **Composite score**: 0.162
- **task_score** (E): 0.342
- **fitness_score**: 0.632  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.470

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.0577 |
| descend_1 | 1.00 | 1.00 | 0.2059 |
| grasp_1 | 1.00 | 1.00 | 0.0116 |
| lift_1 | 1.00 | 1.00 | 0.1113 |
| transport_arc | 1.00 | 0.67 | 0.2443 |
| descend_2 | 1.00 | 1.00 | 0.0703 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.484, -0.001, 0.263) | (0.479, -0.000, 0.030)→(0.479, -0.000, 0.026) | 0.276→0.278 | 1.00 / 4.000 | 0.122 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.484, -0.001, 0.263)→(0.476, -0.000, 0.057) | (0.479, -0.000, 0.026)→(0.479, -0.000, 0.026) | 0.278→0.278 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_1 | grasp | 1.00 / step_budget | (0.476, -0.000, 0.057)→(0.468, -0.001, 0.049) | (0.479, -0.000, 0.026)→(0.479, -0.000, 0.025) | 0.278→0.278 | 1.00 / 41.000 | 0.160 | 0.213 |
| lift_1 | lift | 1.00 / step_budget | (0.468, -0.001, 0.049)→(0.474, -0.000, 0.160) | (0.479, -0.000, 0.025)→(0.488, -0.001, 0.133) | 0.278→0.244 | 1.00 / 22.667 | 74.758 | 0.374 |
| transport_arc | approach | 1.00 / step_budget | (0.474, -0.000, 0.160)→(0.595, 0.186, 0.249) | (0.488, -0.001, 0.133)→(0.582, 0.129, 0.040) | 0.244→0.141 | 0.67 / 5.667 | 3249.645 | 1.296 |
| descend_2 | descend | 1.00 / step_budget | (0.595, 0.186, 0.249)→(0.600, 0.194, 0.179) | (0.582, 0.129, 0.040)→(0.584, 0.130, 0.019) | 0.141→0.161 | 1.00 / 6.333 | 91002.605 | 0.723 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: 1.000
- terminal_score: 0.363
- phase_score: 0.356
- phase_breakdown.descend_1_score: 0.834
- phase_breakdown.transport_arc_score: 0.022
- phase_breakdown.grasp_1_score: 1.000
- phase_breakdown.release_1_score: 0.730
- phase_breakdown.approach_1_score: 0.006
- grasp_place_fitness: 0.640

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.640
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.363
- **Median Q (composite search score)**: 0.160
- **K-run variance**: 0.0000
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.366


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.72109,"average_solve_count":147.0,"average_success_count":147.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.28982,"descend_1.grasp_z_offset":0.01132,"descend_2.descend_speed":0.04992,"descend_2.descend_z_offset":0.04999,"lift_1.lift_height":0.16853,"transport_arc.arc_speed":0.24318,"transport_arc.transport_arc_height":0.07124},"optimized_scores":{"best_composite_score":0.16025,"best_fitness_score":0.63025,"best_task_score":0.33813},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":874.0,"contact_point_centroid":[0.54676,0.14961,-0.00316],"force_p95":0.57048,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.69875,"mean_force":0.17837,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.54148,0.18345,0.21454]},{"body_a":"world","body_b":"grasp_target","contact_count":82.0,"contact_point_centroid":[0.49913,0.04209,-0.00151],"force_p95":0.36473,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.39243,"mean_force":0.07787,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48803,0.04244,0.04913]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1844.0,"contact_point_centroid":[0.51034,0.05166,0.18712],"force_p95":0.16602,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29894,"mean_force":0.09427,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.50391,0.07028,0.18674]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6662.0,"contact_point_centroid":[0.49302,0.06149,0.10472],"force_p95":0.10976,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29164,"mean_force":0.06795,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49058,0.04256,0.10362]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6283.0,"contact_point_centroid":[0.49258,0.02363,0.10441],"force_p95":0.1108,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28556,"mean_force":0.06971,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49058,0.04256,0.10376]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50126,0.04491,-0.0022],"force_p95":0.1785,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.23498,"mean_force":0.13707,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.4902,0.04265,0.04871]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2214.0,"contact_point_centroid":[0.51182,0.09339,0.18906],"force_p95":0.11979,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19093,"mean_force":0.08071,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.50541,0.07515,0.18881]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4132.0,"contact_point_centroid":[0.48934,0.02331,0.04888],"force_p95":0.08,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14002,"mean_force":0.05183,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.48911,0.04255,0.04753]},{"body_a":"world","body_b":"grasp_target","contact_count":368.0,"contact_point_centroid":[0.50118,0.04505,-0.00166],"force_p95":0.13823,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12404,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.4988,0.01368,0.30342]},{"body_a":"world","body_b":"grasp_target","contact_count":84.0,"contact_point_centroid":[0.54684,0.14974,-0.00199],"force_p95":0.12265,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12265,"mean_force":0.12263,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.55614,0.22873,0.21108]},{"body_a":"world","body_b":"grasp_target","contact_count":1900.0,"contact_point_centroid":[0.50118,0.04505,-0.00199],"force_p95":0.12264,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12264,"mean_force":0.12261,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49741,0.03611,0.18319]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5366.0,"contact_point_centroid":[0.48879,0.06175,0.04923],"force_p95":0.07399,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07676,"mean_force":0.04162,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.48911,0.04255,0.04754]},{"body_a":"left_finger","body_b":"right_finger","contact_count":697.0,"contact_point_centroid":[0.54544,0.19429,0.21745],"force_p95":0.01269,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01638,"mean_force":0.01082,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.54516,0.19427,0.21511]},{"body_a":"left_finger","body_b":"right_finger","contact_count":90.0,"contact_point_centroid":[0.55634,0.22876,0.21355],"force_p95":0.01089,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01091,"mean_force":0.01039,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.55613,0.22873,0.21108]}],"total_contact_groups":14},"final_pose_error":0.01985,"key_states":{"actual_goal_position":[0.56442,0.24486,0.14677],"final_object_position":[0.54684,0.14974,0.01602],"final_tcp_position":[0.55686,0.2305,0.20819],"realised_goal_position":[0.56442,0.24486,0.14677],"realised_object_initial_position":[0.50118,0.04505,0.03]},"peak_contact_force":273005.90358,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":93.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.026],"object_pos_start":[0.50118,0.04505,0.03],"object_to_goal_dist_end":0.24189,"object_to_goal_dist_start":0.23992,"object_z_max":0.03,"peak_contact_force":0.12213,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":368.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.49874,0.02919,0.30825],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.2827,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":475.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.026],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.24189,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1900.0,"raw_peak_contact_force":0.12264,"subtask_id":"descend_1","tcp_end":[0.49728,0.04325,0.05674],"tcp_start":[0.49874,0.02919,0.30825],"tcp_to_object_dist_end":0.03102,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":42.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50118,0.04338,0.02529],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.24362,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"peak_contact_force":0.17342,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11298.0,"raw_peak_contact_force":0.23498,"subtask_id":"grasp_1","tcp_end":[0.48908,0.04255,0.0475],"tcp_start":[0.49728,0.04325,0.05674],"tcp_to_object_dist_end":0.02531,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":24.0,"n_steps":411.0,"n_steps_budget":930.0,"object_pos_end":[0.51044,0.04383,0.14783],"object_pos_start":[0.50118,0.04338,0.02529],"object_to_goal_dist_end":0.20815,"object_to_goal_dist_start":0.24362,"object_z_max":0.14757,"peak_contact_force":224.03132,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":13027.0,"raw_peak_contact_force":0.39243,"tcp_end":[0.49657,0.04298,0.17463],"tcp_start":[0.48908,0.04255,0.0475],"tcp_to_object_dist_end":0.03018,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":490.0,"n_steps_budget":1000.0,"object_pos_end":[0.54684,0.14974,0.01602],"object_pos_start":[0.51044,0.04383,0.14783],"object_to_goal_dist_end":0.16265,"object_to_goal_dist_start":0.20815,"object_z_max":0.16979,"peak_contact_force":9748.81117,"phase_name":"transport_arc","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":5629.0,"raw_peak_contact_force":1.69875,"subtask_id":"transport_arc","tcp_end":[0.55628,0.22741,0.21293],"tcp_start":[0.49657,0.04298,0.17463],"tcp_to_object_dist_end":0.21188,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":21.0,"n_steps_budget":1000.0,"object_pos_end":[0.54684,0.14974,0.01602],"object_pos_start":[0.54684,0.14974,0.01602],"object_to_goal_dist_end":0.16265,"object_to_goal_dist_start":0.16265,"object_z_max":0.01602,"peak_contact_force":273005.90358,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":174.0,"raw_peak_contact_force":0.12265,"subtask_id":"release_1","tcp_end":[0.55686,0.2305,0.20819],"tcp_start":[0.55628,0.22741,0.21293],"tcp_to_object_dist_end":0.20869,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.80303,"average_solve_count":132.0,"average_success_count":132.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.14557,"descend_1.grasp_z_offset":0.01079,"descend_2.descend_speed":0.02191,"descend_2.descend_z_offset":0.04399,"lift_1.lift_height":0.14532,"transport_arc.arc_speed":0.20924,"transport_arc.transport_arc_height":0.05001},"optimized_scores":{"best_composite_score":0.15467,"best_fitness_score":0.62467,"best_task_score":0.32611},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":6.0,"contact_point_centroid":[0.62807,0.12843,-0.00312],"force_p95":1.92002,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.92365,"mean_force":1.68545,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.61882,0.14831,0.22966]},{"body_a":"world","body_b":"grasp_target","contact_count":74.0,"contact_point_centroid":[0.47425,-0.01882,-0.0014],"force_p95":0.33197,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.37502,"mean_force":0.07698,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46414,-0.01922,0.04955]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5433.0,"contact_point_centroid":[0.4678,-0.00017,0.0966],"force_p95":0.10471,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27499,"mean_force":0.06471,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46637,-0.01924,0.09582]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6074.0,"contact_point_centroid":[0.46755,-0.03823,0.09664],"force_p95":0.09807,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27155,"mean_force":0.05912,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46637,-0.01924,0.09578]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5967.0,"contact_point_centroid":[0.53251,0.06363,0.19624],"force_p95":0.13411,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26247,"mean_force":0.09194,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.52685,0.04511,0.1978]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6333.0,"contact_point_centroid":[0.53337,0.02758,0.1967],"force_p95":0.13508,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23301,"mean_force":0.08744,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.52765,0.046,0.19816]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.47618,-0.02007,-0.00208],"force_p95":0.14503,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.19242,"mean_force":0.12849,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46618,-0.01928,0.04925]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4103.0,"contact_point_centroid":[0.46602,-4e-05,0.04915],"force_p95":0.07878,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1406,"mean_force":0.05214,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46513,-0.01925,0.04819]},{"body_a":"world","body_b":"grasp_target","contact_count":808.0,"contact_point_centroid":[0.47616,-0.02015,-0.00184],"force_p95":0.13728,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12323,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48922,-0.00764,0.24895]},{"body_a":"world","body_b":"grasp_target","contact_count":1064.0,"contact_point_centroid":[0.47616,-0.02015,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.47486,-0.01771,0.1262]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4929.0,"contact_point_centroid":[0.46519,-0.03833,0.04923],"force_p95":0.07002,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07203,"mean_force":0.0443,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46513,-0.01925,0.0482]}],"total_contact_groups":11},"final_pose_error":0.01674,"key_states":{"actual_goal_position":[0.63142,0.15919,0.19002],"final_object_position":[0.62906,0.13423,0.02382],"final_tcp_position":[0.61924,0.14867,0.22942],"realised_goal_position":[0.63142,0.15919,0.19002],"realised_object_initial_position":[0.47616,-0.02015,0.03]},"peak_contact_force":1.92365,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":203.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.03],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28614,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":808.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.47832,-0.01611,0.19493],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.16897,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":266.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.12262,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1064.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.47299,-0.01942,0.05652],"tcp_start":[0.47832,-0.01611,0.19493],"tcp_to_object_dist_end":0.03067,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.4761,-0.01947,0.02571],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28817,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.14284,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10832.0,"raw_peak_contact_force":0.19242,"subtask_id":"grasp_1","tcp_end":[0.4651,-0.01925,0.04816],"tcp_start":[0.47299,-0.01942,0.05652],"tcp_to_object_dist_end":0.025,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":324.0,"n_steps_budget":780.0,"object_pos_end":[0.48581,-0.01963,0.12663],"object_pos_start":[0.4761,-0.01947,0.02571],"object_to_goal_dist_end":0.23916,"object_to_goal_dist_start":0.28817,"object_z_max":0.12636,"peak_contact_force":0.1054,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":11581.0,"raw_peak_contact_force":0.37502,"tcp_end":[0.4713,-0.01933,0.15177],"tcp_start":[0.4651,-0.01925,0.04816],"tcp_to_object_dist_end":0.02903,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":636.0,"n_steps_budget":1000.0,"object_pos_end":[0.62414,0.13207,0.08671],"object_pos_start":[0.48581,-0.01963,0.12663],"object_to_goal_dist_end":0.10705,"object_to_goal_dist_start":0.23916,"object_z_max":0.1919,"peak_contact_force":0.0,"phase_name":"transport_arc","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":12300.0,"raw_peak_contact_force":0.26247,"subtask_id":"transport_arc","tcp_end":[0.61824,0.14675,0.23173],"tcp_start":[0.4713,-0.01933,0.15177],"tcp_to_object_dist_end":0.14588,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":20.0,"n_steps_budget":1000.0,"object_pos_end":[0.62906,0.13423,0.02382],"object_pos_start":[0.62414,0.13207,0.08671],"object_to_goal_dist_end":0.16808,"object_to_goal_dist_start":0.10705,"object_z_max":0.08671,"peak_contact_force":1.78903,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":6.0,"raw_peak_contact_force":1.92365,"subtask_id":"release_1","tcp_end":[0.61924,0.14867,0.22942],"tcp_start":[0.61824,0.14675,0.23173],"tcp_to_object_dist_end":0.20634,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.67568,"average_solve_count":259.0,"average_success_count":259.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.25027,"descend_1.grasp_z_offset":0.01308,"descend_2.descend_speed":0.07862,"descend_2.descend_z_offset":-0.03147,"lift_1.lift_height":0.14734,"transport_arc.arc_speed":0.06277,"transport_arc.transport_arc_height":0.19995},"optimized_scores":{"best_composite_score":0.17006,"best_fitness_score":0.64006,"best_task_score":0.36311},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":1152.0,"contact_point_centroid":[0.57571,0.10566,-0.00314],"force_p95":0.54593,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.92684,"mean_force":0.16761,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.58352,0.14869,0.29079]},{"body_a":"world","body_b":"grasp_target","contact_count":77.0,"contact_point_centroid":[0.4565,-0.0238,-0.00148],"force_p95":0.3061,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.35421,"mean_force":0.0693,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44804,-0.02478,0.05255]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3800.0,"contact_point_centroid":[0.45157,-0.00579,0.09579],"force_p95":0.13719,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31152,"mean_force":0.08639,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44978,-0.02479,0.09772]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6025.0,"contact_point_centroid":[0.45074,-0.04317,0.10043],"force_p95":0.10048,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26486,"mean_force":0.05879,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44992,-0.02479,0.10024]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4719.0,"contact_point_centroid":[0.4988,0.04845,0.20992],"force_p95":0.14105,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23118,"mean_force":0.11304,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.49314,0.03037,0.21272]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5405.0,"contact_point_centroid":[0.49588,0.0091,0.20687],"force_p95":0.14316,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21829,"mean_force":0.10495,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.49065,0.02706,0.2093]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.45858,-0.02624,-0.00214],"force_p95":0.1633,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.21167,"mean_force":0.13262,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.45008,-0.02486,0.05199]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3926.0,"contact_point_centroid":[0.45069,-0.00566,0.05055],"force_p95":0.10389,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14809,"mean_force":0.05433,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44906,-0.02482,0.051]},{"body_a":"world","body_b":"grasp_target","contact_count":292.0,"contact_point_centroid":[0.45856,-0.02632,-0.00157],"force_p95":0.13832,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12453,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.4879,-0.00682,0.29297]},{"body_a":"world","body_b":"grasp_target","contact_count":1728.0,"contact_point_centroid":[0.45856,-0.02632,-0.00199],"force_p95":0.12264,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12264,"mean_force":0.12259,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.46492,-0.02012,0.17232]},{"body_a":"world","body_b":"grasp_target","contact_count":1412.0,"contact_point_centroid":[0.57581,0.10566,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.61623,0.19318,0.20232]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4983.0,"contact_point_centroid":[0.44909,-0.04359,0.05123],"force_p95":0.07116,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07416,"mean_force":0.04289,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44906,-0.02482,0.051]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1054.0,"contact_point_centroid":[0.58751,0.15363,0.29498],"force_p95":0.01272,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01517,"mean_force":0.01074,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.5873,0.15362,0.29265]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1494.0,"contact_point_centroid":[0.61654,0.19321,0.20442],"force_p95":0.01101,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01281,"mean_force":0.01052,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.61624,0.19319,0.20211]}],"total_contact_groups":14},"final_pose_error":0.01952,"key_states":{"actual_goal_position":[0.63013,0.20822,0.11412],"final_object_position":[0.57581,0.10566,0.01602],"final_tcp_position":[0.62367,0.20374,0.10051],"realised_goal_position":[0.63013,0.20822,0.11412],"realised_object_initial_position":[0.45856,-0.02632,0.03]},"peak_contact_force":1.92684,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":74.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02593],"object_pos_start":[0.45856,-0.02632,0.03],"object_to_goal_dist_end":0.30367,"object_to_goal_dist_start":0.30252,"object_z_max":0.03,"peak_contact_force":0.12248,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":292.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.47424,-0.01532,0.28504],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.25982,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":432.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.02593],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30367,"object_z_max":0.02602,"peak_contact_force":0.12262,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1728.0,"raw_peak_contact_force":0.12264,"subtask_id":"descend_1","tcp_end":[0.4567,-0.02507,0.0588],"tcp_start":[0.47424,-0.01532,0.28504],"tcp_to_object_dist_end":0.03286,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.45851,-0.02508,0.02546],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30289,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.16328,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10709.0,"raw_peak_contact_force":0.21167,"subtask_id":"grasp_1","tcp_end":[0.44903,-0.02482,0.05097],"tcp_start":[0.4567,-0.02507,0.0588],"tcp_to_object_dist_end":0.02722,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":21.0,"n_steps":315.0,"n_steps_budget":780.0,"object_pos_end":[0.46635,-0.02599,0.12498],"object_pos_start":[0.45851,-0.02508,0.02546],"object_to_goal_dist_end":0.28599,"object_to_goal_dist_start":0.30289,"object_z_max":0.12471,"peak_contact_force":0.13609,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":9902.0,"raw_peak_contact_force":0.35421,"tcp_end":[0.45397,-0.02488,0.15356],"tcp_start":[0.44903,-0.02482,0.05097],"tcp_to_object_dist_end":0.03117,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.57581,0.10566,0.01602],"object_pos_start":[0.46635,-0.02599,0.12498],"object_to_goal_dist_end":0.15196,"object_to_goal_dist_start":0.28599,"object_z_max":0.22647,"peak_contact_force":0.12263,"phase_name":"transport_arc","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":12330.0,"raw_peak_contact_force":1.92684,"subtask_id":"transport_arc","tcp_end":[0.61039,0.18378,0.30122],"tcp_start":[0.45397,-0.02488,0.15356],"tcp_to_object_dist_end":0.29772,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":353.0,"n_steps_budget":1000.0,"object_pos_end":[0.57581,0.10566,0.01602],"object_pos_start":[0.57581,0.10566,0.01602],"object_to_goal_dist_end":0.15196,"object_to_goal_dist_start":0.15196,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2906.0,"raw_peak_contact_force":0.12263,"subtask_id":"release_1","tcp_end":[0.62367,0.20374,0.10051],"tcp_start":[0.61039,0.18378,0.30122],"tcp_to_object_dist_end":0.13802,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```