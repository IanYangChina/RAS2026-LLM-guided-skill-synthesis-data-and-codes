## Search State

- **Seed**: 9
- **Iteration**: 7 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 6 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 9 | 0.0640 | 0.37 | ❌ rejected |
| 5 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 9 | 0.0646 | 0.37 | ✅ accepted |
| 4 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | impedance_control | position_control | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | force_exceeded | time_limit | 10 | 0.1125 | 0.28 | ❌ rejected |
| 3 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | impedance_control | position_control | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | force_exceeded | time_limit | 10 | 0.1531 | 0.37 | ✅ accepted |
| 2 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | impedance_control | position_control | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | force_exceeded | time_limit | 9 | 0.1515 | 0.27 | ✅ accepted |

**Proposal policy**: task_score is 0.37 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen object start: [0.6103148150051562, 0.2277534082920179, 0.2074111944405348]
- Frozen task target: [0.5, 0.0, 0.3]
- Goal object position: (0.5, 0.0, 0.3)
- place_goal_position (task success criterion — final object 3D position must be close to the realised airborne target here): (0.5, 0.0, 0.3)
- Grasp/lift components are optimiser fitness diagnostics only; canonical task_score is final object-to-realised-target proximity.
- Object initial pose: (0.6103148150051562, 0.2277534082920179, 0.2074111944405348)
- Goal tolerance: 0.02 m
- Expressivity sigma: 0.15 m
- Expressivity threshold: 0.3
- Force limit: 20.0 N
- Robot initial TCP position: (0.5370249203970084, -0.021318279091244466, 0.03)
- Robot initial gripper state: **open** (gripper starts fully open; ensure a `grasp`/`force_grasp` phase closes it before lifting)
- Phase navigation guidance: the task `phase_target_map` may provide internal predefined TCP waypoint aliases / semantic phase ids. These names are not DSL phase types and are intentionally not enumerated here to avoid confusing ids with types. Phase `id` may be semantic, but phase `type` must be exactly one of the DSL enum values listed in the prompt.
- Primary evaluation target: **final object-to-realised-airborne-3D-target proximity. Grasp/lift signals are optimiser fitness diagnostics only; they do not gate the canonical task_score.**

## Scene Entities

robot:
  model: panda_full
  tcp_site: attachment_site
  gripper: franka_hand
  tcp_initial_world: [0.5370249203970084, -0.021318279091244466, 0.03]
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
  frozen_object_starts: {'grasp_target': [0.6103148150051562, 0.2277534082920179, 0.2074111944405348]}
  frozen_targets: {'place_target': [0.5, 0.0, 0.3]}
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
| `object` | offset from object initial position (0.6103148150051562, 0.2277534082920179, 0.2074111944405348) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.5, 0.0, 0.3) | final destination targets |
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

## Current Skill (Q=0.064) — your mutation base

```yaml
skill: grasp_place
dsl_version: 2
skill_type: arm_gripper
subtasks:
- id: pre_grasp
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.1
  weight: 0.2
- id: transport_goal
  target_entity: object
  metric: goal_progress
  weight: 0.8
phases:
- id: approach_above
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
    - 0.25
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
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: pre_grasp
- id: descend_grasp
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
    - 0.0
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: pre_grasp
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
      mode: keep_current
  guards:
  - id: bilateral_check
    when: after_phase
    predicate: bilateral_grasp
    threshold: 0.0
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.0
    - 0.0
    - 0.01
  subtask_id: pre_grasp
- id: lift_clear
  type: lift
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.12
      axis: world_z
      mode: add_to_offset
      sign: positive
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    lift_clear_height:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.12
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: pre_grasp
- id: transport_to_goal
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.2
    tolerance: 0.025
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - -1.0
      align_with: world_z
      tolerance: 0.1
  parameters:
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.06
      binds_to:
      - path: generator.speed
        mode: replace
    transport_height:
      type: scalar
      range:
      - 0.1
      - 0.25
      default: 0.2
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: transport_goal
- id: descend_place
  type: descend
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.03
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    place_height:
      type: scalar
      range:
      - 0.01
      - 0.05
      default: 0.03
      binds_to:
      - path: target.offset.z
        mode: replace
    speed:
      type: scalar
      range:
      - 0.005
      - 0.03
      default: 0.01
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: transport_goal
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
      mode: keep_current
  parameters:
    max_time:
      type: scalar
      range:
      - 0.5
      - 2.0
      default: 1.0
      binds_to:
      - path: duration.max_time
        mode: replace

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_above** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.25], tolerance=0.02
  - orientation: mode=align_axis, axis=[0.0, 0.0, -1.0], align_with=world_z, tolerance=0.1
  - parameter_bindings:
    - speed: status=consumed; consumers=generator.speed (replace)
- **descend_grasp** (`descend`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.0], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - speed: status=consumed; consumers=generator.speed (replace)
- **grasp_object** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings: none
  - guards:
    - id=bilateral_check, when=after_phase, predicate=bilateral_grasp, on_failure=retry, threshold=0.0
  - retries: max_attempts=2, strategy=offset_target, offset=[0.0, 0.0, 0.01]
- **lift_clear** (`lift`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=world_z, distance=0.12, mode=add_to_offset, sign=positive}, tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - lift_clear_height: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
- **transport_to_goal** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.2], tolerance=0.025
  - orientation: mode=align_axis, axis=[0.0, 0.0, -1.0], align_with=world_z, tolerance=0.1
  - parameter_bindings:
    - speed: status=consumed; consumers=generator.speed (replace)
    - transport_height: status=consumed; consumers=target.offset.z (replace)
- **descend_place** (`descend`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.03], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - place_height: status=consumed; consumers=target.offset.z (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
- **release_object** (`release`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings:
    - max_time: status=consumed; consumers=duration.max_time (replace)

## Design Metrics

- **Composite score**: 0.064
- **task_score** (E): 0.370
- **fitness_score**: 0.664  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.600

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_above | 1.00 | 1.00 | 0.0304 |
| descend_grasp | 1.00 | 1.00 | 0.2508 |
| grasp_object | 1.00 | 1.00 | 0.0122 |
| lift_clear | 0.67 | 1.00 | 0.1012 |
| transport_to_goal | 1.00 | 1.00 | 0.2979 |
| descend_place | 1.00 | 0.33 | 0.1288 |
| release_object | 1.00 | 1.00 | 0.0203 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_above | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.510, -0.011, 0.285) | (0.515, -0.017, 0.030)→(0.515, -0.017, 0.026) | 0.268→0.270 | 1.00 / 4.000 | 0.124 | 0.138 |
| descend_grasp | descend | 1.00 / step_budget | (0.510, -0.011, 0.285)→(0.510, -0.016, 0.034) | (0.515, -0.017, 0.026)→(0.515, -0.017, 0.026) | 0.270→0.270 | 1.00 / 4.000 | 0.123 | 0.124 |
| grasp_object | grasp | 1.00 / step_budget | (0.510, -0.016, 0.034)→(0.502, -0.016, 0.025) | (0.515, -0.017, 0.026)→(0.515, -0.016, 0.026) | 0.270→0.270 | 1.00 / 42.000 | 0.136 | 0.191 |
| lift_clear | lift | 0.67 / step_budget | (0.502, -0.016, 0.025)→(0.498, -0.016, 0.126) | (0.515, -0.016, 0.026)→(0.509, -0.016, 0.117) | 0.270→0.239 | 1.00 / 37.333 | 0.031 | 0.694 |
| transport_to_goal | approach | 1.00 / step_budget | (0.498, -0.016, 0.126)→(0.610, 0.171, 0.325) | (0.509, -0.016, 0.117)→(0.619, 0.171, 0.309) | 0.239→0.141 | 1.00 / 29.000 | 76.455 | 0.155 |
| descend_place | descend | 1.00 / step_budget | (0.610, 0.171, 0.325)→(0.613, 0.179, 0.197) | (0.619, 0.171, 0.309)→(0.621, 0.182, 0.155) | 0.141→0.017 | 0.33 / 12.667 | 0.024 | 0.245 |
| release_object | release | 1.00 / step_budget | (0.613, 0.179, 0.197)→(0.608, 0.177, 0.216) | (0.621, 0.182, 0.155)→(0.620, 0.186, 0.016) | 0.017→0.154 | 1.00 / 4.000 | 0.118 | 1.866 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.493
- phase_score: 0.939
- phase_breakdown.pre_grasp_score: 0.745
- phase_breakdown.transport_goal_score: 0.988
- grasp_place_fitness: 0.729

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.729
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.493
- **Median Q (composite search score)**: 0.047
- **K-run variance**: 0.0023
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.312


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
{"anchors":[{"name":"object","value":[0.61031,0.22775,0.20741]},{"name":"goal","value":[0.53702,-0.02132,0.03]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.61031,0.22775,0.20741]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.53702,-0.02132,0.03]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.99461,"average_solve_count":371.0,"average_success_count":371.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above.speed":0.05948,"descend_grasp.speed":0.0381,"descend_place.place_height":0.02673,"descend_place.speed":0.01866,"lift_clear.lift_clear_height":0.11374,"lift_clear.speed":0.06024,"release_object.max_time":0.82092,"transport_to_goal.speed":0.07376,"transport_to_goal.transport_height":0.13511},"optimized_scores":{"best_composite_score":0.01538,"best_fitness_score":0.61538,"best_task_score":0.27597},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":600.0,"contact_point_centroid":[0.60473,0.25244,-0.00406],"force_p95":0.92964,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.27516,"mean_force":0.21937,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.60241,0.2223,0.24312]},{"body_a":"world","body_b":"grasp_target","contact_count":193.0,"contact_point_centroid":[0.53241,-0.02013,-0.00118],"force_p95":0.49568,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.71636,"mean_force":0.11251,"phase_index":3.0,"phase_name":"lift_clear","phase_type":"lift","tcp_position_centroid":[0.52087,-0.02055,0.02575]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":17352.0,"contact_point_centroid":[0.51947,-0.0014,0.07402],"force_p95":0.08642,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32699,"mean_force":0.0589,"phase_index":3.0,"phase_name":"lift_clear","phase_type":"lift","tcp_position_centroid":[0.51832,-0.02049,0.07179]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":18948.0,"contact_point_centroid":[0.51943,-0.03946,0.07367],"force_p95":0.0797,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31225,"mean_force":0.0548,"phase_index":3.0,"phase_name":"lift_clear","phase_type":"lift","tcp_position_centroid":[0.51834,-0.02049,0.07203]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2027.0,"contact_point_centroid":[0.60723,0.23583,0.28543],"force_p95":0.14995,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29791,"mean_force":0.10531,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.60408,0.21782,0.28968]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1790.0,"contact_point_centroid":[0.60708,0.19922,0.29045],"force_p95":0.15576,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28372,"mean_force":0.10136,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.60389,0.21725,0.29443]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53703,-0.02107,-0.00206],"force_p95":0.14239,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.20465,"mean_force":0.12812,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.52401,-0.02061,0.02556]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":14635.0,"contact_point_centroid":[0.56031,0.11492,0.2195],"force_p95":0.08479,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17532,"mean_force":0.05595,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.55894,0.09593,0.21929]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":14081.0,"contact_point_centroid":[0.55761,0.07066,0.21389],"force_p95":0.08811,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15585,"mean_force":0.05816,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.5566,0.08965,0.21386]},{"body_a":"world","body_b":"grasp_target","contact_count":300.0,"contact_point_centroid":[0.53702,-0.02132,-0.00158],"force_p95":0.13832,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12447,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.50886,-0.00551,0.29258]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4084.0,"contact_point_centroid":[0.52363,-0.00139,0.02694],"force_p95":0.07796,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12358,"mean_force":0.05181,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.52279,-0.02059,0.02418]},{"body_a":"world","body_b":"grasp_target","contact_count":3332.0,"contact_point_centroid":[0.53702,-0.02132,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12264,"mean_force":0.12261,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.52435,-0.0165,0.15692]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4930.0,"contact_point_centroid":[0.52364,-0.0397,0.02601],"force_p95":0.07002,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08735,"mean_force":0.04482,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.52279,-0.02059,0.02418]}],"total_contact_groups":13},"final_pose_error":0.00975,"key_states":{"actual_goal_position":[0.61031,0.22775,0.20741],"final_object_position":[0.60428,0.25264,0.016],"final_tcp_position":[0.60637,0.224,0.24222],"realised_goal_position":[0.61031,0.22775,0.20741],"realised_object_initial_position":[0.53702,-0.02132,0.03]},"peak_contact_force":229.18019,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":76.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02594],"object_pos_start":[0.53702,-0.02132,0.03],"object_to_goal_dist_end":0.31677,"object_to_goal_dist_start":0.31446,"object_z_max":0.03,"peak_contact_force":0.12235,"phase_name":"approach_above","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":300.0,"raw_peak_contact_force":0.13845,"subtask_id":"pre_grasp","tcp_end":[0.51984,-0.01228,0.28402],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.25881,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":833.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.02594],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31677,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3332.0,"raw_peak_contact_force":0.12264,"subtask_id":"pre_grasp","tcp_end":[0.53128,-0.02074,0.03387],"tcp_start":[0.51984,-0.01228,0.28402],"tcp_to_object_dist_end":0.00975,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53688,-0.02048,0.02578],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31624,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.13785,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10814.0,"raw_peak_contact_force":0.20465,"subtask_id":"pre_grasp","tcp_end":[0.52276,-0.02059,0.02414],"tcp_start":[0.53128,-0.02074,0.03387],"tcp_to_object_dist_end":0.01421,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":36.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53065,-0.02018,0.11239],"object_pos_start":[0.53688,-0.02048,0.02578],"object_to_goal_dist_end":0.27721,"object_to_goal_dist_start":0.31624,"object_z_max":0.11227,"peak_contact_force":0.09392,"phase_name":"lift_clear","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":36493.0,"raw_peak_contact_force":0.71636,"subtask_id":"pre_grasp","tcp_end":[0.51838,-0.02048,0.12219],"tcp_start":[0.52276,-0.02059,0.02414],"tcp_to_object_dist_end":0.01571,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":22.0,"n_steps":817.0,"n_steps_budget":1000.0,"object_pos_end":[0.61742,0.21485,0.30588],"object_pos_start":[0.53065,-0.02018,0.11239],"object_to_goal_dist_end":0.09957,"object_to_goal_dist_start":0.27721,"object_z_max":0.30568,"peak_contact_force":229.18019,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":28716.0,"raw_peak_contact_force":0.17532,"subtask_id":"transport_goal","tcp_end":[0.60379,0.2143,0.32263],"tcp_start":[0.51838,-0.02048,0.12219],"tcp_to_object_dist_end":0.0216,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":244.0,"n_steps_budget":1000.0,"object_pos_end":[0.61546,0.23652,0.16983],"object_pos_start":[0.61742,0.21485,0.30588],"object_to_goal_dist_end":0.03893,"object_to_goal_dist_start":0.09957,"object_z_max":0.30604,"peak_contact_force":0.0,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3817.0,"raw_peak_contact_force":0.29791,"subtask_id":"transport_goal","tcp_end":[0.60637,0.224,0.24222],"tcp_start":[0.60379,0.2143,0.32263],"tcp_to_object_dist_end":0.07403,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.60428,0.25264,0.016],"object_pos_start":[0.61546,0.23652,0.16983],"object_to_goal_dist_end":0.19312,"object_to_goal_dist_start":0.03893,"object_z_max":0.16983,"peak_contact_force":0.12281,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":600.0,"raw_peak_contact_force":2.27516,"tcp_end":[0.60197,0.22208,0.26138],"tcp_start":[0.60637,0.224,0.24222],"tcp_to_object_dist_end":0.24729,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `1e57d18e69439f9d4839513252d085a45363faa5c1c2b52093c9c8149b88bb68`; realized-scene SHA-256: `9bdc6de22965641ffcaccb8421100561fe91fb98e16735236cc25272572d8879`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.63284,0.16493,0.17692]},{"name":"goal","value":[0.5456,-0.02923,0.03]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.63284,0.16493,0.17692]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.5456,-0.02923,0.03]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.78191,"average_solve_count":376.0,"average_success_count":376.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above.speed":0.05123,"descend_grasp.speed":0.06008,"descend_place.place_height":0.02147,"descend_place.speed":0.02,"lift_clear.lift_clear_height":0.12683,"lift_clear.speed":0.06209,"release_object.max_time":0.97768,"transport_to_goal.speed":0.05807,"transport_to_goal.transport_height":0.16267},"optimized_scores":{"best_composite_score":0.0475,"best_fitness_score":0.6475,"best_task_score":0.34079},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":551.0,"contact_point_centroid":[0.64299,0.15644,-0.00411],"force_p95":0.83278,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.91601,"mean_force":0.21028,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.62352,0.16082,0.20818]},{"body_a":"world","body_b":"grasp_target","contact_count":193.0,"contact_point_centroid":[0.54129,-0.02771,-0.0012],"force_p95":0.48944,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.72766,"mean_force":0.11117,"phase_index":3.0,"phase_name":"lift_clear","phase_type":"lift","tcp_position_centroid":[0.52926,-0.02821,0.02566]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":16878.0,"contact_point_centroid":[0.52819,-0.00908,0.07477],"force_p95":0.08841,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32824,"mean_force":0.06043,"phase_index":3.0,"phase_name":"lift_clear","phase_type":"lift","tcp_position_centroid":[0.52668,-0.02812,0.07275]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":18023.0,"contact_point_centroid":[0.52821,-0.04709,0.0732],"force_p95":0.085,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31869,"mean_force":0.05738,"phase_index":3.0,"phase_name":"lift_clear","phase_type":"lift","tcp_position_centroid":[0.52669,-0.02812,0.07158]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2953.0,"contact_point_centroid":[0.62771,0.17544,0.26942],"force_p95":0.15548,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28099,"mean_force":0.09997,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.6257,0.15674,0.27273]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.54562,-0.02895,-0.00209],"force_p95":0.14896,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.22569,"mean_force":0.12981,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.53243,-0.02831,0.02539]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4007.0,"contact_point_centroid":[0.6262,0.13913,0.263],"force_p95":0.10302,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18011,"mean_force":0.07083,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.62592,0.15722,0.26669]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":13851.0,"contact_point_centroid":[0.57457,0.04236,0.2178],"force_p95":0.07954,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15535,"mean_force":0.05581,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.57319,0.06106,0.218]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":10044.0,"contact_point_centroid":[0.57726,0.083,0.22197],"force_p95":0.09604,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1421,"mean_force":0.0738,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.57481,0.06393,0.22115]},{"body_a":"world","body_b":"grasp_target","contact_count":416.0,"contact_point_centroid":[0.5456,-0.02923,-0.0017],"force_p95":0.13814,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12383,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.513,-0.00899,0.29094]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4073.0,"contact_point_centroid":[0.53209,-0.00908,0.02674],"force_p95":0.07892,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12784,"mean_force":0.05183,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.53119,-0.02828,0.02396]},{"body_a":"world","body_b":"grasp_target","contact_count":3244.0,"contact_point_centroid":[0.5456,-0.02923,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12264,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.53288,-0.0239,0.15585]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4954.0,"contact_point_centroid":[0.53209,-0.0474,0.02579],"force_p95":0.07117,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08835,"mean_force":0.04482,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.53119,-0.02828,0.02397]}],"total_contact_groups":13},"final_pose_error":0.00974,"key_states":{"actual_goal_position":[0.63284,0.16493,0.17692],"final_object_position":[0.64305,0.15638,0.016],"final_tcp_position":[0.62846,0.1623,0.20669],"realised_goal_position":[0.63284,0.16493,0.17692],"realised_object_initial_position":[0.5456,-0.02923,0.03]},"peak_contact_force":1.91601,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":105.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.03],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.25864,"object_z_max":0.03,"peak_contact_force":0.12232,"phase_name":"approach_above","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":416.0,"raw_peak_contact_force":0.13845,"subtask_id":"pre_grasp","tcp_end":[0.52832,-0.01931,0.28163],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.25639,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":811.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3244.0,"raw_peak_contact_force":0.12264,"subtask_id":"pre_grasp","tcp_end":[0.53978,-0.02853,0.03397],"tcp_start":[0.52832,-0.01931,0.28163],"tcp_to_object_dist_end":0.00988,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54545,-0.02819,0.02571],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26038,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.14295,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10827.0,"raw_peak_contact_force":0.22569,"subtask_id":"pre_grasp","tcp_end":[0.53116,-0.02827,0.02393],"tcp_start":[0.53978,-0.02853,0.03397],"tcp_to_object_dist_end":0.01441,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":32.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.54069,-0.02807,0.11498],"object_pos_start":[0.54545,-0.02819,0.02571],"object_to_goal_dist_end":0.22265,"object_to_goal_dist_start":0.26038,"object_z_max":0.11487,"peak_contact_force":0.0,"phase_name":"lift_clear","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":35094.0,"raw_peak_contact_force":0.72766,"subtask_id":"pre_grasp","tcp_end":[0.52676,-0.02811,0.1255],"tcp_start":[0.53116,-0.02827,0.02393],"tcp_to_object_dist_end":0.01746,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":27.0,"n_steps":775.0,"n_steps_budget":1000.0,"object_pos_end":[0.63355,0.15367,0.30119],"object_pos_start":[0.54069,-0.02807,0.11498],"object_to_goal_dist_end":0.12478,"object_to_goal_dist_start":0.22265,"object_z_max":0.30098,"peak_contact_force":0.11299,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":23895.0,"raw_peak_contact_force":0.15535,"subtask_id":"transport_goal","tcp_end":[0.62522,0.15349,0.31885],"tcp_start":[0.52676,-0.02811,0.1255],"tcp_to_object_dist_end":0.01953,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":328.0,"n_steps_budget":1000.0,"object_pos_end":[0.63673,0.15755,0.17041],"object_pos_start":[0.63355,0.15367,0.30119],"object_to_goal_dist_end":0.01058,"object_to_goal_dist_start":0.12478,"object_z_max":0.30133,"peak_contact_force":0.0,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":6960.0,"raw_peak_contact_force":0.28099,"subtask_id":"transport_goal","tcp_end":[0.62846,0.1623,0.20669],"tcp_start":[0.62522,0.15349,0.31885],"tcp_to_object_dist_end":0.03751,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.64305,0.15638,0.016],"object_pos_start":[0.63673,0.15755,0.17041],"object_to_goal_dist_end":0.16147,"object_to_goal_dist_start":0.01058,"object_z_max":0.17041,"peak_contact_force":0.12349,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":551.0,"raw_peak_contact_force":1.91601,"tcp_end":[0.62312,0.16068,0.22576],"tcp_start":[0.62846,0.1623,0.20669],"tcp_to_object_dist_end":0.21075,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `5836f8a66456087ed82e2e1accc6472c2a7681a19bf8e3d54637158aadaafc47`; realized-scene SHA-256: `776f3cbcac69f75f44cb26f0b1a492bbf1ced59f3c5fca79400c3f557c2ce565`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.61015,0.15287,0.12219]},{"name":"goal","value":[0.46286,-7e-05,0.03]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.61015,0.15287,0.12219]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.46286,-7e-05,0.03]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.16393,"average_solve_count":366.0,"average_success_count":366.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above.speed":0.07223,"descend_grasp.speed":0.08127,"descend_place.place_height":0.01031,"descend_place.speed":0.02324,"lift_clear.lift_clear_height":0.16448,"lift_clear.speed":0.05047,"release_object.max_time":1.10384,"transport_to_goal.speed":0.05648,"transport_to_goal.transport_height":0.23163},"optimized_scores":{"best_composite_score":0.12911,"best_fitness_score":0.72911,"best_task_score":0.49286},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":266.0,"contact_point_centroid":[0.6105,0.14991,-0.00496],"force_p95":1.01624,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.40667,"mean_force":0.279,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.59871,0.14918,0.15104]},{"body_a":"world","body_b":"grasp_target","contact_count":150.0,"contact_point_centroid":[0.45938,-0.00017,-0.00114],"force_p95":0.47193,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.63737,"mean_force":0.10301,"phase_index":3.0,"phase_name":"lift_clear","phase_type":"lift","tcp_position_centroid":[0.45071,-0.00023,0.02936]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":20994.0,"contact_point_centroid":[0.44797,0.01894,0.08302],"force_p95":0.07168,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28913,"mean_force":0.04822,"phase_index":3.0,"phase_name":"lift_clear","phase_type":"lift","tcp_position_centroid":[0.44819,-0.00024,0.08092]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":21056.0,"contact_point_centroid":[0.44798,-0.01941,0.08317],"force_p95":0.07106,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28247,"mean_force":0.04804,"phase_index":3.0,"phase_name":"lift_clear","phase_type":"lift","tcp_position_centroid":[0.44819,-0.00024,0.08105]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1175.0,"contact_point_centroid":[0.60423,0.16948,0.13713],"force_p95":0.07415,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16747,"mean_force":0.04612,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.603,0.15042,0.13673]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":997.0,"contact_point_centroid":[0.60367,0.13128,0.13712],"force_p95":0.08825,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16208,"mean_force":0.05296,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.60296,0.15041,0.13665]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":11099.0,"contact_point_centroid":[0.60212,0.16597,0.23966],"force_p95":0.07281,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15647,"mean_force":0.05024,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.60147,0.147,0.23909]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.46284,-0.00011,-0.00202],"force_p95":0.12877,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.14388,"mean_force":0.12443,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.45322,-0.00019,0.02884]},{"body_a":"world","body_b":"grasp_target","contact_count":200.0,"contact_point_centroid":[0.46286,-7e-05,-0.00134],"force_p95":0.13839,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12467,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.49156,-5e-05,0.29477]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":16457.0,"contact_point_centroid":[0.52194,0.05254,0.23255],"force_p95":0.06866,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13397,"mean_force":0.04684,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.52211,0.07159,0.23053]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":9800.0,"contact_point_centroid":[0.60193,0.12796,0.23846],"force_p95":0.08624,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13369,"mean_force":0.05655,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.60156,0.14708,0.23758]},{"body_a":"world","body_b":"grasp_target","contact_count":3184.0,"contact_point_centroid":[0.46286,-7e-05,-0.00199],"force_p95":0.12264,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12703,"mean_force":0.12265,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.46933,-8e-05,0.15971]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":14502.0,"contact_point_centroid":[0.52497,0.09334,0.23655],"force_p95":0.07538,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11714,"mean_force":0.05222,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.52483,0.07413,0.23415]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4844.0,"contact_point_centroid":[0.45227,-0.0194,0.02972],"force_p95":0.06799,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09846,"mean_force":0.04478,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.45215,-0.00021,0.02782]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4873.0,"contact_point_centroid":[0.45225,0.01899,0.0297],"force_p95":0.06805,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08551,"mean_force":0.04476,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.45215,-0.00021,0.02782]}],"total_contact_groups":15},"final_pose_error":0.00988,"key_states":{"actual_goal_position":[0.61015,0.15287,0.12219],"final_object_position":[0.61379,0.1499,0.01616],"final_tcp_position":[0.60521,0.151,0.14084],"realised_goal_position":[0.61015,0.15287,0.12219],"realised_object_initial_position":[0.46286,-7e-05,0.03]},"peak_contact_force":1.40667,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":51.0,"n_steps_budget":1000.0,"object_pos_end":[0.46286,-7e-05,0.02587],"object_pos_start":[0.46286,-7e-05,0.03],"object_to_goal_dist_end":0.23316,"object_to_goal_dist_start":0.23148,"object_z_max":0.03,"peak_contact_force":0.12742,"phase_name":"approach_above","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":200.0,"raw_peak_contact_force":0.13845,"subtask_id":"pre_grasp","tcp_end":[0.48113,-7e-05,0.28786],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.26263,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":796.0,"n_steps_budget":1000.0,"object_pos_end":[0.46286,-7e-05,0.02602],"object_pos_start":[0.46286,-7e-05,0.02587],"object_to_goal_dist_end":0.2331,"object_to_goal_dist_start":0.23316,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3184.0,"raw_peak_contact_force":0.12703,"subtask_id":"pre_grasp","tcp_end":[0.45969,-0.00012,0.0351],"tcp_start":[0.48113,-7e-05,0.28786],"tcp_to_object_dist_end":0.00962,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.46273,-0.00019,0.02591],"object_pos_start":[0.46286,-7e-05,0.02602],"object_to_goal_dist_end":0.2333,"object_to_goal_dist_start":0.2331,"object_z_max":0.02602,"peak_contact_force":0.1285,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11517.0,"raw_peak_contact_force":0.14388,"subtask_id":"pre_grasp","tcp_end":[0.45212,-0.00021,0.02779],"tcp_start":[0.45969,-0.00012,0.0351],"tcp_to_object_dist_end":0.01077,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.45649,-0.0002,0.1226],"object_pos_start":[0.46273,-0.00019,0.02591],"object_to_goal_dist_end":0.21689,"object_to_goal_dist_start":0.2333,"object_z_max":0.12249,"peak_contact_force":0.0,"phase_name":"lift_clear","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":42200.0,"raw_peak_contact_force":0.63737,"subtask_id":"pre_grasp","tcp_end":[0.44824,-0.00023,0.13147],"tcp_start":[0.45212,-0.00021,0.02779],"tcp_to_object_dist_end":0.01212,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":38.0,"n_steps":774.0,"n_steps_budget":1000.0,"object_pos_end":[0.60609,0.14377,0.32009],"object_pos_start":[0.45649,-0.0002,0.1226],"object_to_goal_dist_end":0.19815,"object_to_goal_dist_start":0.21689,"object_z_max":0.31986,"peak_contact_force":0.07281,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":30959.0,"raw_peak_contact_force":0.13397,"subtask_id":"transport_goal","tcp_end":[0.59957,0.14381,0.33343],"tcp_start":[0.44824,-0.00023,0.13147],"tcp_to_object_dist_end":0.01485,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":38.0,"n_steps":558.0,"n_steps_budget":1000.0,"object_pos_end":[0.61121,0.15103,0.12345],"object_pos_start":[0.60609,0.14377,0.32009],"object_to_goal_dist_end":0.00247,"object_to_goal_dist_start":0.19815,"object_z_max":0.32024,"peak_contact_force":0.07247,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":20899.0,"raw_peak_contact_force":0.15647,"subtask_id":"transport_goal","tcp_end":[0.60521,0.151,0.14084],"tcp_start":[0.59957,0.14381,0.33343],"tcp_to_object_dist_end":0.01839,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.61379,0.1499,0.01616],"object_pos_start":[0.61121,0.15103,0.12345],"object_to_goal_dist_end":0.10613,"object_to_goal_dist_start":0.00247,"object_z_max":0.12345,"peak_contact_force":0.10636,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2438.0,"raw_peak_contact_force":1.40667,"tcp_end":[0.59863,0.14916,0.16113],"tcp_start":[0.60521,0.151,0.14084],"tcp_to_object_dist_end":0.14576,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```