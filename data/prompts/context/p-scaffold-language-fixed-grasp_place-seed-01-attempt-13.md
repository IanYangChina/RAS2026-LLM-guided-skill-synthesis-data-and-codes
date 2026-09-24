## Search State

- **Seed**: 1
- **Iteration**: 14 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 13 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | admittance_control | position_control | position_control | position_control | admittance_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 4 | 0.2262 | 0.29 | ❌ rejected |
| 12 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | admittance_control | position_control | position_control | position_control | admittance_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 4 | 0.2658 | 0.37 | ❌ rejected |
| 11 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | admittance_control | position_control | position_control | position_control | admittance_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 6 | -0.1066 | 0.18 | ❌ rejected |
| 10 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | admittance_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 5 | 0.2160 | 0.37 | ❌ rejected |
| 9 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | admittance_control | position_control | position_control | impedance_control | admittance_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 6 | 0.2929 | 0.38 | ❌ rejected |

**Proposal policy**: task_score is 0.29 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.226) — your mutation base

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

- **Composite score**: 0.226
- **task_score** (E): 0.292
- **fitness_score**: 0.606  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.380

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.0757 |
| descend_1 | 1.00 | 1.00 | 0.1843 |
| grasp_1 | 1.00 | 1.00 | 0.0116 |
| lift_1 | 1.00 | 1.00 | 0.1190 |
| transport_arc | 1.00 | 1.00 | 0.2371 |
| descend_2 | 1.00 | 1.00 | 0.0395 |
| release_1 | 1.00 | 1.00 | 0.0200 |
| retract_1 | 1.00 | 1.00 | 0.0858 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.485, 0.003, 0.241) | (0.479, -0.000, 0.030)→(0.479, -0.000, 0.026) | 0.276→0.278 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.485, 0.003, 0.241)→(0.476, -0.000, 0.057) | (0.479, -0.000, 0.026)→(0.479, -0.000, 0.026) | 0.278→0.278 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_1 | grasp | 1.00 / step_budget | (0.476, -0.000, 0.057)→(0.468, -0.000, 0.049) | (0.479, -0.000, 0.026)→(0.479, -0.000, 0.026) | 0.278→0.278 | 1.00 / 37.667 | 0.157 | 0.216 |
| lift_1 | lift | 1.00 / step_budget | (0.468, -0.000, 0.049)→(0.474, -0.000, 0.168) | (0.479, -0.000, 0.026)→(0.487, -0.000, 0.140) | 0.278→0.247 | 1.00 / 22.667 | 0.114 | 0.368 |
| transport_arc | approach | 1.00 / step_budget | (0.474, -0.000, 0.168)→(0.597, 0.190, 0.215) | (0.487, -0.000, 0.140)→(0.546, 0.094, 0.016) | 0.247→0.187 | 1.00 / 8.000 | 91004.381 | 1.772 |
| descend_2 | descend | 1.00 / step_budget | (0.597, 0.190, 0.215)→(0.601, 0.197, 0.177) | (0.546, 0.094, 0.016)→(0.546, 0.094, 0.016) | 0.187→0.187 | 1.00 / 8.667 | 182007.982 | 0.123 |
| release_1 | release | 1.00 / step_budget | (0.601, 0.197, 0.177)→(0.595, 0.195, 0.196) | (0.546, 0.094, 0.016)→(0.546, 0.094, 0.016) | 0.187→0.187 | 1.00 / 4.000 | 0.123 | 0.123 |
| retract_1 | retract | 1.00 / step_budget | (0.595, 0.195, 0.196)→(0.605, 0.202, 0.281) | (0.546, 0.094, 0.016)→(0.546, 0.094, 0.016) | 0.187→0.187 | 1.00 / 4.000 | 0.123 | 0.123 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: 1.000
- terminal_score: 0.332
- phase_score: 0.447
- phase_breakdown.descend_1_score: 0.854
- phase_breakdown.transport_arc_score: 0.276
- phase_breakdown.grasp_1_score: 1.000
- phase_breakdown.release_1_score: 0.368
- phase_breakdown.approach_1_score: 0.094
- grasp_place_fitness: 0.627

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.627
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.332
- **Median Q (composite search score)**: 0.238
- **K-run variance**: 0.0005
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.517


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.80682,"average_solve_count":176.0,"average_success_count":176.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.09945,"descend_1.grasp_z_offset":0.01134,"lift_1.lift_height":0.15548,"transport_arc.transport_arc_height":0.06733},"optimized_scores":{"best_composite_score":0.24725,"best_fitness_score":0.62725,"best_task_score":0.33187},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":1055.0,"contact_point_centroid":[0.54065,0.14624,-0.00292],"force_p95":0.46869,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.66424,"mean_force":0.16808,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.54092,0.18287,0.208]},{"body_a":"world","body_b":"grasp_target","contact_count":82.0,"contact_point_centroid":[0.49918,0.04205,-0.00151],"force_p95":0.3521,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.39917,"mean_force":0.07683,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.4877,0.04245,0.04887]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6061.0,"contact_point_centroid":[0.49278,0.06151,0.09898],"force_p95":0.11021,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29298,"mean_force":0.06787,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49036,0.04258,0.09791]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2483.0,"contact_point_centroid":[0.51011,0.05363,0.17574],"force_p95":0.16593,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26766,"mean_force":0.09128,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.50377,0.07215,0.17597]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5664.0,"contact_point_centroid":[0.49231,0.02366,0.09837],"force_p95":0.11136,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26738,"mean_force":0.06993,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49034,0.04258,0.09766]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50126,0.04491,-0.0022],"force_p95":0.17788,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.23736,"mean_force":0.13701,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.48984,0.04267,0.04841]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2609.0,"contact_point_centroid":[0.51091,0.09331,0.17672],"force_p95":0.13904,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19532,"mean_force":0.0883,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.50467,0.07492,0.17727]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4145.0,"contact_point_centroid":[0.48905,0.0234,0.04867],"force_p95":0.08001,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14261,"mean_force":0.05143,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.48875,0.04257,0.04723]},{"body_a":"world","body_b":"grasp_target","contact_count":1188.0,"contact_point_centroid":[0.50118,0.04505,-0.00189],"force_p95":0.13631,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12304,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.4984,0.01855,0.22498]},{"body_a":"world","body_b":"grasp_target","contact_count":704.0,"contact_point_centroid":[0.50118,0.04505,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49666,0.04076,0.10272]},{"body_a":"world","body_b":"grasp_target","contact_count":292.0,"contact_point_centroid":[0.54068,0.14631,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.55702,0.23193,0.19253]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.54068,0.14631,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.55413,0.2347,0.17407]},{"body_a":"world","body_b":"grasp_target","contact_count":1276.0,"contact_point_centroid":[0.54068,0.14631,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":7.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.55583,0.23792,0.23541]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4881.0,"contact_point_centroid":[0.48936,0.0618,0.04858],"force_p95":0.07918,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08086,"mean_force":0.04553,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.48876,0.04257,0.04724]},{"body_a":"left_finger","body_b":"right_finger","contact_count":894.0,"contact_point_centroid":[0.54441,0.1921,0.21124],"force_p95":0.01313,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01613,"mean_force":0.01071,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.54406,0.19207,0.20891]},{"body_a":"left_finger","body_b":"right_finger","contact_count":218.0,"contact_point_centroid":[0.55692,0.23592,0.1716],"force_p95":0.01099,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01273,"mean_force":0.01021,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.55648,0.23589,0.16945]}],"total_contact_groups":17},"final_pose_error":0.01977,"key_states":{"actual_goal_position":[0.56442,0.24486,0.14677],"final_object_position":[0.54068,0.14631,0.01602],"final_tcp_position":[0.5608,0.24247,0.27749],"realised_goal_position":[0.56442,0.24486,0.14677],"realised_object_initial_position":[0.50118,0.04505,0.03]},"peak_contact_force":273014.28525,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":298.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.03],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.23992,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1188.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.49796,0.03843,0.14801],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.12221,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":176.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"peak_contact_force":0.12262,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":704.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.4969,0.04327,0.05639],"tcp_start":[0.49796,0.03843,0.14801],"tcp_to_object_dist_end":0.03072,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50118,0.04342,0.02529],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.24359,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"peak_contact_force":0.17214,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10826.0,"raw_peak_contact_force":0.23736,"subtask_id":"grasp_1","tcp_end":[0.48872,0.04256,0.0472],"tcp_start":[0.4969,0.04327,0.05639],"tcp_to_object_dist_end":0.02522,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":26.0,"n_steps":371.0,"n_steps_budget":840.0,"object_pos_end":[0.51056,0.04371,0.13542],"object_pos_start":[0.50118,0.04342,0.02529],"object_to_goal_dist_end":0.20854,"object_to_goal_dist_start":0.24359,"object_z_max":0.13516,"peak_contact_force":0.10219,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":11807.0,"raw_peak_contact_force":0.39917,"tcp_end":[0.49632,0.04299,0.16159],"tcp_start":[0.48872,0.04256,0.0472],"tcp_to_object_dist_end":0.02981,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":590.0,"n_steps_budget":1000.0,"object_pos_end":[0.54068,0.14631,0.01602],"object_pos_start":[0.51056,0.04371,0.13542],"object_to_goal_dist_end":0.16545,"object_to_goal_dist_start":0.20854,"object_z_max":0.16251,"peak_contact_force":0.12263,"phase_name":"transport_arc","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":7041.0,"raw_peak_contact_force":1.66424,"subtask_id":"transport_arc","tcp_end":[0.5562,0.22779,0.20824],"tcp_start":[0.49632,0.04299,0.16159],"tcp_to_object_dist_end":0.20935,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":73.0,"n_steps_budget":1000.0,"object_pos_end":[0.54068,0.14631,0.01602],"object_pos_start":[0.54068,0.14631,0.01602],"object_to_goal_dist_end":0.16545,"object_to_goal_dist_start":0.16545,"object_z_max":0.01602,"peak_contact_force":273014.28525,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":605.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.55849,0.23645,0.17379],"tcp_start":[0.5562,0.22779,0.20824],"tcp_to_object_dist_end":0.18258,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54068,0.14631,0.01602],"object_pos_start":[0.54068,0.14631,0.01602],"object_to_goal_dist_end":0.16545,"object_to_goal_dist_start":0.16545,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1018.0,"raw_peak_contact_force":0.12263,"subtask_id":"release_1","tcp_end":[0.5527,0.23398,0.19413],"tcp_start":[0.55849,0.23645,0.17379],"tcp_to_object_dist_end":0.19889,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":319.0,"n_steps_budget":660.0,"object_pos_end":[0.54068,0.14631,0.01602],"object_pos_start":[0.54068,0.14631,0.01602],"object_to_goal_dist_end":0.16545,"object_to_goal_dist_start":0.16545,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1276.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.5608,0.24247,0.27749],"tcp_start":[0.5527,0.23398,0.19413],"tcp_to_object_dist_end":0.27932,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.72589,"average_solve_count":197.0,"average_success_count":197.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.29573,"descend_1.grasp_z_offset":0.01033,"lift_1.lift_height":0.13918,"transport_arc.transport_arc_height":0.05185},"optimized_scores":{"best_composite_score":0.19365,"best_fitness_score":0.57365,"best_task_score":0.22205},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":1673.0,"contact_point_centroid":[0.54314,0.04538,-0.00263],"force_p95":0.26019,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.83281,"mean_force":0.15502,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.57274,0.09666,0.22251]},{"body_a":"world","body_b":"grasp_target","contact_count":74.0,"contact_point_centroid":[0.47427,-0.01877,-0.00143],"force_p95":0.3371,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.38421,"mean_force":0.07831,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46449,-0.01906,0.04888]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5373.0,"contact_point_centroid":[0.46782,1e-05,0.0951],"force_p95":0.10025,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27588,"mean_force":0.06234,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46666,-0.0191,0.09411]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6015.0,"contact_point_centroid":[0.46755,-0.03812,0.09497],"force_p95":0.09336,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27188,"mean_force":0.05694,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46665,-0.0191,0.09389]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2978.0,"contact_point_centroid":[0.49587,-0.01374,0.16809],"force_p95":0.13379,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26317,"mean_force":0.08337,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.49002,0.00468,0.16776]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2572.0,"contact_point_centroid":[0.49463,0.02179,0.16699],"force_p95":0.15554,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25277,"mean_force":0.09199,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.48867,0.00313,0.16636]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.47618,-0.02006,-0.00209],"force_p95":0.14876,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.20099,"mean_force":0.12956,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46654,-0.0191,0.04859]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4098.0,"contact_point_centroid":[0.46639,0.00013,0.04865],"force_p95":0.0794,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14418,"mean_force":0.05214,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46548,-0.01908,0.04752]},{"body_a":"world","body_b":"grasp_target","contact_count":252.0,"contact_point_centroid":[0.47616,-0.02015,-0.00149],"force_p95":0.13832,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12478,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49251,-0.00491,0.3043]},{"body_a":"world","body_b":"grasp_target","contact_count":1936.0,"contact_point_centroid":[0.47616,-0.02015,-0.00199],"force_p95":0.12264,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12353,"mean_force":0.1226,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.47872,-0.01509,0.18418]},{"body_a":"world","body_b":"grasp_target","contact_count":168.0,"contact_point_centroid":[0.54323,0.04561,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.62008,0.14923,0.22597]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.54323,0.04561,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.61832,0.15079,0.21472]},{"body_a":"world","body_b":"grasp_target","contact_count":1412.0,"contact_point_centroid":[0.54323,0.04561,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":7.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.6218,0.15389,0.27693]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4950.0,"contact_point_centroid":[0.46557,-0.03817,0.04877],"force_p95":0.0705,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07282,"mean_force":0.04422,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46548,-0.01908,0.04753]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1592.0,"contact_point_centroid":[0.57821,0.10253,0.22702],"force_p95":0.01218,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01634,"mean_force":0.01054,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.57807,0.10253,0.22474]},{"body_a":"left_finger","body_b":"right_finger","contact_count":181.0,"contact_point_centroid":[0.62017,0.14926,0.22823],"force_p95":0.01098,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.011,"mean_force":0.01038,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.62009,0.14926,0.22589]}],"total_contact_groups":17},"final_pose_error":0.01996,"key_states":{"actual_goal_position":[0.63142,0.15919,0.19002],"final_object_position":[0.54323,0.04561,0.01602],"final_tcp_position":[0.62813,0.15764,0.32039],"realised_goal_position":[0.63142,0.15919,0.19002],"realised_object_initial_position":[0.47616,-0.02015,0.03]},"peak_contact_force":273012.8983,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":64.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02588],"object_pos_start":[0.47616,-0.02015,0.03],"object_to_goal_dist_end":0.28846,"object_to_goal_dist_start":0.28614,"object_z_max":0.03,"peak_contact_force":0.12371,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":252.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.48495,-0.01108,0.31045],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.28485,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":484.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.02588],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28846,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1936.0,"raw_peak_contact_force":0.12353,"subtask_id":"descend_1","tcp_end":[0.47339,-0.01924,0.05587],"tcp_start":[0.48495,-0.01108,0.31045],"tcp_to_object_dist_end":0.03,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.4761,-0.01936,0.02566],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28812,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.1461,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10848.0,"raw_peak_contact_force":0.20099,"subtask_id":"grasp_1","tcp_end":[0.46545,-0.01908,0.04749],"tcp_start":[0.47339,-0.01924,0.05587],"tcp_to_object_dist_end":0.02429,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":25.0,"n_steps":308.0,"n_steps_budget":750.0,"object_pos_end":[0.48584,-0.0195,0.12139],"object_pos_start":[0.4761,-0.01936,0.02566],"object_to_goal_dist_end":0.24049,"object_to_goal_dist_start":0.28812,"object_z_max":0.12112,"peak_contact_force":0.10499,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":11462.0,"raw_peak_contact_force":0.38421,"tcp_end":[0.47124,-0.01921,0.14562],"tcp_start":[0.46545,-0.01908,0.04749],"tcp_to_object_dist_end":0.02828,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":759.0,"n_steps_budget":1000.0,"object_pos_end":[0.54323,0.04561,0.01602],"object_pos_start":[0.48584,-0.0195,0.12139],"object_to_goal_dist_end":0.22573,"object_to_goal_dist_start":0.24049,"object_z_max":0.15928,"peak_contact_force":273012.8983,"phase_name":"transport_arc","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":8815.0,"raw_peak_contact_force":1.83281,"subtask_id":"transport_arc","tcp_end":[0.61853,0.1471,0.23306],"tcp_start":[0.47124,-0.01921,0.14562],"tcp_to_object_dist_end":0.25115,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":42.0,"n_steps_budget":1000.0,"object_pos_end":[0.54323,0.04561,0.01602],"object_pos_start":[0.54323,0.04561,0.01602],"object_to_goal_dist_end":0.22573,"object_to_goal_dist_start":0.22573,"object_z_max":0.01602,"peak_contact_force":273009.53735,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":349.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.62239,0.15176,0.21572],"tcp_start":[0.61853,0.1471,0.23306],"tcp_to_object_dist_end":0.23962,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54323,0.04561,0.01602],"object_pos_start":[0.54323,0.04561,0.01602],"object_to_goal_dist_end":0.22573,"object_to_goal_dist_start":0.22573,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1022.0,"raw_peak_contact_force":0.12263,"subtask_id":"release_1","tcp_end":[0.61702,0.15036,0.23427],"tcp_start":[0.62239,0.15176,0.21572],"tcp_to_object_dist_end":0.25308,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":353.0,"n_steps_budget":690.0,"object_pos_end":[0.54323,0.04561,0.01602],"object_pos_start":[0.54323,0.04561,0.01602],"object_to_goal_dist_end":0.22573,"object_to_goal_dist_start":0.22573,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1412.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.62813,0.15764,0.32039],"tcp_start":[0.61702,0.15036,0.23427],"tcp_to_object_dist_end":0.33526,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.92157,"average_solve_count":204.0,"average_success_count":204.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.22322,"descend_1.grasp_z_offset":0.01421,"lift_1.lift_height":0.19,"transport_arc.transport_arc_height":0.09397},"optimized_scores":{"best_composite_score":0.2378,"best_fitness_score":0.6178,"best_task_score":0.32145},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":1495.0,"contact_point_centroid":[0.5546,0.09123,-0.00268],"force_p95":0.34182,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.81757,"mean_force":0.15774,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.57553,0.13865,0.21901]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5446.0,"contact_point_centroid":[0.4511,-0.04338,0.11567],"force_p95":0.13673,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32175,"mean_force":0.08329,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44976,-0.02495,0.11772]},{"body_a":"world","body_b":"grasp_target","contact_count":76.0,"contact_point_centroid":[0.45673,-0.02435,-0.00143],"force_p95":0.2906,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.31492,"mean_force":0.06417,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44786,-0.02489,0.05367]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4454.0,"contact_point_centroid":[0.45171,-0.00648,0.11574],"force_p95":0.14212,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29575,"mean_force":0.09842,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44979,-0.02495,0.11857]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2633.0,"contact_point_centroid":[0.48646,-0.00527,0.20539],"force_p95":0.14773,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29406,"mean_force":0.10391,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.4809,0.01277,0.20862]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2502.0,"contact_point_centroid":[0.49139,0.03731,0.20732],"force_p95":0.14028,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2666,"mean_force":0.10709,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.48564,0.01924,0.21059]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.45859,-0.02621,-0.00212],"force_p95":0.15643,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.20902,"mean_force":0.13147,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44993,-0.02497,0.05314]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2653.0,"contact_point_centroid":[0.44955,-0.00607,0.04958],"force_p95":0.1024,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1443,"mean_force":0.0762,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44891,-0.02493,0.05215]},{"body_a":"world","body_b":"grasp_target","contact_count":384.0,"contact_point_centroid":[0.45856,-0.02632,-0.00168],"force_p95":0.13822,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12396,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48633,-0.00788,0.28366]},{"body_a":"world","body_b":"grasp_target","contact_count":1572.0,"contact_point_centroid":[0.45856,-0.02632,-0.00199],"force_p95":0.12264,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12264,"mean_force":0.12261,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.46316,-0.02115,0.1628]},{"body_a":"world","body_b":"grasp_target","contact_count":464.0,"contact_point_centroid":[0.55473,0.09129,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.6194,0.19789,0.17446]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.55473,0.09129,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.61769,0.20083,0.13986]},{"body_a":"world","body_b":"grasp_target","contact_count":1448.0,"contact_point_centroid":[0.55473,0.09129,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":7.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.61988,0.20292,0.20163]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4014.0,"contact_point_centroid":[0.44958,-0.04376,0.05107],"force_p95":0.0918,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09485,"mean_force":0.05297,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44892,-0.02493,0.05215]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1377.0,"contact_point_centroid":[0.58172,0.1466,0.22034],"force_p95":0.01226,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01655,"mean_force":0.01063,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.58154,0.1466,0.21804]},{"body_a":"left_finger","body_b":"right_finger","contact_count":490.0,"contact_point_centroid":[0.61965,0.19789,0.17673],"force_p95":0.01098,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01101,"mean_force":0.01053,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.61939,0.19788,0.17454]}],"total_contact_groups":17},"final_pose_error":0.01997,"key_states":{"actual_goal_position":[0.63013,0.20822,0.11412],"final_object_position":[0.55473,0.09129,0.01602],"final_tcp_position":[0.62596,0.2063,0.24469],"realised_goal_position":[0.63013,0.20822,0.11412],"realised_object_initial_position":[0.45856,-0.02632,0.03]},"peak_contact_force":1.81757,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":97.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02601],"object_pos_start":[0.45856,-0.02632,0.03],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30252,"object_z_max":0.03,"peak_contact_force":0.12218,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":384.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.47121,-0.01725,0.26542],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.23992,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":393.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.02601],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.12262,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1572.0,"raw_peak_contact_force":0.12264,"subtask_id":"descend_1","tcp_end":[0.45653,-0.02518,0.05993],"tcp_start":[0.47121,-0.01725,0.26542],"tcp_to_object_dist_end":0.034,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":31.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.45851,-0.02533,0.02555],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30305,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.1516,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":8467.0,"raw_peak_contact_force":0.20902,"subtask_id":"grasp_1","tcp_end":[0.44888,-0.02493,0.05212],"tcp_start":[0.45653,-0.02518,0.05993],"tcp_to_object_dist_end":0.02826,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":17.0,"n_steps":439.0,"n_steps_budget":1000.0,"object_pos_end":[0.46373,-0.02547,0.16366],"object_pos_start":[0.45851,-0.02533,0.02555],"object_to_goal_dist_end":0.29112,"object_to_goal_dist_start":0.30305,"object_z_max":0.16338,"peak_contact_force":0.13403,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":9976.0,"raw_peak_contact_force":0.32175,"tcp_end":[0.45451,-0.02514,0.196],"tcp_start":[0.44888,-0.02493,0.05212],"tcp_to_object_dist_end":0.03363,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":772.0,"n_steps_budget":1000.0,"object_pos_end":[0.55473,0.09129,0.01602],"object_pos_start":[0.46373,-0.02547,0.16366],"object_to_goal_dist_end":0.17024,"object_to_goal_dist_start":0.29112,"object_z_max":0.18482,"peak_contact_force":0.12263,"phase_name":"transport_arc","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":8007.0,"raw_peak_contact_force":1.81757,"subtask_id":"transport_arc","tcp_end":[0.61703,0.19363,0.20502],"tcp_start":[0.45451,-0.02514,0.196],"tcp_to_object_dist_end":0.22378,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":116.0,"n_steps_budget":1000.0,"object_pos_end":[0.55473,0.09129,0.01602],"object_pos_start":[0.55473,0.09129,0.01602],"object_to_goal_dist_end":0.17024,"object_to_goal_dist_start":0.17024,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":954.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.62285,0.20254,0.14134],"tcp_start":[0.61703,0.19363,0.20502],"tcp_to_object_dist_end":0.18089,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.55473,0.09129,0.01602],"object_pos_start":[0.55473,0.09129,0.01602],"object_to_goal_dist_end":0.17024,"object_to_goal_dist_start":0.17024,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1027.0,"raw_peak_contact_force":0.12263,"subtask_id":"release_1","tcp_end":[0.61597,0.20016,0.1593],"tcp_start":[0.62285,0.20254,0.14134],"tcp_to_object_dist_end":0.19009,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":362.0,"n_steps_budget":690.0,"object_pos_end":[0.55473,0.09129,0.01602],"object_pos_start":[0.55473,0.09129,0.01602],"object_to_goal_dist_end":0.17024,"object_to_goal_dist_start":0.17024,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1448.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.62596,0.2063,0.24469],"tcp_start":[0.61597,0.20016,0.1593],"tcp_to_object_dist_end":0.26569,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```