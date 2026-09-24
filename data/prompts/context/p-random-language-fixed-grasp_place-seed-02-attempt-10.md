## Search State

- **Seed**: 2
- **Iteration**: 11 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 10 | approach → descend → grasp → lift → push → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | — | linear_cartesian | position_control | force_threshold_switch | position_control | impedance_control | position_control | position_control | position_control | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 13 | -0.4045 | 0.12 | ❌ rejected |
| 9 | approach → descend → grasp → lift → push → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | — | linear_cartesian | position_control | position_control | position_control | impedance_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 12 | -0.5760 | 0.18 | ✅ accepted |
| 8 | approach → descend → contact → grasp → lift → push → release → retract | arc_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | — | linear_cartesian | position_control | position_control | force_threshold_switch | position_control | impedance_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 14 | -0.6090 | 0.14 | ❌ rejected |
| 7 | approach → descend → contact → grasp → lift → push → release → retract | arc_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | — | linear_cartesian | position_control | position_control | force_threshold_switch | position_control | impedance_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 14 | -0.5320 | 0.14 | ✅ accepted |
| 6 | approach → descend → grasp → lift → push → release → retract | arc_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | — | linear_cartesian | position_control | impedance_control | position_control | impedance_control | position_control | position_control | position_control | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 14 | -0.6791 | 0.13 | ✅ accepted |

**Proposal policy**: task_score is 0.12 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=-0.404) — your mutation base

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

- **Composite score**: -0.404
- **task_score** (E): 0.124
- **fitness_score**: 0.253  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.143
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.800

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1395 |
| descend_1 | 1.00 | 1.00 | 0.0024 |
| grasp_1 | 1.00 | 1.00 | 0.0000 |
| lift_1 | 0.00 | 1.00 | 0.1165 |
| transport_1 | 0.33 | 1.00 | 0.2725 |
| release_1 | 1.00 | 1.00 | 0.0254 |
| retract_1 | 0.67 | 1.00 | 0.1032 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.489, -0.014, 0.167) | (0.493, -0.015, 0.030)→(0.493, -0.015, 0.026) | 0.279→0.281 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_1 | descend | 1.00 / force_exceeded | (0.489, -0.014, 0.167)→(0.489, -0.014, 0.165) | (0.493, -0.015, 0.026)→(0.493, -0.015, 0.026) | 0.281→0.281 | 1.00 / 4.000 | 132.979 | 0.123 |
| grasp_1 | grasp | 1.00 / step_budget | (0.482, -0.014, 0.156)→(0.482, -0.014, 0.156) | (0.493, -0.015, 0.026)→(0.493, -0.015, 0.026) | 0.281→0.281 | 1.00 / 8.333 | 91001.455 | 0.123 |
| lift_1 | lift | 0.00 / step_budget | (0.482, -0.014, 0.156)→(0.460, -0.066, 0.105) | (0.493, -0.015, 0.026)→(0.475, -0.035, 0.091) | 0.281→0.298 | 1.00 / 6.333 | 187.014 | 1082.808 |
| transport_1 | push | 0.33 / step_budget | (0.460, -0.066, 0.105)→(0.573, 0.088, 0.265) | (0.475, -0.035, 0.091)→(0.513, -0.028, 0.079) | 0.298→0.300 | 1.00 / 8.000 | 3329.006 | 855.141 |
| release_1 | release | 1.00 / step_budget | (0.573, 0.088, 0.265)→(0.573, 0.093, 0.290) | (0.513, -0.028, 0.079)→(0.517, -0.028, 0.079) | 0.300→0.298 | 1.00 / 3.333 | 0.225 | 155.854 |
| retract_1 | retract | 0.67 / step_budget | (0.573, 0.093, 0.290)→(0.550, 0.073, 0.368) | (0.517, -0.028, 0.079)→(0.531, -0.060, 0.016) | 0.298→0.320 | 1.00 / 4.667 | 26.825 | 247.269 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 0.000
- place_accuracy: 0.000
- lift_clearance: 0.000
- transport_retention: None
- terminal_score: 0.076
- phase_score: 0.235
- phase_breakdown.grasp_1_score: 1.000
- phase_breakdown.transport_arc_score: 0.125
- phase_breakdown.descend_1_score: 0.039
- phase_breakdown.approach_1_score: 0.026
- phase_breakdown.release_1_score: 0.076
- grasp_place_fitness: 0.365

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.365
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.162
- **Median Q (composite search score)**: -0.453
- **K-run variance**: 0.0064
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.300


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":6.52427,"average_solve_count":103.0,"average_success_count":103.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.1085,"approach_1.speed":0.32063,"descend_1.contact_force_threshold":6.56832,"descend_1.grasp_z_offset":0.0176,"descend_1.speed":0.05935,"grasp_1.grasp_force":0.55533,"lift_1.lift_height":0.10997,"lift_1.lift_speed":0.09429,"release_1.release_time":0.18937,"retract_1.retract_height":0.1435,"retract_1.retract_speed":0.33709,"transport_1.arc_height":0.12339,"transport_1.transport_speed":0.22943},"optimized_scores":{"best_composite_score":-0.46838,"best_fitness_score":0.18876,"best_task_score":0.13503},"replay_outcomes":[{"contacts":{"omitted_contact_groups":7,"reported_contact_groups":[{"body_a":"world","body_b":"hand","contact_count":42.0,"contact_point_centroid":[0.52979,0.0365,-0.0048],"force_p95":1015.26296,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1147.5473,"mean_force":225.50734,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48748,-0.02437,-0.01249]},{"body_a":"world","body_b":"link6","contact_count":887.0,"contact_point_centroid":[0.62021,-0.03946,-0.00024],"force_p95":339.87445,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":661.95949,"mean_force":242.23984,"phase_index":4.0,"phase_name":"transport_1","phase_type":"push","tcp_position_centroid":[0.40064,0.0212,0.10139]},{"body_a":"world","body_b":"link7","contact_count":465.0,"contact_point_centroid":[0.57659,-0.0275,-0.00018],"force_p95":276.05301,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":627.97097,"mean_force":199.48056,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44909,-0.03421,0.02204]},{"body_a":"world","body_b":"link6","contact_count":114.0,"contact_point_centroid":[0.62079,-0.01266,-0.00038],"force_p95":242.6865,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":361.86334,"mean_force":166.99808,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.4083,-0.04098,0.04635]},{"body_a":"world","body_b":"link6","contact_count":74.0,"contact_point_centroid":[0.60777,0.11113,-9e-05],"force_p95":71.97143,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":133.75478,"mean_force":45.71445,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.62298,0.08245,0.29074]},{"body_a":"world","body_b":"link7","contact_count":2.0,"contact_point_centroid":[0.56424,-0.02653,-4e-05],"force_p95":75.89604,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":79.89057,"mean_force":39.94528,"phase_index":4.0,"phase_name":"transport_1","phase_type":"push","tcp_position_centroid":[0.40556,-0.04293,0.0452]},{"body_a":"world","body_b":"right_finger","contact_count":797.0,"contact_point_centroid":[0.48926,-0.02132,-0.00944],"force_p95":11.2975,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":35.22186,"mean_force":3.80231,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48703,-0.02456,-0.00893]},{"body_a":"world","body_b":"left_finger","contact_count":795.0,"contact_point_centroid":[0.4895,-0.02762,-0.00945],"force_p95":11.30991,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":35.15201,"mean_force":3.81223,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48705,-0.02456,-0.00898]},{"body_a":"world","body_b":"grasp_target","contact_count":1289.0,"contact_point_centroid":[0.4538,0.01726,-0.00336],"force_p95":0.45796,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.27559,"mean_force":0.24799,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.45287,-0.03294,0.04019]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":859.0,"contact_point_centroid":[0.47989,-0.0238,0.01108],"force_p95":0.27339,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":3.13631,"mean_force":0.15429,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.47898,-0.02733,0.00381]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":685.0,"contact_point_centroid":[0.48265,-0.02922,0.00867],"force_p95":0.26821,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.58799,"mean_force":0.1426,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48211,-0.02636,0.00104]},{"body_a":"grasp_target","body_b":"hand","contact_count":328.0,"contact_point_centroid":[0.46559,0.04446,0.03484],"force_p95":0.59907,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.75419,"mean_force":0.25243,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.43248,-0.03738,0.03181]},{"body_a":"grasp_target","body_b":"hand","contact_count":285.0,"contact_point_centroid":[0.44257,0.07051,0.02641],"force_p95":0.36609,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.50189,"mean_force":0.26662,"phase_index":4.0,"phase_name":"transport_1","phase_type":"push","tcp_position_centroid":[0.37743,0.0248,0.06307]},{"body_a":"world","body_b":"grasp_target","contact_count":3941.0,"contact_point_centroid":[0.41652,0.04237,-0.00231],"force_p95":0.28793,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.43596,"mean_force":0.1427,"phase_index":4.0,"phase_name":"transport_1","phase_type":"push","tcp_position_centroid":[0.41046,0.02114,0.11288]},{"body_a":"world","body_b":"grasp_target","contact_count":1644.0,"contact_point_centroid":[0.47616,-0.02015,-0.00192],"force_p95":0.13462,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12292,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48668,-0.00888,0.22435]},{"body_a":"world","body_b":"grasp_target","contact_count":100.0,"contact_point_centroid":[0.47616,-0.02015,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.47352,-0.01836,0.14528]}],"total_contact_groups":23},"final_pose_error":0.01671,"key_states":{"actual_goal_position":[0.63142,0.15919,0.19002],"final_object_position":[0.41589,0.04311,0.01602],"final_tcp_position":[0.62343,0.08227,0.44368],"realised_goal_position":[0.63142,0.15919,0.19002],"realised_object_initial_position":[0.47616,-0.02015,0.03]},"peak_contact_force":273004.12083,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":412.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.03],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28614,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1644.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.47448,-0.01827,0.14792],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.12193,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":25.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":81.14225,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":100.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.4728,-0.01838,0.14255],"tcp_start":[0.47448,-0.01827,0.14792],"tcp_to_object_dist_end":0.11659,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":150.0,"n_steps_budget":50.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":2956.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_1","tcp_end":[0.46593,-0.01825,0.13406],"tcp_start":[0.46593,-0.01825,0.13406],"tcp_to_object_dist_end":0.10854,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":603.0,"n_steps_budget":690.0,"object_pos_end":[0.42519,0.03951,0.01656],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.29486,"object_to_goal_dist_start":0.28838,"object_z_max":0.05442,"peak_contact_force":115.25336,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":7945.0,"raw_peak_contact_force":1147.5473,"tcp_end":[0.40552,-0.04291,0.04511],"tcp_start":[0.46593,-0.01825,0.13406],"tcp_to_object_dist_end":0.08942,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":998.0,"n_steps_budget":1000.0,"object_pos_end":[0.41589,0.04311,0.01602],"object_pos_start":[0.42519,0.03951,0.01656],"object_to_goal_dist_end":0.30034,"object_to_goal_dist_start":0.29486,"object_z_max":0.01656,"peak_contact_force":237.77998,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":9370.0,"raw_peak_contact_force":661.95949,"subtask_id":"transport_arc","tcp_end":[0.61917,0.07079,0.28999],"tcp_start":[0.40552,-0.04291,0.04511],"tcp_to_object_dist_end":0.34227,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.41589,0.04311,0.01602],"object_pos_start":[0.41589,0.04311,0.01602],"object_to_goal_dist_end":0.30034,"object_to_goal_dist_start":0.30034,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1095.0,"raw_peak_contact_force":133.75478,"subtask_id":"release_1","tcp_end":[0.62247,0.08112,0.31682],"tcp_start":[0.61917,0.07079,0.28999],"tcp_to_object_dist_end":0.36688,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":542.0,"n_steps_budget":600.0,"object_pos_end":[0.41589,0.04311,0.01602],"object_pos_start":[0.41589,0.04311,0.01602],"object_to_goal_dist_end":0.30034,"object_to_goal_dist_start":0.30034,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2168.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.62343,0.08227,0.44368],"tcp_start":[0.62247,0.08112,0.31682],"tcp_to_object_dist_end":0.47697,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":5.0,"average_failure_rate":0.06024,"average_mean_iterations":18.77108,"average_solve_count":83.0,"average_success_count":78.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.10049,"approach_1.speed":0.36635,"descend_1.contact_force_threshold":6.71331,"descend_1.grasp_z_offset":0.00099,"descend_1.speed":0.06963,"grasp_1.grasp_force":0.9562,"lift_1.lift_height":0.11801,"lift_1.lift_speed":0.35651,"release_1.release_time":0.44763,"retract_1.retract_height":0.10043,"retract_1.retract_speed":0.18209,"transport_1.arc_height":0.1383,"transport_1.transport_speed":0.37854},"optimized_scores":{"best_composite_score":-0.45297,"best_fitness_score":0.20418,"best_task_score":0.16176},"replay_outcomes":[{"contacts":{"omitted_contact_groups":14,"reported_contact_groups":[{"body_a":"world","body_b":"link6","contact_count":399.0,"contact_point_centroid":[0.61349,0.00507,-0.00014],"force_p95":493.93575,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1232.3796,"mean_force":289.36227,"phase_index":4.0,"phase_name":"transport_1","phase_type":"push","tcp_position_centroid":[0.39076,-0.03727,0.10782]},{"body_a":"world","body_b":"hand","contact_count":35.0,"contact_point_centroid":[0.50912,-0.08805,-0.00537],"force_p95":1041.06167,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1146.54432,"mean_force":180.24869,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46381,-0.02975,-0.01124]},{"body_a":"world","body_b":"link7","contact_count":201.0,"contact_point_centroid":[0.56821,-0.03108,-0.00041],"force_p95":381.48467,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":962.40133,"mean_force":193.24166,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.42833,-0.03597,0.03005]},{"body_a":"world","body_b":"link6","contact_count":484.0,"contact_point_centroid":[0.51643,0.07949,-0.00025],"force_p95":271.25406,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":741.56148,"mean_force":215.92257,"phase_index":6.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.39475,0.00479,0.24316]},{"body_a":"world","body_b":"link6","contact_count":342.0,"contact_point_centroid":[0.57126,-0.03191,-0.00014],"force_p95":222.9057,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":302.82851,"mean_force":189.13354,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.40194,-0.03981,0.04507]},{"body_a":"world","body_b":"link6","contact_count":72.0,"contact_point_centroid":[0.62612,0.11785,-0.00026],"force_p95":179.81608,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":222.27164,"mean_force":105.53837,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.45508,0.05658,0.20948]},{"body_a":"link5","body_b":"hand","contact_count":265.0,"contact_point_centroid":[0.41462,0.11441,0.21954],"force_p95":110.28856,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":127.7876,"mean_force":67.80343,"phase_index":6.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.38965,-0.00018,0.25771]},{"body_a":"world","body_b":"right_finger","contact_count":642.0,"contact_point_centroid":[0.46626,-0.02652,-0.00985],"force_p95":21.26966,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":34.82226,"mean_force":3.68214,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46405,-0.02976,-0.01011]},{"body_a":"world","body_b":"left_finger","contact_count":642.0,"contact_point_centroid":[0.46641,-0.03284,-0.00989],"force_p95":21.22737,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":34.74223,"mean_force":3.68448,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46405,-0.02976,-0.01011]},{"body_a":"world","body_b":"grasp_target","contact_count":401.0,"contact_point_centroid":[0.45712,-0.02623,-0.00401],"force_p95":3.14939,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.76558,"mean_force":0.39584,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.47805,-0.02785,0.05966]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2411.0,"contact_point_centroid":[0.43167,-0.03095,0.03319],"force_p95":0.40375,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":2.51188,"mean_force":0.18764,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.42954,-0.03585,0.02812]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4184.0,"contact_point_centroid":[0.4244,-0.04275,0.03883],"force_p95":0.41753,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":2.37252,"mean_force":0.20738,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.42133,-0.03706,0.0345]},{"body_a":"world","body_b":"grasp_target","contact_count":1264.0,"contact_point_centroid":[0.56314,-0.03774,-0.00277],"force_p95":0.46612,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.81367,"mean_force":0.16499,"phase_index":6.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.38886,-0.00047,0.252]},{"body_a":"grasp_target","body_b":"hand","contact_count":200.0,"contact_point_centroid":[0.52033,0.06274,0.1754],"force_p95":1.02498,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.40363,"mean_force":0.59732,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.45428,0.05608,0.21551]},{"body_a":"grasp_target","body_b":"hand","contact_count":140.0,"contact_point_centroid":[0.50572,0.0251,0.16736],"force_p95":0.80011,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.94071,"mean_force":0.35573,"phase_index":6.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.41807,0.02475,0.22882]},{"body_a":"grasp_target","body_b":"hand","contact_count":466.0,"contact_point_centroid":[0.45594,-0.02314,0.11316],"force_p95":0.78012,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.9387,"mean_force":0.37252,"phase_index":4.0,"phase_name":"transport_1","phase_type":"push","tcp_position_centroid":[0.39287,-0.03265,0.11493]}],"total_contact_groups":30},"final_pose_error":0.12262,"key_states":{"actual_goal_position":[0.63013,0.20822,0.11412],"final_object_position":[0.56306,-0.03784,0.01602],"final_tcp_position":[0.38181,-0.00735,0.25611],"realised_goal_position":[0.63013,0.20822,0.11412],"realised_object_initial_position":[0.45856,-0.02632,0.03]},"peak_contact_force":273004.12084,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":434.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.03],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30252,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1732.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.45834,-0.02396,0.14015],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.11416,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":236.65345,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.45816,-0.02399,0.1399],"tcp_start":[0.45834,-0.02396,0.14015],"tcp_to_object_dist_end":0.11391,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":150.0,"n_steps_budget":50.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":273004.12084,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":2945.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_1","tcp_end":[0.45129,-0.02383,0.13177],"tcp_start":[0.45129,-0.02383,0.13177],"tcp_to_object_dist_end":0.10603,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":542.0,"n_steps_budget":600.0,"object_pos_end":[0.4178,-0.0346,0.07609],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.32479,"object_to_goal_dist_start":0.30365,"object_z_max":0.08094,"peak_contact_force":208.9508,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":9573.0,"raw_peak_contact_force":1146.54432,"tcp_end":[0.38601,-0.0427,0.04501],"tcp_start":[0.45129,-0.02383,0.13177],"tcp_to_object_dist_end":0.04519,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":7.0,"n_steps":466.0,"n_steps_budget":660.0,"object_pos_end":[0.50787,0.05925,0.2056],"object_pos_start":[0.4178,-0.0346,0.07609],"object_to_goal_dist_end":0.21332,"object_to_goal_dist_start":0.32479,"object_z_max":0.22242,"peak_contact_force":0.31247,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":6433.0,"raw_peak_contact_force":1232.3796,"subtask_id":"transport_arc","tcp_end":[0.4561,0.0542,0.21223],"tcp_start":[0.38601,-0.0427,0.04501],"tcp_to_object_dist_end":0.05243,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.52186,0.05734,0.20407],"object_pos_start":[0.50787,0.05925,0.2056],"object_to_goal_dist_end":0.20634,"object_to_goal_dist_start":0.21332,"object_z_max":0.2056,"peak_contact_force":0.43016,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":644.0,"raw_peak_contact_force":222.27164,"subtask_id":"release_1","tcp_end":[0.45297,0.05519,0.23354],"tcp_start":[0.4561,0.0542,0.21223],"tcp_to_object_dist_end":0.07496,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":6.0,"n_steps":542.0,"n_steps_budget":600.0,"object_pos_end":[0.56306,-0.03784,0.01602],"object_pos_start":[0.52186,0.05734,0.20407],"object_to_goal_dist_end":0.27325,"object_to_goal_dist_start":0.20634,"object_z_max":0.20571,"peak_contact_force":80.23119,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2307.0,"raw_peak_contact_force":741.56148,"tcp_end":[0.38181,-0.00735,0.25611],"tcp_start":[0.45297,0.05519,0.23354],"tcp_to_object_dist_end":0.30236,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":5.28571,"average_solve_count":84.0,"average_success_count":84.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.17819,"approach_1.speed":0.29381,"descend_1.contact_force_threshold":6.41295,"descend_1.grasp_z_offset":0.0137,"descend_1.speed":0.05681,"grasp_1.grasp_force":0.38155,"lift_1.lift_height":0.09348,"lift_1.lift_speed":0.22134,"release_1.release_time":0.30214,"retract_1.retract_height":0.10015,"retract_1.retract_speed":0.17935,"transport_1.arc_height":0.06843,"transport_1.transport_speed":0.31809},"optimized_scores":{"best_composite_score":-0.29205,"best_fitness_score":0.36509,"best_task_score":0.07569},"replay_outcomes":[{"contacts":{"omitted_contact_groups":8,"reported_contact_groups":[{"body_a":"world","body_b":"hand","contact_count":50.0,"contact_point_centroid":[0.59892,0.06469,-0.00379],"force_p95":833.43359,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":954.33297,"mean_force":272.09519,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.54746,0.00564,-0.01017]},{"body_a":"world","body_b":"link6","contact_count":61.0,"contact_point_centroid":[0.5977,0.02548,-6e-05],"force_p95":549.1057,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":671.08315,"mean_force":327.51883,"phase_index":4.0,"phase_name":"transport_1","phase_type":"push","tcp_position_centroid":[0.60301,-0.05749,0.27466]},{"body_a":"world","body_b":"link7","contact_count":31.0,"contact_point_centroid":[0.59947,-0.03857,-0.00072],"force_p95":523.28309,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":529.5558,"mean_force":357.84034,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46699,-0.02722,0.02785]},{"body_a":"world","body_b":"link6","contact_count":53.0,"contact_point_centroid":[0.62562,0.0631,-0.00033],"force_p95":440.22504,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":497.95482,"mean_force":301.93877,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51109,-0.11702,0.14375]},{"body_a":"world","body_b":"link6","contact_count":84.0,"contact_point_centroid":[0.61782,0.14032,-0.00021],"force_p95":110.70599,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":111.53687,"mean_force":67.05411,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.6437,0.14162,0.29296]},{"body_a":"world","body_b":"left_finger","contact_count":1015.0,"contact_point_centroid":[0.54671,0.00135,-0.00662],"force_p95":20.98853,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":45.6846,"mean_force":7.32195,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.54531,0.00494,-0.00599]},{"body_a":"world","body_b":"right_finger","contact_count":1039.0,"contact_point_centroid":[0.54722,0.00757,-0.00656],"force_p95":23.41853,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":45.23471,"mean_force":7.37187,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.54501,0.00488,-0.00573]},{"body_a":"world","body_b":"grasp_target","contact_count":495.0,"contact_point_centroid":[0.54457,0.00135,-0.00245],"force_p95":1.0271,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.57379,"mean_force":0.23488,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.58392,0.00377,0.10275]},{"body_a":"grasp_target","body_b":"hand","contact_count":137.0,"contact_point_centroid":[0.52754,-0.04711,0.08195],"force_p95":1.82296,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":2.31889,"mean_force":1.14907,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49709,-0.0709,0.08779]},{"body_a":"world","body_b":"grasp_target","contact_count":1297.0,"contact_point_centroid":[0.61469,-0.18474,-0.00288],"force_p95":0.48505,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.24197,"mean_force":0.17642,"phase_index":4.0,"phase_name":"transport_1","phase_type":"push","tcp_position_centroid":[0.6252,0.05635,0.3129]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":664.0,"contact_point_centroid":[0.53289,-0.06819,0.08023],"force_p95":0.36134,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.85828,"mean_force":0.19063,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.53069,-0.06784,0.08069]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":642.0,"contact_point_centroid":[0.52269,-0.05684,0.06846],"force_p95":0.43329,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.67415,"mean_force":0.17261,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52162,-0.06186,0.06666]},{"body_a":"grasp_target","body_b":"hand","contact_count":70.0,"contact_point_centroid":[0.61872,-0.10238,0.20121],"force_p95":1.20049,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.40619,"mean_force":0.48299,"phase_index":4.0,"phase_name":"transport_1","phase_type":"push","tcp_position_centroid":[0.60045,-0.07378,0.26496]},{"body_a":"grasp_target","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.62155,-0.10469,0.15486],"force_p95":0.70062,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.70062,"mean_force":0.70062,"phase_index":4.0,"phase_name":"transport_1","phase_type":"push","tcp_position_centroid":[0.60442,-0.02978,0.29191]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3.0,"contact_point_centroid":[0.602,-0.10009,0.22919],"force_p95":0.556,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.55764,"mean_force":0.53204,"phase_index":4.0,"phase_name":"transport_1","phase_type":"push","tcp_position_centroid":[0.59384,-0.10221,0.24028]},{"body_a":"world","body_b":"grasp_target","contact_count":1296.0,"contact_point_centroid":[0.54431,0.00113,-0.0019],"force_p95":0.13564,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.123,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.5166,0.00046,0.25611]}],"total_contact_groups":24},"final_pose_error":0.01471,"key_states":{"actual_goal_position":[0.64762,0.15808,0.1911],"final_object_position":[0.61444,-0.18563,0.01602],"final_tcp_position":[0.64431,0.14268,0.40463],"realised_goal_position":[0.64762,0.15808,0.1911],"realised_object_initial_position":[0.54431,0.00113,0.03]},"peak_contact_force":9748.92575,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":325.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.03],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.24751,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1296.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.53567,0.00094,0.21315],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.18733,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":5.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":81.14225,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":20.0,"raw_peak_contact_force":0.12262,"subtask_id":"descend_1","tcp_end":[0.53539,0.00094,0.21206],"tcp_start":[0.53567,0.00094,0.21315],"tcp_to_object_dist_end":0.18625,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":150.0,"n_steps_budget":50.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":2962.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_1","tcp_end":[0.52936,0.00084,0.20156],"tcp_start":[0.52936,0.00084,0.20156],"tcp_to_object_dist_end":0.17618,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":310.0,"n_steps_budget":600.0,"object_pos_end":[0.58315,-0.1096,0.18177],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.2755,"object_to_goal_dist_start":0.25012,"object_z_max":0.1808,"peak_contact_force":236.83843,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":5034.0,"raw_peak_contact_force":954.33297,"tcp_end":[0.58735,-0.11205,0.22498],"tcp_start":[0.52936,0.00084,0.20156],"tcp_to_object_dist_end":0.04349,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":505.0,"n_steps_budget":600.0,"object_pos_end":[0.61444,-0.18563,0.01602],"object_pos_start":[0.58315,-0.1096,0.18177],"object_to_goal_dist_end":0.38716,"object_to_goal_dist_start":0.2755,"object_z_max":0.22505,"peak_contact_force":9748.92575,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3590.0,"raw_peak_contact_force":671.08315,"subtask_id":"transport_arc","tcp_end":[0.64398,0.14039,0.29343],"tcp_start":[0.58735,-0.11205,0.22498],"tcp_to_object_dist_end":0.42909,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.61444,-0.18563,0.01602],"object_pos_start":[0.61444,-0.18563,0.01602],"object_to_goal_dist_end":0.38716,"object_to_goal_dist_start":0.38716,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1108.0,"raw_peak_contact_force":111.53687,"subtask_id":"release_1","tcp_end":[0.64383,0.14177,0.31916],"tcp_start":[0.64398,0.14039,0.29343],"tcp_to_object_dist_end":0.44715,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":515.0,"n_steps_budget":600.0,"object_pos_end":[0.61444,-0.18563,0.01602],"object_pos_start":[0.61444,-0.18563,0.01602],"object_to_goal_dist_end":0.38716,"object_to_goal_dist_start":0.38716,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2060.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.64431,0.14268,0.40463],"tcp_start":[0.64383,0.14177,0.31916],"tcp_to_object_dist_end":0.5096,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```