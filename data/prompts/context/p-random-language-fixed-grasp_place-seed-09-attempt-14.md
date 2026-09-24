## Search State

- **Seed**: 9
- **Iteration**: 15 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 14 | approach → descend → grasp → lift → approach → approach → grasp | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | position_control | impedance_control | impedance_control | impedance_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 9 | 0.0504 | 0.37 | ❌ rejected |
| 13 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | impedance_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 8 | 0.0757 | 0.38 | ❌ rejected |
| 12 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | impedance_control | impedance_control | impedance_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 10 | -0.0359 | 0.36 | ❌ rejected |
| 11 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | position_control | position_control | position_control | impedance_control | impedance_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 8 | 0.2955 | 0.70 | ❌ rejected |
| 10 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | position_control | position_control | position_control | impedance_control | impedance_control | impedance_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 8 | 0.2587 | 0.63 | ❌ rejected |

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

## Current Skill (Q=0.050) — your mutation base

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

- **Composite score**: 0.050
- **task_score** (E): 0.373
- **fitness_score**: 0.650  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.600

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_to_object | 1.00 | 1.00 | 0.1488 |
| descend_to_grasp | 1.00 | 1.00 | 0.1032 |
| grasp | 1.00 | 1.00 | 0.0122 |
| lift_object | 1.00 | 1.00 | 0.1610 |
| transport_to_goal | 1.00 | 1.00 | 0.1549 |
| place_at_goal | 1.00 | 1.00 | 0.1197 |
| hold_grasp | 1.00 | 1.00 | 0.0165 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_to_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.510, -0.015, 0.158) | (0.515, -0.017, 0.030)→(0.515, -0.017, 0.026) | 0.268→0.270 | 1.00 / 4.000 | 9.125 | 0.138 |
| descend_to_grasp | descend | 1.00 / step_budget | (0.510, -0.015, 0.158)→(0.510, -0.017, 0.054) | (0.515, -0.017, 0.026)→(0.515, -0.017, 0.026) | 0.270→0.270 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp | grasp | 1.00 / step_budget | (0.510, -0.017, 0.054)→(0.502, -0.017, 0.045) | (0.515, -0.017, 0.026)→(0.515, -0.016, 0.026) | 0.270→0.270 | 1.00 / 42.000 | 0.134 | 0.168 |
| lift_object | lift | 1.00 / step_budget | (0.502, -0.017, 0.045)→(0.511, -0.016, 0.206) | (0.515, -0.016, 0.026)→(0.516, -0.016, 0.180) | 0.270→0.234 | 1.00 / 37.000 | 0.079 | 0.394 |
| transport_to_goal | approach | 1.00 / step_budget | (0.538, 0.042, 0.248)→(0.607, 0.160, 0.300) | (0.516, -0.016, 0.180)→(0.612, 0.157, 0.184) | 0.234→0.126 | 1.00 / 11.333 | 3249.512 | 0.840 |
| place_at_goal | approach | 1.00 / step_budget | (0.607, 0.160, 0.300)→(0.613, 0.177, 0.182) | (0.612, 0.157, 0.184)→(0.619, 0.162, 0.020) | 0.125→0.151 | 1.00 / 6.667 | 3327.644 | 1.473 |
| hold_grasp | grasp | 1.00 / step_budget | (0.613, 0.177, 0.182)→(0.606, 0.175, 0.167) | (0.619, 0.162, 0.020)→(0.618, 0.160, 0.019) | 0.151→0.153 | 1.00 / 8.333 | 0.123 | 0.160 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.506
- phase_score: 0.280
- phase_breakdown.descend_1_score: 0.879
- phase_breakdown.grasp_1_score: 1.000
- phase_breakdown.transport_arc_score: 0.069
- phase_breakdown.approach_1_score: 0.074
- phase_breakdown.release_1_score: 0.000
- grasp_place_fitness: 0.715

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.715
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.506
- **Median Q (composite search score)**: 0.034
- **K-run variance**: 0.0023
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.468


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.22029,"average_solve_count":345.0,"average_success_count":345.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_to_object.speed":0.10331,"descend_to_grasp.speed":0.0418,"grasp.grip_force":24.13842,"hold_grasp.hold_duration":0.36045,"lift_object.lift_height":0.19854,"lift_object.speed":0.05019,"place_at_goal.speed":0.04108,"transport_to_goal.arc_height":0.19185,"transport_to_goal.speed":0.04304},"optimized_scores":{"best_composite_score":0.00192,"best_fitness_score":0.60192,"best_task_score":0.27509},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":763.0,"contact_point_centroid":[0.63406,0.21124,-0.00407],"force_p95":0.89794,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.49372,"mean_force":0.21061,"phase_index":5.0,"phase_name":"place_at_goal","phase_type":"approach","tcp_position_centroid":[0.60233,0.20953,0.26085]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":51.0,"contact_point_centroid":[0.60288,0.17376,0.34536],"force_p95":0.31424,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.49275,"mean_force":0.08047,"phase_index":5.0,"phase_name":"place_at_goal","phase_type":"approach","tcp_position_centroid":[0.59676,0.18835,0.34982]},{"body_a":"world","body_b":"grasp_target","contact_count":114.0,"contact_point_centroid":[0.53347,-0.02058,-0.0013],"force_p95":0.39869,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.43288,"mean_force":0.10256,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.52196,-0.0208,0.04551]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":18541.0,"contact_point_centroid":[0.52627,-0.00156,0.1267],"force_p95":0.07687,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27962,"mean_force":0.05413,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.52571,-0.02073,0.12438]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":20414.0,"contact_point_centroid":[0.52617,-0.03983,0.12673],"force_p95":0.07291,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26906,"mean_force":0.04988,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.52575,-0.02073,0.12481]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":13972.0,"contact_point_centroid":[0.55394,0.0204,0.30954],"force_p95":0.09828,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24588,"mean_force":0.06875,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.54966,0.03905,0.3094]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":12625.0,"contact_point_centroid":[0.55285,0.05385,0.30866],"force_p95":0.1204,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23085,"mean_force":0.07527,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.5484,0.03504,0.30843]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53703,-0.02122,-0.00205],"force_p95":0.13607,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.1689,"mean_force":0.12667,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.52428,-0.02085,0.04566]},{"body_a":"world","body_b":"grasp_target","contact_count":1908.0,"contact_point_centroid":[0.53702,-0.02132,-0.00193],"force_p95":0.13338,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12288,"phase_index":0.0,"phase_name":"approach_to_object","phase_type":"approach","tcp_position_centroid":[0.51384,-0.00954,0.22782]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4471.0,"contact_point_centroid":[0.52367,-0.00162,0.04719],"force_p95":0.0764,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12873,"mean_force":0.04787,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.52308,-0.02082,0.04426]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.63415,0.21097,-0.00199],"force_p95":0.12264,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12265,"mean_force":0.12262,"phase_index":6.0,"phase_name":"hold_grasp","phase_type":"grasp","tcp_position_centroid":[0.60063,0.21888,0.20664]},{"body_a":"world","body_b":"grasp_target","contact_count":1376.0,"contact_point_centroid":[0.53702,-0.02132,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.52933,-0.02016,0.10505]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4897.0,"contact_point_centroid":[0.52391,-0.03998,0.04606],"force_p95":0.06944,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08694,"mean_force":0.04487,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.52308,-0.02083,0.04426]},{"body_a":"left_finger","body_b":"right_finger","contact_count":714.0,"contact_point_centroid":[0.60341,0.21102,0.2576],"force_p95":0.01364,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01645,"mean_force":0.01076,"phase_index":5.0,"phase_name":"place_at_goal","phase_type":"approach","tcp_position_centroid":[0.60275,0.211,0.25536]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1942.0,"contact_point_centroid":[0.60112,0.21892,0.20889],"force_p95":0.01096,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01276,"mean_force":0.01034,"phase_index":6.0,"phase_name":"hold_grasp","phase_type":"grasp","tcp_position_centroid":[0.60064,0.21889,0.20666]}],"total_contact_groups":15},"final_pose_error":0.01486,"key_states":{"actual_goal_position":[0.61031,0.22775,0.20741],"final_object_position":[0.63415,0.21097,0.01602],"final_tcp_position":[0.60557,0.22069,0.21959],"realised_goal_position":[0.61031,0.22775,0.20741],"realised_object_initial_position":[0.53702,-0.02132,0.03]},"peak_contact_force":2.49372,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":478.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.03],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31446,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_to_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1908.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.53013,-0.01943,0.15669],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.13086,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":344.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1376.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.53142,-0.02098,0.05411],"tcp_start":[0.53013,-0.01943,0.15669],"tcp_to_object_dist_end":0.02865,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53694,-0.02079,0.02581],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31645,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.13438,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11168.0,"raw_peak_contact_force":0.1689,"subtask_id":"grasp_1","tcp_end":[0.52305,-0.02082,0.04422],"tcp_start":[0.53142,-0.02098,0.05411],"tcp_to_object_dist_end":0.02306,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":38.0,"n_steps":980.0,"n_steps_budget":1000.0,"object_pos_end":[0.53837,-0.02069,0.18498],"object_pos_start":[0.53694,-0.02079,0.02581],"object_to_goal_dist_end":0.25962,"object_to_goal_dist_start":0.31645,"object_z_max":0.18483,"peak_contact_force":0.07487,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":39069.0,"raw_peak_contact_force":0.43288,"tcp_end":[0.53289,-0.02072,0.21006],"tcp_start":[0.52305,-0.02082,0.04422],"tcp_to_object_dist_end":0.02568,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":7.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.60473,0.18495,0.31597],"object_pos_start":[0.53837,-0.02069,0.18498],"object_to_goal_dist_end":0.11683,"object_to_goal_dist_start":0.25962,"object_z_max":0.34021,"peak_contact_force":0.18924,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":26597.0,"raw_peak_contact_force":0.24588,"subtask_id":"transport_arc","tcp_end":[0.59699,0.18783,0.35085],"tcp_start":[0.53289,-0.02072,0.21006],"tcp_to_object_dist_end":0.03584,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":304.0,"n_steps_budget":1000.0,"object_pos_end":[0.63414,0.21096,0.01602],"object_pos_start":[0.60473,0.18495,0.31597],"object_to_goal_dist_end":0.1936,"object_to_goal_dist_start":0.11683,"object_z_max":0.31597,"peak_contact_force":0.12266,"phase_name":"place_at_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1528.0,"raw_peak_contact_force":2.49372,"tcp_end":[0.60557,0.22069,0.21959],"tcp_start":[0.59699,0.18783,0.35085],"tcp_to_object_dist_end":0.2058,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.63415,0.21097,0.01602],"object_pos_start":[0.63414,0.21096,0.01602],"object_to_goal_dist_end":0.1936,"object_to_goal_dist_start":0.1936,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"hold_grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":3742.0,"raw_peak_contact_force":0.12265,"tcp_end":[0.59979,0.21853,0.20448],"tcp_start":[0.60557,0.22069,0.21959],"tcp_to_object_dist_end":0.19171,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.2952,"average_solve_count":271.0,"average_success_count":271.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_to_object.speed":0.07658,"descend_to_grasp.speed":0.05698,"grasp.grip_force":17.06741,"hold_grasp.hold_duration":0.76677,"lift_object.lift_height":0.1595,"lift_object.speed":0.02844,"place_at_goal.speed":0.07977,"transport_to_goal.arc_height":0.07469,"transport_to_goal.speed":0.14473},"optimized_scores":{"best_composite_score":0.03389,"best_fitness_score":0.63389,"best_task_score":0.33864},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":334.0,"contact_point_centroid":[0.62962,0.14314,-0.00652],"force_p95":1.22672,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.99704,"mean_force":0.29186,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.61878,0.13815,0.30039]},{"body_a":"world","body_b":"grasp_target","contact_count":139.0,"contact_point_centroid":[0.54215,-0.02834,-0.00138],"force_p95":0.32168,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.3624,"mean_force":0.10332,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.53015,-0.02845,0.04492]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":7769.0,"contact_point_centroid":[0.55728,-0.01707,0.24237],"force_p95":0.1241,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24028,"mean_force":0.07274,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.55285,0.00165,0.24218]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":15372.0,"contact_point_centroid":[0.53479,-0.00924,0.10959],"force_p95":0.07803,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23988,"mean_force":0.05418,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.53416,-0.02839,0.10728]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":16523.0,"contact_point_centroid":[0.53484,-0.04746,0.10917],"force_p95":0.07507,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23157,"mean_force":0.05109,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.53413,-0.02839,0.10697]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":7726.0,"contact_point_centroid":[0.55995,0.02511,0.24764],"force_p95":0.11399,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19366,"mean_force":0.07292,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.55516,0.00643,0.24742]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.54562,-0.0291,-0.00207],"force_p95":0.14195,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.18406,"mean_force":0.12792,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.53262,-0.02853,0.04527]},{"body_a":"world","body_b":"grasp_target","contact_count":2072.0,"contact_point_centroid":[0.5456,-0.02923,-0.00193],"force_p95":0.13237,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12286,"phase_index":0.0,"phase_name":"approach_to_object","phase_type":"approach","tcp_position_centroid":[0.51768,-0.01316,0.22723]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4104.0,"contact_point_centroid":[0.5323,-0.00929,0.04655],"force_p95":0.0781,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.134,"mean_force":0.05185,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.5314,-0.0285,0.04382]},{"body_a":"world","body_b":"grasp_target","contact_count":864.0,"contact_point_centroid":[0.62962,0.14299,-0.00196],"force_p95":0.12577,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12707,"mean_force":0.12287,"phase_index":5.0,"phase_name":"place_at_goal","phase_type":"approach","tcp_position_centroid":[0.62518,0.15537,0.24285]},{"body_a":"world","body_b":"grasp_target","contact_count":1344.0,"contact_point_centroid":[0.5456,-0.02923,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.53755,-0.02769,0.10453]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.62962,0.143,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"hold_grasp","phase_type":"grasp","tcp_position_centroid":[0.62226,0.15963,0.17715]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4914.0,"contact_point_centroid":[0.5323,-0.04759,0.0456],"force_p95":0.07027,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07749,"mean_force":0.04466,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.5314,-0.0285,0.04383]},{"body_a":"left_finger","body_b":"right_finger","contact_count":223.0,"contact_point_centroid":[0.62175,0.14392,0.30009],"force_p95":0.01504,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01642,"mean_force":0.01161,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.62133,0.14391,0.29791]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1898.0,"contact_point_centroid":[0.62282,0.15965,0.17934],"force_p95":0.01101,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01283,"mean_force":0.01056,"phase_index":6.0,"phase_name":"hold_grasp","phase_type":"grasp","tcp_position_centroid":[0.62225,0.15962,0.17712]},{"body_a":"left_finger","body_b":"right_finger","contact_count":924.0,"contact_point_centroid":[0.62568,0.15537,0.24517],"force_p95":0.01094,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01099,"mean_force":0.01043,"phase_index":5.0,"phase_name":"place_at_goal","phase_type":"approach","tcp_position_centroid":[0.62518,0.15536,0.24292]}],"total_contact_groups":16},"final_pose_error":0.01484,"key_states":{"actual_goal_position":[0.63284,0.16493,0.17692],"final_object_position":[0.62962,0.143,0.01602],"final_tcp_position":[0.62795,0.16117,0.19041],"realised_goal_position":[0.63284,0.16493,0.17692],"realised_object_initial_position":[0.5456,-0.02923,0.03]},"peak_contact_force":9748.77702,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":519.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.03],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.25864,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_to_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2072.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.53803,-0.02674,0.15593],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.13015,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":336.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1344.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.53985,-0.02875,0.054],"tcp_start":[0.53803,-0.02674,0.15593],"tcp_to_object_dist_end":0.02858,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54552,-0.02855,0.02575],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.2606,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.13862,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10818.0,"raw_peak_contact_force":0.18406,"subtask_id":"grasp_1","tcp_end":[0.53137,-0.0285,0.04379],"tcp_start":[0.53985,-0.02875,0.054],"tcp_to_object_dist_end":0.02292,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":38.0,"n_steps":820.0,"n_steps_budget":1000.0,"object_pos_end":[0.54747,-0.02845,0.14709],"object_pos_start":[0.54552,-0.02855,0.02575],"object_to_goal_dist_end":0.21348,"object_to_goal_dist_start":0.2606,"object_z_max":0.14695,"peak_contact_force":0.07642,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":32034.0,"raw_peak_contact_force":0.3624,"tcp_end":[0.54087,-0.02842,0.171],"tcp_start":[0.53137,-0.0285,0.04379],"tcp_to_object_dist_end":0.0248,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":773.0,"n_steps_budget":1000.0,"object_pos_end":[0.62961,0.14263,0.01605],"object_pos_start":[0.54747,-0.02845,0.14709],"object_to_goal_dist_end":0.16244,"object_to_goal_dist_start":0.21348,"object_z_max":0.27316,"peak_contact_force":9748.21776,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":16052.0,"raw_peak_contact_force":1.99704,"subtask_id":"transport_arc","tcp_end":[0.6237,0.15033,0.29361],"tcp_start":[0.62323,0.1474,0.29669],"tcp_to_object_dist_end":0.27773,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":216.0,"n_steps_budget":1000.0,"object_pos_end":[0.62962,0.143,0.01602],"object_pos_start":[0.62962,0.14304,0.01683],"object_to_goal_dist_end":0.16242,"object_to_goal_dist_start":0.16162,"object_z_max":0.01683,"peak_contact_force":9748.77702,"phase_name":"place_at_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1788.0,"raw_peak_contact_force":0.12707,"tcp_end":[0.62795,0.16117,0.19041],"tcp_start":[0.6237,0.15033,0.29361],"tcp_to_object_dist_end":0.17535,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.62962,0.143,0.01602],"object_pos_start":[0.62962,0.143,0.01602],"object_to_goal_dist_end":0.16242,"object_to_goal_dist_start":0.16242,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"hold_grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":3698.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.6213,0.15934,0.17496],"tcp_start":[0.62795,0.16117,0.19041],"tcp_to_object_dist_end":0.16,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.45714,"average_solve_count":245.0,"average_success_count":245.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_to_object.speed":0.07691,"descend_to_grasp.speed":0.0574,"grasp.grip_force":17.0637,"hold_grasp.hold_duration":0.46437,"lift_object.lift_height":0.22534,"lift_object.speed":0.05426,"place_at_goal.speed":0.07293,"transport_to_goal.arc_height":0.15144,"transport_to_goal.speed":0.09461},"optimized_scores":{"best_composite_score":0.11534,"best_fitness_score":0.71534,"best_task_score":0.50612},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":247.0,"contact_point_centroid":[0.59224,0.13087,-0.00643],"force_p95":1.12625,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.79758,"mean_force":0.32798,"phase_index":5.0,"phase_name":"place_at_goal","phase_type":"approach","tcp_position_centroid":[0.60306,0.14878,0.1556]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":893.0,"contact_point_centroid":[0.6031,0.16219,0.22558],"force_p95":0.17473,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.43348,"mean_force":0.12109,"phase_index":5.0,"phase_name":"place_at_goal","phase_type":"approach","tcp_position_centroid":[0.59883,0.14418,0.23031]},{"body_a":"world","body_b":"grasp_target","contact_count":98.0,"contact_point_centroid":[0.46077,-0.00048,-0.00127],"force_p95":0.33664,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.38602,"mean_force":0.07081,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.45026,-0.00021,0.04887]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":921.0,"contact_point_centroid":[0.60267,0.12615,0.22389],"force_p95":0.17881,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.3818,"mean_force":0.11884,"phase_index":5.0,"phase_name":"place_at_goal","phase_type":"approach","tcp_position_centroid":[0.59889,0.14427,0.22849]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":7063.0,"contact_point_centroid":[0.51493,0.07228,0.28145],"force_p95":0.14353,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27637,"mean_force":0.09188,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.5108,0.05384,0.2833]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":18660.0,"contact_point_centroid":[0.45334,0.01889,0.14315],"force_p95":0.07849,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26526,"mean_force":0.05303,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.45337,-0.0002,0.14234]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":18364.0,"contact_point_centroid":[0.45223,-0.01933,0.14276],"force_p95":0.08141,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2529,"mean_force":0.05397,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.45337,-0.0002,0.14227]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":7439.0,"contact_point_centroid":[0.51388,0.03518,0.27916],"force_p95":0.13756,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23658,"mean_force":0.08626,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.5105,0.05353,0.28105]},{"body_a":"world","body_b":"grasp_target","contact_count":1781.0,"contact_point_centroid":[0.58958,0.12564,-0.00199],"force_p95":0.15535,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.2356,"mean_force":0.12455,"phase_index":6.0,"phase_name":"hold_grasp","phase_type":"grasp","tcp_position_centroid":[0.59781,0.14848,0.12311]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.46285,-7e-05,-0.00202],"force_p95":0.12944,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.15221,"mean_force":0.12445,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.45234,-0.00018,0.04864]},{"body_a":"world","body_b":"grasp_target","contact_count":1720.0,"contact_point_centroid":[0.46286,-7e-05,-0.00192],"force_p95":0.13411,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12291,"phase_index":0.0,"phase_name":"approach_to_object","phase_type":"approach","tcp_position_centroid":[0.48115,-5e-05,0.23067]},{"body_a":"world","body_b":"grasp_target","contact_count":1476.0,"contact_point_centroid":[0.46286,-7e-05,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.45963,-0.0001,0.10719]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4870.0,"contact_point_centroid":[0.45117,0.019,0.04914],"force_p95":0.06698,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0817,"mean_force":0.0448,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.45128,-0.00019,0.0476]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4857.0,"contact_point_centroid":[0.45027,-0.01939,0.04845],"force_p95":0.06666,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0805,"mean_force":0.04494,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.45128,-0.00019,0.0476]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1920.0,"contact_point_centroid":[0.59845,0.14852,0.12537],"force_p95":0.01164,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01474,"mean_force":0.01056,"phase_index":6.0,"phase_name":"hold_grasp","phase_type":"grasp","tcp_position_centroid":[0.59785,0.14849,0.12318]}],"total_contact_groups":15},"final_pose_error":0.01459,"key_states":{"actual_goal_position":[0.61015,0.15287,0.12219],"final_object_position":[0.58936,0.12542,0.02602],"final_tcp_position":[0.6045,0.15021,0.13537],"realised_goal_position":[0.61015,0.15287,0.12219],"realised_object_initial_position":[0.46286,-7e-05,0.03]},"peak_contact_force":234.03316,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":431.0,"n_steps_budget":1000.0,"object_pos_end":[0.46286,-7e-05,0.02602],"object_pos_start":[0.46286,-7e-05,0.03],"object_to_goal_dist_end":0.2331,"object_to_goal_dist_start":0.23148,"object_z_max":0.03,"peak_contact_force":27.12826,"phase_name":"approach_to_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1720.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.46313,-8e-05,0.15992],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.1339,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":369.0,"n_steps_budget":1000.0,"object_pos_end":[0.46286,-7e-05,0.02602],"object_pos_start":[0.46286,-7e-05,0.02602],"object_to_goal_dist_end":0.2331,"object_to_goal_dist_start":0.2331,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1476.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.45872,-0.00011,0.05496],"tcp_start":[0.46313,-8e-05,0.15992],"tcp_to_object_dist_end":0.02924,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.46277,-0.00015,0.02591],"object_pos_start":[0.46286,-7e-05,0.02602],"object_to_goal_dist_end":0.23325,"object_to_goal_dist_start":0.2331,"object_z_max":0.02602,"peak_contact_force":0.12958,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11527.0,"raw_peak_contact_force":0.15221,"subtask_id":"grasp_1","tcp_end":[0.45125,-0.00019,0.04757],"tcp_start":[0.45872,-0.00011,0.05496],"tcp_to_object_dist_end":0.02453,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":35.0,"n_steps":939.0,"n_steps_budget":1000.0,"object_pos_end":[0.46244,0.00015,0.2083],"object_pos_start":[0.46277,-0.00015,0.02591],"object_to_goal_dist_end":0.22925,"object_to_goal_dist_start":0.23325,"object_z_max":0.20812,"peak_contact_force":0.08564,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":37122.0,"raw_peak_contact_force":0.38602,"tcp_end":[0.45921,-0.00017,0.23671],"tcp_start":[0.45125,-0.00019,0.04757],"tcp_to_object_dist_end":0.0286,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":19.0,"n_steps":658.0,"n_steps_budget":1000.0,"object_pos_end":[0.60261,0.14277,0.21916],"object_pos_start":[0.46244,0.00015,0.2083],"object_to_goal_dist_end":0.09778,"object_to_goal_dist_start":0.22925,"object_z_max":0.27546,"peak_contact_force":0.12971,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":14502.0,"raw_peak_contact_force":0.27637,"subtask_id":"transport_arc","tcp_end":[0.59883,0.14297,0.25471],"tcp_start":[0.45921,-0.00017,0.23671],"tcp_to_object_dist_end":0.03575,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":256.0,"n_steps_budget":1000.0,"object_pos_end":[0.59467,0.13223,0.0276],"object_pos_start":[0.60261,0.14277,0.21916],"object_to_goal_dist_end":0.09804,"object_to_goal_dist_start":0.09778,"object_z_max":0.21916,"peak_contact_force":234.03316,"phase_name":"place_at_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2061.0,"raw_peak_contact_force":1.79758,"tcp_end":[0.6045,0.15021,0.13537],"tcp_start":[0.59883,0.14297,0.25471],"tcp_to_object_dist_end":0.1097,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.58936,0.12542,0.02602],"object_pos_start":[0.59467,0.13223,0.0276],"object_to_goal_dist_end":0.10215,"object_to_goal_dist_start":0.09804,"object_z_max":0.0276,"peak_contact_force":0.12263,"phase_name":"hold_grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":3701.0,"raw_peak_contact_force":0.2356,"tcp_end":[0.59675,0.1482,0.12121],"tcp_start":[0.6045,0.15021,0.13537],"tcp_to_object_dist_end":0.09816,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```