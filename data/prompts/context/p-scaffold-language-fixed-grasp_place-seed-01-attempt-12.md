## Search State

- **Seed**: 1
- **Iteration**: 13 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 12 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | admittance_control | position_control | position_control | position_control | admittance_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 4 | 0.2658 | 0.37 | ❌ rejected |
| 11 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | admittance_control | position_control | position_control | position_control | admittance_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 6 | -0.1066 | 0.18 | ❌ rejected |
| 10 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | admittance_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 5 | 0.2160 | 0.37 | ❌ rejected |
| 9 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | admittance_control | position_control | position_control | impedance_control | admittance_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 6 | 0.2929 | 0.38 | ❌ rejected |
| 8 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | admittance_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 5 | 0.1161 | 0.17 | ❌ rejected |

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

## Current Skill (Q=0.266) — your mutation base

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

- **Composite score**: 0.266
- **task_score** (E): 0.369
- **fitness_score**: 0.646  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.380

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.0629 |
| descend_1 | 1.00 | 1.00 | 0.1922 |
| grasp_1 | 1.00 | 1.00 | 0.0116 |
| lift_1 | 1.00 | 1.00 | 0.1302 |
| transport_arc | 1.00 | 1.00 | 0.2614 |
| descend_2 | 1.00 | 1.00 | 0.0984 |
| release_1 | 1.00 | 1.00 | 0.0198 |
| retract_1 | 1.00 | 1.00 | 0.0835 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.484, 0.001, 0.248) | (0.479, -0.000, 0.030)→(0.479, -0.000, 0.026) | 0.276→0.278 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.484, 0.001, 0.248)→(0.476, -0.000, 0.057) | (0.479, -0.000, 0.026)→(0.479, -0.000, 0.026) | 0.278→0.278 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_1 | grasp | 1.00 / step_budget | (0.476, -0.000, 0.057)→(0.468, -0.001, 0.048) | (0.479, -0.000, 0.026)→(0.479, -0.000, 0.026) | 0.278→0.278 | 1.00 / 41.000 | 0.157 | 0.214 |
| lift_1 | lift | 1.00 / step_budget | (0.468, -0.001, 0.048)→(0.474, -0.000, 0.178) | (0.479, -0.000, 0.026)→(0.488, -0.000, 0.152) | 0.278→0.246 | 1.00 / 23.667 | 0.105 | 0.381 |
| transport_arc | approach | 1.00 / step_budget | (0.474, -0.000, 0.178)→(0.600, 0.193, 0.277) | (0.488, -0.000, 0.152)→(0.570, 0.130, 0.072) | 0.246→0.154 | 1.00 / 11.333 | 3249.676 | 1.335 |
| descend_2 | descend | 1.00 / step_budget | (0.600, 0.193, 0.277)→(0.604, 0.200, 0.179) | (0.570, 0.130, 0.072)→(0.571, 0.132, 0.046) | 0.154→0.134 | 1.00 / 11.333 | 94253.222 | 0.172 |
| release_1 | release | 1.00 / step_budget | (0.604, 0.200, 0.179)→(0.598, 0.198, 0.198) | (0.571, 0.132, 0.046)→(0.565, 0.132, 0.020) | 0.134→0.160 | 1.00 / 4.000 | 0.129 | 0.479 |
| retract_1 | retract | 1.00 / step_budget | (0.598, 0.198, 0.198)→(0.605, 0.202, 0.281) | (0.565, 0.132, 0.020)→(0.565, 0.132, 0.019) | 0.160→0.160 | 1.00 / 4.000 | 0.123 | 0.134 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: 1.000
- terminal_score: 0.546
- phase_score: 0.363
- phase_breakdown.descend_1_score: 0.883
- phase_breakdown.transport_arc_score: 0.122
- phase_breakdown.grasp_1_score: 1.000
- phase_breakdown.release_1_score: 0.380
- phase_breakdown.approach_1_score: 0.006
- grasp_place_fitness: 0.735

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.735
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.546
- **Median Q (composite search score)**: 0.254
- **K-run variance**: 0.0047
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.346


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.92268,"average_solve_count":194.0,"average_success_count":194.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.18922,"descend_1.grasp_z_offset":0.01212,"lift_1.lift_height":0.18939,"transport_arc.transport_arc_height":0.1519},"optimized_scores":{"best_composite_score":0.25387,"best_fitness_score":0.63387,"best_task_score":0.3468},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":1300.0,"contact_point_centroid":[0.54737,0.15625,-0.00292],"force_p95":0.43497,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.00268,"mean_force":0.15959,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.54316,0.18848,0.26323]},{"body_a":"world","body_b":"grasp_target","contact_count":82.0,"contact_point_centroid":[0.49911,0.04207,-0.00152],"force_p95":0.35116,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.38746,"mean_force":0.07764,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48794,0.04241,0.04967]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":7436.0,"contact_point_centroid":[0.49337,0.06146,0.11356],"force_p95":0.11117,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29357,"mean_force":0.06998,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49057,0.04256,0.11273]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":7088.0,"contact_point_centroid":[0.49301,0.02367,0.11393],"force_p95":0.11076,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28972,"mean_force":0.07089,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49063,0.04256,0.11353]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2495.0,"contact_point_centroid":[0.5115,0.05603,0.20583],"force_p95":0.14419,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25734,"mean_force":0.09226,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.50529,0.07438,0.20747]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50126,0.04492,-0.0022],"force_p95":0.17856,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.23738,"mean_force":0.1372,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49014,0.04262,0.04925]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2438.0,"contact_point_centroid":[0.51235,0.09515,0.20682],"force_p95":0.14156,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17068,"mean_force":0.09488,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.50608,0.07686,0.20864]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4130.0,"contact_point_centroid":[0.48928,0.02336,0.04924],"force_p95":0.07952,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14315,"mean_force":0.05162,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.48905,0.04252,0.04807]},{"body_a":"world","body_b":"grasp_target","contact_count":572.0,"contact_point_centroid":[0.50118,0.04505,-0.00178],"force_p95":0.13791,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12348,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49897,0.01555,0.26853]},{"body_a":"world","body_b":"grasp_target","contact_count":1348.0,"contact_point_centroid":[0.50118,0.04505,-0.00199],"force_p95":0.12264,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12264,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49707,0.03805,0.14649]},{"body_a":"world","body_b":"grasp_target","contact_count":780.0,"contact_point_centroid":[0.54746,0.15627,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.55888,0.23617,0.23208]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.54746,0.15627,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.55611,0.23892,0.17591]},{"body_a":"world","body_b":"grasp_target","contact_count":1236.0,"contact_point_centroid":[0.54746,0.15627,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":7.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.5569,0.24016,0.2362]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4897.0,"contact_point_centroid":[0.48955,0.06175,0.04917],"force_p95":0.07889,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08067,"mean_force":0.04537,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.48906,0.04252,0.04808]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1184.0,"contact_point_centroid":[0.54586,0.19504,0.26875],"force_p95":0.01247,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01641,"mean_force":0.0107,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.5454,0.19501,0.2665]},{"body_a":"left_finger","body_b":"right_finger","contact_count":827.0,"contact_point_centroid":[0.55923,0.23619,0.23443],"force_p95":0.01097,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01269,"mean_force":0.0105,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.55888,0.23617,0.23214]}],"total_contact_groups":17},"final_pose_error":0.01984,"key_states":{"actual_goal_position":[0.56442,0.24486,0.14677],"final_object_position":[0.54746,0.15627,0.01602],"final_tcp_position":[0.56099,0.24289,0.27733],"realised_goal_position":[0.56442,0.24486,0.14677],"realised_object_initial_position":[0.50118,0.04505,0.03]},"peak_contact_force":273010.71552,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":144.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.03],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.23992,"object_z_max":0.03,"peak_contact_force":0.12264,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":572.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.49863,0.03312,0.23504],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.20937,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":337.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"peak_contact_force":0.12262,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1348.0,"raw_peak_contact_force":0.12264,"subtask_id":"descend_1","tcp_end":[0.49719,0.04322,0.05724],"tcp_start":[0.49863,0.03312,0.23504],"tcp_to_object_dist_end":0.03153,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50118,0.04341,0.02528],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.24361,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"peak_contact_force":0.17353,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10827.0,"raw_peak_contact_force":0.23738,"subtask_id":"grasp_1","tcp_end":[0.48902,0.04252,0.04804],"tcp_start":[0.49719,0.04322,0.05724],"tcp_to_object_dist_end":0.02582,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":25.0,"n_steps":475.0,"n_steps_budget":1000.0,"object_pos_end":[0.51023,0.04386,0.16734],"object_pos_start":[0.50118,0.04341,0.02528],"object_to_goal_dist_end":0.20919,"object_to_goal_dist_start":0.24361,"object_z_max":0.16708,"peak_contact_force":0.10355,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":14606.0,"raw_peak_contact_force":0.38746,"tcp_end":[0.49686,0.04302,0.19541],"tcp_start":[0.48902,0.04252,0.04804],"tcp_to_object_dist_end":0.0311,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":672.0,"n_steps_budget":1000.0,"object_pos_end":[0.54746,0.15627,0.01602],"object_pos_start":[0.51023,0.04386,0.16734],"object_to_goal_dist_end":0.15885,"object_to_goal_dist_start":0.20919,"object_z_max":0.19414,"peak_contact_force":9748.78855,"phase_name":"transport_arc","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":7417.0,"raw_peak_contact_force":2.00268,"subtask_id":"transport_arc","tcp_end":[0.55812,0.23206,0.28497],"tcp_start":[0.49686,0.04302,0.19541],"tcp_to_object_dist_end":0.27963,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":195.0,"n_steps_budget":1000.0,"object_pos_end":[0.54746,0.15627,0.01602],"object_pos_start":[0.54746,0.15627,0.01602],"object_to_goal_dist_end":0.15885,"object_to_goal_dist_start":0.15885,"object_z_max":0.01602,"peak_contact_force":273010.71552,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1607.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.56043,0.24085,0.17585],"tcp_start":[0.55812,0.23206,0.28497],"tcp_to_object_dist_end":0.1813,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54746,0.15627,0.01602],"object_pos_start":[0.54746,0.15627,0.01602],"object_to_goal_dist_end":0.15885,"object_to_goal_dist_start":0.15885,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1024.0,"raw_peak_contact_force":0.12263,"subtask_id":"release_1","tcp_end":[0.5547,0.23821,0.19594],"tcp_start":[0.56043,0.24085,0.17585],"tcp_to_object_dist_end":0.19784,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":309.0,"n_steps_budget":660.0,"object_pos_end":[0.54746,0.15627,0.01602],"object_pos_start":[0.54746,0.15627,0.01602],"object_to_goal_dist_end":0.15885,"object_to_goal_dist_start":0.15885,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1236.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.56099,0.24289,0.27733],"tcp_start":[0.5547,0.23821,0.19594],"tcp_to_object_dist_end":0.27563,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.92424,"average_solve_count":198.0,"average_success_count":198.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.17258,"descend_1.grasp_z_offset":0.01161,"lift_1.lift_height":0.14327,"transport_arc.transport_arc_height":0.15416},"optimized_scores":{"best_composite_score":0.18807,"best_fitness_score":0.56807,"best_task_score":0.21383},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":2574.0,"contact_point_centroid":[0.53881,0.03793,-0.0024],"force_p95":0.13022,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.79036,"mean_force":0.14225,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.57324,0.0968,0.26951]},{"body_a":"world","body_b":"grasp_target","contact_count":74.0,"contact_point_centroid":[0.47427,-0.01883,-0.00142],"force_p95":0.32354,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.37079,"mean_force":0.07688,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46426,-0.0192,0.04995]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2778.0,"contact_point_centroid":[0.49451,-0.01545,0.17004],"force_p95":0.13531,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28603,"mean_force":0.08311,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.48863,0.00295,0.16998]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5396.0,"contact_point_centroid":[0.46779,-0.00014,0.09603],"force_p95":0.10424,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.273,"mean_force":0.06432,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46644,-0.01923,0.09539]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6034.0,"contact_point_centroid":[0.46754,-0.03823,0.09605],"force_p95":0.09733,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27038,"mean_force":0.05879,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46644,-0.01923,0.09531]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2373.0,"contact_point_centroid":[0.49325,0.01999,0.1688],"force_p95":0.1566,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24093,"mean_force":0.09269,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.48724,0.00133,0.16835]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.47618,-0.02007,-0.00208],"force_p95":0.14554,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.19047,"mean_force":0.1286,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46629,-0.01925,0.04967]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4104.0,"contact_point_centroid":[0.46613,-1e-05,0.04941],"force_p95":0.07866,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14034,"mean_force":0.05214,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46524,-0.01923,0.04861]},{"body_a":"world","body_b":"grasp_target","contact_count":620.0,"contact_point_centroid":[0.47616,-0.02015,-0.00179],"force_p95":0.13791,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12341,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49005,-0.00715,0.26202]},{"body_a":"world","body_b":"grasp_target","contact_count":1256.0,"contact_point_centroid":[0.47616,-0.02015,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12264,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.4756,-0.01725,0.13943]},{"body_a":"world","body_b":"grasp_target","contact_count":752.0,"contact_point_centroid":[0.53885,0.03797,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.62496,0.15379,0.27564]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.53885,0.03797,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.62329,0.15554,0.21789]},{"body_a":"world","body_b":"grasp_target","contact_count":1348.0,"contact_point_centroid":[0.53885,0.03797,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":7.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.62443,0.15637,0.27838]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4927.0,"contact_point_centroid":[0.4653,-0.03831,0.04953],"force_p95":0.07004,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07206,"mean_force":0.0443,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46524,-0.01923,0.04862]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2527.0,"contact_point_centroid":[0.57766,0.1014,0.2767],"force_p95":0.01133,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01566,"mean_force":0.01055,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.57744,0.1014,0.27445]},{"body_a":"left_finger","body_b":"right_finger","contact_count":803.0,"contact_point_centroid":[0.6252,0.15379,0.27824],"force_p95":0.01096,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01263,"mean_force":0.01043,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.62496,0.15378,0.27584]}],"total_contact_groups":17},"final_pose_error":0.01997,"key_states":{"actual_goal_position":[0.63142,0.15919,0.19002],"final_object_position":[0.53885,0.03797,0.01602],"final_tcp_position":[0.62859,0.15809,0.32028],"realised_goal_position":[0.63142,0.15919,0.19002],"realised_object_initial_position":[0.47616,-0.02015,0.03]},"peak_contact_force":9748.81511,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":156.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.03],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28614,"object_z_max":0.03,"peak_contact_force":0.12264,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":620.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.4797,-0.01522,0.22121],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.19529,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":314.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.12262,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1256.0,"raw_peak_contact_force":0.12264,"subtask_id":"descend_1","tcp_end":[0.47309,-0.0194,0.05691],"tcp_start":[0.4797,-0.01522,0.22121],"tcp_to_object_dist_end":0.03105,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.4761,-0.01947,0.02571],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28817,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.14339,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10831.0,"raw_peak_contact_force":0.19047,"subtask_id":"grasp_1","tcp_end":[0.46521,-0.01923,0.04858],"tcp_start":[0.47309,-0.0194,0.05691],"tcp_to_object_dist_end":0.02533,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":319.0,"n_steps_budget":780.0,"object_pos_end":[0.48557,-0.01964,0.12419],"object_pos_start":[0.4761,-0.01947,0.02571],"object_to_goal_dist_end":0.23997,"object_to_goal_dist_start":0.28817,"object_z_max":0.12392,"peak_contact_force":0.10523,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":11504.0,"raw_peak_contact_force":0.37079,"tcp_end":[0.47126,-0.01932,0.1497],"tcp_start":[0.46521,-0.01923,0.04858],"tcp_to_object_dist_end":0.02925,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":964.0,"n_steps_budget":1000.0,"object_pos_end":[0.53885,0.03797,0.01602],"object_pos_start":[0.48557,-0.01964,0.12419],"object_to_goal_dist_end":0.23138,"object_to_goal_dist_start":0.23997,"object_z_max":0.16107,"peak_contact_force":0.12263,"phase_name":"transport_arc","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":10252.0,"raw_peak_contact_force":1.79036,"subtask_id":"transport_arc","tcp_end":[0.62321,0.15121,0.32804],"tcp_start":[0.47126,-0.01932,0.1497],"tcp_to_object_dist_end":0.34248,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":7.0,"n_steps":188.0,"n_steps_budget":1000.0,"object_pos_end":[0.53885,0.03797,0.01602],"object_pos_start":[0.53885,0.03797,0.01602],"object_to_goal_dist_end":0.23138,"object_to_goal_dist_start":0.23138,"object_z_max":0.01602,"peak_contact_force":9748.81511,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1555.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.62727,0.15668,0.21908],"tcp_start":[0.62321,0.15121,0.32804],"tcp_to_object_dist_end":0.25129,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53885,0.03797,0.01602],"object_pos_start":[0.53885,0.03797,0.01602],"object_to_goal_dist_end":0.23138,"object_to_goal_dist_start":0.23138,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1021.0,"raw_peak_contact_force":0.12263,"subtask_id":"release_1","tcp_end":[0.62201,0.15511,0.23737],"tcp_start":[0.62727,0.15668,0.21908],"tcp_to_object_dist_end":0.26388,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":337.0,"n_steps_budget":660.0,"object_pos_end":[0.53885,0.03797,0.01602],"object_pos_start":[0.53885,0.03797,0.01602],"object_to_goal_dist_end":0.23138,"object_to_goal_dist_start":0.23138,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1348.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.62859,0.15809,0.32028],"tcp_start":[0.62201,0.15511,0.23737],"tcp_to_object_dist_end":0.3392,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.8381,"average_solve_count":210.0,"average_success_count":210.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.25656,"descend_1.grasp_z_offset":0.01035,"lift_1.lift_height":0.18349,"transport_arc.transport_arc_height":0.11421},"optimized_scores":{"best_composite_score":0.3554,"best_fitness_score":0.7354,"best_task_score":0.54579},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":298.0,"contact_point_centroid":[0.60939,0.2028,-0.00401],"force_p95":0.83323,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.19156,"mean_force":0.23215,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.61668,0.20106,0.14893]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":489.0,"contact_point_centroid":[0.62543,0.22102,0.13077],"force_p95":0.1666,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.39958,"mean_force":0.10418,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.62069,0.20261,0.13603]},{"body_a":"world","body_b":"grasp_target","contact_count":76.0,"contact_point_centroid":[0.45672,-0.02439,-0.00143],"force_p95":0.341,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.38461,"mean_force":0.08072,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44791,-0.0248,0.04947]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":550.0,"contact_point_centroid":[0.62538,0.18446,0.13152],"force_p95":0.14447,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.35952,"mean_force":0.09258,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.62079,0.20264,0.13621]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":7831.0,"contact_point_centroid":[0.45105,-0.04383,0.11298],"force_p95":0.10137,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27633,"mean_force":0.06053,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44971,-0.02488,0.11207]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6968.0,"contact_point_centroid":[0.45141,-0.00583,0.11333],"force_p95":0.10673,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27495,"mean_force":0.06638,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44973,-0.02488,0.11262]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1207.0,"contact_point_centroid":[0.62577,0.21757,0.17836],"force_p95":0.16423,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26981,"mean_force":0.11237,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.62047,0.1993,0.182]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1315.0,"contact_point_centroid":[0.62581,0.18108,0.17732],"force_p95":0.15624,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26117,"mean_force":0.10353,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.62053,0.19939,0.18097]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.45859,-0.02622,-0.00212],"force_p95":0.15724,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.21331,"mean_force":0.13172,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44999,-0.02488,0.04898]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":9382.0,"contact_point_centroid":[0.53908,0.06448,0.20134],"force_p95":0.12191,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21132,"mean_force":0.08248,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.53339,0.08296,0.20173]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":9112.0,"contact_point_centroid":[0.5379,0.10026,0.20069],"force_p95":0.1211,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18612,"mean_force":0.08434,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.53247,0.08174,0.20156]},{"body_a":"world","body_b":"grasp_target","contact_count":1444.0,"contact_point_centroid":[0.60869,0.20291,-0.00197],"force_p95":0.13744,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.15726,"mean_force":0.12254,"phase_index":7.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.62022,0.20338,0.20203]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4091.0,"contact_point_centroid":[0.44986,-0.00563,0.04887],"force_p95":0.08034,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14987,"mean_force":0.05217,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44897,-0.02484,0.04799]},{"body_a":"world","body_b":"grasp_target","contact_count":280.0,"contact_point_centroid":[0.45856,-0.02632,-0.00155],"force_p95":0.13832,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12461,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48809,-0.00668,0.29472]},{"body_a":"world","body_b":"grasp_target","contact_count":1780.0,"contact_point_centroid":[0.45856,-0.02632,-0.00199],"force_p95":0.12264,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12264,"mean_force":0.12259,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.46512,-0.01999,0.17284]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4990.0,"contact_point_centroid":[0.44905,-0.04395,0.0491],"force_p95":0.07194,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07446,"mean_force":0.04402,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44897,-0.02484,0.04799]}],"total_contact_groups":16},"final_pose_error":0.0199,"key_states":{"actual_goal_position":[0.63013,0.20822,0.11412],"final_object_position":[0.60868,0.20292,0.02602],"final_tcp_position":[0.62602,0.20639,0.24473],"realised_goal_position":[0.63013,0.20822,0.11412],"realised_object_initial_position":[0.45856,-0.02632,0.03]},"peak_contact_force":1.19156,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":71.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02591],"object_pos_start":[0.45856,-0.02632,0.03],"object_to_goal_dist_end":0.30368,"object_to_goal_dist_start":0.30252,"object_z_max":0.03,"peak_contact_force":0.12273,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":280.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.47466,-0.01505,0.2889],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.26372,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":445.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.02591],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30368,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1780.0,"raw_peak_contact_force":0.12264,"subtask_id":"descend_1","tcp_end":[0.45666,-0.02509,0.05579],"tcp_start":[0.47466,-0.01505,0.2889],"tcp_to_object_dist_end":0.02986,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.45851,-0.02528,0.02555],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30301,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.15368,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10881.0,"raw_peak_contact_force":0.21331,"subtask_id":"grasp_1","tcp_end":[0.44894,-0.02484,0.04796],"tcp_start":[0.45666,-0.02509,0.05579],"tcp_to_object_dist_end":0.02437,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":433.0,"n_steps_budget":1000.0,"object_pos_end":[0.4688,-0.02555,0.16366],"object_pos_start":[0.45851,-0.02528,0.02555],"object_to_goal_dist_end":0.28832,"object_to_goal_dist_start":0.30301,"object_z_max":0.16338,"peak_contact_force":0.10587,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":14875.0,"raw_peak_contact_force":0.38461,"tcp_end":[0.45447,-0.02508,0.18969],"tcp_start":[0.44894,-0.02484,0.04796],"tcp_to_object_dist_end":0.02972,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":18.0,"n_steps":809.0,"n_steps_budget":1000.0,"object_pos_end":[0.6235,0.19514,0.1832],"object_pos_start":[0.4688,-0.02555,0.16366],"object_to_goal_dist_end":0.07062,"object_to_goal_dist_start":0.28832,"object_z_max":0.1832,"peak_contact_force":0.11548,"phase_name":"transport_arc","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":18494.0,"raw_peak_contact_force":0.21132,"subtask_id":"transport_arc","tcp_end":[0.61855,0.19564,0.21802],"tcp_start":[0.45447,-0.02508,0.18969],"tcp_to_object_dist_end":0.03518,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":18.0,"n_steps":135.0,"n_steps_budget":1000.0,"object_pos_end":[0.62658,0.20277,0.10554],"object_pos_start":[0.6235,0.19514,0.1832],"object_to_goal_dist_end":0.01076,"object_to_goal_dist_start":0.07062,"object_z_max":0.1832,"peak_contact_force":0.13422,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2522.0,"raw_peak_contact_force":0.26981,"tcp_end":[0.6235,0.20344,0.14216],"tcp_start":[0.61855,0.19564,0.21802],"tcp_to_object_dist_end":0.03675,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.60971,0.20255,0.02653],"object_pos_start":[0.62658,0.20277,0.10554],"object_to_goal_dist_end":0.09011,"object_to_goal_dist_start":0.01076,"object_z_max":0.10554,"peak_contact_force":0.14033,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1337.0,"raw_peak_contact_force":1.19156,"subtask_id":"release_1","tcp_end":[0.61659,0.20102,0.15996],"tcp_start":[0.6235,0.20344,0.14216],"tcp_to_object_dist_end":0.13361,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":361.0,"n_steps_budget":690.0,"object_pos_end":[0.60868,0.20292,0.02602],"object_pos_start":[0.60971,0.20255,0.02653],"object_to_goal_dist_end":0.09083,"object_to_goal_dist_start":0.09011,"object_z_max":0.02656,"peak_contact_force":0.12263,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1444.0,"raw_peak_contact_force":0.15726,"tcp_end":[0.62602,0.20639,0.24473],"tcp_start":[0.61659,0.20102,0.15996],"tcp_to_object_dist_end":0.21943,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```