## Search State

- **Seed**: 9
- **Iteration**: 3 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 2 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | impedance_control | position_control | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | force_exceeded | time_limit | 9 | 0.1515 | 0.27 | ✅ accepted |
| 1 | approach → descend → grasp → lift → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | — | position_control | impedance_control | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | force_exceeded | time_limit | 7 | 0.3008 | 0.25 | ✅ accepted |
| 0 | rotate → pull → push → descend → descend → grasp → approach | impedance_motion | arc_cartesian | impedance_motion | linear_cartesian | linear_cartesian | — | linear_cartesian | impedance_control | impedance_control | impedance_control | admittance_control | position_control | position_control | position_control | pose_tolerance | time_limit | time_limit | pose_tolerance | contact_detected | grasp_success | pose_tolerance | 6 | -0.1649 | 0.13 | ✅ accepted |

**Proposal policy**: task_score is 0.27 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.152) — your mutation base

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
    tolerance: 0.01
    orientation:
      mode: keep_current
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
    - 0.0
    orientation:
      mode: keep_current
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
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.12], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - speed: status=consumed; consumers=generator.speed (replace)
    - transport_height: status=consumed; consumers=target.offset.z (replace)
- **place_descend** (`descend`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings:
    - force_threshold: status=consumed; consumers=termination.force_threshold (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
- **release_object** (`release`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings:
    - max_time: status=consumed; consumers=duration.max_time (replace)

## Design Metrics

- **Composite score**: 0.152
- **task_score** (E): 0.266
- **fitness_score**: 0.609  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.143
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.600

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_above | 1.00 | 1.00 | 0.1204 |
| descend_grasp | 1.00 | 1.00 | 0.1480 |
| grasp_object | 1.00 | 1.00 | 0.0118 |
| lift_clear | 0.33 | 1.00 | 0.0989 |
| transport_to_goal | 0.00 | 1.00 | 0.0894 |
| place_descend | 1.00 | 1.00 | 0.0069 |
| release_object | 1.00 | 1.00 | 0.0243 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_above | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.510, -0.015, 0.187) | (0.515, -0.017, 0.030)→(0.515, -0.017, 0.026) | 0.268→0.270 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_grasp | descend | 1.00 / step_budget | (0.510, -0.015, 0.187)→(0.510, -0.017, 0.039) | (0.515, -0.017, 0.026)→(0.515, -0.017, 0.026) | 0.270→0.270 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_object | grasp | 1.00 / step_budget | (0.510, -0.017, 0.039)→(0.502, -0.016, 0.030) | (0.515, -0.017, 0.026)→(0.515, -0.016, 0.026) | 0.270→0.270 | 1.00 / 41.667 | 0.135 | 0.175 |
| lift_clear | lift | 0.33 / step_budget | (0.502, -0.016, 0.030)→(0.498, -0.016, 0.129) | (0.515, -0.016, 0.026)→(0.508, -0.016, 0.115) | 0.270→0.239 | 1.00 / 35.667 | 0.087 | 0.610 |
| transport_to_goal | approach | 0.00 / step_budget | (0.498, -0.016, 0.129)→(0.538, 0.053, 0.165) | (0.508, -0.016, 0.115)→(0.543, 0.053, 0.141) | 0.239→0.157 | 1.00 / 26.667 | 0.087 | 0.168 |
| place_descend | descend | 1.00 / force_exceeded | (0.538, 0.053, 0.165)→(0.538, 0.058, 0.162) | (0.543, 0.053, 0.141)→(0.543, 0.059, 0.136) | 0.157→0.153 | 1.00 / 24.333 | 3433.216 | 0.121 |
| release_object | release | 1.00 / step_budget | (0.538, 0.058, 0.162)→(0.532, 0.058, 0.185) | (0.543, 0.059, 0.136)→(0.551, 0.066, 0.018) | 0.153→0.205 | 1.00 / 3.333 | 0.153 | 1.359 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.369
- phase_score: 0.156
- phase_breakdown.pre_grasp_score: 0.722
- phase_breakdown.transport_goal_score: 0.014
- grasp_place_fitness: 0.665

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.665
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.369
- **Median Q (composite search score)**: 0.137
- **K-run variance**: 0.0017
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.284


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.16022,"average_solve_count":181.0,"average_success_count":181.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above.speed":0.04533,"descend_grasp.speed":0.06671,"lift_clear.lift_clear_height":0.14781,"lift_clear.speed":0.05872,"place_descend.force_threshold":15.3739,"place_descend.speed":0.04074,"release_object.max_time":1.58096,"transport_to_goal.speed":0.06632,"transport_to_goal.transport_height":0.05146},"optimized_scores":{"best_composite_score":0.11023,"best_fitness_score":0.56737,"best_task_score":0.18557},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":156.0,"contact_point_centroid":[0.54156,0.07107,-0.0074],"force_p95":1.18039,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.26023,"mean_force":0.44552,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.53994,0.07151,0.1758]},{"body_a":"world","body_b":"grasp_target","contact_count":202.0,"contact_point_centroid":[0.53217,-0.02022,-0.00117],"force_p95":0.32489,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55772,"mean_force":0.09267,"phase_index":3.0,"phase_name":"lift_clear","phase_type":"lift","tcp_position_centroid":[0.521,-0.02069,0.03535]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":18491.0,"contact_point_centroid":[0.51938,-0.00153,0.08402],"force_p95":0.07896,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32205,"mean_force":0.05456,"phase_index":3.0,"phase_name":"lift_clear","phase_type":"lift","tcp_position_centroid":[0.51857,-0.02063,0.08188]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":19182.0,"contact_point_centroid":[0.51941,-0.03969,0.08263],"force_p95":0.07691,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30261,"mean_force":0.0531,"phase_index":3.0,"phase_name":"lift_clear","phase_type":"lift","tcp_position_centroid":[0.51859,-0.02063,0.08074]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53703,-0.02116,-0.00206],"force_p95":0.13961,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.18111,"mean_force":0.12724,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.52417,-0.02075,0.03515]},{"body_a":"world","body_b":"grasp_target","contact_count":1732.0,"contact_point_centroid":[0.53702,-0.02132,-0.00192],"force_p95":0.13411,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12291,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.51347,-0.00932,0.24252]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4845.0,"contact_point_centroid":[0.54714,0.04804,0.163],"force_p95":0.08454,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13418,"mean_force":0.06227,"phase_index":5.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.54416,0.06705,0.16125]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4101.0,"contact_point_centroid":[0.52371,-0.00152,0.03653],"force_p95":0.07745,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.126,"mean_force":0.05183,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.52296,-0.02073,0.03376]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.53702,-0.02132,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.52917,-0.02012,0.0999]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5491.0,"contact_point_centroid":[0.54701,0.08591,0.16197],"force_p95":0.07694,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1189,"mean_force":0.0557,"phase_index":5.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.54416,0.06705,0.16125]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":15940.0,"contact_point_centroid":[0.53227,0.00247,0.14674],"force_p95":0.08738,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10029,"mean_force":0.05998,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.5305,0.02156,0.14525]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":959.0,"contact_point_centroid":[0.54721,0.05306,0.16011],"force_p95":0.08434,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09011,"mean_force":0.05228,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.54391,0.07213,0.1588]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":18655.0,"contact_point_centroid":[0.53181,0.04095,0.14582],"force_p95":0.0761,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08772,"mean_force":0.05185,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.53065,0.02208,0.14545]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1018.0,"contact_point_centroid":[0.54749,0.09107,0.15963],"force_p95":0.07951,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0871,"mean_force":0.05004,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.54392,0.07213,0.15882]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4910.0,"contact_point_centroid":[0.52375,-0.03982,0.03561],"force_p95":0.06975,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08692,"mean_force":0.04471,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.52296,-0.02073,0.03376]}],"total_contact_groups":15},"final_pose_error":0.17453,"key_states":{"actual_goal_position":[0.61031,0.22775,0.20741],"final_object_position":[0.56127,0.07134,0.01516],"final_tcp_position":[0.54564,0.07228,0.16154],"realised_goal_position":[0.61031,0.22775,0.20741],"realised_object_initial_position":[0.53702,-0.02132,0.03]},"peak_contact_force":256.09241,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":434.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.03],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31446,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_above","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1732.0,"raw_peak_contact_force":0.13845,"subtask_id":"pre_grasp","tcp_end":[0.52971,-0.01907,0.18614],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.1603,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.12263,"subtask_id":"pre_grasp","tcp_end":[0.53107,-0.02089,0.04315],"tcp_start":[0.52971,-0.01907,0.18614],"tcp_to_object_dist_end":0.01814,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53691,-0.02067,0.02579],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31636,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.13624,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10811.0,"raw_peak_contact_force":0.18111,"subtask_id":"pre_grasp","tcp_end":[0.52293,-0.02073,0.03372],"tcp_start":[0.53107,-0.02089,0.04315],"tcp_to_object_dist_end":0.01608,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":42.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.52645,-0.02061,0.11221],"object_pos_start":[0.53691,-0.02067,0.02579],"object_to_goal_dist_end":0.27889,"object_to_goal_dist_start":0.31636,"object_z_max":0.1121,"peak_contact_force":0.07011,"phase_name":"lift_clear","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":37875.0,"raw_peak_contact_force":0.55772,"subtask_id":"pre_grasp","tcp_end":[0.51869,-0.02062,0.12878],"tcp_start":[0.52293,-0.02073,0.03372],"tcp_to_object_dist_end":0.01829,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":32.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.54881,0.06031,0.14261],"object_pos_start":[0.52645,-0.02061,0.11221],"object_to_goal_dist_end":0.18979,"object_to_goal_dist_start":0.27889,"object_z_max":0.14257,"peak_contact_force":0.08496,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":34595.0,"raw_peak_contact_force":0.10029,"subtask_id":"transport_goal","tcp_end":[0.54483,0.06053,0.165],"tcp_start":[0.51869,-0.02062,0.12878],"tcp_to_object_dist_end":0.02275,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":31.0,"n_steps":323.0,"n_steps_budget":1000.0,"object_pos_end":[0.54898,0.07202,0.13752],"object_pos_start":[0.54881,0.06031,0.14261],"object_to_goal_dist_end":0.18139,"object_to_goal_dist_start":0.18979,"object_z_max":0.14261,"peak_contact_force":256.09241,"phase_name":"place_descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":10336.0,"raw_peak_contact_force":0.13418,"subtask_id":"transport_goal","tcp_end":[0.54564,0.07228,0.16154],"tcp_start":[0.54483,0.06053,0.165],"tcp_to_object_dist_end":0.02425,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.56127,0.07134,0.01516],"object_pos_start":[0.54898,0.07202,0.13752],"object_to_goal_dist_end":0.25265,"object_to_goal_dist_start":0.18139,"object_z_max":0.13752,"peak_contact_force":0.26433,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2133.0,"raw_peak_contact_force":1.26023,"tcp_end":[0.53986,0.0715,0.18491],"tcp_start":[0.54564,0.07228,0.16154],"tcp_to_object_dist_end":0.1711,"terminated_normally":true,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.39597,"average_solve_count":149.0,"average_success_count":149.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above.speed":0.07801,"descend_grasp.speed":0.07399,"lift_clear.lift_clear_height":0.15741,"lift_clear.speed":0.0602,"place_descend.force_threshold":11.97754,"place_descend.speed":0.02064,"release_object.max_time":0.87421,"transport_to_goal.speed":0.05993,"transport_to_goal.transport_height":0.0794},"optimized_scores":{"best_composite_score":0.13687,"best_fitness_score":0.59402,"best_task_score":0.24366},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":142.0,"contact_point_centroid":[0.54662,0.03678,-0.00839],"force_p95":1.1655,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.22637,"mean_force":0.46979,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.54932,0.0366,0.17128]},{"body_a":"world","body_b":"grasp_target","contact_count":209.0,"contact_point_centroid":[0.54088,-0.02775,-0.00118],"force_p95":0.29875,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.52778,"mean_force":0.09002,"phase_index":3.0,"phase_name":"lift_clear","phase_type":"lift","tcp_position_centroid":[0.52918,-0.02826,0.03776]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":17966.0,"contact_point_centroid":[0.52784,-0.00909,0.08633],"force_p95":0.08037,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31762,"mean_force":0.05606,"phase_index":3.0,"phase_name":"lift_clear","phase_type":"lift","tcp_position_centroid":[0.52679,-0.02817,0.08404]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":18804.0,"contact_point_centroid":[0.52787,-0.04722,0.08497],"force_p95":0.07822,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30439,"mean_force":0.05416,"phase_index":3.0,"phase_name":"lift_clear","phase_type":"lift","tcp_position_centroid":[0.52681,-0.02817,0.08298]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.54562,-0.02905,-0.00208],"force_p95":0.14651,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.2056,"mean_force":0.12906,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.53242,-0.02837,0.03755]},{"body_a":"world","body_b":"grasp_target","contact_count":1732.0,"contact_point_centroid":[0.5456,-0.02923,-0.00192],"force_p95":0.13411,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12291,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.51752,-0.01295,0.2417]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4092.0,"contact_point_centroid":[0.53207,-0.00912,0.03888],"force_p95":0.07856,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13494,"mean_force":0.05185,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.5312,-0.02833,0.03611]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":16203.0,"contact_point_centroid":[0.54393,0.02431,0.15006],"force_p95":0.08656,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12847,"mean_force":0.05904,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.54145,0.00534,0.14849]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.5456,-0.02923,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.53739,-0.02766,0.09886]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":17177.0,"contact_point_centroid":[0.5438,-0.01368,0.14968],"force_p95":0.08283,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1177,"mean_force":0.05602,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.54141,0.00523,0.14844]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3145.0,"contact_point_centroid":[0.5587,0.0541,0.1621],"force_p95":0.07479,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08478,"mean_force":0.05604,"phase_index":5.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.55493,0.03501,0.16025]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1050.0,"contact_point_centroid":[0.55714,0.05608,0.15739],"force_p95":0.07478,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08328,"mean_force":0.0486,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.55343,0.03695,0.15602]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4941.0,"contact_point_centroid":[0.53209,-0.04744,0.03795],"force_p95":0.0711,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08061,"mean_force":0.04466,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.5312,-0.02833,0.03612]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1110.0,"contact_point_centroid":[0.55712,0.0179,0.15754],"force_p95":0.07174,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07937,"mean_force":0.04584,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.55343,0.03695,0.15602]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3515.0,"contact_point_centroid":[0.5583,0.01601,0.16184],"force_p95":0.06992,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07575,"mean_force":0.05023,"phase_index":5.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.55493,0.03501,0.16025]}],"total_contact_groups":15},"final_pose_error":0.15074,"key_states":{"actual_goal_position":[0.63284,0.16493,0.17692],"final_object_position":[0.56682,0.03649,0.022],"final_tcp_position":[0.55512,0.03705,0.15874],"realised_goal_position":[0.63284,0.16493,0.17692],"realised_object_initial_position":[0.5456,-0.02923,0.03]},"peak_contact_force":283.24786,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":434.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.03],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.25864,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_above","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1732.0,"raw_peak_contact_force":0.13845,"subtask_id":"pre_grasp","tcp_end":[0.53765,-0.02632,0.18526],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.15946,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.12263,"subtask_id":"pre_grasp","tcp_end":[0.53942,-0.02859,0.04586],"tcp_start":[0.53765,-0.02632,0.18526],"tcp_to_object_dist_end":0.02079,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54551,-0.02836,0.02571],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26048,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.14196,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10833.0,"raw_peak_contact_force":0.2056,"subtask_id":"pre_grasp","tcp_end":[0.53117,-0.02833,0.03608],"tcp_start":[0.53942,-0.02859,0.04586],"tcp_to_object_dist_end":0.01769,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":35.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53399,-0.02798,0.11418],"object_pos_start":[0.54551,-0.02836,0.02571],"object_to_goal_dist_end":0.22566,"object_to_goal_dist_start":0.26048,"object_z_max":0.11407,"peak_contact_force":0.09209,"phase_name":"lift_clear","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":36979.0,"raw_peak_contact_force":0.52778,"subtask_id":"pre_grasp","tcp_end":[0.52694,-0.02817,0.13309],"tcp_start":[0.53117,-0.02833,0.03608],"tcp_to_object_dist_end":0.02018,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":36.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.55996,0.03194,0.14041],"object_pos_start":[0.53399,-0.02798,0.11418],"object_to_goal_dist_end":0.15599,"object_to_goal_dist_start":0.22566,"object_z_max":0.14038,"peak_contact_force":0.07482,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":33380.0,"raw_peak_contact_force":0.12847,"subtask_id":"transport_goal","tcp_end":[0.55599,0.03186,0.16485],"tcp_start":[0.52694,-0.02817,0.13309],"tcp_to_object_dist_end":0.02476,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":35.0,"n_steps":185.0,"n_steps_budget":1000.0,"object_pos_end":[0.55882,0.0371,0.13343],"object_pos_start":[0.55996,0.03194,0.14041],"object_to_goal_dist_end":0.15399,"object_to_goal_dist_start":0.15599,"object_z_max":0.14041,"peak_contact_force":283.24786,"phase_name":"place_descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":6660.0,"raw_peak_contact_force":0.08478,"subtask_id":"transport_goal","tcp_end":[0.55512,0.03705,0.15874],"tcp_start":[0.55599,0.03186,0.16485],"tcp_to_object_dist_end":0.02558,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.56682,0.03649,0.022],"object_pos_start":[0.55882,0.0371,0.13343],"object_to_goal_dist_end":0.2118,"object_to_goal_dist_start":0.15399,"object_z_max":0.13343,"peak_contact_force":0.06955,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2302.0,"raw_peak_contact_force":1.22637,"tcp_end":[0.54922,0.03659,0.18189],"tcp_start":[0.55512,0.03705,0.15874],"tcp_to_object_dist_end":0.16085,"terminated_normally":true,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.84167,"average_solve_count":240.0,"average_success_count":240.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above.speed":0.02562,"descend_grasp.speed":0.05607,"lift_clear.lift_clear_height":0.1422,"lift_clear.speed":0.05766,"place_descend.force_threshold":19.99579,"place_descend.speed":0.01589,"release_object.max_time":1.38725,"transport_to_goal.speed":0.07051,"transport_to_goal.transport_height":0.1093},"optimized_scores":{"best_composite_score":0.20752,"best_fitness_score":0.66466,"best_task_score":0.36924},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":482.0,"contact_point_centroid":[0.52522,0.08924,-0.00386],"force_p95":1.04407,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.58972,"mean_force":0.23429,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.50862,0.06508,0.17282]},{"body_a":"world","body_b":"grasp_target","contact_count":149.0,"contact_point_centroid":[0.45909,-0.00015,-0.00114],"force_p95":0.57409,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.74592,"mean_force":0.10989,"phase_index":3.0,"phase_name":"lift_clear","phase_type":"lift","tcp_position_centroid":[0.44971,-0.00023,0.02286]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":18100.0,"contact_point_centroid":[0.4476,0.01889,0.0745],"force_p95":0.08284,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30454,"mean_force":0.05638,"phase_index":3.0,"phase_name":"lift_clear","phase_type":"lift","tcp_position_centroid":[0.44711,-0.00024,0.07267]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":19641.0,"contact_point_centroid":[0.44746,-0.01929,0.07289],"force_p95":0.08063,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27899,"mean_force":0.05256,"phase_index":3.0,"phase_name":"lift_clear","phase_type":"lift","tcp_position_centroid":[0.44713,-0.00024,0.07121]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":13090.0,"contact_point_centroid":[0.47904,0.01294,0.14216],"force_p95":0.1108,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27585,"mean_force":0.07491,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.47794,0.03183,0.14324]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":16.0,"contact_point_centroid":[0.51616,0.08029,0.15894],"force_p95":0.12042,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14677,"mean_force":0.05339,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.51381,0.06575,0.16503]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":76.0,"contact_point_centroid":[0.5135,0.08163,0.16086],"force_p95":0.07871,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14303,"mean_force":0.01633,"phase_index":5.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.51386,0.06559,0.16549]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":15086.0,"contact_point_centroid":[0.48108,0.05218,0.14312],"force_p95":0.09344,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14301,"mean_force":0.06552,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.47967,0.0335,0.1443]},{"body_a":"world","body_b":"grasp_target","contact_count":1488.0,"contact_point_centroid":[0.46286,-7e-05,-0.00191],"force_p95":0.13511,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12295,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.48189,-4e-05,0.24582]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.46283,-5e-05,-0.00201],"force_p95":0.12811,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13805,"mean_force":0.12419,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.45222,-0.0002,0.02239]},{"body_a":"world","body_b":"grasp_target","contact_count":3996.0,"contact_point_centroid":[0.46286,-7e-05,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.45971,-9e-05,0.10532]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4389.0,"contact_point_centroid":[0.45094,0.01906,0.02374],"force_p95":0.07357,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09364,"mean_force":0.0493,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.45114,-0.00021,0.02136]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5091.0,"contact_point_centroid":[0.45086,-0.01929,0.02329],"force_p95":0.06454,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08399,"mean_force":0.0427,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.45114,-0.00021,0.02136]}],"total_contact_groups":13},"final_pose_error":0.13678,"key_states":{"actual_goal_position":[0.61015,0.15287,0.12219],"final_object_position":[0.52503,0.09115,0.01599],"final_tcp_position":[0.51386,0.06573,0.16515],"realised_goal_position":[0.61015,0.15287,0.12219],"realised_object_initial_position":[0.46286,-7e-05,0.03]},"peak_contact_force":9760.30694,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":373.0,"n_steps_budget":1000.0,"object_pos_end":[0.46286,-7e-05,0.02602],"object_pos_start":[0.46286,-7e-05,0.03],"object_to_goal_dist_end":0.2331,"object_to_goal_dist_start":0.23148,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_above","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1488.0,"raw_peak_contact_force":0.13845,"subtask_id":"pre_grasp","tcp_end":[0.46413,-7e-05,0.18988],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.16386,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":999.0,"n_steps_budget":1000.0,"object_pos_end":[0.46286,-7e-05,0.02602],"object_pos_start":[0.46286,-7e-05,0.02602],"object_to_goal_dist_end":0.2331,"object_to_goal_dist_start":0.2331,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3996.0,"raw_peak_contact_force":0.12263,"subtask_id":"pre_grasp","tcp_end":[0.45851,-0.00012,0.02838],"tcp_start":[0.46413,-7e-05,0.18988],"tcp_to_object_dist_end":0.00495,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.46271,-5e-05,0.02593],"object_pos_start":[0.46286,-7e-05,0.02602],"object_to_goal_dist_end":0.23321,"object_to_goal_dist_start":0.2331,"object_z_max":0.02602,"peak_contact_force":0.1282,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11280.0,"raw_peak_contact_force":0.13805,"subtask_id":"pre_grasp","tcp_end":[0.45111,-0.00021,0.02133],"tcp_start":[0.45851,-0.00012,0.02838],"tcp_to_object_dist_end":0.01248,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":30.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.46403,-0.0002,0.12002],"object_pos_start":[0.46271,-5e-05,0.02593],"object_to_goal_dist_end":0.21163,"object_to_goal_dist_start":0.23321,"object_z_max":0.11995,"peak_contact_force":0.10022,"phase_name":"lift_clear","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":37890.0,"raw_peak_contact_force":0.74592,"subtask_id":"pre_grasp","tcp_end":[0.44716,-0.00023,0.12565],"tcp_start":[0.45111,-0.00021,0.02133],"tcp_to_object_dist_end":0.01779,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":12.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.52004,0.06728,0.13987],"object_pos_start":[0.46403,-0.0002,0.12002],"object_to_goal_dist_end":0.12553,"object_to_goal_dist_start":0.21163,"object_z_max":0.1425,"peak_contact_force":0.10124,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":28176.0,"raw_peak_contact_force":0.27585,"subtask_id":"transport_goal","tcp_end":[0.51381,0.0655,0.16558],"tcp_start":[0.44716,-0.00023,0.12565],"tcp_to_object_dist_end":0.02652,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":7.0,"n_steps":7.0,"n_steps_budget":1000.0,"object_pos_end":[0.52043,0.0688,0.13645],"object_pos_start":[0.52004,0.06728,0.13987],"object_to_goal_dist_end":0.12378,"object_to_goal_dist_start":0.12553,"object_z_max":0.13987,"peak_contact_force":9760.30694,"phase_name":"place_descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":76.0,"raw_peak_contact_force":0.14303,"subtask_id":"transport_goal","tcp_end":[0.51386,0.06573,0.16515],"tcp_start":[0.51381,0.0655,0.16558],"tcp_to_object_dist_end":0.0296,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.52503,0.09115,0.01599],"object_pos_start":[0.52043,0.0688,0.13645],"object_to_goal_dist_end":0.14945,"object_to_goal_dist_start":0.12378,"object_z_max":0.13645,"peak_contact_force":0.1238,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":498.0,"raw_peak_contact_force":1.58972,"tcp_end":[0.50827,0.06504,0.18955],"tcp_start":[0.51386,0.06573,0.16515],"tcp_to_object_dist_end":0.17631,"terminated_normally":true,"termination_reason":"step_budget"}],"success":false}]}
```