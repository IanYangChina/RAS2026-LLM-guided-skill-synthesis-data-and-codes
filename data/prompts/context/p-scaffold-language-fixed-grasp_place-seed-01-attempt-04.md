## Search State

- **Seed**: 1
- **Iteration**: 5 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 4 | approach → descend → grasp → lift → approach → grasp | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | — | position_control | admittance_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | time_limit | 6 | 0.0520 | 0.20 | ❌ rejected |
| 3 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | admittance_control | position_control | position_control | position_control | admittance_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 4 | 0.2735 | 0.38 | ✅ accepted |
| 2 | approach → descend → grasp → lift → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | position_control | admittance_control | position_control | position_control | admittance_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | 4 | 0.3448 | 0.34 | ✅ accepted |
| 1 | approach → descend → grasp → lift → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | position_control | admittance_control | position_control | position_control | admittance_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | 4 | 0.3429 | 0.34 | ❌ rejected |
| 0 | approach → descend → grasp → lift → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | position_control | admittance_control | position_control | position_control | admittance_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | 4 | 0.3438 | 0.34 | ✅ accepted |

**Proposal policy**: task_score is 0.20 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.052) — your mutation base

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

- **Composite score**: 0.052
- **task_score** (E): 0.200
- **fitness_score**: 0.472  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.420

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1157 |
| descend_1 | 1.00 | 1.00 | 0.1318 |
| grasp_1 | 1.00 | 1.00 | 0.0116 |
| lift_1 | 1.00 | 1.00 | 0.1687 |
| transport_arc | 1.00 | 1.00 | 0.2508 |
| final_grasp | 1.00 | 1.00 | 0.0162 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.482, 0.000, 0.193) | (0.479, -0.000, 0.030)→(0.479, -0.000, 0.026) | 0.276→0.278 | 1.00 / 4.000 | 0.122 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.482, 0.000, 0.193)→(0.475, -0.000, 0.061) | (0.479, -0.000, 0.026)→(0.479, -0.000, 0.026) | 0.278→0.278 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_1 | grasp | 1.00 / step_budget | (0.475, -0.000, 0.061)→(0.468, -0.000, 0.053) | (0.479, -0.000, 0.026)→(0.479, -0.000, 0.025) | 0.278→0.278 | 1.00 / 32.667 | 0.164 | 0.213 |
| lift_1 | lift | 1.00 / step_budget | (0.468, -0.000, 0.053)→(0.475, -0.000, 0.221) | (0.479, -0.000, 0.025)→(0.489, 0.010, 0.101) | 0.278→0.247 | 1.00 / 16.667 | 3249.713 | 0.848 |
| transport_arc | approach | 1.00 / step_budget | (0.475, -0.000, 0.221)→(0.600, 0.196, 0.197) | (0.489, 0.010, 0.101)→(0.514, 0.030, 0.016) | 0.247→0.243 | 1.00 / 8.333 | 0.123 | 1.267 |
| final_grasp | grasp | 1.00 / step_budget | (0.600, 0.196, 0.197)→(0.593, 0.194, 0.182) | (0.514, 0.030, 0.016)→(0.514, 0.030, 0.016) | 0.243→0.243 | 1.00 / 8.000 | 0.123 | 0.123 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: 1.000
- terminal_score: 0.207
- phase_score: 0.441
- phase_breakdown.descend_1_score: 0.858
- phase_breakdown.transport_arc_score: 0.372
- phase_breakdown.grasp_1_score: 1.000
- phase_breakdown.release_1_score: 0.000
- phase_breakdown.approach_1_score: 0.008
- grasp_place_fitness: 0.563

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.563
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.232
- **Median Q (composite search score)**: 0.116
- **K-run variance**: 0.0122
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.465


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.94675,"average_solve_count":169.0,"average_success_count":169.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.15709,"descend_1.grasp_z_offset":0.02021,"final_grasp.hold_duration":0.84276,"lift_1.lift_height":0.30947,"transport_arc.arc_height":0.19022,"transport_arc.place_height":0.02028},"optimized_scores":{"best_composite_score":-0.10355,"best_fitness_score":0.31645,"best_task_score":0.23232},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":1050.0,"contact_point_centroid":[0.5174,0.07272,-0.00295],"force_p95":0.50874,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.85759,"mean_force":0.16409,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49568,0.04313,0.26061]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4476.0,"contact_point_centroid":[0.49188,0.06076,0.12251],"force_p95":0.1562,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29877,"mean_force":0.10834,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48892,0.04253,0.12672]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4444.0,"contact_point_centroid":[0.49105,0.02429,0.12171],"force_p95":0.15169,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28334,"mean_force":0.10701,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48889,0.04252,0.12619]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50126,0.04499,-0.00217],"force_p95":0.17375,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.2284,"mean_force":0.13506,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49018,0.04266,0.05756]},{"body_a":"world","body_b":"grasp_target","contact_count":784.0,"contact_point_centroid":[0.50118,0.04505,-0.00184],"force_p95":0.13755,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12325,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49874,0.01696,0.25335]},{"body_a":"world","body_b":"grasp_target","contact_count":2632.0,"contact_point_centroid":[0.51888,0.07525,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12264,"mean_force":0.12263,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.53422,0.15719,0.29654]},{"body_a":"world","body_b":"grasp_target","contact_count":1056.0,"contact_point_centroid":[0.50118,0.04505,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49692,0.03937,0.13547]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.51888,0.07525,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":5.0,"phase_name":"final_grasp","phase_type":"grasp","tcp_position_centroid":[0.55646,0.24195,0.17449]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2649.0,"contact_point_centroid":[0.48837,0.02387,0.05245],"force_p95":0.09776,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11624,"mean_force":0.07621,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.4891,0.04256,0.05638]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2847.0,"contact_point_centroid":[0.48893,0.06136,0.05271],"force_p95":0.10065,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10089,"mean_force":0.07294,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.48911,0.04256,0.05639]},{"body_a":"left_finger","body_b":"right_finger","contact_count":806.0,"contact_point_centroid":[0.49679,0.04324,0.28787],"force_p95":0.01329,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01554,"mean_force":0.01087,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49676,0.04322,0.28572]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2794.0,"contact_point_centroid":[0.53443,0.15696,0.29888],"force_p95":0.01098,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01283,"mean_force":0.01049,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.53414,0.15694,0.29662]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1917.0,"contact_point_centroid":[0.55679,0.24199,0.17683],"force_p95":0.011,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01104,"mean_force":0.01047,"phase_index":5.0,"phase_name":"final_grasp","phase_type":"grasp","tcp_position_centroid":[0.55646,0.24195,0.17449]}],"total_contact_groups":13},"final_pose_error":0.01956,"key_states":{"actual_goal_position":[0.56442,0.24486,0.14677],"final_object_position":[0.51888,0.07525,0.01602],"final_tcp_position":[0.5619,0.24446,0.18645],"realised_goal_position":[0.56442,0.24486,0.14677],"realised_object_initial_position":[0.50118,0.04505,0.03]},"peak_contact_force":9748.8627,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":197.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.03],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.23992,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":784.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.49837,0.03573,0.20446],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.17871,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":264.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"peak_contact_force":0.12262,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1056.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.49714,0.04325,0.06558],"tcp_start":[0.49837,0.03573,0.20446],"tcp_to_object_dist_end":0.03981,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":26.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50117,0.04364,0.02539],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.24336,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"peak_contact_force":0.16989,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":7296.0,"raw_peak_contact_force":0.2284,"subtask_id":"grasp_1","tcp_end":[0.48908,0.04256,0.05635],"tcp_start":[0.49714,0.04325,0.06558],"tcp_to_object_dist_end":0.03326,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":828.0,"n_steps_budget":1000.0,"object_pos_end":[0.51888,0.07525,0.01602],"object_pos_start":[0.50117,0.04364,0.02539],"object_to_goal_dist_end":0.21895,"object_to_goal_dist_start":0.24336,"object_z_max":0.17118,"peak_contact_force":9748.8627,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":10776.0,"raw_peak_contact_force":1.85759,"tcp_end":[0.49838,0.04337,0.31525],"tcp_start":[0.48908,0.04256,0.05635],"tcp_to_object_dist_end":0.30163,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":658.0,"n_steps_budget":1000.0,"object_pos_end":[0.51888,0.07525,0.01602],"object_pos_start":[0.51888,0.07525,0.01602],"object_to_goal_dist_end":0.21895,"object_to_goal_dist_start":0.21895,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"transport_arc","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":5426.0,"raw_peak_contact_force":0.12264,"subtask_id":"transport_arc","tcp_end":[0.5619,0.24446,0.18645],"tcp_start":[0.49838,0.04337,0.31525],"tcp_to_object_dist_end":0.24398,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51888,0.07525,0.01602],"object_pos_start":[0.51888,0.07525,0.01602],"object_to_goal_dist_end":0.21895,"object_to_goal_dist_start":0.21895,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"final_grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":3717.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.55556,0.24154,0.1726],"tcp_start":[0.5619,0.24446,0.18645],"tcp_to_object_dist_end":0.23133,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.87075,"average_solve_count":147.0,"average_success_count":147.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.05423,"descend_1.grasp_z_offset":0.01527,"final_grasp.hold_duration":0.92115,"lift_1.lift_height":0.18041,"transport_arc.arc_height":0.17847,"transport_arc.place_height":0.0451},"optimized_scores":{"best_composite_score":0.11619,"best_fitness_score":0.53619,"best_task_score":0.16022},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":2351.0,"contact_point_centroid":[0.50289,-0.01007,-0.00245],"force_p95":0.14134,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.91408,"mean_force":0.14221,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.54756,0.06774,0.27212]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4823.0,"contact_point_centroid":[0.46834,-0.03741,0.11177],"force_p95":0.1384,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31312,"mean_force":0.08868,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46643,-0.01904,0.11411]},{"body_a":"world","body_b":"grasp_target","contact_count":75.0,"contact_point_centroid":[0.47458,-0.01849,-0.00141],"force_p95":0.28245,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.30913,"mean_force":0.06211,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46397,-0.01898,0.05388]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4106.0,"contact_point_centroid":[0.46858,-0.00062,0.11006],"force_p95":0.14328,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29584,"mean_force":0.10135,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46632,-0.01904,0.1129]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":578.0,"contact_point_centroid":[0.47904,0.00227,0.19594],"force_p95":0.19287,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23442,"mean_force":0.13779,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.47308,-0.01592,0.19861]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":928.0,"contact_point_centroid":[0.47913,-0.03321,0.19705],"force_p95":0.15037,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21915,"mean_force":0.09128,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.47336,-0.01555,0.19977]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.47619,-0.02005,-0.00209],"force_p95":0.15076,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.19908,"mean_force":0.12962,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46604,-0.01903,0.05351]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2559.0,"contact_point_centroid":[0.46602,-0.00017,0.05001],"force_p95":0.10634,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14053,"mean_force":0.07883,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.465,-0.019,0.05245]},{"body_a":"world","body_b":"grasp_target","contact_count":1476.0,"contact_point_centroid":[0.47616,-0.02015,-0.00191],"force_p95":0.13511,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12296,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48745,-0.00863,0.20287]},{"body_a":"world","body_b":"grasp_target","contact_count":352.0,"contact_point_centroid":[0.47616,-0.02015,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.47376,-0.01842,0.08307]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50288,-0.01007,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"final_grasp","phase_type":"grasp","tcp_position_centroid":[0.61393,0.14598,0.23122]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3728.0,"contact_point_centroid":[0.46584,-0.03771,0.05096],"force_p95":0.0912,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09463,"mean_force":0.05593,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.465,-0.019,0.05246]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2325.0,"contact_point_centroid":[0.55255,0.07311,0.27663],"force_p95":0.01118,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01554,"mean_force":0.0105,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.55243,0.07311,0.2743]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1936.0,"contact_point_centroid":[0.61413,0.14599,0.23353],"force_p95":0.01097,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01271,"mean_force":0.01036,"phase_index":5.0,"phase_name":"final_grasp","phase_type":"grasp","tcp_position_centroid":[0.61394,0.14598,0.23124]}],"total_contact_groups":14},"final_pose_error":0.01973,"key_states":{"actual_goal_position":[0.63142,0.15919,0.19002],"final_object_position":[0.50288,-0.01007,0.01602],"final_tcp_position":[0.61873,0.14693,0.24395],"realised_goal_position":[0.63142,0.15919,0.19002],"realised_object_initial_position":[0.47616,-0.02015,0.03]},"peak_contact_force":1.91408,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":370.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.03],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28614,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1476.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.4756,-0.01774,0.10384],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.07786,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":88.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.12262,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":352.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.4728,-0.01917,0.06075],"tcp_start":[0.4756,-0.01774,0.10384],"tcp_to_object_dist_end":0.03491,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":30.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.47611,-0.01933,0.02567],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.2881,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.14578,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":8087.0,"raw_peak_contact_force":0.19908,"subtask_id":"grasp_1","tcp_end":[0.46497,-0.019,0.05242],"tcp_start":[0.4728,-0.01917,0.06075],"tcp_to_object_dist_end":0.02898,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":18.0,"n_steps":418.0,"n_steps_budget":960.0,"object_pos_end":[0.48058,-0.01922,0.15392],"object_pos_start":[0.47611,-0.01933,0.02567],"object_to_goal_dist_end":0.23641,"object_to_goal_dist_start":0.2881,"object_z_max":0.15364,"peak_contact_force":0.13838,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":9004.0,"raw_peak_contact_force":0.31312,"tcp_end":[0.47179,-0.01919,0.18667],"tcp_start":[0.46497,-0.019,0.05242],"tcp_to_object_dist_end":0.03391,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":775.0,"n_steps_budget":1000.0,"object_pos_end":[0.50288,-0.01007,0.01602],"object_pos_start":[0.48058,-0.01922,0.15392],"object_to_goal_dist_end":0.27468,"object_to_goal_dist_start":0.23641,"object_z_max":0.17853,"peak_contact_force":0.12263,"phase_name":"transport_arc","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":6182.0,"raw_peak_contact_force":1.91408,"subtask_id":"transport_arc","tcp_end":[0.61873,0.14693,0.24395],"tcp_start":[0.47179,-0.01919,0.18667],"tcp_to_object_dist_end":0.30004,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50288,-0.01007,0.01602],"object_pos_start":[0.50288,-0.01007,0.01602],"object_to_goal_dist_end":0.27468,"object_to_goal_dist_start":0.27468,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"final_grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":3736.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.61313,0.14574,0.22914],"tcp_start":[0.61873,0.14693,0.24395],"tcp_to_object_dist_end":0.2861,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.87821,"average_solve_count":156.0,"average_success_count":156.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.22884,"descend_1.grasp_z_offset":0.01191,"final_grasp.hold_duration":0.57653,"lift_1.lift_height":0.15598,"transport_arc.arc_height":0.24725,"transport_arc.place_height":0.03571},"optimized_scores":{"best_composite_score":0.14339,"best_fitness_score":0.56339,"best_task_score":0.20682},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":2319.0,"contact_point_centroid":[0.51924,0.02394,-0.00245],"force_p95":0.15071,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.76293,"mean_force":0.14295,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.55674,0.11401,0.21815]},{"body_a":"world","body_b":"grasp_target","contact_count":80.0,"contact_point_centroid":[0.45688,-0.02407,-0.00156],"force_p95":0.32547,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.37428,"mean_force":0.07322,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.4478,-0.02489,0.05118]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5814.0,"contact_point_centroid":[0.45073,-0.00585,0.1013],"force_p95":0.1322,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32097,"mean_force":0.06523,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44967,-0.02495,0.10135]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6450.0,"contact_point_centroid":[0.45084,-0.04341,0.1031],"force_p95":0.10255,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26957,"mean_force":0.0596,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44977,-0.02495,0.1026]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1634.0,"contact_point_centroid":[0.46933,0.0095,0.18134],"force_p95":0.17322,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25173,"mean_force":0.10955,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.46399,-0.00903,0.18272]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2332.0,"contact_point_centroid":[0.47057,-0.02552,0.18445],"force_p95":0.12417,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21727,"mean_force":0.08006,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.46492,-0.00769,0.18427]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.45861,-0.02631,-0.00215],"force_p95":0.17039,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.21053,"mean_force":0.13387,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44986,-0.02497,0.0505]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4184.0,"contact_point_centroid":[0.44949,-0.00576,0.04982],"force_p95":0.09689,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14873,"mean_force":0.05776,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44884,-0.02493,0.04951]},{"body_a":"world","body_b":"grasp_target","contact_count":364.0,"contact_point_centroid":[0.45856,-0.02632,-0.00166],"force_p95":0.13823,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12406,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48663,-0.00767,0.28575]},{"body_a":"world","body_b":"grasp_target","contact_count":1624.0,"contact_point_centroid":[0.45856,-0.02632,-0.00199],"force_p95":0.12264,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12264,"mean_force":0.12261,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.46343,-0.02096,0.16375]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.51928,0.02391,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":5.0,"phase_name":"final_grasp","phase_type":"grasp","tcp_position_centroid":[0.61258,0.19471,0.14757]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4979.0,"contact_point_centroid":[0.44889,-0.04385,0.05016],"force_p95":0.0713,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07472,"mean_force":0.04268,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44885,-0.02493,0.04951]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2252.0,"contact_point_centroid":[0.56251,0.12138,0.2199],"force_p95":0.01156,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0164,"mean_force":0.01057,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.56235,0.12138,0.21761]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1896.0,"contact_point_centroid":[0.61288,0.19473,0.14973],"force_p95":0.01101,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01284,"mean_force":0.01057,"phase_index":5.0,"phase_name":"final_grasp","phase_type":"grasp","tcp_position_centroid":[0.61256,0.19471,0.14754]}],"total_contact_groups":14},"final_pose_error":0.01959,"key_states":{"actual_goal_position":[0.63013,0.20822,0.11412],"final_object_position":[0.51928,0.02391,0.01602],"final_tcp_position":[0.61884,0.1965,0.16075],"realised_goal_position":[0.63013,0.20822,0.11412],"realised_object_initial_position":[0.45856,-0.02632,0.03]},"peak_contact_force":1.76293,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":92.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.026],"object_pos_start":[0.45856,-0.02632,0.03],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30252,"object_z_max":0.03,"peak_contact_force":0.12212,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":364.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.47175,-0.01689,0.26974],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.24428,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":406.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.026],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.12262,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1624.0,"raw_peak_contact_force":0.12264,"subtask_id":"descend_1","tcp_end":[0.4565,-0.02518,0.0573],"tcp_start":[0.47175,-0.01689,0.26974],"tcp_to_object_dist_end":0.03137,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":42.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.45854,-0.02532,0.02519],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30314,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.17729,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10963.0,"raw_peak_contact_force":0.21053,"subtask_id":"grasp_1","tcp_end":[0.44882,-0.02493,0.04948],"tcp_start":[0.4565,-0.02518,0.0573],"tcp_to_object_dist_end":0.02617,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":24.0,"n_steps":345.0,"n_steps_budget":840.0,"object_pos_end":[0.46709,-0.02653,0.13408],"object_pos_start":[0.45854,-0.02532,0.02519],"object_to_goal_dist_end":0.28651,"object_to_goal_dist_start":0.30314,"object_z_max":0.1338,"peak_contact_force":0.13727,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":12344.0,"raw_peak_contact_force":0.37428,"tcp_end":[0.45411,-0.02512,0.16193],"tcp_start":[0.44882,-0.02493,0.04948],"tcp_to_object_dist_end":0.03076,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":860.0,"n_steps_budget":1000.0,"object_pos_end":[0.51928,0.02391,0.01602],"object_pos_start":[0.46709,-0.02653,0.13408],"object_to_goal_dist_end":0.23639,"object_to_goal_dist_start":0.28651,"object_z_max":0.17239,"peak_contact_force":0.12263,"phase_name":"transport_arc","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":8537.0,"raw_peak_contact_force":1.76293,"subtask_id":"transport_arc","tcp_end":[0.61884,0.1965,0.16075],"tcp_start":[0.45411,-0.02512,0.16193],"tcp_to_object_dist_end":0.24626,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51928,0.02391,0.01602],"object_pos_start":[0.51928,0.02391,0.01602],"object_to_goal_dist_end":0.23639,"object_to_goal_dist_start":0.23639,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"final_grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":3696.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.61155,0.19434,0.14543],"tcp_start":[0.61884,0.1965,0.16075],"tcp_to_object_dist_end":0.23304,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```