## Search State

- **Seed**: 2
- **Iteration**: 6 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 5 | approach → descend → grasp → lift → push → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | — | linear_cartesian | position_control | position_control | position_control | impedance_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 12 | -0.5858 | 0.16 | ✅ accepted |
| 4 | align → align → pull → descend | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | admittance_control | pose_tolerance | pose_tolerance | pose_tolerance | contact_detected | 0 | 0.1073 | 0.16 | ❌ rejected |
| 3 | align → align → pull → descend | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | admittance_control | pose_tolerance | pose_tolerance | pose_tolerance | contact_detected | 0 | 0.1073 | 0.16 | ❌ rejected |
| 2 | align → align → pull → descend | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | admittance_control | pose_tolerance | pose_tolerance | pose_tolerance | contact_detected | 0 | 0.1073 | 0.16 | ❌ rejected |
| 1 | align → align → pull → descend | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | admittance_control | pose_tolerance | pose_tolerance | pose_tolerance | contact_detected | 0 | 0.1073 | 0.16 | ❌ rejected |

**Proposal policy**: task_score is 0.16 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=-0.586) — your mutation base

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

- **Composite score**: -0.586
- **task_score** (E): 0.161
- **fitness_score**: 0.164  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.750

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 0.00 | 1.00 | 0.1472 |
| descend_1 | 0.00 | 1.00 | 0.0380 |
| grasp_1 | 1.00 | 1.00 | 0.0000 |
| lift_1 | 0.00 | 1.00 | 0.1297 |
| transport_1 | 0.67 | 1.00 | 0.2107 |
| release_1 | 1.00 | 1.00 | 0.0276 |
| retract_1 | 0.67 | 1.00 | 0.0955 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 0.00 / step_budget | (0.500, -0.000, 0.301)→(0.430, -0.010, 0.174) | (0.493, -0.015, 0.030)→(0.454, -0.012, 0.016) | 0.279→0.305 | 1.00 / 5.000 | 250.895 | 1394.689 |
| descend_1 | descend | 0.00 / step_budget | (0.430, -0.010, 0.174)→(0.464, -0.026, 0.176) | (0.454, -0.012, 0.016)→(0.454, -0.012, 0.016) | 0.305→0.305 | 1.00 / 5.000 | 232.683 | 850.621 |
| grasp_1 | grasp | 1.00 / step_budget | (0.464, -0.026, 0.175)→(0.464, -0.026, 0.175) | (0.454, -0.012, 0.016)→(0.454, -0.012, 0.016) | 0.305→0.305 | 1.00 / 9.333 | 91052.382 | 207.717 |
| lift_1 | lift | 0.00 / step_budget | (0.464, -0.026, 0.175)→(0.425, 0.048, 0.147) | (0.454, -0.012, 0.016)→(0.454, -0.012, 0.016) | 0.305→0.305 | 1.00 / 9.667 | 56093.077 | 438.746 |
| transport_1 | push | 0.67 / step_budget | (0.425, 0.048, 0.147)→(0.545, 0.134, 0.260) | (0.454, -0.012, 0.016)→(0.459, 0.042, 0.016) | 0.305→0.276 | 1.00 / 9.000 | 271.986 | 1319.324 |
| release_1 | release | 1.00 / step_budget | (0.545, 0.134, 0.260)→(0.545, 0.134, 0.288) | (0.459, 0.042, 0.016)→(0.459, 0.042, 0.016) | 0.276→0.276 | 1.00 / 4.000 | 0.123 | 162.703 |
| retract_1 | retract | 0.67 / step_budget | (0.545, 0.134, 0.288)→(0.529, 0.138, 0.376) | (0.459, 0.042, 0.016)→(0.459, 0.042, 0.016) | 0.276→0.276 | 1.00 / 4.000 | 0.123 | 279.245 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 0.000
- place_accuracy: 0.000
- lift_clearance: 0.000
- transport_retention: None
- terminal_score: 0.186
- phase_score: 0.241
- phase_breakdown.transport_arc_score: 0.125
- phase_breakdown.approach_1_score: 0.045
- phase_breakdown.release_1_score: 0.074
- phase_breakdown.grasp_1_score: 1.000
- phase_breakdown.descend_1_score: 0.085
- grasp_place_fitness: 0.180

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.180
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.186
- **Median Q (composite search score)**: -0.580
- **K-run variance**: 0.0003
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.271


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":7.06122,"average_solve_count":98.0,"average_success_count":98.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.16473,"approach_1.speed":0.24361,"descend_1.grasp_z_offset":0.02178,"descend_1.speed":0.27747,"grasp_1.grasp_force":0.42731,"lift_1.lift_height":0.10339,"lift_1.lift_speed":0.23856,"release_1.release_time":0.33488,"retract_1.retract_height":0.10827,"retract_1.retract_speed":0.23808,"transport_1.arc_height":0.08985,"transport_1.transport_speed":0.34611},"optimized_scores":{"best_composite_score":-0.56953,"best_fitness_score":0.18047,"best_task_score":0.1859},"replay_outcomes":[{"contacts":{"omitted_contact_groups":6,"reported_contact_groups":[{"body_a":"world","body_b":"link6","contact_count":886.0,"contact_point_centroid":[0.62839,-0.00645,-0.00048],"force_p95":205.58623,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1372.51481,"mean_force":204.42068,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.39273,-0.00649,0.13289]},{"body_a":"world","body_b":"link6","contact_count":976.0,"contact_point_centroid":[0.62152,-0.01523,-0.00021],"force_p95":507.97136,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":924.72579,"mean_force":294.4339,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.42477,-0.01792,0.19191]},{"body_a":"world","body_b":"link6","contact_count":313.0,"contact_point_centroid":[0.50941,-0.03817,-0.00015],"force_p95":637.10583,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":707.01543,"mean_force":358.2528,"phase_index":4.0,"phase_name":"transport_1","phase_type":"push","tcp_position_centroid":[0.49804,0.06285,0.25987]},{"body_a":"world","body_b":"link7","contact_count":20.0,"contact_point_centroid":[0.52597,0.00151,-0.0035],"force_p95":26.83971,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":536.79412,"mean_force":26.83971,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.37056,-0.00265,0.05059]},{"body_a":"world","body_b":"link6","contact_count":439.0,"contact_point_centroid":[0.60065,-0.06404,-0.00017],"force_p95":306.30843,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":427.15431,"mean_force":236.59213,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.45318,0.08692,0.15962]},{"body_a":"world","body_b":"link6","contact_count":550.0,"contact_point_centroid":[0.67717,-0.01931,-0.00012],"force_p95":72.12245,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":215.97392,"mean_force":69.17604,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46439,-0.04114,0.16958]},{"body_a":"link5","body_b":"hand","contact_count":47.0,"contact_point_centroid":[0.45175,-0.05451,0.2639],"force_p95":192.87847,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":203.22051,"mean_force":162.32345,"phase_index":4.0,"phase_name":"transport_1","phase_type":"push","tcp_position_centroid":[0.48654,0.04084,0.28207]},{"body_a":"world","body_b":"link6","contact_count":85.0,"contact_point_centroid":[0.60251,0.1351,-9e-05],"force_p95":84.1916,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":152.89086,"mean_force":55.32722,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.61578,0.15552,0.29333]},{"body_a":"grasp_target","body_b":"hand","contact_count":37.0,"contact_point_centroid":[0.45656,-0.02013,0.03993],"force_p95":3.78245,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":4.16618,"mean_force":1.76102,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.38127,-0.0026,0.05217]},{"body_a":"grasp_target","body_b":"link7","contact_count":27.0,"contact_point_centroid":[0.48062,-0.00668,0.01011],"force_p95":0.64008,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":3.75264,"mean_force":0.43587,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.37126,-0.00266,0.05485]},{"body_a":"world","body_b":"grasp_target","contact_count":3938.0,"contact_point_centroid":[0.4404,-0.02091,-0.00214],"force_p95":0.13728,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.09038,"mean_force":0.13862,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.40443,-0.00596,0.1413]},{"body_a":"world","body_b":"grasp_target","contact_count":1789.0,"contact_point_centroid":[0.44183,0.01768,-0.00288],"force_p95":0.51047,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.04371,"mean_force":0.21495,"phase_index":4.0,"phase_name":"transport_1","phase_type":"push","tcp_position_centroid":[0.52423,0.09014,0.27122]},{"body_a":"grasp_target","body_b":"link6","contact_count":260.0,"contact_point_centroid":[0.46375,-0.00838,0.03483],"force_p95":1.21241,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":2.011,"mean_force":0.43412,"phase_index":4.0,"phase_name":"transport_1","phase_type":"push","tcp_position_centroid":[0.5069,0.04939,0.28662]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.46034,0.09476,-0.00199],"force_p95":0.12322,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12497,"mean_force":0.12265,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.61582,0.15536,0.29953]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.43546,-0.02102,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.42559,-0.01812,0.19202]},{"body_a":"world","body_b":"grasp_target","contact_count":2200.0,"contact_point_centroid":[0.43546,-0.02102,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46439,-0.04114,0.16958]}],"total_contact_groups":22},"final_pose_error":0.01502,"key_states":{"actual_goal_position":[0.63142,0.15919,0.19002],"final_object_position":[0.46034,0.09476,0.01602],"final_tcp_position":[0.61691,0.15444,0.41276],"realised_goal_position":[0.63142,0.15919,0.19002],"realised_object_initial_position":[0.47616,-0.02015,0.03]},"peak_contact_force":273004.12066,"phases":[{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.43546,-0.02102,0.01602],"object_pos_start":[0.47616,-0.02015,0.03],"object_to_goal_dist_end":0.31804,"object_to_goal_dist_start":0.28614,"object_z_max":0.03,"peak_contact_force":201.8645,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4908.0,"raw_peak_contact_force":1372.51481,"subtask_id":"approach_1","tcp_end":[0.40742,-0.01246,0.16917],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.15593,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.43546,-0.02102,0.01602],"object_pos_start":[0.43546,-0.02102,0.01602],"object_to_goal_dist_end":0.31804,"object_to_goal_dist_start":0.31804,"object_z_max":0.01602,"peak_contact_force":0.62457,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4976.0,"raw_peak_contact_force":924.72579,"subtask_id":"descend_1","tcp_end":[0.46447,-0.04102,0.17083],"tcp_start":[0.40742,-0.01246,0.16917],"tcp_to_object_dist_end":0.15877,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":150.0,"n_steps_budget":50.0,"object_pos_end":[0.43546,-0.02102,0.01602],"object_pos_start":[0.43546,-0.02102,0.01602],"object_to_goal_dist_end":0.31804,"object_to_goal_dist_start":0.31804,"object_z_max":0.01602,"peak_contact_force":85.36093,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":3531.0,"raw_peak_contact_force":215.97392,"subtask_id":"grasp_1","tcp_end":[0.46437,-0.04117,0.16946],"tcp_start":[0.46437,-0.04116,0.16946],"tcp_to_object_dist_end":0.15744,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":467.0,"n_steps_budget":600.0,"object_pos_end":[0.43546,-0.02102,0.01602],"object_pos_start":[0.43546,-0.02102,0.01602],"object_to_goal_dist_end":0.31804,"object_to_goal_dist_start":0.31804,"object_z_max":0.01602,"peak_contact_force":219.17909,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":4286.0,"raw_peak_contact_force":427.15431,"tcp_end":[0.45712,0.12243,0.16978],"tcp_start":[0.46437,-0.04117,0.16946],"tcp_to_object_dist_end":0.2114,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":571.0,"n_steps_budget":600.0,"object_pos_end":[0.46029,0.09471,0.01604],"object_pos_start":[0.43546,-0.02102,0.01602],"object_to_goal_dist_end":0.25241,"object_to_goal_dist_start":0.31804,"object_z_max":0.02338,"peak_contact_force":395.75551,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":4873.0,"raw_peak_contact_force":707.01543,"subtask_id":"transport_arc","tcp_end":[0.61567,0.15575,0.29273],"tcp_start":[0.45712,0.12243,0.16978],"tcp_to_object_dist_end":0.32315,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.46034,0.09476,0.01602],"object_pos_start":[0.46029,0.09471,0.01604],"object_to_goal_dist_end":0.25238,"object_to_goal_dist_start":0.25241,"object_z_max":0.01604,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1105.0,"raw_peak_contact_force":152.89086,"subtask_id":"release_1","tcp_end":[0.616,0.1552,0.31946],"tcp_start":[0.61567,0.15575,0.29273],"tcp_to_object_dist_end":0.34635,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":533.0,"n_steps_budget":600.0,"object_pos_end":[0.46034,0.09476,0.01602],"object_pos_start":[0.46034,0.09476,0.01602],"object_to_goal_dist_end":0.25238,"object_to_goal_dist_start":0.25238,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2132.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.61691,0.15444,0.41276],"tcp_start":[0.616,0.1552,0.31946],"tcp_to_object_dist_end":0.43067,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":7.69608,"average_solve_count":102.0,"average_success_count":102.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.11909,"approach_1.speed":0.4389,"descend_1.grasp_z_offset":0.01291,"descend_1.speed":0.25439,"grasp_1.grasp_force":0.99476,"lift_1.lift_height":0.08913,"lift_1.lift_speed":0.12352,"release_1.release_time":0.21525,"retract_1.retract_height":0.0906,"retract_1.retract_speed":0.13797,"transport_1.arc_height":0.16188,"transport_1.transport_speed":0.35644},"optimized_scores":{"best_composite_score":-0.60742,"best_fitness_score":0.14258,"best_task_score":0.13033},"replay_outcomes":[{"contacts":{"omitted_contact_groups":9,"reported_contact_groups":[{"body_a":"world","body_b":"link6","contact_count":559.0,"contact_point_centroid":[0.57725,0.03913,-0.00018],"force_p95":715.74658,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1685.55616,"mean_force":316.09256,"phase_index":4.0,"phase_name":"transport_1","phase_type":"push","tcp_position_centroid":[0.36601,-0.00947,0.13869]},{"body_a":"world","body_b":"link6","contact_count":887.0,"contact_point_centroid":[0.63235,-0.0088,-0.00044],"force_p95":218.26447,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1321.64587,"mean_force":207.7145,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.39704,-0.00863,0.13165]},{"body_a":"world","body_b":"link7","contact_count":22.0,"contact_point_centroid":[0.52616,-4e-05,-0.00312],"force_p95":379.62341,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1250.82737,"mean_force":75.01959,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.3735,-0.00335,0.04772]},{"body_a":"world","body_b":"link6","contact_count":982.0,"contact_point_centroid":[0.61683,-0.02179,-0.00023],"force_p95":509.4794,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":937.09469,"mean_force":293.81652,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.42414,-0.02358,0.19703]},{"body_a":"world","body_b":"link6","contact_count":425.0,"contact_point_centroid":[0.44253,0.14287,-0.00024],"force_p95":293.20378,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":837.4899,"mean_force":238.9749,"phase_index":6.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.33443,0.14344,0.25961]},{"body_a":"link5","body_b":"hand","contact_count":176.0,"contact_point_centroid":[0.47738,0.14767,0.20879],"force_p95":299.92629,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":461.71305,"mean_force":111.52081,"phase_index":4.0,"phase_name":"transport_1","phase_type":"push","tcp_position_centroid":[0.43533,0.04827,0.23048]},{"body_a":"world","body_b":"link6","contact_count":437.0,"contact_point_centroid":[0.62585,-0.03824,-0.0003],"force_p95":224.21297,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":258.37742,"mean_force":198.75857,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.3877,-0.04878,0.11829]},{"body_a":"world","body_b":"link6","contact_count":547.0,"contact_point_centroid":[0.672,-0.034,-0.00012],"force_p95":72.16055,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":235.87964,"mean_force":69.46597,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46229,-0.0377,0.18562]},{"body_a":"world","body_b":"link7","contact_count":66.0,"contact_point_centroid":[0.48172,-0.13095,-0.00022],"force_p95":207.51938,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":208.39038,"mean_force":116.45344,"phase_index":4.0,"phase_name":"transport_1","phase_type":"push","tcp_position_centroid":[0.34343,-0.08502,0.05824]},{"body_a":"world","body_b":"link6","contact_count":72.0,"contact_point_centroid":[0.57458,0.16897,-8e-05],"force_p95":126.22637,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":176.78054,"mean_force":80.52256,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.38261,0.13285,0.19698]},{"body_a":"grasp_target","body_b":"hand","contact_count":41.0,"contact_point_centroid":[0.43939,-0.01732,0.04254],"force_p95":3.52332,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":3.93737,"mean_force":1.40253,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.38279,-0.00333,0.05109]},{"body_a":"grasp_target","body_b":"hand","contact_count":229.0,"contact_point_centroid":[0.42913,-0.03653,0.03756],"force_p95":0.91859,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.8989,"mean_force":0.44096,"phase_index":4.0,"phase_name":"transport_1","phase_type":"push","tcp_position_centroid":[0.33598,-0.07218,0.07277]},{"body_a":"world","body_b":"grasp_target","contact_count":3907.0,"contact_point_centroid":[0.42246,-0.02487,-0.00213],"force_p95":0.13797,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.33686,"mean_force":0.13851,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.40852,-0.00797,0.14074]},{"body_a":"grasp_target","body_b":"link7","contact_count":194.0,"contact_point_centroid":[0.42959,-0.02645,0.03998],"force_p95":0.87015,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.10634,"mean_force":0.42505,"phase_index":4.0,"phase_name":"transport_1","phase_type":"push","tcp_position_centroid":[0.33125,-0.06678,0.08065]},{"body_a":"world","body_b":"grasp_target","contact_count":2296.0,"contact_point_centroid":[0.40841,3e-05,-0.00258],"force_p95":0.43926,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.84443,"mean_force":0.17688,"phase_index":4.0,"phase_name":"transport_1","phase_type":"push","tcp_position_centroid":[0.37657,0.00081,0.1445]},{"body_a":"world","body_b":"grasp_target","contact_count":1764.0,"contact_point_centroid":[0.41726,-0.02464,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12653,"mean_force":0.12264,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.3883,-0.0487,0.11888]}],"total_contact_groups":25},"final_pose_error":0.0633,"key_states":{"actual_goal_position":[0.63013,0.20822,0.11412],"final_object_position":[0.40841,0.02209,0.01602],"final_tcp_position":[0.33003,0.14239,0.28071],"realised_goal_position":[0.63013,0.20822,0.11412],"realised_object_initial_position":[0.45856,-0.02632,0.03]},"peak_contact_force":167951.73011,"phases":[{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.41726,-0.02464,0.01602],"object_pos_start":[0.45856,-0.02632,0.03],"object_to_goal_dist_end":0.33039,"object_to_goal_dist_start":0.30252,"object_z_max":0.03,"peak_contact_force":204.96806,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4857.0,"raw_peak_contact_force":1321.64587,"subtask_id":"approach_1","tcp_end":[0.41844,-0.01767,0.17953],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.16367,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.41726,-0.02464,0.01602],"object_pos_start":[0.41726,-0.02464,0.01602],"object_to_goal_dist_end":0.33039,"object_to_goal_dist_start":0.33039,"object_z_max":0.01602,"peak_contact_force":363.65036,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4982.0,"raw_peak_contact_force":937.09469,"subtask_id":"descend_1","tcp_end":[0.46246,-0.03749,0.18679],"tcp_start":[0.41844,-0.01767,0.17953],"tcp_to_object_dist_end":0.17712,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":150.0,"n_steps_budget":50.0,"object_pos_end":[0.41726,-0.02464,0.01602],"object_pos_start":[0.41726,-0.02464,0.01602],"object_to_goal_dist_end":0.33039,"object_to_goal_dist_start":0.33039,"object_z_max":0.01602,"peak_contact_force":67.66417,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":3527.0,"raw_peak_contact_force":235.87964,"subtask_id":"grasp_1","tcp_end":[0.46228,-0.03774,0.1855],"tcp_start":[0.46228,-0.03773,0.1855],"tcp_to_object_dist_end":0.17585,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":11.0,"n_steps":441.0,"n_steps_budget":600.0,"object_pos_end":[0.41726,-0.02464,0.01601],"object_pos_start":[0.41726,-0.02464,0.01602],"object_to_goal_dist_end":0.33039,"object_to_goal_dist_start":0.33039,"object_z_max":0.01602,"peak_contact_force":167951.73011,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":4051.0,"raw_peak_contact_force":258.37742,"tcp_end":[0.35958,-0.05308,0.08011],"tcp_start":[0.46228,-0.03774,0.1855],"tcp_to_object_dist_end":0.0908,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":691.0,"n_steps_budget":720.0,"object_pos_end":[0.40841,0.02209,0.01602],"object_pos_start":[0.41726,-0.02464,0.01601],"object_to_goal_dist_end":0.30566,"object_to_goal_dist_start":0.33039,"object_z_max":0.03332,"peak_contact_force":100.12195,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":6442.0,"raw_peak_contact_force":1685.55616,"subtask_id":"transport_arc","tcp_end":[0.38241,0.13259,0.19626],"tcp_start":[0.35958,-0.05308,0.08011],"tcp_to_object_dist_end":0.21301,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.40841,0.02209,0.01602],"object_pos_start":[0.40841,0.02209,0.01602],"object_to_goal_dist_end":0.30566,"object_to_goal_dist_start":0.30566,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1089.0,"raw_peak_contact_force":176.78054,"subtask_id":"release_1","tcp_end":[0.3812,0.13234,0.22598],"tcp_start":[0.38241,0.13259,0.19626],"tcp_to_object_dist_end":0.2387,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":513.0,"n_steps_budget":600.0,"object_pos_end":[0.40841,0.02209,0.01602],"object_pos_start":[0.40841,0.02209,0.01602],"object_to_goal_dist_end":0.30566,"object_to_goal_dist_start":0.30566,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2477.0,"raw_peak_contact_force":837.4899,"tcp_end":[0.33003,0.14239,0.28071],"tcp_start":[0.3812,0.13234,0.22598],"tcp_to_object_dist_end":0.30113,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":14.0,"average_failure_rate":0.12844,"average_mean_iterations":32.2844,"average_solve_count":109.0,"average_success_count":95.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.10764,"approach_1.speed":0.23023,"descend_1.grasp_z_offset":0.0459,"descend_1.speed":0.36349,"grasp_1.grasp_force":0.47059,"lift_1.lift_height":0.07063,"lift_1.lift_speed":0.21413,"release_1.release_time":0.44359,"retract_1.retract_height":0.13466,"retract_1.retract_speed":0.17543,"transport_1.arc_height":0.1466,"transport_1.transport_speed":0.16442},"optimized_scores":{"best_composite_score":-0.58047,"best_fitness_score":0.16953,"best_task_score":0.16654},"replay_outcomes":[{"contacts":{"omitted_contact_groups":7,"reported_contact_groups":[{"body_a":"world","body_b":"link6","contact_count":674.0,"contact_point_centroid":[0.60727,0.03255,-0.00024],"force_p95":359.84114,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1565.40018,"mean_force":245.36965,"phase_index":4.0,"phase_name":"transport_1","phase_type":"push","tcp_position_centroid":[0.42158,0.14782,0.13704]},{"body_a":"world","body_b":"link6","contact_count":661.0,"contact_point_centroid":[0.65298,0.00043,-0.00045],"force_p95":481.06758,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1489.90492,"mean_force":228.46165,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.42832,0.00029,0.14728]},{"body_a":"world","body_b":"link6","contact_count":531.0,"contact_point_centroid":[0.66275,0.00235,-0.00023],"force_p95":415.70649,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":690.04134,"mean_force":217.01531,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.4478,-9e-05,0.16752]},{"body_a":"world","body_b":"link6","contact_count":475.0,"contact_point_centroid":[0.65121,-0.004,-0.00024],"force_p95":262.85725,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":630.70587,"mean_force":210.55566,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44551,0.05229,0.17026]},{"body_a":"world","body_b":"link7","contact_count":22.0,"contact_point_centroid":[0.53799,0.00384,-0.00356],"force_p95":0.0,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":391.24481,"mean_force":17.78385,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.38565,-0.00011,0.0476]},{"body_a":"world","body_b":"hand","contact_count":81.0,"contact_point_centroid":[0.54284,0.18138,-0.00015],"force_p95":137.51886,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":188.34037,"mean_force":81.24789,"phase_index":4.0,"phase_name":"transport_1","phase_type":"push","tcp_position_centroid":[0.42477,0.20281,0.09163]},{"body_a":"world","body_b":"link6","contact_count":550.0,"contact_point_centroid":[0.67894,0.005,-0.00012],"force_p95":71.80851,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":171.29724,"mean_force":68.22456,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.4648,0.00065,0.16922]},{"body_a":"world","body_b":"link6","contact_count":86.0,"contact_point_centroid":[0.61421,0.14341,-0.00012],"force_p95":75.48298,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":158.43626,"mean_force":55.99856,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.63809,0.1161,0.29202]},{"body_a":"grasp_target","body_b":"link7","contact_count":181.0,"contact_point_centroid":[0.5249,0.00477,0.03203],"force_p95":3.34994,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":4.77713,"mean_force":0.69439,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.4004,1e-05,0.09682]},{"body_a":"grasp_target","body_b":"link6","contact_count":113.0,"contact_point_centroid":[0.54772,0.01426,0.02719],"force_p95":0.85462,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":4.65866,"mean_force":0.48558,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.39492,-2e-05,0.08998]},{"body_a":"grasp_target","body_b":"hand","contact_count":93.0,"contact_point_centroid":[0.50095,0.01357,0.04441],"force_p95":2.49647,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":3.31859,"mean_force":1.04484,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.39491,-4e-05,0.07636]},{"body_a":"world","body_b":"grasp_target","contact_count":2880.0,"contact_point_centroid":[0.51654,0.00788,-0.00226],"force_p95":0.29957,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.73407,"mean_force":0.16166,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.44254,0.00031,0.16052]},{"body_a":"grasp_target","body_b":"link6","contact_count":242.0,"contact_point_centroid":[0.5403,0.02194,0.03599],"force_p95":0.17675,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.71764,"mean_force":0.13144,"phase_index":4.0,"phase_name":"transport_1","phase_type":"push","tcp_position_centroid":[0.41962,0.19476,0.09771]},{"body_a":"world","body_b":"grasp_target","contact_count":3364.0,"contact_point_centroid":[0.50844,0.00941,-0.00201],"force_p95":0.19006,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.38682,"mean_force":0.12634,"phase_index":4.0,"phase_name":"transport_1","phase_type":"push","tcp_position_centroid":[0.44172,0.12877,0.15666]},{"body_a":"world","body_b":"grasp_target","contact_count":2168.0,"contact_point_centroid":[0.50908,0.00977,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.44813,-8e-05,0.16776]},{"body_a":"world","body_b":"grasp_target","contact_count":2200.0,"contact_point_centroid":[0.50908,0.00977,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.4648,0.00065,0.16922]}],"total_contact_groups":23},"final_pose_error":0.01706,"key_states":{"actual_goal_position":[0.64762,0.15808,0.1911],"final_object_position":[0.50822,0.00907,0.01602],"final_tcp_position":[0.63895,0.11672,0.43538],"realised_goal_position":[0.64762,0.15808,0.1911],"realised_object_initial_position":[0.54431,0.00113,0.03]},"peak_contact_force":273004.12063,"phases":[{"contact_detected":true,"contact_event_count":5.0,"n_steps":782.0,"n_steps_budget":1000.0,"object_pos_end":[0.50908,0.00977,0.01602],"object_pos_start":[0.54431,0.00113,0.03],"object_to_goal_dist_end":0.26804,"object_to_goal_dist_start":0.24751,"object_z_max":0.03,"peak_contact_force":345.85197,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3950.0,"raw_peak_contact_force":1489.90492,"subtask_id":"approach_1","tcp_end":[0.465,0.00089,0.17221],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.16253,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":542.0,"n_steps_budget":1000.0,"object_pos_end":[0.50908,0.00977,0.01602],"object_pos_start":[0.50908,0.00977,0.01602],"object_to_goal_dist_end":0.26804,"object_to_goal_dist_start":0.26804,"object_z_max":0.01602,"peak_contact_force":333.77276,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2699.0,"raw_peak_contact_force":690.04134,"subtask_id":"descend_1","tcp_end":[0.46501,0.00041,0.17086],"tcp_start":[0.465,0.00089,0.17221],"tcp_to_object_dist_end":0.16126,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":10.0,"n_steps":150.0,"n_steps_budget":50.0,"object_pos_end":[0.50908,0.00977,0.01602],"object_pos_start":[0.50908,0.00977,0.01602],"object_to_goal_dist_end":0.26804,"object_to_goal_dist_start":0.26804,"object_z_max":0.01602,"peak_contact_force":273004.12063,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":3535.0,"raw_peak_contact_force":171.29724,"subtask_id":"grasp_1","tcp_end":[0.46479,0.00062,0.16909],"tcp_start":[0.46479,0.00062,0.16909],"tcp_to_object_dist_end":0.15961,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":484.0,"n_steps_budget":600.0,"object_pos_end":[0.50908,0.00977,0.01602],"object_pos_start":[0.50908,0.00977,0.01602],"object_to_goal_dist_end":0.26804,"object_to_goal_dist_start":0.26804,"object_z_max":0.01602,"peak_contact_force":108.32214,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":4471.0,"raw_peak_contact_force":630.70587,"tcp_end":[0.45885,0.07478,0.19041],"tcp_start":[0.46479,0.00062,0.16909],"tcp_to_object_dist_end":0.19277,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":841.0,"n_steps_budget":870.0,"object_pos_end":[0.50822,0.00907,0.01602],"object_pos_start":[0.50908,0.00977,0.01602],"object_to_goal_dist_end":0.26887,"object_to_goal_dist_start":0.26804,"object_z_max":0.01637,"peak_contact_force":320.08131,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":7941.0,"raw_peak_contact_force":1565.40018,"subtask_id":"transport_arc","tcp_end":[0.63736,0.11267,0.29151],"tcp_start":[0.45885,0.07478,0.19041],"tcp_to_object_dist_end":0.32141,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50822,0.00907,0.01602],"object_pos_start":[0.50822,0.00907,0.01602],"object_to_goal_dist_end":0.26887,"object_to_goal_dist_start":0.26887,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1109.0,"raw_peak_contact_force":158.43626,"subtask_id":"release_1","tcp_end":[0.63803,0.11566,0.31771],"tcp_start":[0.63736,0.11267,0.29151],"tcp_to_object_dist_end":0.3453,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":542.0,"n_steps_budget":600.0,"object_pos_end":[0.50822,0.00907,0.01602],"object_pos_start":[0.50822,0.00907,0.01602],"object_to_goal_dist_end":0.26887,"object_to_goal_dist_start":0.26887,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2168.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.63895,0.11672,0.43538],"tcp_start":[0.63803,0.11566,0.31771],"tcp_to_object_dist_end":0.45226,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```