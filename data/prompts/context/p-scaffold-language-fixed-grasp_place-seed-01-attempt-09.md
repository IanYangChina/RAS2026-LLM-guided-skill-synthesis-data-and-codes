## Search State

- **Seed**: 1
- **Iteration**: 10 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 9 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | admittance_control | position_control | position_control | impedance_control | admittance_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 6 | 0.2929 | 0.38 | ❌ rejected |
| 8 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | admittance_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 5 | 0.1161 | 0.17 | ❌ rejected |
| 7 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | position_control | admittance_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 7 | 0.1617 | 0.34 | ❌ rejected |
| 6 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | admittance_control | position_control | position_control | impedance_control | admittance_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 7 | 0.2287 | 0.35 | ❌ rejected |
| 5 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | admittance_control | position_control | position_control | position_control | admittance_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 4 | 0.2014 | 0.24 | ❌ rejected |

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

## Current Skill (Q=0.293) — your mutation base

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

- **Composite score**: 0.293
- **task_score** (E): 0.376
- **fitness_score**: 0.648  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.125
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.480

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1026 |
| descend_1 | 1.00 | 1.00 | 0.1523 |
| grasp_1 | 1.00 | 1.00 | 0.0116 |
| lift_1 | 1.00 | 1.00 | 0.1279 |
| transport_linear | 0.00 | 0.00 | 0.0002 |
| descend_2 | 1.00 | 1.00 | 0.0008 |
| release_1 | 1.00 | 1.00 | 0.0224 |
| retract_1 | 1.00 | 1.00 | 0.0737 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.480, -0.004, 0.210) | (0.479, -0.000, 0.030)→(0.479, -0.000, 0.026) | 0.276→0.278 | 1.00 / 4.000 | 12.585 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.480, -0.004, 0.210)→(0.475, -0.001, 0.058) | (0.479, -0.000, 0.026)→(0.479, -0.000, 0.026) | 0.278→0.278 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_1 | grasp | 1.00 / step_budget | (0.475, -0.001, 0.058)→(0.468, -0.001, 0.049) | (0.479, -0.000, 0.026)→(0.479, -0.001, 0.025) | 0.278→0.278 | 1.00 / 39.667 | 0.160 | 0.216 |
| lift_1 | lift | 1.00 / step_budget | (0.468, -0.001, 0.049)→(0.474, -0.001, 0.177) | (0.479, -0.001, 0.025)→(0.487, -0.000, 0.149) | 0.278→0.245 | 1.00 / 22.333 | 0.115 | 0.373 |
| transport_linear | approach | 0.00 / guard_failure | (0.565, 0.143, 0.232)→(0.565, 0.143, 0.232) | (0.487, -0.000, 0.149)→(0.581, 0.156, 0.048) | 0.245→0.120 | 0.00 / 0.000 | 0.000 | 0.346 |
| descend_2 | descend | 1.00 / force_exceeded | (0.565, 0.143, 0.232)→(0.565, 0.143, 0.232) | (0.582, 0.157, 0.042)→(0.584, 0.159, 0.022) | 0.126→0.142 | 1.00 / 2.000 | 1615.746 | 1.213 |
| release_1 | release | 1.00 / step_budget | (0.565, 0.143, 0.232)→(0.560, 0.142, 0.254) | (0.584, 0.159, 0.022)→(0.586, 0.155, 0.016) | 0.142→0.148 | 1.00 / 4.000 | 0.123 | 1.788 |
| retract_1 | retract | 1.00 / step_budget | (0.560, 0.142, 0.254)→(0.600, 0.194, 0.286) | (0.586, 0.155, 0.016)→(0.586, 0.155, 0.016) | 0.148→0.148 | 1.00 / 4.000 | 0.123 | 0.123 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.423
- phase_score: 0.281
- phase_breakdown.descend_1_score: 0.823
- phase_breakdown.transport_arc_score: 0.073
- phase_breakdown.grasp_1_score: 1.000
- phase_breakdown.release_1_score: 0.052
- phase_breakdown.approach_1_score: 0.017
- grasp_place_fitness: 0.669

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.669
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.423
- **Median Q (composite search score)**: 0.308
- **K-run variance**: 0.0007
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.458


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.81879,"average_solve_count":149.0,"average_success_count":149.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.27052,"descend_1.grasp_z_offset":0.012,"descend_2.place_z_offset":0.07479,"lift_1.lift_height":0.18222,"transport_linear.transport_height":0.10924,"transport_linear.transport_speed":0.25124},"optimized_scores":{"best_composite_score":0.30777,"best_fitness_score":0.66277,"best_task_score":0.4042},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":2.0,"contact_point_centroid":[0.54202,0.22891,-0.00091],"force_p95":1.93661,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.96758,"mean_force":1.6578,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.54434,0.19263,0.23148]},{"body_a":"world","body_b":"grasp_target","contact_count":795.0,"contact_point_centroid":[0.56646,0.20793,-0.00341],"force_p95":0.6573,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.76182,"mean_force":0.17799,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.54097,0.19165,0.23326]},{"body_a":"world","body_b":"grasp_target","contact_count":83.0,"contact_point_centroid":[0.49943,0.04183,-0.00155],"force_p95":0.34915,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.38913,"mean_force":0.07688,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48799,0.04208,0.04945]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":7178.0,"contact_point_centroid":[0.49322,0.06116,0.11031],"force_p95":0.11104,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29382,"mean_force":0.06936,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49057,0.04227,0.10934]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6639.0,"contact_point_centroid":[0.49311,0.02336,0.11119],"force_p95":0.11113,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28635,"mean_force":0.07211,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49065,0.04228,0.11059]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2971.0,"contact_point_centroid":[0.51722,0.07403,0.19929],"force_p95":0.15848,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25995,"mean_force":0.09954,"phase_index":4.0,"phase_name":"transport_linear","phase_type":"approach","tcp_position_centroid":[0.51145,0.09253,0.20046]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50127,0.0449,-0.00223],"force_p95":0.18555,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24096,"mean_force":0.13883,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49018,0.04229,0.04901]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3369.0,"contact_point_centroid":[0.51923,0.11613,0.20104],"force_p95":0.13645,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20328,"mean_force":0.0889,"phase_index":4.0,"phase_name":"transport_linear","phase_type":"approach","tcp_position_centroid":[0.51317,0.09794,0.20204]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4112.0,"contact_point_centroid":[0.48935,0.02295,0.04903],"force_p95":0.08091,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15701,"mean_force":0.05204,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.48909,0.0422,0.04783]},{"body_a":"world","body_b":"grasp_target","contact_count":288.0,"contact_point_centroid":[0.50118,0.04505,-0.00156],"force_p95":0.13832,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12456,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49899,0.01153,0.29796]},{"body_a":"world","body_b":"grasp_target","contact_count":1808.0,"contact_point_centroid":[0.50118,0.04505,-0.00199],"force_p95":0.12264,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12264,"mean_force":0.12259,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49737,0.0342,0.17716]},{"body_a":"world","body_b":"grasp_target","contact_count":756.0,"contact_point_centroid":[0.56654,0.20797,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":7.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.5484,0.213,0.26648]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5368.0,"contact_point_centroid":[0.4888,0.06141,0.04939],"force_p95":0.07514,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07825,"mean_force":0.04173,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.4891,0.0422,0.04784]},{"body_a":"left_finger","body_b":"right_finger","contact_count":4.0,"contact_point_centroid":[0.54239,0.19217,0.22873],"force_p95":0.0,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0,"mean_force":0.0,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.54219,0.19215,0.22664]}],"total_contact_groups":14},"final_pose_error":0.01986,"key_states":{"actual_goal_position":[0.56442,0.24486,0.14677],"final_object_position":[0.56654,0.20797,0.01602],"final_tcp_position":[0.55765,0.23419,0.28146],"realised_goal_position":[0.56442,0.24486,0.14677],"realised_object_initial_position":[0.50118,0.04505,0.03]},"peak_contact_force":2240.03321,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":73.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02592],"object_pos_start":[0.50118,0.04505,0.03],"object_to_goal_dist_end":0.24193,"object_to_goal_dist_start":0.23992,"object_z_max":0.03,"peak_contact_force":0.12255,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":288.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.49877,0.02577,0.29613],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.2709,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":452.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.02592],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.24193,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1808.0,"raw_peak_contact_force":0.12264,"subtask_id":"descend_1","tcp_end":[0.49726,0.04287,0.05702],"tcp_start":[0.49877,0.02577,0.29613],"tcp_to_object_dist_end":0.03132,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":42.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50119,0.04318,0.0252],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.24384,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"peak_contact_force":0.17993,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11280.0,"raw_peak_contact_force":0.24096,"subtask_id":"grasp_1","tcp_end":[0.48906,0.04219,0.0478],"tcp_start":[0.49726,0.04287,0.05702],"tcp_to_object_dist_end":0.02567,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":24.0,"n_steps":453.0,"n_steps_budget":1000.0,"object_pos_end":[0.51014,0.04371,0.16016],"object_pos_start":[0.50119,0.04318,0.0252],"object_to_goal_dist_end":0.20877,"object_to_goal_dist_start":0.24384,"object_z_max":0.15989,"peak_contact_force":0.11009,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":13900.0,"raw_peak_contact_force":0.38913,"tcp_end":[0.49674,0.04277,0.18793],"tcp_start":[0.48906,0.04219,0.0478],"tcp_to_object_dist_end":0.03085,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":404.0,"n_steps_budget":1000.0,"object_pos_end":[0.56238,0.20541,0.04843],"object_pos_start":[0.51014,0.04371,0.16016],"object_to_goal_dist_end":0.10599,"object_to_goal_dist_start":0.20877,"object_z_max":0.18507,"peak_contact_force":0.0,"phase_name":"transport_linear","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":6340.0,"raw_peak_contact_force":0.25995,"subtask_id":"transport_arc","tcp_end":[0.54448,0.19213,0.23177],"tcp_start":[0.54453,0.19196,0.23176],"tcp_to_object_dist_end":0.18469,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":6.0,"n_steps_budget":1000.0,"object_pos_end":[0.56455,0.20905,0.02135],"object_pos_start":[0.56289,0.20638,0.04183],"object_to_goal_dist_end":0.13044,"object_to_goal_dist_start":0.11179,"object_z_max":0.04183,"peak_contact_force":2240.03321,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2.0,"raw_peak_contact_force":1.96758,"tcp_end":[0.54432,0.19277,0.23132],"tcp_start":[0.54448,0.19213,0.23177],"tcp_to_object_dist_end":0.21156,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.56654,0.20797,0.01602],"object_pos_start":[0.56455,0.20905,0.02135],"object_to_goal_dist_end":0.13588,"object_to_goal_dist_start":0.13044,"object_z_max":0.02135,"peak_contact_force":0.12261,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":799.0,"raw_peak_contact_force":1.76182,"subtask_id":"release_1","tcp_end":[0.53982,0.19115,0.25347],"tcp_start":[0.54432,0.19277,0.23132],"tcp_to_object_dist_end":0.23954,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":189.0,"n_steps_budget":600.0,"object_pos_end":[0.56654,0.20797,0.01602],"object_pos_start":[0.56654,0.20797,0.01602],"object_to_goal_dist_end":0.13588,"object_to_goal_dist_start":0.13588,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":756.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.55765,0.23419,0.28146],"tcp_start":[0.53982,0.19115,0.25347],"tcp_to_object_dist_end":0.26688,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.94444,"average_solve_count":144.0,"average_success_count":144.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.05011,"descend_1.grasp_z_offset":0.01068,"descend_2.place_z_offset":0.07314,"lift_1.lift_height":0.15234,"transport_linear.transport_height":0.13092,"transport_linear.transport_speed":0.19107},"optimized_scores":{"best_composite_score":0.25699,"best_fitness_score":0.61199,"best_task_score":0.3008},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":795.0,"contact_point_centroid":[0.60209,0.1225,-0.00356],"force_p95":0.7262,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06932,"mean_force":0.18509,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.57907,0.10615,0.26734]},{"body_a":"world","body_b":"grasp_target","contact_count":76.0,"contact_point_centroid":[0.47431,-0.01831,-0.0014],"force_p95":0.34568,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.40656,"mean_force":0.07984,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46391,-0.01899,0.04947]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5168.0,"contact_point_centroid":[0.5188,0.01121,0.19782],"force_p95":0.14286,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.3484,"mean_force":0.08701,"phase_index":4.0,"phase_name":"transport_linear","phase_type":"approach","tcp_position_centroid":[0.51299,0.02971,0.1985]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6269.0,"contact_point_centroid":[0.46762,-0.03803,0.09844],"force_p95":0.10179,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27589,"mean_force":0.06122,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46615,-0.01906,0.09755]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5666.0,"contact_point_centroid":[0.46782,-2e-05,0.09842],"force_p95":0.10707,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26725,"mean_force":0.06643,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46615,-0.01906,0.09764]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.47619,-0.02006,-0.00209],"force_p95":0.14964,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.20162,"mean_force":0.12966,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46596,-0.01904,0.04911]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5147.0,"contact_point_centroid":[0.51989,0.0495,0.19871],"force_p95":0.12781,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1925,"mean_force":0.08691,"phase_index":4.0,"phase_name":"transport_linear","phase_type":"approach","tcp_position_centroid":[0.51414,0.03099,0.19963]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4176.0,"contact_point_centroid":[0.46562,0.00019,0.04888],"force_p95":0.07826,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14256,"mean_force":0.05134,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46491,-0.01902,0.04805]},{"body_a":"world","body_b":"grasp_target","contact_count":1508.0,"contact_point_centroid":[0.47616,-0.02015,-0.00191],"force_p95":0.13496,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12295,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48741,-0.00864,0.20095]},{"body_a":"world","body_b":"grasp_target","contact_count":356.0,"contact_point_centroid":[0.47616,-0.02015,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.47369,-0.01844,0.07883]},{"body_a":"world","body_b":"grasp_target","contact_count":980.0,"contact_point_centroid":[0.60219,0.12256,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":7.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.60014,0.1289,0.30459]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4951.0,"contact_point_centroid":[0.46497,-0.03811,0.04913],"force_p95":0.07084,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07296,"mean_force":0.04421,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46491,-0.01902,0.04805]},{"body_a":"left_finger","body_b":"right_finger","contact_count":33.0,"contact_point_centroid":[0.58068,0.10643,0.2634],"force_p95":0.01649,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01649,"mean_force":0.01141,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.58023,0.10642,0.26107]}],"total_contact_groups":13},"final_pose_error":0.01988,"key_states":{"actual_goal_position":[0.63142,0.15919,0.19002],"final_object_position":[0.60219,0.12256,0.01602],"final_tcp_position":[0.62218,0.15089,0.3245],"realised_goal_position":[0.63142,0.15919,0.19002],"realised_object_initial_position":[0.47616,-0.02015,0.03]},"peak_contact_force":359.27487,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":378.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.03],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28614,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1508.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.47555,-0.01777,0.09988],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.07391,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":89.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.12262,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":356.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.47275,-0.01918,0.05631],"tcp_start":[0.47555,-0.01777,0.09988],"tcp_to_object_dist_end":0.0305,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":42.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.47611,-0.01938,0.02566],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28814,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.14695,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10927.0,"raw_peak_contact_force":0.20162,"subtask_id":"grasp_1","tcp_end":[0.46488,-0.01901,0.04802],"tcp_start":[0.47275,-0.01918,0.05631],"tcp_to_object_dist_end":0.02502,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":348.0,"n_steps_budget":840.0,"object_pos_end":[0.48595,-0.01957,0.13327],"object_pos_start":[0.47611,-0.01938,0.02566],"object_to_goal_dist_end":0.23736,"object_to_goal_dist_start":0.28814,"object_z_max":0.133,"peak_contact_force":0.10572,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":12011.0,"raw_peak_contact_force":0.40656,"tcp_end":[0.47139,-0.01922,0.15869],"tcp_start":[0.46488,-0.01901,0.04802],"tcp_to_object_dist_end":0.0293,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":557.0,"n_steps_budget":1000.0,"object_pos_end":[0.59973,0.12088,0.04817],"object_pos_start":[0.48595,-0.01957,0.13327],"object_to_goal_dist_end":0.15031,"object_to_goal_dist_start":0.23736,"object_z_max":0.21062,"peak_contact_force":0.0,"phase_name":"transport_linear","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":10315.0,"raw_peak_contact_force":0.3484,"subtask_id":"transport_arc","tcp_end":[0.5819,0.10618,0.26602],"tcp_start":[0.58186,0.10606,0.26595],"tcp_to_object_dist_end":0.21907,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":5.0,"n_steps_budget":1000.0,"object_pos_end":[0.60192,0.1234,0.02227],"object_pos_start":[0.60036,0.1216,0.04096],"object_to_goal_dist_end":0.17404,"object_to_goal_dist_start":0.15682,"object_z_max":0.04096,"peak_contact_force":359.27487,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.58207,0.10666,0.26584],"tcp_start":[0.5819,0.10618,0.26602],"tcp_to_object_dist_end":0.24496,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.60219,0.12256,0.01602],"object_pos_start":[0.60192,0.1234,0.02227],"object_to_goal_dist_end":0.1802,"object_to_goal_dist_start":0.17404,"object_z_max":0.02227,"peak_contact_force":0.1226,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":828.0,"raw_peak_contact_force":2.06932,"subtask_id":"release_1","tcp_end":[0.57804,0.10588,0.28732],"tcp_start":[0.58207,0.10666,0.26584],"tcp_to_object_dist_end":0.27288,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":245.0,"n_steps_budget":600.0,"object_pos_end":[0.60219,0.12256,0.01602],"object_pos_start":[0.60219,0.12256,0.01602],"object_to_goal_dist_end":0.1802,"object_to_goal_dist_start":0.1802,"object_z_max":0.01602,"peak_contact_force":0.12262,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":980.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.62218,0.15089,0.3245],"tcp_start":[0.57804,0.10588,0.28732],"tcp_to_object_dist_end":0.31042,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.86364,"average_solve_count":154.0,"average_success_count":154.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.18604,"descend_1.grasp_z_offset":0.01358,"descend_2.place_z_offset":0.05217,"lift_1.lift_height":0.17789,"transport_linear.transport_height":0.103,"transport_linear.transport_speed":0.13776},"optimized_scores":{"best_composite_score":0.314,"best_fitness_score":0.669,"best_task_score":0.42311},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":4.0,"contact_point_centroid":[0.56204,0.15121,-0.00249],"force_p95":1.66813,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.67007,"mean_force":1.64335,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.5685,0.13042,0.19877]},{"body_a":"world","body_b":"grasp_target","contact_count":738.0,"contact_point_centroid":[0.58799,0.13675,-0.00328],"force_p95":0.78784,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.53172,"mean_force":0.19131,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.56451,0.12984,0.20044]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3997.0,"contact_point_centroid":[0.50519,0.02054,0.18528],"force_p95":0.14706,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.42936,"mean_force":0.10406,"phase_index":4.0,"phase_name":"transport_linear","phase_type":"approach","tcp_position_centroid":[0.5,0.03865,0.18833]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5955.0,"contact_point_centroid":[0.4503,-0.04354,0.10901],"force_p95":0.13426,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32447,"mean_force":0.07283,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44943,-0.02503,0.11017]},{"body_a":"world","body_b":"grasp_target","contact_count":78.0,"contact_point_centroid":[0.45673,-0.02484,-0.00145],"force_p95":0.29557,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.32315,"mean_force":0.06597,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44756,-0.02502,0.0532]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4722.0,"contact_point_centroid":[0.45139,-0.00654,0.11151],"force_p95":0.13455,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30389,"mean_force":0.08697,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44966,-0.02504,0.1135]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3888.0,"contact_point_centroid":[0.50945,0.06211,0.18601],"force_p95":0.13662,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23324,"mean_force":0.10527,"phase_index":4.0,"phase_name":"transport_linear","phase_type":"approach","tcp_position_centroid":[0.50398,0.04402,0.18891]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.45859,-0.02618,-0.00213],"force_p95":0.15551,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.20684,"mean_force":0.13206,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44963,-0.0251,0.05264]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3138.0,"contact_point_centroid":[0.4505,-0.00611,0.05008],"force_p95":0.10226,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1463,"mean_force":0.06494,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44861,-0.02506,0.05165]},{"body_a":"world","body_b":"grasp_target","contact_count":584.0,"contact_point_centroid":[0.45856,-0.02632,-0.00178],"force_p95":0.13791,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12346,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48397,-0.00923,0.26744]},{"body_a":"world","body_b":"grasp_target","contact_count":1244.0,"contact_point_centroid":[0.5878,0.13589,-0.00199],"force_p95":0.12265,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12268,"mean_force":0.12262,"phase_index":7.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.59149,0.16462,0.23381]},{"body_a":"world","body_b":"grasp_target","contact_count":1332.0,"contact_point_centroid":[0.45856,-0.02632,-0.00199],"force_p95":0.12264,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12264,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.46082,-0.02242,0.14635]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4537.0,"contact_point_centroid":[0.44837,-0.04388,0.05127],"force_p95":0.08857,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09387,"mean_force":0.04838,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44862,-0.02506,0.05166]}],"total_contact_groups":13},"final_pose_error":0.01987,"key_states":{"actual_goal_position":[0.63013,0.20822,0.11412],"final_object_position":[0.5878,0.13589,0.01602],"final_tcp_position":[0.61978,0.19789,0.25066],"realised_goal_position":[0.63013,0.20822,0.11412],"realised_object_initial_position":[0.45856,-0.02632,0.03]},"peak_contact_force":2247.92848,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":147.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.03],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30252,"object_z_max":0.03,"peak_contact_force":37.50955,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":584.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.46693,-0.01968,0.23254],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.2068,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":333.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.12262,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1332.0,"raw_peak_contact_force":0.12264,"subtask_id":"descend_1","tcp_end":[0.45624,-0.02532,0.05944],"tcp_start":[0.46693,-0.01968,0.23254],"tcp_to_object_dist_end":0.03351,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":35.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.45851,-0.02536,0.02546],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30311,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.15257,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":9475.0,"raw_peak_contact_force":0.20684,"subtask_id":"grasp_1","tcp_end":[0.44859,-0.02506,0.05162],"tcp_start":[0.45624,-0.02532,0.05944],"tcp_to_object_dist_end":0.02799,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":20.0,"n_steps":405.0,"n_steps_budget":960.0,"object_pos_end":[0.46441,-0.02548,0.15254],"object_pos_start":[0.45851,-0.02536,0.02546],"object_to_goal_dist_end":0.28905,"object_to_goal_dist_start":0.30311,"object_z_max":0.15226,"peak_contact_force":0.12902,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":10755.0,"raw_peak_contact_force":0.32447,"tcp_end":[0.45434,-0.02517,0.184],"tcp_start":[0.44859,-0.02506,0.05162],"tcp_to_object_dist_end":0.03304,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":533.0,"n_steps_budget":1000.0,"object_pos_end":[0.58229,0.14137,0.04847],"object_pos_start":[0.46441,-0.02548,0.15254],"object_to_goal_dist_end":0.1052,"object_to_goal_dist_start":0.28905,"object_z_max":0.15984,"peak_contact_force":0.0,"phase_name":"transport_linear","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":7885.0,"raw_peak_contact_force":0.42936,"subtask_id":"transport_arc","tcp_end":[0.56846,0.12994,0.19926],"tcp_start":[0.5685,0.12981,0.19932],"tcp_to_object_dist_end":0.15185,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":7.0,"n_steps_budget":1000.0,"object_pos_end":[0.58555,0.14469,0.02168],"object_pos_start":[0.58292,0.14221,0.04254],"object_to_goal_dist_end":0.1207,"object_to_goal_dist_start":0.10821,"object_z_max":0.04254,"peak_contact_force":2247.92848,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4.0,"raw_peak_contact_force":1.67007,"tcp_end":[0.56864,0.13071,0.19839],"tcp_start":[0.56846,0.12994,0.19926],"tcp_to_object_dist_end":0.17807,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.5878,0.1359,0.01602],"object_pos_start":[0.58555,0.14469,0.02168],"object_to_goal_dist_end":0.12901,"object_to_goal_dist_start":0.1207,"object_z_max":0.02168,"peak_contact_force":0.12268,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":738.0,"raw_peak_contact_force":1.53172,"subtask_id":"release_1","tcp_end":[0.56334,0.12952,0.22031],"tcp_start":[0.56864,0.13071,0.19839],"tcp_to_object_dist_end":0.20585,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":311.0,"n_steps_budget":720.0,"object_pos_end":[0.5878,0.13589,0.01602],"object_pos_start":[0.5878,0.1359,0.01602],"object_to_goal_dist_end":0.12902,"object_to_goal_dist_start":0.12901,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1244.0,"raw_peak_contact_force":0.12268,"tcp_end":[0.61978,0.19789,0.25066],"tcp_start":[0.56334,0.12952,0.22031],"tcp_to_object_dist_end":0.24479,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```