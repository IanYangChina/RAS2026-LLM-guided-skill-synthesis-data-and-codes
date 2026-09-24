## Search State

- **Seed**: 9
- **Iteration**: 9 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 8 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | position_control | impedance_control | impedance_control | impedance_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 9 | 0.0458 | 0.36 | ❌ rejected |
| 7 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | position_control | position_control | position_control | impedance_control | impedance_control | impedance_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 8 | 0.0338 | 0.21 | ❌ rejected |
| 6 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | position_control | impedance_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 9 | 0.0520 | 0.39 | ❌ rejected |
| 5 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | position_control | position_control | position_control | impedance_control | impedance_control | impedance_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 8 | 0.2655 | 0.64 | ✅ accepted |
| 4 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | impedance_control | impedance_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 11 | -0.0794 | 0.37 | ❌ rejected |

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

## Current Skill (Q=0.046) — your mutation base

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

- **Composite score**: 0.046
- **task_score** (E): 0.364
- **fitness_score**: 0.646  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.600

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_to_object | 1.00 | 1.00 | 0.1488 |
| descend_to_grasp | 1.00 | 1.00 | 0.1031 |
| grasp | 1.00 | 1.00 | 0.0123 |
| lift_object | 0.67 | 1.00 | 0.1594 |
| transport_to_goal | 1.00 | 1.00 | 0.0728 |
| descend_to_place | 1.00 | 1.00 | 0.1082 |
| release_object | 1.00 | 1.00 | 0.0202 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_to_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.510, -0.015, 0.158) | (0.515, -0.017, 0.030)→(0.515, -0.017, 0.026) | 0.268→0.270 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_to_grasp | descend | 1.00 / step_budget | (0.510, -0.015, 0.158)→(0.510, -0.017, 0.054) | (0.515, -0.017, 0.026)→(0.515, -0.017, 0.026) | 0.270→0.270 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp | grasp | 1.00 / step_budget | (0.510, -0.017, 0.054)→(0.502, -0.017, 0.045) | (0.515, -0.017, 0.026)→(0.515, -0.017, 0.026) | 0.270→0.270 | 1.00 / 42.000 | 0.134 | 0.168 |
| lift_object | lift | 0.67 / step_budget | (0.502, -0.017, 0.045)→(0.506, -0.016, 0.205) | (0.515, -0.017, 0.026)→(0.509, -0.016, 0.176) | 0.270→0.234 | 1.00 / 35.333 | 0.083 | 0.390 |
| transport_to_goal | approach | 1.00 / step_budget | (0.577, 0.108, 0.258)→(0.607, 0.167, 0.284) | (0.509, -0.016, 0.176)→(0.599, 0.128, 0.098) | 0.234→0.138 | 1.00 / 11.333 | 0.121 | 1.599 |
| descend_to_place | descend | 1.00 / step_budget | (0.607, 0.167, 0.284)→(0.613, 0.179, 0.177) | (0.599, 0.128, 0.098)→(0.601, 0.133, 0.063) | 0.138→0.122 | 1.00 / 11.667 | 91002.180 | 0.156 |
| release_object | release | 1.00 / step_budget | (0.613, 0.179, 0.177)→(0.607, 0.177, 0.196) | (0.601, 0.133, 0.063)→(0.598, 0.132, 0.023) | 0.122→0.163 | 1.00 / 3.333 | 0.144 | 0.603 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.525
- phase_score: 0.370
- phase_breakdown.descend_1_score: 0.876
- phase_breakdown.grasp_1_score: 1.000
- phase_breakdown.transport_arc_score: 0.087
- phase_breakdown.approach_1_score: 0.074
- phase_breakdown.release_1_score: 0.540
- grasp_place_fitness: 0.725

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.725
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.525
- **Median Q (composite search score)**: 0.048
- **K-run variance**: 0.0043
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.391


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.39041,"average_solve_count":292.0,"average_success_count":292.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_to_object.speed":0.10395,"descend_to_grasp.speed":0.06652,"descend_to_place.speed":0.0366,"grasp.grip_force":12.82922,"lift_object.lift_height":0.20713,"lift_object.speed":0.04097,"release_object.release_duration":0.45892,"transport_to_goal.arc_height":0.18453,"transport_to_goal.speed":0.12445},"optimized_scores":{"best_composite_score":-0.03513,"best_fitness_score":0.56487,"best_task_score":0.20111},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":3191.0,"contact_point_centroid":[0.57152,0.08726,-0.00248],"force_p95":0.12647,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.40895,"mean_force":0.14198,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.59123,0.17439,0.34467]},{"body_a":"world","body_b":"grasp_target","contact_count":120.0,"contact_point_centroid":[0.53326,-0.02062,-0.00132],"force_p95":0.37699,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.40237,"mean_force":0.10579,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.52193,-0.0208,0.04554]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5995.0,"contact_point_centroid":[0.53371,0.00785,0.267],"force_p95":0.1162,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27646,"mean_force":0.07254,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.52987,-0.01094,0.26753]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":26983.0,"contact_point_centroid":[0.52714,-0.00162,0.1506],"force_p95":0.07431,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25218,"mean_force":0.05219,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.52663,-0.02075,0.14897]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":27884.0,"contact_point_centroid":[0.52717,-0.03986,0.14872],"force_p95":0.07327,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24874,"mean_force":0.05069,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.5265,-0.02075,0.14691]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6092.0,"contact_point_centroid":[0.53354,-0.03033,0.26642],"force_p95":0.11821,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23078,"mean_force":0.07095,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.52965,-0.01156,0.26665]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53703,-0.02125,-0.00205],"force_p95":0.13527,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.16889,"mean_force":0.12659,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.52431,-0.02085,0.04572]},{"body_a":"world","body_b":"grasp_target","contact_count":1908.0,"contact_point_centroid":[0.53702,-0.02132,-0.00193],"force_p95":0.13338,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12288,"phase_index":0.0,"phase_name":"approach_to_object","phase_type":"approach","tcp_position_centroid":[0.51384,-0.00954,0.22782]},{"body_a":"world","body_b":"grasp_target","contact_count":1324.0,"contact_point_centroid":[0.53702,-0.02132,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.52941,-0.02017,0.10501]},{"body_a":"world","body_b":"grasp_target","contact_count":1212.0,"contact_point_centroid":[0.57152,0.08723,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.60402,0.2174,0.27007]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.57152,0.08723,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.60266,0.22263,0.21527]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4963.0,"contact_point_centroid":[0.52349,-0.00165,0.04744],"force_p95":0.06579,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12183,"mean_force":0.04344,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.52311,-0.02082,0.04432]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4897.0,"contact_point_centroid":[0.52393,-0.04008,0.04612],"force_p95":0.06942,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08691,"mean_force":0.04507,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.52311,-0.02082,0.04432]},{"body_a":"left_finger","body_b":"right_finger","contact_count":3338.0,"contact_point_centroid":[0.59266,0.17735,0.34636],"force_p95":0.01106,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01615,"mean_force":0.01047,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.59218,0.17733,0.34408]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1301.0,"contact_point_centroid":[0.60471,0.21744,0.2722],"force_p95":0.01096,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01257,"mean_force":0.01039,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.60402,0.21741,0.26998]},{"body_a":"left_finger","body_b":"right_finger","contact_count":226.0,"contact_point_centroid":[0.60525,0.22366,0.21406],"force_p95":0.01085,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01089,"mean_force":0.00989,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.60482,0.22363,0.21185]}],"total_contact_groups":16},"final_pose_error":0.00995,"key_states":{"actual_goal_position":[0.61031,0.22775,0.20741],"final_object_position":[0.57152,0.08723,0.01602],"final_tcp_position":[0.6063,0.22412,0.21575],"realised_goal_position":[0.61031,0.22775,0.20741],"realised_object_initial_position":[0.53702,-0.02132,0.03]},"peak_contact_force":273006.29921,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":478.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.03],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31446,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_to_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1908.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.53013,-0.01943,0.15669],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.13086,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":331.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1324.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.53146,-0.02098,0.0542],"tcp_start":[0.53013,-0.01943,0.15669],"tcp_to_object_dist_end":0.02873,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53694,-0.02086,0.02581],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.3165,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.13475,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11660.0,"raw_peak_contact_force":0.16889,"subtask_id":"grasp_1","tcp_end":[0.52308,-0.02083,0.04429],"tcp_start":[0.53146,-0.02098,0.0542],"tcp_to_object_dist_end":0.0231,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":38.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53175,-0.02084,0.17859],"object_pos_start":[0.53694,-0.02086,0.02581],"object_to_goal_dist_end":0.2623,"object_to_goal_dist_start":0.3165,"object_z_max":0.18709,"peak_contact_force":0.07245,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":54987.0,"raw_peak_contact_force":0.40237,"tcp_end":[0.52885,-0.02071,0.20594],"tcp_start":[0.52308,-0.02083,0.04429],"tcp_to_object_dist_end":0.02751,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":966.0,"n_steps_budget":1000.0,"object_pos_end":[0.57152,0.08723,0.01602],"object_pos_start":[0.53175,-0.02084,0.17859],"object_to_goal_dist_end":0.24059,"object_to_goal_dist_start":0.2623,"object_z_max":0.30764,"peak_contact_force":0.12263,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":18616.0,"raw_peak_contact_force":2.40895,"subtask_id":"transport_arc","tcp_end":[0.60315,0.21183,0.32385],"tcp_start":[0.60211,0.20981,0.32573],"tcp_to_object_dist_end":0.33359,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":303.0,"n_steps_budget":1000.0,"object_pos_end":[0.57152,0.08723,0.01602],"object_pos_start":[0.57152,0.08723,0.01602],"object_to_goal_dist_end":0.24059,"object_to_goal_dist_start":0.24059,"object_z_max":0.01602,"peak_contact_force":273006.29921,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2513.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.6063,0.22412,0.21575],"tcp_start":[0.60315,0.21183,0.32385],"tcp_to_object_dist_end":0.24462,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.57152,0.08723,0.01602],"object_pos_start":[0.57152,0.08723,0.01602],"object_to_goal_dist_end":0.24059,"object_to_goal_dist_start":0.24059,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1026.0,"raw_peak_contact_force":0.12263,"subtask_id":"release_1","tcp_end":[0.60144,0.22204,0.23463],"tcp_start":[0.6063,0.22412,0.21575],"tcp_to_object_dist_end":0.25857,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.09288,"average_solve_count":323.0,"average_success_count":323.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_to_object.speed":0.13797,"descend_to_grasp.speed":0.06434,"descend_to_place.speed":0.05026,"grasp.grip_force":21.49476,"lift_object.lift_height":0.23992,"lift_object.speed":0.03193,"release_object.release_duration":0.49212,"transport_to_goal.arc_height":0.05134,"transport_to_goal.speed":0.03139},"optimized_scores":{"best_composite_score":0.04785,"best_fitness_score":0.64785,"best_task_score":0.36673},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":159.0,"contact_point_centroid":[0.61846,0.16054,-0.00783],"force_p95":1.24161,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.56354,"mean_force":0.44339,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.62164,0.15954,0.19294]},{"body_a":"world","body_b":"grasp_target","contact_count":124.0,"contact_point_centroid":[0.54163,-0.02813,-0.00135],"force_p95":0.36093,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.3918,"mean_force":0.10777,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.53017,-0.02845,0.04509]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":18792.0,"contact_point_centroid":[0.57847,0.04202,0.26864],"force_p95":0.11454,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27356,"mean_force":0.0607,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.57761,0.06065,0.26969]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":16164.0,"contact_point_centroid":[0.57897,0.07934,0.2685],"force_p95":0.12455,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27352,"mean_force":0.07052,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.57753,0.06049,0.26961]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":592.0,"contact_point_centroid":[0.62948,0.14231,0.17505],"force_p95":0.12107,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27228,"mean_force":0.08444,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.62531,0.16072,0.17967]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":600.0,"contact_point_centroid":[0.62956,0.17912,0.17445],"force_p95":0.11764,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26499,"mean_force":0.08415,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.6253,0.16072,0.17967]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":25910.0,"contact_point_centroid":[0.53435,-0.00923,0.14814],"force_p95":0.07629,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26217,"mean_force":0.05397,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.53365,-0.02836,0.14627]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":28004.0,"contact_point_centroid":[0.53448,-0.04744,0.14959],"force_p95":0.07307,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25263,"mean_force":0.05041,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.53375,-0.02836,0.14794]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2697.0,"contact_point_centroid":[0.62733,0.13543,0.23026],"force_p95":0.12964,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22115,"mean_force":0.09979,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.62295,0.15369,0.23418]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2628.0,"contact_point_centroid":[0.62743,0.17183,0.23084],"force_p95":0.12511,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20273,"mean_force":0.10158,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.62288,0.15357,0.23504]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.54562,-0.0291,-0.00207],"force_p95":0.14194,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.18404,"mean_force":0.12792,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.53265,-0.02853,0.04537]},{"body_a":"world","body_b":"grasp_target","contact_count":1948.0,"contact_point_centroid":[0.5456,-0.02923,-0.00193],"force_p95":0.13308,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12288,"phase_index":0.0,"phase_name":"approach_to_object","phase_type":"approach","tcp_position_centroid":[0.51778,-0.01317,0.22725]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4105.0,"contact_point_centroid":[0.53232,-0.00929,0.04666],"force_p95":0.07809,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13402,"mean_force":0.05184,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.53143,-0.0285,0.04393]},{"body_a":"world","body_b":"grasp_target","contact_count":1308.0,"contact_point_centroid":[0.5456,-0.02923,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.53757,-0.02769,0.10463]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4914.0,"contact_point_centroid":[0.53232,-0.04759,0.04571],"force_p95":0.07027,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07744,"mean_force":0.04466,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.53143,-0.0285,0.04393]}],"total_contact_groups":15},"final_pose_error":0.00998,"key_states":{"actual_goal_position":[0.63284,0.16493,0.17692],"final_object_position":[0.62176,0.15879,0.02699],"final_tcp_position":[0.62738,0.16119,0.18439],"realised_goal_position":[0.63284,0.16493,0.17692],"realised_object_initial_position":[0.5456,-0.02923,0.03]},"peak_contact_force":1.56354,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":488.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.03],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.25864,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_to_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1948.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.53804,-0.02674,0.15595],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.13017,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":327.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1308.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.53989,-0.02875,0.05413],"tcp_start":[0.53804,-0.02674,0.15595],"tcp_to_object_dist_end":0.02869,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54552,-0.02855,0.02575],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.2606,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.13862,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10819.0,"raw_peak_contact_force":0.18404,"subtask_id":"grasp_1","tcp_end":[0.5314,-0.02849,0.04389],"tcp_start":[0.53989,-0.02875,0.05413],"tcp_to_object_dist_end":0.02299,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":38.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53813,-0.02831,0.1747],"object_pos_start":[0.54552,-0.02855,0.02575],"object_to_goal_dist_end":0.21521,"object_to_goal_dist_start":0.2606,"object_z_max":0.18333,"peak_contact_force":0.07417,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":54038.0,"raw_peak_contact_force":0.3918,"tcp_end":[0.53513,-0.0283,0.20179],"tcp_start":[0.5314,-0.02849,0.04389],"tcp_to_object_dist_end":0.02725,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":18.0,"n_steps":794.0,"n_steps_budget":1000.0,"object_pos_end":[0.62458,0.14675,0.25053],"object_pos_start":[0.53813,-0.02831,0.1747],"object_to_goal_dist_end":0.07627,"object_to_goal_dist_start":0.21521,"object_z_max":0.27114,"peak_contact_force":0.11546,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":34956.0,"raw_peak_contact_force":0.27356,"subtask_id":"transport_arc","tcp_end":[0.62036,0.14736,0.28511],"tcp_start":[0.53513,-0.0283,0.20179],"tcp_to_object_dist_end":0.03483,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":18.0,"n_steps":292.0,"n_steps_budget":1000.0,"object_pos_end":[0.63182,0.16065,0.14715],"object_pos_start":[0.62458,0.14675,0.25053],"object_to_goal_dist_end":0.0301,"object_to_goal_dist_start":0.07627,"object_z_max":0.25053,"peak_contact_force":0.11837,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":5325.0,"raw_peak_contact_force":0.22115,"tcp_end":[0.62738,0.16119,0.18439],"tcp_start":[0.62036,0.14736,0.28511],"tcp_to_object_dist_end":0.03751,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.62176,0.15879,0.02699],"object_pos_start":[0.63182,0.16065,0.14715],"object_to_goal_dist_end":0.15047,"object_to_goal_dist_start":0.0301,"object_z_max":0.14715,"peak_contact_force":0.18789,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1351.0,"raw_peak_contact_force":1.56354,"subtask_id":"release_1","tcp_end":[0.62159,0.15953,0.20315],"tcp_start":[0.62738,0.16119,0.18439],"tcp_to_object_dist_end":0.17616,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.73412,"average_solve_count":425.0,"average_success_count":425.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_to_object.speed":0.06112,"descend_to_grasp.speed":0.02006,"descend_to_place.speed":0.05767,"grasp.grip_force":10.11942,"lift_object.lift_height":0.19945,"lift_object.speed":0.03942,"release_object.release_duration":0.27745,"transport_to_goal.arc_height":0.14753,"transport_to_goal.speed":0.04394},"optimized_scores":{"best_composite_score":0.12465,"best_fitness_score":0.72465,"best_task_score":0.52512},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":967.0,"contact_point_centroid":[0.60218,0.15596,-0.00374],"force_p95":0.66714,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.11299,"mean_force":0.20978,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.59471,0.14139,0.24543]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8379.0,"contact_point_centroid":[0.50461,0.03252,0.26537],"force_p95":0.14459,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.46136,"mean_force":0.08835,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.50529,0.05104,0.268]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":9587.0,"contact_point_centroid":[0.5032,0.06693,0.26279],"force_p95":0.129,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.4376,"mean_force":0.08006,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.50274,0.04854,0.26538]},{"body_a":"world","body_b":"grasp_target","contact_count":99.0,"contact_point_centroid":[0.4591,-0.00032,-0.00133],"force_p95":0.35457,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.37595,"mean_force":0.11245,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.45025,-0.00021,0.04877]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":24101.0,"contact_point_centroid":[0.45356,0.0187,0.15382],"force_p95":0.07664,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25934,"mean_force":0.05163,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.45411,-0.0002,0.15333]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":20481.0,"contact_point_centroid":[0.4527,-0.01934,0.15379],"force_p95":0.0934,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24832,"mean_force":0.06107,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.45412,-0.0002,0.1533]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.46285,-8e-05,-0.00202],"force_p95":0.12952,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.15223,"mean_force":0.12446,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.45227,-0.00018,0.04875]},{"body_a":"world","body_b":"grasp_target","contact_count":1780.0,"contact_point_centroid":[0.46286,-7e-05,-0.00192],"force_p95":0.1336,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.1229,"phase_index":0.0,"phase_name":"approach_to_object","phase_type":"approach","tcp_position_centroid":[0.48111,-5e-05,0.23058]},{"body_a":"world","body_b":"grasp_target","contact_count":1348.0,"contact_point_centroid":[0.60112,0.15065,-0.00199],"force_p95":0.12311,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12506,"mean_force":0.12263,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.59906,0.14612,0.18594]},{"body_a":"world","body_b":"grasp_target","contact_count":1580.0,"contact_point_centroid":[0.46286,-7e-05,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.45944,-0.0001,0.10752]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.60112,0.15065,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.59912,0.14905,0.1301]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4870.0,"contact_point_centroid":[0.45111,0.01897,0.04925],"force_p95":0.06673,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08169,"mean_force":0.04473,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.45121,-0.00019,0.04771]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4639.0,"contact_point_centroid":[0.45057,-0.01938,0.04862],"force_p95":0.06876,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0805,"mean_force":0.04695,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.45121,-0.00019,0.04771]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1112.0,"contact_point_centroid":[0.5952,0.14139,0.24762],"force_p95":0.01225,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01607,"mean_force":0.01062,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.5947,0.14138,0.2454]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1448.0,"contact_point_centroid":[0.59952,0.14613,0.18842],"force_p95":0.01096,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0127,"mean_force":0.01038,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.59904,0.14611,0.18613]},{"body_a":"left_finger","body_b":"right_finger","contact_count":215.0,"contact_point_centroid":[0.60257,0.14994,0.12827],"force_p95":0.01102,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01103,"mean_force":0.01034,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.60213,0.14991,0.1261]}],"total_contact_groups":16},"final_pose_error":0.00998,"key_states":{"actual_goal_position":[0.61015,0.15287,0.12219],"final_object_position":[0.60112,0.15065,0.02602],"final_tcp_position":[0.60413,0.15039,0.12976],"realised_goal_position":[0.61015,0.15287,0.12219],"realised_object_initial_position":[0.46286,-7e-05,0.03]},"peak_contact_force":2.11299,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":446.0,"n_steps_budget":1000.0,"object_pos_end":[0.46286,-7e-05,0.02602],"object_pos_start":[0.46286,-7e-05,0.03],"object_to_goal_dist_end":0.2331,"object_to_goal_dist_start":0.23148,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_to_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1780.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.46298,-8e-05,0.15993],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.13391,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":395.0,"n_steps_budget":1000.0,"object_pos_end":[0.46286,-7e-05,0.02602],"object_pos_start":[0.46286,-7e-05,0.02602],"object_to_goal_dist_end":0.2331,"object_to_goal_dist_start":0.2331,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1580.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.45863,-0.00011,0.05506],"tcp_start":[0.46298,-8e-05,0.15993],"tcp_to_object_dist_end":0.02935,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.46277,-0.00016,0.02591],"object_pos_start":[0.46286,-7e-05,0.02602],"object_to_goal_dist_end":0.23325,"object_to_goal_dist_start":0.2331,"object_z_max":0.02602,"peak_contact_force":0.12949,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11309.0,"raw_peak_contact_force":0.15223,"subtask_id":"grasp_1","tcp_end":[0.45118,-0.00019,0.04768],"tcp_start":[0.45863,-0.00011,0.05506],"tcp_to_object_dist_end":0.02467,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":30.0,"n_steps":825.0,"n_steps_budget":1000.0,"object_pos_end":[0.4559,0.00047,0.17584],"object_pos_start":[0.46277,-0.00016,0.02591],"object_to_goal_dist_end":0.22337,"object_to_goal_dist_start":0.23325,"object_z_max":0.18386,"peak_contact_force":0.10141,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":44681.0,"raw_peak_contact_force":0.37595,"tcp_end":[0.45546,-0.0002,0.20612],"tcp_start":[0.45118,-0.00019,0.04768],"tcp_to_object_dist_end":0.03029,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":804.0,"n_steps_budget":1000.0,"object_pos_end":[0.60112,0.15081,0.02602],"object_pos_start":[0.4559,0.00047,0.17584],"object_to_goal_dist_end":0.09661,"object_to_goal_dist_start":0.22337,"object_z_max":0.26612,"peak_contact_force":0.12518,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":20045.0,"raw_peak_contact_force":2.11299,"subtask_id":"transport_arc","tcp_end":[0.59642,0.14267,0.24309],"tcp_start":[0.59466,0.14135,0.24545],"tcp_to_object_dist_end":0.21727,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":337.0,"n_steps_budget":1000.0,"object_pos_end":[0.60112,0.15065,0.02602],"object_pos_start":[0.60114,0.15082,0.02602],"object_to_goal_dist_end":0.09662,"object_to_goal_dist_start":0.09661,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2796.0,"raw_peak_contact_force":0.12506,"tcp_end":[0.60413,0.15039,0.12976],"tcp_start":[0.59642,0.14267,0.24309],"tcp_to_object_dist_end":0.10378,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.60112,0.15065,0.02602],"object_pos_start":[0.60112,0.15065,0.02602],"object_to_goal_dist_end":0.09662,"object_to_goal_dist_start":0.09662,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1015.0,"raw_peak_contact_force":0.12263,"subtask_id":"release_1","tcp_end":[0.5973,0.14853,0.14982],"tcp_start":[0.60413,0.15039,0.12976],"tcp_to_object_dist_end":0.12388,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```