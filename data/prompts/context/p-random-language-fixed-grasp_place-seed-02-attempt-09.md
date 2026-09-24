## Search State

- **Seed**: 2
- **Iteration**: 10 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 9 | approach → descend → grasp → lift → push → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | — | linear_cartesian | position_control | position_control | position_control | impedance_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 12 | -0.5760 | 0.18 | ✅ accepted |
| 8 | approach → descend → contact → grasp → lift → push → release → retract | arc_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | — | linear_cartesian | position_control | position_control | force_threshold_switch | position_control | impedance_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 14 | -0.6090 | 0.14 | ❌ rejected |
| 7 | approach → descend → contact → grasp → lift → push → release → retract | arc_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | — | linear_cartesian | position_control | position_control | force_threshold_switch | position_control | impedance_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 14 | -0.5320 | 0.14 | ✅ accepted |
| 6 | approach → descend → grasp → lift → push → release → retract | arc_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | — | linear_cartesian | position_control | impedance_control | position_control | impedance_control | position_control | position_control | position_control | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 14 | -0.6791 | 0.13 | ✅ accepted |
| 5 | approach → descend → grasp → lift → push → release → retract | arc_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | — | linear_cartesian | position_control | admittance_control | position_control | impedance_control | position_control | position_control | position_control | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 14 | -0.5858 | 0.16 | ✅ accepted |

**Proposal policy**: task_score is 0.18 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=-0.576) — your mutation base

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

- **Composite score**: -0.576
- **task_score** (E): 0.176
- **fitness_score**: 0.174  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.750

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 0.00 | 1.00 | 0.1394 |
| descend_1 | 0.00 | 1.00 | 0.0493 |
| grasp_1 | 1.00 | 1.00 | 0.0000 |
| lift_1 | 0.00 | 1.00 | 0.1158 |
| transport_1 | 0.67 | 1.00 | 0.2407 |
| release_1 | 1.00 | 1.00 | 0.0260 |
| retract_1 | 1.00 | 1.00 | 0.0902 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 0.00 / step_budget | (0.500, -0.000, 0.301)→(0.435, -0.008, 0.179) | (0.493, -0.015, 0.030)→(0.454, -0.012, 0.016) | 0.279→0.305 | 1.00 / 5.000 | 262.916 | 1398.026 |
| descend_1 | descend | 0.00 / step_budget | (0.435, -0.008, 0.179)→(0.464, -0.028, 0.171) | (0.454, -0.012, 0.016)→(0.454, -0.012, 0.016) | 0.305→0.305 | 1.00 / 5.000 | 394.726 | 889.021 |
| grasp_1 | grasp | 1.00 / step_budget | (0.464, -0.028, 0.170)→(0.464, -0.028, 0.170) | (0.454, -0.012, 0.016)→(0.454, -0.012, 0.016) | 0.305→0.305 | 1.00 / 9.000 | 73.686 | 231.724 |
| lift_1 | lift | 0.00 / step_budget | (0.464, -0.028, 0.170)→(0.443, 0.069, 0.187) | (0.454, -0.012, 0.016)→(0.454, -0.012, 0.016) | 0.305→0.305 | 1.00 / 9.000 | 91132.318 | 330.975 |
| transport_1 | push | 0.67 / step_budget | (0.443, 0.069, 0.187)→(0.622, 0.178, 0.293) | (0.454, -0.012, 0.016)→(0.463, 0.065, 0.016) | 0.305→0.260 | 1.00 / 9.333 | 91207.613 | 959.654 |
| release_1 | release | 1.00 / step_budget | (0.622, 0.178, 0.293)→(0.622, 0.178, 0.319) | (0.463, 0.065, 0.016)→(0.462, 0.064, 0.016) | 0.260→0.261 | 1.00 / 4.000 | 0.123 | 274.275 |
| retract_1 | retract | 1.00 / step_budget | (0.622, 0.178, 0.319)→(0.623, 0.177, 0.409) | (0.462, 0.064, 0.016)→(0.462, 0.064, 0.016) | 0.261→0.261 | 1.00 / 4.000 | 0.123 | 0.123 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 0.000
- place_accuracy: 0.000
- lift_clearance: 0.000
- transport_retention: None
- terminal_score: 0.186
- phase_score: 0.239
- phase_breakdown.grasp_1_score: 1.000
- phase_breakdown.transport_arc_score: 0.125
- phase_breakdown.descend_1_score: 0.085
- phase_breakdown.approach_1_score: 0.025
- phase_breakdown.release_1_score: 0.074
- grasp_place_fitness: 0.180

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.180
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.186
- **Median Q (composite search score)**: -0.574
- **K-run variance**: 0.0000
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.264


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":7.07143,"average_solve_count":98.0,"average_success_count":98.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.10217,"approach_1.speed":0.20084,"descend_1.grasp_z_offset":0.02209,"descend_1.speed":0.35755,"grasp_1.grasp_force":0.60778,"lift_1.lift_height":0.09876,"lift_1.lift_speed":0.18031,"release_1.release_time":0.31279,"retract_1.retract_height":0.09008,"retract_1.retract_speed":0.2872,"transport_1.arc_height":0.13488,"transport_1.transport_speed":0.37928},"optimized_scores":{"best_composite_score":-0.56979,"best_fitness_score":0.18021,"best_task_score":0.18568},"replay_outcomes":[{"contacts":{"omitted_contact_groups":6,"reported_contact_groups":[{"body_a":"world","body_b":"link6","contact_count":887.0,"contact_point_centroid":[0.63562,-0.00618,-0.00043],"force_p95":257.17797,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1329.42905,"mean_force":206.77944,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.41147,-0.0069,0.14839]},{"body_a":"world","body_b":"link7","contact_count":23.0,"contact_point_centroid":[0.52811,0.00054,-0.00331],"force_p95":282.33337,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1316.82571,"mean_force":70.89258,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.37727,-0.0026,0.04745]},{"body_a":"world","body_b":"link6","contact_count":975.0,"contact_point_centroid":[0.61608,-0.01607,-0.00021],"force_p95":550.42258,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":928.68316,"mean_force":330.45164,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.43472,-0.02066,0.21075]},{"body_a":"world","body_b":"link6","contact_count":321.0,"contact_point_centroid":[0.51347,-0.0357,-0.00016],"force_p95":608.3478,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":717.63587,"mean_force":357.36685,"phase_index":4.0,"phase_name":"transport_1","phase_type":"push","tcp_position_centroid":[0.50191,0.05988,0.26344]},{"body_a":"world","body_b":"link6","contact_count":434.0,"contact_point_centroid":[0.59609,-0.06238,-0.00019],"force_p95":314.49612,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":404.204,"mean_force":244.74207,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.45115,0.08133,0.1705]},{"body_a":"world","body_b":"link6","contact_count":548.0,"contact_point_centroid":[0.67732,-0.0214,-0.00013],"force_p95":73.50901,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":231.31376,"mean_force":69.93502,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46453,-0.043,0.16958]},{"body_a":"link5","body_b":"hand","contact_count":58.0,"contact_point_centroid":[0.45465,-0.05597,0.26344],"force_p95":211.66633,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":213.67294,"mean_force":173.84264,"phase_index":4.0,"phase_name":"transport_1","phase_type":"push","tcp_position_centroid":[0.49024,0.03905,0.28168]},{"body_a":"world","body_b":"link6","contact_count":79.0,"contact_point_centroid":[0.60269,0.13542,-0.00016],"force_p95":91.20371,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":140.71015,"mean_force":64.08686,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.61583,0.15576,0.29319]},{"body_a":"grasp_target","body_b":"hand","contact_count":40.0,"contact_point_centroid":[0.45524,-0.02299,0.04026],"force_p95":3.7174,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":4.08735,"mean_force":1.6314,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.38667,-0.00258,0.04986]},{"body_a":"world","body_b":"grasp_target","contact_count":1679.0,"contact_point_centroid":[0.4399,0.00988,-0.00296],"force_p95":0.528,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.8046,"mean_force":0.21635,"phase_index":4.0,"phase_name":"transport_1","phase_type":"push","tcp_position_centroid":[0.52135,0.08202,0.27042]},{"body_a":"grasp_target","body_b":"link6","contact_count":252.0,"contact_point_centroid":[0.46565,-0.01313,0.0355],"force_p95":0.97348,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.57195,"mean_force":0.36328,"phase_index":4.0,"phase_name":"transport_1","phase_type":"push","tcp_position_centroid":[0.50982,0.0441,0.28599]},{"body_a":"world","body_b":"grasp_target","contact_count":3923.0,"contact_point_centroid":[0.4405,-0.02108,-0.00213],"force_p95":0.13762,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.41927,"mean_force":0.13864,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.42158,-0.00635,0.1557]},{"body_a":"grasp_target","body_b":"link7","contact_count":24.0,"contact_point_centroid":[0.48437,-0.0068,0.00911],"force_p95":0.47346,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.53824,"mean_force":0.22922,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.37704,-0.00261,0.04932]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.46001,0.09494,-0.00199],"force_p95":0.12562,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12928,"mean_force":0.12213,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.61588,0.15562,0.29944]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.4355,-0.02122,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.43528,-0.02082,0.2104]},{"body_a":"world","body_b":"grasp_target","contact_count":2200.0,"contact_point_centroid":[0.4355,-0.02122,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46453,-0.043,0.16959]}],"total_contact_groups":22},"final_pose_error":0.01389,"key_states":{"actual_goal_position":[0.63142,0.15919,0.19002],"final_object_position":[0.46001,0.09494,0.01602],"final_tcp_position":[0.61676,0.15479,0.39558],"realised_goal_position":[0.63142,0.15919,0.19002],"realised_object_initial_position":[0.47616,-0.02015,0.03]},"peak_contact_force":1329.42905,"phases":[{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.4355,-0.02122,0.01602],"object_pos_start":[0.47616,-0.02015,0.03],"object_to_goal_dist_end":0.31813,"object_to_goal_dist_start":0.28614,"object_z_max":0.03,"peak_contact_force":252.18701,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4897.0,"raw_peak_contact_force":1329.42905,"subtask_id":"approach_1","tcp_end":[0.44935,-0.01465,0.21238],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.19696,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.4355,-0.02122,0.01602],"object_pos_start":[0.4355,-0.02122,0.01602],"object_to_goal_dist_end":0.31813,"object_to_goal_dist_start":0.31813,"object_z_max":0.01602,"peak_contact_force":400.07036,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4975.0,"raw_peak_contact_force":928.68316,"subtask_id":"descend_1","tcp_end":[0.46462,-0.04288,0.17085],"tcp_start":[0.44935,-0.01465,0.21238],"tcp_to_object_dist_end":0.15902,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":150.0,"n_steps_budget":50.0,"object_pos_end":[0.4355,-0.02122,0.01602],"object_pos_start":[0.4355,-0.02122,0.01602],"object_to_goal_dist_end":0.31813,"object_to_goal_dist_start":0.31813,"object_z_max":0.01602,"peak_contact_force":68.25793,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":3531.0,"raw_peak_contact_force":231.31376,"subtask_id":"grasp_1","tcp_end":[0.46452,-0.04304,0.16947],"tcp_start":[0.46452,-0.04303,0.16947],"tcp_to_object_dist_end":0.15769,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":463.0,"n_steps_budget":600.0,"object_pos_end":[0.4355,-0.02122,0.01602],"object_pos_start":[0.4355,-0.02122,0.01602],"object_to_goal_dist_end":0.31813,"object_to_goal_dist_start":0.31813,"object_z_max":0.01602,"peak_contact_force":223.58096,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":4257.0,"raw_peak_contact_force":404.204,"tcp_end":[0.45864,0.12113,0.1736],"tcp_start":[0.46452,-0.04304,0.16947],"tcp_to_object_dist_end":0.21361,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":571.0,"n_steps_budget":600.0,"object_pos_end":[0.46086,0.09588,0.01562],"object_pos_start":[0.4355,-0.02122,0.01602],"object_to_goal_dist_end":0.25201,"object_to_goal_dist_start":0.31813,"object_z_max":0.02429,"peak_contact_force":545.86607,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":4825.0,"raw_peak_contact_force":717.63587,"subtask_id":"transport_arc","tcp_end":[0.61594,0.15565,0.29293],"tcp_start":[0.45864,0.12113,0.1736],"tcp_to_object_dist_end":0.32329,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.46001,0.09494,0.01602],"object_pos_start":[0.46086,0.09588,0.01562],"object_to_goal_dist_end":0.25256,"object_to_goal_dist_start":0.25201,"object_z_max":0.01607,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1105.0,"raw_peak_contact_force":140.71015,"subtask_id":"release_1","tcp_end":[0.61605,0.15547,0.31935],"tcp_start":[0.61594,0.15565,0.29293],"tcp_to_object_dist_end":0.34644,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":513.0,"n_steps_budget":600.0,"object_pos_end":[0.46001,0.09494,0.01602],"object_pos_start":[0.46001,0.09494,0.01602],"object_to_goal_dist_end":0.25256,"object_to_goal_dist_start":0.25256,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2052.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.61676,0.15479,0.39558],"tcp_start":[0.61605,0.15547,0.31935],"tcp_to_object_dist_end":0.41499,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":6.9596,"average_solve_count":99.0,"average_success_count":99.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.14225,"approach_1.speed":0.0821,"descend_1.grasp_z_offset":0.00359,"descend_1.speed":0.25649,"grasp_1.grasp_force":0.52622,"lift_1.lift_height":0.08897,"lift_1.lift_speed":0.11866,"release_1.release_time":0.24896,"retract_1.retract_height":0.11864,"retract_1.retract_speed":0.39151,"transport_1.arc_height":0.11972,"transport_1.transport_speed":0.26317},"optimized_scores":{"best_composite_score":-0.58402,"best_fitness_score":0.16598,"best_task_score":0.16177},"replay_outcomes":[{"contacts":{"omitted_contact_groups":6,"reported_contact_groups":[{"body_a":"world","body_b":"link6","contact_count":886.0,"contact_point_centroid":[0.62765,-0.00546,-0.00048],"force_p95":199.56105,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1355.13114,"mean_force":202.65487,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.3849,-0.0054,0.1209]},{"body_a":"world","body_b":"link6","contact_count":303.0,"contact_point_centroid":[0.52354,0.03462,-0.00019],"force_p95":772.15685,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1002.87313,"mean_force":474.68954,"phase_index":4.0,"phase_name":"transport_1","phase_type":"push","tcp_position_centroid":[0.52429,0.08691,0.28286]},{"body_a":"world","body_b":"link6","contact_count":977.0,"contact_point_centroid":[0.62558,-0.01547,-0.0002],"force_p95":495.39346,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":925.46755,"mean_force":283.22533,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.42394,-0.01759,0.1857]},{"body_a":"world","body_b":"link7","contact_count":20.0,"contact_point_centroid":[0.52448,0.00154,-0.00327],"force_p95":26.49309,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":529.86171,"mean_force":26.49309,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.36908,-0.00263,0.05111]},{"body_a":"world","body_b":"link6","contact_count":87.0,"contact_point_centroid":[0.63442,0.20365,-0.0001],"force_p95":217.96958,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":442.34427,"mean_force":77.79155,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.63253,0.20639,0.29426]},{"body_a":"link5","body_b":"hand","contact_count":85.0,"contact_point_centroid":[0.43986,-0.06478,0.26273],"force_p95":351.38416,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":411.03502,"mean_force":232.8132,"phase_index":4.0,"phase_name":"transport_1","phase_type":"push","tcp_position_centroid":[0.47426,0.03012,0.2821]},{"body_a":"world","body_b":"link6","contact_count":443.0,"contact_point_centroid":[0.59771,-0.06959,-0.00013],"force_p95":301.75977,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":350.98982,"mean_force":227.51718,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.4507,0.07213,0.16873]},{"body_a":"world","body_b":"link6","contact_count":546.0,"contact_point_centroid":[0.67681,-0.02668,-0.00013],"force_p95":73.26817,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":289.8238,"mean_force":70.08848,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46375,-0.04559,0.16957]},{"body_a":"grasp_target","body_b":"hand","contact_count":37.0,"contact_point_centroid":[0.44057,-0.02195,0.04288],"force_p95":3.58654,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":4.00361,"mean_force":1.57192,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.37979,-0.00259,0.05267]},{"body_a":"world","body_b":"grasp_target","contact_count":1821.0,"contact_point_centroid":[0.42235,0.02232,-0.00269],"force_p95":0.44656,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.38738,"mean_force":0.18944,"phase_index":4.0,"phase_name":"transport_1","phase_type":"push","tcp_position_centroid":[0.54073,0.11324,0.28805]},{"body_a":"world","body_b":"grasp_target","contact_count":3925.0,"contact_point_centroid":[0.42215,-0.02565,-0.00212],"force_p95":0.13759,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.26853,"mean_force":0.13745,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.3974,-0.005,0.13067]},{"body_a":"grasp_target","body_b":"link6","contact_count":205.0,"contact_point_centroid":[0.44643,-0.02218,0.03659],"force_p95":0.87912,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.17364,"mean_force":0.36263,"phase_index":4.0,"phase_name":"transport_1","phase_type":"push","tcp_position_centroid":[0.49707,0.03445,0.28724]},{"body_a":"grasp_target","body_b":"link7","contact_count":10.0,"contact_point_centroid":[0.47159,-0.00712,0.00785],"force_p95":0.39861,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.41212,"mean_force":0.24329,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.3679,-0.00263,0.04849]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.42553,0.05599,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12265,"mean_force":0.12262,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.63258,0.20641,0.30005]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.41701,-0.02554,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.42476,-0.01785,0.18591]},{"body_a":"world","body_b":"grasp_target","contact_count":2200.0,"contact_point_centroid":[0.41701,-0.02554,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46376,-0.04559,0.16958]}],"total_contact_groups":22},"final_pose_error":0.01657,"key_states":{"actual_goal_position":[0.63013,0.20822,0.11412],"final_object_position":[0.42553,0.05599,0.01602],"final_tcp_position":[0.6339,0.20593,0.42153],"realised_goal_position":[0.63013,0.20822,0.11412],"realised_object_initial_position":[0.45856,-0.02632,0.03]},"peak_contact_force":273076.84982,"phases":[{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.41701,-0.02554,0.01602],"object_pos_start":[0.45856,-0.02632,0.03],"object_to_goal_dist_end":0.33119,"object_to_goal_dist_start":0.30252,"object_z_max":0.03,"peak_contact_force":196.92211,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4878.0,"raw_peak_contact_force":1355.13114,"subtask_id":"approach_1","tcp_end":[0.39066,-0.00965,0.14422],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.13184,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.41701,-0.02554,0.01602],"object_pos_start":[0.41701,-0.02554,0.01602],"object_to_goal_dist_end":0.33119,"object_to_goal_dist_start":0.33119,"object_z_max":0.01602,"peak_contact_force":397.70524,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4977.0,"raw_peak_contact_force":925.46755,"subtask_id":"descend_1","tcp_end":[0.46385,-0.04525,0.17082],"tcp_start":[0.39066,-0.00965,0.14422],"tcp_to_object_dist_end":0.16293,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":150.0,"n_steps_budget":50.0,"object_pos_end":[0.41701,-0.02554,0.01602],"object_pos_start":[0.41701,-0.02554,0.01602],"object_to_goal_dist_end":0.33119,"object_to_goal_dist_start":0.33119,"object_z_max":0.01602,"peak_contact_force":85.42452,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":3532.0,"raw_peak_contact_force":289.8238,"subtask_id":"grasp_1","tcp_end":[0.46374,-0.04562,0.16947],"tcp_start":[0.46374,-0.04561,0.16947],"tcp_to_object_dist_end":0.16166,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":484.0,"n_steps_budget":600.0,"object_pos_end":[0.41701,-0.02554,0.01602],"object_pos_start":[0.41701,-0.02554,0.01602],"object_to_goal_dist_end":0.33119,"object_to_goal_dist_start":0.33119,"object_z_max":0.01602,"peak_contact_force":272983.76594,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":4429.0,"raw_peak_contact_force":350.98982,"tcp_end":[0.44667,0.07926,0.22896],"tcp_start":[0.46374,-0.04562,0.16947],"tcp_to_object_dist_end":0.23918,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":10.0,"n_steps":571.0,"n_steps_budget":600.0,"object_pos_end":[0.42553,0.05599,0.01602],"object_pos_start":[0.41701,-0.02554,0.01602],"object_to_goal_dist_end":0.27323,"object_to_goal_dist_start":0.33119,"object_z_max":0.02124,"peak_contact_force":273076.84982,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":4875.0,"raw_peak_contact_force":1002.87313,"subtask_id":"transport_arc","tcp_end":[0.63253,0.20674,0.29361],"tcp_start":[0.44667,0.07926,0.22896],"tcp_to_object_dist_end":0.37767,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.42553,0.05599,0.01602],"object_pos_start":[0.42553,0.05599,0.01602],"object_to_goal_dist_end":0.27323,"object_to_goal_dist_start":0.27323,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1111.0,"raw_peak_contact_force":442.34427,"subtask_id":"release_1","tcp_end":[0.63276,0.2065,0.31942],"tcp_start":[0.63253,0.20674,0.29361],"tcp_to_object_dist_end":0.39705,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":542.0,"n_steps_budget":600.0,"object_pos_end":[0.42553,0.05599,0.01602],"object_pos_start":[0.42553,0.05599,0.01602],"object_to_goal_dist_end":0.27323,"object_to_goal_dist_start":0.27323,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2168.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.6339,0.20593,0.42153],"tcp_start":[0.63276,0.2065,0.31942],"tcp_to_object_dist_end":0.47994,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":16.0,"average_failure_rate":0.14545,"average_mean_iterations":35.31818,"average_solve_count":110.0,"average_success_count":94.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.09483,"approach_1.speed":0.39199,"descend_1.grasp_z_offset":0.01422,"descend_1.speed":0.19002,"grasp_1.grasp_force":0.51201,"lift_1.lift_height":0.10829,"lift_1.lift_speed":0.27161,"release_1.release_time":0.25266,"retract_1.retract_height":0.10739,"retract_1.retract_speed":0.2173,"transport_1.arc_height":0.11856,"transport_1.transport_speed":0.2081},"optimized_scores":{"best_composite_score":-0.57425,"best_fitness_score":0.17575,"best_task_score":0.18146},"replay_outcomes":[{"contacts":{"omitted_contact_groups":9,"reported_contact_groups":[{"body_a":"world","body_b":"link6","contact_count":606.0,"contact_point_centroid":[0.65407,0.00042,-0.00048],"force_p95":397.63164,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1509.51917,"mean_force":216.90928,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.42764,0.00028,0.14428]},{"body_a":"world","body_b":"link6","contact_count":641.0,"contact_point_centroid":[0.60317,0.02842,-0.00017],"force_p95":331.36523,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1158.45286,"mean_force":232.92719,"phase_index":4.0,"phase_name":"transport_1","phase_type":"push","tcp_position_centroid":[0.37969,0.02908,0.10531]},{"body_a":"world","body_b":"link6","contact_count":472.0,"contact_point_centroid":[0.65672,0.00238,-0.0002],"force_p95":484.35118,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":812.91262,"mean_force":232.64986,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.44715,0.00154,0.17427]},{"body_a":"world","body_b":"link7","contact_count":22.0,"contact_point_centroid":[0.53862,0.00384,-0.00378],"force_p95":0.0,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":395.80152,"mean_force":17.99098,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.3863,-0.00011,0.04721]},{"body_a":"world","body_b":"link6","contact_count":86.0,"contact_point_centroid":[0.61391,0.1437,-0.00014],"force_p95":76.74426,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":239.77175,"mean_force":58.68554,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.6179,0.17132,0.29288]},{"body_a":"world","body_b":"link6","contact_count":512.0,"contact_point_centroid":[0.65321,0.00677,-0.00034],"force_p95":204.98067,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":237.731,"mean_force":187.70265,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.42523,0.00538,0.14937]},{"body_a":"world","body_b":"link6","contact_count":550.0,"contact_point_centroid":[0.67726,0.00573,-0.00013],"force_p95":76.88146,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":174.03483,"mean_force":69.31029,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46474,0.00407,0.17128]},{"body_a":"world","body_b":"link7","contact_count":38.0,"contact_point_centroid":[0.51459,0.01493,-6e-05],"force_p95":84.01102,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":117.78246,"mean_force":62.29086,"phase_index":4.0,"phase_name":"transport_1","phase_type":"push","tcp_position_centroid":[0.35504,0.01026,0.04517]},{"body_a":"grasp_target","body_b":"link7","contact_count":183.0,"contact_point_centroid":[0.52656,0.00661,0.03208],"force_p95":3.39901,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":5.07902,"mean_force":0.69318,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.40169,2e-05,0.09661]},{"body_a":"grasp_target","body_b":"link6","contact_count":104.0,"contact_point_centroid":[0.54861,0.01429,0.02679],"force_p95":0.85824,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":4.63074,"mean_force":0.48996,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.39516,-2e-05,0.08761]},{"body_a":"grasp_target","body_b":"hand","contact_count":93.0,"contact_point_centroid":[0.50212,0.01617,0.04513],"force_p95":2.51856,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":3.34904,"mean_force":1.04283,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.39577,-4e-05,0.07659]},{"body_a":"world","body_b":"grasp_target","contact_count":2656.0,"contact_point_centroid":[0.51775,0.00911,-0.00229],"force_p95":0.31277,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.78688,"mean_force":0.16584,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.44268,0.0003,0.15845]},{"body_a":"grasp_target","body_b":"link7","contact_count":500.0,"contact_point_centroid":[0.51299,0.01517,0.02219],"force_p95":0.8569,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":2.21427,"mean_force":0.69378,"phase_index":4.0,"phase_name":"transport_1","phase_type":"push","tcp_position_centroid":[0.36377,0.01732,0.07863]},{"body_a":"grasp_target","body_b":"link6","contact_count":509.0,"contact_point_centroid":[0.52411,0.02447,0.01674],"force_p95":0.75492,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.57869,"mean_force":0.64362,"phase_index":4.0,"phase_name":"transport_1","phase_type":"push","tcp_position_centroid":[0.36434,0.01773,0.08025]},{"body_a":"world","body_b":"grasp_target","contact_count":3190.0,"contact_point_centroid":[0.50039,0.02378,-0.0038],"force_p95":0.48656,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.03576,"mean_force":0.26245,"phase_index":4.0,"phase_name":"transport_1","phase_type":"push","tcp_position_centroid":[0.40734,0.05616,0.13663]},{"body_a":"grasp_target","body_b":"hand","contact_count":263.0,"contact_point_centroid":[0.47009,0.00068,0.02836],"force_p95":0.32426,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.59221,"mean_force":0.19845,"phase_index":4.0,"phase_name":"transport_1","phase_type":"push","tcp_position_centroid":[0.35491,0.01247,0.05207]}],"total_contact_groups":25},"final_pose_error":0.01508,"key_states":{"actual_goal_position":[0.64762,0.15808,0.1911],"final_object_position":[0.50111,0.04224,0.01602],"final_tcp_position":[0.61869,0.17076,0.41109],"realised_goal_position":[0.64762,0.15808,0.1911],"realised_object_initial_position":[0.54431,0.00113,0.03]},"peak_contact_force":1509.51917,"phases":[{"contact_detected":true,"contact_event_count":5.0,"n_steps":722.0,"n_steps_budget":1000.0,"object_pos_end":[0.51,0.01151,0.01602],"object_pos_start":[0.54431,0.00113,0.03],"object_to_goal_dist_end":0.26661,"object_to_goal_dist_start":0.24751,"object_z_max":0.03,"peak_contact_force":339.64001,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3664.0,"raw_peak_contact_force":1509.51917,"subtask_id":"approach_1","tcp_end":[0.46433,0.00072,0.18187],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.17236,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":482.0,"n_steps_budget":1000.0,"object_pos_end":[0.51,0.01151,0.01602],"object_pos_start":[0.51,0.01151,0.01602],"object_to_goal_dist_end":0.26661,"object_to_goal_dist_start":0.26661,"object_z_max":0.01602,"peak_contact_force":386.40171,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2400.0,"raw_peak_contact_force":812.91262,"subtask_id":"descend_1","tcp_end":[0.4649,0.00404,0.17278],"tcp_start":[0.46433,0.00072,0.18187],"tcp_to_object_dist_end":0.16329,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":150.0,"n_steps_budget":50.0,"object_pos_end":[0.51,0.01151,0.01602],"object_pos_start":[0.51,0.01151,0.01602],"object_to_goal_dist_end":0.26661,"object_to_goal_dist_start":0.26661,"object_z_max":0.01602,"peak_contact_force":67.37535,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":3525.0,"raw_peak_contact_force":174.03483,"subtask_id":"grasp_1","tcp_end":[0.46474,0.00405,0.17116],"tcp_start":[0.46474,0.00405,0.17116],"tcp_to_object_dist_end":0.16178,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":513.0,"n_steps_budget":600.0,"object_pos_end":[0.51,0.01151,0.01602],"object_pos_start":[0.51,0.01151,0.01602],"object_to_goal_dist_end":0.26661,"object_to_goal_dist_start":0.26661,"object_z_max":0.01602,"peak_contact_force":189.60859,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":4725.0,"raw_peak_contact_force":237.731,"tcp_end":[0.42316,0.00778,0.15872],"tcp_start":[0.46474,0.00405,0.17116],"tcp_to_object_dist_end":0.16709,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":871.0,"n_steps_budget":900.0,"object_pos_end":[0.50111,0.04224,0.01602],"object_pos_start":[0.51,0.01151,0.01602],"object_to_goal_dist_end":0.25601,"object_to_goal_dist_start":0.26661,"object_z_max":0.02941,"peak_contact_force":0.12263,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":8780.0,"raw_peak_contact_force":1158.45286,"subtask_id":"transport_arc","tcp_end":[0.61681,0.1721,0.29289],"tcp_start":[0.42316,0.00778,0.15872],"tcp_to_object_dist_end":0.32697,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50111,0.04224,0.01602],"object_pos_start":[0.50111,0.04224,0.01602],"object_to_goal_dist_end":0.25601,"object_to_goal_dist_start":0.25601,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1114.0,"raw_peak_contact_force":239.77175,"subtask_id":"release_1","tcp_end":[0.61776,0.17149,0.31873],"tcp_start":[0.61681,0.1721,0.29289],"tcp_to_object_dist_end":0.34921,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":515.0,"n_steps_budget":600.0,"object_pos_end":[0.50111,0.04224,0.01602],"object_pos_start":[0.50111,0.04224,0.01602],"object_to_goal_dist_end":0.25601,"object_to_goal_dist_start":0.25601,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2060.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.61869,0.17076,0.41109],"tcp_start":[0.61776,0.17149,0.31873],"tcp_to_object_dist_end":0.43177,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```