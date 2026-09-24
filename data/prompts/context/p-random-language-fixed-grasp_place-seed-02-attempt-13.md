## Search State

- **Seed**: 2
- **Iteration**: 14 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 13 | approach → descend → grasp → lift → push → release → retract | arc_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | — | linear_cartesian | position_control | position_control | position_control | impedance_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 13 | -0.6307 | 0.17 | ❌ rejected |
| 12 | approach → descend → grasp → lift → push → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | — | linear_cartesian | position_control | position_control | position_control | impedance_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 12 | -0.5804 | 0.17 | ❌ rejected |
| 11 | approach → descend → grasp → lift → push → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | — | linear_cartesian | position_control | position_control | impedance_control | impedance_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 12 | -0.5948 | 0.14 | ❌ rejected |
| 10 | approach → descend → grasp → lift → push → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | — | linear_cartesian | position_control | force_threshold_switch | position_control | impedance_control | position_control | position_control | position_control | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 13 | -0.4045 | 0.12 | ❌ rejected |
| 9 | approach → descend → grasp → lift → push → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | — | linear_cartesian | position_control | position_control | position_control | impedance_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 12 | -0.5760 | 0.18 | ✅ accepted |

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

## Current Skill (Q=-0.631) — your mutation base

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

- **Composite score**: -0.631
- **task_score** (E): 0.170
- **fitness_score**: 0.169  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.800

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 0.00 | 1.00 | 0.1928 |
| descend_1 | 0.00 | 1.00 | 0.0909 |
| grasp_1 | 1.00 | 1.00 | 0.0000 |
| lift_1 | 0.00 | 1.00 | 0.1309 |
| transport_1 | 0.33 | 1.00 | 0.3149 |
| release_1 | 1.00 | 1.00 | 0.0360 |
| retract_1 | 0.67 | 1.00 | 0.0577 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 0.00 / step_budget | (0.500, -0.000, 0.301)→(0.391, -0.010, 0.143) | (0.493, -0.015, 0.030)→(0.454, -0.013, 0.016) | 0.279→0.306 | 1.00 / 5.000 | 201.307 | 1637.582 |
| descend_1 | descend | 0.00 / step_budget | (0.391, -0.010, 0.143)→(0.464, -0.028, 0.174) | (0.454, -0.013, 0.016)→(0.454, -0.013, 0.016) | 0.306→0.306 | 1.00 / 5.000 | 401.827 | 928.843 |
| grasp_1 | grasp | 1.00 / step_budget | (0.464, -0.029, 0.173)→(0.464, -0.029, 0.173) | (0.454, -0.013, 0.016)→(0.454, -0.013, 0.016) | 0.306→0.306 | 1.00 / 9.667 | 182025.273 | 193.510 |
| lift_1 | lift | 0.00 / step_budget | (0.464, -0.029, 0.173)→(0.416, 0.063, 0.149) | (0.454, -0.013, 0.016)→(0.454, -0.013, 0.016) | 0.306→0.306 | 1.00 / 9.667 | 213.681 | 333.138 |
| transport_1 | push | 0.33 / step_budget | (0.416, 0.063, 0.149)→(0.684, 0.121, 0.193) | (0.454, -0.013, 0.016)→(0.453, 0.067, 0.016) | 0.306→0.267 | 1.00 / 9.000 | 273039.578 | 577.549 |
| release_1 | release | 1.00 / step_budget | (0.684, 0.121, 0.193)→(0.692, 0.121, 0.227) | (0.453, 0.067, 0.016)→(0.453, 0.067, 0.016) | 0.267→0.267 | 1.00 / 4.000 | 0.123 | 55.827 |
| retract_1 | retract | 0.67 / step_budget | (0.692, 0.121, 0.227)→(0.692, 0.123, 0.284) | (0.453, 0.067, 0.016)→(0.453, 0.067, 0.016) | 0.267→0.267 | 1.00 / 4.000 | 0.123 | 386.188 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 0.000
- place_accuracy: 0.000
- lift_clearance: 0.000
- transport_retention: None
- terminal_score: 0.182
- phase_score: 0.197
- phase_breakdown.grasp_1_score: 1.000
- phase_breakdown.transport_arc_score: 0.055
- phase_breakdown.descend_1_score: 0.087
- phase_breakdown.approach_1_score: 0.058
- phase_breakdown.release_1_score: 0.036
- grasp_place_fitness: 0.180

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.180
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.189
- **Median Q (composite search score)**: -0.623
- **K-run variance**: 0.0002
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.275


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":5.55556,"average_solve_count":135.0,"average_success_count":135.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.23072,"approach_1.arc_height":0.15835,"approach_1.speed":0.34274,"descend_1.grasp_z_offset":0.02235,"descend_1.speed":0.29108,"grasp_1.grasp_force":0.66379,"lift_1.lift_height":0.12409,"lift_1.lift_speed":0.32228,"release_1.release_time":0.26336,"retract_1.retract_height":0.08446,"retract_1.retract_speed":0.02036,"transport_1.arc_height":0.22518,"transport_1.transport_speed":0.20037},"optimized_scores":{"best_composite_score":-0.6204,"best_fitness_score":0.1796,"best_task_score":0.1822},"replay_outcomes":[{"contacts":{"omitted_contact_groups":5,"reported_contact_groups":[{"body_a":"world","body_b":"link6","contact_count":849.0,"contact_point_centroid":[0.61953,-0.00998,-0.00051],"force_p95":201.54288,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1663.34882,"mean_force":207.31876,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.37359,-0.0095,0.11565]},{"body_a":"world","body_b":"link6","contact_count":974.0,"contact_point_centroid":[0.62249,-0.01831,-0.00021],"force_p95":494.12088,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":922.99045,"mean_force":292.00984,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.42319,-0.02036,0.18853]},{"body_a":"world","body_b":"link6","contact_count":410.0,"contact_point_centroid":[0.50368,-0.04843,-0.00016],"force_p95":489.25591,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":658.23861,"mean_force":326.73904,"phase_index":4.0,"phase_name":"transport_1","phase_type":"push","tcp_position_centroid":[0.49505,0.05298,0.26008]},{"body_a":"world","body_b":"link6","contact_count":464.0,"contact_point_centroid":[0.59527,-0.07279,-0.00014],"force_p95":295.00456,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":420.0695,"mean_force":237.72519,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.45116,0.08288,0.15756]},{"body_a":"world","body_b":"link6","contact_count":546.0,"contact_point_centroid":[0.67866,-0.02528,-0.00013],"force_p95":75.0045,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":198.66588,"mean_force":70.39116,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46409,-0.04928,0.16701]},{"body_a":"link5","body_b":"hand","contact_count":48.0,"contact_point_centroid":[0.44563,-0.06252,0.263],"force_p95":145.32552,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":146.91032,"mean_force":97.88866,"phase_index":4.0,"phase_name":"transport_1","phase_type":"push","tcp_position_centroid":[0.48505,0.03082,0.28251]},{"body_a":"grasp_target","body_b":"link7","contact_count":41.0,"contact_point_centroid":[0.47422,-0.00973,0.01343],"force_p95":3.36138,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":3.97752,"mean_force":0.72953,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.36463,-0.00565,0.06629]},{"body_a":"grasp_target","body_b":"hand","contact_count":36.0,"contact_point_centroid":[0.45806,-0.02619,0.0392],"force_p95":3.51942,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":3.84641,"mean_force":1.7323,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.37394,-0.00556,0.05526]},{"body_a":"world","body_b":"grasp_target","contact_count":3800.0,"contact_point_centroid":[0.4415,-0.02185,-0.00219],"force_p95":0.13814,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.00396,"mean_force":0.14179,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.38736,-0.00884,0.12589]},{"body_a":"world","body_b":"grasp_target","contact_count":2455.0,"contact_point_centroid":[0.44205,0.02691,-0.00266],"force_p95":0.4052,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.00165,"mean_force":0.19186,"phase_index":4.0,"phase_name":"transport_1","phase_type":"push","tcp_position_centroid":[0.52517,0.08999,0.28476]},{"body_a":"grasp_target","body_b":"link6","contact_count":321.0,"contact_point_centroid":[0.46503,-0.01103,0.03425],"force_p95":1.23387,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.89702,"mean_force":0.37828,"phase_index":4.0,"phase_name":"transport_1","phase_type":"push","tcp_position_centroid":[0.50202,0.04046,0.28687]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.45408,0.09999,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12264,"mean_force":0.12262,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.61732,0.15581,0.33566]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.43659,-0.0221,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.42414,-0.02061,0.18867]},{"body_a":"world","body_b":"grasp_target","contact_count":2200.0,"contact_point_centroid":[0.43659,-0.0221,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.4641,-0.04927,0.16701]},{"body_a":"world","body_b":"grasp_target","contact_count":1984.0,"contact_point_centroid":[0.43659,-0.0221,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.45115,0.07744,0.15869]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.45408,0.09999,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.61812,0.155,0.37452]}],"total_contact_groups":21},"final_pose_error":0.04586,"key_states":{"actual_goal_position":[0.63142,0.15919,0.19002],"final_object_position":[0.45408,0.09999,0.01602],"final_tcp_position":[0.61835,0.1549,0.39408],"realised_goal_position":[0.63142,0.15919,0.19002],"realised_object_initial_position":[0.47616,-0.02015,0.03]},"peak_contact_force":273010.8441,"phases":[{"contact_detected":true,"contact_event_count":5.0,"n_steps":964.0,"n_steps_budget":1000.0,"object_pos_end":[0.43659,-0.0221,0.01602],"object_pos_start":[0.47616,-0.02015,0.03],"object_to_goal_dist_end":0.31796,"object_to_goal_dist_start":0.28614,"object_z_max":0.03,"peak_contact_force":200.49729,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4745.0,"raw_peak_contact_force":1663.34882,"subtask_id":"approach_1","tcp_end":[0.37504,-0.01446,0.13022],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.12996,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.43659,-0.0221,0.01602],"object_pos_start":[0.43659,-0.0221,0.01602],"object_to_goal_dist_end":0.31796,"object_to_goal_dist_start":0.31796,"object_z_max":0.01602,"peak_contact_force":423.38519,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4974.0,"raw_peak_contact_force":922.99045,"subtask_id":"descend_1","tcp_end":[0.46417,-0.04819,0.16828],"tcp_start":[0.37504,-0.01446,0.13022],"tcp_to_object_dist_end":0.15692,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":10.0,"n_steps":150.0,"n_steps_budget":50.0,"object_pos_end":[0.43659,-0.0221,0.01602],"object_pos_start":[0.43659,-0.0221,0.01602],"object_to_goal_dist_end":0.31796,"object_to_goal_dist_start":0.31796,"object_z_max":0.01602,"peak_contact_force":273004.12056,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":3521.0,"raw_peak_contact_force":198.66588,"subtask_id":"grasp_1","tcp_end":[0.46408,-0.04931,0.16691],"tcp_start":[0.46408,-0.0493,0.16691],"tcp_to_object_dist_end":0.15576,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":496.0,"n_steps_budget":600.0,"object_pos_end":[0.43659,-0.0221,0.01602],"object_pos_start":[0.43659,-0.0221,0.01602],"object_to_goal_dist_end":0.31796,"object_to_goal_dist_start":0.31796,"object_z_max":0.01602,"peak_contact_force":239.25701,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":4560.0,"raw_peak_contact_force":420.0695,"tcp_end":[0.44997,0.12143,0.16178],"tcp_start":[0.46408,-0.04931,0.16691],"tcp_to_object_dist_end":0.205,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":756.0,"n_steps_budget":810.0,"object_pos_end":[0.45408,0.1,0.01602],"object_pos_start":[0.43659,-0.0221,0.01602],"object_to_goal_dist_end":0.2554,"object_to_goal_dist_start":0.31796,"object_z_max":0.02665,"peak_contact_force":273010.8441,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":6523.0,"raw_peak_contact_force":658.23861,"subtask_id":"transport_arc","tcp_end":[0.61714,0.15619,0.33432],"tcp_start":[0.44997,0.12143,0.16178],"tcp_to_object_dist_end":0.36202,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.45408,0.09999,0.01602],"object_pos_start":[0.45408,0.1,0.01602],"object_to_goal_dist_end":0.2554,"object_to_goal_dist_start":0.2554,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1029.0,"raw_peak_contact_force":0.12264,"subtask_id":"release_1","tcp_end":[0.61771,0.15554,0.35546],"tcp_start":[0.61714,0.15619,0.33432],"tcp_to_object_dist_end":0.3809,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.45408,0.09999,0.01602],"object_pos_start":[0.45408,0.09999,0.01602],"object_to_goal_dist_end":0.2554,"object_to_goal_dist_start":0.2554,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.61835,0.1549,0.39408],"tcp_start":[0.61771,0.15554,0.35546],"tcp_to_object_dist_end":0.41584,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":20.0,"average_failure_rate":0.18868,"average_mean_iterations":43.59434,"average_solve_count":106.0,"average_success_count":86.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.25174,"approach_1.arc_height":0.1039,"approach_1.speed":0.28349,"descend_1.grasp_z_offset":0.00991,"descend_1.speed":0.2483,"grasp_1.grasp_force":0.52908,"lift_1.lift_height":0.18743,"lift_1.lift_speed":0.38265,"release_1.release_time":0.26587,"retract_1.retract_height":0.15634,"retract_1.retract_speed":0.27144,"transport_1.arc_height":0.1232,"transport_1.transport_speed":0.24724},"optimized_scores":{"best_composite_score":-0.64911,"best_fitness_score":0.15089,"best_task_score":0.13891},"replay_outcomes":[{"contacts":{"omitted_contact_groups":7,"reported_contact_groups":[{"body_a":"world","body_b":"link6","contact_count":848.0,"contact_point_centroid":[0.60921,-0.01194,-0.00051],"force_p95":215.14783,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1570.98802,"mean_force":214.3255,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.3578,-0.01109,0.10287]},{"body_a":"world","body_b":"link6","contact_count":979.0,"contact_point_centroid":[0.61862,-0.02503,-0.00021],"force_p95":513.06228,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":951.03227,"mean_force":304.02596,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.42326,-0.02559,0.1932]},{"body_a":"world","body_b":"link6","contact_count":601.0,"contact_point_centroid":[0.50505,-0.02437,-0.00027],"force_p95":450.36435,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":698.20146,"mean_force":288.83449,"phase_index":4.0,"phase_name":"transport_1","phase_type":"push","tcp_position_centroid":[0.54219,0.18584,0.13123]},{"body_a":"world","body_b":"hand","contact_count":387.0,"contact_point_centroid":[0.54957,0.14589,-0.00022],"force_p95":472.61502,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":596.96662,"mean_force":252.83607,"phase_index":4.0,"phase_name":"transport_1","phase_type":"push","tcp_position_centroid":[0.56175,0.20245,0.1275]},{"body_a":"world","body_b":"link6","contact_count":506.0,"contact_point_centroid":[0.58851,-0.07595,-0.00014],"force_p95":249.06063,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":313.59182,"mean_force":215.23794,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.40255,0.0522,0.13297]},{"body_a":"world","body_b":"link6","contact_count":547.0,"contact_point_centroid":[0.67098,-0.04758,-0.00013],"force_p95":76.46816,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":223.75522,"mean_force":70.08633,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46333,-0.04371,0.1771]},{"body_a":"world","body_b":"link6","contact_count":86.0,"contact_point_centroid":[0.5866,0.11898,-6e-05],"force_p95":78.01772,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":167.23556,"mean_force":55.12055,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.74867,0.29689,0.129]},{"body_a":"grasp_target","body_b":"hand","contact_count":36.0,"contact_point_centroid":[0.44106,-0.02932,0.04353],"force_p95":3.22132,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":3.57145,"mean_force":1.5388,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.36579,-0.00617,0.06015]},{"body_a":"grasp_target","body_b":"link7","contact_count":25.0,"contact_point_centroid":[0.46324,-0.01059,0.01209],"force_p95":0.46244,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":3.12299,"mean_force":0.29938,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.35484,-0.00622,0.06393]},{"body_a":"grasp_target","body_b":"link6","contact_count":314.0,"contact_point_centroid":[0.44132,-0.01264,0.02725],"force_p95":1.41676,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":2.32976,"mean_force":0.54172,"phase_index":4.0,"phase_name":"transport_1","phase_type":"push","tcp_position_centroid":[0.54933,0.191,0.13563]},{"body_a":"world","body_b":"grasp_target","contact_count":3788.0,"contact_point_centroid":[0.42217,-0.02813,-0.00213],"force_p95":0.13759,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.71609,"mean_force":0.13793,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.37299,-0.01031,0.11443]},{"body_a":"world","body_b":"grasp_target","contact_count":2572.0,"contact_point_centroid":[0.41305,0.0012,-0.00302],"force_p95":0.54629,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.34002,"mean_force":0.20873,"phase_index":4.0,"phase_name":"transport_1","phase_type":"push","tcp_position_centroid":[0.54903,0.19065,0.12868]},{"body_a":"grasp_target","body_b":"link7","contact_count":35.0,"contact_point_centroid":[0.44539,-0.02057,0.03595],"force_p95":0.19372,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2183,"mean_force":0.12225,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.37602,0.08824,0.11849]},{"body_a":"world","body_b":"grasp_target","contact_count":2168.0,"contact_point_centroid":[0.41685,-0.02842,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.18686,"mean_force":0.12294,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.4033,0.05107,0.13354]},{"body_a":"grasp_target","body_b":"link7","contact_count":7.0,"contact_point_centroid":[0.44466,-0.02186,0.03633],"force_p95":0.12854,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13246,"mean_force":0.10128,"phase_index":4.0,"phase_name":"transport_1","phase_type":"push","tcp_position_centroid":[0.37581,0.08853,0.1195]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.40718,0.03988,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12265,"mean_force":0.12263,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.74758,0.29661,0.13414]}],"total_contact_groups":23},"final_pose_error":0.17995,"key_states":{"actual_goal_position":[0.63013,0.20822,0.11412],"final_object_position":[0.40718,0.03988,0.01602],"final_tcp_position":[0.74873,0.29621,0.12867],"realised_goal_position":[0.63013,0.20822,0.11412],"realised_object_initial_position":[0.45856,-0.02632,0.03]},"peak_contact_force":273054.5619,"phases":[{"contact_detected":true,"contact_event_count":5.0,"n_steps":964.0,"n_steps_budget":1000.0,"object_pos_end":[0.41686,-0.02842,0.01602],"object_pos_start":[0.45856,-0.02632,0.03],"object_to_goal_dist_end":0.33332,"object_to_goal_dist_start":0.30252,"object_z_max":0.03,"peak_contact_force":214.55961,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4713.0,"raw_peak_contact_force":1570.98802,"subtask_id":"approach_1","tcp_end":[0.35143,-0.01753,0.09848],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.10582,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.41686,-0.02842,0.01602],"object_pos_start":[0.41686,-0.02842,0.01602],"object_to_goal_dist_end":0.33332,"object_to_goal_dist_start":0.33332,"object_z_max":0.01602,"peak_contact_force":392.72162,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4979.0,"raw_peak_contact_force":951.03227,"subtask_id":"descend_1","tcp_end":[0.46346,-0.04335,0.17816],"tcp_start":[0.35143,-0.01753,0.09848],"tcp_to_object_dist_end":0.16937,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":10.0,"n_steps":150.0,"n_steps_budget":50.0,"object_pos_end":[0.41686,-0.02842,0.01602],"object_pos_start":[0.41686,-0.02842,0.01602],"object_to_goal_dist_end":0.33332,"object_to_goal_dist_start":0.33332,"object_z_max":0.01602,"peak_contact_force":273004.12057,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":3516.0,"raw_peak_contact_force":223.75522,"subtask_id":"grasp_1","tcp_end":[0.46332,-0.04377,0.177],"tcp_start":[0.46332,-0.04376,0.177],"tcp_to_object_dist_end":0.16826,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":10.0,"n_steps":542.0,"n_steps_budget":600.0,"object_pos_end":[0.41613,-0.02845,0.01595],"object_pos_start":[0.41686,-0.02842,0.01602],"object_to_goal_dist_end":0.33383,"object_to_goal_dist_start":0.33332,"object_z_max":0.01603,"peak_contact_force":211.04237,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":5012.0,"raw_peak_contact_force":313.59182,"tcp_end":[0.3754,0.08914,0.1182],"tcp_start":[0.46332,-0.04377,0.177],"tcp_to_object_dist_end":0.16106,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":762.0,"n_steps_budget":810.0,"object_pos_end":[0.40718,0.03988,0.01602],"object_pos_start":[0.41613,-0.02845,0.01595],"object_to_goal_dist_end":0.29609,"object_to_goal_dist_start":0.33383,"object_z_max":0.01605,"peak_contact_force":273054.5619,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":7182.0,"raw_peak_contact_force":698.20146,"subtask_id":"transport_arc","tcp_end":[0.74873,0.29621,0.12867],"tcp_start":[0.3754,0.08914,0.1182],"tcp_to_object_dist_end":0.44165,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.40718,0.03988,0.01602],"object_pos_start":[0.40718,0.03988,0.01602],"object_to_goal_dist_end":0.29609,"object_to_goal_dist_start":0.29609,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1112.0,"raw_peak_contact_force":167.23556,"subtask_id":"release_1","tcp_end":[0.74625,0.29618,0.15227],"tcp_start":[0.74873,0.29621,0.12867],"tcp_to_object_dist_end":0.44635,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":0.0,"n_steps_budget":600.0,"object_pos_end":[0.40718,0.03988,0.01602],"object_pos_start":[0.40718,0.03988,0.01602],"object_to_goal_dist_end":0.29609,"object_to_goal_dist_start":0.29609,"peak_contact_force":0.12263,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.74625,0.29618,0.15227],"tcp_start":[0.74625,0.29618,0.15227],"tcp_to_object_dist_end":0.44635,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":11.0,"average_failure_rate":0.11,"average_mean_iterations":29.01,"average_solve_count":100.0,"average_success_count":89.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.2293,"approach_1.arc_height":0.21266,"approach_1.speed":0.33026,"descend_1.grasp_z_offset":0.02437,"descend_1.speed":0.24306,"grasp_1.grasp_force":0.85115,"lift_1.lift_height":0.1154,"lift_1.lift_speed":0.36549,"release_1.release_time":0.35457,"retract_1.retract_height":0.15181,"retract_1.retract_speed":0.20011,"transport_1.arc_height":0.24996,"transport_1.transport_speed":0.40794},"optimized_scores":{"best_composite_score":-0.62269,"best_fitness_score":0.17731,"best_task_score":0.18867},"replay_outcomes":[{"contacts":{"omitted_contact_groups":9,"reported_contact_groups":[{"body_a":"world","body_b":"link6","contact_count":794.0,"contact_point_centroid":[0.64296,0.00102,-0.00049],"force_p95":206.39799,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1678.40843,"mean_force":199.60017,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.41925,0.00043,0.15108]},{"body_a":"world","body_b":"link5","contact_count":168.0,"contact_point_centroid":[0.62458,0.0431,-0.00066],"force_p95":483.25278,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1158.44071,"mean_force":317.20654,"phase_index":6.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.68014,-0.08725,0.25102]},{"body_a":"world","body_b":"link6","contact_count":584.0,"contact_point_centroid":[0.63221,0.00607,-0.00018],"force_p95":560.78411,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":912.50497,"mean_force":282.32288,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.43534,0.00268,0.19332]},{"body_a":"world","body_b":"link6","contact_count":247.0,"contact_point_centroid":[0.59621,0.00268,-0.00015],"force_p95":277.84983,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":376.20832,"mean_force":224.68915,"phase_index":4.0,"phase_name":"transport_1","phase_type":"push","tcp_position_centroid":[0.36592,-0.05269,0.12582]},{"body_a":"world","body_b":"link6","contact_count":68.0,"contact_point_centroid":[0.71023,0.01562,-0.00015],"force_p95":263.36699,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":331.30293,"mean_force":206.46755,"phase_index":6.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.7004,-0.02637,0.28883]},{"body_a":"world","body_b":"link6","contact_count":509.0,"contact_point_centroid":[0.64443,0.00786,-0.00033],"force_p95":213.66517,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":265.75271,"mean_force":190.87925,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.42381,-0.01239,0.15857]},{"body_a":"world","body_b":"link6","contact_count":550.0,"contact_point_centroid":[0.67377,0.00774,-0.00012],"force_p95":71.43694,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":158.10971,"mean_force":68.52713,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46456,0.00677,0.17532]},{"body_a":"link5","body_b":"hand","contact_count":105.0,"contact_point_centroid":[0.50098,0.1583,0.21719],"force_p95":122.01443,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":123.69754,"mean_force":64.09784,"phase_index":4.0,"phase_name":"transport_1","phase_type":"push","tcp_position_centroid":[0.45192,0.04845,0.21422]},{"body_a":"grasp_target","body_b":"link7","contact_count":236.0,"contact_point_centroid":[0.5292,0.00557,0.03314],"force_p95":3.09297,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":4.47161,"mean_force":0.53382,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.40134,0.00017,0.10657]},{"body_a":"grasp_target","body_b":"link6","contact_count":124.0,"contact_point_centroid":[0.54622,0.015,0.02749],"force_p95":0.84279,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":3.88367,"mean_force":0.47543,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.39546,0.0001,0.09628]},{"body_a":"grasp_target","body_b":"hand","contact_count":85.0,"contact_point_centroid":[0.50128,0.01515,0.0456],"force_p95":2.53786,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":3.29727,"mean_force":1.01,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.39488,7e-05,0.07903]},{"body_a":"world","body_b":"grasp_target","contact_count":3406.0,"contact_point_centroid":[0.51547,0.00869,-0.00221],"force_p95":0.2601,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.50862,"mean_force":0.15384,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.43176,0.00044,0.16139]},{"body_a":"grasp_target","body_b":"link6","contact_count":300.0,"contact_point_centroid":[0.52284,0.00539,0.02939],"force_p95":1.48024,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":2.07631,"mean_force":0.62578,"phase_index":4.0,"phase_name":"transport_1","phase_type":"push","tcp_position_centroid":[0.35941,-0.04791,0.13797]},{"body_a":"grasp_target","body_b":"link7","contact_count":116.0,"contact_point_centroid":[0.48444,-0.00646,0.02656],"force_p95":0.7254,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.20913,"mean_force":0.27541,"phase_index":4.0,"phase_name":"transport_1","phase_type":"push","tcp_position_centroid":[0.34875,-0.06184,0.10164]},{"body_a":"world","body_b":"grasp_target","contact_count":1834.0,"contact_point_centroid":[0.50114,0.02705,-0.0036],"force_p95":0.54877,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.89914,"mean_force":0.25604,"phase_index":4.0,"phase_name":"transport_1","phase_type":"push","tcp_position_centroid":[0.40954,-0.02673,0.14219]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.49739,0.06136,-0.00199],"force_p95":0.12287,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.1239,"mean_force":0.12264,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.71133,-0.08738,0.1512]}],"total_contact_groups":25},"final_pose_error":0.01823,"key_states":{"actual_goal_position":[0.64762,0.15808,0.1911],"final_object_position":[0.49739,0.06136,0.01602],"final_tcp_position":[0.71101,-0.08254,0.30634],"realised_goal_position":[0.64762,0.15808,0.1911],"realised_object_initial_position":[0.54431,0.00113,0.03]},"peak_contact_force":273053.32922,"phases":[{"contact_detected":true,"contact_event_count":5.0,"n_steps":910.0,"n_steps_budget":1000.0,"object_pos_end":[0.50949,0.01047,0.01602],"object_pos_start":[0.54431,0.00113,0.03],"object_to_goal_dist_end":0.26745,"object_to_goal_dist_start":0.24751,"object_z_max":0.03,"peak_contact_force":188.86418,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4664.0,"raw_peak_contact_force":1678.40843,"subtask_id":"approach_1","tcp_end":[0.44567,0.00084,0.19926],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.19428,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":602.0,"n_steps_budget":1000.0,"object_pos_end":[0.50949,0.01047,0.01602],"object_pos_start":[0.50949,0.01047,0.01602],"object_to_goal_dist_end":0.26745,"object_to_goal_dist_start":0.26745,"object_z_max":0.01602,"peak_contact_force":389.37352,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2992.0,"raw_peak_contact_force":912.50497,"subtask_id":"descend_1","tcp_end":[0.46467,0.0068,0.17651],"tcp_start":[0.44567,0.00084,0.19926],"tcp_to_object_dist_end":0.16667,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":150.0,"n_steps_budget":50.0,"object_pos_end":[0.50949,0.01047,0.01602],"object_pos_start":[0.50949,0.01047,0.01602],"object_to_goal_dist_end":0.26745,"object_to_goal_dist_start":0.26745,"object_z_max":0.01602,"peak_contact_force":67.57667,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":3511.0,"raw_peak_contact_force":158.10971,"subtask_id":"grasp_1","tcp_end":[0.46456,0.00675,0.1752],"tcp_start":[0.46456,0.00675,0.1752],"tcp_to_object_dist_end":0.16544,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":10.0,"n_steps":513.0,"n_steps_budget":600.0,"object_pos_end":[0.50949,0.01047,0.01602],"object_pos_start":[0.50949,0.01047,0.01602],"object_to_goal_dist_end":0.26745,"object_to_goal_dist_start":0.26745,"object_z_max":0.01602,"peak_contact_force":190.74326,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":4763.0,"raw_peak_contact_force":265.75271,"tcp_end":[0.42305,-0.02294,0.16837],"tcp_start":[0.46456,0.00675,0.1752],"tcp_to_object_dist_end":0.17832,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":571.0,"n_steps_budget":600.0,"object_pos_end":[0.4974,0.06132,0.01603],"object_pos_start":[0.50949,0.01047,0.01602],"object_to_goal_dist_end":0.25016,"object_to_goal_dist_start":0.26745,"object_z_max":0.02532,"peak_contact_force":273053.32922,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":5042.0,"raw_peak_contact_force":376.20832,"subtask_id":"transport_arc","tcp_end":[0.68481,-0.0881,0.11479],"tcp_start":[0.42305,-0.02294,0.16837],"tcp_to_object_dist_end":0.25923,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.49739,0.06136,0.01602],"object_pos_start":[0.4974,0.06132,0.01603],"object_to_goal_dist_end":0.25016,"object_to_goal_dist_start":0.25016,"object_z_max":0.01603,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1025.0,"raw_peak_contact_force":0.1239,"subtask_id":"release_1","tcp_end":[0.71097,-0.08741,0.1721],"tcp_start":[0.68481,-0.0881,0.11479],"tcp_to_object_dist_end":0.3035,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":426.0,"n_steps_budget":600.0,"object_pos_end":[0.49739,0.06136,0.01602],"object_pos_start":[0.49739,0.06136,0.01602],"object_to_goal_dist_end":0.25016,"object_to_goal_dist_start":0.25016,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1940.0,"raw_peak_contact_force":1158.44071,"tcp_end":[0.71101,-0.08254,0.30634],"tcp_start":[0.71097,-0.08741,0.1721],"tcp_to_object_dist_end":0.3881,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```