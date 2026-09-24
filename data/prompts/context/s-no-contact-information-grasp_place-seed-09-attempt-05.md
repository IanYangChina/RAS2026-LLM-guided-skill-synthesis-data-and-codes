## Search State

- **Seed**: 9
- **Iteration**: 6 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 5 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | position_control | impedance_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 7 | 0.1884 | 0.39 | ✅ accepted |
| 4 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | position_control | impedance_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 6 | -0.2037 | 0.17 | ✅ accepted |
| 3 | approach → descend → grasp → lift → approach → descend → release | joint_interpolation | joint_interpolation | — | joint_interpolation | arc_cartesian | linear_cartesian | — | position_control | position_control | position_control | impedance_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 6 | -0.3223 | 0.17 | ✅ accepted |
| 2 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | impedance_control | position_control | position_control | position_control | pose_tolerance | contact_detected | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 5 | -0.2543 | 0.14 | ✅ accepted |
| 1 | rotate → pull → push → descend → descend → grasp → approach | impedance_motion | arc_cartesian | impedance_motion | linear_cartesian | linear_cartesian | — | linear_cartesian | impedance_control | impedance_control | impedance_control | admittance_control | position_control | position_control | position_control | pose_tolerance | time_limit | time_limit | pose_tolerance | contact_detected | grasp_success | pose_tolerance | 6 | -0.1646 | 0.13 | ✅ accepted |

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

**Mode**: free (you define subtask targets; use `subtasks:` block in your YAML)

Define subtasks in a `subtasks:` block **before** `phases:`. Each subtask specifies an intermediate optimisation target.

**Required fields** — always include both, never omit:
- `anchor` (**required**): fixture | goal | object | world
- `target_entity` (**required**): hinge | object | tcp

Subtask anchors are separate from phase `target.anchor` vocabulary: subtasks use `world | object | goal | fixture`, while phase targets use `world | task_goal | task_object | fixture | body | site | current_tcp`.

Optional fields:
- `metric`: contact | distance | goal_progress | hinge_angle (default: distance)
- `offset`: [x, y, z] in metres relative to anchor (default: [0, 0, 0])
- `param_offset_key`: CMA-ES parameter added to offset at runtime (optional)
- `weight`: scoring weight [0.1, 1.0] (default: 1.0)

**Anchor resolution for this task** — choose anchor so the resolved position is meaningful:
| Anchor | Resolves to | Best used for |
|--------|-------------|---------------|
| `world` | absolute world-frame coordinate | fixed reference points not tied to objects |
| `object` | offset from object initial position (0.5370249203970084, -0.021318279091244466, 0.03) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.6103148150051562, 0.2277534082920179, 0.2074111944405348) | final destination targets |
| `fixture` | offset from fixture pose (if defined, else world) | targets near fixture |

Annotate each phase with `subtask_id: <id>` to bind it to a subtask.
Only the **last phase** bound to a given subtask contributes to subtask scoring.

Example (two subtasks — one near object start, one at goal):
```yaml
subtasks:
  - id: reach_pre_contact
    anchor: object         # resolved to object initial position (see table above)
    target_entity: tcp     # score TCP distance to this target
    metric: distance
    offset: [0.0, 0.0, 0.10]  # 10 cm above object start position
    weight: 0.3
  - id: reach_goal
    anchor: goal           # resolved to task goal position (see table above)
    target_entity: tcp
    metric: distance
    offset: [0.0, 0.0, 0.0]
    weight: 0.7
phases:
  - id: approach_1
    type: approach
    subtask_id: reach_pre_contact
    ...
  - id: push_1
    type: push
    subtask_id: reach_goal
    ...
```

## Current Skill (Q=0.188) — your mutation base

```yaml
skill: grasp_place
dsl_version: 2
skill_type: arm_gripper
subtasks:
- id: approach_object
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.1
  weight: 0.2
- id: descend_to_grasp
  anchor: object
  weight: 0.2
- id: lift_object
  anchor: object
  target_entity: object
  offset:
  - 0.0
  - 0.0
  - 0.15
  weight: 0.3
- id: transport_to_goal
  target_entity: object
  metric: goal_progress
  weight: 0.3
phases:
- id: approach_to_object
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
    tolerance: 0.02
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - -1.0
      align_with: world_z
      tolerance: 0.1
  parameters:
    approach_speed:
      type: scalar
      range:
      - 0.05
      - 0.25
      default: 0.12
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: approach_object
- id: descend_to_grasp
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
    - 0.0
    tolerance: 0.015
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - -1.0
      align_with: world_z
      tolerance: 0.1
  parameters:
    descend_lateral_x:
      type: scalar
      range:
      - 0.0
      - 0.05
      default: 0.025
      binds_to:
      - path: target.offset.x
        mode: add
    descend_speed:
      type: scalar
      range:
      - 0.02
      - 0.15
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: descend_to_grasp
- id: grasp_object
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
    orientation:
      mode: none
  guards:
  - id: grasp_check
    when: after_phase
    predicate: bilateral_grasp
    threshold: 1.0
    on_failure: retry
  retries:
    max_attempts: 3
    strategy: repeat
- id: lift_object
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
    - 0.15
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    lift_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
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
    max_attempts: 2
    strategy: repeat
  subtask_id: lift_object
- id: transport_to_goal
  type: approach
  generator: arc_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    entity: place_target
    offset:
    - 0.0
    - 0.0
    - 0.15
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    arc_height:
      type: scalar
      range:
      - 0.05
      - 0.25
      default: 0.12
      binds_to:
      - path: generator.arc_height
        mode: replace
    transport_speed:
      type: scalar
      range:
      - 0.02
      - 0.2
      default: 0.1
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: transport_to_goal
- id: descend_to_place
  type: descend
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    entity: place_target
    offset:
    - 0.0
    - 0.0
    - 0.0
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    place_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.03
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
    orientation:
      mode: none

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_to_object** (`approach`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.1], tolerance=0.02
  - orientation: mode=align_axis, axis=[0.0, 0.0, -1.0], align_with=world_z, tolerance=0.1
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (replace)
- **descend_to_grasp** (`descend`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.0], tolerance=0.015
  - orientation: mode=align_axis, axis=[0.0, 0.0, -1.0], align_with=world_z, tolerance=0.1
  - parameter_bindings:
    - descend_lateral_x: status=consumed; consumers=target.offset.x (add)
    - descend_speed: status=consumed; consumers=generator.speed (replace)
- **grasp_object** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - orientation: mode=none
  - parameter_bindings: none
  - guards:
    - id=grasp_check, when=after_phase, predicate=bilateral_grasp, on_failure=retry, threshold=1.0
  - retries: max_attempts=3, strategy=repeat
- **lift_object** (`lift`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.15], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - lift_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=lift_check, when=after_phase, predicate=object_lifted, on_failure=retry, threshold=0.05
  - retries: max_attempts=2, strategy=repeat
- **transport_to_goal** (`approach`)
  - target: source=yaml, anchor=task_goal, entity=place_target, offset=[0.0, 0.0, 0.15], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - arc_height: status=consumed; consumers=generator.arc_height (replace)
    - transport_speed: status=consumed; consumers=generator.speed (replace)
- **descend_to_place** (`descend`)
  - target: source=yaml, anchor=task_goal, entity=place_target, offset=[0.0, 0.0, 0.0], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - place_speed: status=consumed; consumers=generator.speed (replace)
- **release_object** (`release`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - orientation: mode=none
  - parameter_bindings: none

## Design Metrics

- **Composite score**: 0.188
- **task_score** (E): 0.391
- **fitness_score**: 0.688  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Complexity Penalty**: 0.500

## Per-Phase Performance

| Phase | Normal Term. Rate | Mean Displacement (m) |
| ------- | ------------------- | ------------------------ |
| approach_to_object | 1.00 | 0.1575 |
| descend_to_grasp | 1.00 | 0.1110 |
| grasp_object | 1.00 | 0.0130 |
| lift_object | 1.00 | 0.1277 |
| transport_to_goal | 0.67 | 0.2516 |
| descend_to_place | 1.00 | 0.1481 |
| release_object | 1.00 | 0.0198 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end |
| --- | --- | --- | --- | --- | --- |
| approach_to_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.510, -0.015, 0.148) | (0.515, -0.017, 0.030)→(0.515, -0.017, 0.026) | 0.268→0.270 |
| descend_to_grasp | descend | 1.00 / step_budget | (0.510, -0.015, 0.148)→(0.525, -0.016, 0.038) | (0.515, -0.017, 0.026)→(0.515, -0.017, 0.026) | 0.270→0.270 |
| grasp_object | grasp | 1.00 / step_budget | (0.525, -0.016, 0.038)→(0.517, -0.016, 0.029) | (0.515, -0.017, 0.026)→(0.515, -0.016, 0.026) | 0.270→0.270 |
| lift_object | lift | 1.00 / step_budget | (0.517, -0.016, 0.029)→(0.511, -0.016, 0.156) | (0.515, -0.016, 0.026)→(0.509, -0.016, 0.152) | 0.270→0.233 |
| transport_to_goal | approach | 0.67 / step_budget | (0.511, -0.016, 0.156)→(0.599, 0.139, 0.325) | (0.509, -0.016, 0.152)→(0.609, 0.139, 0.312) | 0.233→0.153 |
| descend_to_place | descend | 1.00 / step_budget | (0.599, 0.139, 0.325)→(0.612, 0.175, 0.185) | (0.609, 0.139, 0.312)→(0.615, 0.175, 0.169) | 0.153→0.009 |
| release_object | release | 1.00 / step_budget | (0.612, 0.175, 0.185)→(0.606, 0.173, 0.204) | (0.615, 0.175, 0.169)→(0.602, 0.173, 0.025) | 0.009→0.146 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.524
- phase_score: 0.581
- phase_breakdown.transport_to_goal_score: 0.346
- phase_breakdown.approach_object_score: 0.672
- phase_breakdown.lift_object_score: 0.619
- phase_breakdown.descend_to_grasp_score: 0.785
- grasp_place_fitness: 0.752

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.752
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.524
- **Median Q (composite search score)**: 0.177
- **K-run variance**: 0.0023
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.275


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.75194,"average_solve_count":258.0,"average_success_count":258.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_to_object.approach_speed":0.12483,"descend_to_grasp.descend_lateral_x":0.02248,"descend_to_grasp.descend_speed":0.09023,"descend_to_place.place_speed":0.07798,"lift_object.lift_speed":0.05882,"transport_to_goal.arc_height":0.11145,"transport_to_goal.transport_speed":0.03961},"optimized_scores":{"best_composite_score":0.13563,"best_fitness_score":0.63563,"best_task_score":0.28702},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":186.0,"contact_point_centroid":[0.59082,0.21416,-0.008],"force_p95":1.30762,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.9244,"mean_force":0.40788,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.59861,0.21241,0.23153]},{"body_a":"world","body_b":"grasp_target","contact_count":100.0,"contact_point_centroid":[0.53302,-0.02054,-0.00151],"force_p95":0.67997,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.79389,"mean_force":0.17852,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.54008,-0.02063,0.02849]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":9380.0,"contact_point_centroid":[0.53556,-0.03973,0.09232],"force_p95":0.07078,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.34038,"mean_force":0.05085,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.53545,-0.02058,0.09044]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":9380.0,"contact_point_centroid":[0.53553,-0.00144,0.09235],"force_p95":0.07138,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32985,"mean_force":0.05059,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.53545,-0.02058,0.09044]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1236.0,"contact_point_centroid":[0.60185,0.23319,0.21656],"force_p95":0.07641,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19864,"mean_force":0.04513,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.60171,0.21398,0.21485]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1219.0,"contact_point_centroid":[0.60194,0.19479,0.21695],"force_p95":0.0723,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19396,"mean_force":0.04399,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.60172,0.21399,0.21489]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53698,-0.02117,-0.00207],"force_p95":0.1413,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.18398,"mean_force":0.12867,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.54278,-0.02067,0.02843]},{"body_a":"world","body_b":"grasp_target","contact_count":1188.0,"contact_point_centroid":[0.53702,-0.02132,-0.00189],"force_p95":0.13631,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12304,"phase_index":0.0,"phase_name":"approach_to_object","phase_type":"approach","tcp_position_centroid":[0.51327,-0.00885,0.22454]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6726.0,"contact_point_centroid":[0.59067,0.18922,0.29817],"force_p95":0.07398,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13786,"mean_force":0.05147,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.59054,0.17012,0.29637]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6740.0,"contact_point_centroid":[0.59068,0.15086,0.29852],"force_p95":0.07472,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13094,"mean_force":0.05138,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.59052,0.17004,0.29652]},{"body_a":"world","body_b":"grasp_target","contact_count":1104.0,"contact_point_centroid":[0.53702,-0.02132,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.538,-0.0195,0.09194]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4810.0,"contact_point_centroid":[0.54161,-0.00146,0.02889],"force_p95":0.06995,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10841,"mean_force":0.04476,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.54155,-0.02065,0.02697]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":20000.0,"contact_point_centroid":[0.5434,0.03761,0.28654],"force_p95":0.07098,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09648,"mean_force":0.04922,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.54328,0.01848,0.28463]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":20000.0,"contact_point_centroid":[0.54342,-0.00066,0.28652],"force_p95":0.07215,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09321,"mean_force":0.04948,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.54328,0.01848,0.28463]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4924.0,"contact_point_centroid":[0.54163,-0.03987,0.02887],"force_p95":0.07026,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08776,"mean_force":0.04485,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.54155,-0.02065,0.02698]}],"total_contact_groups":15},"final_pose_error":0.01958,"key_states":{"actual_goal_position":[0.61031,0.22775,0.20741],"final_object_position":[0.59814,0.21157,0.02128],"final_tcp_position":[0.60367,0.21409,0.21976],"realised_goal_position":[0.61031,0.22775,0.20741],"realised_object_initial_position":[0.53702,-0.02132,0.03]},"phases":[{"n_steps":298.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.03],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31446,"object_z_max":0.03,"phase_name":"approach_to_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"approach_object","tcp_end":[0.52867,-0.01828,0.1476],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.1219,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":276.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"descend_to_grasp","tcp_end":[0.5504,-0.02079,0.03756],"tcp_start":[0.52867,-0.01828,0.1476],"tcp_to_object_dist_end":0.01767,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53687,-0.02069,0.02571],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31644,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","tcp_end":[0.54152,-0.02065,0.02693],"tcp_start":[0.5504,-0.02079,0.03756],"tcp_to_object_dist_end":0.00481,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":469.0,"n_steps_budget":1000.0,"object_pos_end":[0.52957,-0.02061,0.1526],"object_pos_start":[0.53687,-0.02069,0.02571],"object_to_goal_dist_end":0.26685,"object_to_goal_dist_start":0.31644,"object_z_max":0.15233,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","subtask_id":"lift_object","tcp_end":[0.5335,-0.02059,0.15607],"tcp_start":[0.54152,-0.02065,0.02693],"tcp_to_object_dist_end":0.00525,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.58915,0.12891,0.36512],"object_pos_start":[0.52957,-0.02061,0.1526],"object_to_goal_dist_end":0.18732,"object_to_goal_dist_start":0.26685,"object_z_max":0.3651,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"transport_to_goal","tcp_end":[0.57879,0.12901,0.37317],"tcp_start":[0.5335,-0.02059,0.15607],"tcp_to_object_dist_end":0.01313,"terminated_normally":false,"termination_reason":"step_budget"},{"n_steps":337.0,"n_steps_budget":1000.0,"object_pos_end":[0.6085,0.21387,0.20953],"object_pos_start":[0.58915,0.12891,0.36512],"object_to_goal_dist_end":0.01416,"object_to_goal_dist_start":0.18732,"object_z_max":0.36512,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","tcp_end":[0.60367,0.21409,0.21976],"tcp_start":[0.57879,0.12901,0.37317],"tcp_to_object_dist_end":0.01132,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.59814,0.21157,0.02128],"object_pos_start":[0.6085,0.21387,0.20953],"object_to_goal_dist_end":0.18723,"object_to_goal_dist_start":0.01416,"object_z_max":0.20953,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","tcp_end":[0.59858,0.2124,0.23867],"tcp_start":[0.60367,0.21409,0.21976],"tcp_to_object_dist_end":0.21739,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.29123,"average_solve_count":285.0,"average_success_count":285.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_to_object.approach_speed":0.09511,"descend_to_grasp.descend_lateral_x":0.01899,"descend_to_grasp.descend_speed":0.05102,"descend_to_place.place_speed":0.08116,"lift_object.lift_speed":0.02419,"transport_to_goal.arc_height":0.21249,"transport_to_goal.transport_speed":0.15029},"optimized_scores":{"best_composite_score":0.17726,"best_fitness_score":0.67726,"best_task_score":0.36116},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":229.0,"contact_point_centroid":[0.61663,0.16214,-0.00665],"force_p95":0.96409,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.53311,"mean_force":0.3123,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.62241,0.15908,0.20522]},{"body_a":"world","body_b":"grasp_target","contact_count":128.0,"contact_point_centroid":[0.54096,-0.02806,-0.00172],"force_p95":0.5088,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.58886,"mean_force":0.21474,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.54516,-0.02818,0.02826]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":10100.0,"contact_point_centroid":[0.54221,-0.04727,0.09161],"force_p95":0.07193,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25866,"mean_force":0.05087,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.54211,-0.02812,0.08973]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":10100.0,"contact_point_centroid":[0.54219,-0.00898,0.09166],"force_p95":0.07216,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24249,"mean_force":0.05038,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.54211,-0.02812,0.08973]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4386.0,"contact_point_centroid":[0.62563,0.17266,0.26695],"force_p95":0.0888,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21538,"mean_force":0.05712,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.6253,0.15356,0.26496]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":17449.0,"contact_point_centroid":[0.56457,0.04363,0.27658],"force_p95":0.0729,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21487,"mean_force":0.0493,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.56457,0.02455,0.2746]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.54556,-0.02903,-0.00211],"force_p95":0.15078,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.21287,"mean_force":0.1314,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.54795,-0.02826,0.02867]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":16426.0,"contact_point_centroid":[0.56469,0.00556,0.275],"force_p95":0.07732,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20853,"mean_force":0.0522,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.56465,0.02473,0.2729]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4530.0,"contact_point_centroid":[0.62529,0.13462,0.26465],"force_p95":0.08635,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19437,"mean_force":0.05487,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.6254,0.15381,0.26252]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1221.0,"contact_point_centroid":[0.62615,0.14125,0.19166],"force_p95":0.07411,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15344,"mean_force":0.04413,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.62602,0.16028,0.19019]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1065.0,"contact_point_centroid":[0.62698,0.17952,0.19133],"force_p95":0.08249,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14007,"mean_force":0.05063,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.62599,0.16027,0.19012]},{"body_a":"world","body_b":"grasp_target","contact_count":1248.0,"contact_point_centroid":[0.5456,-0.02923,-0.00189],"force_p95":0.13606,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12302,"phase_index":0.0,"phase_name":"approach_to_object","phase_type":"approach","tcp_position_centroid":[0.51697,-0.01219,0.22417]},{"body_a":"world","body_b":"grasp_target","contact_count":1144.0,"contact_point_centroid":[0.5456,-0.02923,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.54433,-0.02678,0.09189]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4791.0,"contact_point_centroid":[0.54677,-0.00904,0.02911],"force_p95":0.07143,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11673,"mean_force":0.04479,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.54671,-0.02822,0.02718]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4960.0,"contact_point_centroid":[0.5468,-0.04747,0.02907],"force_p95":0.07189,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0872,"mean_force":0.04482,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.54671,-0.02822,0.02719]}],"total_contact_groups":15},"final_pose_error":0.01981,"key_states":{"actual_goal_position":[0.63284,0.16493,0.17692],"final_object_position":[0.61665,0.16054,0.02508],"final_tcp_position":[0.6282,0.16074,0.19572],"realised_goal_position":[0.63284,0.16493,0.17692],"realised_object_initial_position":[0.5456,-0.02923,0.03]},"phases":[{"n_steps":313.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.03],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.25864,"object_z_max":0.03,"phase_name":"approach_to_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"approach_object","tcp_end":[0.53632,-0.02519,0.14678],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.12118,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":286.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"descend_to_grasp","tcp_end":[0.55562,-0.02847,0.03799],"tcp_start":[0.53632,-0.02519,0.14678],"tcp_to_object_dist_end":0.01562,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54544,-0.02829,0.02557],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26053,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","tcp_end":[0.54668,-0.02822,0.02715],"tcp_start":[0.55562,-0.02847,0.03799],"tcp_to_object_dist_end":0.002,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":505.0,"n_steps_budget":1000.0,"object_pos_end":[0.53999,-0.02817,0.15283],"object_pos_start":[0.54544,-0.02829,0.02557],"object_to_goal_dist_end":0.21561,"object_to_goal_dist_start":0.26053,"object_z_max":0.15257,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","subtask_id":"lift_object","tcp_end":[0.54169,-0.02814,0.1561],"tcp_start":[0.54668,-0.02822,0.02715],"tcp_to_object_dist_end":0.00368,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":855.0,"n_steps_budget":1000.0,"object_pos_end":[0.62904,0.14768,0.30623],"object_pos_start":[0.53999,-0.02817,0.15283],"object_to_goal_dist_end":0.13051,"object_to_goal_dist_start":0.21561,"object_z_max":0.31997,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"transport_to_goal","tcp_end":[0.62374,0.14757,0.32539],"tcp_start":[0.54169,-0.02814,0.1561],"tcp_to_object_dist_end":0.01988,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":224.0,"n_steps_budget":1000.0,"object_pos_end":[0.62478,0.16041,0.17467],"object_pos_start":[0.62904,0.14768,0.30623],"object_to_goal_dist_end":0.00951,"object_to_goal_dist_start":0.13051,"object_z_max":0.30623,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","tcp_end":[0.6282,0.16074,0.19572],"tcp_start":[0.62374,0.14757,0.32539],"tcp_to_object_dist_end":0.02132,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.61665,0.16054,0.02508],"object_pos_start":[0.62478,0.16041,0.17467],"object_to_goal_dist_end":0.15276,"object_to_goal_dist_start":0.00951,"object_z_max":0.17467,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","tcp_end":[0.62237,0.15907,0.21386],"tcp_start":[0.6282,0.16074,0.19572],"tcp_to_object_dist_end":0.18887,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.29795,"average_solve_count":292.0,"average_success_count":292.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_to_object.approach_speed":0.142,"descend_to_grasp.descend_lateral_x":0.01288,"descend_to_grasp.descend_speed":0.08815,"descend_to_place.place_speed":0.06814,"lift_object.lift_speed":0.02015,"transport_to_goal.arc_height":0.16434,"transport_to_goal.transport_speed":0.07267},"optimized_scores":{"best_composite_score":0.25219,"best_fitness_score":0.75219,"best_task_score":0.52384},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":176.0,"contact_point_centroid":[0.59753,0.14787,-0.00705],"force_p95":1.09596,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.17045,"mean_force":0.39351,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.59725,0.14775,0.14888]},{"body_a":"world","body_b":"grasp_target","contact_count":109.0,"contact_point_centroid":[0.45891,-0.00035,-0.00156],"force_p95":0.43079,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.50371,"mean_force":0.20695,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.46136,-0.00023,0.03283]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3936.0,"contact_point_centroid":[0.6008,0.16353,0.20997],"force_p95":0.10239,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.41895,"mean_force":0.06813,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.59924,0.14455,0.20818]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4657.0,"contact_point_centroid":[0.60064,0.12579,0.2082],"force_p95":0.0974,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28428,"mean_force":0.06068,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.59932,0.14464,0.20711]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8560.0,"contact_point_centroid":[0.4593,0.01891,0.09409],"force_p95":0.07168,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24771,"mean_force":0.05108,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.45923,-0.00023,0.0922]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8560.0,"contact_point_centroid":[0.45933,-0.01938,0.0941],"force_p95":0.07091,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2406,"mean_force":0.05097,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.45923,-0.00023,0.0922]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1271.0,"contact_point_centroid":[0.60152,0.16823,0.13714],"force_p95":0.08466,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20164,"mean_force":0.04433,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.60139,0.14897,0.13552]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1294.0,"contact_point_centroid":[0.60156,0.12988,0.13727],"force_p95":0.07625,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19161,"mean_force":0.04492,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.60148,0.149,0.13569]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":15580.0,"contact_point_centroid":[0.5003,0.06202,0.25624],"force_p95":0.08536,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17183,"mean_force":0.05579,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.49959,0.04288,0.25408]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":17001.0,"contact_point_centroid":[0.50242,0.02598,0.25868],"force_p95":0.0785,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16737,"mean_force":0.05187,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.50169,0.04499,0.25693]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.46283,-0.0001,-0.00202],"force_p95":0.12939,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.14326,"mean_force":0.1249,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.46362,-0.0002,0.03292]},{"body_a":"world","body_b":"grasp_target","contact_count":1096.0,"contact_point_centroid":[0.46286,-7e-05,-0.00188],"force_p95":0.1365,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12307,"phase_index":0.0,"phase_name":"approach_to_object","phase_type":"approach","tcp_position_centroid":[0.48269,-4e-05,0.22597]},{"body_a":"world","body_b":"grasp_target","contact_count":1096.0,"contact_point_centroid":[0.46286,-7e-05,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.46662,-9e-05,0.09444]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4844.0,"contact_point_centroid":[0.46262,-0.0194,0.03377],"force_p95":0.06797,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09971,"mean_force":0.04479,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.46254,-0.00021,0.03186]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4872.0,"contact_point_centroid":[0.46259,0.01899,0.03376],"force_p95":0.06804,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08534,"mean_force":0.04477,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.46254,-0.00021,0.03187]}],"total_contact_groups":15},"final_pose_error":0.01988,"key_states":{"actual_goal_position":[0.61015,0.15287,0.12219],"final_object_position":[0.59038,0.14734,0.0274],"final_tcp_position":[0.60408,0.14958,0.14083],"realised_goal_position":[0.61015,0.15287,0.12219],"realised_object_initial_position":[0.46286,-7e-05,0.03]},"phases":[{"n_steps":275.0,"n_steps_budget":1000.0,"object_pos_end":[0.46286,-7e-05,0.02602],"object_pos_start":[0.46286,-7e-05,0.03],"object_to_goal_dist_end":0.2331,"object_to_goal_dist_start":0.23148,"object_z_max":0.03,"phase_name":"approach_to_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"approach_object","tcp_end":[0.46531,-7e-05,0.1497],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.12371,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":274.0,"n_steps_budget":1000.0,"object_pos_end":[0.46286,-7e-05,0.02602],"object_pos_start":[0.46286,-7e-05,0.02602],"object_to_goal_dist_end":0.2331,"object_to_goal_dist_start":0.2331,"object_z_max":0.02602,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"descend_to_grasp","tcp_end":[0.47022,-0.00011,0.03964],"tcp_start":[0.46531,-7e-05,0.1497],"tcp_to_object_dist_end":0.01548,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.46273,-0.0002,0.02588],"object_pos_start":[0.46286,-7e-05,0.02602],"object_to_goal_dist_end":0.23331,"object_to_goal_dist_start":0.2331,"object_z_max":0.02602,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","tcp_end":[0.46252,-0.00021,0.03184],"tcp_start":[0.47022,-0.00011,0.03964],"tcp_to_object_dist_end":0.00596,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":428.0,"n_steps_budget":1000.0,"object_pos_end":[0.45887,-0.00021,0.1492],"object_pos_start":[0.46273,-0.0002,0.02588],"object_to_goal_dist_end":0.21691,"object_to_goal_dist_start":0.23331,"object_z_max":0.14891,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","subtask_id":"lift_object","tcp_end":[0.45929,-0.00021,0.15632],"tcp_start":[0.46252,-0.00021,0.03184],"tcp_to_object_dist_end":0.00712,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":861.0,"n_steps_budget":1000.0,"object_pos_end":[0.60945,0.14012,0.26337],"object_pos_start":[0.45887,-0.00021,0.1492],"object_to_goal_dist_end":0.14176,"object_to_goal_dist_start":0.21691,"object_z_max":0.29077,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"transport_to_goal","tcp_end":[0.59593,0.13993,0.27702],"tcp_start":[0.45929,-0.00021,0.15632],"tcp_to_object_dist_end":0.01922,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":246.0,"n_steps_budget":1000.0,"object_pos_end":[0.61077,0.14948,0.12382],"object_pos_start":[0.60945,0.14012,0.26337],"object_to_goal_dist_end":0.00381,"object_to_goal_dist_start":0.14176,"object_z_max":0.26337,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","tcp_end":[0.60408,0.14958,0.14083],"tcp_start":[0.59593,0.13993,0.27702],"tcp_to_object_dist_end":0.01828,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.59038,0.14734,0.0274],"object_pos_start":[0.61077,0.14948,0.12382],"object_to_goal_dist_end":0.09699,"object_to_goal_dist_start":0.00381,"object_z_max":0.12382,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","tcp_end":[0.59714,0.14772,0.16028],"tcp_start":[0.60408,0.14958,0.14083],"tcp_to_object_dist_end":0.13306,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```