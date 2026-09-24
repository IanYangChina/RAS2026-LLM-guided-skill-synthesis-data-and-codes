## Search State

- **Seed**: 9
- **Iteration**: 8 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 7 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | position_control | position_control | position_control | impedance_control | impedance_control | impedance_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 8 | 0.0338 | 0.21 | ❌ rejected |
| 6 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | position_control | impedance_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 9 | 0.0520 | 0.39 | ❌ rejected |
| 5 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | position_control | position_control | position_control | impedance_control | impedance_control | impedance_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 8 | 0.2655 | 0.64 | ✅ accepted |
| 4 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | impedance_control | impedance_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 11 | -0.0794 | 0.37 | ❌ rejected |
| 3 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | impedance_control | impedance_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 10 | -0.0206 | 0.39 | ✅ accepted |

**Proposal policy**: task_score is 0.21 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.034) — your mutation base

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

- **Composite score**: 0.034
- **task_score** (E): 0.205
- **fitness_score**: 0.554  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.520

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_to_object | 1.00 | 1.00 | 0.1184 |
| descend_to_grasp | 1.00 | 1.00 | 0.1224 |
| grasp | 1.00 | 1.00 | 0.0129 |
| lift_object | 1.00 | 1.00 | 0.1339 |
| transport_to_goal | 1.00 | 1.00 | 0.0072 |
| descend_to_place | 1.00 | 1.00 | 0.0991 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_to_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.510, -0.012, 0.187) | (0.515, -0.017, 0.030)→(0.515, -0.017, 0.026) | 0.268→0.270 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_to_grasp | descend | 1.00 / step_budget | (0.510, -0.012, 0.187)→(0.510, -0.016, 0.065) | (0.515, -0.017, 0.026)→(0.515, -0.017, 0.026) | 0.270→0.270 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp | grasp | 1.00 / step_budget | (0.510, -0.016, 0.065)→(0.502, -0.016, 0.055) | (0.515, -0.017, 0.026)→(0.515, -0.016, 0.026) | 0.270→0.270 | 1.00 / 25.667 | 0.147 | 0.190 |
| lift_object | lift | 1.00 / step_budget | (0.502, -0.016, 0.055)→(0.511, -0.016, 0.189) | (0.515, -0.016, 0.026)→(0.516, -0.015, 0.151) | 0.270→0.230 | 1.00 / 15.000 | 0.103 | 0.313 |
| transport_to_goal | approach | 1.00 / step_budget | (0.605, 0.160, 0.301)→(0.607, 0.163, 0.295) | (0.516, -0.015, 0.151)→(0.543, 0.020, 0.018) | 0.230→0.244 | 1.00 / 8.000 | 3249.758 | 2.019 |
| descend_to_place | descend | 1.00 / step_budget | (0.607, 0.163, 0.295)→(0.612, 0.176, 0.197) | (0.544, 0.018, 0.016)→(0.545, 0.018, 0.016) | 0.245→0.246 | 1.00 / 8.667 | 182005.677 | 0.189 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.260
- phase_score: 0.272
- phase_breakdown.descend_1_score: 0.726
- phase_breakdown.grasp_1_score: 1.000
- phase_breakdown.transport_arc_score: 0.087
- phase_breakdown.approach_1_score: 0.044
- phase_breakdown.release_1_score: 0.000
- grasp_place_fitness: 0.581

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.581
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.260
- **Median Q (composite search score)**: 0.048
- **K-run variance**: 0.0009
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.250


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.36164,"average_solve_count":318.0,"average_success_count":318.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_to_object.speed":0.1008,"descend_to_grasp.speed":0.04873,"descend_to_place.speed":0.03855,"grasp.grip_force":14.96912,"lift_object.lift_height":0.19953,"lift_object.speed":0.06159,"transport_to_goal.arc_height":0.10817,"transport_to_goal.speed":0.07358},"optimized_scores":{"best_composite_score":-0.00821,"best_fitness_score":0.51179,"best_task_score":0.12039},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":1774.0,"contact_point_centroid":[0.55179,-0.01882,-0.0027],"force_p95":0.27288,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.04796,"mean_force":0.15088,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.56768,0.09424,0.34852]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5176.0,"contact_point_centroid":[0.52883,-0.0018,0.12241],"force_p95":0.14259,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31482,"mean_force":0.10352,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.5253,-0.02011,0.12606]},{"body_a":"world","body_b":"grasp_target","contact_count":93.0,"contact_point_centroid":[0.53577,-0.0195,-0.00143],"force_p95":0.23364,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.27577,"mean_force":0.06378,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.5212,-0.02001,0.05554]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5537.0,"contact_point_centroid":[0.52828,-0.03827,0.1222],"force_p95":0.14104,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26347,"mean_force":0.09868,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.52528,-0.02011,0.12592]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":762.0,"contact_point_centroid":[0.5368,-0.00194,0.2193],"force_p95":0.1573,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23324,"mean_force":0.11113,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.53093,-0.0203,0.22363]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":906.0,"contact_point_centroid":[0.53656,-0.03814,0.22157],"force_p95":0.14124,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23194,"mean_force":0.09609,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.53095,-0.02011,0.22575]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53707,-0.02123,-0.0021],"force_p95":0.15291,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.20569,"mean_force":0.13065,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.52343,-0.02006,0.05558]},{"body_a":"world","body_b":"grasp_target","contact_count":532.0,"contact_point_centroid":[0.53702,-0.02132,-0.00176],"force_p95":0.13797,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12354,"phase_index":0.0,"phase_name":"approach_to_object","phase_type":"approach","tcp_position_centroid":[0.51217,-0.00702,0.24689]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2623.0,"contact_point_centroid":[0.52365,-0.00135,0.05122],"force_p95":0.11903,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1258,"mean_force":0.08319,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.52226,-0.02003,0.05421]},{"body_a":"world","body_b":"grasp_target","contact_count":952.0,"contact_point_centroid":[0.53702,-0.02132,-0.00199],"force_p95":0.12264,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12264,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.5268,-0.01764,0.12502]},{"body_a":"world","body_b":"grasp_target","contact_count":556.0,"contact_point_centroid":[0.55179,-0.01879,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.60406,0.21289,0.28835]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2993.0,"contact_point_centroid":[0.52307,-0.03859,0.05111],"force_p95":0.09462,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09665,"mean_force":0.06853,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.52227,-0.02003,0.05421]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1720.0,"contact_point_centroid":[0.57078,0.10257,0.35446],"force_p95":0.01188,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01644,"mean_force":0.01072,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.57038,0.10257,0.35225]},{"body_a":"left_finger","body_b":"right_finger","contact_count":592.0,"contact_point_centroid":[0.60451,0.21295,0.29034],"force_p95":0.01095,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01098,"mean_force":0.01046,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.60407,0.21294,0.28805]}],"total_contact_groups":14},"final_pose_error":0.02941,"key_states":{"actual_goal_position":[0.61031,0.22775,0.20741],"final_object_position":[0.55179,-0.01879,0.01602],"final_tcp_position":[0.60636,0.22067,0.23568],"realised_goal_position":[0.61031,0.22775,0.20741],"realised_object_initial_position":[0.53702,-0.02132,0.03]},"peak_contact_force":273009.34322,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":134.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.03],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31446,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_to_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":532.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.52532,-0.01518,0.18693],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.16145,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":238.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.12262,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":952.0,"raw_peak_contact_force":0.12264,"subtask_id":"descend_1","tcp_end":[0.53081,-0.02016,0.06468],"tcp_start":[0.52532,-0.01518,0.18693],"tcp_to_object_dist_end":0.03917,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":27.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53722,-0.02037,0.02558],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31618,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.15025,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":7416.0,"raw_peak_contact_force":0.20569,"subtask_id":"grasp_1","tcp_end":[0.52223,-0.02003,0.05417],"tcp_start":[0.53081,-0.02016,0.06468],"tcp_to_object_dist_end":0.03228,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":19.0,"n_steps":554.0,"n_steps_budget":1000.0,"object_pos_end":[0.53826,-0.02052,0.16912],"object_pos_start":[0.53722,-0.02037,0.02558],"object_to_goal_dist_end":0.26133,"object_to_goal_dist_start":0.31618,"object_z_max":0.16887,"peak_contact_force":0.11336,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":10806.0,"raw_peak_contact_force":0.31482,"tcp_end":[0.53268,-0.02027,0.20575],"tcp_start":[0.52223,-0.02003,0.05417],"tcp_to_object_dist_end":0.03706,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":644.0,"n_steps_budget":1000.0,"object_pos_end":[0.55179,-0.01879,0.01602],"object_pos_start":[0.53826,-0.02052,0.16912],"object_to_goal_dist_end":0.31755,"object_to_goal_dist_start":0.26133,"object_z_max":0.21056,"peak_contact_force":9748.81076,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":5162.0,"raw_peak_contact_force":2.04796,"subtask_id":"transport_arc","tcp_end":[0.60254,0.20641,0.33392],"tcp_start":[0.60176,0.20176,0.33934],"tcp_to_object_dist_end":0.39288,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":139.0,"n_steps_budget":1000.0,"object_pos_end":[0.55179,-0.01879,0.01602],"object_pos_start":[0.55179,-0.01879,0.01602],"object_to_goal_dist_end":0.31755,"object_to_goal_dist_start":0.31755,"object_z_max":0.01602,"peak_contact_force":273009.34322,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1148.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.60636,0.22067,0.23568],"tcp_start":[0.60254,0.20641,0.33392],"tcp_to_object_dist_end":0.3295,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.22082,"average_solve_count":317.0,"average_success_count":317.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_to_object.speed":0.13228,"descend_to_grasp.speed":0.06744,"descend_to_place.speed":0.03217,"grasp.grip_force":8.0151,"lift_object.lift_height":0.15931,"lift_object.speed":0.05842,"transport_to_goal.arc_height":0.19532,"transport_to_goal.speed":0.04953},"optimized_scores":{"best_composite_score":0.06141,"best_fitness_score":0.58141,"best_task_score":0.25957},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":207.0,"contact_point_centroid":[0.60404,0.05982,-0.00796],"force_p95":1.69893,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.28398,"mean_force":0.52018,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.61133,0.12216,0.30513]},{"body_a":"world","body_b":"grasp_target","contact_count":536.0,"contact_point_centroid":[0.61736,0.0433,-0.00207],"force_p95":0.22692,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.32262,"mean_force":0.13049,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.62327,0.14969,0.25498]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4495.0,"contact_point_centroid":[0.53595,-0.04583,0.1048],"force_p95":0.14523,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31356,"mean_force":0.0968,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.53377,-0.02768,0.1086]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4522.0,"contact_point_centroid":[0.5355,-0.00951,0.10206],"force_p95":0.14142,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30474,"mean_force":0.0949,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.53344,-0.02766,0.10579]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2841.0,"contact_point_centroid":[0.55453,0.01349,0.23436],"force_p95":0.15971,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29462,"mean_force":0.11247,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.54984,-0.00459,0.23931]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3049.0,"contact_point_centroid":[0.55517,-0.0209,0.23547],"force_p95":0.14145,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27837,"mean_force":0.10534,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.55067,-0.00294,0.24032]},{"body_a":"world","body_b":"grasp_target","contact_count":99.0,"contact_point_centroid":[0.54489,-0.02757,-0.00147],"force_p95":0.23467,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.26295,"mean_force":0.06379,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.52936,-0.02741,0.05501]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.54567,-0.02917,-0.00215],"force_p95":0.16158,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.21613,"mean_force":0.13333,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.53154,-0.02748,0.05506]},{"body_a":"world","body_b":"grasp_target","contact_count":540.0,"contact_point_centroid":[0.5456,-0.02923,-0.00177],"force_p95":0.13797,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12353,"phase_index":0.0,"phase_name":"approach_to_object","phase_type":"approach","tcp_position_centroid":[0.51533,-0.00983,0.24564]},{"body_a":"world","body_b":"grasp_target","contact_count":924.0,"contact_point_centroid":[0.5456,-0.02923,-0.00199],"force_p95":0.12264,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12264,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.53419,-0.02431,0.12424]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2657.0,"contact_point_centroid":[0.53208,-0.046,0.05057],"force_p95":0.11836,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12226,"mean_force":0.07982,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.53037,-0.02744,0.05366]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2630.0,"contact_point_centroid":[0.53193,-0.00905,0.05069],"force_p95":0.11823,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12135,"mean_force":0.0818,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.53036,-0.02744,0.05365]},{"body_a":"left_finger","body_b":"right_finger","contact_count":269.0,"contact_point_centroid":[0.61623,0.13171,0.30493],"force_p95":0.01364,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0163,"mean_force":0.01128,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.61582,0.13171,0.30264]},{"body_a":"left_finger","body_b":"right_finger","contact_count":579.0,"contact_point_centroid":[0.62372,0.14962,0.25785],"force_p95":0.01096,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01271,"mean_force":0.01032,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.62324,0.14961,0.25552]}],"total_contact_groups":14},"final_pose_error":0.02951,"key_states":{"actual_goal_position":[0.63284,0.16493,0.17692],"final_object_position":[0.61742,0.04327,0.01602],"final_tcp_position":[0.62699,0.15763,0.20491],"realised_goal_position":[0.63284,0.16493,0.17692],"realised_object_initial_position":[0.5456,-0.02923,0.03]},"peak_contact_force":273007.56559,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":136.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.03],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.25864,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_to_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":540.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.53189,-0.02102,0.18585],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.16062,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":231.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.12262,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":924.0,"raw_peak_contact_force":0.12264,"subtask_id":"descend_1","tcp_end":[0.53903,-0.02765,0.06448],"tcp_start":[0.53189,-0.02102,0.18585],"tcp_to_object_dist_end":0.03905,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":25.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.546,-0.02823,0.02543],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26039,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.15972,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":7087.0,"raw_peak_contact_force":0.21613,"subtask_id":"grasp_1","tcp_end":[0.53033,-0.02744,0.05361],"tcp_start":[0.53903,-0.02765,0.06448],"tcp_to_object_dist_end":0.03226,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":18.0,"n_steps":427.0,"n_steps_budget":1000.0,"object_pos_end":[0.54553,-0.02836,0.13029],"object_pos_start":[0.546,-0.02823,0.02543],"object_to_goal_dist_end":0.21716,"object_to_goal_dist_start":0.26039,"object_z_max":0.13005,"peak_contact_force":0.13322,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":9116.0,"raw_peak_contact_force":0.31356,"tcp_end":[0.54071,-0.02803,0.16555],"tcp_start":[0.53033,-0.02744,0.05361],"tcp_to_object_dist_end":0.03559,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":560.0,"n_steps_budget":1000.0,"object_pos_end":[0.61029,0.04691,0.02053],"object_pos_start":[0.54553,-0.02836,0.13029],"object_to_goal_dist_end":0.19721,"object_to_goal_dist_start":0.21716,"object_z_max":0.25864,"peak_contact_force":0.34174,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":6366.0,"raw_peak_contact_force":2.28398,"subtask_id":"transport_arc","tcp_end":[0.62078,0.14329,0.29667],"tcp_start":[0.61947,0.13872,0.3005],"tcp_to_object_dist_end":0.29266,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":134.0,"n_steps_budget":1000.0,"object_pos_end":[0.61742,0.04327,0.01602],"object_pos_start":[0.61601,0.04321,0.01723],"object_to_goal_dist_end":0.20231,"object_to_goal_dist_start":0.20149,"object_z_max":0.01723,"peak_contact_force":273007.56559,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1115.0,"raw_peak_contact_force":0.32262,"tcp_end":[0.62699,0.15763,0.20491],"tcp_start":[0.62078,0.14329,0.29667],"tcp_to_object_dist_end":0.22102,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.40925,"average_solve_count":281.0,"average_success_count":281.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_to_object.speed":0.05022,"descend_to_grasp.speed":0.053,"descend_to_place.speed":0.05151,"grasp.grip_force":14.29054,"lift_object.lift_height":0.18819,"lift_object.speed":0.07174,"transport_to_goal.arc_height":0.12142,"transport_to_goal.speed":0.10302},"optimized_scores":{"best_composite_score":0.04832,"best_fitness_score":0.56832,"best_task_score":0.23535},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":1541.0,"contact_point_centroid":[0.46526,0.03006,-0.0026],"force_p95":0.34353,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.72397,"mean_force":0.16128,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.52783,0.07033,0.28846]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4031.0,"contact_point_centroid":[0.45438,-0.01877,0.11575],"force_p95":0.16201,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31077,"mean_force":0.10617,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.45379,-0.00036,0.11998]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4497.0,"contact_point_centroid":[0.45514,0.01788,0.11349],"force_p95":0.14262,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28286,"mean_force":0.09714,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.45371,-0.00036,0.1178]},{"body_a":"world","body_b":"grasp_target","contact_count":75.0,"contact_point_centroid":[0.46121,-0.00069,-0.00136],"force_p95":0.22945,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.25944,"mean_force":0.05464,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.45222,-0.0002,0.05868]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":63.0,"contact_point_centroid":[0.46319,0.0151,0.18998],"force_p95":0.1258,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1607,"mean_force":0.05933,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.45828,-0.00054,0.19532]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.46286,-0.00018,-0.00202],"force_p95":0.13116,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.14828,"mean_force":0.12457,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.45425,-0.00017,0.05853]},{"body_a":"world","body_b":"grasp_target","contact_count":540.0,"contact_point_centroid":[0.46286,-7e-05,-0.00177],"force_p95":0.13797,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12353,"phase_index":0.0,"phase_name":"approach_to_object","phase_type":"approach","tcp_position_centroid":[0.48757,-3e-05,0.24911]},{"body_a":"world","body_b":"grasp_target","contact_count":980.0,"contact_point_centroid":[0.46286,-7e-05,-0.00199],"force_p95":0.12264,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12264,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.4658,-8e-05,0.12674]},{"body_a":"world","body_b":"grasp_target","contact_count":584.0,"contact_point_centroid":[0.46556,0.03076,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.5992,0.14437,0.20586]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2193.0,"contact_point_centroid":[0.45127,-0.01895,0.05441],"force_p95":0.11411,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11494,"mean_force":0.09031,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.45321,-0.00018,0.0575]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2928.0,"contact_point_centroid":[0.4528,0.01824,0.05356],"force_p95":0.09136,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09202,"mean_force":0.06946,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.45321,-0.00018,0.0575]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1456.0,"contact_point_centroid":[0.53571,0.07795,0.29491],"force_p95":0.01243,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01857,"mean_force":0.01069,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.53546,0.07794,0.29258]},{"body_a":"left_finger","body_b":"right_finger","contact_count":620.0,"contact_point_centroid":[0.59981,0.14438,0.20822],"force_p95":0.01101,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01286,"mean_force":0.01049,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.5992,0.14437,0.20594]}],"total_contact_groups":13},"final_pose_error":0.02997,"key_states":{"actual_goal_position":[0.61015,0.15287,0.12219],"final_object_position":[0.46556,0.03076,0.01602],"final_tcp_position":[0.60347,0.14864,0.15109],"realised_goal_position":[0.61015,0.15287,0.12219],"realised_object_initial_position":[0.46286,-7e-05,0.03]},"peak_contact_force":9748.94559,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":136.0,"n_steps_budget":1000.0,"object_pos_end":[0.46286,-7e-05,0.02602],"object_pos_start":[0.46286,-7e-05,0.03],"object_to_goal_dist_end":0.2331,"object_to_goal_dist_start":0.23148,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_to_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":540.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.47244,-6e-05,0.18803],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.16229,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":245.0,"n_steps_budget":1000.0,"object_pos_end":[0.46286,-7e-05,0.02602],"object_pos_start":[0.46286,-7e-05,0.02602],"object_to_goal_dist_end":0.2331,"object_to_goal_dist_start":0.2331,"object_z_max":0.02602,"peak_contact_force":0.12262,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":980.0,"raw_peak_contact_force":0.12264,"subtask_id":"descend_1","tcp_end":[0.46092,-0.0001,0.06548],"tcp_start":[0.47244,-6e-05,0.18803],"tcp_to_object_dist_end":0.03951,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":25.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.46277,-0.00054,0.02591],"object_pos_start":[0.46286,-7e-05,0.02602],"object_to_goal_dist_end":0.23351,"object_to_goal_dist_start":0.2331,"object_z_max":0.02602,"peak_contact_force":0.13026,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":6921.0,"raw_peak_contact_force":0.14828,"subtask_id":"grasp_1","tcp_end":[0.45318,-0.00018,0.05747],"tcp_start":[0.46092,-0.0001,0.06548],"tcp_to_object_dist_end":0.03299,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":436.0,"n_steps_budget":1000.0,"object_pos_end":[0.46361,0.00308,0.154],"object_pos_start":[0.46277,-0.00054,0.02591],"object_to_goal_dist_end":0.21195,"object_to_goal_dist_start":0.23351,"object_z_max":0.15395,"peak_contact_force":0.06113,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":8603.0,"raw_peak_contact_force":0.31077,"tcp_end":[0.45852,-0.00054,0.19463],"tcp_start":[0.45318,-0.00018,0.05747],"tcp_to_object_dist_end":0.04111,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":487.0,"n_steps_budget":1000.0,"object_pos_end":[0.46556,0.03076,0.01602],"object_pos_start":[0.46361,0.00308,0.154],"object_to_goal_dist_end":0.217,"object_to_goal_dist_start":0.21195,"object_z_max":0.154,"peak_contact_force":0.12263,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3060.0,"raw_peak_contact_force":1.72397,"subtask_id":"transport_arc","tcp_end":[0.59629,0.14073,0.25527],"tcp_start":[0.59485,0.13819,0.26308],"tcp_to_object_dist_end":0.29398,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":146.0,"n_steps_budget":1000.0,"object_pos_end":[0.46556,0.03076,0.01602],"object_pos_start":[0.46556,0.03076,0.01602],"object_to_goal_dist_end":0.217,"object_to_goal_dist_start":0.217,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1204.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.60347,0.14864,0.15109],"tcp_start":[0.59629,0.14073,0.25527],"tcp_to_object_dist_end":0.22619,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```