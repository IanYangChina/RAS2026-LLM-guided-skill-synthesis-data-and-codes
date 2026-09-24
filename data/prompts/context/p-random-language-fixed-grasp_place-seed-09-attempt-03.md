## Search State

- **Seed**: 9
- **Iteration**: 4 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 3 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | impedance_control | impedance_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 10 | -0.0206 | 0.39 | ✅ accepted |
| 2 | rotate → pull → push → descend → descend → grasp → approach | impedance_motion | arc_cartesian | impedance_motion | linear_cartesian | linear_cartesian | — | linear_cartesian | impedance_control | impedance_control | impedance_control | admittance_control | position_control | position_control | position_control | pose_tolerance | time_limit | time_limit | pose_tolerance | contact_detected | grasp_success | pose_tolerance | 6 | -0.1650 | 0.13 | ❌ rejected |
| 1 | rotate → pull → push → descend → descend → grasp → approach | impedance_motion | arc_cartesian | impedance_motion | linear_cartesian | linear_cartesian | — | linear_cartesian | impedance_control | impedance_control | impedance_control | admittance_control | position_control | position_control | position_control | pose_tolerance | time_limit | time_limit | pose_tolerance | contact_detected | grasp_success | pose_tolerance | 6 | -0.1646 | 0.13 | ❌ rejected |
| 0 | rotate → pull → push → descend → descend → grasp → approach | impedance_motion | arc_cartesian | impedance_motion | linear_cartesian | linear_cartesian | — | linear_cartesian | impedance_control | impedance_control | impedance_control | admittance_control | position_control | position_control | position_control | pose_tolerance | time_limit | time_limit | pose_tolerance | contact_detected | grasp_success | pose_tolerance | 6 | -0.1649 | 0.13 | ❌ rejected |

**Proposal policy**: task_score is 0.39 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=-0.021) — your mutation base

```yaml
skill: grasp_place
dsl_version: 2
skill_type: arm_gripper
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
      - 0.1
      - 0.25
      default: 0.15
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
      - 0.03
      - 0.15
      default: 0.08
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
- id: descend_to_place
  type: descend
  generator: linear_cartesian
  control: position_control
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
- id: release_object
  type: release
  control: position_control
  termination: time_limit
  end_effector_action: open
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0
  parameters:
    release_duration:
      type: scalar
      range:
      - 0.2
      - 1.0
      default: 0.5
      binds_to:
      - path: duration.max_time
        mode: replace
- id: retract_from_goal
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
- **descend_to_place** (`descend`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - speed: status=consumed; consumers=generator.speed (replace)
- **release_object** (`release`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings:
    - release_duration: status=consumed; consumers=duration.max_time (replace)
- **retract_from_goal** (`retract`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.1], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - speed: status=consumed; consumers=generator.speed (replace)

## Design Metrics

- **Composite score**: -0.021
- **task_score** (E): 0.391
- **fitness_score**: 0.659  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.680

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_to_object | 1.00 | 1.00 | 0.1488 |
| descend_to_grasp | 1.00 | 1.00 | 0.1033 |
| grasp | 1.00 | 1.00 | 0.0122 |
| lift_object | 1.00 | 1.00 | 0.1220 |
| transport_to_goal | 1.00 | 1.00 | 0.2435 |
| descend_to_place | 1.00 | 1.00 | 0.1093 |
| release_object | 1.00 | 1.00 | 0.0202 |
| retract_from_goal | 1.00 | 1.00 | 0.0545 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_to_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.510, -0.015, 0.158) | (0.515, -0.017, 0.030)→(0.515, -0.017, 0.026) | 0.268→0.270 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_to_grasp | descend | 1.00 / step_budget | (0.510, -0.015, 0.158)→(0.510, -0.017, 0.054) | (0.515, -0.017, 0.026)→(0.515, -0.017, 0.026) | 0.270→0.270 | 1.00 / 4.000 | 8.932 | 0.123 |
| grasp | grasp | 1.00 / step_budget | (0.510, -0.017, 0.054)→(0.502, -0.017, 0.045) | (0.515, -0.017, 0.026)→(0.515, -0.016, 0.026) | 0.270→0.270 | 1.00 / 42.000 | 0.134 | 0.168 |
| lift_object | lift | 1.00 / step_budget | (0.502, -0.017, 0.045)→(0.510, -0.016, 0.167) | (0.515, -0.016, 0.026)→(0.518, -0.016, 0.142) | 0.270→0.236 | 1.00 / 35.667 | 10.623 | 0.377 |
| transport_to_goal | approach | 1.00 / step_budget | (0.510, -0.016, 0.167)→(0.607, 0.163, 0.284) | (0.518, -0.016, 0.142)→(0.613, 0.164, 0.253) | 0.236→0.087 | 1.00 / 23.333 | 0.127 | 0.179 |
| descend_to_place | descend | 1.00 / step_budget | (0.607, 0.163, 0.284)→(0.613, 0.178, 0.176) | (0.613, 0.164, 0.253)→(0.616, 0.178, 0.142) | 0.087→0.027 | 1.00 / 20.667 | 0.131 | 0.353 |
| release_object | release | 1.00 / step_budget | (0.613, 0.178, 0.176)→(0.607, 0.176, 0.196) | (0.616, 0.178, 0.142)→(0.603, 0.176, 0.023) | 0.027→0.147 | 1.00 / 3.000 | 0.230 | 1.478 |
| retract_from_goal | retract | 1.00 / step_budget | (0.607, 0.176, 0.196)→(0.613, 0.180, 0.250) | (0.603, 0.176, 0.023)→(0.595, 0.180, 0.026) | 0.147→0.145 | 1.00 / 4.000 | 0.123 | 0.229 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.517
- phase_score: 0.000
- phase_breakdown.descend_1_score: 0.000
- phase_breakdown.grasp_1_score: 0.000
- phase_breakdown.transport_arc_score: 0.000
- phase_breakdown.approach_1_score: 0.000
- phase_breakdown.release_1_score: 0.000
- grasp_place_fitness: 0.721

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.721
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.517
- **Median Q (composite search score)**: -0.035
- **K-run variance**: 0.0021
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.414


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.27397,"average_solve_count":292.0,"average_success_count":292.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_to_object.speed":0.11101,"descend_to_grasp.speed":0.04533,"descend_to_place.speed":0.07161,"grasp.grip_force":28.83246,"lift_object.lift_height":0.14645,"lift_object.speed":0.06238,"release_object.release_duration":0.40193,"retract_from_goal.speed":0.14795,"transport_to_goal.arc_height":0.04142,"transport_to_goal.speed":0.03684},"optimized_scores":{"best_composite_score":-0.06749,"best_fitness_score":0.61251,"best_task_score":0.29605},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":158.0,"contact_point_centroid":[0.5912,0.226,-0.00781],"force_p95":1.27301,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.76082,"mean_force":0.44021,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.60095,0.22053,0.22693]},{"body_a":"world","body_b":"grasp_target","contact_count":114.0,"contact_point_centroid":[0.53439,-0.0206,-0.00128],"force_p95":0.33517,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.41328,"mean_force":0.07837,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.522,-0.0208,0.04553]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":768.0,"contact_point_centroid":[0.60551,0.20349,0.20498],"force_p95":0.21936,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.34759,"mean_force":0.0969,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.6039,0.22192,0.20946]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":685.0,"contact_point_centroid":[0.60554,0.2401,0.20399],"force_p95":0.25444,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33089,"mean_force":0.10124,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.60383,0.22189,0.20933]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2592.0,"contact_point_centroid":[0.60671,0.22922,0.26136],"force_p95":0.16057,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28965,"mean_force":0.10668,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.60248,0.21114,0.26456]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":11833.0,"contact_point_centroid":[0.52715,-0.00166,0.10079],"force_p95":0.09327,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28725,"mean_force":0.05871,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.52544,-0.02072,0.09872]},{"body_a":"world","body_b":"grasp_target","contact_count":872.0,"contact_point_centroid":[0.59084,0.22659,-0.00218],"force_p95":0.19636,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.27932,"mean_force":0.12431,"phase_index":7.0,"phase_name":"retract_from_goal","phase_type":"retract","tcp_position_centroid":[0.60338,0.22307,0.26167]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":12635.0,"contact_point_centroid":[0.5272,-0.03972,0.10145],"force_p95":0.08402,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26977,"mean_force":0.0553,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.52553,-0.02072,0.09968]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2901.0,"contact_point_centroid":[0.60633,0.19241,0.26418],"force_p95":0.16047,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25354,"mean_force":0.10455,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.60233,0.21062,0.26694]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":11981.0,"contact_point_centroid":[0.56496,0.09253,0.25181],"force_p95":0.11158,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17815,"mean_force":0.07861,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.55942,0.07384,0.25147]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":13294.0,"contact_point_centroid":[0.56362,0.05316,0.24929],"force_p95":0.09696,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17008,"mean_force":0.0711,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.55875,0.07175,0.24927]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53703,-0.0212,-0.00205],"force_p95":0.13645,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.1689,"mean_force":0.12652,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.52428,-0.02085,0.04556]},{"body_a":"world","body_b":"grasp_target","contact_count":1896.0,"contact_point_centroid":[0.53702,-0.02132,-0.00193],"force_p95":0.13354,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12288,"phase_index":0.0,"phase_name":"approach_to_object","phase_type":"approach","tcp_position_centroid":[0.51379,-0.00952,0.228]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4111.0,"contact_point_centroid":[0.52389,-0.00162,0.04689],"force_p95":0.07711,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12869,"mean_force":0.05182,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.52308,-0.02083,0.04416]},{"body_a":"world","body_b":"grasp_target","contact_count":1376.0,"contact_point_centroid":[0.53702,-0.02132,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.52932,-0.02016,0.10496]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4898.0,"contact_point_centroid":[0.5239,-0.03991,0.04596],"force_p95":0.06926,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08697,"mean_force":0.04466,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.52308,-0.02083,0.04416]}],"total_contact_groups":16},"final_pose_error":0.01993,"key_states":{"actual_goal_position":[0.61031,0.22775,0.20741],"final_object_position":[0.58949,0.22727,0.02602],"final_tcp_position":[0.6068,0.22569,0.28791],"realised_goal_position":[0.61031,0.22775,0.20741],"realised_object_initial_position":[0.53702,-0.02132,0.03]},"peak_contact_force":1.76082,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":475.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.03],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31446,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_to_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1896.0,"raw_peak_contact_force":0.13845,"tcp_end":[0.53009,-0.01942,0.15678],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.13096,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":344.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1376.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.53142,-0.02098,0.05402],"tcp_start":[0.53009,-0.01942,0.15678],"tcp_to_object_dist_end":0.02855,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53694,-0.0208,0.02582],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31644,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.13406,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10809.0,"raw_peak_contact_force":0.1689,"tcp_end":[0.52305,-0.02082,0.04413],"tcp_start":[0.53142,-0.02098,0.05402],"tcp_to_object_dist_end":0.02298,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":28.0,"n_steps":662.0,"n_steps_budget":1000.0,"object_pos_end":[0.54342,-0.02069,0.13408],"object_pos_start":[0.53694,-0.0208,0.02582],"object_to_goal_dist_end":0.26754,"object_to_goal_dist_start":0.31644,"object_z_max":0.13394,"peak_contact_force":0.10126,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":24582.0,"raw_peak_contact_force":0.41328,"tcp_end":[0.53209,-0.02071,0.15823],"tcp_start":[0.52305,-0.02082,0.04413],"tcp_to_object_dist_end":0.02667,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.60661,0.20035,0.28417],"object_pos_start":[0.54342,-0.02069,0.13408],"object_to_goal_dist_end":0.08159,"object_to_goal_dist_start":0.26754,"object_z_max":0.28414,"peak_contact_force":0.13526,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":25275.0,"raw_peak_contact_force":0.17815,"tcp_end":[0.60042,0.2008,0.3159],"tcp_start":[0.53209,-0.02071,0.15823],"tcp_to_object_dist_end":0.03233,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":22.0,"n_steps":286.0,"n_steps_budget":1000.0,"object_pos_end":[0.60637,0.22088,0.17926],"object_pos_start":[0.60661,0.20035,0.28417],"object_to_goal_dist_end":0.02925,"object_to_goal_dist_start":0.08159,"object_z_max":0.28417,"peak_contact_force":0.14869,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":5493.0,"raw_peak_contact_force":0.28965,"tcp_end":[0.60589,0.22254,0.21443],"tcp_start":[0.60042,0.2008,0.3159],"tcp_to_object_dist_end":0.03521,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.60064,0.22203,0.01856],"object_pos_start":[0.60637,0.22088,0.17926],"object_to_goal_dist_end":0.18918,"object_to_goal_dist_start":0.02925,"object_z_max":0.17926,"peak_contact_force":0.28915,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1611.0,"raw_peak_contact_force":1.76082,"tcp_end":[0.60092,0.22052,0.23337],"tcp_start":[0.60589,0.22254,0.21443],"tcp_to_object_dist_end":0.21481,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":233.0,"n_steps_budget":600.0,"object_pos_end":[0.58949,0.22727,0.02602],"object_pos_start":[0.60064,0.22203,0.01856],"object_to_goal_dist_end":0.18258,"object_to_goal_dist_start":0.18918,"object_z_max":0.02741,"peak_contact_force":0.12299,"phase_name":"retract_from_goal","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":872.0,"raw_peak_contact_force":0.27932,"tcp_end":[0.6068,0.22569,0.28791],"tcp_start":[0.60092,0.22052,0.23337],"tcp_to_object_dist_end":0.26246,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.97409,"average_solve_count":386.0,"average_success_count":386.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_to_object.speed":0.10528,"descend_to_grasp.speed":0.02502,"descend_to_place.speed":0.03877,"grasp.grip_force":14.10041,"lift_object.lift_height":0.12243,"lift_object.speed":0.03367,"release_object.release_duration":0.74977,"retract_from_goal.speed":0.08658,"transport_to_goal.arc_height":0.0548,"transport_to_goal.speed":0.03276},"optimized_scores":{"best_composite_score":-0.03494,"best_fitness_score":0.64506,"best_task_score":0.36091},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":146.0,"contact_point_centroid":[0.62171,0.1603,-0.00871],"force_p95":1.26379,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.57748,"mean_force":0.49458,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.62213,0.15983,0.19467]},{"body_a":"world","body_b":"grasp_target","contact_count":131.0,"contact_point_centroid":[0.54203,-0.02831,-0.00137],"force_p95":0.34059,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.37054,"mean_force":0.09937,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.53032,-0.02845,0.04493]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":780.0,"contact_point_centroid":[0.63119,0.17988,0.1794],"force_p95":0.09752,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29835,"mean_force":0.06716,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.62585,0.16102,0.18022]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":831.0,"contact_point_centroid":[0.63092,0.14231,0.18023],"force_p95":0.09265,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28272,"mean_force":0.06217,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.62588,0.16102,0.18027]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3758.0,"contact_point_centroid":[0.62981,0.17355,0.23737],"force_p95":0.10693,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26896,"mean_force":0.07602,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.62477,0.15478,0.23763]},{"body_a":"world","body_b":"grasp_target","contact_count":866.0,"contact_point_centroid":[0.61021,0.16161,-0.0021],"force_p95":0.22097,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24934,"mean_force":0.12942,"phase_index":7.0,"phase_name":"retract_from_goal","phase_type":"retract","tcp_position_centroid":[0.62481,0.16152,0.23194]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":10912.0,"contact_point_centroid":[0.53478,-0.00925,0.09259],"force_p95":0.07941,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24704,"mean_force":0.05421,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.53423,-0.02839,0.09001]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":11450.0,"contact_point_centroid":[0.53472,-0.04747,0.09046],"force_p95":0.07628,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24057,"mean_force":0.05248,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.53399,-0.02839,0.0882]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4157.0,"contact_point_centroid":[0.62893,0.13607,0.23772],"force_p95":0.09811,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22545,"mean_force":0.06928,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.62474,0.15472,0.2381]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.54562,-0.0291,-0.00207],"force_p95":0.14195,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.18405,"mean_force":0.12792,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.53264,-0.02854,0.04525]},{"body_a":"world","body_b":"grasp_target","contact_count":2000.0,"contact_point_centroid":[0.5456,-0.02923,-0.00193],"force_p95":0.13259,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12287,"phase_index":0.0,"phase_name":"approach_to_object","phase_type":"approach","tcp_position_centroid":[0.5178,-0.01317,0.22724]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4104.0,"contact_point_centroid":[0.53231,-0.00929,0.04653],"force_p95":0.07809,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13397,"mean_force":0.05186,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.53142,-0.0285,0.0438]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":18282.0,"contact_point_centroid":[0.56868,0.01452,0.22794],"force_p95":0.07805,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12383,"mean_force":0.05197,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.56719,0.03345,0.227]},{"body_a":"world","body_b":"grasp_target","contact_count":1404.0,"contact_point_centroid":[0.5456,-0.02923,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.53748,-0.02768,0.10477]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":15713.0,"contact_point_centroid":[0.56847,0.05134,0.22687],"force_p95":0.08917,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12244,"mean_force":0.0603,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.56661,0.03226,0.22602]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4914.0,"contact_point_centroid":[0.53231,-0.04759,0.04559],"force_p95":0.07027,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07748,"mean_force":0.04466,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.53142,-0.0285,0.04381]}],"total_contact_groups":16},"final_pose_error":0.01996,"key_states":{"actual_goal_position":[0.63284,0.16493,0.17692],"final_object_position":[0.6086,0.16174,0.02602],"final_tcp_position":[0.62861,0.16333,0.25748],"realised_goal_position":[0.63284,0.16493,0.17692],"realised_object_initial_position":[0.5456,-0.02923,0.03]},"peak_contact_force":31.67879,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":501.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.03],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.25864,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_to_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2000.0,"raw_peak_contact_force":0.13845,"tcp_end":[0.53811,-0.02675,0.15597],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.13019,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":351.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1404.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.53986,-0.02875,0.05399],"tcp_start":[0.53811,-0.02675,0.15597],"tcp_to_object_dist_end":0.02855,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54552,-0.02855,0.02575],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.2606,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.13862,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10818.0,"raw_peak_contact_force":0.18405,"tcp_end":[0.53139,-0.0285,0.04377],"tcp_start":[0.53986,-0.02875,0.05399],"tcp_to_object_dist_end":0.0229,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":575.0,"n_steps_budget":1000.0,"object_pos_end":[0.54876,-0.02844,0.11177],"object_pos_start":[0.54552,-0.02855,0.02575],"object_to_goal_dist_end":0.2207,"object_to_goal_dist_start":0.2606,"object_z_max":0.11163,"peak_contact_force":31.67879,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":22493.0,"raw_peak_contact_force":0.37054,"tcp_end":[0.54028,-0.02841,0.13418],"tcp_start":[0.53139,-0.0285,0.04377],"tcp_to_object_dist_end":0.02396,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":27.0,"n_steps":963.0,"n_steps_budget":1000.0,"object_pos_end":[0.62933,0.14895,0.26107],"object_pos_start":[0.54876,-0.02844,0.11177],"object_to_goal_dist_end":0.08573,"object_to_goal_dist_start":0.2207,"object_z_max":0.26154,"peak_contact_force":0.11048,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":33995.0,"raw_peak_contact_force":0.12383,"tcp_end":[0.62359,0.14911,0.28904],"tcp_start":[0.54028,-0.02841,0.13418],"tcp_to_object_dist_end":0.02855,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":25.0,"n_steps":296.0,"n_steps_budget":1000.0,"object_pos_end":[0.63399,0.16107,0.155],"object_pos_start":[0.62933,0.14895,0.26107],"object_to_goal_dist_end":0.02229,"object_to_goal_dist_start":0.08573,"object_z_max":0.26107,"peak_contact_force":0.10095,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":7915.0,"raw_peak_contact_force":0.26896,"tcp_end":[0.62789,0.16148,0.18487],"tcp_start":[0.62359,0.14911,0.28904],"tcp_to_object_dist_end":0.03049,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.62138,0.15634,0.02533],"object_pos_start":[0.63399,0.16107,0.155],"object_to_goal_dist_end":0.15227,"object_to_goal_dist_start":0.02229,"object_z_max":0.155,"peak_contact_force":0.25118,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1757.0,"raw_peak_contact_force":1.57748,"tcp_end":[0.62209,0.15981,0.20366],"tcp_start":[0.62789,0.16148,0.18487],"tcp_to_object_dist_end":0.17836,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":234.0,"n_steps_budget":600.0,"object_pos_end":[0.6086,0.16174,0.02602],"object_pos_start":[0.62138,0.15634,0.02533],"object_to_goal_dist_end":0.15287,"object_to_goal_dist_start":0.15227,"object_z_max":0.02812,"peak_contact_force":0.12319,"phase_name":"retract_from_goal","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":866.0,"raw_peak_contact_force":0.24934,"tcp_end":[0.62861,0.16333,0.25748],"tcp_start":[0.62209,0.15981,0.20366],"tcp_to_object_dist_end":0.23233,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.13043,"average_solve_count":345.0,"average_success_count":345.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_to_object.speed":0.1177,"descend_to_grasp.speed":0.03546,"descend_to_place.speed":0.05869,"grasp.grip_force":15.5635,"lift_object.lift_height":0.19647,"lift_object.speed":0.02629,"release_object.release_duration":0.37145,"retract_from_goal.speed":0.0619,"transport_to_goal.arc_height":0.05863,"transport_to_goal.speed":0.07265},"optimized_scores":{"best_composite_score":0.04071,"best_fitness_score":0.72071,"best_task_score":0.51662},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":306.0,"contact_point_centroid":[0.58768,0.14983,-0.00372],"force_p95":0.82505,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.09471,"mean_force":0.22834,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.59741,0.14834,0.13824]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2868.0,"contact_point_centroid":[0.60321,0.16249,0.18924],"force_p95":0.15775,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.50023,"mean_force":0.11551,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.59845,0.14444,0.19257]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2836.0,"contact_point_centroid":[0.60358,0.12701,0.1817],"force_p95":0.15086,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.39673,"mean_force":0.11123,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.59908,0.14509,0.18494]},{"body_a":"world","body_b":"grasp_target","contact_count":109.0,"contact_point_centroid":[0.45935,-0.0003,-0.00134],"force_p95":0.3263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.34624,"mean_force":0.11373,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.45019,-0.00021,0.04849]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":511.0,"contact_point_centroid":[0.60589,0.16784,0.1199],"force_p95":0.14241,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32025,"mean_force":0.09773,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.6016,0.14955,0.12493]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":518.0,"contact_point_centroid":[0.6057,0.13148,0.12077],"force_p95":0.13466,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31395,"mean_force":0.09427,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.60171,0.14958,0.1251]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":9169.0,"contact_point_centroid":[0.51456,0.07273,0.25315],"force_p95":0.10936,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23443,"mean_force":0.06916,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.51076,0.05433,0.25329]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":17151.0,"contact_point_centroid":[0.4532,0.0188,0.12982],"force_p95":0.07386,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23436,"mean_force":0.05058,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.45329,-0.0002,0.1288]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":14649.0,"contact_point_centroid":[0.45241,-0.01937,0.13027],"force_p95":0.08481,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22523,"mean_force":0.0583,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.45332,-0.0002,0.12915]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8117.0,"contact_point_centroid":[0.50822,0.03049,0.25044],"force_p95":0.13429,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19928,"mean_force":0.08091,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.50573,0.04928,0.25176]},{"body_a":"world","body_b":"grasp_target","contact_count":948.0,"contact_point_centroid":[0.58657,0.15002,-0.00197],"force_p95":0.14469,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.15866,"mean_force":0.12266,"phase_index":7.0,"phase_name":"retract_from_goal","phase_type":"retract","tcp_position_centroid":[0.60017,0.14955,0.17578]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.46285,-8e-05,-0.00202],"force_p95":0.12947,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.15221,"mean_force":0.12446,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.45227,-0.00018,0.04851]},{"body_a":"world","body_b":"grasp_target","contact_count":1652.0,"contact_point_centroid":[0.46286,-7e-05,-0.00192],"force_p95":0.13462,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12292,"phase_index":0.0,"phase_name":"approach_to_object","phase_type":"approach","tcp_position_centroid":[0.48123,-5e-05,0.23062]},{"body_a":"world","body_b":"grasp_target","contact_count":1496.0,"contact_point_centroid":[0.46286,-7e-05,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.45951,-0.0001,0.10713]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4870.0,"contact_point_centroid":[0.45112,0.01898,0.04908],"force_p95":0.06674,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08171,"mean_force":0.04474,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.45121,-0.00019,0.04747]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4673.0,"contact_point_centroid":[0.45052,-0.01938,0.04845],"force_p95":0.06876,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0805,"mean_force":0.04664,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.45121,-0.00019,0.04747]}],"total_contact_groups":16},"final_pose_error":0.01984,"key_states":{"actual_goal_position":[0.61015,0.15287,0.12219],"final_object_position":[0.58654,0.15002,0.02602],"final_tcp_position":[0.60484,0.15121,0.20314],"realised_goal_position":[0.61015,0.15287,0.12219],"realised_object_initial_position":[0.46286,-7e-05,0.03]},"peak_contact_force":26.5509,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":414.0,"n_steps_budget":1000.0,"object_pos_end":[0.46286,-7e-05,0.02602],"object_pos_start":[0.46286,-7e-05,0.03],"object_to_goal_dist_end":0.2331,"object_to_goal_dist_start":0.23148,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_to_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1652.0,"raw_peak_contact_force":0.13845,"tcp_end":[0.46303,-8e-05,0.15984],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.13382,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":374.0,"n_steps_budget":1000.0,"object_pos_end":[0.46286,-7e-05,0.02602],"object_pos_start":[0.46286,-7e-05,0.02602],"object_to_goal_dist_end":0.2331,"object_to_goal_dist_start":0.2331,"object_z_max":0.02602,"peak_contact_force":26.5509,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1496.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.45866,-0.00011,0.05484],"tcp_start":[0.46303,-8e-05,0.15984],"tcp_to_object_dist_end":0.02912,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.46277,-0.00015,0.02591],"object_pos_start":[0.46286,-7e-05,0.02602],"object_to_goal_dist_end":0.23325,"object_to_goal_dist_start":0.2331,"object_z_max":0.02602,"peak_contact_force":0.12947,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11343.0,"raw_peak_contact_force":0.15221,"tcp_end":[0.45118,-0.00019,0.04744],"tcp_start":[0.45866,-0.00011,0.05484],"tcp_to_object_dist_end":0.02445,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":39.0,"n_steps":836.0,"n_steps_budget":1000.0,"object_pos_end":[0.4625,-7e-05,0.18115],"object_pos_start":[0.46277,-0.00015,0.02591],"object_to_goal_dist_end":0.2206,"object_to_goal_dist_start":0.23325,"object_z_max":0.18097,"peak_contact_force":0.08861,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":31909.0,"raw_peak_contact_force":0.34624,"tcp_end":[0.45887,-0.00017,0.20806],"tcp_start":[0.45118,-0.00019,0.04744],"tcp_to_object_dist_end":0.02715,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":20.0,"n_steps":656.0,"n_steps_budget":1000.0,"object_pos_end":[0.60261,0.1417,0.21524],"object_pos_start":[0.4625,-7e-05,0.18115],"object_to_goal_dist_end":0.09402,"object_to_goal_dist_start":0.2206,"object_z_max":0.24657,"peak_contact_force":0.13626,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":17286.0,"raw_peak_contact_force":0.23443,"tcp_end":[0.59599,0.14028,0.24788],"tcp_start":[0.45887,-0.00017,0.20806],"tcp_to_object_dist_end":0.03334,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":15.0,"n_steps":351.0,"n_steps_budget":1000.0,"object_pos_end":[0.60845,0.15099,0.09295],"object_pos_start":[0.60261,0.1417,0.21524],"object_to_goal_dist_end":0.02935,"object_to_goal_dist_start":0.09402,"object_z_max":0.21524,"peak_contact_force":0.14348,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":5704.0,"raw_peak_contact_force":0.50023,"tcp_end":[0.60413,0.15016,0.12948],"tcp_start":[0.59599,0.14028,0.24788],"tcp_to_object_dist_end":0.0368,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.5872,0.14988,0.02653],"object_pos_start":[0.60845,0.15099,0.09295],"object_to_goal_dist_end":0.09842,"object_to_goal_dist_start":0.02935,"object_z_max":0.09295,"peak_contact_force":0.14904,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1335.0,"raw_peak_contact_force":1.09471,"tcp_end":[0.5973,0.14831,0.1496],"tcp_start":[0.60413,0.15016,0.12948],"tcp_to_object_dist_end":0.12349,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":237.0,"n_steps_budget":750.0,"object_pos_end":[0.58654,0.15002,0.02602],"object_pos_start":[0.5872,0.14988,0.02653],"object_to_goal_dist_end":0.09907,"object_to_goal_dist_start":0.09842,"object_z_max":0.02653,"peak_contact_force":0.12274,"phase_name":"retract_from_goal","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":948.0,"raw_peak_contact_force":0.15866,"tcp_end":[0.60484,0.15121,0.20314],"tcp_start":[0.5973,0.14831,0.1496],"tcp_to_object_dist_end":0.17807,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```