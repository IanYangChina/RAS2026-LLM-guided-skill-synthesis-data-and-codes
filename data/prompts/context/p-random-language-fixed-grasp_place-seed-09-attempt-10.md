## Search State

- **Seed**: 9
- **Iteration**: 11 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 10 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | position_control | position_control | position_control | impedance_control | impedance_control | impedance_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 8 | 0.2587 | 0.63 | ❌ rejected |
| 9 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | position_control | position_control | position_control | impedance_control | impedance_control | impedance_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 8 | 0.3059 | 0.72 | ✅ accepted |
| 8 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | position_control | impedance_control | impedance_control | impedance_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 9 | 0.0458 | 0.36 | ❌ rejected |
| 7 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | position_control | position_control | position_control | impedance_control | impedance_control | impedance_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 8 | 0.0338 | 0.21 | ❌ rejected |
| 6 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | position_control | impedance_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 9 | 0.0520 | 0.39 | ❌ rejected |

**Proposal policy**: task_score is 0.63 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.259) — your mutation base

```yaml
skill: grasp_place
dsl_version: 2
skill_type: arm_gripper
subtasks:
- id: approach_1
  anchor: object
- id: descend_1
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.02
- id: grasp_1
  anchor: object
  metric: contact
  offset:
  - 0.0
  - 0.0
  - 0.02
- id: transport_arc
- id: release_1
phases:
- id: approach_to_object
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
    - 0.12
    orientation:
      mode: keep_current
  parameters:
    speed:
      type: scalar
      range:
      - 0.02
      - 0.15
      default: 0.08
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: approach_1
- id: descend_to_grasp
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
    - 0.02
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    speed:
      type: scalar
      range:
      - 0.01
      - 0.08
      default: 0.04
      binds_to:
      - path: generator.speed
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
  parameters:
    grip_force:
      type: scalar
      range:
      - 5.0
      - 30.0
      default: 20.0
      binds_to:
      - path: guards.grasp_check.threshold
        mode: replace
  guards:
  - id: grasp_check
    when: after_phase
    predicate: bilateral_grasp
    threshold: 0.5
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.0
    - 0.0
    - 0.005
  subtask_id: grasp_1
- id: lift_object
  type: lift
  generator: linear_cartesian
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.0
    - 0.15
    tolerance: 0.015
    orientation:
      mode: keep_current
  parameters:
    lift_height:
      type: scalar
      range:
      - 0.12
      - 0.3
      default: 0.2
      binds_to:
      - path: target.offset.z
        mode: replace
    speed:
      type: scalar
      range:
      - 0.02
      - 0.12
      default: 0.06
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: lift_check
    when: after_phase
    predicate: object_lifted
    threshold: 0.05
    on_failure: retry
  retries:
    max_attempts: 1
    strategy: offset_target
    offset:
    - 0.0
    - 0.0
    - 0.01
- id: transport_to_goal
  type: approach
  generator: arc_cartesian
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.12
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    arc_height:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.12
      binds_to:
      - path: generator.arc_height
        mode: replace
    speed:
      type: scalar
      range:
      - 0.02
      - 0.15
      default: 0.08
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: transport_retain
    when: after_phase
    predicate: object_lifted
    threshold: 0.05
    on_failure: retry
  retries:
    max_attempts: 1
    strategy: reduce_speed
  subtask_id: transport_arc
- id: descend_to_place
  type: descend
  generator: linear_cartesian
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.0
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    speed:
      type: scalar
      range:
      - 0.01
      - 0.08
      default: 0.04
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: release_1

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_to_object** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.12]
  - orientation: mode=keep_current
  - parameter_bindings:
    - speed: status=consumed; consumers=generator.speed (replace)
- **descend_to_grasp** (`descend`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.02], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - speed: status=consumed; consumers=generator.speed (replace)
- **grasp** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings:
    - grip_force: status=consumed; consumers=guards.grasp_check.threshold (replace)
  - guards:
    - id=grasp_check, when=after_phase, predicate=bilateral_grasp, on_failure=retry, threshold=0.5
  - retries: max_attempts=2, strategy=offset_target, offset=[0.0, 0.0, 0.005]
- **lift_object** (`lift`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.15], tolerance=0.015
  - orientation: mode=keep_current
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset.z (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=lift_check, when=after_phase, predicate=object_lifted, on_failure=retry, threshold=0.05
  - retries: max_attempts=1, strategy=offset_target, offset=[0.0, 0.0, 0.01]
- **transport_to_goal** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.12], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - arc_height: status=consumed; consumers=generator.arc_height (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=transport_retain, when=after_phase, predicate=object_lifted, on_failure=retry, threshold=0.05
  - retries: max_attempts=1, strategy=reduce_speed
- **descend_to_place** (`descend`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - speed: status=consumed; consumers=generator.speed (replace)

## Design Metrics

- **Composite score**: 0.259
- **task_score** (E): 0.630
- **fitness_score**: 0.779  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.520

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_to_object | 1.00 | 1.00 | 0.1488 |
| descend_to_grasp | 1.00 | 1.00 | 0.1033 |
| grasp | 1.00 | 1.00 | 0.0123 |
| lift_object | 1.00 | 1.00 | 0.1538 |
| transport_to_goal | 1.00 | 1.00 | 0.1440 |
| descend_to_place | 1.00 | 1.00 | 0.1162 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_to_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.510, -0.015, 0.158) | (0.515, -0.017, 0.030)→(0.515, -0.017, 0.026) | 0.268→0.270 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_to_grasp | descend | 1.00 / step_budget | (0.510, -0.015, 0.158)→(0.510, -0.017, 0.054) | (0.515, -0.017, 0.026)→(0.515, -0.017, 0.026) | 0.270→0.270 | 1.00 / 4.000 | 18.182 | 0.123 |
| grasp | grasp | 1.00 / step_budget | (0.510, -0.017, 0.054)→(0.502, -0.017, 0.045) | (0.515, -0.017, 0.026)→(0.515, -0.017, 0.026) | 0.270→0.270 | 1.00 / 41.667 | 0.134 | 0.168 |
| lift_object | lift | 1.00 / step_budget | (0.502, -0.017, 0.045)→(0.510, -0.016, 0.199) | (0.515, -0.017, 0.026)→(0.515, -0.016, 0.173) | 0.270→0.229 | 1.00 / 38.667 | 0.077 | 0.370 |
| transport_to_goal | approach | 1.00 / step_budget | (0.534, 0.060, 0.238)→(0.608, 0.167, 0.292) | (0.515, -0.016, 0.173)→(0.605, 0.134, 0.169) | 0.229→0.139 | 1.00 / 17.667 | 18.954 | 0.828 |
| descend_to_place | descend | 1.00 / step_budget | (0.608, 0.167, 0.292)→(0.613, 0.179, 0.177) | (0.605, 0.134, 0.169)→(0.605, 0.142, 0.087) | 0.139→0.093 | 1.00 / 17.667 | 0.112 | 0.357 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.839
- phase_score: 0.406
- phase_breakdown.descend_1_score: 0.869
- phase_breakdown.grasp_1_score: 1.000
- phase_breakdown.transport_arc_score: 0.076
- phase_breakdown.approach_1_score: 0.080
- phase_breakdown.release_1_score: 0.823
- grasp_place_fitness: 0.884

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.884
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.839
- **Median Q (composite search score)**: 0.356
- **K-run variance**: 0.0206
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.344


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.0457,"average_solve_count":372.0,"average_success_count":372.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_to_object.speed":0.07562,"descend_to_grasp.speed":0.03795,"descend_to_place.speed":0.02672,"grasp.grip_force":7.79161,"lift_object.lift_height":0.22183,"lift_object.speed":0.02905,"transport_to_goal.arc_height":0.07783,"transport_to_goal.speed":0.11467},"optimized_scores":{"best_composite_score":0.05593,"best_fitness_score":0.57593,"best_task_score":0.22307},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":1300.0,"contact_point_centroid":[0.58134,0.11299,-0.00315],"force_p95":0.50899,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.14599,"mean_force":0.17117,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.58566,0.15381,0.34139]},{"body_a":"world","body_b":"grasp_target","contact_count":124.0,"contact_point_centroid":[0.53333,-0.02061,-0.00135],"force_p95":0.35427,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.382,"mean_force":0.11029,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.52184,-0.0208,0.04532]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5910.0,"contact_point_centroid":[0.54198,0.02522,0.26651],"force_p95":0.11639,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27151,"mean_force":0.07439,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.53784,0.0064,0.26627]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":19307.0,"contact_point_centroid":[0.52532,-0.00162,0.12662],"force_p95":0.07641,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25554,"mean_force":0.05283,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.52493,-0.02073,0.12439]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":19727.0,"contact_point_centroid":[0.52573,-0.03984,0.12971],"force_p95":0.07474,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24206,"mean_force":0.05182,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.52519,-0.02073,0.12776]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6309.0,"contact_point_centroid":[0.54114,-0.01387,0.26441],"force_p95":0.11667,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23934,"mean_force":0.06959,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.53735,0.00487,0.26418]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53703,-0.02121,-0.00205],"force_p95":0.13646,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.16891,"mean_force":0.12665,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.52427,-0.02085,0.04563]},{"body_a":"world","body_b":"grasp_target","contact_count":1972.0,"contact_point_centroid":[0.53702,-0.02132,-0.00193],"force_p95":0.13308,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12287,"phase_index":0.0,"phase_name":"approach_to_object","phase_type":"approach","tcp_position_centroid":[0.5137,-0.00953,0.22787]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4325.0,"contact_point_centroid":[0.52375,-0.00162,0.04709],"force_p95":0.07656,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12873,"mean_force":0.0494,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.52307,-0.02082,0.04423]},{"body_a":"world","body_b":"grasp_target","contact_count":1380.0,"contact_point_centroid":[0.53702,-0.02132,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.52927,-0.02016,0.10502]},{"body_a":"world","body_b":"grasp_target","contact_count":1256.0,"contact_point_centroid":[0.58127,0.11299,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.60425,0.21751,0.27059]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4898.0,"contact_point_centroid":[0.5239,-0.03995,0.04603],"force_p95":0.0694,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08696,"mean_force":0.04478,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.52307,-0.02082,0.04423]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1276.0,"contact_point_centroid":[0.58738,0.15801,0.34369],"force_p95":0.01233,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01635,"mean_force":0.01072,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.58701,0.158,0.34139]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1342.0,"contact_point_centroid":[0.60476,0.21749,0.27326],"force_p95":0.011,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01275,"mean_force":0.01044,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.60423,0.21747,0.27097]}],"total_contact_groups":14},"final_pose_error":0.00977,"key_states":{"actual_goal_position":[0.61031,0.22775,0.20741],"final_object_position":[0.58127,0.11299,0.01602],"final_tcp_position":[0.60634,0.22418,0.21559],"realised_goal_position":[0.61031,0.22775,0.20741],"realised_object_initial_position":[0.53702,-0.02132,0.03]},"peak_contact_force":9748.82792,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":494.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.03],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31446,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_to_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1972.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.53003,-0.01943,0.15666],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.13084,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":345.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1380.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.53141,-0.02098,0.05409],"tcp_start":[0.53003,-0.01943,0.15666],"tcp_to_object_dist_end":0.02863,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53694,-0.0208,0.02581],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31645,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.1343,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11023.0,"raw_peak_contact_force":0.16891,"subtask_id":"grasp_1","tcp_end":[0.52304,-0.02082,0.04419],"tcp_start":[0.53141,-0.02098,0.05409],"tcp_to_object_dist_end":0.02304,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":38.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53671,-0.02069,0.18659],"object_pos_start":[0.53694,-0.0208,0.02581],"object_to_goal_dist_end":0.25995,"object_to_goal_dist_start":0.31645,"object_z_max":0.18642,"peak_contact_force":0.07718,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":39158.0,"raw_peak_contact_force":0.382,"tcp_end":[0.53147,-0.02073,0.21167],"tcp_start":[0.52304,-0.02082,0.04419],"tcp_to_object_dist_end":0.02562,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":898.0,"n_steps_budget":1000.0,"object_pos_end":[0.58127,0.11299,0.01602],"object_pos_start":[0.53671,-0.02069,0.18659],"object_to_goal_dist_end":0.22504,"object_to_goal_dist_start":0.25995,"object_z_max":0.29437,"peak_contact_force":0.12262,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":14795.0,"raw_peak_contact_force":2.14599,"subtask_id":"transport_arc","tcp_end":[0.60357,0.21199,0.32503],"tcp_start":[0.60334,0.20913,0.32829],"tcp_to_object_dist_end":0.32525,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":314.0,"n_steps_budget":1000.0,"object_pos_end":[0.58127,0.11299,0.01602],"object_pos_start":[0.58127,0.11299,0.01602],"object_to_goal_dist_end":0.22504,"object_to_goal_dist_start":0.22504,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2598.0,"raw_peak_contact_force":0.12263,"subtask_id":"release_1","tcp_end":[0.60634,0.22418,0.21559],"tcp_start":[0.60357,0.21199,0.32503],"tcp_to_object_dist_end":0.22983,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.16374,"average_solve_count":342.0,"average_success_count":342.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_to_object.speed":0.09926,"descend_to_grasp.speed":0.04691,"descend_to_place.speed":0.0741,"grasp.grip_force":22.97582,"lift_object.lift_height":0.22565,"lift_object.speed":0.02762,"transport_to_goal.arc_height":0.14826,"transport_to_goal.speed":0.02291},"optimized_scores":{"best_composite_score":0.36394,"best_fitness_score":0.88394,"best_task_score":0.83862},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"right_finger","body_b":"grasp_target","contact_count":3603.0,"contact_point_centroid":[0.62678,0.17352,0.24038],"force_p95":0.1425,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.44918,"mean_force":0.09191,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.62518,0.15519,0.24327]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3836.0,"contact_point_centroid":[0.62676,0.13669,0.24035],"force_p95":0.1498,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.42869,"mean_force":0.09115,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.62521,0.15525,0.24283]},{"body_a":"world","body_b":"grasp_target","contact_count":127.0,"contact_point_centroid":[0.54187,-0.02829,-0.00136],"force_p95":0.35317,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.38364,"mean_force":0.10599,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.53014,-0.02845,0.04491]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":18718.0,"contact_point_centroid":[0.53396,-0.00924,0.12724],"force_p95":0.07761,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25544,"mean_force":0.05413,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.5333,-0.02838,0.12504]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":20126.0,"contact_point_centroid":[0.53403,-0.04746,0.12716],"force_p95":0.07443,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24715,"mean_force":0.05096,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.53331,-0.02838,0.12509]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.54562,-0.0291,-0.00207],"force_p95":0.14199,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.18411,"mean_force":0.12793,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.53263,-0.02853,0.04523]},{"body_a":"world","body_b":"grasp_target","contact_count":2012.0,"contact_point_centroid":[0.5456,-0.02923,-0.00193],"force_p95":0.13256,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12287,"phase_index":0.0,"phase_name":"approach_to_object","phase_type":"approach","tcp_position_centroid":[0.51778,-0.01315,0.22736]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":13728.0,"contact_point_centroid":[0.56464,0.04187,0.29008],"force_p95":0.09925,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1358,"mean_force":0.06472,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.56224,0.02289,0.29005]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4104.0,"contact_point_centroid":[0.53231,-0.00929,0.04651],"force_p95":0.0781,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13402,"mean_force":0.05186,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.53141,-0.0285,0.04378]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":15716.0,"contact_point_centroid":[0.56454,0.00464,0.2916],"force_p95":0.08737,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13366,"mean_force":0.05691,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.56253,0.02348,0.2915]},{"body_a":"world","body_b":"grasp_target","contact_count":1356.0,"contact_point_centroid":[0.5456,-0.02923,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.53753,-0.02768,0.10457]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4915.0,"contact_point_centroid":[0.53231,-0.04759,0.04556],"force_p95":0.07027,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0775,"mean_force":0.04465,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.53141,-0.0285,0.04378]}],"total_contact_groups":12},"final_pose_error":0.00975,"key_states":{"actual_goal_position":[0.63284,0.16493,0.17692],"final_object_position":[0.62488,0.16098,0.15206],"final_tcp_position":[0.62816,0.16178,0.18487],"realised_goal_position":[0.63284,0.16493,0.17692],"realised_object_initial_position":[0.5456,-0.02923,0.03]},"peak_contact_force":26.64309,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":504.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.03],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.25864,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_to_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2012.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.5381,-0.02672,0.15609],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.13031,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":339.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":26.64309,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1356.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.53985,-0.02875,0.05396],"tcp_start":[0.5381,-0.02672,0.15609],"tcp_to_object_dist_end":0.02853,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54552,-0.02855,0.02575],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.2606,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.13865,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10819.0,"raw_peak_contact_force":0.18411,"subtask_id":"grasp_1","tcp_end":[0.53138,-0.02849,0.04374],"tcp_start":[0.53985,-0.02875,0.05396],"tcp_to_object_dist_end":0.02288,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":38.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.54492,-0.02844,0.18237],"object_pos_start":[0.54552,-0.02855,0.02575],"object_to_goal_dist_end":0.21249,"object_to_goal_dist_start":0.2606,"object_z_max":0.18222,"peak_contact_force":0.07577,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":38971.0,"raw_peak_contact_force":0.38364,"tcp_end":[0.53945,-0.02842,0.20716],"tcp_start":[0.53138,-0.02849,0.04374],"tcp_to_object_dist_end":0.02539,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":26.0,"n_steps":907.0,"n_steps_budget":1000.0,"object_pos_end":[0.63059,0.1486,0.2745],"object_pos_start":[0.54492,-0.02844,0.18237],"object_to_goal_dist_end":0.09896,"object_to_goal_dist_start":0.21249,"object_z_max":0.30873,"peak_contact_force":0.09722,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":29444.0,"raw_peak_contact_force":0.1358,"subtask_id":"transport_arc","tcp_end":[0.62382,0.14914,0.30433],"tcp_start":[0.53945,-0.02842,0.20716],"tcp_to_object_dist_end":0.0306,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":27.0,"n_steps":314.0,"n_steps_budget":1000.0,"object_pos_end":[0.62488,0.16098,0.15206],"object_pos_start":[0.63059,0.1486,0.2745],"object_to_goal_dist_end":0.0264,"object_to_goal_dist_start":0.09896,"object_z_max":0.2745,"peak_contact_force":0.09112,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":7439.0,"raw_peak_contact_force":0.44918,"subtask_id":"release_1","tcp_end":[0.62816,0.16178,0.18487],"tcp_start":[0.62382,0.14914,0.30433],"tcp_to_object_dist_end":0.03298,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.77363,"average_solve_count":402.0,"average_success_count":402.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_to_object.speed":0.13105,"descend_to_grasp.speed":0.04286,"descend_to_place.speed":0.02051,"grasp.grip_force":20.06546,"lift_object.lift_height":0.16576,"lift_object.speed":0.02547,"transport_to_goal.arc_height":0.18763,"transport_to_goal.speed":0.05235},"optimized_scores":{"best_composite_score":0.35623,"best_fitness_score":0.87623,"best_task_score":0.82772},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"right_finger","body_b":"grasp_target","contact_count":3236.0,"contact_point_centroid":[0.60335,0.16265,0.18772],"force_p95":0.13265,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.50047,"mean_force":0.10522,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.59836,0.14445,0.19072]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3213.0,"contact_point_centroid":[0.6035,0.12669,0.18306],"force_p95":0.12736,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.43089,"mean_force":0.10168,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.59871,0.14481,0.1865]},{"body_a":"world","body_b":"grasp_target","contact_count":114.0,"contact_point_centroid":[0.45931,-0.00047,-0.00138],"force_p95":0.30032,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.34512,"mean_force":0.11523,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.45018,-0.00021,0.04845]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":14058.0,"contact_point_centroid":[0.4531,0.01878,0.11403],"force_p95":0.0743,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23189,"mean_force":0.05088,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.45315,-0.00021,0.11295]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":11871.0,"contact_point_centroid":[0.45231,-0.01938,0.11359],"force_p95":0.08495,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22333,"mean_force":0.05888,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.45312,-0.00021,0.11243]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":11705.0,"contact_point_centroid":[0.50775,0.06783,0.2395],"force_p95":0.09943,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20107,"mean_force":0.06296,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.5052,0.04915,0.23976]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":11123.0,"contact_point_centroid":[0.5042,0.02784,0.23815],"force_p95":0.12777,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18085,"mean_force":0.06759,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.50276,0.04671,0.23891]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.46285,-8e-05,-0.00202],"force_p95":0.12955,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.15222,"mean_force":0.12446,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.45227,-0.00018,0.04853]},{"body_a":"world","body_b":"grasp_target","contact_count":1632.0,"contact_point_centroid":[0.46286,-7e-05,-0.00192],"force_p95":0.13462,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12293,"phase_index":0.0,"phase_name":"approach_to_object","phase_type":"approach","tcp_position_centroid":[0.48121,-5e-05,0.23059]},{"body_a":"world","body_b":"grasp_target","contact_count":1488.0,"contact_point_centroid":[0.46286,-7e-05,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.45951,-0.0001,0.10706]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4870.0,"contact_point_centroid":[0.45112,0.01897,0.0491],"force_p95":0.06673,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08171,"mean_force":0.04473,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.4512,-0.00019,0.04749]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4616.0,"contact_point_centroid":[0.45061,-0.01938,0.04847],"force_p95":0.06878,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08049,"mean_force":0.04714,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.4512,-0.00019,0.04749]}],"total_contact_groups":12},"final_pose_error":0.00995,"key_states":{"actual_goal_position":[0.61015,0.15287,0.12219],"final_object_position":[0.60913,0.15054,0.09394],"final_tcp_position":[0.60408,0.15013,0.12958],"realised_goal_position":[0.61015,0.15287,0.12219],"realised_object_initial_position":[0.46286,-7e-05,0.03]},"peak_contact_force":56.64214,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":409.0,"n_steps_budget":1000.0,"object_pos_end":[0.46286,-7e-05,0.02602],"object_pos_start":[0.46286,-7e-05,0.03],"object_to_goal_dist_end":0.2331,"object_to_goal_dist_start":0.23148,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_to_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1632.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.46299,-8e-05,0.15977],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.13375,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":372.0,"n_steps_budget":1000.0,"object_pos_end":[0.46286,-7e-05,0.02602],"object_pos_start":[0.46286,-7e-05,0.02602],"object_to_goal_dist_end":0.2331,"object_to_goal_dist_start":0.2331,"object_z_max":0.02602,"peak_contact_force":27.7797,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1488.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.45865,-0.00011,0.05485],"tcp_start":[0.46299,-8e-05,0.15977],"tcp_to_object_dist_end":0.02914,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.46277,-0.00017,0.02591],"object_pos_start":[0.46286,-7e-05,0.02602],"object_to_goal_dist_end":0.23326,"object_to_goal_dist_start":0.2331,"object_z_max":0.02602,"peak_contact_force":0.12962,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11286.0,"raw_peak_contact_force":0.15222,"subtask_id":"grasp_1","tcp_end":[0.45117,-0.00019,0.04746],"tcp_start":[0.45865,-0.00011,0.05485],"tcp_to_object_dist_end":0.02447,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":689.0,"n_steps_budget":1000.0,"object_pos_end":[0.46336,-0.00013,0.15133],"object_pos_start":[0.46277,-0.00017,0.02591],"object_to_goal_dist_end":0.21402,"object_to_goal_dist_start":0.23326,"object_z_max":0.15116,"peak_contact_force":0.07714,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":26043.0,"raw_peak_contact_force":0.34512,"tcp_end":[0.45849,-0.0002,0.17733],"tcp_start":[0.45117,-0.00019,0.04746],"tcp_to_object_dist_end":0.02645,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":19.0,"n_steps":750.0,"n_steps_budget":1000.0,"object_pos_end":[0.6023,0.14098,0.21523],"object_pos_start":[0.46336,-0.00013,0.15133],"object_to_goal_dist_end":0.09412,"object_to_goal_dist_start":0.21402,"object_z_max":0.2424,"peak_contact_force":56.64214,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":22828.0,"raw_peak_contact_force":0.20107,"subtask_id":"transport_arc","tcp_end":[0.59583,0.14017,0.24697],"tcp_start":[0.45849,-0.0002,0.17733],"tcp_to_object_dist_end":0.03241,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":18.0,"n_steps":368.0,"n_steps_budget":1000.0,"object_pos_end":[0.60913,0.15054,0.09394],"object_pos_start":[0.6023,0.14098,0.21523],"object_to_goal_dist_end":0.02836,"object_to_goal_dist_start":0.09412,"object_z_max":0.21523,"peak_contact_force":0.12207,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":6449.0,"raw_peak_contact_force":0.50047,"subtask_id":"release_1","tcp_end":[0.60408,0.15013,0.12958],"tcp_start":[0.59583,0.14017,0.24697],"tcp_to_object_dist_end":0.036,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```