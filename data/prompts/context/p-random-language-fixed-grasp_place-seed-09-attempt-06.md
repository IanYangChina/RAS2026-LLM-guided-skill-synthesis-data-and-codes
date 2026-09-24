## Search State

- **Seed**: 9
- **Iteration**: 7 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 6 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | position_control | impedance_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 9 | 0.0520 | 0.39 | ❌ rejected |
| 5 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | position_control | position_control | position_control | impedance_control | impedance_control | impedance_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 8 | 0.2655 | 0.64 | ✅ accepted |
| 4 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | impedance_control | impedance_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 11 | -0.0794 | 0.37 | ❌ rejected |
| 3 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | impedance_control | impedance_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 10 | -0.0206 | 0.39 | ✅ accepted |
| 2 | rotate → pull → push → descend → descend → grasp → approach | impedance_motion | arc_cartesian | impedance_motion | linear_cartesian | linear_cartesian | — | linear_cartesian | impedance_control | impedance_control | impedance_control | admittance_control | position_control | position_control | position_control | pose_tolerance | time_limit | time_limit | pose_tolerance | contact_detected | grasp_success | pose_tolerance | 6 | -0.1650 | 0.13 | ❌ rejected |

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

## Current Skill (Q=0.052) — your mutation base

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

- **Composite score**: 0.052
- **task_score** (E): 0.389
- **fitness_score**: 0.652  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.600

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_to_object | 1.00 | 1.00 | 0.1332 |
| descend_to_grasp | 1.00 | 1.00 | 0.1130 |
| grasp | 1.00 | 1.00 | 0.0125 |
| lift_object | 1.00 | 1.00 | 0.1616 |
| transport_to_goal | 1.00 | 1.00 | 0.2239 |
| descend_to_place | 1.00 | 1.00 | 0.1137 |
| release_object | 1.00 | 1.00 | 0.0200 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_to_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.510, -0.014, 0.173) | (0.515, -0.017, 0.030)→(0.515, -0.017, 0.026) | 0.268→0.270 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_to_grasp | descend | 1.00 / step_budget | (0.510, -0.014, 0.173)→(0.510, -0.016, 0.060) | (0.515, -0.017, 0.026)→(0.515, -0.017, 0.026) | 0.270→0.270 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp | grasp | 1.00 / step_budget | (0.510, -0.016, 0.060)→(0.502, -0.016, 0.050) | (0.515, -0.017, 0.026)→(0.515, -0.016, 0.026) | 0.270→0.270 | 1.00 / 38.333 | 0.141 | 0.182 |
| lift_object | lift | 1.00 / step_budget | (0.502, -0.016, 0.050)→(0.511, -0.016, 0.212) | (0.515, -0.016, 0.026)→(0.517, -0.017, 0.183) | 0.270→0.232 | 1.00 / 31.333 | 0.113 | 0.319 |
| transport_to_goal | approach | 1.00 / step_budget | (0.511, -0.016, 0.212)→(0.606, 0.162, 0.294) | (0.517, -0.017, 0.183)→(0.612, 0.161, 0.260) | 0.232→0.094 | 1.00 / 15.333 | 0.140 | 0.202 |
| descend_to_place | descend | 1.00 / step_budget | (0.606, 0.162, 0.294)→(0.612, 0.177, 0.182) | (0.612, 0.161, 0.260)→(0.614, 0.174, 0.119) | 0.094→0.051 | 1.00 / 14.000 | 0.163 | 0.799 |
| release_object | release | 1.00 / step_budget | (0.612, 0.177, 0.182)→(0.607, 0.176, 0.201) | (0.614, 0.174, 0.119)→(0.605, 0.171, 0.024) | 0.051→0.146 | 1.00 / 2.667 | 0.195 | 1.201 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.517
- phase_score: 0.346
- phase_breakdown.descend_1_score: 0.801
- phase_breakdown.grasp_1_score: 1.000
- phase_breakdown.transport_arc_score: 0.072
- phase_breakdown.approach_1_score: 0.056
- phase_breakdown.release_1_score: 0.492
- grasp_place_fitness: 0.714

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.714
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.517
- **Median Q (composite search score)**: 0.040
- **K-run variance**: 0.0022
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.352


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.13125,"average_solve_count":320.0,"average_success_count":320.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_to_object.speed":0.09716,"descend_to_grasp.speed":0.06701,"descend_to_place.speed":0.05455,"grasp.grip_force":26.17328,"lift_object.lift_height":0.18748,"lift_object.speed":0.04112,"release_object.hold_time":0.28595,"transport_to_goal.arc_height":0.06319,"transport_to_goal.speed":0.04165},"optimized_scores":{"best_composite_score":0.00217,"best_fitness_score":0.60217,"best_task_score":0.28846},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":164.0,"contact_point_centroid":[0.59178,0.22069,-0.00868],"force_p95":1.41112,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.78615,"mean_force":0.45321,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.60113,0.22025,0.2315]},{"body_a":"world","body_b":"grasp_target","contact_count":85.0,"contact_point_centroid":[0.53392,-0.02038,-0.00156],"force_p95":0.31642,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.33749,"mean_force":0.14452,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.52175,-0.02044,0.05022]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1981.0,"contact_point_centroid":[0.60816,0.2314,0.2676],"force_p95":0.13569,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30383,"mean_force":0.10721,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.60351,0.21324,0.27152]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1945.0,"contact_point_centroid":[0.60805,0.19526,0.26683],"force_p95":0.14382,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29223,"mean_force":0.10913,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.60355,0.21341,0.27062]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":606.0,"contact_point_centroid":[0.60883,0.24025,0.21085],"force_p95":0.12051,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26508,"mean_force":0.08353,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.6041,0.22167,0.2153]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":654.0,"contact_point_centroid":[0.60856,0.20333,0.21162],"force_p95":0.10921,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25441,"mean_force":0.07715,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.60414,0.22169,0.21539]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":7854.0,"contact_point_centroid":[0.52579,-0.03949,0.11703],"force_p95":0.08272,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24149,"mean_force":0.0545,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.52551,-0.0205,0.11646]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":7069.0,"contact_point_centroid":[0.52605,-0.00134,0.11782],"force_p95":0.10405,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23865,"mean_force":0.06129,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.52557,-0.0205,0.11718]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53705,-0.02126,-0.00207],"force_p95":0.1442,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.18836,"mean_force":0.12836,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.52387,-0.02048,0.05078]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":7870.0,"contact_point_centroid":[0.55644,0.07618,0.27137],"force_p95":0.13239,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1784,"mean_force":0.08811,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.55481,0.05748,0.27381]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":10663.0,"contact_point_centroid":[0.5547,0.03595,0.27138],"force_p95":0.11561,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15879,"mean_force":0.06659,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.55375,0.05423,0.27255]},{"body_a":"world","body_b":"grasp_target","contact_count":868.0,"contact_point_centroid":[0.53702,-0.02132,-0.00185],"force_p95":0.13721,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12319,"phase_index":0.0,"phase_name":"approach_to_object","phase_type":"approach","tcp_position_centroid":[0.51281,-0.0082,0.23799]},{"body_a":"world","body_b":"grasp_target","contact_count":1080.0,"contact_point_centroid":[0.53702,-0.02132,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.52803,-0.01888,0.11559]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4348.0,"contact_point_centroid":[0.52364,-0.00127,0.05007],"force_p95":0.07353,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11847,"mean_force":0.04951,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.52269,-0.02046,0.04939]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4924.0,"contact_point_centroid":[0.52355,-0.0396,0.05],"force_p95":0.07008,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07147,"mean_force":0.04445,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.52269,-0.02046,0.04939]}],"total_contact_groups":15},"final_pose_error":0.01472,"key_states":{"actual_goal_position":[0.61031,0.22775,0.20741],"final_object_position":[0.60185,0.21775,0.02139],"final_tcp_position":[0.60601,0.22225,0.22037],"realised_goal_position":[0.61031,0.22775,0.20741],"realised_object_initial_position":[0.53702,-0.02132,0.03]},"peak_contact_force":1.78615,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":218.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.03],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31446,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_to_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":868.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.52747,-0.01723,0.17241],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.14676,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":270.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.12262,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1080.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.53112,-0.0206,0.05951],"tcp_start":[0.52747,-0.01723,0.17241],"tcp_to_object_dist_end":0.03401,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":42.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53697,-0.02072,0.02572],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31644,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.14268,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11072.0,"raw_peak_contact_force":0.18836,"subtask_id":"grasp_1","tcp_end":[0.52266,-0.02046,0.04935],"tcp_start":[0.53112,-0.0206,0.05951],"tcp_to_object_dist_end":0.02763,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":36.0,"n_steps":387.0,"n_steps_budget":1000.0,"object_pos_end":[0.54066,-0.02098,0.16156],"object_pos_start":[0.53697,-0.02072,0.02572],"object_to_goal_dist_end":0.26234,"object_to_goal_dist_start":0.31644,"object_z_max":0.16121,"peak_contact_force":0.11373,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":15008.0,"raw_peak_contact_force":0.33749,"tcp_end":[0.53206,-0.02062,0.1888],"tcp_start":[0.52266,-0.02046,0.04935],"tcp_to_object_dist_end":0.02856,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":16.0,"n_steps":733.0,"n_steps_budget":1000.0,"object_pos_end":[0.6072,0.20333,0.29009],"object_pos_start":[0.54066,-0.02098,0.16156],"object_to_goal_dist_end":0.08626,"object_to_goal_dist_start":0.26234,"object_z_max":0.29566,"peak_contact_force":0.13037,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":18533.0,"raw_peak_contact_force":0.1784,"subtask_id":"transport_arc","tcp_end":[0.60211,0.20478,0.32415],"tcp_start":[0.53206,-0.02062,0.1888],"tcp_to_object_dist_end":0.03447,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":19.0,"n_steps":230.0,"n_steps_budget":1000.0,"object_pos_end":[0.61091,0.22151,0.18389],"object_pos_start":[0.6072,0.20333,0.29009],"object_to_goal_dist_end":0.02434,"object_to_goal_dist_start":0.08626,"object_z_max":0.29009,"peak_contact_force":0.12181,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3926.0,"raw_peak_contact_force":0.30383,"tcp_end":[0.60601,0.22225,0.22037],"tcp_start":[0.60211,0.20478,0.32415],"tcp_to_object_dist_end":0.03681,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.60185,0.21775,0.02139],"object_pos_start":[0.61091,0.22151,0.18389],"object_to_goal_dist_end":0.18648,"object_to_goal_dist_start":0.02434,"object_z_max":0.18389,"peak_contact_force":0.24691,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1424.0,"raw_peak_contact_force":1.78615,"subtask_id":"release_1","tcp_end":[0.6011,0.22024,0.23904],"tcp_start":[0.60601,0.22225,0.22037],"tcp_to_object_dist_end":0.21767,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.97321,"average_solve_count":448.0,"average_success_count":448.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_to_object.speed":0.03478,"descend_to_grasp.speed":0.04515,"descend_to_place.speed":0.04741,"grasp.grip_force":20.19796,"lift_object.lift_height":0.2452,"lift_object.speed":0.03045,"release_object.hold_time":0.28143,"transport_to_goal.arc_height":0.17072,"transport_to_goal.speed":0.02878},"optimized_scores":{"best_composite_score":0.03953,"best_fitness_score":0.63953,"best_task_score":0.36276},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":182.0,"contact_point_centroid":[0.61504,0.15936,-0.00747],"force_p95":1.24934,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.58598,"mean_force":0.3916,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.62198,0.15886,0.19943]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2164.0,"contact_point_centroid":[0.62928,0.17062,0.24331],"force_p95":0.13362,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.47613,"mean_force":0.10783,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.62425,0.15246,0.2469]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2153.0,"contact_point_centroid":[0.62897,0.13448,0.24248],"force_p95":0.14255,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.42073,"mean_force":0.109,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.62431,0.15259,0.24602]},{"body_a":"world","body_b":"grasp_target","contact_count":88.0,"contact_point_centroid":[0.54239,-0.02802,-0.00163],"force_p95":0.31861,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.33879,"mean_force":0.15121,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.52979,-0.02797,0.04958]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":606.0,"contact_point_centroid":[0.63072,0.17862,0.18109],"force_p95":0.1199,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29063,"mean_force":0.08369,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.62554,0.16003,0.18499]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":658.0,"contact_point_centroid":[0.63036,0.14168,0.18141],"force_p95":0.1085,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27658,"mean_force":0.07717,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.62558,0.16004,0.18506]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":10882.0,"contact_point_centroid":[0.53467,-0.04709,0.14442],"force_p95":0.08235,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24637,"mean_force":0.05433,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.53409,-0.02807,0.14372]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":9974.0,"contact_point_centroid":[0.53469,-0.00894,0.14596],"force_p95":0.09343,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2359,"mean_force":0.05999,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.53421,-0.02808,0.14538]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.54564,-0.02916,-0.00211],"force_p95":0.15251,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.20913,"mean_force":0.13056,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.53201,-0.02804,0.05025]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6509.0,"contact_point_centroid":[0.56935,0.04941,0.3015],"force_p95":0.12946,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15629,"mean_force":0.08184,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.56802,0.03072,0.30342]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8332.0,"contact_point_centroid":[0.56888,0.01218,0.3031],"force_p95":0.1166,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.153,"mean_force":0.06522,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.56792,0.03052,0.3041]},{"body_a":"world","body_b":"grasp_target","contact_count":960.0,"contact_point_centroid":[0.5456,-0.02923,-0.00186],"force_p95":0.13692,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12314,"phase_index":0.0,"phase_name":"approach_to_object","phase_type":"approach","tcp_position_centroid":[0.51556,-0.01113,0.23834]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4341.0,"contact_point_centroid":[0.53192,-0.00881,0.04959],"force_p95":0.07457,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12654,"mean_force":0.04954,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.53081,-0.028,0.04881]},{"body_a":"world","body_b":"grasp_target","contact_count":1104.0,"contact_point_centroid":[0.5456,-0.02923,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.53546,-0.02594,0.11504]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4963.0,"contact_point_centroid":[0.53182,-0.04716,0.04958],"force_p95":0.07149,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07326,"mean_force":0.04426,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.53081,-0.028,0.04882]}],"total_contact_groups":15},"final_pose_error":0.01485,"key_states":{"actual_goal_position":[0.63284,0.16493,0.17692],"final_object_position":[0.62048,0.15668,0.02555],"final_tcp_position":[0.62772,0.16049,0.19014],"realised_goal_position":[0.63284,0.16493,0.17692],"realised_object_initial_position":[0.5456,-0.02923,0.03]},"peak_contact_force":1.58598,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":241.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.03],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.25864,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_to_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":960.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.53431,-0.02376,0.17141],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.14593,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":276.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1104.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.53933,-0.02824,0.05925],"tcp_start":[0.53431,-0.02376,0.17141],"tcp_to_object_dist_end":0.03383,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":42.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54556,-0.02841,0.02561],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26057,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.15018,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11104.0,"raw_peak_contact_force":0.20913,"subtask_id":"grasp_1","tcp_end":[0.53078,-0.028,0.04878],"tcp_start":[0.53933,-0.02824,0.05925],"tcp_to_object_dist_end":0.02748,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":35.0,"n_steps":547.0,"n_steps_budget":1000.0,"object_pos_end":[0.54885,-0.02886,0.21818],"object_pos_start":[0.54556,-0.02841,0.02561],"object_to_goal_dist_end":0.2152,"object_to_goal_dist_start":0.26057,"object_z_max":0.21783,"peak_contact_force":0.10979,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":20944.0,"raw_peak_contact_force":0.33879,"tcp_end":[0.54159,-0.02829,0.24614],"tcp_start":[0.53078,-0.028,0.04878],"tcp_to_object_dist_end":0.02889,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":15.0,"n_steps":561.0,"n_steps_budget":1000.0,"object_pos_end":[0.62817,0.14364,0.27347],"object_pos_start":[0.54885,-0.02886,0.21818],"object_to_goal_dist_end":0.09898,"object_to_goal_dist_start":0.2152,"object_z_max":0.3028,"peak_contact_force":0.14139,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":14841.0,"raw_peak_contact_force":0.15629,"subtask_id":"transport_arc","tcp_end":[0.6222,0.14481,0.30673],"tcp_start":[0.54159,-0.02829,0.24614],"tcp_to_object_dist_end":0.03381,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":19.0,"n_steps":254.0,"n_steps_budget":1000.0,"object_pos_end":[0.63295,0.15998,0.15451],"object_pos_start":[0.62817,0.14364,0.27347],"object_to_goal_dist_end":0.02295,"object_to_goal_dist_start":0.09898,"object_z_max":0.27347,"peak_contact_force":0.1227,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4317.0,"raw_peak_contact_force":0.47613,"tcp_end":[0.62772,0.16049,0.19014],"tcp_start":[0.6222,0.14481,0.30673],"tcp_to_object_dist_end":0.03602,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.62048,0.15668,0.02555],"object_pos_start":[0.63295,0.15998,0.15451],"object_to_goal_dist_end":0.1521,"object_to_goal_dist_start":0.02295,"object_z_max":0.15451,"peak_contact_force":0.21411,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1446.0,"raw_peak_contact_force":1.58598,"subtask_id":"release_1","tcp_end":[0.62194,0.15885,0.20866],"tcp_start":[0.62772,0.16049,0.19014],"tcp_to_object_dist_end":0.18313,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.50388,"average_solve_count":258.0,"average_success_count":258.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_to_object.speed":0.10487,"descend_to_grasp.speed":0.07678,"descend_to_place.speed":0.0736,"grasp.grip_force":24.29414,"lift_object.lift_height":0.19855,"lift_object.speed":0.03143,"release_object.hold_time":0.24007,"transport_to_goal.arc_height":0.1828,"transport_to_goal.speed":0.10386},"optimized_scores":{"best_composite_score":0.11438,"best_fitness_score":0.71438,"best_task_score":0.51694},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":139.0,"contact_point_centroid":[0.59191,0.13873,-0.0075],"force_p95":1.15338,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.61711,"mean_force":0.44719,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.60269,0.14839,0.14283]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1413.0,"contact_point_centroid":[0.59998,0.15869,0.2108],"force_p95":0.16708,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.4605,"mean_force":0.1137,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.59516,0.14065,0.21549]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1370.0,"contact_point_centroid":[0.59978,0.12254,0.21034],"force_p95":0.16954,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.39493,"mean_force":0.11556,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.59524,0.14073,0.21475]},{"body_a":"world","body_b":"grasp_target","contact_count":85.0,"contact_point_centroid":[0.45975,-0.00052,-0.00153],"force_p95":0.26564,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.28115,"mean_force":0.1317,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.45113,-0.0002,0.05366]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4324.0,"contact_point_centroid":[0.51073,0.06899,0.24904],"force_p95":0.15122,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27241,"mean_force":0.10843,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.50752,0.05067,0.2522]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4479.0,"contact_point_centroid":[0.45302,-0.01895,0.11836],"force_p95":0.11929,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2629,"mean_force":0.08513,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.45352,-0.00027,0.12051]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4837.0,"contact_point_centroid":[0.45369,0.01824,0.11859],"force_p95":0.11076,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25763,"mean_force":0.08073,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.45356,-0.00027,0.12116]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.59163,0.13846,-0.00215],"force_p95":0.14745,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.23168,"mean_force":0.11598,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.59849,0.14801,0.1348]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4773.0,"contact_point_centroid":[0.51427,0.03629,0.25051],"force_p95":0.15048,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23163,"mean_force":0.09966,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.51128,0.05447,0.25393]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.46285,-0.00013,-0.00202],"force_p95":0.13003,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.14811,"mean_force":0.12495,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.45308,-0.00018,0.05397]},{"body_a":"world","body_b":"grasp_target","contact_count":820.0,"contact_point_centroid":[0.46286,-7e-05,-0.00184],"force_p95":0.13728,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12322,"phase_index":0.0,"phase_name":"approach_to_object","phase_type":"approach","tcp_position_centroid":[0.48427,-4e-05,0.23885]},{"body_a":"world","body_b":"grasp_target","contact_count":1096.0,"contact_point_centroid":[0.46286,-7e-05,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.46267,-9e-05,0.11721]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3162.0,"contact_point_centroid":[0.45251,-0.01902,0.05132],"force_p95":0.09818,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09978,"mean_force":0.06443,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.45203,-0.00019,0.05294]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3414.0,"contact_point_centroid":[0.45302,0.01849,0.05094],"force_p95":0.0913,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09203,"mean_force":0.06066,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.45203,-0.00019,0.05294]}],"total_contact_groups":14},"final_pose_error":0.01462,"key_states":{"actual_goal_position":[0.61015,0.15287,0.12219],"final_object_position":[0.59169,0.1385,0.02602],"final_tcp_position":[0.60357,0.14931,0.13475],"realised_goal_position":[0.61015,0.15287,0.12219],"realised_object_initial_position":[0.46286,-7e-05,0.03]},"peak_contact_force":1.61711,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":206.0,"n_steps_budget":1000.0,"object_pos_end":[0.46286,-7e-05,0.02602],"object_pos_start":[0.46286,-7e-05,0.03],"object_to_goal_dist_end":0.2331,"object_to_goal_dist_start":0.23148,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_to_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":820.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.46769,-7e-05,0.17394],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.148,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":274.0,"n_steps_budget":1000.0,"object_pos_end":[0.46286,-7e-05,0.02602],"object_pos_start":[0.46286,-7e-05,0.02602],"object_to_goal_dist_end":0.2331,"object_to_goal_dist_start":0.2331,"object_z_max":0.02602,"peak_contact_force":0.12262,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1096.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.45959,-0.00011,0.06061],"tcp_start":[0.46769,-7e-05,0.17394],"tcp_to_object_dist_end":0.03474,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":31.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.46277,-0.00031,0.02588],"object_pos_start":[0.46286,-7e-05,0.02602],"object_to_goal_dist_end":0.23337,"object_to_goal_dist_start":0.2331,"object_z_max":0.02602,"peak_contact_force":0.12956,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":8376.0,"raw_peak_contact_force":0.14811,"subtask_id":"grasp_1","tcp_end":[0.452,-0.00019,0.05291],"tcp_start":[0.45959,-0.00011,0.06061],"tcp_to_object_dist_end":0.0291,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":380.0,"n_steps_budget":1000.0,"object_pos_end":[0.46252,-0.00043,0.16976],"object_pos_start":[0.46277,-0.00031,0.02588],"object_to_goal_dist_end":0.21808,"object_to_goal_dist_start":0.23337,"object_z_max":0.16938,"peak_contact_force":0.11501,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":9401.0,"raw_peak_contact_force":0.28115,"tcp_end":[0.45866,-0.00032,0.20014],"tcp_start":[0.452,-0.00019,0.05291],"tcp_to_object_dist_end":0.03063,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":15.0,"n_steps":502.0,"n_steps_budget":1000.0,"object_pos_end":[0.5998,0.13738,0.21586],"object_pos_start":[0.46252,-0.00043,0.16976],"object_to_goal_dist_end":0.0955,"object_to_goal_dist_start":0.21808,"object_z_max":0.24562,"peak_contact_force":0.14812,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":9097.0,"raw_peak_contact_force":0.27241,"subtask_id":"transport_arc","tcp_end":[0.59339,0.13731,0.25178],"tcp_start":[0.45866,-0.00032,0.20014],"tcp_to_object_dist_end":0.03649,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":257.0,"n_steps_budget":1000.0,"object_pos_end":[0.59766,0.14171,0.0172],"object_pos_start":[0.5998,0.13738,0.21586],"object_to_goal_dist_end":0.10632,"object_to_goal_dist_start":0.0955,"object_z_max":0.21586,"peak_contact_force":0.24333,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2922.0,"raw_peak_contact_force":1.61711,"tcp_end":[0.60357,0.14931,0.13475],"tcp_start":[0.59339,0.13731,0.25178],"tcp_to_object_dist_end":0.11795,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.59169,0.1385,0.02602],"object_pos_start":[0.59766,0.14171,0.0172],"object_to_goal_dist_end":0.09897,"object_to_goal_dist_start":0.10632,"object_z_max":0.0267,"peak_contact_force":0.12316,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":800.0,"raw_peak_contact_force":0.23168,"subtask_id":"release_1","tcp_end":[0.59671,0.14749,0.15459],"tcp_start":[0.60357,0.14931,0.13475],"tcp_to_object_dist_end":0.12899,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```