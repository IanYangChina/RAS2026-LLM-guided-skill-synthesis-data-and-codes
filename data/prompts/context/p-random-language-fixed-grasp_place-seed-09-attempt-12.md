## Search State

- **Seed**: 9
- **Iteration**: 13 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 12 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | impedance_control | impedance_control | impedance_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 10 | -0.0359 | 0.36 | ❌ rejected |
| 11 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | position_control | position_control | position_control | impedance_control | impedance_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 8 | 0.2955 | 0.70 | ❌ rejected |
| 10 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | position_control | position_control | position_control | impedance_control | impedance_control | impedance_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 8 | 0.2587 | 0.63 | ❌ rejected |
| 9 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | position_control | position_control | position_control | impedance_control | impedance_control | impedance_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 8 | 0.3059 | 0.72 | ✅ accepted |
| 8 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | position_control | impedance_control | impedance_control | impedance_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 9 | 0.0458 | 0.36 | ❌ rejected |

**Proposal policy**: task_score is 0.36 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=-0.036) — your mutation base

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

- **Composite score**: -0.036
- **task_score** (E): 0.361
- **fitness_score**: 0.644  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.680

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_to_object | 1.00 | 1.00 | 0.1488 |
| descend_to_grasp | 1.00 | 1.00 | 0.1032 |
| grasp | 1.00 | 1.00 | 0.0123 |
| lift_object | 0.33 | 1.00 | 0.1769 |
| transport_to_goal | 1.00 | 0.67 | 0.1404 |
| descend_to_place | 1.00 | 1.00 | 0.0992 |
| release_object | 1.00 | 1.00 | 0.0201 |
| retract_after_place | 1.00 | 1.00 | 0.0343 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_to_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.510, -0.015, 0.158) | (0.515, -0.017, 0.030)→(0.515, -0.017, 0.026) | 0.268→0.270 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_to_grasp | descend | 1.00 / step_budget | (0.510, -0.015, 0.158)→(0.510, -0.017, 0.054) | (0.515, -0.017, 0.026)→(0.515, -0.017, 0.026) | 0.270→0.270 | 1.00 / 4.000 | 10.292 | 0.123 |
| grasp | grasp | 1.00 / step_budget | (0.510, -0.017, 0.054)→(0.502, -0.017, 0.045) | (0.515, -0.017, 0.026)→(0.515, -0.016, 0.026) | 0.270→0.270 | 1.00 / 42.000 | 0.134 | 0.168 |
| lift_object | lift | 0.33 / step_budget | (0.502, -0.017, 0.045)→(0.509, -0.016, 0.222) | (0.515, -0.016, 0.026)→(0.513, -0.016, 0.196) | 0.270→0.235 | 1.00 / 38.000 | 0.078 | 0.399 |
| transport_to_goal | approach | 1.00 / step_budget | (0.533, 0.059, 0.263)→(0.608, 0.167, 0.295) | (0.513, -0.016, 0.196)→(0.606, 0.118, 0.113) | 0.235→0.140 | 0.67 / 8.333 | 3249.760 | 1.088 |
| descend_to_place | descend | 1.00 / step_budget | (0.608, 0.167, 0.295)→(0.613, 0.178, 0.197) | (0.606, 0.118, 0.113)→(0.609, 0.128, 0.052) | 0.140→0.134 | 1.00 / 11.667 | 94251.813 | 0.837 |
| release_object | release | 1.00 / step_budget | (0.613, 0.178, 0.197)→(0.608, 0.177, 0.216) | (0.609, 0.128, 0.052)→(0.603, 0.127, 0.023) | 0.134→0.163 | 1.00 / 4.000 | 0.140 | 0.445 |
| retract_after_place | retract | 1.00 / step_budget | (0.608, 0.177, 0.216)→(0.613, 0.180, 0.250) | (0.603, 0.127, 0.023)→(0.602, 0.127, 0.023) | 0.163→0.164 | 1.00 / 4.000 | 0.123 | 0.142 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.516
- phase_score: 0.366
- phase_breakdown.descend_1_score: 0.880
- phase_breakdown.grasp_1_score: 1.000
- phase_breakdown.transport_arc_score: 0.071
- phase_breakdown.approach_1_score: 0.074
- phase_breakdown.release_1_score: 0.568
- grasp_place_fitness: 0.721

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.721
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.516
- **Median Q (composite search score)**: -0.034
- **K-run variance**: 0.0040
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.387


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.37838,"average_solve_count":370.0,"average_success_count":370.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_to_object.speed":0.08733,"descend_to_grasp.speed":0.07606,"descend_to_place.speed":0.0308,"grasp.grip_force":12.40947,"lift_object.lift_height":0.26825,"lift_object.speed":0.04104,"release_object.release_duration":0.60416,"retract_after_place.speed":0.09934,"transport_to_goal.arc_height":0.19883,"transport_to_goal.speed":0.0559},"optimized_scores":{"best_composite_score":-0.11438,"best_fitness_score":0.56562,"best_task_score":0.20243},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":1185.0,"contact_point_centroid":[0.58668,0.08558,-0.00356],"force_p95":0.51156,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.58544,"mean_force":0.18206,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.58681,0.15844,0.3582]},{"body_a":"world","body_b":"grasp_target","contact_count":116.0,"contact_point_centroid":[0.53315,-0.02059,-0.00133],"force_p95":0.37584,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.41042,"mean_force":0.10778,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.52192,-0.0208,0.04545]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":18915.0,"contact_point_centroid":[0.52452,-0.00156,0.12848],"force_p95":0.077,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26131,"mean_force":0.05398,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.52399,-0.02073,0.12616]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":20836.0,"contact_point_centroid":[0.52442,-0.03983,0.12846],"force_p95":0.07282,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25267,"mean_force":0.0497,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.52402,-0.02073,0.12654]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":7113.0,"contact_point_centroid":[0.5382,0.01837,0.28029],"force_p95":0.138,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22869,"mean_force":0.07985,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.53378,-0.00045,0.27982]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8259.0,"contact_point_centroid":[0.53892,-0.01656,0.28354],"force_p95":0.11018,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22132,"mean_force":0.0704,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.53461,0.00202,0.28339]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53703,-0.02122,-0.00205],"force_p95":0.13606,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.16885,"mean_force":0.12667,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.52431,-0.02085,0.04565]},{"body_a":"world","body_b":"grasp_target","contact_count":1936.0,"contact_point_centroid":[0.53702,-0.02132,-0.00193],"force_p95":0.13308,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12288,"phase_index":0.0,"phase_name":"approach_to_object","phase_type":"approach","tcp_position_centroid":[0.51383,-0.00952,0.22799]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4473.0,"contact_point_centroid":[0.52369,-0.00163,0.04719],"force_p95":0.07639,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1287,"mean_force":0.04785,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.52311,-0.02083,0.04426]},{"body_a":"world","body_b":"grasp_target","contact_count":1292.0,"contact_point_centroid":[0.53702,-0.02132,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.52943,-0.02017,0.10491]},{"body_a":"world","body_b":"grasp_target","contact_count":1092.0,"contact_point_centroid":[0.58683,0.08552,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.60413,0.21618,0.28386]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.58683,0.08552,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.6031,0.22226,0.23517]},{"body_a":"world","body_b":"grasp_target","contact_count":632.0,"contact_point_centroid":[0.58683,0.08552,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":7.0,"phase_name":"retract_after_place","phase_type":"retract","tcp_position_centroid":[0.60391,0.22351,0.27053]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4897.0,"contact_point_centroid":[0.52393,-0.03998,0.04606],"force_p95":0.06943,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08691,"mean_force":0.04487,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.52311,-0.02083,0.04425]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1243.0,"contact_point_centroid":[0.58769,0.15978,0.36018],"force_p95":0.01193,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01607,"mean_force":0.01062,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.58725,0.15978,0.3579]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1165.0,"contact_point_centroid":[0.60464,0.21622,0.2861],"force_p95":0.011,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0128,"mean_force":0.01044,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.60413,0.2162,0.28375]}],"total_contact_groups":17},"final_pose_error":0.01998,"key_states":{"actual_goal_position":[0.61031,0.22775,0.20741],"final_object_position":[0.58683,0.08552,0.01602],"final_tcp_position":[0.60663,0.22555,0.2879],"realised_goal_position":[0.61031,0.22775,0.20741],"realised_object_initial_position":[0.53702,-0.02132,0.03]},"peak_contact_force":9749.1468,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":485.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.03],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31446,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_to_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1936.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.53016,-0.01943,0.15673],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.13091,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":323.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1292.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.53146,-0.02098,0.05413],"tcp_start":[0.53016,-0.01943,0.15673],"tcp_to_object_dist_end":0.02866,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53694,-0.0208,0.02581],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31645,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.13437,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11170.0,"raw_peak_contact_force":0.16885,"subtask_id":"grasp_1","tcp_end":[0.52308,-0.02083,0.04422],"tcp_start":[0.53146,-0.02098,0.05413],"tcp_to_object_dist_end":0.02304,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":38.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53477,-0.0207,0.18908],"object_pos_start":[0.53694,-0.0208,0.02581],"object_to_goal_dist_end":0.26033,"object_to_goal_dist_start":0.31645,"object_z_max":0.18892,"peak_contact_force":0.07539,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":39867.0,"raw_peak_contact_force":0.41042,"tcp_end":[0.52945,-0.02073,0.21421],"tcp_start":[0.52308,-0.02083,0.04422],"tcp_to_object_dist_end":0.02569,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1022.0,"n_steps_budget":1000.0,"object_pos_end":[0.58683,0.08552,0.01602],"object_pos_start":[0.53477,-0.0207,0.18908],"object_to_goal_dist_end":0.23961,"object_to_goal_dist_start":0.26033,"object_z_max":0.32336,"peak_contact_force":9749.1468,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":17800.0,"raw_peak_contact_force":2.58544,"subtask_id":"transport_arc","tcp_end":[0.60323,0.20985,0.33221],"tcp_start":[0.60226,0.20587,0.3373],"tcp_to_object_dist_end":0.34015,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":273.0,"n_steps_budget":1000.0,"object_pos_end":[0.58683,0.08552,0.01602],"object_pos_start":[0.58683,0.08552,0.01602],"object_to_goal_dist_end":0.23961,"object_to_goal_dist_start":0.23961,"object_z_max":0.01602,"peak_contact_force":9749.05915,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2257.0,"raw_peak_contact_force":0.12263,"subtask_id":"release_1","tcp_end":[0.60645,0.22364,0.23561],"tcp_start":[0.60323,0.20985,0.33221],"tcp_to_object_dist_end":0.26015,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.58683,0.08552,0.01602],"object_pos_start":[0.58683,0.08552,0.01602],"object_to_goal_dist_end":0.23961,"object_to_goal_dist_start":0.23961,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1026.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.602,0.22171,0.25453],"tcp_start":[0.60645,0.22364,0.23561],"tcp_to_object_dist_end":0.27507,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":158.0,"n_steps_budget":600.0,"object_pos_end":[0.58683,0.08552,0.01602],"object_pos_start":[0.58683,0.08552,0.01602],"object_to_goal_dist_end":0.23961,"object_to_goal_dist_start":0.23961,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_after_place","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":632.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.60663,0.22555,0.2879],"tcp_start":[0.602,0.22171,0.25453],"tcp_to_object_dist_end":0.30646,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.13805,"average_solve_count":297.0,"average_success_count":297.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_to_object.speed":0.0561,"descend_to_grasp.speed":0.05719,"descend_to_place.speed":0.0694,"grasp.grip_force":23.29249,"lift_object.lift_height":0.27369,"lift_object.speed":0.02591,"release_object.release_duration":0.6355,"retract_after_place.speed":0.02331,"transport_to_goal.arc_height":0.19257,"transport_to_goal.speed":0.14859},"optimized_scores":{"best_composite_score":-0.03388,"best_fitness_score":0.64612,"best_task_score":0.36343},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":839.0,"contact_point_centroid":[0.63148,0.14544,-0.00404],"force_p95":0.85219,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.96241,"mean_force":0.20734,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.6251,0.15509,0.24487]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6800.0,"contact_point_centroid":[0.56086,0.03301,0.27302],"force_p95":0.13613,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.45495,"mean_force":0.08206,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.55663,0.0143,0.27359]},{"body_a":"world","body_b":"grasp_target","contact_count":121.0,"contact_point_centroid":[0.54173,-0.02828,-0.00133],"force_p95":0.37474,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.40016,"mean_force":0.10338,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.53015,-0.02845,0.04521]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":18765.0,"contact_point_centroid":[0.53277,-0.00925,0.12644],"force_p95":0.07733,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26986,"mean_force":0.05434,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.53213,-0.02838,0.1243]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":19917.0,"contact_point_centroid":[0.53298,-0.04747,0.12899],"force_p95":0.07562,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25883,"mean_force":0.05165,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.53231,-0.02838,0.1271]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":7585.0,"contact_point_centroid":[0.56194,-0.00169,0.2736],"force_p95":0.1159,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25534,"mean_force":0.07407,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.55794,0.01688,0.27423]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.54562,-0.0291,-0.00207],"force_p95":0.14214,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.18427,"mean_force":0.12796,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.53261,-0.02853,0.04541]},{"body_a":"world","body_b":"grasp_target","contact_count":2200.0,"contact_point_centroid":[0.5456,-0.02923,-0.00194],"force_p95":0.13205,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12285,"phase_index":0.0,"phase_name":"approach_to_object","phase_type":"approach","tcp_position_centroid":[0.51764,-0.01315,0.22727]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4105.0,"contact_point_centroid":[0.5323,-0.00928,0.04669],"force_p95":0.07812,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13378,"mean_force":0.05185,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.53139,-0.02849,0.04397]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.63127,0.14829,-0.00199],"force_p95":0.12343,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12608,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.62405,0.16009,0.20407]},{"body_a":"world","body_b":"grasp_target","contact_count":732.0,"contact_point_centroid":[0.63127,0.14829,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12264,"mean_force":0.12263,"phase_index":7.0,"phase_name":"retract_after_place","phase_type":"retract","tcp_position_centroid":[0.62485,0.16117,0.23897]},{"body_a":"world","body_b":"grasp_target","contact_count":1344.0,"contact_point_centroid":[0.5456,-0.02923,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.53754,-0.02768,0.10462]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4913.0,"contact_point_centroid":[0.5323,-0.04758,0.04575],"force_p95":0.07031,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07876,"mean_force":0.04466,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.5314,-0.02849,0.04397]},{"body_a":"left_finger","body_b":"right_finger","contact_count":868.0,"contact_point_centroid":[0.62574,0.15553,0.24338],"force_p95":0.01273,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01622,"mean_force":0.01068,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.62528,0.15552,0.24116]},{"body_a":"left_finger","body_b":"right_finger","contact_count":226.0,"contact_point_centroid":[0.62715,0.16088,0.20289],"force_p95":0.01097,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01266,"mean_force":0.00993,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.62639,0.16086,0.20058]}],"total_contact_groups":15},"final_pose_error":0.02,"key_states":{"actual_goal_position":[0.63284,0.16493,0.17692],"final_object_position":[0.63127,0.14829,0.02602],"final_tcp_position":[0.6283,0.16305,0.25754],"realised_goal_position":[0.63284,0.16493,0.17692],"realised_object_initial_position":[0.5456,-0.02923,0.03]},"peak_contact_force":273006.25941,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":551.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.03],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.25864,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_to_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2200.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.538,-0.02673,0.15599],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.13022,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":336.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1344.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.53984,-0.02875,0.05415],"tcp_start":[0.538,-0.02673,0.15599],"tcp_to_object_dist_end":0.02872,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54552,-0.02855,0.02575],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.2606,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.13879,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10818.0,"raw_peak_contact_force":0.18427,"subtask_id":"grasp_1","tcp_end":[0.53136,-0.02849,0.04393],"tcp_start":[0.53984,-0.02875,0.05415],"tcp_to_object_dist_end":0.02304,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":38.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5428,-0.02842,0.18448],"object_pos_start":[0.54552,-0.02855,0.02575],"object_to_goal_dist_end":0.21343,"object_to_goal_dist_start":0.2606,"object_z_max":0.18433,"peak_contact_force":0.07533,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":38803.0,"raw_peak_contact_force":0.40016,"tcp_end":[0.53743,-0.02841,0.20964],"tcp_start":[0.53136,-0.02849,0.04393],"tcp_to_object_dist_end":0.02572,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":674.0,"n_steps_budget":1000.0,"object_pos_end":[0.62676,0.12715,0.10494],"object_pos_start":[0.5428,-0.02842,0.18448],"object_to_goal_dist_end":0.08152,"object_to_goal_dist_start":0.21343,"object_z_max":0.28418,"peak_contact_force":0.0,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":14385.0,"raw_peak_contact_force":0.45495,"subtask_id":"transport_arc","tcp_end":[0.62312,0.14796,0.29934],"tcp_start":[0.53743,-0.02841,0.20964],"tcp_to_object_dist_end":0.19554,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":259.0,"n_steps_budget":1000.0,"object_pos_end":[0.63127,0.14809,0.02602],"object_pos_start":[0.62676,0.12715,0.10494],"object_to_goal_dist_end":0.15185,"object_to_goal_dist_start":0.08152,"object_z_max":0.10494,"peak_contact_force":273006.25941,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1707.0,"raw_peak_contact_force":1.96241,"subtask_id":"release_1","tcp_end":[0.62804,0.1612,0.20459],"tcp_start":[0.62312,0.14796,0.29934],"tcp_to_object_dist_end":0.17908,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.63127,0.14829,0.02602],"object_pos_start":[0.63127,0.14809,0.02602],"object_to_goal_dist_end":0.15182,"object_to_goal_dist_start":0.15185,"object_z_max":0.02602,"peak_contact_force":0.12264,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1026.0,"raw_peak_contact_force":0.12608,"tcp_end":[0.62268,0.15963,0.22341],"tcp_start":[0.62804,0.1612,0.20459],"tcp_to_object_dist_end":0.1979,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":183.0,"n_steps_budget":1000.0,"object_pos_end":[0.63127,0.14829,0.02602],"object_pos_start":[0.63127,0.14829,0.02602],"object_to_goal_dist_end":0.15182,"object_to_goal_dist_start":0.15182,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"retract_after_place","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":732.0,"raw_peak_contact_force":0.12264,"tcp_end":[0.6283,0.16305,0.25754],"tcp_start":[0.62268,0.15963,0.22341],"tcp_to_object_dist_end":0.23201,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.35526,"average_solve_count":304.0,"average_success_count":304.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_to_object.speed":0.07407,"descend_to_grasp.speed":0.06205,"descend_to_place.speed":0.05586,"grasp.grip_force":19.84555,"lift_object.lift_height":0.23057,"lift_object.speed":0.0464,"release_object.release_duration":0.61188,"retract_after_place.speed":0.06292,"transport_to_goal.arc_height":0.17221,"transport_to_goal.speed":0.06368},"optimized_scores":{"best_composite_score":0.04053,"best_fitness_score":0.72053,"best_task_score":0.51631},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":221.0,"contact_point_centroid":[0.59289,0.1478,-0.00543],"force_p95":1.00039,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.08725,"mean_force":0.30544,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.59801,0.14848,0.15833]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2723.0,"contact_point_centroid":[0.60491,0.12753,0.19701],"force_p95":0.13562,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.42462,"mean_force":0.10309,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.59991,0.14578,0.20063]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2778.0,"contact_point_centroid":[0.60522,0.16405,0.19613],"force_p95":0.1289,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.40477,"mean_force":0.10195,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.59995,0.14582,0.20022]},{"body_a":"world","body_b":"grasp_target","contact_count":101.0,"contact_point_centroid":[0.46011,-0.00028,-0.00128],"force_p95":0.34895,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.38596,"mean_force":0.08358,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.45021,-0.00021,0.04877]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":596.0,"contact_point_centroid":[0.60781,0.16807,0.14098],"force_p95":0.118,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30994,"mean_force":0.08488,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.6021,0.14968,0.14541]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":582.0,"contact_point_centroid":[0.60702,0.13129,0.14136],"force_p95":0.11844,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29141,"mean_force":0.08623,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.60212,0.14969,0.14546]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":20485.0,"contact_point_centroid":[0.45289,0.01888,0.14637],"force_p95":0.07425,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26336,"mean_force":0.05028,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.45342,-0.0002,0.14583]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":18817.0,"contact_point_centroid":[0.45204,-0.01939,0.1457],"force_p95":0.0795,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25199,"mean_force":0.05398,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.45338,-0.0002,0.14508]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6958.0,"contact_point_centroid":[0.51337,0.072,0.27745],"force_p95":0.13339,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22423,"mean_force":0.08897,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.51041,0.05344,0.27945]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":7949.0,"contact_point_centroid":[0.51172,0.03427,0.27822],"force_p95":0.12796,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19529,"mean_force":0.07832,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.50958,0.05262,0.28004]},{"body_a":"world","body_b":"grasp_target","contact_count":624.0,"contact_point_centroid":[0.58636,0.1483,-0.00196],"force_p95":0.17448,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.18049,"mean_force":0.12333,"phase_index":7.0,"phase_name":"retract_after_place","phase_type":"retract","tcp_position_centroid":[0.60055,0.1496,0.18585]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.46285,-7e-05,-0.00202],"force_p95":0.12944,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.15221,"mean_force":0.12445,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.45231,-0.00018,0.04855]},{"body_a":"world","body_b":"grasp_target","contact_count":1716.0,"contact_point_centroid":[0.46286,-7e-05,-0.00192],"force_p95":0.13411,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12291,"phase_index":0.0,"phase_name":"approach_to_object","phase_type":"approach","tcp_position_centroid":[0.48112,-5e-05,0.23066]},{"body_a":"world","body_b":"grasp_target","contact_count":1452.0,"contact_point_centroid":[0.46286,-7e-05,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.45961,-0.0001,0.10711]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4870.0,"contact_point_centroid":[0.45115,0.019,0.04909],"force_p95":0.06696,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08171,"mean_force":0.0448,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.45125,-0.00019,0.04751]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4856.0,"contact_point_centroid":[0.45025,-0.01939,0.04842],"force_p95":0.06666,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08049,"mean_force":0.04495,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.45124,-0.00019,0.0475]}],"total_contact_groups":16},"final_pose_error":0.01992,"key_states":{"actual_goal_position":[0.61015,0.15287,0.12219],"final_object_position":[0.58644,0.1483,0.02602],"final_tcp_position":[0.6044,0.15102,0.20321],"realised_goal_position":[0.61015,0.15287,0.12219],"realised_object_initial_position":[0.46286,-7e-05,0.03]},"peak_contact_force":30.63086,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":430.0,"n_steps_budget":1000.0,"object_pos_end":[0.46286,-7e-05,0.02602],"object_pos_start":[0.46286,-7e-05,0.03],"object_to_goal_dist_end":0.2331,"object_to_goal_dist_start":0.23148,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_to_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1716.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.46309,-8e-05,0.15999],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.13397,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":363.0,"n_steps_budget":1000.0,"object_pos_end":[0.46286,-7e-05,0.02602],"object_pos_start":[0.46286,-7e-05,0.02602],"object_to_goal_dist_end":0.2331,"object_to_goal_dist_start":0.2331,"object_z_max":0.02602,"peak_contact_force":30.63086,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1452.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.45869,-0.00011,0.05487],"tcp_start":[0.46309,-8e-05,0.15999],"tcp_to_object_dist_end":0.02915,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.46277,-0.00015,0.02591],"object_pos_start":[0.46286,-7e-05,0.02602],"object_to_goal_dist_end":0.23325,"object_to_goal_dist_start":0.2331,"object_z_max":0.02602,"peak_contact_force":0.12957,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11526.0,"raw_peak_contact_force":0.15221,"subtask_id":"grasp_1","tcp_end":[0.45122,-0.00019,0.04748],"tcp_start":[0.45869,-0.00011,0.05487],"tcp_to_object_dist_end":0.02447,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":38.0,"n_steps":973.0,"n_steps_budget":1000.0,"object_pos_end":[0.46189,-2e-05,0.21366],"object_pos_start":[0.46277,-0.00015,0.02591],"object_to_goal_dist_end":0.23178,"object_to_goal_dist_start":0.23325,"object_z_max":0.21349,"peak_contact_force":0.08359,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":39403.0,"raw_peak_contact_force":0.38596,"tcp_end":[0.45927,-0.00017,0.242],"tcp_start":[0.45122,-0.00019,0.04748],"tcp_to_object_dist_end":0.02846,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":17.0,"n_steps":648.0,"n_steps_budget":1000.0,"object_pos_end":[0.6038,0.14191,0.2191],"object_pos_start":[0.46189,-2e-05,0.21366],"object_to_goal_dist_end":0.09773,"object_to_goal_dist_start":0.23178,"object_z_max":0.27019,"peak_contact_force":0.13449,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":14907.0,"raw_peak_contact_force":0.22423,"subtask_id":"transport_arc","tcp_end":[0.59783,0.14206,0.25338],"tcp_start":[0.45927,-0.00017,0.242],"tcp_to_object_dist_end":0.0348,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":18.0,"n_steps":303.0,"n_steps_budget":1000.0,"object_pos_end":[0.6098,0.15002,0.11299],"object_pos_start":[0.6038,0.14191,0.2191],"object_to_goal_dist_end":0.00963,"object_to_goal_dist_start":0.09773,"object_z_max":0.2191,"peak_contact_force":0.1209,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":5501.0,"raw_peak_contact_force":0.42462,"subtask_id":"release_1","tcp_end":[0.60438,0.15023,0.14973],"tcp_start":[0.59783,0.14206,0.25338],"tcp_to_object_dist_end":0.03714,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.58974,0.14801,0.02627],"object_pos_start":[0.6098,0.15002,0.11299],"object_to_goal_dist_end":0.09818,"object_to_goal_dist_start":0.00963,"object_z_max":0.11299,"peak_contact_force":0.17502,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1399.0,"raw_peak_contact_force":1.08725,"tcp_end":[0.59792,0.14846,0.16978],"tcp_start":[0.60438,0.15023,0.14973],"tcp_to_object_dist_end":0.14374,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":156.0,"n_steps_budget":600.0,"object_pos_end":[0.58644,0.1483,0.02602],"object_pos_start":[0.58974,0.14801,0.02627],"object_to_goal_dist_end":0.09916,"object_to_goal_dist_start":0.09818,"object_z_max":0.02629,"peak_contact_force":0.12423,"phase_name":"retract_after_place","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":624.0,"raw_peak_contact_force":0.18049,"tcp_end":[0.6044,0.15102,0.20321],"tcp_start":[0.59792,0.14846,0.16978],"tcp_to_object_dist_end":0.17812,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```