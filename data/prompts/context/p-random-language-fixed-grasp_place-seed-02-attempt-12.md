## Search State

- **Seed**: 2
- **Iteration**: 13 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 12 | approach → descend → grasp → lift → push → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | — | linear_cartesian | position_control | position_control | position_control | impedance_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 12 | -0.5804 | 0.17 | ❌ rejected |
| 11 | approach → descend → grasp → lift → push → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | — | linear_cartesian | position_control | position_control | impedance_control | impedance_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 12 | -0.5948 | 0.14 | ❌ rejected |
| 10 | approach → descend → grasp → lift → push → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | — | linear_cartesian | position_control | force_threshold_switch | position_control | impedance_control | position_control | position_control | position_control | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 13 | -0.4045 | 0.12 | ❌ rejected |
| 9 | approach → descend → grasp → lift → push → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | — | linear_cartesian | position_control | position_control | position_control | impedance_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 12 | -0.5760 | 0.18 | ✅ accepted |
| 8 | approach → descend → contact → grasp → lift → push → release → retract | arc_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | — | linear_cartesian | position_control | position_control | force_threshold_switch | position_control | impedance_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 14 | -0.6090 | 0.14 | ❌ rejected |

**Proposal policy**: task_score is 0.17 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `67b45068113fe0ef6f199d4981822d51bd0bd66bb4f388f7402a08094b41852a`
- Frozen object start: [0.4761612134249316, -0.02015088565858767, 0.03]
- Frozen task target: [0.631422574059428, 0.1591915942135097, 0.1900150788948481]
- Goal object position: (0.631422574059428, 0.1591915942135097, 0.1900150788948481)
- place_goal_position (task success criterion — final object 3D position must be close to the realised airborne target here): (0.631422574059428, 0.1591915942135097, 0.1900150788948481)
- Grasp/lift components are optimiser fitness diagnostics only; canonical task_score is final object-to-realised-target proximity.
- Object initial pose: (0.4761612134249316, -0.02015088565858767, 0.03)
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
  frozen_object_start: [0.4762, -0.0202, 0.03]
  frozen_task_target: [0.6314, 0.1592, 0.19]
  frozen_object_starts: {'grasp_target': [0.4761612134249316, -0.02015088565858767, 0.03]}
  frozen_targets: {'place_target': [0.631422574059428, 0.1591915942135097, 0.1900150788948481]}
  goal_tolerance_m: 0.02
  force_limit_n: 20
  force_scale_n: 5
  realized_scene_sha256: 67b45068113fe0ef6f199d4981822d51bd0bd66bb4f388f7402a08094b41852a

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

## Current Skill (Q=-0.580) — your mutation base

```yaml
skill: grasp_place
dsl_version: 2
skill_type: arm_gripper
subtasks:
- id: approach_1
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.1
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
    - 0.1
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - 1.0
      align_with: world_z
      tolerance: 0.1
  parameters:
    approach_height:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.1
      binds_to:
      - path: target.offset.z
        mode: replace
    speed:
      type: scalar
      range:
      - 0.02
      - 0.5
      default: 0.1
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: approach_1
- id: descend_1
  type: descend
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
    - 0.02
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - 1.0
      align_with: world_z
      tolerance: 0.1
  parameters:
    grasp_z_offset:
      type: scalar
      range:
      - -0.01
      - 0.05
      default: 0.02
      binds_to:
      - path: target.offset.z
        mode: replace
    speed:
      type: scalar
      range:
      - 0.02
      - 0.5
      default: 0.05
      binds_to:
      - path: generator.speed
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
  parameters:
    grasp_force:
      type: scalar
      range:
      - 0.1
      - 1.0
      default: 0.5
      binds_to:
      - path: guards.grasp_check.threshold
        mode: replace
  guards:
  - id: grasp_check
    when: after_phase
    predicate: bilateral_grasp
    threshold: 0.9
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: repeat
  subtask_id: grasp_1
- id: lift_1
  type: lift
  generator: linear_cartesian
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    entity: grasp_target
    offset:
    - 0.0
    - 0.0
    - 0.1
    offset_along_axis:
      distance: 0.1
      axis: world_z
      mode: add_to_offset
      sign: positive
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - 1.0
      align_with: world_z
      tolerance: 0.1
  parameters:
    lift_height:
      type: scalar
      range:
      - 0.05
      - 0.15
      default: 0.1
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    lift_speed:
      type: scalar
      range:
      - 0.02
      - 0.5
      default: 0.08
      binds_to:
      - path: generator.speed
        mode: replace
- id: transport_1
  type: push
  generator: arc_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    entity: placement_surface
    offset:
    - 0.0
    - 0.0
    - 0.1
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - 1.0
      align_with: world_z
      tolerance: 0.1
  parameters:
    arc_height:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.1
      binds_to:
      - path: generator.arc_height
        mode: replace
    transport_speed:
      type: scalar
      range:
      - 0.02
      - 0.5
      default: 0.1
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: transport_arc
- id: release_1
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
    release_time:
      type: scalar
      range:
      - 0.1
      - 0.5
      default: 0.3
      binds_to:
      - path: duration.max_time
        mode: replace
  subtask_id: release_1
- id: retract_1
  type: retract
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
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - 1.0
      align_with: world_z
      tolerance: 0.1
  parameters:
    retract_height:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.1
      binds_to:
      - path: target.offset.z
        mode: replace
    retract_speed:
      type: scalar
      range:
      - 0.02
      - 0.5
      default: 0.1
      binds_to:
      - path: generator.speed
        mode: replace

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.1]
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=world_z, tolerance=0.1
  - parameter_bindings:
    - approach_height: status=consumed; consumers=target.offset.z (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
- **descend_1** (`descend`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.02]
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=world_z, tolerance=0.1
  - parameter_bindings:
    - grasp_z_offset: status=consumed; consumers=target.offset.z (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
- **grasp_1** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings:
    - grasp_force: status=consumed; consumers=guards.grasp_check.threshold (replace)
  - guards:
    - id=grasp_check, when=after_phase, predicate=bilateral_grasp, on_failure=retry, threshold=0.9
  - retries: max_attempts=2, strategy=repeat
- **lift_1** (`lift`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.1], offset_along_axis={axis=world_z, distance=0.1, mode=add_to_offset, sign=positive}
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=world_z, tolerance=0.1
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - lift_speed: status=consumed; consumers=generator.speed (replace)
- **transport_1** (`push`)
  - target: source=yaml, anchor=task_goal, entity=placement_surface, offset=[0.0, 0.0, 0.1]
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=world_z, tolerance=0.1
  - parameter_bindings:
    - arc_height: status=consumed; consumers=generator.arc_height (replace)
    - transport_speed: status=consumed; consumers=generator.speed (replace)
- **release_1** (`release`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings:
    - release_time: status=consumed; consumers=duration.max_time (replace)
- **retract_1** (`retract`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.1]
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=world_z, tolerance=0.1
  - parameter_bindings:
    - retract_height: status=consumed; consumers=target.offset.z (replace)
    - retract_speed: status=consumed; consumers=generator.speed (replace)

## Design Metrics

- **Composite score**: -0.580
- **task_score** (E): 0.167
- **fitness_score**: 0.170  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.750

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 0.00 | 1.00 | 0.1635 |
| descend_1 | 0.00 | 1.00 | 0.0523 |
| grasp_1 | 1.00 | 1.00 | 0.0000 |
| lift_1 | 0.00 | 1.00 | 0.1273 |
| transport_1 | 0.67 | 1.00 | 0.2128 |
| release_1 | 1.00 | 1.00 | 0.0259 |
| retract_1 | 1.00 | 1.00 | 0.1104 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 0.00 / step_budget | (0.500, -0.000, 0.301)→(0.421, -0.004, 0.160) | (0.493, -0.015, 0.030)→(0.455, -0.010, 0.016) | 0.279→0.304 | 1.00 / 5.000 | 248.029 | 1444.946 |
| descend_1 | descend | 0.00 / step_budget | (0.421, -0.004, 0.160)→(0.464, -0.027, 0.171) | (0.455, -0.010, 0.016)→(0.455, -0.010, 0.016) | 0.304→0.304 | 1.00 / 4.667 | 45053.758 | 847.223 |
| grasp_1 | grasp | 1.00 / step_budget | (0.464, -0.027, 0.170)→(0.464, -0.027, 0.170) | (0.455, -0.010, 0.016)→(0.455, -0.010, 0.016) | 0.304→0.304 | 1.00 / 9.333 | 91046.569 | 188.940 |
| lift_1 | lift | 0.00 / step_budget | (0.464, -0.027, 0.170)→(0.453, 0.096, 0.195) | (0.455, -0.010, 0.016)→(0.455, -0.010, 0.016) | 0.304→0.304 | 1.00 / 9.333 | 91081.672 | 446.012 |
| transport_1 | push | 0.67 / step_budget | (0.453, 0.096, 0.195)→(0.622, 0.172, 0.293) | (0.455, -0.010, 0.016)→(0.462, 0.049, 0.016) | 0.304→0.269 | 1.00 / 9.333 | 91242.287 | 813.085 |
| release_1 | release | 1.00 / step_budget | (0.622, 0.172, 0.293)→(0.623, 0.172, 0.319) | (0.462, 0.049, 0.016)→(0.462, 0.049, 0.016) | 0.269→0.269 | 1.00 / 4.000 | 0.123 | 192.671 |
| retract_1 | retract | 1.00 / step_budget | (0.623, 0.172, 0.319)→(0.624, 0.171, 0.429) | (0.462, 0.049, 0.016)→(0.462, 0.049, 0.016) | 0.269→0.269 | 1.00 / 4.000 | 0.123 | 0.123 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 0.000
- place_accuracy: 0.000
- lift_clearance: 0.000
- transport_retention: None
- terminal_score: 0.183
- phase_score: 0.241
- phase_breakdown.grasp_1_score: 1.000
- phase_breakdown.transport_arc_score: 0.125
- phase_breakdown.descend_1_score: 0.090
- phase_breakdown.approach_1_score: 0.045
- phase_breakdown.release_1_score: 0.074
- grasp_place_fitness: 0.180

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.180
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.183
- **Median Q (composite search score)**: -0.581
- **K-run variance**: 0.0001
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.256


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `dde525b5f1d1bd9dc458c18c8bb170b8849a392c0909c5e3e8e19baca2e18946`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.05,0.05],"goal_z_delta":0.15,"object_xy_delta":[0.05,0.05]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `3eaf951d4314ad541ffae42f4c615c856bb77d128e3ae1cab520a1988305ba67`; realized-scene SHA-256: `67b45068113fe0ef6f199d4981822d51bd0bd66bb4f388f7402a08094b41852a`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.47616,-0.02015,0.03]},{"name":"goal","value":[0.63142,0.15919,0.19002]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.47616,-0.02015,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.63142,0.15919,0.19002]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":7.2551,"average_solve_count":98.0,"average_success_count":98.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.13483,"approach_1.speed":0.11646,"descend_1.grasp_z_offset":0.02057,"descend_1.speed":0.23809,"grasp_1.grasp_force":0.36911,"lift_1.lift_height":0.11923,"lift_1.lift_speed":0.27963,"release_1.release_time":0.29967,"retract_1.retract_height":0.10383,"retract_1.retract_speed":0.36527,"transport_1.arc_height":0.13661,"transport_1.transport_speed":0.32522},"optimized_scores":{"best_composite_score":-0.56974,"best_fitness_score":0.18026,"best_task_score":0.18265},"replay_outcomes":[{"contacts":{"omitted_contact_groups":6,"reported_contact_groups":[{"body_a":"world","body_b":"link7","contact_count":22.0,"contact_point_centroid":[0.52686,0.0018,-0.003],"force_p95":463.27621,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1195.72521,"mean_force":76.51747,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.37289,-0.00211,0.04995]},{"body_a":"world","body_b":"link6","contact_count":886.0,"contact_point_centroid":[0.63156,-0.00511,-0.00046],"force_p95":203.36888,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1161.4117,"mean_force":201.35085,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.3956,-0.00514,0.13158]},{"body_a":"world","body_b":"link6","contact_count":975.0,"contact_point_centroid":[0.62461,-0.01215,-0.00021],"force_p95":494.77226,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":914.0599,"mean_force":286.93641,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.42622,-0.01516,0.1902]},{"body_a":"world","body_b":"link6","contact_count":313.0,"contact_point_centroid":[0.49987,-0.03992,-0.00015],"force_p95":559.48736,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":711.56775,"mean_force":356.95631,"phase_index":4.0,"phase_name":"transport_1","phase_type":"push","tcp_position_centroid":[0.48935,0.05714,0.26212]},{"body_a":"world","body_b":"link6","contact_count":465.0,"contact_point_centroid":[0.59762,-0.06423,-0.00013],"force_p95":295.33943,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":366.78939,"mean_force":235.90043,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.45209,0.08791,0.15978]},{"body_a":"world","body_b":"link6","contact_count":547.0,"contact_point_centroid":[0.67893,-0.01796,-0.00012],"force_p95":71.24834,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":185.4014,"mean_force":68.83385,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46408,-0.04518,0.16617]},{"body_a":"world","body_b":"link6","contact_count":85.0,"contact_point_centroid":[0.60219,0.13492,-0.00013],"force_p95":153.73383,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":166.6376,"mean_force":70.56695,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.61598,0.15549,0.29321]},{"body_a":"link5","body_b":"hand","contact_count":30.0,"contact_point_centroid":[0.44057,-0.05739,0.26331],"force_p95":147.23802,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":156.18173,"mean_force":114.56542,"phase_index":4.0,"phase_name":"transport_1","phase_type":"push","tcp_position_centroid":[0.4807,0.03566,0.28278]},{"body_a":"grasp_target","body_b":"hand","contact_count":40.0,"contact_point_centroid":[0.45594,-0.01212,0.04007],"force_p95":3.61804,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":3.99638,"mean_force":1.65829,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.38325,-0.00208,0.05229]},{"body_a":"grasp_target","body_b":"link6","contact_count":301.0,"contact_point_centroid":[0.4639,-0.00396,0.03541],"force_p95":1.19711,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":2.89754,"mean_force":0.43439,"phase_index":4.0,"phase_name":"transport_1","phase_type":"push","tcp_position_centroid":[0.50628,0.05143,0.28788]},{"body_a":"world","body_b":"grasp_target","contact_count":1816.0,"contact_point_centroid":[0.44131,0.01926,-0.00294],"force_p95":0.49498,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.28192,"mean_force":0.21734,"phase_index":4.0,"phase_name":"transport_1","phase_type":"push","tcp_position_centroid":[0.51925,0.08721,0.27409]},{"body_a":"world","body_b":"grasp_target","contact_count":3931.0,"contact_point_centroid":[0.44036,-0.01887,-0.00213],"force_p95":0.13759,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.25679,"mean_force":0.13788,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.40707,-0.00472,0.14027]},{"body_a":"grasp_target","body_b":"link7","contact_count":28.0,"contact_point_centroid":[0.48182,-0.00353,0.01135],"force_p95":0.6762,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.69701,"mean_force":0.27806,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.37324,-0.00212,0.05418]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.45844,0.08959,-0.00199],"force_p95":0.12284,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12397,"mean_force":0.12264,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.61602,0.15533,0.29943]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.43542,-0.01867,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.42707,-0.01539,0.19027]},{"body_a":"world","body_b":"grasp_target","contact_count":2200.0,"contact_point_centroid":[0.43542,-0.01867,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46408,-0.04517,0.16617]}],"total_contact_groups":22},"final_pose_error":0.01473,"key_states":{"actual_goal_position":[0.63142,0.15919,0.19002],"final_object_position":[0.45844,0.08959,0.01602],"final_tcp_position":[0.61704,0.15443,0.40851],"realised_goal_position":[0.63142,0.15919,0.19002],"realised_object_initial_position":[0.47616,-0.02015,0.03]},"peak_contact_force":273004.12057,"phases":[{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.43542,-0.01867,0.01602],"object_pos_start":[0.47616,-0.02015,0.03],"object_to_goal_dist_end":0.31675,"object_to_goal_dist_start":0.28614,"object_z_max":0.03,"peak_contact_force":197.38335,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4907.0,"raw_peak_contact_force":1195.72521,"subtask_id":"approach_1","tcp_end":[0.41231,-0.00992,0.17101],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.15695,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.43542,-0.01867,0.01602],"object_pos_start":[0.43542,-0.01867,0.01602],"object_to_goal_dist_end":0.31675,"object_to_goal_dist_start":0.31675,"object_z_max":0.01602,"peak_contact_force":134400.05046,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4975.0,"raw_peak_contact_force":914.0599,"subtask_id":"descend_1","tcp_end":[0.46419,-0.04333,0.16764],"tcp_start":[0.41231,-0.00992,0.17101],"tcp_to_object_dist_end":0.15628,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":150.0,"n_steps_budget":50.0,"object_pos_end":[0.43542,-0.01867,0.01602],"object_pos_start":[0.43542,-0.01867,0.01602],"object_to_goal_dist_end":0.31675,"object_to_goal_dist_start":0.31675,"object_z_max":0.01602,"peak_contact_force":68.13073,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":3520.0,"raw_peak_contact_force":185.4014,"subtask_id":"grasp_1","tcp_end":[0.46406,-0.04517,0.16606],"tcp_start":[0.46407,-0.04517,0.16606],"tcp_to_object_dist_end":0.15503,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":498.0,"n_steps_budget":600.0,"object_pos_end":[0.43542,-0.01867,0.01602],"object_pos_start":[0.43542,-0.01867,0.01602],"object_to_goal_dist_end":0.31675,"object_to_goal_dist_start":0.31675,"object_z_max":0.01602,"peak_contact_force":81.55692,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":4559.0,"raw_peak_contact_force":366.78939,"tcp_end":[0.44689,0.11953,0.17759],"tcp_start":[0.46406,-0.04517,0.16606],"tcp_to_object_dist_end":0.21292,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":571.0,"n_steps_budget":600.0,"object_pos_end":[0.45841,0.08954,0.01603],"object_pos_start":[0.43542,-0.01867,0.01602],"object_to_goal_dist_end":0.25506,"object_to_goal_dist_start":0.31675,"object_z_max":0.0194,"peak_contact_force":296.2647,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":4948.0,"raw_peak_contact_force":711.56775,"subtask_id":"transport_arc","tcp_end":[0.61593,0.15571,0.29283],"tcp_start":[0.44689,0.11953,0.17759],"tcp_to_object_dist_end":0.32528,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.45844,0.08959,0.01602],"object_pos_start":[0.45841,0.08954,0.01603],"object_to_goal_dist_end":0.25503,"object_to_goal_dist_start":0.25506,"object_z_max":0.01603,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1107.0,"raw_peak_contact_force":166.6376,"subtask_id":"release_1","tcp_end":[0.61619,0.15518,0.31936],"tcp_start":[0.61593,0.15571,0.29283],"tcp_to_object_dist_end":0.34814,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":524.0,"n_steps_budget":600.0,"object_pos_end":[0.45844,0.08959,0.01602],"object_pos_start":[0.45844,0.08959,0.01602],"object_to_goal_dist_end":0.25503,"object_to_goal_dist_start":0.25503,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2096.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.61704,0.15443,0.40851],"tcp_start":[0.61619,0.15518,0.31936],"tcp_to_object_dist_end":0.42826,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `92fc0f2bbc35407e7976a239cbab7bb266e8a517486aa3be6bd6666f4c63f38d`; realized-scene SHA-256: `5ce27bcdb8582e1d517b17df0f9c2ad7b05701113a75707627744a889253e6a7`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.45856,-0.02632,0.03]},{"name":"goal","value":[0.63013,0.20822,0.11412]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.45856,-0.02632,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.63013,0.20822,0.11412]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":6.94286,"average_solve_count":105.0,"average_success_count":105.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.11415,"approach_1.speed":0.02106,"descend_1.grasp_z_offset":0.00478,"descend_1.speed":0.26189,"grasp_1.grasp_force":0.60651,"lift_1.lift_height":0.06791,"lift_1.lift_speed":0.2995,"release_1.release_time":0.29128,"retract_1.retract_height":0.11471,"retract_1.retract_speed":0.17862,"transport_1.arc_height":0.12062,"transport_1.transport_speed":0.21433},"optimized_scores":{"best_composite_score":-0.59067,"best_fitness_score":0.15933,"best_task_score":0.15005},"replay_outcomes":[{"contacts":{"omitted_contact_groups":6,"reported_contact_groups":[{"body_a":"world","body_b":"link6","contact_count":885.0,"contact_point_centroid":[0.6256,-0.00243,-0.00049],"force_p95":194.22171,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1673.18061,"mean_force":201.15894,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.38251,-0.00246,0.12118]},{"body_a":"world","body_b":"link6","contact_count":311.0,"contact_point_centroid":[0.54524,0.06413,-0.00019],"force_p95":826.36874,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1036.46768,"mean_force":470.31558,"phase_index":4.0,"phase_name":"transport_1","phase_type":"push","tcp_position_centroid":[0.54002,0.11241,0.28251]},{"body_a":"world","body_b":"link6","contact_count":977.0,"contact_point_centroid":[0.62352,-0.01022,-0.00021],"force_p95":469.6513,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":934.4335,"mean_force":291.30322,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.42336,-0.01274,0.18693]},{"body_a":"world","body_b":"link6","contact_count":430.0,"contact_point_centroid":[0.6078,-0.06316,-0.00013],"force_p95":278.29781,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":336.51927,"mean_force":215.29271,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44358,0.06608,0.16724]},{"body_a":"world","body_b":"link6","contact_count":549.0,"contact_point_centroid":[0.67567,-0.0232,-0.00012],"force_p95":72.36868,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":192.36551,"mean_force":69.1757,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46393,-0.03659,0.17174]},{"body_a":"link5","body_b":"hand","contact_count":28.0,"contact_point_centroid":[0.46124,-0.06917,0.25827],"force_p95":182.22785,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":182.99141,"mean_force":156.89183,"phase_index":4.0,"phase_name":"transport_1","phase_type":"push","tcp_position_centroid":[0.4861,0.03718,0.28479]},{"body_a":"world","body_b":"link6","contact_count":83.0,"contact_point_centroid":[0.63602,0.20175,-0.00013],"force_p95":85.58126,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":171.39458,"mean_force":59.66406,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.63235,0.20539,0.29418]},{"body_a":"grasp_target","body_b":"hand","contact_count":36.0,"contact_point_centroid":[0.44164,-0.02048,0.04344],"force_p95":3.51151,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":3.9107,"mean_force":1.55078,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.37866,-0.00165,0.05473]},{"body_a":"grasp_target","body_b":"link6","contact_count":179.0,"contact_point_centroid":[0.44615,-0.01762,0.03641],"force_p95":0.89347,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.28532,"mean_force":0.34986,"phase_index":4.0,"phase_name":"transport_1","phase_type":"push","tcp_position_centroid":[0.50329,0.04756,0.2902]},{"body_a":"world","body_b":"grasp_target","contact_count":3925.0,"contact_point_centroid":[0.42173,-0.02579,-0.00211],"force_p95":0.13736,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.23797,"mean_force":0.13681,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.39528,-0.00229,0.13086]},{"body_a":"world","body_b":"grasp_target","contact_count":2265.0,"contact_point_centroid":[0.41875,0.016,-0.00229],"force_p95":0.34914,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.04867,"mean_force":0.15482,"phase_index":4.0,"phase_name":"transport_1","phase_type":"push","tcp_position_centroid":[0.54238,0.12014,0.28701]},{"body_a":"grasp_target","body_b":"link7","contact_count":11.0,"contact_point_centroid":[0.47125,-0.00663,0.00814],"force_p95":0.43587,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.45745,"mean_force":0.27826,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.36705,-0.00172,0.0512]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.41647,-0.02571,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.42418,-0.01302,0.18715]},{"body_a":"world","body_b":"grasp_target","contact_count":2200.0,"contact_point_centroid":[0.41647,-0.02571,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46393,-0.03659,0.17174]},{"body_a":"world","body_b":"grasp_target","contact_count":1836.0,"contact_point_centroid":[0.41647,-0.02571,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44418,0.06436,0.16789]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.42008,0.04328,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.6324,0.2054,0.29999]}],"total_contact_groups":22},"final_pose_error":0.01625,"key_states":{"actual_goal_position":[0.63013,0.20822,0.11412],"final_object_position":[0.42008,0.04328,0.01602],"final_tcp_position":[0.63368,0.20489,0.41788],"realised_goal_position":[0.63013,0.20822,0.11412],"realised_object_initial_position":[0.45856,-0.02632,0.03]},"peak_contact_force":273004.12061,"phases":[{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.41647,-0.02571,0.01602],"object_pos_start":[0.45856,-0.02632,0.03],"object_to_goal_dist_end":0.33165,"object_to_goal_dist_start":0.30252,"object_z_max":0.03,"peak_contact_force":192.66472,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4876.0,"raw_peak_contact_force":1673.18061,"subtask_id":"approach_1","tcp_end":[0.38504,-0.00369,0.13863],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.12848,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.41647,-0.02571,0.01602],"object_pos_start":[0.41647,-0.02571,0.01602],"object_to_goal_dist_end":0.33165,"object_to_goal_dist_start":0.33165,"object_z_max":0.01602,"peak_contact_force":383.0287,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4977.0,"raw_peak_contact_force":934.4335,"subtask_id":"descend_1","tcp_end":[0.46402,-0.03676,0.17287],"tcp_start":[0.38504,-0.00369,0.13863],"tcp_to_object_dist_end":0.16427,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":10.0,"n_steps":150.0,"n_steps_budget":50.0,"object_pos_end":[0.41647,-0.02571,0.01602],"object_pos_start":[0.41647,-0.02571,0.01602],"object_to_goal_dist_end":0.33165,"object_to_goal_dist_start":0.33165,"object_z_max":0.01602,"peak_contact_force":273004.12061,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":3525.0,"raw_peak_contact_force":192.36551,"subtask_id":"grasp_1","tcp_end":[0.46392,-0.03662,0.17163],"tcp_start":[0.46392,-0.03661,0.17163],"tcp_to_object_dist_end":0.16305,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":459.0,"n_steps_budget":600.0,"object_pos_end":[0.41647,-0.02571,0.01602],"object_pos_start":[0.41647,-0.02571,0.01602],"object_to_goal_dist_end":0.33165,"object_to_goal_dist_start":0.33165,"object_z_max":0.01602,"peak_contact_force":80.60284,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":4209.0,"raw_peak_contact_force":336.51927,"tcp_end":[0.45043,0.08423,0.21258],"tcp_start":[0.46392,-0.03662,0.17163],"tcp_to_object_dist_end":0.22776,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":608.0,"n_steps_budget":660.0,"object_pos_end":[0.42008,0.04328,0.01602],"object_pos_start":[0.41647,-0.02571,0.01602],"object_to_goal_dist_end":0.28452,"object_to_goal_dist_start":0.33165,"object_z_max":0.01819,"peak_contact_force":507.62558,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":5397.0,"raw_peak_contact_force":1036.46768,"subtask_id":"transport_arc","tcp_end":[0.63222,0.20604,0.29405],"tcp_start":[0.45043,0.08423,0.21258],"tcp_to_object_dist_end":0.38574,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.42008,0.04328,0.01602],"object_pos_start":[0.42008,0.04328,0.01602],"object_to_goal_dist_end":0.28452,"object_to_goal_dist_start":0.28452,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1105.0,"raw_peak_contact_force":171.39458,"subtask_id":"release_1","tcp_end":[0.63258,0.20547,0.31937],"tcp_start":[0.63222,0.20604,0.29405],"tcp_to_object_dist_end":0.40434,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":529.0,"n_steps_budget":600.0,"object_pos_end":[0.42008,0.04328,0.01602],"object_pos_start":[0.42008,0.04328,0.01602],"object_to_goal_dist_end":0.28452,"object_to_goal_dist_start":0.28452,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2116.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.63368,0.20489,0.41788],"tcp_start":[0.63258,0.20547,0.31937],"tcp_to_object_dist_end":0.48295,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `a3b2449a94ded39f3d450008c4da002b4ddf87103ab7d1b86900d116c316ff53`; realized-scene SHA-256: `1959b3932a54fd3d3850620783d44a63a35b8fa059f78d939fdbdef5fbfc64e8`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.54431,0.00113,0.03]},{"name":"goal","value":[0.64762,0.15808,0.1911]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.54431,0.00113,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.64762,0.15808,0.1911]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":14.0,"average_failure_rate":0.13861,"average_mean_iterations":34.42574,"average_solve_count":101.0,"average_success_count":87.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.13736,"approach_1.speed":0.18152,"descend_1.grasp_z_offset":0.00815,"descend_1.speed":0.28235,"grasp_1.grasp_force":0.6476,"lift_1.lift_height":0.07156,"lift_1.lift_speed":0.25271,"release_1.release_time":0.34378,"retract_1.retract_height":0.16137,"retract_1.retract_speed":0.20931,"transport_1.arc_height":0.11742,"transport_1.transport_speed":0.22566},"optimized_scores":{"best_composite_score":-0.58094,"best_fitness_score":0.16906,"best_task_score":0.16943},"replay_outcomes":[{"contacts":{"omitted_contact_groups":7,"reported_contact_groups":[{"body_a":"world","body_b":"link6","contact_count":774.0,"contact_point_centroid":[0.64672,0.00149,-0.00045],"force_p95":453.97767,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1465.933,"mean_force":242.37458,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.42888,0.00032,0.15936]},{"body_a":"world","body_b":"link6","contact_count":410.0,"contact_point_centroid":[0.66119,0.00241,-0.00024],"force_p95":462.40993,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":693.17445,"mean_force":233.172,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.45094,-0.00062,0.17355]},{"body_a":"world","body_b":"link6","contact_count":476.0,"contact_point_centroid":[0.60796,0.03311,-0.00016],"force_p95":445.66158,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":691.22052,"mean_force":258.41917,"phase_index":4.0,"phase_name":"transport_1","phase_type":"push","tcp_position_centroid":[0.43503,0.16575,0.14657]},{"body_a":"world","body_b":"link6","contact_count":473.0,"contact_point_centroid":[0.64509,-0.00392,-0.00019],"force_p95":323.57625,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":634.72808,"mean_force":227.27905,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44934,0.06019,0.18028]},{"body_a":"world","body_b":"link7","contact_count":20.0,"contact_point_centroid":[0.53557,0.00416,-0.00378],"force_p95":23.71423,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":474.28467,"mean_force":23.71423,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.38213,-0.00011,0.04918]},{"body_a":"world","body_b":"hand","contact_count":100.0,"contact_point_centroid":[0.53634,0.17458,-0.00014],"force_p95":250.80031,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":278.77989,"mean_force":99.6956,"phase_index":4.0,"phase_name":"transport_1","phase_type":"push","tcp_position_centroid":[0.41985,0.19849,0.09943]},{"body_a":"world","body_b":"link6","contact_count":84.0,"contact_point_centroid":[0.62689,0.1264,-0.0001],"force_p95":78.99626,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":239.98164,"mean_force":56.09698,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.61956,0.15404,0.29108]},{"body_a":"world","body_b":"link6","contact_count":550.0,"contact_point_centroid":[0.67708,0.00612,-0.00013],"force_p95":80.72934,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":189.0545,"mean_force":69.81258,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46485,0.00033,0.17154]},{"body_a":"grasp_target","body_b":"link6","contact_count":214.0,"contact_point_centroid":[0.54404,0.01623,0.03202],"force_p95":0.84912,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":4.63487,"mean_force":0.42716,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.39858,2e-05,0.11164]},{"body_a":"grasp_target","body_b":"link7","contact_count":227.0,"contact_point_centroid":[0.52883,0.00718,0.03447],"force_p95":3.11755,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":4.44405,"mean_force":0.57379,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.39962,2e-05,0.10789]},{"body_a":"grasp_target","body_b":"hand","contact_count":84.0,"contact_point_centroid":[0.50004,0.01485,0.04518],"force_p95":2.60822,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":3.29629,"mean_force":1.07101,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.39168,-5e-05,0.07643]},{"body_a":"world","body_b":"grasp_target","contact_count":3215.0,"contact_point_centroid":[0.51611,0.01085,-0.00222],"force_p95":0.25782,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.57611,"mean_force":0.15493,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.44306,0.00036,0.17175]},{"body_a":"grasp_target","body_b":"link6","contact_count":226.0,"contact_point_centroid":[0.53964,0.01992,0.03504],"force_p95":0.55814,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.13321,"mean_force":0.35467,"phase_index":4.0,"phase_name":"transport_1","phase_type":"push","tcp_position_centroid":[0.41619,0.19073,0.1048]},{"body_a":"world","body_b":"grasp_target","contact_count":2317.0,"contact_point_centroid":[0.50949,0.01297,-0.00228],"force_p95":0.27853,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.56105,"mean_force":0.15157,"phase_index":4.0,"phase_name":"transport_1","phase_type":"push","tcp_position_centroid":[0.44748,0.16251,0.16047]},{"body_a":"world","body_b":"grasp_target","contact_count":1688.0,"contact_point_centroid":[0.51212,0.01379,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.4513,-0.0006,0.17372]},{"body_a":"world","body_b":"grasp_target","contact_count":2200.0,"contact_point_centroid":[0.51212,0.01379,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46485,0.00033,0.17154]}],"total_contact_groups":23},"final_pose_error":0.01788,"key_states":{"actual_goal_position":[0.64762,0.15808,0.1911],"final_object_position":[0.50889,0.01313,0.01602],"final_tcp_position":[0.62101,0.15313,0.46056],"realised_goal_position":[0.64762,0.15808,0.1911],"realised_object_initial_position":[0.54431,0.00113,0.03]},"peak_contact_force":273082.85601,"phases":[{"contact_detected":true,"contact_event_count":5.0,"n_steps":902.0,"n_steps_budget":1000.0,"object_pos_end":[0.51212,0.01379,0.01602],"object_pos_start":[0.54431,0.00113,0.03],"object_to_goal_dist_end":0.26427,"object_to_goal_dist_start":0.24751,"object_z_max":0.03,"peak_contact_force":354.03883,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4534.0,"raw_peak_contact_force":1465.933,"subtask_id":"approach_1","tcp_end":[0.46487,0.00111,0.17045],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.16199,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":422.0,"n_steps_budget":1000.0,"object_pos_end":[0.51212,0.01379,0.01602],"object_pos_start":[0.51212,0.01379,0.01602],"object_to_goal_dist_end":0.26427,"object_to_goal_dist_start":0.26427,"object_z_max":0.01602,"peak_contact_force":378.1947,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2098.0,"raw_peak_contact_force":693.17445,"subtask_id":"descend_1","tcp_end":[0.46501,3e-05,0.17304],"tcp_start":[0.46487,0.00111,0.17045],"tcp_to_object_dist_end":0.16452,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":150.0,"n_steps_budget":50.0,"object_pos_end":[0.51212,0.01379,0.01602],"object_pos_start":[0.51212,0.01379,0.01602],"object_to_goal_dist_end":0.26427,"object_to_goal_dist_start":0.26427,"object_z_max":0.01602,"peak_contact_force":67.45556,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":3537.0,"raw_peak_contact_force":189.0545,"subtask_id":"grasp_1","tcp_end":[0.46484,0.0003,0.17141],"tcp_start":[0.46484,0.00031,0.17142],"tcp_to_object_dist_end":0.16299,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":10.0,"n_steps":484.0,"n_steps_budget":600.0,"object_pos_end":[0.51212,0.01379,0.01602],"object_pos_start":[0.51212,0.01379,0.01602],"object_to_goal_dist_end":0.26427,"object_to_goal_dist_start":0.26427,"object_z_max":0.01602,"peak_contact_force":273082.85601,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":4467.0,"raw_peak_contact_force":634.72808,"tcp_end":[0.46182,0.08482,0.19378],"tcp_start":[0.46484,0.0003,0.17141],"tcp_to_object_dist_end":0.19793,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":10.0,"n_steps":601.0,"n_steps_budget":630.0,"object_pos_end":[0.50889,0.01313,0.01602],"object_pos_start":[0.51212,0.01379,0.01602],"object_to_goal_dist_end":0.26629,"object_to_goal_dist_start":0.26427,"object_z_max":0.01718,"peak_contact_force":272922.97046,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":5670.0,"raw_peak_contact_force":691.22052,"subtask_id":"transport_arc","tcp_end":[0.61911,0.1533,0.29101],"tcp_start":[0.46182,0.08482,0.19378],"tcp_to_object_dist_end":0.32774,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50889,0.01313,0.01602],"object_pos_start":[0.50889,0.01313,0.01602],"object_to_goal_dist_end":0.26629,"object_to_goal_dist_start":0.26629,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1112.0,"raw_peak_contact_force":239.98164,"subtask_id":"release_1","tcp_end":[0.6194,0.1542,0.31696],"tcp_start":[0.61911,0.1533,0.29101],"tcp_to_object_dist_end":0.35026,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":542.0,"n_steps_budget":600.0,"object_pos_end":[0.50889,0.01313,0.01602],"object_pos_start":[0.50889,0.01313,0.01602],"object_to_goal_dist_end":0.26629,"object_to_goal_dist_start":0.26629,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2168.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.62101,0.15313,0.46056],"tcp_start":[0.6194,0.1542,0.31696],"tcp_to_object_dist_end":0.47936,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```