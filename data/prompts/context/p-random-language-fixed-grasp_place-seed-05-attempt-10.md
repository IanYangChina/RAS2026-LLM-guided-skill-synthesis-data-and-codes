## Search State

- **Seed**: 5
- **Iteration**: 11 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 10 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | force_threshold_switch | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 8 | 0.2227 | 0.41 | ❌ rejected |
| 9 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | force_threshold_switch | position_control | position_control | position_control | force_threshold_switch | position_control | position_control | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 8 | 0.3481 | 0.42 | ❌ rejected |
| 8 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | force_threshold_switch | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 8 | 0.2235 | 0.42 | ❌ rejected |
| 7 | approach → descend → grasp → lift → approach → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | — | linear_cartesian | position_control | force_threshold_switch | position_control | position_control | position_control | position_control | position_control | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 6 | 0.3719 | 0.42 | ✅ accepted |
| 6 | approach → descend → grasp → lift → approach → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | — | linear_cartesian | position_control | force_threshold_switch | position_control | position_control | position_control | position_control | position_control | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 6 | -0.3167 | 0.22 | ✅ accepted |

**Proposal policy**: task_score is 0.41 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `ca83b0c5488ee900ee32f323a4fc38ffcc2f5381fd3d2b180044b561c962382d`
- Frozen object start: [0.530500292374538, 0.030794078973649372, 0.03]
- Frozen task target: [0.6015325561042142, 0.17858013800881417, 0.10808960535724847]
- Goal object position: (0.6015325561042142, 0.17858013800881417, 0.10808960535724847)
- place_goal_position (task success criterion — final object 3D position must be close to the realised airborne target here): (0.6015325561042142, 0.17858013800881417, 0.10808960535724847)
- Grasp/lift components are optimiser fitness diagnostics only; canonical task_score is final object-to-realised-target proximity.
- Object initial pose: (0.530500292374538, 0.030794078973649372, 0.03)
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
  frozen_object_start: [0.5305, 0.0308, 0.03]
  frozen_task_target: [0.6015, 0.1786, 0.1081]
  frozen_object_starts: {'grasp_target': [0.530500292374538, 0.030794078973649372, 0.03]}
  frozen_targets: {'place_target': [0.6015325561042142, 0.17858013800881417, 0.10808960535724847]}
  goal_tolerance_m: 0.02
  force_limit_n: 20
  force_scale_n: 5
  realized_scene_sha256: ca83b0c5488ee900ee32f323a4fc38ffcc2f5381fd3d2b180044b561c962382d

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

## Current Skill (Q=0.223) — your mutation base

```yaml
skill: grasp_place
dsl_version: 2
skill_type: arm_gripper
phases:
- id: approach
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
    - 0.0
    tolerance: 0.02
  parameters:
    approach_speed:
      type: scalar
      range:
      - 0.05
      - 0.3
      default: 0.15
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: approach_1
- id: descend
  type: descend
  generator: linear_cartesian
  control: force_threshold_switch
  termination: force_exceeded
  target:
    source: yaml
    anchor: task_object
    entity: grasp_target
    offset:
    - 0.0
    - 0.0
    - 0.0
  parameters:
    descend_force_threshold:
      type: scalar
      range:
      - 1.0
      - 10.0
      default: 5.0
      binds_to:
      - path: termination.force_threshold
        mode: replace
  subtask_id: descend_1
- id: grasp
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
  guards:
  - id: grasp_check
    when: during_phase
    predicate: bilateral_grasp
    threshold: 0.0
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.0
    - 0.0
    - -0.005
  subtask_id: grasp_1
- id: lift
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
    - 0.1
    tolerance: 0.02
  parameters:
    lift_height:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.1
      binds_to:
      - path: target.offset.z
        mode: replace
- id: transport
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
    - 0.05
    tolerance: 0.02
  parameters:
    arc_height:
      type: scalar
      range:
      - 0.02
      - 0.15
      default: 0.08
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
- id: release
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
- id: retract
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
    - 0.1
    tolerance: 0.02
  parameters:
    retract_speed:
      type: scalar
      range:
      - 0.05
      - 0.3
      default: 0.15
      binds_to:
      - path: generator.speed
        mode: replace

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach** (`approach`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.0], tolerance=0.02
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (replace)
- **descend** (`descend`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.0]
  - parameter_bindings:
    - descend_force_threshold: status=consumed; consumers=termination.force_threshold (replace)
- **grasp** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings: none
  - guards:
    - id=grasp_check, when=during_phase, predicate=bilateral_grasp, on_failure=retry, threshold=0.0
  - retries: max_attempts=2, strategy=offset_target, offset=[0.0, 0.0, -0.005]
- **lift** (`lift`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.1], tolerance=0.02
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset.z (replace)
- **transport** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.05], tolerance=0.02
  - parameter_bindings:
    - arc_height: status=consumed; consumers=generator.arc_height (replace)
    - transport_speed: status=consumed; consumers=generator.speed (replace)
- **release** (`release`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings: none
- **retract** (`retract`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.1], tolerance=0.02
  - parameter_bindings:
    - retract_speed: status=consumed; consumers=generator.speed (replace)

## Design Metrics

- **Composite score**: 0.223
- **task_score** (E): 0.414
- **fitness_score**: 0.678  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.125
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.580

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach | 1.00 | 1.00 | 0.2543 |
| descend | 1.00 | 1.00 | 0.0043 |
| grasp | 0.00 | 1.00 | 0.0000 |
| lift | 1.00 | 1.00 | 0.1445 |
| transport | 1.00 | 1.00 | 0.1889 |
| descend_to_goal | 1.00 | 1.00 | 0.0419 |
| release | 1.00 | 1.00 | 0.0207 |
| retract | 1.00 | 1.00 | 0.0445 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.510, 0.016, 0.048) | (0.516, 0.018, 0.030)→(0.516, 0.018, 0.026) | 0.234→0.236 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend | descend | 1.00 / force_exceeded | (0.510, 0.016, 0.048)→(0.508, 0.017, 0.045) | (0.516, 0.018, 0.026)→(0.516, 0.018, 0.026) | 0.236→0.236 | 1.00 / 4.000 | 81.142 | 0.123 |
| grasp | grasp | 0.00 / guard_failure | (0.503, 0.016, 0.039)→(0.503, 0.016, 0.039) | (0.516, 0.018, 0.026)→(0.516, 0.017, 0.025) | 0.236→0.237 | 1.00 / 43.000 | 0.180 | 0.249 |
| lift | lift | 1.00 / step_budget | (0.503, 0.016, 0.039)→(0.499, 0.016, 0.183) | (0.516, 0.017, 0.025)→(0.511, 0.017, 0.167) | 0.237→0.195 | 1.00 / 39.667 | 0.079 | 0.563 |
| transport | approach | 1.00 / step_budget | (0.499, 0.016, 0.183)→(0.596, 0.167, 0.226) | (0.511, 0.017, 0.167)→(0.600, 0.170, 0.205) | 0.195→0.040 | 1.00 / 40.333 | 0.077 | 0.238 |
| descend_to_goal | descend | 1.00 / step_budget | (0.596, 0.167, 0.226)→(0.599, 0.174, 0.185) | (0.600, 0.170, 0.205)→(0.603, 0.176, 0.163) | 0.040→0.006 | 1.00 / 41.000 | 0.078 | 0.337 |
| release | release | 1.00 / step_budget | (0.599, 0.174, 0.185)→(0.593, 0.172, 0.205) | (0.603, 0.176, 0.163)→(0.590, 0.171, 0.023) | 0.006→0.146 | 1.00 / 4.000 | 0.146 | 1.472 |
| retract | retract | 1.00 / step_budget | (0.593, 0.172, 0.205)→(0.600, 0.177, 0.248) | (0.590, 0.171, 0.023)→(0.587, 0.171, 0.026) | 0.146→0.143 | 1.00 / 4.000 | 0.123 | 0.153 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.569
- phase_score: 0.485
- phase_breakdown.approach_1_score: 0.675
- phase_breakdown.descend_1_score: 0.807
- phase_breakdown.transport_arc_score: 0.281
- phase_breakdown.grasp_1_score: 1.000
- phase_breakdown.release_1_score: 0.440
- grasp_place_fitness: 0.754

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.754
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.569
- **Median Q (composite search score)**: 0.239
- **K-run variance**: 0.0049
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.342


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `181fdad61feb8a6d3dd6561c82dc2730a5598964bf30fa08b43615687239c379`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.05,0.05],"goal_z_delta":0.15,"object_xy_delta":[0.05,0.05]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `eed1fc17ff57094d5189888f0dc8540ea7c165c4c73333e7487a550c7ded377e`; realized-scene SHA-256: `ca83b0c5488ee900ee32f323a4fc38ffcc2f5381fd3d2b180044b561c962382d`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.5305,0.03079,0.03]},{"name":"goal","value":[0.60153,0.17858,0.10809]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.5305,0.03079,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.60153,0.17858,0.10809]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.03937,"average_solve_count":127.0,"average_success_count":127.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach.approach_speed":0.16762,"descend.descend_force_threshold":6.21385,"descend_to_goal.descend_to_goal_speed":0.08054,"lift.lift_height":0.11939,"release.release_duration":0.48424,"retract.retract_speed":0.13073,"transport.arc_height":0.06989,"transport.transport_speed":0.18544},"optimized_scores":{"best_composite_score":0.29892,"best_fitness_score":0.75392,"best_task_score":0.5687},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":320.0,"contact_point_centroid":[0.58298,0.17014,-0.00404],"force_p95":0.78476,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.02867,"mean_force":0.2194,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.5874,0.17093,0.134]},{"body_a":"world","body_b":"grasp_target","contact_count":86.0,"contact_point_centroid":[0.52759,0.02731,-0.00157],"force_p95":0.49493,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.57352,"mean_force":0.11154,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.51518,0.02751,0.04019]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5488.0,"contact_point_centroid":[0.5133,0.0466,0.09059],"force_p95":0.08826,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.36908,"mean_force":0.06308,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.51269,0.02736,0.08787]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1193.0,"contact_point_centroid":[0.58852,0.19105,0.12515],"force_p95":0.08046,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.35008,"mean_force":0.04866,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.59169,0.17226,0.12081]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1602.0,"contact_point_centroid":[0.58907,0.1881,0.15238],"force_p95":0.09074,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.34403,"mean_force":0.05754,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.59222,0.16929,0.14833]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":7008.0,"contact_point_centroid":[0.51397,0.00841,0.08845],"force_p95":0.08127,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30928,"mean_force":0.05111,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.51271,0.02736,0.08652]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":10389.0,"contact_point_centroid":[0.54883,0.06868,0.18893],"force_p95":0.08899,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2853,"mean_force":0.05298,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.54527,0.08712,0.18766]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8994.0,"contact_point_centroid":[0.54331,0.10457,0.19061],"force_p95":0.10935,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27232,"mean_force":0.0627,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.54431,0.08551,0.18786]},{"body_a":"world","body_b":"grasp_target","contact_count":1804.0,"contact_point_centroid":[0.5307,0.0306,-0.00232],"force_p95":0.19545,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.26008,"mean_force":0.14508,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.51703,0.02764,0.03905]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1391.0,"contact_point_centroid":[0.59615,0.15355,0.12097],"force_p95":0.08229,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25849,"mean_force":0.04339,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.5917,0.17226,0.12083]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2004.0,"contact_point_centroid":[0.59681,0.15066,0.14894],"force_p95":0.08742,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24472,"mean_force":0.04823,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.59222,0.1693,0.14828]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6335.0,"contact_point_centroid":[0.51755,0.00864,0.04043],"force_p95":0.06896,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1547,"mean_force":0.04104,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.51653,0.02761,0.03847]},{"body_a":"world","body_b":"grasp_target","contact_count":752.0,"contact_point_centroid":[0.5826,0.17004,-0.00197],"force_p95":0.14113,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.14357,"mean_force":0.12273,"phase_index":7.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.59076,0.17341,0.16703]},{"body_a":"world","body_b":"grasp_target","contact_count":1828.0,"contact_point_centroid":[0.5305,0.03079,-0.00192],"force_p95":0.13358,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12289,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.51083,0.01361,0.17496]},{"body_a":"world","body_b":"grasp_target","contact_count":48.0,"contact_point_centroid":[0.5305,0.03079,-0.00199],"force_p95":0.12262,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12262,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend","phase_type":"descend","tcp_position_centroid":[0.52252,0.02787,0.04615]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4942.0,"contact_point_centroid":[0.51739,0.04704,0.04133],"force_p95":0.09226,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09515,"mean_force":0.05464,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.51654,0.02761,0.03849]}],"total_contact_groups":16},"final_pose_error":0.01983,"key_states":{"actual_goal_position":[0.60153,0.17858,0.10809],"final_object_position":[0.58259,0.17004,0.02602],"final_tcp_position":[0.5956,0.17619,0.18931],"realised_goal_position":[0.60153,0.17858,0.10809],"realised_object_initial_position":[0.5305,0.03079,0.03]},"peak_contact_force":81.14225,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":458.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.03],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18162,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1828.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.52351,0.02779,0.0481],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.02336,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":12.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":81.14225,"phase_name":"descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":48.0,"raw_peak_contact_force":0.12262,"subtask_id":"descend_1","tcp_end":[0.5218,0.02792,0.04448],"tcp_start":[0.52351,0.02779,0.0481],"tcp_to_object_dist_end":0.02061,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":42.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53059,0.02885,0.02507],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18532,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.18611,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":13081.0,"raw_peak_contact_force":0.26008,"subtask_id":"grasp_1","tcp_end":[0.51651,0.02761,0.03845],"tcp_start":[0.51651,0.02761,0.03845],"tcp_to_object_dist_end":0.01947,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":327.0,"n_steps_budget":750.0,"object_pos_end":[0.52574,0.02823,0.12243],"object_pos_start":[0.53061,0.02883,0.02512],"object_to_goal_dist_end":0.16898,"object_to_goal_dist_start":0.18531,"object_z_max":0.12216,"peak_contact_force":0.08457,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":12582.0,"raw_peak_contact_force":0.57352,"tcp_end":[0.51262,0.02736,0.13826],"tcp_start":[0.51651,0.02761,0.03845],"tcp_to_object_dist_end":0.02058,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":507.0,"n_steps_budget":1000.0,"object_pos_end":[0.59944,0.16898,0.14859],"object_pos_start":[0.52574,0.02823,0.12243],"object_to_goal_dist_end":0.04168,"object_to_goal_dist_start":0.16898,"object_z_max":0.19082,"peak_contact_force":0.08034,"phase_name":"transport","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":19383.0,"raw_peak_contact_force":0.2853,"subtask_id":"transport_arc","tcp_end":[0.5914,0.16609,0.16941],"tcp_start":[0.51262,0.02736,0.13826],"tcp_to_object_dist_end":0.02251,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":84.0,"n_steps_budget":1000.0,"object_pos_end":[0.60285,0.17621,0.10441],"object_pos_start":[0.59944,0.16898,0.14859],"object_to_goal_dist_end":0.00457,"object_to_goal_dist_start":0.04168,"object_z_max":0.14859,"peak_contact_force":0.08381,"phase_name":"descend_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3606.0,"raw_peak_contact_force":0.34403,"tcp_end":[0.59435,0.17286,0.12583],"tcp_start":[0.5914,0.16609,0.16941],"tcp_to_object_dist_end":0.02328,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.58266,0.17004,0.02651],"object_pos_start":[0.60285,0.17621,0.10441],"object_to_goal_dist_end":0.08417,"object_to_goal_dist_start":0.00457,"object_z_max":0.10441,"peak_contact_force":0.13802,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2904.0,"raw_peak_contact_force":1.02867,"subtask_id":"release_1","tcp_end":[0.58727,0.17089,0.14576],"tcp_start":[0.59435,0.17286,0.12583],"tcp_to_object_dist_end":0.11934,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":188.0,"n_steps_budget":600.0,"object_pos_end":[0.58259,0.17004,0.02602],"object_pos_start":[0.58266,0.17004,0.02651],"object_to_goal_dist_end":0.08466,"object_to_goal_dist_start":0.08417,"object_z_max":0.02651,"peak_contact_force":0.12281,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":752.0,"raw_peak_contact_force":0.14357,"tcp_end":[0.5956,0.17619,0.18931],"tcp_start":[0.58727,0.17089,0.14576],"tcp_to_object_dist_end":0.16393,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `5dcdc1a4e2a8d4c3bb30f9ac92fb306bea0b16a8f449f4d02b0333754e50f910`; realized-scene SHA-256: `584133b5261cffac0dd4282704ff39e97bf4d452e60b02507679bbdea5a4de22`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50382,-0.01567,0.03]},{"name":"goal","value":[0.58691,0.18745,0.24812]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.50382,-0.01567,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.58691,0.18745,0.24812]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.86301,"average_solve_count":146.0,"average_success_count":146.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach.approach_speed":0.28604,"descend.descend_force_threshold":2.60291,"descend_to_goal.descend_to_goal_speed":0.09765,"lift.lift_height":0.18252,"release.release_duration":0.47776,"retract.retract_speed":0.18657,"transport.arc_height":0.05553,"transport.transport_speed":0.12689},"optimized_scores":{"best_composite_score":0.12971,"best_fitness_score":0.58471,"best_task_score":0.22606},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":149.0,"contact_point_centroid":[0.56971,0.17597,-0.00966],"force_p95":1.35667,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.08558,"mean_force":0.52157,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.57633,0.17793,0.27959]},{"body_a":"world","body_b":"grasp_target","contact_count":77.0,"contact_point_centroid":[0.50043,-0.0143,-0.00141],"force_p95":0.47286,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.5433,"mean_force":0.1249,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.4908,-0.01435,0.04072]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1344.0,"contact_point_centroid":[0.57289,0.19298,0.28478],"force_p95":0.08678,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.35273,"mean_force":0.05571,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.57846,0.17471,0.28188]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":9941.0,"contact_point_centroid":[0.48765,-0.0335,0.12493],"force_p95":0.07654,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31652,"mean_force":0.05467,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.48836,-0.01432,0.12259]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":10957.0,"contact_point_centroid":[0.48888,0.00476,0.11982],"force_p95":0.07397,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30977,"mean_force":0.05047,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.48835,-0.01432,0.11803]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1053.0,"contact_point_centroid":[0.57449,0.19758,0.26301],"force_p95":0.08473,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25619,"mean_force":0.05254,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.57894,0.17893,0.26036]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1496.0,"contact_point_centroid":[0.58266,0.15584,0.28359],"force_p95":0.0782,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22684,"mean_force":0.04963,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.57841,0.17459,0.28236]},{"body_a":"world","body_b":"grasp_target","contact_count":1804.0,"contact_point_centroid":[0.50387,-0.01565,-0.00213],"force_p95":0.154,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.21101,"mean_force":0.13215,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.49251,-0.01436,0.03981]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1334.0,"contact_point_centroid":[0.58328,0.16021,0.26136],"force_p95":0.06951,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20507,"mean_force":0.04188,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.57895,0.17894,0.26038]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":13975.0,"contact_point_centroid":[0.52713,0.04527,0.27707],"force_p95":0.07644,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20295,"mean_force":0.05084,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.52499,0.06423,0.27509]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":13254.0,"contact_point_centroid":[0.52244,0.08138,0.27712],"force_p95":0.0778,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18149,"mean_force":0.05286,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.5241,0.06242,0.27455]},{"body_a":"world","body_b":"grasp_target","contact_count":712.0,"contact_point_centroid":[0.56974,0.17602,-0.00217],"force_p95":0.14703,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.18006,"mean_force":0.11268,"phase_index":7.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.57929,0.18141,0.30643]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6387.0,"contact_point_centroid":[0.49234,0.00473,0.04082],"force_p95":0.0653,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13999,"mean_force":0.04128,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.49202,-0.01435,0.03928]},{"body_a":"world","body_b":"grasp_target","contact_count":1636.0,"contact_point_centroid":[0.50382,-0.01567,-0.00192],"force_p95":0.13462,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12292,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.49897,-0.00695,0.1756]},{"body_a":"world","body_b":"grasp_target","contact_count":60.0,"contact_point_centroid":[0.50382,-0.01567,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend","phase_type":"descend","tcp_position_centroid":[0.49788,-0.01432,0.04665]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5374.0,"contact_point_centroid":[0.49131,-0.03364,0.04191],"force_p95":0.07676,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07967,"mean_force":0.04939,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.49202,-0.01435,0.03929]}],"total_contact_groups":16},"final_pose_error":0.01979,"key_states":{"actual_goal_position":[0.58691,0.18745,0.24812],"final_object_position":[0.56985,0.17604,0.02602],"final_tcp_position":[0.58305,0.185,0.32886],"realised_goal_position":[0.58691,0.18745,0.24812],"realised_object_initial_position":[0.50382,-0.01567,0.03]},"peak_contact_force":81.14225,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":410.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.03],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.30942,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1636.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.49907,-0.01423,0.04891],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.02342,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":15.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":81.14225,"phase_name":"descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":60.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.49715,-0.01438,0.04481],"tcp_start":[0.49907,-0.01423,0.04891],"tcp_to_object_dist_end":0.01998,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50376,-0.01499,0.02561],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31209,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.15108,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":13565.0,"raw_peak_contact_force":0.21101,"subtask_id":"grasp_1","tcp_end":[0.492,-0.01435,0.03926],"tcp_start":[0.492,-0.01435,0.03926],"tcp_to_object_dist_end":0.01803,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":518.0,"n_steps_budget":1000.0,"object_pos_end":[0.49964,-0.01468,0.18583],"object_pos_start":[0.50377,-0.01499,0.02563],"object_to_goal_dist_end":0.22881,"object_to_goal_dist_start":0.31208,"object_z_max":0.18555,"peak_contact_force":0.06985,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":20975.0,"raw_peak_contact_force":0.5433,"tcp_end":[0.48876,-0.01431,0.20226],"tcp_start":[0.492,-0.01435,0.03926],"tcp_to_object_dist_end":0.01971,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":690.0,"n_steps_budget":1000.0,"object_pos_end":[0.58089,0.17231,0.27574],"object_pos_start":[0.49964,-0.01468,0.18583],"object_to_goal_dist_end":0.03207,"object_to_goal_dist_start":0.22881,"object_z_max":0.28681,"peak_contact_force":0.06889,"phase_name":"transport","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":27229.0,"raw_peak_contact_force":0.20295,"subtask_id":"transport_arc","tcp_end":[0.57692,0.17034,0.29694],"tcp_start":[0.48876,-0.01431,0.20226],"tcp_to_object_dist_end":0.02166,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":68.0,"n_steps_budget":1000.0,"object_pos_end":[0.58477,0.18155,0.24318],"object_pos_start":[0.58089,0.17231,0.27574],"object_to_goal_dist_end":0.00799,"object_to_goal_dist_start":0.03207,"object_z_max":0.27574,"peak_contact_force":0.06792,"phase_name":"descend_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2840.0,"raw_peak_contact_force":0.35273,"tcp_end":[0.58063,0.17925,0.26509],"tcp_start":[0.57692,0.17034,0.29694],"tcp_to_object_dist_end":0.02241,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.57678,0.17739,0.0155],"object_pos_start":[0.58477,0.18155,0.24318],"object_to_goal_dist_end":0.23306,"object_to_goal_dist_start":0.00799,"object_z_max":0.24318,"peak_contact_force":0.192,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2536.0,"raw_peak_contact_force":2.08558,"subtask_id":"release_1","tcp_end":[0.5763,0.17792,0.28539],"tcp_start":[0.58063,0.17925,0.26509],"tcp_to_object_dist_end":0.26989,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":178.0,"n_steps_budget":600.0,"object_pos_end":[0.56985,0.17604,0.02602],"object_pos_start":[0.57678,0.17739,0.0155],"object_to_goal_dist_end":0.22304,"object_to_goal_dist_start":0.23306,"object_z_max":0.02696,"peak_contact_force":0.12408,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":712.0,"raw_peak_contact_force":0.18006,"tcp_end":[0.58305,0.185,0.32886],"tcp_start":[0.5763,0.17792,0.28539],"tcp_to_object_dist_end":0.30326,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `53da4dc33bcb1151bde99c46f4ec5d44dda63d23acc62ec623c12d4d0fb32574`; realized-scene SHA-256: `8a4edc50bf1a337961423afe5cdf858aa28147f944f8fcd30a2ce1adc75d1bd6`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.51251,0.03972,0.03]},{"name":"goal","value":[0.62757,0.17252,0.14502]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.51251,0.03972,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.62757,0.17252,0.14502]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.95808,"average_solve_count":167.0,"average_success_count":167.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach.approach_speed":0.13413,"descend.descend_force_threshold":5.39904,"descend_to_goal.descend_to_goal_speed":0.17527,"lift.lift_height":0.19033,"release.release_duration":0.56244,"retract.retract_speed":0.06488,"transport.arc_height":0.08396,"transport.transport_speed":0.11083},"optimized_scores":{"best_composite_score":0.23938,"best_fitness_score":0.69438,"best_task_score":0.44786},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":271.0,"contact_point_centroid":[0.6096,0.16702,-0.00532],"force_p95":0.83707,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.30155,"mean_force":0.25712,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.61501,0.1674,0.17244]},{"body_a":"world","body_b":"grasp_target","contact_count":87.0,"contact_point_centroid":[0.50952,0.03581,-0.00166],"force_p95":0.46882,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.57114,"mean_force":0.11738,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.49887,0.03558,0.0407]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":9277.0,"contact_point_centroid":[0.49636,0.05462,0.12592],"force_p95":0.08755,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.35883,"mean_force":0.06147,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.49653,0.03541,0.12333]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1462.0,"contact_point_centroid":[0.61607,0.18609,0.19091],"force_p95":0.09805,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31342,"mean_force":0.06308,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.61969,0.1674,0.18836]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":11816.0,"contact_point_centroid":[0.49767,0.01645,0.12457],"force_p95":0.07937,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29756,"mean_force":0.04956,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.49654,0.03541,0.12295]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1050.0,"contact_point_centroid":[0.61539,0.18734,0.16069],"force_p95":0.08267,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2961,"mean_force":0.05237,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.61893,0.16858,0.15823]},{"body_a":"world","body_b":"grasp_target","contact_count":1804.0,"contact_point_centroid":[0.51277,0.03946,-0.00241],"force_p95":0.21343,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.27459,"mean_force":0.15086,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.5007,0.03574,0.03944]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1234.0,"contact_point_centroid":[0.62321,0.14998,0.15769],"force_p95":0.07444,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27213,"mean_force":0.04604,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.61894,0.16858,0.15823]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1720.0,"contact_point_centroid":[0.62395,0.14884,0.1881],"force_p95":0.09364,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2583,"mean_force":0.05563,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.61969,0.1674,0.18836]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":12350.0,"contact_point_centroid":[0.55342,0.07478,0.25584],"force_p95":0.08114,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22583,"mean_force":0.05159,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.55072,0.09373,0.25422]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":11377.0,"contact_point_centroid":[0.55042,0.11516,0.25839],"force_p95":0.08294,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20105,"mean_force":0.05454,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.5532,0.09633,0.25547]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6311.0,"contact_point_centroid":[0.50115,0.01672,0.04026],"force_p95":0.07265,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17984,"mean_force":0.04119,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.5002,0.0357,0.03889]},{"body_a":"world","body_b":"grasp_target","contact_count":1888.0,"contact_point_centroid":[0.51251,0.03972,-0.00193],"force_p95":0.13354,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12288,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.50269,0.01759,0.17489]},{"body_a":"world","body_b":"grasp_target","contact_count":772.0,"contact_point_centroid":[0.60956,0.16698,-0.00195],"force_p95":0.12947,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13514,"mean_force":0.12173,"phase_index":7.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.61802,0.16892,0.20367]},{"body_a":"world","body_b":"grasp_target","contact_count":56.0,"contact_point_centroid":[0.51251,0.03972,-0.00199],"force_p95":0.12262,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12262,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend","phase_type":"descend","tcp_position_centroid":[0.50609,0.03598,0.04632]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4987.0,"contact_point_centroid":[0.50031,0.05518,0.04118],"force_p95":0.0928,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09909,"mean_force":0.05485,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.50021,0.0357,0.0389]}],"total_contact_groups":16},"final_pose_error":0.01979,"key_states":{"actual_goal_position":[0.62757,0.17252,0.14502],"final_object_position":[0.60955,0.16698,0.02602],"final_tcp_position":[0.62235,0.17075,0.22601],"realised_goal_position":[0.62757,0.17252,0.14502],"realised_object_initial_position":[0.51251,0.03972,0.03]},"peak_contact_force":81.14225,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":473.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.03],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21001,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1888.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.50718,0.03587,0.04843],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.02335,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":14.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":81.14225,"phase_name":"descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":56.0,"raw_peak_contact_force":0.12262,"subtask_id":"descend_1","tcp_end":[0.50537,0.03607,0.04458],"tcp_start":[0.50718,0.03587,0.04843],"tcp_to_object_dist_end":0.02022,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51268,0.03723,0.02481],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21437,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.20205,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":13102.0,"raw_peak_contact_force":0.27459,"subtask_id":"grasp_1","tcp_end":[0.50018,0.0357,0.03887],"tcp_start":[0.50018,0.0357,0.03887],"tcp_to_object_dist_end":0.01887,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":39.0,"n_steps":548.0,"n_steps_budget":1000.0,"object_pos_end":[0.50826,0.03653,0.19222],"object_pos_start":[0.5127,0.03717,0.02488],"object_to_goal_dist_end":0.18696,"object_to_goal_dist_start":0.21436,"object_z_max":0.19194,"peak_contact_force":0.08372,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":21180.0,"raw_peak_contact_force":0.57114,"tcp_end":[0.49699,0.03544,0.20949],"tcp_start":[0.50018,0.0357,0.03887],"tcp_to_object_dist_end":0.02065,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":600.0,"n_steps_budget":1000.0,"object_pos_end":[0.62027,0.16766,0.18919],"object_pos_start":[0.50826,0.03653,0.19222],"object_to_goal_dist_end":0.04502,"object_to_goal_dist_start":0.18696,"object_z_max":0.25871,"peak_contact_force":0.08056,"phase_name":"transport","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":23727.0,"raw_peak_contact_force":0.22583,"subtask_id":"transport_arc","tcp_end":[0.61913,0.16593,0.21166],"tcp_start":[0.49699,0.03544,0.20949],"tcp_to_object_dist_end":0.02258,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":86.0,"n_steps_budget":1000.0,"object_pos_end":[0.62268,0.17127,0.14074],"object_pos_start":[0.62027,0.16766,0.18919],"object_to_goal_dist_end":0.00662,"object_to_goal_dist_start":0.04502,"object_z_max":0.18919,"peak_contact_force":0.0831,"phase_name":"descend_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3182.0,"raw_peak_contact_force":0.31342,"tcp_end":[0.62141,0.16921,0.16375],"tcp_start":[0.61913,0.16593,0.21166],"tcp_to_object_dist_end":0.02314,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.61008,0.16685,0.02629],"object_pos_start":[0.62268,0.17127,0.14074],"object_to_goal_dist_end":0.12015,"object_to_goal_dist_start":0.00662,"object_z_max":0.14074,"peak_contact_force":0.10914,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2555.0,"raw_peak_contact_force":1.30155,"subtask_id":"release_1","tcp_end":[0.61493,0.16738,0.18254],"tcp_start":[0.62141,0.16921,0.16375],"tcp_to_object_dist_end":0.15633,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":193.0,"n_steps_budget":630.0,"object_pos_end":[0.60955,0.16698,0.02602],"object_pos_start":[0.61008,0.16685,0.02629],"object_to_goal_dist_end":0.12049,"object_to_goal_dist_start":0.12015,"object_z_max":0.02654,"peak_contact_force":0.12272,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":772.0,"raw_peak_contact_force":0.13514,"tcp_end":[0.62235,0.17075,0.22601],"tcp_start":[0.61493,0.16738,0.18254],"tcp_to_object_dist_end":0.20044,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```