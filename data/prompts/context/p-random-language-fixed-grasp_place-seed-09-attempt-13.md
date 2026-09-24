## Search State

- **Seed**: 9
- **Iteration**: 14 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 13 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | impedance_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 8 | 0.0757 | 0.38 | ❌ rejected |
| 12 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | impedance_control | impedance_control | impedance_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 10 | -0.0359 | 0.36 | ❌ rejected |
| 11 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | position_control | position_control | position_control | impedance_control | impedance_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 8 | 0.2955 | 0.70 | ❌ rejected |
| 10 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | position_control | position_control | position_control | impedance_control | impedance_control | impedance_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 8 | 0.2587 | 0.63 | ❌ rejected |
| 9 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | position_control | position_control | position_control | impedance_control | impedance_control | impedance_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 8 | 0.3059 | 0.72 | ✅ accepted |

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

## Current Skill (Q=0.076) — your mutation base

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

- **Composite score**: 0.076
- **task_score** (E): 0.384
- **fitness_score**: 0.656  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.580

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_to_object | 1.00 | 1.00 | 0.1489 |
| descend_to_grasp | 1.00 | 1.00 | 0.1031 |
| grasp | 1.00 | 1.00 | 0.0123 |
| lift_object | 1.00 | 1.00 | 0.1180 |
| transport_to_goal | 0.33 | 1.00 | 0.1886 |
| descend_to_place | 1.00 | 1.00 | 0.0716 |
| release_object | 1.00 | 1.00 | 0.0201 |
| retract_after_place | 1.00 | 1.00 | 0.0779 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_to_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.510, -0.015, 0.157) | (0.515, -0.017, 0.030)→(0.515, -0.017, 0.026) | 0.268→0.270 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_to_grasp | descend | 1.00 / step_budget | (0.510, -0.015, 0.157)→(0.510, -0.017, 0.054) | (0.515, -0.017, 0.026)→(0.515, -0.017, 0.026) | 0.270→0.270 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp | grasp | 1.00 / step_budget | (0.510, -0.017, 0.054)→(0.502, -0.017, 0.045) | (0.515, -0.017, 0.026)→(0.515, -0.017, 0.026) | 0.270→0.270 | 1.00 / 42.000 | 0.134 | 0.168 |
| lift_object | lift | 1.00 / step_budget | (0.502, -0.017, 0.045)→(0.510, -0.016, 0.163) | (0.515, -0.017, 0.026)→(0.522, -0.016, 0.139) | 0.270→0.232 | 1.00 / 30.667 | 0.093 | 0.408 |
| transport_to_goal | approach | 0.33 / step_budget | (0.510, -0.016, 0.163)→(0.593, 0.126, 0.242) | (0.522, -0.016, 0.139)→(0.597, 0.126, 0.211) | 0.232→0.088 | 1.00 / 23.667 | 0.097 | 0.157 |
| descend_to_place | descend | 1.00 / step_budget | (0.593, 0.126, 0.242)→(0.610, 0.170, 0.204) | (0.597, 0.126, 0.211)→(0.615, 0.170, 0.171) | 0.088→0.018 | 1.00 / 18.667 | 0.137 | 0.230 |
| release_object | release | 1.00 / step_budget | (0.610, 0.170, 0.204)→(0.604, 0.169, 0.223) | (0.615, 0.170, 0.171)→(0.605, 0.168, 0.016) | 0.018→0.154 | 1.00 / 3.333 | 0.299 | 1.638 |
| retract_after_place | retract | 1.00 / step_budget | (0.604, 0.169, 0.223)→(0.614, 0.180, 0.299) | (0.605, 0.168, 0.016)→(0.597, 0.174, 0.023) | 0.154→0.149 | 1.00 / 4.000 | 0.123 | 0.294 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.518
- phase_score: 0.359
- phase_breakdown.descend_1_score: 0.878
- phase_breakdown.grasp_1_score: 1.000
- phase_breakdown.transport_arc_score: 0.110
- phase_breakdown.approach_1_score: 0.075
- phase_breakdown.release_1_score: 0.376
- grasp_place_fitness: 0.721

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.721
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.518
- **Median Q (composite search score)**: 0.062
- **K-run variance**: 0.0024
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.386


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.13415,"average_solve_count":246.0,"average_success_count":246.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_to_object.speed":0.12815,"descend_to_grasp.speed":0.05181,"descend_to_place.speed":0.05562,"lift_object.lift_height":0.13181,"lift_object.speed":0.11849,"release_object.release_duration":0.94972,"retract_after_place.speed":0.05751,"transport_to_goal.speed":0.03171},"optimized_scores":{"best_composite_score":0.02372,"best_fitness_score":0.60372,"best_task_score":0.2789},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":91.0,"contact_point_centroid":[0.5984,0.20048,-0.01159],"force_p95":1.79495,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.93893,"mean_force":0.87147,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.59769,0.20999,0.24181]},{"body_a":"world","body_b":"grasp_target","contact_count":83.0,"contact_point_centroid":[0.53549,-0.02077,-0.00132],"force_p95":0.38066,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.42089,"mean_force":0.08184,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.5221,-0.0208,0.04572]},{"body_a":"world","body_b":"grasp_target","contact_count":1602.0,"contact_point_centroid":[0.60488,0.22195,-0.00207],"force_p95":0.14692,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.37609,"mean_force":0.12325,"phase_index":7.0,"phase_name":"retract_after_place","phase_type":"retract","tcp_position_centroid":[0.60197,0.21771,0.29345]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":487.0,"contact_point_centroid":[0.60633,0.22981,0.22247],"force_p95":0.16116,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29829,"mean_force":0.10146,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.60063,0.21147,0.22533]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":744.0,"contact_point_centroid":[0.60624,0.19339,0.22278],"force_p95":0.13143,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28146,"mean_force":0.07593,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.60058,0.21144,0.22522]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4899.0,"contact_point_centroid":[0.52743,-0.00184,0.08733],"force_p95":0.10942,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.278,"mean_force":0.0694,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.52494,-0.02078,0.08489]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5095.0,"contact_point_centroid":[0.52752,-0.03967,0.086],"force_p95":0.10715,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26916,"mean_force":0.06744,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.52486,-0.02077,0.08426]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3430.0,"contact_point_centroid":[0.59307,0.14753,0.23177],"force_p95":0.11726,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17885,"mean_force":0.07548,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.58702,0.16571,0.23264]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53703,-0.02125,-0.00205],"force_p95":0.13521,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.16906,"mean_force":0.12655,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.52427,-0.02084,0.04573]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":12839.0,"contact_point_centroid":[0.5566,0.07043,0.18845],"force_p95":0.09393,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16696,"mean_force":0.0733,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.55111,0.05171,0.1875]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2800.0,"contact_point_centroid":[0.5926,0.18257,0.23221],"force_p95":0.13612,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16276,"mean_force":0.0923,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.58645,0.16398,0.23281]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":12963.0,"contact_point_centroid":[0.55652,0.0328,0.18836],"force_p95":0.094,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1588,"mean_force":0.07279,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.55104,0.05151,0.18734]},{"body_a":"world","body_b":"grasp_target","contact_count":1868.0,"contact_point_centroid":[0.53702,-0.02132,-0.00193],"force_p95":0.13354,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12289,"phase_index":0.0,"phase_name":"approach_to_object","phase_type":"approach","tcp_position_centroid":[0.51375,-0.00951,0.22809]},{"body_a":"world","body_b":"grasp_target","contact_count":1368.0,"contact_point_centroid":[0.53702,-0.02132,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.52932,-0.02015,0.10506]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5021.0,"contact_point_centroid":[0.52345,-0.00165,0.04746],"force_p95":0.06567,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.098,"mean_force":0.04302,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.52307,-0.02082,0.04433]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4897.0,"contact_point_centroid":[0.5239,-0.04008,0.04613],"force_p95":0.06939,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08706,"mean_force":0.04508,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.52307,-0.02082,0.04433]}],"total_contact_groups":16},"final_pose_error":0.01996,"key_states":{"actual_goal_position":[0.61031,0.22775,0.20741],"final_object_position":[0.60511,0.22247,0.01602],"final_tcp_position":[0.60749,0.22518,0.33782],"realised_goal_position":[0.61031,0.22775,0.20741],"realised_object_initial_position":[0.53702,-0.02132,0.03]},"peak_contact_force":1.93893,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":468.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.03],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31446,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_to_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1868.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.53004,-0.01941,0.15685],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.13103,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":342.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1368.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.53141,-0.02098,0.05419],"tcp_start":[0.53004,-0.01941,0.15685],"tcp_to_object_dist_end":0.02873,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53694,-0.0209,0.02581],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31653,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.135,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11718.0,"raw_peak_contact_force":0.16906,"subtask_id":"grasp_1","tcp_end":[0.52304,-0.02082,0.0443],"tcp_start":[0.53141,-0.02098,0.05419],"tcp_to_object_dist_end":0.02313,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":321.0,"n_steps_budget":630.0,"object_pos_end":[0.54688,-0.02082,0.11594],"object_pos_start":[0.53694,-0.0209,0.02581],"object_to_goal_dist_end":0.27236,"object_to_goal_dist_start":0.31653,"object_z_max":0.1157,"peak_contact_force":0.10601,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":10077.0,"raw_peak_contact_force":0.42089,"tcp_end":[0.5314,-0.0208,0.13852],"tcp_start":[0.52304,-0.02082,0.0443],"tcp_to_object_dist_end":0.02738,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":24.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.58009,0.12223,0.20977],"object_pos_start":[0.54688,-0.02082,0.11594],"object_to_goal_dist_end":0.10979,"object_to_goal_dist_start":0.27236,"object_z_max":0.20968,"peak_contact_force":0.09403,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":25802.0,"raw_peak_contact_force":0.16696,"subtask_id":"transport_arc","tcp_end":[0.57399,0.12232,0.24029],"tcp_start":[0.5314,-0.0208,0.13852],"tcp_to_object_dist_end":0.03112,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":17.0,"n_steps":278.0,"n_steps_budget":1000.0,"object_pos_end":[0.60788,0.21078,0.19606],"object_pos_start":[0.58009,0.12223,0.20977],"object_to_goal_dist_end":0.02057,"object_to_goal_dist_start":0.10979,"object_z_max":0.20977,"peak_contact_force":0.13599,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":6230.0,"raw_peak_contact_force":0.17885,"subtask_id":"release_1","tcp_end":[0.60229,0.21137,0.22928],"tcp_start":[0.57399,0.12232,0.24029],"tcp_to_object_dist_end":0.0337,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.60601,0.21202,0.00697],"object_pos_start":[0.60788,0.21078,0.19606],"object_to_goal_dist_end":0.20111,"object_to_goal_dist_start":0.02057,"object_z_max":0.19606,"peak_contact_force":0.40414,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1322.0,"raw_peak_contact_force":1.93893,"tcp_end":[0.59767,0.20998,0.24893],"tcp_start":[0.60229,0.21137,0.22928],"tcp_to_object_dist_end":0.24212,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":407.0,"n_steps_budget":1000.0,"object_pos_end":[0.60511,0.22247,0.01602],"object_pos_start":[0.60601,0.21202,0.00697],"object_to_goal_dist_end":0.19154,"object_to_goal_dist_start":0.20111,"object_z_max":0.01713,"peak_contact_force":0.12263,"phase_name":"retract_after_place","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1602.0,"raw_peak_contact_force":0.37609,"tcp_end":[0.60749,0.22518,0.33782],"tcp_start":[0.59767,0.20998,0.24893],"tcp_to_object_dist_end":0.32182,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.35206,"average_solve_count":267.0,"average_success_count":267.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_to_object.speed":0.08403,"descend_to_grasp.speed":0.06568,"descend_to_place.speed":0.07439,"lift_object.lift_height":0.16178,"lift_object.speed":0.06241,"release_object.release_duration":0.83047,"retract_after_place.speed":0.06697,"transport_to_goal.speed":0.03562},"optimized_scores":{"best_composite_score":0.06238,"best_fitness_score":0.64238,"best_task_score":0.35535},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":125.0,"contact_point_centroid":[0.60796,0.14947,-0.00975],"force_p95":1.42213,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.72388,"mean_force":0.57613,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.61689,0.14805,0.22428]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":654.0,"contact_point_centroid":[0.62505,0.16798,0.20543],"force_p95":0.2241,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.53362,"mean_force":0.10288,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.62003,0.14917,0.20648]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":818.0,"contact_point_centroid":[0.62581,0.13111,0.20552],"force_p95":0.17148,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.48272,"mean_force":0.0808,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.62006,0.14919,0.20654]},{"body_a":"world","body_b":"grasp_target","contact_count":90.0,"contact_point_centroid":[0.54343,-0.02834,-0.00141],"force_p95":0.34734,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.42024,"mean_force":0.08946,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.53039,-0.02846,0.04492]},{"body_a":"world","body_b":"grasp_target","contact_count":1309.0,"contact_point_centroid":[0.60096,0.14995,-0.00216],"force_p95":0.21338,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.3482,"mean_force":0.12562,"phase_index":7.0,"phase_name":"retract_after_place","phase_type":"retract","tcp_position_centroid":[0.62259,0.15573,0.27057]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":7689.0,"contact_point_centroid":[0.53596,-0.00939,0.10493],"force_p95":0.09769,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2873,"mean_force":0.06408,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.53382,-0.02839,0.10285]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8508.0,"contact_point_centroid":[0.53557,-0.04734,0.10375],"force_p95":0.09815,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2758,"mean_force":0.05969,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.53375,-0.02839,0.10204]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1551.0,"contact_point_centroid":[0.61807,0.10978,0.23173],"force_p95":0.12963,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2596,"mean_force":0.08368,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.61231,0.12806,0.23235]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1405.0,"contact_point_centroid":[0.61742,0.1456,0.23289],"force_p95":0.14943,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22884,"mean_force":0.0943,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.61181,0.12696,0.23351]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.54562,-0.0291,-0.00207],"force_p95":0.14185,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.18391,"mean_force":0.1279,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.53265,-0.02854,0.04518]},{"body_a":"world","body_b":"grasp_target","contact_count":2052.0,"contact_point_centroid":[0.5456,-0.02923,-0.00193],"force_p95":0.13256,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12286,"phase_index":0.0,"phase_name":"approach_to_object","phase_type":"approach","tcp_position_centroid":[0.51778,-0.01318,0.22718]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4105.0,"contact_point_centroid":[0.53232,-0.00929,0.04646],"force_p95":0.07808,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13381,"mean_force":0.05184,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.53143,-0.0285,0.04373]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":13567.0,"contact_point_centroid":[0.57619,0.06261,0.20952],"force_p95":0.10084,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12325,"mean_force":0.06901,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.57193,0.04388,0.20973]},{"body_a":"world","body_b":"grasp_target","contact_count":1308.0,"contact_point_centroid":[0.5456,-0.02923,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.53757,-0.02771,0.10442]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":14343.0,"contact_point_centroid":[0.57538,0.02374,0.20885],"force_p95":0.0933,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12236,"mean_force":0.06614,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.57123,0.0424,0.20879]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4914.0,"contact_point_centroid":[0.53232,-0.04759,0.04551],"force_p95":0.07026,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07749,"mean_force":0.04465,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.53143,-0.0285,0.04373]}],"total_contact_groups":16},"final_pose_error":0.01987,"key_states":{"actual_goal_position":[0.63284,0.16493,0.17692],"final_object_position":[0.59966,0.15028,0.02602],"final_tcp_position":[0.62908,0.16241,0.30757],"realised_goal_position":[0.63284,0.16493,0.17692],"realised_object_initial_position":[0.5456,-0.02923,0.03]},"peak_contact_force":1.72388,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":514.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.03],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.25864,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_to_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2052.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.53804,-0.02677,0.15578],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.13,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":327.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1308.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.53988,-0.02876,0.05393],"tcp_start":[0.53804,-0.02677,0.15578],"tcp_to_object_dist_end":0.02849,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54552,-0.02856,0.02576],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.2606,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.13855,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10819.0,"raw_peak_contact_force":0.18391,"subtask_id":"grasp_1","tcp_end":[0.5314,-0.0285,0.04369],"tcp_start":[0.53988,-0.02876,0.05393],"tcp_to_object_dist_end":0.02283,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":30.0,"n_steps":464.0,"n_steps_budget":1000.0,"object_pos_end":[0.55334,-0.02837,0.14547],"object_pos_start":[0.54552,-0.02856,0.02576],"object_to_goal_dist_end":0.21136,"object_to_goal_dist_start":0.2606,"object_z_max":0.14523,"peak_contact_force":0.09689,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":16287.0,"raw_peak_contact_force":0.42024,"tcp_end":[0.54047,-0.02842,0.1683],"tcp_start":[0.5314,-0.0285,0.04369],"tcp_to_object_dist_end":0.0262,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":24.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.60963,0.10989,0.22225],"object_pos_start":[0.55334,-0.02837,0.14547],"object_to_goal_dist_end":0.07499,"object_to_goal_dist_start":0.21136,"object_z_max":0.22217,"peak_contact_force":0.09577,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":27910.0,"raw_peak_contact_force":0.12325,"subtask_id":"transport_arc","tcp_end":[0.60403,0.11009,0.25268],"tcp_start":[0.54047,-0.02842,0.1683],"tcp_to_object_dist_end":0.03094,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":20.0,"n_steps":131.0,"n_steps_budget":1000.0,"object_pos_end":[0.62784,0.14849,0.17983],"object_pos_start":[0.60963,0.10989,0.22225],"object_to_goal_dist_end":0.01743,"object_to_goal_dist_start":0.07499,"object_z_max":0.22225,"peak_contact_force":0.13797,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2956.0,"raw_peak_contact_force":0.2596,"subtask_id":"release_1","tcp_end":[0.62225,0.14904,0.21152],"tcp_start":[0.60403,0.11009,0.25268],"tcp_to_object_dist_end":0.03218,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.61386,0.14403,0.01668],"object_pos_start":[0.62784,0.14849,0.17983],"object_to_goal_dist_end":0.16271,"object_to_goal_dist_start":0.01743,"object_z_max":0.17983,"peak_contact_force":0.35945,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1597.0,"raw_peak_contact_force":1.72388,"tcp_end":[0.61687,0.14804,0.23052],"tcp_start":[0.62225,0.14904,0.21152],"tcp_to_object_dist_end":0.2139,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":348.0,"n_steps_budget":930.0,"object_pos_end":[0.59966,0.15028,0.02602],"object_pos_start":[0.61386,0.14403,0.01668],"object_to_goal_dist_end":0.1552,"object_to_goal_dist_start":0.16271,"object_z_max":0.02806,"peak_contact_force":0.12268,"phase_name":"retract_after_place","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1309.0,"raw_peak_contact_force":0.3482,"tcp_end":[0.62908,0.16241,0.30757],"tcp_start":[0.61687,0.14804,0.23052],"tcp_to_object_dist_end":0.28334,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.22426,"average_solve_count":272.0,"average_success_count":272.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_to_object.speed":0.13057,"descend_to_grasp.speed":0.04789,"descend_to_place.speed":0.0296,"lift_object.lift_height":0.17533,"lift_object.speed":0.05457,"release_object.release_duration":1.1913,"retract_after_place.speed":0.06674,"transport_to_goal.speed":0.07909},"optimized_scores":{"best_composite_score":0.14094,"best_fitness_score":0.72094,"best_task_score":0.51753},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":212.0,"contact_point_centroid":[0.58823,0.14997,-0.00586],"force_p95":1.15009,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.2507,"mean_force":0.31427,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.59803,0.1482,0.18186]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":687.0,"contact_point_centroid":[0.60326,0.13091,0.16181],"force_p95":0.29917,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.38923,"mean_force":0.10079,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.60162,0.14928,0.16506]},{"body_a":"world","body_b":"grasp_target","contact_count":79.0,"contact_point_centroid":[0.46057,-0.00034,-0.00137],"force_p95":0.34228,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.383,"mean_force":0.1031,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.45044,-0.00021,0.04879]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":761.0,"contact_point_centroid":[0.60373,0.1676,0.16071],"force_p95":0.26241,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.36154,"mean_force":0.09399,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.6016,0.14927,0.16502]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8997.0,"contact_point_centroid":[0.45313,0.01882,0.11499],"force_p95":0.08002,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26291,"mean_force":0.055,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.45325,-0.0002,0.114]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1231.0,"contact_point_centroid":[0.6034,0.12961,0.20243],"force_p95":0.1259,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25074,"mean_force":0.09103,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.60226,0.14792,0.20512]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8044.0,"contact_point_centroid":[0.45243,-0.01937,0.11702],"force_p95":0.08629,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2507,"mean_force":0.0597,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.45339,-0.0002,0.11587]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1271.0,"contact_point_centroid":[0.60415,0.16641,0.20108],"force_p95":0.13264,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24521,"mean_force":0.09313,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.60228,0.14794,0.20487]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":16455.0,"contact_point_centroid":[0.5244,0.05128,0.20331],"force_p95":0.0954,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17973,"mean_force":0.05868,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.52556,0.07019,0.20393]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":16032.0,"contact_point_centroid":[0.52686,0.09019,0.20416],"force_p95":0.09499,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17697,"mean_force":0.05955,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.52665,0.07128,0.20434]},{"body_a":"world","body_b":"grasp_target","contact_count":1084.0,"contact_point_centroid":[0.58769,0.15004,-0.00195],"force_p95":0.15131,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.15766,"mean_force":0.1205,"phase_index":7.0,"phase_name":"retract_after_place","phase_type":"retract","tcp_position_centroid":[0.60099,0.14959,0.22093]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.46285,-7e-05,-0.00202],"force_p95":0.12945,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.1522,"mean_force":0.12445,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.45238,-0.00018,0.04874]},{"body_a":"world","body_b":"grasp_target","contact_count":1632.0,"contact_point_centroid":[0.46286,-7e-05,-0.00192],"force_p95":0.13462,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12293,"phase_index":0.0,"phase_name":"approach_to_object","phase_type":"approach","tcp_position_centroid":[0.48121,-5e-05,0.23059]},{"body_a":"world","body_b":"grasp_target","contact_count":1480.0,"contact_point_centroid":[0.46286,-7e-05,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.4596,-0.0001,0.10719]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4870.0,"contact_point_centroid":[0.4512,0.019,0.04917],"force_p95":0.067,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08169,"mean_force":0.0448,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.45132,-0.00019,0.0477]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4857.0,"contact_point_centroid":[0.4503,-0.01939,0.04848],"force_p95":0.06666,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0805,"mean_force":0.04494,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.45132,-0.00019,0.0477]}],"total_contact_groups":16},"final_pose_error":0.01981,"key_states":{"actual_goal_position":[0.61015,0.15287,0.12219],"final_object_position":[0.58766,0.15005,0.02602],"final_tcp_position":[0.60577,0.15141,0.25292],"realised_goal_position":[0.61015,0.15287,0.12219],"realised_object_initial_position":[0.46286,-7e-05,0.03]},"peak_contact_force":1.2507,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":409.0,"n_steps_budget":1000.0,"object_pos_end":[0.46286,-7e-05,0.02602],"object_pos_start":[0.46286,-7e-05,0.03],"object_to_goal_dist_end":0.2331,"object_to_goal_dist_start":0.23148,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_to_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1632.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.46299,-8e-05,0.15977],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.13375,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":370.0,"n_steps_budget":1000.0,"object_pos_end":[0.46286,-7e-05,0.02602],"object_pos_start":[0.46286,-7e-05,0.02602],"object_to_goal_dist_end":0.2331,"object_to_goal_dist_start":0.2331,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1480.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.45876,-0.00011,0.05507],"tcp_start":[0.46299,-8e-05,0.15977],"tcp_to_object_dist_end":0.02934,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.46277,-0.00015,0.02591],"object_pos_start":[0.46286,-7e-05,0.02602],"object_to_goal_dist_end":0.23325,"object_to_goal_dist_start":0.2331,"object_z_max":0.02602,"peak_contact_force":0.12959,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11527.0,"raw_peak_contact_force":0.1522,"subtask_id":"grasp_1","tcp_end":[0.45129,-0.00019,0.04767],"tcp_start":[0.45876,-0.00011,0.05507],"tcp_to_object_dist_end":0.0246,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":39.0,"n_steps":449.0,"n_steps_budget":1000.0,"object_pos_end":[0.46568,-0.00012,0.15662],"object_pos_start":[0.46277,-0.00015,0.02591],"object_to_goal_dist_end":0.21322,"object_to_goal_dist_start":0.23325,"object_z_max":0.15635,"peak_contact_force":0.07685,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":17120.0,"raw_peak_contact_force":0.383,"tcp_end":[0.45842,-0.00017,0.18191],"tcp_start":[0.45129,-0.00019,0.04767],"tcp_to_object_dist_end":0.02631,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":987.0,"n_steps_budget":1000.0,"object_pos_end":[0.60268,0.14648,0.19949],"object_pos_start":[0.46568,-0.00012,0.15662],"object_to_goal_dist_end":0.07793,"object_to_goal_dist_start":0.21322,"object_z_max":0.19947,"peak_contact_force":0.10157,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":32487.0,"raw_peak_contact_force":0.17973,"subtask_id":"transport_arc","tcp_end":[0.6015,0.14648,0.23181],"tcp_start":[0.45842,-0.00017,0.18191],"tcp_to_object_dist_end":0.03234,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":19.0,"n_steps":121.0,"n_steps_budget":1000.0,"object_pos_end":[0.60848,0.14987,0.1372],"object_pos_start":[0.60268,0.14648,0.19949],"object_to_goal_dist_end":0.0154,"object_to_goal_dist_start":0.07793,"object_z_max":0.19949,"peak_contact_force":0.13781,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2502.0,"raw_peak_contact_force":0.25074,"subtask_id":"release_1","tcp_end":[0.60426,0.14992,0.17065],"tcp_start":[0.6015,0.14648,0.23181],"tcp_to_object_dist_end":0.03371,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.59427,0.14942,0.02439],"object_pos_start":[0.60848,0.14987,0.1372],"object_to_goal_dist_end":0.09914,"object_to_goal_dist_start":0.0154,"object_z_max":0.1372,"peak_contact_force":0.13293,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1660.0,"raw_peak_contact_force":1.2507,"tcp_end":[0.59798,0.14819,0.18995],"tcp_start":[0.60426,0.14992,0.17065],"tcp_to_object_dist_end":0.16561,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":271.0,"n_steps_budget":780.0,"object_pos_end":[0.58766,0.15005,0.02602],"object_pos_start":[0.59427,0.14942,0.02439],"object_to_goal_dist_end":0.0988,"object_to_goal_dist_start":0.09914,"object_z_max":0.02671,"peak_contact_force":0.12271,"phase_name":"retract_after_place","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1084.0,"raw_peak_contact_force":0.15766,"tcp_end":[0.60577,0.15141,0.25292],"tcp_start":[0.59798,0.14819,0.18995],"tcp_to_object_dist_end":0.22763,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```