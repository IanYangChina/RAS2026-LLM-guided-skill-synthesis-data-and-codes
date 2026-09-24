## Search State

- **Seed**: 9
- **Iteration**: 5 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 4 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | impedance_control | position_control | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | force_exceeded | time_limit | 10 | 0.1125 | 0.28 | ❌ rejected |
| 3 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | impedance_control | position_control | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | force_exceeded | time_limit | 10 | 0.1531 | 0.37 | ✅ accepted |
| 2 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | impedance_control | position_control | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | force_exceeded | time_limit | 9 | 0.1515 | 0.27 | ✅ accepted |
| 1 | approach → descend → grasp → lift → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | — | position_control | impedance_control | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | force_exceeded | time_limit | 7 | 0.3008 | 0.25 | ✅ accepted |
| 0 | rotate → pull → push → descend → descend → grasp → approach | impedance_motion | arc_cartesian | impedance_motion | linear_cartesian | linear_cartesian | — | linear_cartesian | impedance_control | impedance_control | impedance_control | admittance_control | position_control | position_control | position_control | pose_tolerance | time_limit | time_limit | pose_tolerance | contact_detected | grasp_success | pose_tolerance | 6 | -0.1649 | 0.13 | ✅ accepted |

**Proposal policy**: task_score is 0.28 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.112) — your mutation base

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
    - 0.15
    tolerance: 0.01
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
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.0
    - 0.0
    tolerance: 0.005
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
    - 0.12
    tolerance: 0.02
    orientation:
      mode: none
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
      - 0.05
      - 0.2
      default: 0.12
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: transport_goal
- id: place_descend
  type: descend
  generator: linear_cartesian
  control: impedance_control
  termination: force_exceeded
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.05
    orientation:
      mode: none
  parameters:
    force_threshold:
      type: scalar
      range:
      - 5.0
      - 20.0
      default: 10.0
      binds_to:
      - path: termination.force_threshold
        mode: replace
    place_height:
      type: scalar
      range:
      - 0.02
      - 0.1
      default: 0.05
      binds_to:
      - path: target.offset.z
        mode: replace
    speed:
      type: scalar
      range:
      - 0.01
      - 0.05
      default: 0.02
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
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.15], tolerance=0.01
  - orientation: mode=align_axis, axis=[0.0, 0.0, -1.0], align_with=world_z, tolerance=0.1
  - parameter_bindings:
    - speed: status=consumed; consumers=generator.speed (replace)
- **descend_grasp** (`descend`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.0], tolerance=0.005
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
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.12], tolerance=0.02
  - orientation: mode=none
  - parameter_bindings:
    - speed: status=consumed; consumers=generator.speed (replace)
    - transport_height: status=consumed; consumers=target.offset.z (replace)
- **place_descend** (`descend`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.05]
  - orientation: mode=none
  - parameter_bindings:
    - force_threshold: status=consumed; consumers=termination.force_threshold (replace)
    - place_height: status=consumed; consumers=target.offset.z (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
- **release_object** (`release`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings:
    - max_time: status=consumed; consumers=duration.max_time (replace)

## Design Metrics

- **Composite score**: 0.112
- **task_score** (E): 0.284
- **fitness_score**: 0.620  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.143
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.650

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_above | 1.00 | 1.00 | 0.1204 |
| descend_grasp | 1.00 | 1.00 | 0.1476 |
| grasp_object | 1.00 | 1.00 | 0.0118 |
| lift_clear | 0.67 | 1.00 | 0.1074 |
| transport_to_goal | 0.00 | 1.00 | 0.0979 |
| place_descend | 1.00 | 1.00 | 0.0032 |
| release_object | 1.00 | 1.00 | 0.0242 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_above | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.510, -0.015, 0.187) | (0.515, -0.017, 0.030)→(0.515, -0.017, 0.026) | 0.268→0.270 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_grasp | descend | 1.00 / step_budget | (0.510, -0.015, 0.187)→(0.510, -0.017, 0.040) | (0.515, -0.017, 0.026)→(0.515, -0.017, 0.026) | 0.270→0.270 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_object | grasp | 1.00 / step_budget | (0.510, -0.017, 0.040)→(0.502, -0.016, 0.031) | (0.515, -0.017, 0.026)→(0.515, -0.016, 0.026) | 0.270→0.270 | 1.00 / 42.000 | 0.135 | 0.175 |
| lift_clear | lift | 0.67 / step_budget | (0.502, -0.016, 0.031)→(0.498, -0.016, 0.138) | (0.515, -0.016, 0.026)→(0.508, -0.016, 0.124) | 0.270→0.237 | 1.00 / 33.333 | 0.100 | 0.596 |
| transport_to_goal | approach | 0.00 / step_budget | (0.498, -0.016, 0.138)→(0.545, 0.058, 0.171) | (0.508, -0.016, 0.124)→(0.549, 0.058, 0.150) | 0.237→0.146 | 1.00 / 30.000 | 0.094 | 0.152 |
| place_descend | descend | 1.00 / force_exceeded | (0.545, 0.058, 0.171)→(0.544, 0.061, 0.169) | (0.549, 0.058, 0.150)→(0.548, 0.061, 0.148) | 0.146→0.145 | 1.00 / 29.667 | 56160.918 | 0.113 |
| release_object | release | 1.00 / step_budget | (0.544, 0.061, 0.169)→(0.539, 0.060, 0.192) | (0.548, 0.061, 0.148)→(0.546, 0.094, 0.012) | 0.145→0.195 | 1.00 / 3.333 | 0.143 | 1.423 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.392
- phase_score: 0.146
- phase_breakdown.pre_grasp_score: 0.732
- phase_breakdown.transport_goal_score: 0.000
- grasp_place_fitness: 0.676

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.676
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.392
- **Median Q (composite search score)**: 0.100
- **K-run variance**: 0.0018
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.359


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.59603,"average_solve_count":151.0,"average_success_count":151.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above.speed":0.06199,"descend_grasp.speed":0.07988,"lift_clear.lift_clear_height":0.12449,"lift_clear.speed":0.06803,"place_descend.force_threshold":13.3587,"place_descend.place_height":0.04802,"place_descend.speed":0.03643,"release_object.max_time":1.26753,"transport_to_goal.speed":0.0787,"transport_to_goal.transport_height":0.12252},"optimized_scores":{"best_composite_score":0.06816,"best_fitness_score":0.5753,"best_task_score":0.1969},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":117.0,"contact_point_centroid":[0.54268,0.11679,-0.009],"force_p95":1.43818,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.56881,"mean_force":0.58538,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.53754,0.05855,0.20983]},{"body_a":"world","body_b":"grasp_target","contact_count":168.0,"contact_point_centroid":[0.53209,-0.02033,-0.00117],"force_p95":0.47155,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.63787,"mean_force":0.11141,"phase_index":3.0,"phase_name":"lift_clear","phase_type":"lift","tcp_position_centroid":[0.5213,-0.02074,0.03177]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":16361.0,"contact_point_centroid":[0.52043,-0.00166,0.08439],"force_p95":0.08952,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.34362,"mean_force":0.06215,"phase_index":3.0,"phase_name":"lift_clear","phase_type":"lift","tcp_position_centroid":[0.51863,-0.02067,0.08259]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":17445.0,"contact_point_centroid":[0.52049,-0.03961,0.08317],"force_p95":0.08653,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31702,"mean_force":0.05895,"phase_index":3.0,"phase_name":"lift_clear","phase_type":"lift","tcp_position_centroid":[0.51865,-0.02067,0.08168]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1005.0,"contact_point_centroid":[0.54413,0.07928,0.18515],"force_p95":0.17317,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19445,"mean_force":0.09847,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.54046,0.05893,0.18769]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53703,-0.02115,-0.00205],"force_p95":0.13858,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.17941,"mean_force":0.12699,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.52424,-0.0208,0.0316]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":791.0,"contact_point_centroid":[0.54431,0.04067,0.18674],"force_p95":0.09319,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14689,"mean_force":0.05684,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.54123,0.05904,0.18841]},{"body_a":"world","body_b":"grasp_target","contact_count":1688.0,"contact_point_centroid":[0.53702,-0.02132,-0.00192],"force_p95":0.13411,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12292,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.51346,-0.0093,0.24265]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":15858.0,"contact_point_centroid":[0.53247,0.00121,0.16623],"force_p95":0.0872,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13803,"mean_force":0.06004,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.53021,0.02001,0.16611]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":492.0,"contact_point_centroid":[0.54638,0.07683,0.1901],"force_p95":0.11324,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13491,"mean_force":0.08318,"phase_index":5.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.54344,0.0581,0.19245]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":533.0,"contact_point_centroid":[0.5465,0.03954,0.19084],"force_p95":0.09409,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12763,"mean_force":0.07008,"phase_index":5.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.54344,0.0581,0.19245]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":14124.0,"contact_point_centroid":[0.53263,0.03788,0.16551],"force_p95":0.09363,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.125,"mean_force":0.06709,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.52983,0.01896,0.16534]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.53702,-0.02132,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.52926,-0.02014,0.09738]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4100.0,"contact_point_centroid":[0.52375,-0.00157,0.03298],"force_p95":0.07729,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12219,"mean_force":0.05181,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.52302,-0.02077,0.03021]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4907.0,"contact_point_centroid":[0.5238,-0.03986,0.03206],"force_p95":0.06953,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09206,"mean_force":0.04475,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.52302,-0.02077,0.03021]}],"total_contact_groups":15},"final_pose_error":0.19268,"key_states":{"actual_goal_position":[0.61031,0.22775,0.20741],"final_object_position":[0.53964,0.11405,0.0037],"final_tcp_position":[0.54283,0.05914,0.19109],"realised_goal_position":[0.61031,0.22775,0.20741],"realised_object_initial_position":[0.53702,-0.02132,0.03]},"peak_contact_force":269.64442,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":423.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.03],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31446,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_above","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1688.0,"raw_peak_contact_force":0.13845,"subtask_id":"pre_grasp","tcp_end":[0.52968,-0.01904,0.18634],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.16051,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.12263,"subtask_id":"pre_grasp","tcp_end":[0.53121,-0.02094,0.03962],"tcp_start":[0.52968,-0.01904,0.18634],"tcp_to_object_dist_end":0.0148,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.5369,-0.02068,0.02581],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31637,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.13526,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10807.0,"raw_peak_contact_force":0.17941,"subtask_id":"pre_grasp","tcp_end":[0.52299,-0.02077,0.03017],"tcp_start":[0.53121,-0.02094,0.03962],"tcp_to_object_dist_end":0.01457,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":31.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53125,-0.02061,0.12566],"object_pos_start":[0.5369,-0.02068,0.02581],"object_to_goal_dist_end":0.27316,"object_to_goal_dist_start":0.31637,"object_z_max":0.12557,"peak_contact_force":0.11567,"phase_name":"lift_clear","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":33974.0,"raw_peak_contact_force":0.63787,"subtask_id":"pre_grasp","tcp_end":[0.51887,-0.02067,0.14083],"tcp_start":[0.52299,-0.02077,0.03017],"tcp_to_object_dist_end":0.01958,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":25.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.54891,0.05696,0.17184],"object_pos_start":[0.53125,-0.02061,0.12566],"object_to_goal_dist_end":0.18495,"object_to_goal_dist_start":0.27316,"object_z_max":0.17181,"peak_contact_force":0.11068,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":29982.0,"raw_peak_contact_force":0.13803,"subtask_id":"transport_goal","tcp_end":[0.54395,0.05703,0.19379],"tcp_start":[0.51887,-0.02067,0.14083],"tcp_to_object_dist_end":0.02251,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":24.0,"n_steps":41.0,"n_steps_budget":1000.0,"object_pos_end":[0.54691,0.05906,0.16856],"object_pos_start":[0.54891,0.05696,0.17184],"object_to_goal_dist_end":0.18436,"object_to_goal_dist_start":0.18495,"object_z_max":0.17184,"peak_contact_force":269.64442,"phase_name":"place_descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1025.0,"raw_peak_contact_force":0.13491,"subtask_id":"transport_goal","tcp_end":[0.54283,0.05914,0.19109],"tcp_start":[0.54395,0.05703,0.19379],"tcp_to_object_dist_end":0.0229,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53964,0.11405,0.0037],"object_pos_start":[0.54691,0.05906,0.16856],"object_to_goal_dist_end":0.24376,"object_to_goal_dist_start":0.18436,"object_z_max":0.16856,"peak_contact_force":0.27145,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1913.0,"raw_peak_contact_force":1.56881,"tcp_end":[0.53749,0.05855,0.21456],"tcp_start":[0.54283,0.05914,0.19109],"tcp_to_object_dist_end":0.21805,"terminated_normally":true,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.24324,"average_solve_count":185.0,"average_success_count":185.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above.speed":0.03885,"descend_grasp.speed":0.08992,"lift_clear.lift_clear_height":0.12974,"lift_clear.speed":0.06749,"place_descend.force_threshold":19.38426,"place_descend.place_height":0.05979,"place_descend.speed":0.03327,"release_object.max_time":1.11023,"transport_to_goal.speed":0.04679,"transport_to_goal.transport_height":0.07441},"optimized_scores":{"best_composite_score":0.10047,"best_fitness_score":0.60761,"best_task_score":0.26371},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":176.0,"contact_point_centroid":[0.55433,0.08469,-0.00711],"force_p95":0.95535,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.26056,"mean_force":0.3672,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.55142,0.03899,0.18329]},{"body_a":"world","body_b":"grasp_target","contact_count":172.0,"contact_point_centroid":[0.54082,-0.02789,-0.00118],"force_p95":0.45454,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.61802,"mean_force":0.10791,"phase_index":3.0,"phase_name":"lift_clear","phase_type":"lift","tcp_position_centroid":[0.52951,-0.02835,0.03297]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":16005.0,"contact_point_centroid":[0.52879,-0.00925,0.08448],"force_p95":0.09203,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33948,"mean_force":0.06345,"phase_index":3.0,"phase_name":"lift_clear","phase_type":"lift","tcp_position_centroid":[0.52684,-0.02825,0.08268]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":17386.0,"contact_point_centroid":[0.52883,-0.04717,0.08346],"force_p95":0.0866,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31985,"mean_force":0.0591,"phase_index":3.0,"phase_name":"lift_clear","phase_type":"lift","tcp_position_centroid":[0.52686,-0.02825,0.08208]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.54562,-0.02902,-0.00207],"force_p95":0.14475,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.20415,"mean_force":0.12864,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.53251,-0.02845,0.0328]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":981.0,"contact_point_centroid":[0.55836,0.05939,0.16109],"force_p95":0.17123,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20377,"mean_force":0.09379,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.55471,0.03929,0.16346]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":12950.0,"contact_point_centroid":[0.54518,0.02549,0.15492],"force_p95":0.09514,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19185,"mean_force":0.07241,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.54232,0.00656,0.15467]},{"body_a":"world","body_b":"grasp_target","contact_count":1872.0,"contact_point_centroid":[0.5456,-0.02923,-0.00193],"force_p95":0.13354,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12289,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.51744,-0.01293,0.24174]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":15571.0,"contact_point_centroid":[0.5444,-0.01385,0.15405],"force_p95":0.08817,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13792,"mean_force":0.06057,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.54139,0.00485,0.15373]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4088.0,"contact_point_centroid":[0.53213,-0.00921,0.03414],"force_p95":0.07831,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1313,"mean_force":0.05185,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.53127,-0.02841,0.03136]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.5456,-0.02923,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.53754,-0.0277,0.09662]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1326.0,"contact_point_centroid":[0.56035,0.01869,0.16644],"force_p95":0.0925,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11812,"mean_force":0.07103,"phase_index":5.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.55718,0.03742,0.16796]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1326.0,"contact_point_centroid":[0.56045,0.05615,0.16627],"force_p95":0.09277,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11569,"mean_force":0.071,"phase_index":5.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.55718,0.03742,0.16796]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":791.0,"contact_point_centroid":[0.55872,0.02083,0.16256],"force_p95":0.09181,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09437,"mean_force":0.05657,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.55545,0.03937,0.16421]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4937.0,"contact_point_centroid":[0.53214,-0.04752,0.03319],"force_p95":0.07069,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08372,"mean_force":0.04472,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.53128,-0.02841,0.03136]}],"total_contact_groups":15},"final_pose_error":0.16236,"key_states":{"actual_goal_position":[0.63284,0.16493,0.17692],"final_object_position":[0.55402,0.08432,0.01181],"final_tcp_position":[0.55709,0.03944,0.16689],"realised_goal_position":[0.63284,0.16493,0.17692],"realised_object_initial_position":[0.5456,-0.02923,0.03]},"peak_contact_force":261.37965,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":469.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.03],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.25864,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_above","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1872.0,"raw_peak_contact_force":0.13845,"subtask_id":"pre_grasp","tcp_end":[0.53766,-0.02632,0.18527],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.15947,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.12263,"subtask_id":"pre_grasp","tcp_end":[0.53953,-0.02868,0.04107],"tcp_start":[0.53766,-0.02632,0.18527],"tcp_to_object_dist_end":0.01624,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54549,-0.02838,0.02574],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26049,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.14023,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10825.0,"raw_peak_contact_force":0.20415,"subtask_id":"pre_grasp","tcp_end":[0.53124,-0.02841,0.03132],"tcp_start":[0.53953,-0.02868,0.04107],"tcp_to_object_dist_end":0.0153,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":28.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53913,-0.02789,0.12439],"object_pos_start":[0.54549,-0.02838,0.02574],"object_to_goal_dist_end":0.22073,"object_to_goal_dist_start":0.26049,"object_z_max":0.12428,"peak_contact_force":0.1145,"phase_name":"lift_clear","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":33563.0,"raw_peak_contact_force":0.61802,"subtask_id":"pre_grasp","tcp_end":[0.52706,-0.02825,0.14071],"tcp_start":[0.53124,-0.02841,0.03132],"tcp_to_object_dist_end":0.02031,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":26.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.56249,0.03455,0.14723],"object_pos_start":[0.53913,-0.02789,0.12439],"object_to_goal_dist_end":0.1511,"object_to_goal_dist_start":0.22073,"object_z_max":0.14721,"peak_contact_force":0.09725,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":28521.0,"raw_peak_contact_force":0.19185,"subtask_id":"transport_goal","tcp_end":[0.55779,0.0348,0.17028],"tcp_start":[0.52706,-0.02825,0.14071],"tcp_to_object_dist_end":0.02353,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":25.0,"n_steps":102.0,"n_steps_budget":1000.0,"object_pos_end":[0.56071,0.03921,0.14304],"object_pos_start":[0.56249,0.03455,0.14723],"object_to_goal_dist_end":0.14885,"object_to_goal_dist_start":0.1511,"object_z_max":0.14723,"peak_contact_force":261.37965,"phase_name":"place_descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2652.0,"raw_peak_contact_force":0.11812,"subtask_id":"transport_goal","tcp_end":[0.55709,0.03944,0.16689],"tcp_start":[0.55779,0.0348,0.17028],"tcp_to_object_dist_end":0.02412,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.55402,0.08432,0.01181],"object_pos_start":[0.56071,0.03921,0.14304],"object_to_goal_dist_end":0.19993,"object_to_goal_dist_start":0.14885,"object_z_max":0.14304,"peak_contact_force":0.0751,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1948.0,"raw_peak_contact_force":1.26056,"tcp_end":[0.55135,0.03899,0.19009],"tcp_start":[0.55709,0.03944,0.16689],"tcp_to_object_dist_end":0.18397,"terminated_normally":true,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.78188,"average_solve_count":298.0,"average_success_count":298.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above.speed":0.02892,"descend_grasp.speed":0.02216,"lift_clear.lift_clear_height":0.20034,"lift_clear.speed":0.02719,"place_descend.force_threshold":12.82479,"place_descend.place_height":0.07264,"place_descend.speed":0.01869,"release_object.max_time":1.0691,"transport_to_goal.speed":0.09924,"transport_to_goal.transport_height":0.05039},"optimized_scores":{"best_composite_score":0.16883,"best_fitness_score":0.67597,"best_task_score":0.39187},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":143.0,"contact_point_centroid":[0.52175,0.07882,-0.00817],"force_p95":1.15456,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.43906,"mean_force":0.46138,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.52698,0.08226,0.16172]},{"body_a":"world","body_b":"grasp_target","contact_count":156.0,"contact_point_centroid":[0.458,-3e-05,-0.00118],"force_p95":0.46432,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.53353,"mean_force":0.11997,"phase_index":3.0,"phase_name":"lift_clear","phase_type":"lift","tcp_position_centroid":[0.44991,-0.00022,0.03237]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":20910.0,"contact_point_centroid":[0.44716,0.01895,0.08481],"force_p95":0.07105,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27148,"mean_force":0.04844,"phase_index":3.0,"phase_name":"lift_clear","phase_type":"lift","tcp_position_centroid":[0.44742,-0.00023,0.08271]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":21078.0,"contact_point_centroid":[0.44718,-0.0194,0.08512],"force_p95":0.07039,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24171,"mean_force":0.04804,"phase_index":3.0,"phase_name":"lift_clear","phase_type":"lift","tcp_position_centroid":[0.44743,-0.00023,0.08302]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.46284,-3e-05,-0.00201],"force_p95":0.12802,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.14007,"mean_force":0.12427,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.45242,-0.00019,0.03201]},{"body_a":"world","body_b":"grasp_target","contact_count":1480.0,"contact_point_centroid":[0.46286,-7e-05,-0.00191],"force_p95":0.13511,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12296,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.48183,-4e-05,0.24561]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":19710.0,"contact_point_centroid":[0.49054,0.02494,0.14128],"force_p95":0.07498,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12584,"mean_force":0.04949,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.49131,0.04416,0.13939]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.46286,-7e-05,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.45969,-9e-05,0.1103]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":21871.0,"contact_point_centroid":[0.49146,0.06387,0.14169],"force_p95":0.06735,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11907,"mean_force":0.04469,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.49194,0.04477,0.13952]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1335.0,"contact_point_centroid":[0.53062,0.10206,0.14794],"force_p95":0.06552,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09448,"mean_force":0.0388,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.53102,0.08296,0.14591]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4389.0,"contact_point_centroid":[0.45111,0.0191,0.03304],"force_p95":0.07394,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09377,"mean_force":0.04932,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.45135,-0.0002,0.03098]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1120.0,"contact_point_centroid":[0.5302,0.06365,0.14782],"force_p95":0.07486,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09241,"mean_force":0.04564,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.53098,0.08295,0.14585]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5332.0,"contact_point_centroid":[0.45066,-0.01928,0.03249],"force_p95":0.06282,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0864,"mean_force":0.0409,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.45135,-0.0002,0.03098]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":21.0,"contact_point_centroid":[0.53264,0.10228,0.15039],"force_p95":0.08518,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.086,"mean_force":0.05661,"phase_index":5.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.53266,0.08312,0.14844]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":18.0,"contact_point_centroid":[0.5319,0.06394,0.15033],"force_p95":0.07661,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0835,"mean_force":0.05703,"phase_index":5.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.53266,0.08312,0.14844]}],"total_contact_groups":15},"final_pose_error":0.11406,"key_states":{"actual_goal_position":[0.61015,0.15287,0.12219],"final_object_position":[0.54453,0.08266,0.01966],"final_tcp_position":[0.5327,0.08316,0.14843],"realised_goal_position":[0.61015,0.15287,0.12219],"realised_object_initial_position":[0.46286,-7e-05,0.03]},"peak_contact_force":167951.73011,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":371.0,"n_steps_budget":1000.0,"object_pos_end":[0.46286,-7e-05,0.02602],"object_pos_start":[0.46286,-7e-05,0.03],"object_to_goal_dist_end":0.2331,"object_to_goal_dist_start":0.23148,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_above","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1480.0,"raw_peak_contact_force":0.13845,"subtask_id":"pre_grasp","tcp_end":[0.46405,-7e-05,0.18962],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.16361,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.46286,-7e-05,0.02602],"object_pos_start":[0.46286,-7e-05,0.02602],"object_to_goal_dist_end":0.2331,"object_to_goal_dist_start":0.2331,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.12263,"subtask_id":"pre_grasp","tcp_end":[0.45862,-0.00012,0.038],"tcp_start":[0.46405,-7e-05,0.18962],"tcp_to_object_dist_end":0.01271,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.46274,-0.0,0.02592],"object_pos_start":[0.46286,-7e-05,0.02602],"object_to_goal_dist_end":0.23317,"object_to_goal_dist_start":0.2331,"object_z_max":0.02602,"peak_contact_force":0.12817,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11521.0,"raw_peak_contact_force":0.14007,"subtask_id":"pre_grasp","tcp_end":[0.45132,-0.0002,0.03095],"tcp_start":[0.45862,-0.00012,0.038],"tcp_to_object_dist_end":0.01248,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.45511,-0.00013,0.12115],"object_pos_start":[0.46274,-0.0,0.02592],"object_to_goal_dist_end":0.21783,"object_to_goal_dist_start":0.23317,"object_z_max":0.12106,"peak_contact_force":0.07036,"phase_name":"lift_clear","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":42144.0,"raw_peak_contact_force":0.53353,"subtask_id":"pre_grasp","tcp_end":[0.4475,-0.00022,0.13278],"tcp_start":[0.45132,-0.0002,0.03095],"tcp_to_object_dist_end":0.0139,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":39.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53552,0.08328,0.13171],"object_pos_start":[0.45511,-0.00013,0.12115],"object_to_goal_dist_end":0.10248,"object_to_goal_dist_start":0.21783,"object_z_max":0.13171,"peak_contact_force":0.07519,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":41581.0,"raw_peak_contact_force":0.12584,"subtask_id":"transport_goal","tcp_end":[0.53266,0.08312,0.14844],"tcp_start":[0.4475,-0.00022,0.13278],"tcp_to_object_dist_end":0.01697,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.53551,0.08331,0.13168],"object_pos_start":[0.53552,0.08328,0.13171],"object_to_goal_dist_end":0.10247,"object_to_goal_dist_start":0.10248,"object_z_max":0.13171,"peak_contact_force":167951.73011,"phase_name":"place_descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":39.0,"raw_peak_contact_force":0.086,"subtask_id":"transport_goal","tcp_end":[0.5327,0.08316,0.14843],"tcp_start":[0.53266,0.08312,0.14844],"tcp_to_object_dist_end":0.01698,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54453,0.08266,0.01966],"object_pos_start":[0.53551,0.08331,0.13168],"object_to_goal_dist_end":0.14053,"object_to_goal_dist_start":0.10247,"object_z_max":0.13168,"peak_contact_force":0.08126,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2598.0,"raw_peak_contact_force":1.43906,"tcp_end":[0.52687,0.08224,0.17241],"tcp_start":[0.5327,0.08316,0.14843],"tcp_to_object_dist_end":0.15376,"terminated_normally":true,"termination_reason":"step_budget"}],"success":false}]}
```