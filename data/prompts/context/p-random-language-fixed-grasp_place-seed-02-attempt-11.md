## Search State

- **Seed**: 2
- **Iteration**: 12 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 11 | approach → descend → grasp → lift → push → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | — | linear_cartesian | position_control | position_control | impedance_control | impedance_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 12 | -0.5948 | 0.14 | ❌ rejected |
| 10 | approach → descend → grasp → lift → push → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | — | linear_cartesian | position_control | force_threshold_switch | position_control | impedance_control | position_control | position_control | position_control | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 13 | -0.4045 | 0.12 | ❌ rejected |
| 9 | approach → descend → grasp → lift → push → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | — | linear_cartesian | position_control | position_control | position_control | impedance_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 12 | -0.5760 | 0.18 | ✅ accepted |
| 8 | approach → descend → contact → grasp → lift → push → release → retract | arc_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | — | linear_cartesian | position_control | position_control | force_threshold_switch | position_control | impedance_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 14 | -0.6090 | 0.14 | ❌ rejected |
| 7 | approach → descend → contact → grasp → lift → push → release → retract | arc_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | — | linear_cartesian | position_control | position_control | force_threshold_switch | position_control | impedance_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 14 | -0.5320 | 0.14 | ✅ accepted |

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

## Current Skill (Q=-0.595) — your mutation base

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

- **Composite score**: -0.595
- **task_score** (E): 0.138
- **fitness_score**: 0.155  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.750

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 0.00 | 1.00 | 0.1341 |
| descend_1 | 0.00 | 1.00 | 0.0429 |
| grasp_1 | 1.00 | 1.00 | 0.0000 |
| lift_1 | 1.00 | 1.00 | 0.0994 |
| transport_1 | 0.00 | 1.00 | 0.1905 |
| release_1 | 1.00 | 1.00 | 0.0242 |
| retract_1 | 0.33 | 1.00 | 0.1362 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 0.00 / step_budget | (0.500, -0.000, 0.301)→(0.443, -0.010, 0.182) | (0.493, -0.015, 0.030)→(0.455, -0.011, 0.016) | 0.279→0.304 | 1.00 / 5.000 | 307.203 | 1478.011 |
| descend_1 | descend | 0.00 / step_budget | (0.443, -0.010, 0.182)→(0.464, -0.035, 0.170) | (0.455, -0.011, 0.016)→(0.455, -0.011, 0.016) | 0.304→0.304 | 1.00 / 5.000 | 375.626 | 828.273 |
| grasp_1 | grasp | 1.00 / step_budget | (0.464, -0.035, 0.168)→(0.464, -0.035, 0.168) | (0.455, -0.011, 0.016)→(0.455, -0.011, 0.016) | 0.304→0.304 | 1.00 / 9.000 | 79.794 | 185.414 |
| lift_1 | lift | 1.00 / step_budget | (0.464, -0.035, 0.168)→(0.463, -0.035, 0.268) | (0.455, -0.011, 0.016)→(0.455, -0.011, 0.016) | 0.304→0.304 | 1.00 / 8.333 | 0.123 | 182.679 |
| transport_1 | push | 0.00 / step_budget | (0.463, -0.035, 0.268)→(0.508, 0.123, 0.230) | (0.455, -0.011, 0.016)→(0.452, 0.003, 0.016) | 0.304→0.299 | 1.00 / 9.000 | 90955.278 | 918.771 |
| release_1 | release | 1.00 / step_budget | (0.508, 0.123, 0.230)→(0.503, 0.131, 0.249) | (0.452, 0.003, 0.016)→(0.452, 0.003, 0.016) | 0.299→0.299 | 1.00 / 4.333 | 54.062 | 179.305 |
| retract_1 | retract | 0.33 / step_budget | (0.503, 0.131, 0.249)→(0.441, 0.117, 0.272) | (0.452, 0.003, 0.016)→(0.451, 0.003, 0.015) | 0.299→0.301 | 1.00 / 5.000 | 67.213 | 284.575 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 0.000
- place_accuracy: 0.000
- lift_clearance: 0.000
- transport_retention: None
- terminal_score: 0.185
- phase_score: 0.169
- phase_breakdown.grasp_1_score: 1.000
- phase_breakdown.transport_arc_score: 0.018
- phase_breakdown.descend_1_score: 0.052
- phase_breakdown.approach_1_score: 0.042
- phase_breakdown.release_1_score: 0.016
- grasp_place_fitness: 0.176

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.176
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.185
- **Median Q (composite search score)**: -0.600
- **K-run variance**: 0.0002
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":5.0,"average_failure_rate":0.05102,"average_mean_iterations":17.44898,"average_solve_count":98.0,"average_success_count":93.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.08636,"approach_1.speed":0.38181,"descend_1.grasp_z_offset":0.0215,"descend_1.speed":0.24167,"grasp_1.grasp_force":0.52978,"lift_1.lift_height":0.10615,"lift_1.lift_speed":0.39127,"release_1.release_time":0.22618,"retract_1.retract_height":0.13997,"retract_1.retract_speed":0.23827,"transport_1.arc_height":0.14445,"transport_1.transport_speed":0.37626},"optimized_scores":{"best_composite_score":-0.60046,"best_fitness_score":0.14954,"best_task_score":0.12016},"replay_outcomes":[{"contacts":{"omitted_contact_groups":4,"reported_contact_groups":[{"body_a":"world","body_b":"link6","contact_count":887.0,"contact_point_centroid":[0.63736,-0.00591,-0.00045],"force_p95":307.21349,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1525.60761,"mean_force":215.27824,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.41647,-0.0071,0.15335]},{"body_a":"world","body_b":"link6","contact_count":974.0,"contact_point_centroid":[0.62414,-0.01779,-0.00021],"force_p95":509.23844,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":944.78851,"mean_force":312.84458,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.4375,-0.0222,0.20493]},{"body_a":"world","body_b":"link6","contact_count":293.0,"contact_point_centroid":[0.53484,0.08703,-0.00038],"force_p95":263.90632,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":569.13088,"mean_force":207.74527,"phase_index":6.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.36086,0.06023,0.21716]},{"body_a":"world","body_b":"link6","contact_count":48.0,"contact_point_centroid":[0.55967,-0.03878,-0.0012],"force_p95":433.75341,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":487.00818,"mean_force":258.17545,"phase_index":4.0,"phase_name":"transport_1","phase_type":"push","tcp_position_centroid":[0.40657,-0.04638,0.23442]},{"body_a":"world","body_b":"link7","contact_count":23.0,"contact_point_centroid":[0.52875,0.00048,-0.0038],"force_p95":0.0,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":316.09383,"mean_force":13.74321,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.37786,-0.00265,0.04631]},{"body_a":"world","body_b":"link6","contact_count":4.0,"contact_point_centroid":[0.68138,-0.02708,-0.0001],"force_p95":174.84079,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":177.99628,"mean_force":109.06806,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46467,-0.05462,0.16371]},{"body_a":"world","body_b":"link6","contact_count":545.0,"contact_point_centroid":[0.68132,-0.02699,-0.00013],"force_p95":74.037,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":144.67605,"mean_force":69.75156,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46469,-0.05455,0.16376]},{"body_a":"grasp_target","body_b":"hand","contact_count":42.0,"contact_point_centroid":[0.45763,-0.01923,0.03756],"force_p95":3.56143,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":3.89851,"mean_force":1.6589,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.38807,-0.00261,0.04947]},{"body_a":"world","body_b":"grasp_target","contact_count":3936.0,"contact_point_centroid":[0.44054,-0.02087,-0.00213],"force_p95":0.13728,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.43476,"mean_force":0.13843,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.42602,-0.00653,0.16008]},{"body_a":"grasp_target","body_b":"link7","contact_count":20.0,"contact_point_centroid":[0.48362,-0.01267,0.01109],"force_p95":0.76218,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.79336,"mean_force":0.34229,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.37743,-0.00265,0.04517]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.43576,-0.02099,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.43809,-0.02243,0.20458]},{"body_a":"world","body_b":"grasp_target","contact_count":2200.0,"contact_point_centroid":[0.43576,-0.02099,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46469,-0.05455,0.16377]},{"body_a":"world","body_b":"grasp_target","contact_count":2092.0,"contact_point_centroid":[0.43576,-0.02099,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46332,-0.05441,0.2081]},{"body_a":"world","body_b":"grasp_target","contact_count":1684.0,"contact_point_centroid":[0.43576,-0.02099,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":4.0,"phase_name":"transport_1","phase_type":"push","tcp_position_centroid":[0.41477,-0.00758,0.26467]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.43576,-0.02099,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.45139,0.07358,0.23324]},{"body_a":"world","body_b":"grasp_target","contact_count":2168.0,"contact_point_centroid":[0.43576,-0.02099,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.36337,0.06085,0.24228]}],"total_contact_groups":20},"final_pose_error":0.11508,"key_states":{"actual_goal_position":[0.63142,0.15919,0.19002],"final_object_position":[0.43576,-0.02099,0.01602],"final_tcp_position":[0.36452,0.06155,0.31689],"realised_goal_position":[0.63142,0.15919,0.19002],"realised_object_initial_position":[0.47616,-0.02015,0.03]},"peak_contact_force":1525.60761,"phases":[{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.43576,-0.02099,0.01602],"object_pos_start":[0.47616,-0.02015,0.03],"object_to_goal_dist_end":0.31784,"object_to_goal_dist_start":0.28614,"object_z_max":0.03,"peak_contact_force":364.97468,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4908.0,"raw_peak_contact_force":1525.60761,"subtask_id":"approach_1","tcp_end":[0.45572,-0.0153,0.2072],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.1923,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.43576,-0.02099,0.01602],"object_pos_start":[0.43576,-0.02099,0.01602],"object_to_goal_dist_end":0.31784,"object_to_goal_dist_start":0.31784,"object_z_max":0.01602,"peak_contact_force":384.62416,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4974.0,"raw_peak_contact_force":944.78851,"subtask_id":"descend_1","tcp_end":[0.46475,-0.05323,0.16495],"tcp_start":[0.45572,-0.0153,0.2072],"tcp_to_object_dist_end":0.15512,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":150.0,"n_steps_budget":50.0,"object_pos_end":[0.43576,-0.02099,0.01602],"object_pos_start":[0.43576,-0.02099,0.01602],"object_to_goal_dist_end":0.31784,"object_to_goal_dist_start":0.31784,"object_z_max":0.01602,"peak_contact_force":68.63513,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":3525.0,"raw_peak_contact_force":144.67605,"subtask_id":"grasp_1","tcp_end":[0.46467,-0.05459,0.16366],"tcp_start":[0.46467,-0.05459,0.16367],"tcp_to_object_dist_end":0.15416,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":523.0,"n_steps_budget":600.0,"object_pos_end":[0.43576,-0.02099,0.01602],"object_pos_start":[0.43576,-0.02099,0.01602],"object_to_goal_dist_end":0.31784,"object_to_goal_dist_start":0.31784,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":4378.0,"raw_peak_contact_force":177.99628,"tcp_end":[0.46349,-0.05458,0.25635],"tcp_start":[0.46467,-0.05459,0.16366],"tcp_to_object_dist_end":0.24424,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":421.0,"n_steps_budget":600.0,"object_pos_end":[0.43576,-0.02099,0.01602],"object_pos_start":[0.43576,-0.02099,0.01602],"object_to_goal_dist_end":0.31784,"object_to_goal_dist_start":0.31784,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3563.0,"raw_peak_contact_force":487.00818,"subtask_id":"transport_arc","tcp_end":[0.45333,0.07349,0.23158],"tcp_start":[0.46349,-0.05458,0.25635],"tcp_to_object_dist_end":0.23601,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.43576,-0.02099,0.01602],"object_pos_start":[0.43576,-0.02099,0.01602],"object_to_goal_dist_end":0.31784,"object_to_goal_dist_start":0.31784,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1017.0,"raw_peak_contact_force":0.12263,"subtask_id":"release_1","tcp_end":[0.45052,0.07335,0.25247],"tcp_start":[0.45333,0.07349,0.23158],"tcp_to_object_dist_end":0.255,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":542.0,"n_steps_budget":600.0,"object_pos_end":[0.43576,-0.02099,0.01602],"object_pos_start":[0.43576,-0.02099,0.01602],"object_to_goal_dist_end":0.31784,"object_to_goal_dist_start":0.31784,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2461.0,"raw_peak_contact_force":569.13088,"tcp_end":[0.36452,0.06155,0.31689],"tcp_start":[0.45052,0.07335,0.25247],"tcp_to_object_dist_end":0.32002,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":6.88793,"average_solve_count":116.0,"average_success_count":116.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.13413,"approach_1.speed":0.25493,"descend_1.grasp_z_offset":0.00274,"descend_1.speed":0.23217,"grasp_1.grasp_force":0.49726,"lift_1.lift_height":0.11262,"lift_1.lift_speed":0.3096,"release_1.release_time":0.30068,"retract_1.retract_height":0.15105,"retract_1.retract_speed":0.08379,"transport_1.arc_height":0.08014,"transport_1.transport_speed":0.49817},"optimized_scores":{"best_composite_score":-0.60983,"best_fitness_score":0.14017,"best_task_score":0.11028},"replay_outcomes":[{"contacts":{"omitted_contact_groups":5,"reported_contact_groups":[{"body_a":"world","body_b":"link6","contact_count":321.0,"contact_point_centroid":[0.58671,0.04301,-0.00041],"force_p95":966.09818,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1475.92888,"mean_force":479.52339,"phase_index":4.0,"phase_name":"transport_1","phase_type":"push","tcp_position_centroid":[0.44356,0.0259,0.23398]},{"body_a":"world","body_b":"link6","contact_count":887.0,"contact_point_centroid":[0.62907,-0.00864,-0.00048],"force_p95":213.59366,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1474.65622,"mean_force":208.83396,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.39262,-0.00855,0.13085]},{"body_a":"world","body_b":"link6","contact_count":974.0,"contact_point_centroid":[0.62134,-0.02155,-0.00021],"force_p95":492.12042,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":931.44541,"mean_force":292.7599,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.42471,-0.02346,0.19235]},{"body_a":"world","body_b":"link5","contact_count":73.0,"contact_point_centroid":[0.51555,0.18505,-0.00034],"force_p95":626.96013,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":742.68158,"mean_force":390.59085,"phase_index":4.0,"phase_name":"transport_1","phase_type":"push","tcp_position_centroid":[0.52034,0.06439,0.24602]},{"body_a":"world","body_b":"link7","contact_count":22.0,"contact_point_centroid":[0.52457,0.00027,-0.00354],"force_p95":0.0,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":478.33748,"mean_force":21.74261,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.37081,-0.00338,0.04945]},{"body_a":"world","body_b":"link6","contact_count":78.0,"contact_point_centroid":[0.6337,0.22091,-0.00014],"force_p95":184.13159,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":375.85116,"mean_force":66.07724,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.61698,0.18809,0.29014]},{"body_a":"world","body_b":"link6","contact_count":546.0,"contact_point_centroid":[0.67697,-0.029,-0.00013],"force_p95":73.57062,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":232.67108,"mean_force":70.30489,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46366,-0.05074,0.16891]},{"body_a":"world","body_b":"link6","contact_count":6.0,"contact_point_centroid":[0.67702,-0.02883,-9e-05],"force_p95":156.93627,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":174.831,"mean_force":65.80542,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46361,-0.0507,0.16884]},{"body_a":"grasp_target","body_b":"hand","contact_count":37.0,"contact_point_centroid":[0.43952,-0.01866,0.04207],"force_p95":3.52624,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":3.90032,"mean_force":1.56191,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.3819,-0.00333,0.04993]},{"body_a":"world","body_b":"grasp_target","contact_count":3928.0,"contact_point_centroid":[0.42223,-0.02521,-0.00212],"force_p95":0.13709,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.32312,"mean_force":0.13776,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.40436,-0.00787,0.13968]},{"body_a":"grasp_target","body_b":"link7","contact_count":2.0,"contact_point_centroid":[0.47226,-0.00689,0.00779],"force_p95":0.46277,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.46415,"mean_force":0.45044,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.36926,-0.00334,0.04337]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.4172,-0.02504,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.42554,-0.0237,0.19242]},{"body_a":"world","body_b":"grasp_target","contact_count":2200.0,"contact_point_centroid":[0.4172,-0.02504,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46367,-0.05074,0.16892]},{"body_a":"world","body_b":"grasp_target","contact_count":2144.0,"contact_point_centroid":[0.4172,-0.02504,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.4623,-0.05057,0.21523]},{"body_a":"world","body_b":"grasp_target","contact_count":2284.0,"contact_point_centroid":[0.4172,-0.02504,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":4.0,"phase_name":"transport_1","phase_type":"push","tcp_position_centroid":[0.45687,0.02883,0.23522]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.4172,-0.02504,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.61696,0.1878,0.2964]}],"total_contact_groups":21},"final_pose_error":0.01631,"key_states":{"actual_goal_position":[0.63013,0.20822,0.11412],"final_object_position":[0.4172,-0.02504,0.01602],"final_tcp_position":[0.61784,0.18877,0.45115],"realised_goal_position":[0.63013,0.20822,0.11412],"realised_object_initial_position":[0.45856,-0.02632,0.03]},"peak_contact_force":272865.57772,"phases":[{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.4172,-0.02504,0.01602],"object_pos_start":[0.45856,-0.02632,0.03],"object_to_goal_dist_end":0.33071,"object_to_goal_dist_start":0.30252,"object_z_max":0.03,"peak_contact_force":209.81168,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4876.0,"raw_peak_contact_force":1474.65622,"subtask_id":"approach_1","tcp_end":[0.40909,-0.01681,0.17042],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.15483,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.4172,-0.02504,0.01602],"object_pos_start":[0.4172,-0.02504,0.01602],"object_to_goal_dist_end":0.33071,"object_to_goal_dist_start":0.33071,"object_z_max":0.01602,"peak_contact_force":410.30909,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4974.0,"raw_peak_contact_force":931.44541,"subtask_id":"descend_1","tcp_end":[0.46376,-0.05027,0.17018],"tcp_start":[0.40909,-0.01681,0.17042],"tcp_to_object_dist_end":0.163,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":150.0,"n_steps_budget":50.0,"object_pos_end":[0.4172,-0.02504,0.01602],"object_pos_start":[0.4172,-0.02504,0.01602],"object_to_goal_dist_end":0.33071,"object_to_goal_dist_start":0.33071,"object_z_max":0.01602,"peak_contact_force":85.46462,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":3532.0,"raw_peak_contact_force":232.67108,"subtask_id":"grasp_1","tcp_end":[0.46365,-0.05076,0.16882],"tcp_start":[0.46365,-0.05076,0.16882],"tcp_to_object_dist_end":0.16176,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":536.0,"n_steps_budget":600.0,"object_pos_end":[0.4172,-0.02504,0.01602],"object_pos_start":[0.4172,-0.02504,0.01602],"object_to_goal_dist_end":0.33071,"object_to_goal_dist_start":0.33071,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":4505.0,"raw_peak_contact_force":174.831,"tcp_end":[0.46258,-0.0508,0.26751],"tcp_start":[0.46365,-0.05076,0.16882],"tcp_to_object_dist_end":0.25685,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":10.0,"n_steps":571.0,"n_steps_budget":600.0,"object_pos_end":[0.4172,-0.02504,0.01602],"object_pos_start":[0.4172,-0.02504,0.01602],"object_to_goal_dist_end":0.33071,"object_to_goal_dist_start":0.33071,"object_z_max":0.01602,"peak_contact_force":272865.57772,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":5132.0,"raw_peak_contact_force":1475.92888,"subtask_id":"transport_arc","tcp_end":[0.61668,0.18592,0.28976],"tcp_start":[0.46258,-0.0508,0.26751],"tcp_to_object_dist_end":0.39903,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.4172,-0.02504,0.01602],"object_pos_start":[0.4172,-0.02504,0.01602],"object_to_goal_dist_end":0.33071,"object_to_goal_dist_start":0.33071,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1102.0,"raw_peak_contact_force":375.85116,"subtask_id":"release_1","tcp_end":[0.61706,0.1875,0.31635],"tcp_start":[0.61668,0.18592,0.28976],"tcp_to_object_dist_end":0.41871,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.4172,-0.02504,0.01602],"object_pos_start":[0.4172,-0.02504,0.01602],"object_to_goal_dist_end":0.33071,"object_to_goal_dist_start":0.33071,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.61784,0.18877,0.45115],"tcp_start":[0.61706,0.1875,0.31635],"tcp_to_object_dist_end":0.5247,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":18.0,"average_failure_rate":0.18,"average_mean_iterations":42.1,"average_solve_count":100.0,"average_success_count":82.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.15168,"approach_1.speed":0.27262,"descend_1.grasp_z_offset":0.01394,"descend_1.speed":0.2364,"grasp_1.grasp_force":0.71468,"lift_1.lift_height":0.12138,"lift_1.lift_speed":0.18383,"release_1.release_time":0.33661,"retract_1.retract_height":0.13094,"retract_1.retract_speed":0.27353,"transport_1.arc_height":0.07415,"transport_1.transport_speed":0.31312},"optimized_scores":{"best_composite_score":-0.5741,"best_fitness_score":0.1759,"best_task_score":0.18461},"replay_outcomes":[{"contacts":{"omitted_contact_groups":9,"reported_contact_groups":[{"body_a":"world","body_b":"link6","contact_count":830.0,"contact_point_centroid":[0.64539,0.00184,-0.00044],"force_p95":458.54775,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1433.76777,"mean_force":248.17247,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.4285,0.00034,0.16102]},{"body_a":"world","body_b":"link6","contact_count":64.0,"contact_point_centroid":[0.55885,0.0263,-0.00039],"force_p95":647.57989,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":793.37637,"mean_force":247.06217,"phase_index":4.0,"phase_name":"transport_1","phase_type":"push","tcp_position_centroid":[0.41786,0.02024,0.24164]},{"body_a":"world","body_b":"link6","contact_count":412.0,"contact_point_centroid":[0.66717,0.00273,-0.00028],"force_p95":384.95426,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":608.58464,"mean_force":211.23364,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.45055,-0.00083,0.16536]},{"body_a":"world","body_b":"link7","contact_count":20.0,"contact_point_centroid":[0.53508,0.00416,-0.00337],"force_p95":23.22856,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":464.57125,"mean_force":23.22856,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.38159,-0.00011,0.04988]},{"body_a":"world","body_b":"link6","contact_count":539.0,"contact_point_centroid":[0.5985,0.17486,-0.00029],"force_p95":213.95898,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":284.47071,"mean_force":196.10064,"phase_index":6.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.36962,0.1079,0.09833]},{"body_a":"world","body_b":"link6","contact_count":5.0,"contact_point_centroid":[0.67587,0.00572,-0.00011],"force_p95":188.37914,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":195.21058,"mean_force":114.13743,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46477,-9e-05,0.17298]},{"body_a":"world","body_b":"link6","contact_count":550.0,"contact_point_centroid":[0.67581,0.00571,-0.00012],"force_p95":72.52,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":178.894,"mean_force":68.98587,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46482,-8e-05,0.17307]},{"body_a":"world","body_b":"link6","contact_count":149.0,"contact_point_centroid":[0.64965,0.18953,-6e-05],"force_p95":157.8872,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":161.94038,"mean_force":122.08567,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.445,0.13158,0.17107]},{"body_a":"grasp_target","body_b":"link6","contact_count":235.0,"contact_point_centroid":[0.54384,0.01583,0.03219],"force_p95":0.81381,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":4.74253,"mean_force":0.40926,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.39845,3e-05,0.11264]},{"body_a":"grasp_target","body_b":"link7","contact_count":243.0,"contact_point_centroid":[0.52786,0.00676,0.03474],"force_p95":2.89258,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":4.41378,"mean_force":0.54315,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.39903,3e-05,0.10885]},{"body_a":"grasp_target","body_b":"hand","contact_count":88.0,"contact_point_centroid":[0.50084,0.01396,0.04657],"force_p95":2.52206,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":3.15695,"mean_force":1.07599,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.39108,-5e-05,0.07749]},{"body_a":"world","body_b":"grasp_target","contact_count":3474.0,"contact_point_centroid":[0.51556,0.01096,-0.00218],"force_p95":0.2558,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.59053,"mean_force":0.15111,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.44168,0.00037,0.17236]},{"body_a":"grasp_target","body_b":"link6","contact_count":225.0,"contact_point_centroid":[0.51834,0.02897,0.03429],"force_p95":1.36947,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.49594,"mean_force":0.67325,"phase_index":4.0,"phase_name":"transport_1","phase_type":"push","tcp_position_centroid":[0.41162,0.0216,0.25381]},{"body_a":"world","body_b":"grasp_target","contact_count":1139.0,"contact_point_centroid":[0.50019,0.02894,-0.00421],"force_p95":0.78553,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.82883,"mean_force":0.29892,"phase_index":4.0,"phase_name":"transport_1","phase_type":"push","tcp_position_centroid":[0.42869,0.03476,0.2423]},{"body_a":"grasp_target","body_b":"link7","contact_count":247.0,"contact_point_centroid":[0.49689,0.07489,0.02989],"force_p95":0.36001,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.38485,"mean_force":0.24785,"phase_index":6.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.34969,0.10176,0.06596]},{"body_a":"world","body_b":"grasp_target","contact_count":2168.0,"contact_point_centroid":[0.50218,0.05439,-0.00237],"force_p95":0.2644,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.36591,"mean_force":0.15066,"phase_index":6.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.36999,0.10802,0.09875]}],"total_contact_groups":25},"final_pose_error":0.27974,"key_states":{"actual_goal_position":[0.64762,0.15808,0.1911],"final_object_position":[0.50017,0.05505,0.0126],"final_tcp_position":[0.34202,0.09949,0.04883],"realised_goal_position":[0.64762,0.15808,0.1911],"realised_object_initial_position":[0.54431,0.00113,0.03]},"peak_contact_force":1433.76777,"phases":[{"contact_detected":true,"contact_event_count":5.0,"n_steps":962.0,"n_steps_budget":1000.0,"object_pos_end":[0.51157,0.01353,0.01602],"object_pos_start":[0.54431,0.00113,0.03],"object_to_goal_dist_end":0.26469,"object_to_goal_dist_start":0.24751,"object_z_max":0.03,"peak_contact_force":346.82137,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4890.0,"raw_peak_contact_force":1433.76777,"subtask_id":"approach_1","tcp_end":[0.4648,0.00114,0.16749],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.15901,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":422.0,"n_steps_budget":1000.0,"object_pos_end":[0.51157,0.01353,0.01602],"object_pos_start":[0.51157,0.01353,0.01602],"object_to_goal_dist_end":0.26469,"object_to_goal_dist_start":0.26469,"object_z_max":0.01602,"peak_contact_force":331.94442,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2100.0,"raw_peak_contact_force":608.58464,"subtask_id":"descend_1","tcp_end":[0.46498,-0.00029,0.17438],"tcp_start":[0.4648,0.00114,0.16749],"tcp_to_object_dist_end":0.16565,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":150.0,"n_steps_budget":50.0,"object_pos_end":[0.51157,0.01353,0.01602],"object_pos_start":[0.51157,0.01353,0.01602],"object_to_goal_dist_end":0.26469,"object_to_goal_dist_start":0.26469,"object_z_max":0.01602,"peak_contact_force":85.28373,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":3525.0,"raw_peak_contact_force":178.894,"subtask_id":"grasp_1","tcp_end":[0.46481,-0.00011,0.17296],"tcp_start":[0.46481,-0.0001,0.17296],"tcp_to_object_dist_end":0.16432,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":542.0,"n_steps_budget":600.0,"object_pos_end":[0.51157,0.01353,0.01602],"object_pos_start":[0.51157,0.01353,0.01602],"object_to_goal_dist_end":0.26469,"object_to_goal_dist_start":0.26469,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":4549.0,"raw_peak_contact_force":195.21058,"tcp_end":[0.46386,-0.0002,0.27977],"tcp_start":[0.46481,-0.00011,0.17296],"tcp_to_object_dist_end":0.26839,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":421.0,"n_steps_budget":600.0,"object_pos_end":[0.50236,0.05594,0.01556],"object_pos_start":[0.51157,0.01353,0.01602],"object_to_goal_dist_end":0.2497,"object_to_goal_dist_start":0.26469,"object_z_max":0.02045,"peak_contact_force":0.13425,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3203.0,"raw_peak_contact_force":793.37637,"subtask_id":"transport_arc","tcp_end":[0.45259,0.11035,0.16853],"tcp_start":[0.46386,-0.0002,0.27977],"tcp_to_object_dist_end":0.16981,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50237,0.05467,0.01602],"object_pos_start":[0.50236,0.05594,0.01556],"object_to_goal_dist_end":0.2499,"object_to_goal_dist_start":0.2497,"object_z_max":0.01607,"peak_contact_force":161.94038,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1162.0,"raw_peak_contact_force":161.94038,"subtask_id":"release_1","tcp_end":[0.44184,0.13084,0.17732],"tcp_start":[0.45259,0.11035,0.16853],"tcp_to_object_dist_end":0.18837,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":7.0,"n_steps":542.0,"n_steps_budget":600.0,"object_pos_end":[0.50017,0.05505,0.0126],"object_pos_start":[0.50237,0.05467,0.01602],"object_to_goal_dist_end":0.25342,"object_to_goal_dist_start":0.2499,"object_z_max":0.01602,"peak_contact_force":201.39373,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3010.0,"raw_peak_contact_force":284.47071,"tcp_end":[0.34202,0.09949,0.04883],"tcp_start":[0.44184,0.13084,0.17732],"tcp_to_object_dist_end":0.16822,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```