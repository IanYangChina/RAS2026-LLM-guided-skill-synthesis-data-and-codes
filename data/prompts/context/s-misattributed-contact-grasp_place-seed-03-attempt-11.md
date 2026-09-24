## Search State

- **Seed**: 3
- **Iteration**: 12 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 11 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 5 | 0.2545 | 0.43 | ✅ accepted |
| 10 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 5 | 0.2520 | 0.43 | ✅ accepted |
| 9 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 5 | 0.2299 | 0.37 | ❌ rejected |
| 8 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | impedance_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 5 | 0.2412 | 0.40 | ✅ accepted |
| 7 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 7 | 0.0806 | 0.27 | ❌ rejected |

**Proposal policy**: task_score is 0.43 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `5ce27bcdb8582e1d517b17df0f9c2ad7b05701113a75707627744a889253e6a7`
- Frozen object start: [0.45856491671436245, -0.02631894934039003, 0.03]
- Frozen task target: [0.6301274465206397, 0.20821620360643678, 0.11411929633605987]
- Goal object position: (0.6301274465206397, 0.20821620360643678, 0.11411929633605987)
- place_goal_position (task success criterion — final object 3D position must be close to the realised airborne target here): (0.6301274465206397, 0.20821620360643678, 0.11411929633605987)
- Grasp/lift components are optimiser fitness diagnostics only; canonical task_score is final object-to-realised-target proximity.
- Object initial pose: (0.45856491671436245, -0.02631894934039003, 0.03)
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
  frozen_object_start: [0.4586, -0.0263, 0.03]
  frozen_task_target: [0.6301, 0.2082, 0.1141]
  frozen_object_starts: {'grasp_target': [0.45856491671436245, -0.02631894934039003, 0.03]}
  frozen_targets: {'place_target': [0.6301274465206397, 0.20821620360643678, 0.11411929633605987]}
  goal_tolerance_m: 0.02
  force_limit_n: 20
  force_scale_n: 5
  realized_scene_sha256: 5ce27bcdb8582e1d517b17df0f9c2ad7b05701113a75707627744a889253e6a7

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
| `object` | offset from object initial position (0.45856491671436245, -0.02631894934039003, 0.03) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.6301274465206397, 0.20821620360643678, 0.11411929633605987) | final destination targets |
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

## Current Skill (Q=0.255) — your mutation base

```yaml
skill: grasp_place
dsl_version: 2
subtasks:
- id: reach_grasp
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.05
  weight: 0.3
- id: reach_goal
  weight: 0.7
phases:
- id: approach_grasp
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
    - 0.05
    orientation:
      mode: keep_current
  parameters:
    approach_speed:
      type: scalar
      range:
      - 0.1
      - 0.5
      default: 0.3
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: reach_grasp
- id: descend_to_grasp
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
    orientation:
      mode: keep_current
  parameters:
    descend_depth:
      type: scalar
      range:
      - -0.02
      - 0.02
      default: 0.0
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: reach_grasp
- id: grasp
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
  - id: grasp_check
    when: after_phase
    predicate: bilateral_grasp
    threshold: 0.05
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.0
    - 0.0
    - 0.005
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
      distance: 0.1
      axis: world_z
      mode: add_to_offset
      sign: positive
    orientation:
      mode: keep_current
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
  guards:
  - id: lift_check
    when: after_phase
    predicate: object_lifted
    threshold: 0.05
    on_failure: retry
  retries:
    max_attempts: 1
    strategy: repeat
- id: transport_approach
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
    - 0.1
    orientation:
      mode: keep_current
  parameters:
    transport_speed:
      type: scalar
      range:
      - 0.1
      - 0.5
      default: 0.2
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: transport_grasp_check
    when: during_phase
    predicate: bilateral_grasp
    threshold: 0.05
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.0
    - 0.0
    - 0.002
  subtask_id: reach_goal
- id: place_descend
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
    - 0.0
    orientation:
      mode: keep_current
  parameters:
    place_z_offset:
      type: scalar
      range:
      - -0.05
      - 0.05
      default: 0.0
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: reach_goal
- id: release
  type: release
  control: position_control
  termination: pose_tolerance
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
- id: retract
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
    - 0.0
    offset_along_axis:
      distance: 0.05
      axis: world_z
      mode: add_to_offset
      sign: positive
    orientation:
      mode: keep_current

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_grasp** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.05]
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (replace)
- **descend_to_grasp** (`descend`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings:
    - descend_depth: status=consumed; consumers=target.offset.z (replace)
- **grasp** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings: none
  - guards:
    - id=grasp_check, when=after_phase, predicate=bilateral_grasp, on_failure=retry, threshold=0.05
  - retries: max_attempts=2, strategy=offset_target, offset=[0.0, 0.0, 0.005]
- **lift_clear** (`lift`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=world_z, distance=0.1, mode=add_to_offset, sign=positive}
  - orientation: mode=keep_current
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset_along_axis.distance (replace)
  - guards:
    - id=lift_check, when=after_phase, predicate=object_lifted, on_failure=retry, threshold=0.05
  - retries: max_attempts=1, strategy=repeat
- **transport_approach** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.1]
  - orientation: mode=keep_current
  - parameter_bindings:
    - transport_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=transport_grasp_check, when=during_phase, predicate=bilateral_grasp, on_failure=retry, threshold=0.05
  - retries: max_attempts=2, strategy=offset_target, offset=[0.0, 0.0, 0.002]
- **place_descend** (`descend`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings:
    - place_z_offset: status=consumed; consumers=target.offset.z (replace)
- **release** (`release`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings: none
- **retract** (`retract`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=world_z, distance=0.05, mode=add_to_offset, sign=positive}
  - orientation: mode=keep_current
  - parameter_bindings: none

## Design Metrics

- **Composite score**: 0.255
- **task_score** (E): 0.429
- **fitness_score**: 0.685  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.430

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_grasp | 1.00 | 1.00 | 0.2170 |
| descend_to_grasp | 1.00 | 1.00 | 0.0422 |
| grasp | 1.00 | 1.00 | 0.0121 |
| lift_clear | 1.00 | 0.00 | 0.1051 |
| transport_approach | 0.00 | 1.00 | 0.0008 |
| place_descend | 0.67 | 1.00 | 0.0760 |
| release | 1.00 | 1.00 | 0.0213 |
| retract | 1.00 | 1.00 | 0.0380 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_grasp | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.506, 0.002, 0.088) | (0.511, 0.002, 0.030)→(0.511, 0.002, 0.026) | 0.244→0.246 | 1.00 / 4.000 | 0.123 | 0.123 |
| descend_to_grasp | descend | 1.00 / step_budget | (0.506, 0.002, 0.088)→(0.505, 0.002, 0.046) | (0.511, 0.002, 0.026)→(0.511, 0.002, 0.026) | 0.246→0.246 | 1.00 / 42.333 | 0.141 | 0.193 |
| grasp | grasp | 1.00 / step_budget | (0.505, 0.002, 0.046)→(0.497, 0.002, 0.037) | (0.511, 0.002, 0.026)→(0.511, 0.002, 0.026) | 0.246→0.246 | 1.00 / 26.000 | 0.099 | 0.553 |
| lift_clear | lift | 1.00 / step_budget | (0.497, 0.002, 0.037)→(0.493, 0.002, 0.142) | (0.511, 0.002, 0.026)→(0.508, 0.002, 0.122) | 0.246→0.221 | 0.00 / 0.000 | 0.000 | 0.294 |
| transport_approach | approach | 0.00 / guard_failure | (0.574, 0.117, 0.180)→(0.574, 0.118, 0.180) | (0.508, 0.002, 0.122)→(0.534, 0.057, 0.134) | 0.221→0.168 | 1.00 / 8.667 | 94251.503 | 1.585 |
| place_descend | descend | 0.67 / step_budget | (0.574, 0.118, 0.180)→(0.604, 0.159, 0.146) | (0.582, 0.123, 0.139)→(0.593, 0.149, 0.016) | 0.090→0.136 | 1.00 / 4.000 | 0.123 | 0.125 |
| release | release | 1.00 / step_budget | (0.604, 0.159, 0.146)→(0.598, 0.157, 0.166) | (0.593, 0.149, 0.016)→(0.593, 0.149, 0.016) | 0.136→0.136 | 1.00 / 4.000 | 0.123 | 0.123 |
| retract | retract | 1.00 / step_budget | (0.598, 0.157, 0.166)→(0.595, 0.156, 0.204) | (0.593, 0.149, 0.016)→(0.593, 0.149, 0.016) | 0.136→0.136 | 1.00 / 4.000 | 0.123 | 0.138 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.540
- phase_score: 0.460
- phase_breakdown.reach_grasp_score: 0.575
- phase_breakdown.reach_goal_score: 0.411
- grasp_place_fitness: 0.734

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.734
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.540
- **Median Q (composite search score)**: 0.294
- **K-run variance**: 0.0040
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.287


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `a4a71a7b2980790489e8194d1356bdee33fb951291c2e0792659ad3d3b3dc711`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.05,0.05],"goal_z_delta":0.15,"object_xy_delta":[0.05,0.05]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `8a78b0f0015ebaf8c4b14c8fbc8142d9b66e4b4efca10f362859101c0ae207df`; realized-scene SHA-256: `5ce27bcdb8582e1d517b17df0f9c2ad7b05701113a75707627744a889253e6a7`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.45856,-0.02632,0.03]},{"name":"goal","value":[0.63013,0.20822,0.11412]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.45856,-0.02632,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.63013,0.20822,0.11412]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.91603,"average_solve_count":131.0,"average_success_count":131.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_grasp.approach_speed":0.29329,"descend_to_grasp.descend_depth":0.0142,"lift_clear.lift_height":0.11849,"place_descend.place_z_offset":-0.00162,"transport_approach.transport_speed":0.29213},"optimized_scores":{"best_composite_score":0.29384,"best_fitness_score":0.72384,"best_task_score":0.51006},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":1323.0,"contact_point_centroid":[0.62282,0.18532,-0.00271],"force_p95":0.37874,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.73732,"mean_force":0.16016,"phase_index":5.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.60807,0.18612,0.14049]},{"body_a":"world","body_b":"grasp_target","contact_count":123.0,"contact_point_centroid":[0.45557,-0.02482,-0.00114],"force_p95":0.38697,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.46064,"mean_force":0.05902,"phase_index":3.0,"phase_name":"lift_clear","phase_type":"lift","tcp_position_centroid":[0.44549,-0.02535,0.04377]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":9083.0,"contact_point_centroid":[0.51128,0.03738,0.16708],"force_p95":0.14015,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32873,"mean_force":0.08172,"phase_index":4.0,"phase_name":"transport_approach","phase_type":"approach","tcp_position_centroid":[0.50548,0.05588,0.16732]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8450.0,"contact_point_centroid":[0.51205,0.07592,0.16723],"force_p95":0.12917,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31221,"mean_force":0.08763,"phase_index":4.0,"phase_name":"transport_approach","phase_type":"approach","tcp_position_centroid":[0.50668,0.05737,0.1677]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":10107.0,"contact_point_centroid":[0.44537,-0.0063,0.09103],"force_p95":0.10546,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28426,"mean_force":0.06645,"phase_index":3.0,"phase_name":"lift_clear","phase_type":"lift","tcp_position_centroid":[0.44311,-0.02525,0.08888]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":10882.0,"contact_point_centroid":[0.44543,-0.04411,0.08981],"force_p95":0.10019,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27804,"mean_force":0.06265,"phase_index":3.0,"phase_name":"lift_clear","phase_type":"lift","tcp_position_centroid":[0.4431,-0.02525,0.08823]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.45858,-0.02622,-0.00207],"force_p95":0.14446,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.20012,"mean_force":0.12847,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.44789,-0.02544,0.04299]},{"body_a":"world","body_b":"grasp_target","contact_count":2156.0,"contact_point_centroid":[0.45856,-0.02632,-0.00193],"force_p95":0.13209,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12285,"phase_index":0.0,"phase_name":"approach_grasp","phase_type":"approach","tcp_position_centroid":[0.47801,-0.01202,0.19471]},{"body_a":"world","body_b":"grasp_target","contact_count":580.0,"contact_point_centroid":[0.45856,-0.02632,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.45488,-0.025,0.06951]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.62296,0.18535,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.61707,0.20105,0.11026]},{"body_a":"world","body_b":"grasp_target","contact_count":1820.0,"contact_point_centroid":[0.62296,0.18535,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":7.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.61153,0.19905,0.14715]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4825.0,"contact_point_centroid":[0.44683,-0.00618,0.04428],"force_p95":0.06897,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10655,"mean_force":0.04493,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.44683,-0.0254,0.04197]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5181.0,"contact_point_centroid":[0.44668,-0.04463,0.04378],"force_p95":0.06781,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.06965,"mean_force":0.04286,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.44683,-0.0254,0.04197]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1134.0,"contact_point_centroid":[0.61117,0.18932,0.13671],"force_p95":0.01272,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01627,"mean_force":0.01083,"phase_index":5.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.61074,0.18931,0.13454]},{"body_a":"left_finger","body_b":"right_finger","contact_count":222.0,"contact_point_centroid":[0.62083,0.20227,0.10933],"force_p95":0.01096,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01098,"mean_force":0.01009,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.62031,0.20225,0.10697]}],"total_contact_groups":15},"final_pose_error":0.01346,"key_states":{"actual_goal_position":[0.63013,0.20822,0.11412],"final_object_position":[0.62296,0.18535,0.01602],"final_tcp_position":[0.61128,0.19894,0.16673],"realised_goal_position":[0.63013,0.20822,0.11412],"realised_object_initial_position":[0.45856,-0.02632,0.03]},"peak_contact_force":273007.45032,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":540.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.03],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30252,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_grasp","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":580.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_grasp","tcp_end":[0.45719,-0.02443,0.08962],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.06365,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":45.0,"n_steps":145.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.14147,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":11806.0,"raw_peak_contact_force":0.20012,"subtask_id":"reach_grasp","tcp_end":[0.45426,-0.02567,0.0492],"tcp_start":[0.45719,-0.02443,0.08962],"tcp_to_object_dist_end":0.02358,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":25.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.45849,-0.02563,0.02573],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30324,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.09846,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":21112.0,"raw_peak_contact_force":0.46064,"tcp_end":[0.4468,-0.0254,0.04194],"tcp_start":[0.45426,-0.02567,0.0492],"tcp_to_object_dist_end":0.01999,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":663.0,"n_steps_budget":750.0,"object_pos_end":[0.45566,-0.02518,0.12522],"object_pos_start":[0.45849,-0.02563,0.02573],"object_to_goal_dist_end":0.29161,"object_to_goal_dist_start":0.30324,"object_z_max":0.12511,"peak_contact_force":0.0,"phase_name":"lift_clear","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":17533.0,"raw_peak_contact_force":0.32873,"tcp_end":[0.44313,-0.02524,0.14936],"tcp_start":[0.4468,-0.0254,0.04194],"tcp_to_object_dist_end":0.0272,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":789.0,"n_steps_budget":1000.0,"object_pos_end":[0.45608,-0.02433,0.12501],"object_pos_start":[0.45566,-0.02518,0.12522],"object_to_goal_dist_end":0.29067,"object_to_goal_dist_start":0.29161,"object_z_max":0.15766,"peak_contact_force":273007.45032,"phase_name":"transport_approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2457.0,"raw_peak_contact_force":1.73732,"subtask_id":"reach_goal","tcp_end":[0.58954,0.16154,0.19369],"tcp_start":[0.58881,0.15972,0.19446],"tcp_to_object_dist_end":0.23891,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":400.0,"n_steps_budget":1000.0,"object_pos_end":[0.62296,0.18535,0.01602],"object_pos_start":[0.59945,0.16731,0.1507],"object_to_goal_dist_end":0.10099,"object_to_goal_dist_start":0.06287,"object_z_max":0.1507,"peak_contact_force":0.12263,"phase_name":"place_descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1022.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_goal","tcp_end":[0.62211,0.20269,0.11041],"tcp_start":[0.58954,0.16154,0.19369],"tcp_to_object_dist_end":0.09598,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.62296,0.18535,0.01602],"object_pos_start":[0.62296,0.18535,0.01602],"object_to_goal_dist_end":0.10099,"object_to_goal_dist_start":0.10099,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1820.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.61512,0.20032,0.12956],"tcp_start":[0.62211,0.20269,0.11041],"tcp_to_object_dist_end":0.11479,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":455.0,"n_steps_budget":600.0,"object_pos_end":[0.62296,0.18535,0.01602],"object_pos_start":[0.62296,0.18535,0.01602],"object_to_goal_dist_end":0.10099,"object_to_goal_dist_start":0.10099,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2156.0,"raw_peak_contact_force":0.13845,"tcp_end":[0.61128,0.19894,0.16673],"tcp_start":[0.61512,0.20032,0.12956],"tcp_to_object_dist_end":0.15178,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `aa6ec658384c70fac6b4eb656cc8c53536c3d5c760368ab2b384dccf294e2c48`; realized-scene SHA-256: `1959b3932a54fd3d3850620783d44a63a35b8fa059f78d939fdbdef5fbfc64e8`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.54431,0.00113,0.03]},{"name":"goal","value":[0.64762,0.15808,0.1911]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.54431,0.00113,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.64762,0.15808,0.1911]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.75652,"average_solve_count":115.0,"average_success_count":115.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_grasp.approach_speed":0.38269,"descend_to_grasp.descend_depth":0.00163,"lift_clear.lift_height":0.11569,"place_descend.place_z_offset":0.01535,"transport_approach.transport_speed":0.36514},"optimized_scores":{"best_composite_score":0.16554,"best_fitness_score":0.59554,"best_task_score":0.23854},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":3715.0,"contact_point_centroid":[0.55506,0.0742,-0.00222],"force_p95":0.12913,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.48586,"mean_force":0.13646,"phase_index":5.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.5744,0.07226,0.16431]},{"body_a":"world","body_b":"grasp_target","contact_count":145.0,"contact_point_centroid":[0.54125,0.00058,-0.00111],"force_p95":0.50831,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.75583,"mean_force":0.09911,"phase_index":3.0,"phase_name":"lift_clear","phase_type":"lift","tcp_position_centroid":[0.52758,0.00082,0.02671]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":9538.0,"contact_point_centroid":[0.528,-0.01801,0.07328],"force_p95":0.11077,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33624,"mean_force":0.07125,"phase_index":3.0,"phase_name":"lift_clear","phase_type":"lift","tcp_position_centroid":[0.52487,0.00078,0.07192]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":9673.0,"contact_point_centroid":[0.52844,0.01953,0.07201],"force_p95":0.10736,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31984,"mean_force":0.07064,"phase_index":3.0,"phase_name":"lift_clear","phase_type":"lift","tcp_position_centroid":[0.52491,0.00078,0.07049]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2384.0,"contact_point_centroid":[0.53756,0.03405,0.13586],"force_p95":0.16836,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30778,"mean_force":0.10311,"phase_index":4.0,"phase_name":"transport_approach","phase_type":"approach","tcp_position_centroid":[0.53398,0.01611,0.13947]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2081.0,"contact_point_centroid":[0.53645,-0.00367,0.13458],"force_p95":0.18874,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30721,"mean_force":0.107,"phase_index":4.0,"phase_name":"transport_approach","phase_type":"approach","tcp_position_centroid":[0.53285,0.01454,0.13803]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.54429,0.00098,-0.00203],"force_p95":0.13196,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.16101,"mean_force":0.12532,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.53051,0.00088,0.02648]},{"body_a":"world","body_b":"grasp_target","contact_count":2332.0,"contact_point_centroid":[0.54431,0.00113,-0.00194],"force_p95":0.13103,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12284,"phase_index":0.0,"phase_name":"approach_grasp","phase_type":"approach","tcp_position_centroid":[0.5174,0.00049,0.19249]},{"body_a":"world","body_b":"grasp_target","contact_count":684.0,"contact_point_centroid":[0.54431,0.00113,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.53637,0.00098,0.06073]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.55513,0.07437,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.59324,0.09962,0.17653]},{"body_a":"world","body_b":"grasp_target","contact_count":1820.0,"contact_point_centroid":[0.55513,0.07437,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":7.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.58864,0.09871,0.21489]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4114.0,"contact_point_centroid":[0.53048,-0.01835,0.02772],"force_p95":0.07606,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11184,"mean_force":0.05172,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.52926,0.00085,0.02505]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4879.0,"contact_point_centroid":[0.53039,0.01993,0.02684],"force_p95":0.0681,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09215,"mean_force":0.04479,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.52926,0.00085,0.02505]},{"body_a":"left_finger","body_b":"right_finger","contact_count":3747.0,"contact_point_centroid":[0.57618,0.07398,0.16713],"force_p95":0.01104,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01519,"mean_force":0.01051,"phase_index":5.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.57577,0.07397,0.16493]},{"body_a":"left_finger","body_b":"right_finger","contact_count":223.0,"contact_point_centroid":[0.59662,0.10019,0.1747],"force_p95":0.01092,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01094,"mean_force":0.01,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.596,0.10018,0.17248]}],"total_contact_groups":15},"final_pose_error":0.0122,"key_states":{"actual_goal_position":[0.64762,0.15808,0.1911],"final_object_position":[0.55513,0.07437,0.01602],"final_tcp_position":[0.58846,0.09866,0.23459],"realised_goal_position":[0.64762,0.15808,0.1911],"realised_object_initial_position":[0.54431,0.00113,0.03]},"peak_contact_force":1.48586,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":584.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.03],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.24751,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_grasp","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":684.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_grasp","tcp_end":[0.53706,0.00099,0.08675],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.06116,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":171.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.12984,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":10793.0,"raw_peak_contact_force":0.16101,"subtask_id":"reach_grasp","tcp_end":[0.53792,0.00101,0.03508],"tcp_start":[0.53706,0.00099,0.08675],"tcp_to_object_dist_end":0.01109,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":25.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54416,0.00072,0.02588],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25053,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.11153,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":19356.0,"raw_peak_contact_force":0.75583,"tcp_end":[0.52922,0.00085,0.02502],"tcp_start":[0.53792,0.00101,0.03508],"tcp_to_object_dist_end":0.01496,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":663.0,"n_steps_budget":750.0,"object_pos_end":[0.54285,0.00086,0.11649],"object_pos_start":[0.54416,0.00072,0.02588],"object_to_goal_dist_end":0.20313,"object_to_goal_dist_start":0.25053,"object_z_max":0.11639,"peak_contact_force":0.0,"phase_name":"lift_clear","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":4465.0,"raw_peak_contact_force":0.30778,"tcp_end":[0.52501,0.00079,0.12827],"tcp_start":[0.52922,0.00085,0.02502],"tcp_to_object_dist_end":0.02138,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":245.0,"n_steps_budget":1000.0,"object_pos_end":[0.55648,0.03602,0.12442],"object_pos_start":[0.54285,0.00086,0.11649],"object_to_goal_dist_end":0.16629,"object_to_goal_dist_start":0.20313,"object_z_max":0.1291,"peak_contact_force":0.12263,"phase_name":"transport_approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":7462.0,"raw_peak_contact_force":1.48586,"subtask_id":"reach_goal","tcp_end":[0.5465,0.03344,0.15536],"tcp_start":[0.54647,0.03334,0.15538],"tcp_to_object_dist_end":0.03261,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.55513,0.07437,0.01602],"object_pos_start":[0.55647,0.03866,0.12097],"object_to_goal_dist_end":0.21498,"object_to_goal_dist_start":0.1658,"object_z_max":0.12097,"peak_contact_force":0.12263,"phase_name":"place_descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1023.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_goal","tcp_end":[0.59737,0.10036,0.17518],"tcp_start":[0.5465,0.03344,0.15536],"tcp_to_object_dist_end":0.16671,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.55513,0.07437,0.01602],"object_pos_start":[0.55513,0.07437,0.01602],"object_to_goal_dist_end":0.21498,"object_to_goal_dist_start":0.21498,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1820.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.59164,0.09929,0.19636],"tcp_start":[0.59737,0.10036,0.17518],"tcp_to_object_dist_end":0.18568,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":455.0,"n_steps_budget":600.0,"object_pos_end":[0.55513,0.07437,0.01602],"object_pos_start":[0.55513,0.07437,0.01602],"object_to_goal_dist_end":0.21498,"object_to_goal_dist_start":0.21498,"object_z_max":0.01602,"peak_contact_force":0.12262,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2332.0,"raw_peak_contact_force":0.13845,"tcp_end":[0.58846,0.09866,0.23459],"tcp_start":[0.59164,0.09929,0.19636],"tcp_to_object_dist_end":0.22243,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `e1209649252ffcf03853fe0727696e22a1eda11729c6c1ae21659980557d7e98`; realized-scene SHA-256: `e32d7866764afb23ec7c7faebb4bcca0aa39fbf2f1ab61f3c9c527b297153af9`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.5305,0.03079,0.03]},{"name":"goal","value":[0.60153,0.17858,0.10809]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.5305,0.03079,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.60153,0.17858,0.10809]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.59848,"average_solve_count":132.0,"average_success_count":132.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_grasp.approach_speed":0.24302,"descend_to_grasp.descend_depth":0.01951,"lift_clear.lift_height":0.11663,"place_descend.place_z_offset":0.04138,"transport_approach.transport_speed":0.46918},"optimized_scores":{"best_composite_score":0.30423,"best_fitness_score":0.73423,"best_task_score":0.53964},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":365.0,"contact_point_centroid":[0.59958,0.18734,-0.00475],"force_p95":0.9507,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.53266,"mean_force":0.24014,"phase_index":5.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.59081,0.16801,0.16194]},{"body_a":"world","body_b":"grasp_target","contact_count":148.0,"contact_point_centroid":[0.52792,0.02873,-0.00121],"force_p95":0.30595,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.44264,"mean_force":0.07025,"phase_index":3.0,"phase_name":"lift_clear","phase_type":"lift","tcp_position_centroid":[0.51437,0.02921,0.04533]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":9757.0,"contact_point_centroid":[0.51538,0.0102,0.09341],"force_p95":0.10386,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30576,"mean_force":0.06881,"phase_index":3.0,"phase_name":"lift_clear","phase_type":"lift","tcp_position_centroid":[0.51184,0.02905,0.09107]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":10268.0,"contact_point_centroid":[0.51552,0.04788,0.09245],"force_p95":0.10239,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30072,"mean_force":0.06652,"phase_index":3.0,"phase_name":"lift_clear","phase_type":"lift","tcp_position_centroid":[0.51188,0.02905,0.09043]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":9726.0,"contact_point_centroid":[0.55041,0.07089,0.16507],"force_p95":0.13355,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24514,"mean_force":0.08987,"phase_index":4.0,"phase_name":"transport_approach","phase_type":"approach","tcp_position_centroid":[0.54502,0.08939,0.16627]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53055,0.03061,-0.00212],"force_p95":0.15734,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.21807,"mean_force":0.1319,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.5172,0.0294,0.04489]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":10349.0,"contact_point_centroid":[0.55135,0.10927,0.16551],"force_p95":0.12186,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20891,"mean_force":0.08485,"phase_index":4.0,"phase_name":"transport_approach","phase_type":"approach","tcp_position_centroid":[0.54592,0.09089,0.16684]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4167.0,"contact_point_centroid":[0.51698,0.01011,0.04632],"force_p95":0.08034,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14727,"mean_force":0.05094,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.51601,0.02932,0.04353]},{"body_a":"world","body_b":"grasp_target","contact_count":2300.0,"contact_point_centroid":[0.5305,0.03079,-0.00194],"force_p95":0.13153,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12284,"phase_index":0.0,"phase_name":"approach_grasp","phase_type":"approach","tcp_position_centroid":[0.51098,0.01417,0.19292]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.59946,0.18755,-0.00198],"force_p95":0.12611,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12831,"mean_force":0.12296,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.58942,0.17128,0.15222]},{"body_a":"world","body_b":"grasp_target","contact_count":476.0,"contact_point_centroid":[0.5305,0.03079,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.52337,0.02919,0.07029]},{"body_a":"world","body_b":"grasp_target","contact_count":1820.0,"contact_point_centroid":[0.59947,0.18755,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":7.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.58458,0.16971,0.1903]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4994.0,"contact_point_centroid":[0.51697,0.04848,0.04531],"force_p95":0.07333,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07537,"mean_force":0.04448,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.51602,0.02932,0.04353]},{"body_a":"left_finger","body_b":"right_finger","contact_count":109.0,"contact_point_centroid":[0.59349,0.17129,0.15672],"force_p95":0.01569,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01615,"mean_force":0.01273,"phase_index":5.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.59305,0.17126,0.15442]},{"body_a":"left_finger","body_b":"right_finger","contact_count":217.0,"contact_point_centroid":[0.59293,0.17227,0.15029],"force_p95":0.0114,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01272,"mean_force":0.01034,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.59224,0.17225,0.14823]}],"total_contact_groups":15},"final_pose_error":0.01251,"key_states":{"actual_goal_position":[0.60153,0.17858,0.10809],"final_object_position":[0.59947,0.18755,0.01602],"final_tcp_position":[0.58439,0.16963,0.20997],"realised_goal_position":[0.60153,0.17858,0.10809],"realised_object_initial_position":[0.5305,0.03079,0.03]},"peak_contact_force":9746.93612,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":576.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.03],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18162,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_grasp","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":476.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_grasp","tcp_end":[0.52411,0.02864,0.08733],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.06168,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":119.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.1514,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":10961.0,"raw_peak_contact_force":0.21807,"subtask_id":"reach_grasp","tcp_end":[0.52424,0.02985,0.0531],"tcp_start":[0.52411,0.02864,0.08733],"tcp_to_object_dist_end":0.02781,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":28.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53046,0.02962,0.02558],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18453,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.08677,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":20173.0,"raw_peak_contact_force":0.44264,"tcp_end":[0.51598,0.02932,0.04349],"tcp_start":[0.52424,0.02985,0.0531],"tcp_to_object_dist_end":0.02303,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":663.0,"n_steps_budget":750.0,"object_pos_end":[0.52472,0.02917,0.12292],"object_pos_start":[0.53046,0.02962,0.02558],"object_to_goal_dist_end":0.16865,"object_to_goal_dist_start":0.18453,"object_z_max":0.1228,"peak_contact_force":0.0,"phase_name":"lift_clear","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":20075.0,"raw_peak_contact_force":0.24514,"tcp_end":[0.512,0.02906,0.14785],"tcp_start":[0.51598,0.02932,0.04349],"tcp_to_object_dist_end":0.02799,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":963.0,"n_steps_budget":1000.0,"object_pos_end":[0.59023,0.16024,0.15114],"object_pos_start":[0.52472,0.02917,0.12292],"object_to_goal_dist_end":0.04814,"object_to_goal_dist_start":0.16865,"object_z_max":0.15274,"peak_contact_force":9746.93612,"phase_name":"transport_approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":474.0,"raw_peak_contact_force":1.53266,"subtask_id":"reach_goal","tcp_end":[0.58585,0.15815,0.19137],"tcp_start":[0.58591,0.1581,0.19151],"tcp_to_object_dist_end":0.04052,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":158.0,"n_steps_budget":1000.0,"object_pos_end":[0.59961,0.1876,0.01646],"object_pos_start":[0.59079,0.16425,0.14539],"object_to_goal_dist_end":0.09209,"object_to_goal_dist_start":0.04138,"object_z_max":0.14539,"peak_contact_force":0.12263,"phase_name":"place_descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1017.0,"raw_peak_contact_force":0.12831,"subtask_id":"reach_goal","tcp_end":[0.59397,0.17257,0.15154],"tcp_start":[0.58585,0.15815,0.19137],"tcp_to_object_dist_end":0.13603,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.59947,0.18755,0.01602],"object_pos_start":[0.59961,0.1876,0.01646],"object_to_goal_dist_end":0.09253,"object_to_goal_dist_start":0.09209,"object_z_max":0.01646,"peak_contact_force":0.12263,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1820.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.58775,0.17071,0.17197],"tcp_start":[0.59397,0.17257,0.15154],"tcp_to_object_dist_end":0.1573,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":455.0,"n_steps_budget":600.0,"object_pos_end":[0.59947,0.18755,0.01602],"object_pos_start":[0.59947,0.18755,0.01602],"object_to_goal_dist_end":0.09253,"object_to_goal_dist_start":0.09253,"object_z_max":0.01602,"peak_contact_force":0.12262,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2300.0,"raw_peak_contact_force":0.13845,"tcp_end":[0.58439,0.16963,0.20997],"tcp_start":[0.58775,0.17071,0.17197],"tcp_to_object_dist_end":0.19536,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```