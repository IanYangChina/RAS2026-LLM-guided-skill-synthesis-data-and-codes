## Search State

- **Seed**: 2
- **Iteration**: 9 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 8 | approach → descend → contact → grasp → lift → push → release → retract | arc_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | — | linear_cartesian | position_control | position_control | force_threshold_switch | position_control | impedance_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 14 | -0.6090 | 0.14 | ❌ rejected |
| 7 | approach → descend → grasp → lift → push → release → retract | arc_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | — | linear_cartesian | position_control | impedance_control | position_control | impedance_control | position_control | position_control | position_control | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 14 | -0.5320 | 0.14 | ❌ rejected |
| 6 | approach → descend → grasp → lift → push → release → retract | arc_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | — | linear_cartesian | position_control | admittance_control | position_control | impedance_control | position_control | position_control | position_control | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 14 | -0.6791 | 0.13 | ❌ rejected |
| 5 | approach → descend → grasp → lift → push → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | — | linear_cartesian | position_control | position_control | position_control | impedance_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 12 | -0.5858 | 0.16 | ✅ accepted |
| 4 | align → align → pull → descend | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | admittance_control | pose_tolerance | pose_tolerance | pose_tolerance | contact_detected | 0 | 0.1073 | 0.16 | ❌ rejected |

**Proposal policy**: task_score is 0.14 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=-0.609) — your mutation base

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

- **Composite score**: -0.609
- **task_score** (E): 0.144
- **fitness_score**: 0.146  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.125
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.880

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 0.00 | 1.00 | 0.1512 |
| descend_1 | 0.00 | 1.00 | 0.0688 |
| contact_1 | 1.00 | 1.00 | 0.0000 |
| grasp_1 | 1.00 | 1.00 | 0.0000 |
| lift_1 | 0.00 | 1.00 | 0.1263 |
| transport_1 | 0.00 | 1.00 | 0.2888 |
| release_1 | 1.00 | 1.00 | 0.0299 |
| retract_1 | 0.67 | 1.00 | 0.1346 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 0.00 / step_budget | (0.500, -0.000, 0.301)→(0.411, 0.012, 0.185) | (0.493, -0.015, 0.030)→(0.453, -0.016, 0.016) | 0.279→0.308 | 1.00 / 4.667 | 8834.167 | 1525.762 |
| descend_1 | descend | 0.00 / step_budget | (0.411, 0.012, 0.185)→(0.459, -0.002, 0.195) | (0.453, -0.016, 0.016)→(0.453, -0.016, 0.016) | 0.308→0.308 | 1.00 / 5.000 | 385.771 | 899.789 |
| contact_1 | contact | 1.00 / force_exceeded | (0.459, -0.002, 0.195)→(0.459, -0.002, 0.195) | (0.453, -0.016, 0.016)→(0.453, -0.016, 0.016) | 0.308→0.308 | 1.00 / 5.000 | 171.639 | 171.639 |
| grasp_1 | grasp | 1.00 / step_budget | (0.459, -0.002, 0.194)→(0.459, -0.002, 0.194) | (0.453, -0.016, 0.016)→(0.453, -0.016, 0.016) | 0.308→0.308 | 1.00 / 9.333 | 91048.783 | 236.051 |
| lift_1 | lift | 0.00 / step_budget | (0.459, -0.002, 0.194)→(0.387, -0.047, 0.138) | (0.453, -0.016, 0.016)→(0.453, -0.016, 0.016) | 0.308→0.308 | 1.00 / 10.000 | 91189.893 | 423.402 |
| transport_1 | push | 0.00 / step_budget | (0.387, -0.047, 0.138)→(0.495, 0.173, 0.246) | (0.453, -0.016, 0.016)→(0.444, 0.022, 0.016) | 0.308→0.293 | 1.00 / 8.667 | 91164.904 | 854.191 |
| release_1 | release | 1.00 / step_budget | (0.495, 0.173, 0.246)→(0.499, 0.175, 0.275) | (0.444, 0.022, 0.016)→(0.444, 0.022, 0.016) | 0.293→0.293 | 1.00 / 4.000 | 0.123 | 159.169 |
| retract_1 | retract | 0.67 / step_budget | (0.499, 0.175, 0.275)→(0.473, 0.176, 0.396) | (0.444, 0.022, 0.016)→(0.444, 0.022, 0.016) | 0.293→0.293 | 1.00 / 4.000 | 0.123 | 356.670 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 0.000
- place_accuracy: 0.000
- lift_clearance: 0.000
- transport_retention: None
- terminal_score: 0.176
- phase_score: 0.165
- phase_breakdown.transport_arc_score: 0.014
- phase_breakdown.approach_1_score: 0.011
- phase_breakdown.release_1_score: 0.015
- phase_breakdown.grasp_1_score: 1.000
- phase_breakdown.descend_1_score: 0.044
- grasp_place_fitness: 0.169

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.169
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.176
- **Median Q (composite search score)**: -0.613
- **K-run variance**: 0.0003
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.299


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":3.0,"average_failure_rate":0.0303,"average_mean_iterations":13.66667,"average_solve_count":99.0,"average_success_count":96.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_arc_height":0.11111,"approach_1.approach_height":0.16196,"approach_1.speed":0.11751,"contact_1.contact_force":1.20955,"descend_1.grasp_z_offset":0.03677,"descend_1.speed":0.27016,"grasp_1.grasp_force":0.44155,"lift_1.lift_height":0.10209,"lift_1.lift_speed":0.19994,"release_1.release_time":0.31314,"retract_1.retract_height":0.11986,"retract_1.retract_speed":0.36159,"transport_1.transport_arc_height":0.17637,"transport_1.transport_speed":0.43537},"optimized_scores":{"best_composite_score":-0.61315,"best_fitness_score":0.14185,"best_task_score":0.13222},"replay_outcomes":[{"contacts":{"omitted_contact_groups":12,"reported_contact_groups":[{"body_a":"world","body_b":"link6","contact_count":885.0,"contact_point_centroid":[0.62809,0.01387,-0.00047],"force_p95":219.49263,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1363.2893,"mean_force":205.68114,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.39389,0.01185,0.13514]},{"body_a":"world","body_b":"link6","contact_count":985.0,"contact_point_centroid":[0.61278,-0.00536,-0.00022],"force_p95":476.62491,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":909.65844,"mean_force":295.01587,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.42106,-0.00109,0.19849]},{"body_a":"world","body_b":"link6","contact_count":362.0,"contact_point_centroid":[0.50963,0.09721,-0.0003],"force_p95":297.33188,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":655.27487,"mean_force":222.02899,"phase_index":7.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.34248,0.10397,0.22614]},{"body_a":"world","body_b":"link7","contact_count":20.0,"contact_point_centroid":[0.5259,0.01493,-0.00336],"force_p95":26.32093,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":526.4187,"mean_force":26.32093,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.37054,0.00851,0.05079]},{"body_a":"world","body_b":"link6","contact_count":236.0,"contact_point_centroid":[0.53785,-0.02313,-0.00014],"force_p95":271.53146,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":503.02004,"mean_force":200.39824,"phase_index":5.0,"phase_name":"transport_1","phase_type":"push","tcp_position_centroid":[0.32455,-0.0044,0.06125]},{"body_a":"world","body_b":"link7","contact_count":76.0,"contact_point_centroid":[0.45464,-0.0152,-0.00012],"force_p95":323.55137,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":426.84031,"mean_force":169.7932,"phase_index":5.0,"phase_name":"transport_1","phase_type":"push","tcp_position_centroid":[0.31546,-0.00543,0.04348]},{"body_a":"world","body_b":"link6","contact_count":550.0,"contact_point_centroid":[0.6535,-0.0204,-0.00013],"force_p95":78.04641,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":301.05713,"mean_force":72.82876,"phase_index":3.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46091,-0.01452,0.19331]},{"body_a":"world","body_b":"link6","contact_count":398.0,"contact_point_centroid":[0.62627,-0.02214,-0.00028],"force_p95":221.70454,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":257.89491,"mean_force":197.75119,"phase_index":4.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.39011,-0.01028,0.13194]},{"body_a":"world","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.65257,-0.02018,-8e-05],"force_p95":143.93461,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":143.93461,"mean_force":143.93461,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.46111,-0.01445,0.19452]},{"body_a":"world","body_b":"link6","contact_count":43.0,"contact_point_centroid":[0.60349,0.1068,-0.00011],"force_p95":75.94602,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":95.43808,"mean_force":36.5879,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.4279,0.09996,0.21808]},{"body_a":"grasp_target","body_b":"hand","contact_count":37.0,"contact_point_centroid":[0.45618,-0.02033,0.03995],"force_p95":3.83678,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":4.066,"mean_force":1.74405,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.38123,0.00855,0.05238]},{"body_a":"grasp_target","body_b":"link7","contact_count":27.0,"contact_point_centroid":[0.48101,-0.00048,0.01035],"force_p95":0.6282,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":3.66609,"mean_force":0.38491,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.37123,0.00857,0.05502]},{"body_a":"grasp_target","body_b":"link7","contact_count":358.0,"contact_point_centroid":[0.44713,-0.0168,0.02581],"force_p95":1.8372,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":3.28033,"mean_force":0.88369,"phase_index":5.0,"phase_name":"transport_1","phase_type":"push","tcp_position_centroid":[0.31755,0.00249,0.07274]},{"body_a":"world","body_b":"grasp_target","contact_count":3937.0,"contact_point_centroid":[0.4405,-0.02128,-0.00214],"force_p95":0.13759,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.28725,"mean_force":0.1383,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.40548,0.01121,0.14339]},{"body_a":"grasp_target","body_b":"hand","contact_count":231.0,"contact_point_centroid":[0.4141,-0.02344,0.02157],"force_p95":1.32466,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.97577,"mean_force":0.56539,"phase_index":5.0,"phase_name":"transport_1","phase_type":"push","tcp_position_centroid":[0.31203,-0.00293,0.04908]},{"body_a":"world","body_b":"grasp_target","contact_count":1432.0,"contact_point_centroid":[0.42577,-0.01511,-0.0057],"force_p95":0.79738,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.64299,"mean_force":0.43095,"phase_index":5.0,"phase_name":"transport_1","phase_type":"push","tcp_position_centroid":[0.33174,0.00955,0.0864]}],"total_contact_groups":28},"final_pose_error":0.10348,"key_states":{"actual_goal_position":[0.63142,0.15919,0.19002],"final_object_position":[0.42451,0.02127,0.01602],"final_tcp_position":[0.34723,0.10466,0.30072],"realised_goal_position":[0.63142,0.15919,0.19002],"realised_object_initial_position":[0.47616,-0.02015,0.03]},"peak_contact_force":25970.0,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.4356,-0.02145,0.01602],"object_pos_start":[0.47616,-0.02015,0.03],"object_to_goal_dist_end":0.3182,"object_to_goal_dist_start":0.28614,"object_z_max":0.03,"peak_contact_force":25970.0,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4906.0,"raw_peak_contact_force":1363.2893,"subtask_id":"approach_1","tcp_end":[0.40992,0.00538,0.17742],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.16561,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.4356,-0.02145,0.01602],"object_pos_start":[0.4356,-0.02145,0.01602],"object_to_goal_dist_end":0.3182,"object_to_goal_dist_start":0.3182,"object_z_max":0.01602,"peak_contact_force":385.44719,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4985.0,"raw_peak_contact_force":909.65844,"subtask_id":"descend_1","tcp_end":[0.46111,-0.01445,0.19452],"tcp_start":[0.40992,0.00538,0.17742],"tcp_to_object_dist_end":0.18045,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1.0,"n_steps_budget":600.0,"object_pos_end":[0.4356,-0.02145,0.01602],"object_pos_start":[0.4356,-0.02145,0.01602],"object_to_goal_dist_end":0.3182,"object_to_goal_dist_start":0.3182,"object_z_max":0.01602,"peak_contact_force":143.93461,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":5.0,"raw_peak_contact_force":143.93461,"tcp_end":[0.4611,-0.01446,0.19449],"tcp_start":[0.46111,-0.01445,0.19452],"tcp_to_object_dist_end":0.18042,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":150.0,"n_steps_budget":50.0,"object_pos_end":[0.4356,-0.02145,0.01602],"object_pos_start":[0.4356,-0.02145,0.01602],"object_to_goal_dist_end":0.3182,"object_to_goal_dist_start":0.3182,"object_z_max":0.01602,"peak_contact_force":70.22281,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":3513.0,"raw_peak_contact_force":301.05713,"subtask_id":"grasp_1","tcp_end":[0.46091,-0.01454,0.19321],"tcp_start":[0.46091,-0.01454,0.19321],"tcp_to_object_dist_end":0.17912,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":10.0,"n_steps":401.0,"n_steps_budget":600.0,"object_pos_end":[0.4357,-0.02153,0.0155],"object_pos_start":[0.4356,-0.02145,0.01602],"object_to_goal_dist_end":0.31847,"object_to_goal_dist_start":0.3182,"object_z_max":0.01602,"peak_contact_force":203.0012,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":3729.0,"raw_peak_contact_force":257.89491,"tcp_end":[0.36441,-0.00941,0.10091],"tcp_start":[0.46091,-0.01454,0.19321],"tcp_to_object_dist_end":0.11191,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":481.0,"n_steps_budget":600.0,"object_pos_end":[0.42463,0.02139,0.01544],"object_pos_start":[0.4357,-0.02153,0.0155],"object_to_goal_dist_end":0.30369,"object_to_goal_dist_start":0.31847,"object_z_max":0.04502,"peak_contact_force":0.21286,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":4507.0,"raw_peak_contact_force":503.02004,"subtask_id":"transport_arc","tcp_end":[0.42896,0.09952,0.22201],"tcp_start":[0.36441,-0.00941,0.10091],"tcp_to_object_dist_end":0.2209,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.42451,0.02127,0.01602],"object_pos_start":[0.42463,0.02139,0.01544],"object_to_goal_dist_end":0.30349,"object_to_goal_dist_start":0.30369,"object_z_max":0.01604,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1062.0,"raw_peak_contact_force":95.43808,"subtask_id":"release_1","tcp_end":[0.42697,0.09981,0.24664],"tcp_start":[0.42896,0.09952,0.22201],"tcp_to_object_dist_end":0.24364,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":542.0,"n_steps_budget":600.0,"object_pos_end":[0.42451,0.02127,0.01602],"object_pos_start":[0.42451,0.02127,0.01602],"object_to_goal_dist_end":0.30349,"object_to_goal_dist_start":0.30349,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2530.0,"raw_peak_contact_force":655.27487,"tcp_end":[0.34723,0.10466,0.30072],"tcp_start":[0.42697,0.09981,0.24664],"tcp_to_object_dist_end":0.30656,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":7.06957,"average_solve_count":115.0,"average_success_count":115.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_arc_height":0.11242,"approach_1.approach_height":0.1711,"approach_1.speed":0.31502,"contact_1.contact_force":1.94128,"descend_1.grasp_z_offset":0.04003,"descend_1.speed":0.3466,"grasp_1.grasp_force":0.59162,"lift_1.lift_height":0.0948,"lift_1.lift_speed":0.21952,"release_1.release_time":0.37294,"retract_1.retract_height":0.17097,"retract_1.retract_speed":0.17803,"transport_1.transport_arc_height":0.12387,"transport_1.transport_speed":0.23558},"optimized_scores":{"best_composite_score":-0.62762,"best_fitness_score":0.12738,"best_task_score":0.12331},"replay_outcomes":[{"contacts":{"omitted_contact_groups":9,"reported_contact_groups":[{"body_a":"world","body_b":"link6","contact_count":886.0,"contact_point_centroid":[0.61049,-0.01863,-0.00047],"force_p95":226.86643,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1586.85677,"mean_force":220.49664,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.36428,-0.01618,0.10857]},{"body_a":"world","body_b":"link6","contact_count":799.0,"contact_point_centroid":[0.55948,0.0521,-0.00019],"force_p95":786.82615,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1196.13016,"mean_force":371.40681,"phase_index":5.0,"phase_name":"transport_1","phase_type":"push","tcp_position_centroid":[0.39255,0.00524,0.18992]},{"body_a":"world","body_b":"link6","contact_count":999.0,"contact_point_centroid":[0.60178,-0.02834,-0.00023],"force_p95":439.30223,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":862.3337,"mean_force":271.23045,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.4089,-0.02907,0.19422]},{"body_a":"world","body_b":"link5","contact_count":28.0,"contact_point_centroid":[0.48924,0.20784,-0.00029],"force_p95":596.22274,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":648.86578,"mean_force":449.29159,"phase_index":5.0,"phase_name":"transport_1","phase_type":"push","tcp_position_centroid":[0.54509,0.11505,0.26868]},{"body_a":"link5","body_b":"hand","contact_count":130.0,"contact_point_centroid":[0.48913,0.17333,0.20325],"force_p95":191.60896,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":330.78699,"mean_force":78.84685,"phase_index":5.0,"phase_name":"transport_1","phase_type":"push","tcp_position_centroid":[0.4501,0.07511,0.20651]},{"body_a":"world","body_b":"link6","contact_count":296.0,"contact_point_centroid":[0.5946,-0.03939,-0.00024],"force_p95":242.71641,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":261.90855,"mean_force":204.64652,"phase_index":4.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.37999,-0.04943,0.16848]},{"body_a":"world","body_b":"link6","contact_count":87.0,"contact_point_centroid":[0.61852,0.24045,-0.00018],"force_p95":185.77616,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":227.63711,"mean_force":77.47328,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.61532,0.2152,0.29305]},{"body_a":"world","body_b":"link6","contact_count":550.0,"contact_point_centroid":[0.63223,-0.03516,-0.00014],"force_p95":94.1731,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":189.53977,"mean_force":76.13685,"phase_index":3.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.45102,-0.036,0.21349]},{"body_a":"world","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.63116,-0.0351,-0.00023],"force_p95":153.53103,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":153.53103,"mean_force":153.53103,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.45119,-0.03593,0.21436]},{"body_a":"grasp_target","body_b":"hand","contact_count":38.0,"contact_point_centroid":[0.43882,-0.02582,0.04228],"force_p95":3.587,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":4.01221,"mean_force":1.61218,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.36613,-0.00792,0.05588]},{"body_a":"grasp_target","body_b":"link7","contact_count":285.0,"contact_point_centroid":[0.44311,-0.03711,0.03464],"force_p95":0.6953,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.40381,"mean_force":0.3348,"phase_index":5.0,"phase_name":"transport_1","phase_type":"push","tcp_position_centroid":[0.31897,-0.06878,0.11274]},{"body_a":"world","body_b":"grasp_target","contact_count":3927.0,"contact_point_centroid":[0.42248,-0.02765,-0.00213],"force_p95":0.13759,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.25354,"mean_force":0.13786,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.37823,-0.01501,0.11925]},{"body_a":"world","body_b":"grasp_target","contact_count":3656.0,"contact_point_centroid":[0.41067,-0.00353,-0.00239],"force_p95":0.30597,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.61911,"mean_force":0.15387,"phase_index":5.0,"phase_name":"transport_1","phase_type":"push","tcp_position_centroid":[0.41206,0.02222,0.20026]},{"body_a":"grasp_target","body_b":"link7","contact_count":26.0,"contact_point_centroid":[0.46409,-0.01279,0.01171],"force_p95":0.43307,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.45352,"mean_force":0.18529,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.35589,-0.00804,0.05849]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.41743,-0.02787,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.40894,-0.02908,0.19424]},{"body_a":"world","body_b":"grasp_target","contact_count":4.0,"contact_point_centroid":[0.41743,-0.02787,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.45119,-0.03593,0.21436]}],"total_contact_groups":25},"final_pose_error":0.01851,"key_states":{"actual_goal_position":[0.63013,0.20822,0.11412],"final_object_position":[0.40809,0.00911,0.01602],"final_tcp_position":[0.61649,0.21676,0.47118],"realised_goal_position":[0.63013,0.20822,0.11412],"realised_object_initial_position":[0.45856,-0.02632,0.03]},"peak_contact_force":273019.5289,"phases":[{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.41743,-0.02787,0.01602],"object_pos_start":[0.45856,-0.02632,0.03],"object_to_goal_dist_end":0.33256,"object_to_goal_dist_start":0.30252,"object_z_max":0.03,"peak_contact_force":200.40685,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4895.0,"raw_peak_contact_force":1586.85677,"subtask_id":"approach_1","tcp_end":[0.38155,-0.02389,0.15276],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.14142,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.41743,-0.02787,0.01602],"object_pos_start":[0.41743,-0.02787,0.01602],"object_to_goal_dist_end":0.33256,"object_to_goal_dist_start":0.33256,"object_z_max":0.01602,"peak_contact_force":392.88576,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4999.0,"raw_peak_contact_force":862.3337,"subtask_id":"descend_1","tcp_end":[0.45119,-0.03593,0.21436],"tcp_start":[0.38155,-0.02389,0.15276],"tcp_to_object_dist_end":0.20135,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1.0,"n_steps_budget":600.0,"object_pos_end":[0.41743,-0.02787,0.01602],"object_pos_start":[0.41743,-0.02787,0.01602],"object_to_goal_dist_end":0.33256,"object_to_goal_dist_start":0.33256,"object_z_max":0.01602,"peak_contact_force":153.53103,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":5.0,"raw_peak_contact_force":153.53103,"tcp_end":[0.45117,-0.03592,0.21432],"tcp_start":[0.45119,-0.03593,0.21436],"tcp_to_object_dist_end":0.20131,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":150.0,"n_steps_budget":50.0,"object_pos_end":[0.41743,-0.02787,0.01602],"object_pos_start":[0.41743,-0.02787,0.01602],"object_to_goal_dist_end":0.33256,"object_to_goal_dist_start":0.33256,"object_z_max":0.01602,"peak_contact_force":72.00395,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":3506.0,"raw_peak_contact_force":189.53977,"subtask_id":"grasp_1","tcp_end":[0.45103,-0.03602,0.21341],"tcp_start":[0.45103,-0.03602,0.21341],"tcp_to_object_dist_end":0.20039,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":10.0,"n_steps":303.0,"n_steps_budget":600.0,"object_pos_end":[0.41743,-0.02787,0.01602],"object_pos_start":[0.41743,-0.02787,0.01602],"object_to_goal_dist_end":0.33256,"object_to_goal_dist_start":0.33256,"object_z_max":0.01602,"peak_contact_force":273005.71446,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":2780.0,"raw_peak_contact_force":261.90855,"tcp_end":[0.35092,-0.05527,0.14429],"tcp_start":[0.45103,-0.03602,0.21341],"tcp_to_object_dist_end":0.14707,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.40809,0.00911,0.01602],"object_pos_start":[0.41743,-0.02787,0.01602],"object_to_goal_dist_end":0.31395,"object_to_goal_dist_start":0.33256,"object_z_max":0.0206,"peak_contact_force":273019.5289,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":9148.0,"raw_peak_contact_force":1196.13016,"subtask_id":"transport_arc","tcp_end":[0.61497,0.21625,0.29303],"tcp_start":[0.35092,-0.05527,0.14429],"tcp_to_object_dist_end":0.40304,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.40809,0.00911,0.01602],"object_pos_start":[0.40809,0.00911,0.01602],"object_to_goal_dist_end":0.31395,"object_to_goal_dist_start":0.31395,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1105.0,"raw_peak_contact_force":227.63711,"subtask_id":"release_1","tcp_end":[0.61549,0.21515,0.31862],"tcp_start":[0.61497,0.21625,0.29303],"tcp_to_object_dist_end":0.42076,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":572.0,"n_steps_budget":630.0,"object_pos_end":[0.40809,0.00911,0.01602],"object_pos_start":[0.40809,0.00911,0.01602],"object_to_goal_dist_end":0.31395,"object_to_goal_dist_start":0.31395,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2288.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.61649,0.21676,0.47118],"tcp_start":[0.61549,0.21515,0.31862],"tcp_to_object_dist_end":0.54195,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":5.0,"average_failure_rate":0.04425,"average_mean_iterations":16.32743,"average_solve_count":113.0,"average_success_count":108.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_arc_height":0.05961,"approach_1.approach_height":0.10991,"approach_1.speed":0.07628,"contact_1.contact_force":2.11716,"descend_1.grasp_z_offset":0.05774,"descend_1.speed":0.24205,"grasp_1.grasp_force":0.79296,"lift_1.lift_height":0.10273,"lift_1.lift_speed":0.28037,"release_1.release_time":0.25602,"retract_1.retract_height":0.16983,"retract_1.retract_speed":0.32264,"transport_1.transport_arc_height":0.10606,"transport_1.transport_speed":0.21652},"optimized_scores":{"best_composite_score":-0.58616,"best_fitness_score":0.16884,"best_task_score":0.17619},"replay_outcomes":[{"contacts":{"omitted_contact_groups":14,"reported_contact_groups":[{"body_a":"world","body_b":"link6","contact_count":876.0,"contact_point_centroid":[0.62404,0.03361,-0.00042],"force_p95":263.23737,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1627.13949,"mean_force":228.01088,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.40521,0.03097,0.15729]},{"body_a":"world","body_b":"link6","contact_count":745.0,"contact_point_centroid":[0.60452,0.04391,-0.00021],"force_p95":670.12596,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":927.37534,"mean_force":379.97412,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.43278,0.0482,0.22159]},{"body_a":"world","body_b":"link6","contact_count":786.0,"contact_point_centroid":[0.59793,0.06956,-0.0002],"force_p95":492.80783,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":863.42176,"mean_force":295.6167,"phase_index":5.0,"phase_name":"transport_1","phase_type":"push","tcp_position_centroid":[0.42788,-0.07533,0.13446]},{"body_a":"world","body_b":"link6","contact_count":462.0,"contact_point_centroid":[0.61708,0.0538,-0.00024],"force_p95":379.41502,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":750.40296,"mean_force":331.49607,"phase_index":4.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44366,-0.051,0.1822]},{"body_a":"link5","body_b":"hand","contact_count":386.0,"contact_point_centroid":[0.4739,0.04808,0.20155],"force_p95":197.1672,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":429.78469,"mean_force":152.7468,"phase_index":4.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44304,-0.0625,0.18055]},{"body_a":"world","body_b":"link6","contact_count":9.0,"contact_point_centroid":[0.52027,0.16651,-0.00042],"force_p95":409.89044,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":414.61344,"mean_force":364.61861,"phase_index":7.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.45243,0.21215,0.27925]},{"body_a":"link5","body_b":"hand","contact_count":440.0,"contact_point_centroid":[0.4664,0.02831,0.19805],"force_p95":267.35427,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":365.91244,"mean_force":144.40962,"phase_index":5.0,"phase_name":"transport_1","phase_type":"push","tcp_position_centroid":[0.44585,-0.07124,0.14765]},{"body_a":"world","body_b":"hand","contact_count":15.0,"contact_point_centroid":[0.4169,0.12101,-0.00112],"force_p95":276.88576,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":290.03983,"mean_force":232.913,"phase_index":5.0,"phase_name":"transport_1","phase_type":"push","tcp_position_centroid":[0.34457,0.04989,0.11495]},{"body_a":"world","body_b":"link7","contact_count":173.0,"contact_point_centroid":[0.54193,-0.08627,-0.00011],"force_p95":117.73597,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":229.04791,"mean_force":52.06219,"phase_index":5.0,"phase_name":"transport_1","phase_type":"push","tcp_position_centroid":[0.44104,-0.14191,0.11033]},{"body_a":"world","body_b":"link6","contact_count":550.0,"contact_point_centroid":[0.67381,0.03472,-0.00013],"force_p95":74.91645,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":217.55642,"mean_force":70.29611,"phase_index":3.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46488,0.0452,0.17533]},{"body_a":"world","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.67279,0.03455,-0.00014],"force_p95":217.45213,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":217.45213,"mean_force":217.45213,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.46503,0.04496,0.17669]},{"body_a":"world","body_b":"link6","contact_count":44.0,"contact_point_centroid":[0.59323,0.12529,-0.00017],"force_p95":94.06465,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":154.43278,"mean_force":46.51149,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.45471,0.20871,0.23126]},{"body_a":"grasp_target","body_b":"link6","contact_count":377.0,"contact_point_centroid":[0.53323,0.01889,0.0276],"force_p95":0.82777,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":4.39916,"mean_force":0.31834,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.38902,0.01832,0.11705]},{"body_a":"grasp_target","body_b":"link7","contact_count":330.0,"contact_point_centroid":[0.52499,0.01449,0.03134],"force_p95":2.49187,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":3.91814,"mean_force":0.5198,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.38828,0.01721,0.11093]},{"body_a":"world","body_b":"grasp_target","contact_count":3909.0,"contact_point_centroid":[0.51006,0.00225,-0.00221],"force_p95":0.19765,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.90238,"mean_force":0.14924,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.41612,0.02892,0.16417]},{"body_a":"grasp_target","body_b":"hand","contact_count":19.0,"contact_point_centroid":[0.50458,-0.00813,0.03552],"force_p95":1.87588,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":2.65914,"mean_force":1.05238,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.39282,0.01358,0.05151]}],"total_contact_groups":30},"final_pose_error":0.01514,"key_states":{"actual_goal_position":[0.64762,0.15808,0.1911],"final_object_position":[0.49804,0.03646,0.01602],"final_tcp_position":[0.45629,0.20801,0.41479],"realised_goal_position":[0.64762,0.15808,0.1911],"realised_object_initial_position":[0.54431,0.00113,0.03]},"peak_contact_force":273004.12088,"phases":[{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50471,0.0027,0.01602],"object_pos_start":[0.54431,0.00113,0.03],"object_to_goal_dist_end":0.27427,"object_to_goal_dist_start":0.24751,"object_z_max":0.03,"peak_contact_force":332.09493,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":5530.0,"raw_peak_contact_force":1627.13949,"subtask_id":"approach_1","tcp_end":[0.44056,0.0535,0.22535],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.22476,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":782.0,"n_steps_budget":1000.0,"object_pos_end":[0.50471,0.0027,0.01602],"object_pos_start":[0.50471,0.0027,0.01602],"object_to_goal_dist_end":0.27427,"object_to_goal_dist_start":0.27427,"object_z_max":0.01602,"peak_contact_force":378.9807,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3873.0,"raw_peak_contact_force":927.37534,"subtask_id":"descend_1","tcp_end":[0.46503,0.04496,0.17669],"tcp_start":[0.44056,0.0535,0.22535],"tcp_to_object_dist_end":0.17081,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1.0,"n_steps_budget":600.0,"object_pos_end":[0.50471,0.0027,0.01602],"object_pos_start":[0.50471,0.0027,0.01602],"object_to_goal_dist_end":0.27427,"object_to_goal_dist_start":0.27427,"object_z_max":0.01602,"peak_contact_force":217.45213,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":5.0,"raw_peak_contact_force":217.45213,"tcp_end":[0.46503,0.04498,0.17666],"tcp_start":[0.46503,0.04496,0.17669],"tcp_to_object_dist_end":0.17079,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":10.0,"n_steps":150.0,"n_steps_budget":50.0,"object_pos_end":[0.50471,0.0027,0.01602],"object_pos_start":[0.50471,0.0027,0.01602],"object_to_goal_dist_end":0.27427,"object_to_goal_dist_start":0.27427,"object_z_max":0.01602,"peak_contact_force":273004.12088,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":3528.0,"raw_peak_contact_force":217.55642,"subtask_id":"grasp_1","tcp_end":[0.46487,0.04523,0.17521],"tcp_start":[0.46487,0.04523,0.17521],"tcp_to_object_dist_end":0.16952,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":10.0,"n_steps":489.0,"n_steps_budget":600.0,"object_pos_end":[0.50471,0.0027,0.01602],"object_pos_start":[0.50471,0.0027,0.01602],"object_to_goal_dist_end":0.27427,"object_to_goal_dist_start":0.27427,"object_z_max":0.01602,"peak_contact_force":360.96447,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":4884.0,"raw_peak_contact_force":750.40296,"tcp_end":[0.44695,-0.07535,0.16852],"tcp_start":[0.46487,0.04523,0.17521],"tcp_to_object_dist_end":0.18079,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":931.0,"n_steps_budget":960.0,"object_pos_end":[0.49805,0.03641,0.01601],"object_pos_start":[0.50471,0.0027,0.01602],"object_to_goal_dist_end":0.26045,"object_to_goal_dist_start":0.27427,"object_z_max":0.01733,"peak_contact_force":474.96898,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":9850.0,"raw_peak_contact_force":863.42176,"subtask_id":"transport_arc","tcp_end":[0.44106,0.20357,0.22371],"tcp_start":[0.44695,-0.07535,0.16852],"tcp_to_object_dist_end":0.27263,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.49804,0.03646,0.01602],"object_pos_start":[0.49805,0.03641,0.01601],"object_to_goal_dist_end":0.26043,"object_to_goal_dist_start":0.26045,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1066.0,"raw_peak_contact_force":154.43278,"subtask_id":"release_1","tcp_end":[0.45519,0.20896,0.26002],"tcp_start":[0.44106,0.20357,0.22371],"tcp_to_object_dist_end":0.30188,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":506.0,"n_steps_budget":600.0,"object_pos_end":[0.49804,0.03646,0.01602],"object_pos_start":[0.49804,0.03646,0.01602],"object_to_goal_dist_end":0.26043,"object_to_goal_dist_start":0.26043,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2033.0,"raw_peak_contact_force":414.61344,"tcp_end":[0.45629,0.20801,0.41479],"tcp_start":[0.45519,0.20896,0.26002],"tcp_to_object_dist_end":0.43611,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```