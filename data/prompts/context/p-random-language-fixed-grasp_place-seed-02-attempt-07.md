## Search State

- **Seed**: 2
- **Iteration**: 8 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 7 | approach → descend → grasp → lift → push → release → retract | arc_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | — | linear_cartesian | position_control | impedance_control | position_control | impedance_control | position_control | position_control | position_control | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 14 | -0.5320 | 0.14 | ❌ rejected |
| 6 | approach → descend → grasp → lift → push → release → retract | arc_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | — | linear_cartesian | position_control | admittance_control | position_control | impedance_control | position_control | position_control | position_control | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 14 | -0.6791 | 0.13 | ❌ rejected |
| 5 | approach → descend → grasp → lift → push → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | — | linear_cartesian | position_control | position_control | position_control | impedance_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 12 | -0.5858 | 0.16 | ✅ accepted |
| 4 | align → align → pull → descend | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | admittance_control | pose_tolerance | pose_tolerance | pose_tolerance | contact_detected | 0 | 0.1073 | 0.16 | ❌ rejected |
| 3 | align → align → pull → descend | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | admittance_control | pose_tolerance | pose_tolerance | pose_tolerance | contact_detected | 0 | 0.1073 | 0.16 | ❌ rejected |

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

## Current Skill (Q=-0.532) — your mutation base

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

- **Composite score**: -0.532
- **task_score** (E): 0.144
- **fitness_score**: 0.175  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.143
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.850

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 0.00 | 1.00 | 0.1863 |
| descend_1 | 1.00 | 1.00 | 0.0001 |
| grasp_1 | 1.00 | 1.00 | 0.0000 |
| lift_1 | 0.00 | 1.00 | 0.0379 |
| transport_1 | 0.33 | 1.00 | 0.2372 |
| release_1 | 1.00 | 1.00 | 0.0278 |
| retract_1 | 0.67 | 1.00 | 0.1053 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 0.00 / step_budget | (0.500, -0.000, 0.301)→(0.409, -0.010, 0.141) | (0.493, -0.015, 0.030)→(0.455, -0.011, 0.016) | 0.279→0.304 | 1.00 / 5.000 | 251.267 | 1533.157 |
| descend_1 | descend | 1.00 / force_exceeded | (0.409, -0.010, 0.141)→(0.409, -0.010, 0.141) | (0.455, -0.011, 0.016)→(0.455, -0.011, 0.016) | 0.304→0.304 | 1.00 / 5.000 | 734.365 | 284.955 |
| grasp_1 | grasp | 1.00 / step_budget | (0.410, -0.010, 0.141)→(0.410, -0.010, 0.141) | (0.455, -0.011, 0.016)→(0.455, -0.011, 0.016) | 0.304→0.304 | 1.00 / 9.333 | 72.945 | 278.722 |
| lift_1 | lift | 0.00 / step_budget | (0.410, -0.010, 0.141)→(0.388, -0.004, 0.131) | (0.455, -0.011, 0.016)→(0.455, -0.011, 0.016) | 0.304→0.304 | 1.00 / 9.333 | 91135.686 | 271.042 |
| transport_1 | push | 0.33 / step_budget | (0.388, -0.004, 0.131)→(0.548, 0.096, 0.268) | (0.455, -0.011, 0.016)→(0.448, 0.015, 0.016) | 0.304→0.295 | 1.00 / 9.333 | 398.597 | 1120.550 |
| release_1 | release | 1.00 / step_budget | (0.548, 0.096, 0.268)→(0.551, 0.099, 0.294) | (0.448, 0.015, 0.016)→(0.448, 0.015, 0.016) | 0.295→0.295 | 1.00 / 4.000 | 0.123 | 179.396 |
| retract_1 | retract | 0.67 / step_budget | (0.551, 0.099, 0.294)→(0.526, 0.085, 0.386) | (0.448, 0.015, 0.016)→(0.448, 0.015, 0.016) | 0.295→0.295 | 1.00 / 4.000 | 0.123 | 216.985 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 0.000
- place_accuracy: 0.000
- lift_clearance: 0.000
- transport_retention: None
- terminal_score: 0.190
- phase_score: 0.236
- phase_breakdown.transport_arc_score: 0.119
- phase_breakdown.approach_1_score: 0.049
- phase_breakdown.release_1_score: 0.073
- phase_breakdown.grasp_1_score: 1.000
- phase_breakdown.descend_1_score: 0.068
- grasp_place_fitness: 0.187

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.187
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.190
- **Median Q (composite search score)**: -0.534
- **K-run variance**: 0.0001
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.292


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":6.97872,"average_solve_count":94.0,"average_success_count":94.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.19969,"approach_1.arc_height":0.20715,"approach_1.speed":0.49997,"descend_1.contact_force":1.44262,"descend_1.grasp_z_offset":0.02072,"descend_1.speed":0.33007,"grasp_1.grasp_force":0.60587,"lift_1.lift_height":0.09517,"lift_1.lift_speed":0.29763,"release_1.release_time":0.32533,"retract_1.retract_height":0.13769,"retract_1.retract_speed":0.16537,"transport_1.arc_height":0.16043,"transport_1.transport_speed":0.22975},"optimized_scores":{"best_composite_score":-0.54234,"best_fitness_score":0.1648,"best_task_score":0.127},"replay_outcomes":[{"contacts":{"omitted_contact_groups":8,"reported_contact_groups":[{"body_a":"world","body_b":"link6","contact_count":527.0,"contact_point_centroid":[0.54243,-0.00268,-0.00016],"force_p95":272.36641,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1740.93766,"mean_force":227.21965,"phase_index":4.0,"phase_name":"transport_1","phase_type":"push","tcp_position_centroid":[0.32798,-0.00755,0.07504]},{"body_a":"world","body_b":"link6","contact_count":886.0,"contact_point_centroid":[0.62738,-0.00188,-0.00048],"force_p95":212.15333,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1362.52177,"mean_force":205.44361,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.38462,-0.00249,0.12091]},{"body_a":"world","body_b":"link7","contact_count":20.0,"contact_point_centroid":[0.52423,0.00492,-0.00339],"force_p95":26.53254,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":530.65079,"mean_force":26.53254,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.36888,0.0002,0.05094]},{"body_a":"world","body_b":"link6","contact_count":550.0,"contact_point_centroid":[0.6227,-0.00763,-0.00013],"force_p95":80.3065,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":333.05935,"mean_force":73.43546,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.39034,-0.00876,0.14326]},{"body_a":"world","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.62207,-0.00795,-0.00025],"force_p95":305.7734,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":305.7734,"mean_force":305.7734,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.38998,-0.00905,0.14345]},{"body_a":"world","body_b":"link6","contact_count":513.0,"contact_point_centroid":[0.61522,-0.01098,-0.00026],"force_p95":207.91906,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":281.35332,"mean_force":204.07578,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.36832,-0.01165,0.11597]},{"body_a":"world","body_b":"link7","contact_count":103.0,"contact_point_centroid":[0.45333,-0.01972,-8e-05],"force_p95":182.32801,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":225.81837,"mean_force":104.13606,"phase_index":4.0,"phase_name":"transport_1","phase_type":"push","tcp_position_centroid":[0.31462,-0.0218,0.0438]},{"body_a":"world","body_b":"link6","contact_count":64.0,"contact_point_centroid":[0.60702,0.13048,-9e-05],"force_p95":73.62466,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":131.43278,"mean_force":40.52326,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.5909,0.07844,0.28743]},{"body_a":"grasp_target","body_b":"hand","contact_count":37.0,"contact_point_centroid":[0.45667,-0.0192,0.0395],"force_p95":3.82808,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":4.16867,"mean_force":1.77844,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.37959,0.00024,0.05246]},{"body_a":"grasp_target","body_b":"link7","contact_count":30.0,"contact_point_centroid":[0.48008,-0.00338,0.01],"force_p95":2.2841,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":3.77824,"mean_force":0.52987,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.37006,0.0002,0.05614]},{"body_a":"grasp_target","body_b":"link7","contact_count":519.0,"contact_point_centroid":[0.45102,-0.01821,0.02067],"force_p95":0.98297,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":2.61546,"mean_force":0.74962,"phase_index":4.0,"phase_name":"transport_1","phase_type":"push","tcp_position_centroid":[0.31359,-0.01483,0.06662]},{"body_a":"world","body_b":"grasp_target","contact_count":3938.0,"contact_point_centroid":[0.44068,-0.021,-0.00215],"force_p95":0.13759,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.10305,"mean_force":0.13926,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.39705,-0.00218,0.1305]},{"body_a":"grasp_target","body_b":"hand","contact_count":382.0,"contact_point_centroid":[0.41187,-0.02859,0.02247],"force_p95":0.65445,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.63046,"mean_force":0.4914,"phase_index":4.0,"phase_name":"transport_1","phase_type":"push","tcp_position_centroid":[0.30901,-0.01847,0.05054]},{"body_a":"grasp_target","body_b":"link6","contact_count":170.0,"contact_point_centroid":[0.4466,-0.01866,0.02183],"force_p95":0.86005,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.49331,"mean_force":0.38029,"phase_index":4.0,"phase_name":"transport_1","phase_type":"push","tcp_position_centroid":[0.2948,-0.00334,0.08285]},{"body_a":"world","body_b":"grasp_target","contact_count":3544.0,"contact_point_centroid":[0.42363,-0.00719,-0.0041],"force_p95":0.52782,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.19356,"mean_force":0.28099,"phase_index":4.0,"phase_name":"transport_1","phase_type":"push","tcp_position_centroid":[0.36348,0.01641,0.13753]},{"body_a":"world","body_b":"grasp_target","contact_count":4.0,"contact_point_centroid":[0.43581,-0.02112,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.38998,-0.00905,0.14345]}],"total_contact_groups":24},"final_pose_error":0.01533,"key_states":{"actual_goal_position":[0.63142,0.15919,0.19002],"final_object_position":[0.42088,0.01355,0.01602],"final_tcp_position":[0.59091,0.07911,0.43664],"realised_goal_position":[0.63142,0.15919,0.19002],"realised_object_initial_position":[0.47616,-0.02015,0.03]},"peak_contact_force":273004.12068,"phases":[{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.43581,-0.02112,0.01602],"object_pos_start":[0.47616,-0.02015,0.03],"object_to_goal_dist_end":0.31788,"object_to_goal_dist_start":0.28614,"object_z_max":0.03,"peak_contact_force":211.81193,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4911.0,"raw_peak_contact_force":1362.52177,"subtask_id":"approach_1","tcp_end":[0.38998,-0.00905,0.14345],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.13596,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.43581,-0.02112,0.01602],"object_pos_start":[0.43581,-0.02112,0.01602],"object_to_goal_dist_end":0.31788,"object_to_goal_dist_start":0.31788,"object_z_max":0.01602,"peak_contact_force":872.50007,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":5.0,"raw_peak_contact_force":305.7734,"subtask_id":"descend_1","tcp_end":[0.38996,-0.00895,0.14351],"tcp_start":[0.38998,-0.00905,0.14345],"tcp_to_object_dist_end":0.13603,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":150.0,"n_steps_budget":50.0,"object_pos_end":[0.43581,-0.02112,0.01602],"object_pos_start":[0.43581,-0.02112,0.01602],"object_to_goal_dist_end":0.31788,"object_to_goal_dist_start":0.31788,"object_z_max":0.01602,"peak_contact_force":85.47308,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":3500.0,"raw_peak_contact_force":333.05935,"subtask_id":"grasp_1","tcp_end":[0.39042,-0.00879,0.1431],"tcp_start":[0.39042,-0.00878,0.1431],"tcp_to_object_dist_end":0.1355,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":513.0,"n_steps_budget":600.0,"object_pos_end":[0.43581,-0.02112,0.01602],"object_pos_start":[0.43581,-0.02112,0.01602],"object_to_goal_dist_end":0.31788,"object_to_goal_dist_start":0.31788,"object_z_max":0.01602,"peak_contact_force":207.67977,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":4724.0,"raw_peak_contact_force":281.35332,"tcp_end":[0.36455,-0.01607,0.1158],"tcp_start":[0.39042,-0.00879,0.1431],"tcp_to_object_dist_end":0.12271,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":961.0,"n_steps_budget":990.0,"object_pos_end":[0.42088,0.01355,0.01602],"object_pos_start":[0.43581,-0.02112,0.01602],"object_to_goal_dist_end":0.30954,"object_to_goal_dist_start":0.31788,"object_z_max":0.03009,"peak_contact_force":0.12263,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":9271.0,"raw_peak_contact_force":1740.93766,"subtask_id":"transport_arc","tcp_end":[0.58175,0.06513,0.28455],"tcp_start":[0.36455,-0.01607,0.1158],"tcp_to_object_dist_end":0.31725,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.42088,0.01355,0.01602],"object_pos_start":[0.42088,0.01355,0.01602],"object_to_goal_dist_end":0.30954,"object_to_goal_dist_start":0.30954,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1089.0,"raw_peak_contact_force":131.43278,"subtask_id":"release_1","tcp_end":[0.59028,0.07769,0.3142],"tcp_start":[0.58175,0.06513,0.28455],"tcp_to_object_dist_end":0.34888,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":528.0,"n_steps_budget":600.0,"object_pos_end":[0.42088,0.01355,0.01602],"object_pos_start":[0.42088,0.01355,0.01602],"object_to_goal_dist_end":0.30954,"object_to_goal_dist_start":0.30954,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2112.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.59091,0.07911,0.43664],"tcp_start":[0.59028,0.07769,0.3142],"tcp_to_object_dist_end":0.4584,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":5.0,"average_failure_rate":0.06173,"average_mean_iterations":19.62963,"average_solve_count":81.0,"average_success_count":76.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.19579,"approach_1.arc_height":0.22211,"approach_1.speed":0.18485,"descend_1.contact_force":2.62454,"descend_1.grasp_z_offset":0.02687,"descend_1.speed":0.25009,"grasp_1.grasp_force":0.82207,"lift_1.lift_height":0.08175,"lift_1.lift_speed":0.12595,"release_1.release_time":0.30078,"retract_1.retract_height":0.14606,"retract_1.retract_speed":0.29219,"transport_1.arc_height":0.15204,"transport_1.transport_speed":0.39239},"optimized_scores":{"best_composite_score":-0.53379,"best_fitness_score":0.17335,"best_task_score":0.11393},"replay_outcomes":[{"contacts":{"omitted_contact_groups":8,"reported_contact_groups":[{"body_a":"world","body_b":"link6","contact_count":886.0,"contact_point_centroid":[0.62143,-0.01111,-0.00047],"force_p95":211.88579,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1549.65716,"mean_force":213.40134,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.3708,-0.01071,0.10455]},{"body_a":"world","body_b":"link6","contact_count":425.0,"contact_point_centroid":[0.58089,-0.00063,-0.00015],"force_p95":362.12498,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":792.10254,"mean_force":262.3586,"phase_index":4.0,"phase_name":"transport_1","phase_type":"push","tcp_position_centroid":[0.35121,-0.0119,0.10323]},{"body_a":"world","body_b":"link6","contact_count":187.0,"contact_point_centroid":[0.519,0.0684,-0.00048],"force_p95":359.222,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":650.70852,"mean_force":248.18886,"phase_index":6.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.38962,0.01316,0.24589]},{"body_a":"world","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.61776,-0.01835,-0.00025],"force_p95":285.05808,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":285.05808,"mean_force":285.05808,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.37401,-0.01805,0.12268]},{"body_a":"world","body_b":"link6","contact_count":513.0,"contact_point_centroid":[0.61455,-0.02161,-0.00026],"force_p95":206.52338,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":266.76214,"mean_force":204.07343,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.36341,-0.02335,0.1066]},{"body_a":"world","body_b":"link6","contact_count":550.0,"contact_point_centroid":[0.61841,-0.0185,-0.00013],"force_p95":88.69033,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":214.59037,"mean_force":73.23371,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.3744,-0.01818,0.12242]},{"body_a":"world","body_b":"link6","contact_count":70.0,"contact_point_centroid":[0.61988,0.06408,-0.00016],"force_p95":190.38651,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":202.10916,"mean_force":116.01081,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.44622,0.05067,0.22407]},{"body_a":"world","body_b":"link7","contact_count":5.0,"contact_point_centroid":[0.4939,-0.02184,-2e-05],"force_p95":139.40611,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":151.20152,"mean_force":99.724,"phase_index":4.0,"phase_name":"transport_1","phase_type":"push","tcp_position_centroid":[0.33462,-0.03398,0.04482]},{"body_a":"grasp_target","body_b":"hand","contact_count":38.0,"contact_point_centroid":[0.43967,-0.02016,0.04289],"force_p95":3.53916,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":3.96449,"mean_force":1.58162,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.37293,-0.00488,0.0549]},{"body_a":"grasp_target","body_b":"hand","contact_count":244.0,"contact_point_centroid":[0.43441,-0.03177,0.03173],"force_p95":0.72367,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.99,"mean_force":0.54305,"phase_index":4.0,"phase_name":"transport_1","phase_type":"push","tcp_position_centroid":[0.33252,-0.02375,0.06644]},{"body_a":"grasp_target","body_b":"link7","contact_count":235.0,"contact_point_centroid":[0.43741,-0.01186,0.03038],"force_p95":0.78363,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.3233,"mean_force":0.50112,"phase_index":4.0,"phase_name":"transport_1","phase_type":"push","tcp_position_centroid":[0.33167,-0.02266,0.06664]},{"body_a":"world","body_b":"grasp_target","contact_count":3923.0,"contact_point_centroid":[0.42223,-0.02584,-0.00212],"force_p95":0.13756,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.2368,"mean_force":0.1374,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.3844,-0.00991,0.11581]},{"body_a":"world","body_b":"grasp_target","contact_count":1524.0,"contact_point_centroid":[0.41136,-0.02093,-0.00303],"force_p95":0.45157,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.96901,"mean_force":0.22734,"phase_index":4.0,"phase_name":"transport_1","phase_type":"push","tcp_position_centroid":[0.35525,-0.01183,0.10545]},{"body_a":"grasp_target","body_b":"link7","contact_count":19.0,"contact_point_centroid":[0.46811,-0.0095,0.01002],"force_p95":0.45087,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.46273,"mean_force":0.19626,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.362,-0.00497,0.05465]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.41404,-0.01504,-0.00199],"force_p95":0.12313,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12373,"mean_force":0.12266,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.4454,0.05015,0.23049]},{"body_a":"world","body_b":"grasp_target","contact_count":4.0,"contact_point_centroid":[0.4171,-0.02577,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.37401,-0.01805,0.12268]}],"total_contact_groups":24},"final_pose_error":0.11514,"key_states":{"actual_goal_position":[0.63013,0.20822,0.11412],"final_object_position":[0.41404,-0.01504,0.01602],"final_tcp_position":[0.37004,0.00564,0.32107],"realised_goal_position":[0.63013,0.20822,0.11412],"realised_object_initial_position":[0.45856,-0.02632,0.03]},"peak_contact_force":273002.05609,"phases":[{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.4171,-0.02577,0.01602],"object_pos_start":[0.45856,-0.02632,0.03],"object_to_goal_dist_end":0.33129,"object_to_goal_dist_start":0.30252,"object_z_max":0.03,"peak_contact_force":208.01914,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4885.0,"raw_peak_contact_force":1549.65716,"subtask_id":"approach_1","tcp_end":[0.37401,-0.01805,0.12268],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.1153,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.4171,-0.02577,0.01602],"object_pos_start":[0.4171,-0.02577,0.01602],"object_to_goal_dist_end":0.33129,"object_to_goal_dist_start":0.33129,"object_z_max":0.01602,"peak_contact_force":828.08462,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":5.0,"raw_peak_contact_force":285.05808,"subtask_id":"descend_1","tcp_end":[0.374,-0.01802,0.12274],"tcp_start":[0.37401,-0.01805,0.12268],"tcp_to_object_dist_end":0.11535,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":150.0,"n_steps_budget":50.0,"object_pos_end":[0.4171,-0.02577,0.01602],"object_pos_start":[0.4171,-0.02577,0.01602],"object_to_goal_dist_end":0.33129,"object_to_goal_dist_start":0.33129,"object_z_max":0.01602,"peak_contact_force":67.58663,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":3503.0,"raw_peak_contact_force":214.59037,"subtask_id":"grasp_1","tcp_end":[0.37451,-0.01821,0.12223],"tcp_start":[0.37451,-0.01821,0.12223],"tcp_to_object_dist_end":0.11468,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":10.0,"n_steps":513.0,"n_steps_budget":600.0,"object_pos_end":[0.4171,-0.02577,0.01602],"object_pos_start":[0.4171,-0.02577,0.01602],"object_to_goal_dist_end":0.33129,"object_to_goal_dist_start":0.33129,"object_z_max":0.01602,"peak_contact_force":273002.05609,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":4728.0,"raw_peak_contact_force":266.76214,"tcp_end":[0.35786,-0.02791,0.09954],"tcp_start":[0.37451,-0.01821,0.12223],"tcp_to_object_dist_end":0.10242,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":451.0,"n_steps_budget":630.0,"object_pos_end":[0.41403,-0.01504,0.01606],"object_pos_start":[0.4171,-0.02577,0.01602],"object_to_goal_dist_end":0.32582,"object_to_goal_dist_start":0.33129,"object_z_max":0.02625,"peak_contact_force":906.20531,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":4324.0,"raw_peak_contact_force":792.10254,"subtask_id":"transport_arc","tcp_end":[0.44673,0.05109,0.22655],"tcp_start":[0.35786,-0.02791,0.09954],"tcp_to_object_dist_end":0.22305,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.41404,-0.01504,0.01602],"object_pos_start":[0.41403,-0.01504,0.01606],"object_to_goal_dist_end":0.32582,"object_to_goal_dist_start":0.32582,"object_z_max":0.01606,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1093.0,"raw_peak_contact_force":202.10916,"subtask_id":"release_1","tcp_end":[0.4447,0.04972,0.25078],"tcp_start":[0.44673,0.05109,0.22655],"tcp_to_object_dist_end":0.24545,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":542.0,"n_steps_budget":600.0,"object_pos_end":[0.41404,-0.01504,0.01602],"object_pos_start":[0.41404,-0.01504,0.01602],"object_to_goal_dist_end":0.32582,"object_to_goal_dist_start":0.32582,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2355.0,"raw_peak_contact_force":650.70852,"tcp_end":[0.37004,0.00564,0.32107],"tcp_start":[0.4447,0.04972,0.25078],"tcp_to_object_dist_end":0.3089,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":6.48077,"average_solve_count":104.0,"average_success_count":104.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.18053,"approach_1.arc_height":0.13851,"approach_1.speed":0.3347,"descend_1.contact_force":1.57683,"descend_1.grasp_z_offset":0.02006,"descend_1.speed":0.34481,"grasp_1.grasp_force":0.4054,"lift_1.lift_height":0.0834,"lift_1.lift_speed":0.26916,"release_1.release_time":0.29739,"retract_1.retract_height":0.11066,"retract_1.retract_speed":0.05128,"transport_1.arc_height":0.14195,"transport_1.transport_speed":0.24052},"optimized_scores":{"best_composite_score":-0.51999,"best_fitness_score":0.18715,"best_task_score":0.19037},"replay_outcomes":[{"contacts":{"omitted_contact_groups":7,"reported_contact_groups":[{"body_a":"world","body_b":"link6","contact_count":852.0,"contact_point_centroid":[0.6538,0.00254,-0.00048],"force_p95":420.76341,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1687.29343,"mean_force":237.81963,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.43676,0.00041,0.16247]},{"body_a":"world","body_b":"link6","contact_count":412.0,"contact_point_centroid":[0.61034,0.02688,-0.00022],"force_p95":313.92644,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":828.61064,"mean_force":217.87725,"phase_index":4.0,"phase_name":"transport_1","phase_type":"push","tcp_position_centroid":[0.38607,0.08046,0.12413]},{"body_a":"world","body_b":"link6","contact_count":542.0,"contact_point_centroid":[0.68714,0.00368,-0.00012],"force_p95":72.40768,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":288.51678,"mean_force":70.01573,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46371,-0.00255,0.15669]},{"body_a":"world","body_b":"link6","contact_count":483.0,"contact_point_centroid":[0.65722,0.00481,-0.00036],"force_p95":214.47995,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":265.00963,"mean_force":190.98274,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.43764,0.0148,0.16098]},{"body_a":"world","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.68654,0.0042,-0.00022],"force_p95":264.0325,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":264.0325,"mean_force":264.0325,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.46376,-0.00236,0.15741]},{"body_a":"world","body_b":"link6","contact_count":79.0,"contact_point_centroid":[0.62042,0.13133,-0.00016],"force_p95":84.2898,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":204.64646,"mean_force":59.75078,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.61681,0.1696,0.29165]},{"body_a":"grasp_target","body_b":"link7","contact_count":163.0,"contact_point_centroid":[0.52803,0.00889,0.03426],"force_p95":3.35285,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":4.74864,"mean_force":0.71828,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.40377,0.00019,0.10076]},{"body_a":"grasp_target","body_b":"link6","contact_count":109.0,"contact_point_centroid":[0.54898,0.01493,0.02797],"force_p95":0.77213,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":3.89683,"mean_force":0.47727,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.39913,0.00014,0.09723]},{"body_a":"grasp_target","body_b":"hand","contact_count":84.0,"contact_point_centroid":[0.5037,0.01533,0.04631],"force_p95":2.53587,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":3.32941,"mean_force":1.02211,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.3987,0.00012,0.08034]},{"body_a":"world","body_b":"grasp_target","contact_count":3759.0,"contact_point_centroid":[0.51787,0.01181,-0.00217],"force_p95":0.22808,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.59542,"mean_force":0.14946,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.4479,0.00043,0.17159]},{"body_a":"grasp_target","body_b":"link6","contact_count":372.0,"contact_point_centroid":[0.54124,0.02568,0.02139],"force_p95":1.22756,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.55914,"mean_force":0.58183,"phase_index":4.0,"phase_name":"transport_1","phase_type":"push","tcp_position_centroid":[0.36388,0.07812,0.10992]},{"body_a":"world","body_b":"grasp_target","contact_count":2467.0,"contact_point_centroid":[0.5108,0.02656,-0.00345],"force_p95":0.53212,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.84909,"mean_force":0.2354,"phase_index":4.0,"phase_name":"transport_1","phase_type":"push","tcp_position_centroid":[0.41609,0.10051,0.15851]},{"body_a":"grasp_target","body_b":"link7","contact_count":278.0,"contact_point_centroid":[0.49018,0.019,0.03157],"force_p95":0.52159,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.77136,"mean_force":0.39372,"phase_index":4.0,"phase_name":"transport_1","phase_type":"push","tcp_position_centroid":[0.35625,0.07846,0.0929]},{"body_a":"world","body_b":"grasp_target","contact_count":4.0,"contact_point_centroid":[0.51338,0.01402,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.46376,-0.00236,0.15741]},{"body_a":"world","body_b":"grasp_target","contact_count":2200.0,"contact_point_centroid":[0.51338,0.01402,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46371,-0.00254,0.1567]},{"body_a":"world","body_b":"grasp_target","contact_count":1940.0,"contact_point_centroid":[0.51338,0.01402,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.43775,0.01474,0.16097]}],"total_contact_groups":23},"final_pose_error":0.02875,"key_states":{"actual_goal_position":[0.64762,0.15808,0.1911],"final_object_position":[0.51031,0.04673,0.01602],"final_tcp_position":[0.61737,0.1692,0.3993],"realised_goal_position":[0.64762,0.15808,0.1911],"realised_object_initial_position":[0.54431,0.00113,0.03]},"peak_contact_force":273004.12056,"phases":[{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51338,0.01402,0.01602],"object_pos_start":[0.54431,0.00113,0.03],"object_to_goal_dist_end":0.2635,"object_to_goal_dist_start":0.24751,"object_z_max":0.03,"peak_contact_force":333.96983,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4986.0,"raw_peak_contact_force":1687.29343,"subtask_id":"approach_1","tcp_end":[0.46376,-0.00236,0.15741],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.15073,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.51338,0.01402,0.01602],"object_pos_start":[0.51338,0.01402,0.01602],"object_to_goal_dist_end":0.2635,"object_to_goal_dist_start":0.2635,"object_z_max":0.01602,"peak_contact_force":502.51085,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":5.0,"raw_peak_contact_force":264.0325,"subtask_id":"descend_1","tcp_end":[0.46372,-0.00232,0.15721],"tcp_start":[0.46376,-0.00236,0.15741],"tcp_to_object_dist_end":0.15056,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":10.0,"n_steps":150.0,"n_steps_budget":50.0,"object_pos_end":[0.51338,0.01402,0.01602],"object_pos_start":[0.51338,0.01402,0.01602],"object_to_goal_dist_end":0.2635,"object_to_goal_dist_start":0.2635,"object_z_max":0.01602,"peak_contact_force":65.77618,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":3533.0,"raw_peak_contact_force":288.51678,"subtask_id":"grasp_1","tcp_end":[0.46369,-0.00259,0.15658],"tcp_start":[0.46369,-0.00259,0.15659],"tcp_to_object_dist_end":0.15001,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":485.0,"n_steps_budget":600.0,"object_pos_end":[0.51338,0.01402,0.01602],"object_pos_start":[0.51338,0.01402,0.01602],"object_to_goal_dist_end":0.2635,"object_to_goal_dist_start":0.2635,"object_z_max":0.01602,"peak_contact_force":197.32162,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":4496.0,"raw_peak_contact_force":265.00963,"tcp_end":[0.4413,0.03193,0.17645],"tcp_start":[0.46369,-0.00259,0.15658],"tcp_to_object_dist_end":0.17679,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":10.0,"n_steps":691.0,"n_steps_budget":720.0,"object_pos_end":[0.51031,0.04673,0.01602],"object_pos_start":[0.51338,0.01402,0.01602],"object_to_goal_dist_end":0.24881,"object_to_goal_dist_start":0.2635,"object_z_max":0.02186,"peak_contact_force":289.46207,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":6459.0,"raw_peak_contact_force":828.61064,"subtask_id":"transport_arc","tcp_end":[0.6154,0.17111,0.29159],"tcp_start":[0.4413,0.03193,0.17645],"tcp_to_object_dist_end":0.32008,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51031,0.04673,0.01602],"object_pos_start":[0.51031,0.04673,0.01602],"object_to_goal_dist_end":0.24881,"object_to_goal_dist_start":0.24881,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1106.0,"raw_peak_contact_force":204.64646,"subtask_id":"release_1","tcp_end":[0.61664,0.16982,0.31738],"tcp_start":[0.6154,0.17111,0.29159],"tcp_to_object_dist_end":0.34245,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51031,0.04673,0.01602],"object_pos_start":[0.51031,0.04673,0.01602],"object_to_goal_dist_end":0.24881,"object_to_goal_dist_start":0.24881,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.61737,0.1692,0.3993],"tcp_start":[0.61664,0.16982,0.31738],"tcp_to_object_dist_end":0.41638,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```