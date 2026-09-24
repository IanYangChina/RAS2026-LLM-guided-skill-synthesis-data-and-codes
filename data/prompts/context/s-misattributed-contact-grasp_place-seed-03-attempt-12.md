## Search State

- **Seed**: 3
- **Iteration**: 13 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 12 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | impedance_control | impedance_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 5 | 0.1607 | 0.23 | ❌ rejected |
| 11 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 5 | 0.2545 | 0.43 | ✅ accepted |
| 10 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 5 | 0.2520 | 0.43 | ✅ accepted |
| 9 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 5 | 0.2299 | 0.37 | ❌ rejected |
| 8 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | impedance_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 5 | 0.2412 | 0.40 | ✅ accepted |

**Proposal policy**: task_score is 0.23 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.161) — your mutation base

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

- **Composite score**: 0.161
- **task_score** (E): 0.230
- **fitness_score**: 0.591  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.430

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_grasp | 1.00 | 1.00 | 0.2170 |
| descend_to_grasp | 1.00 | 1.00 | 0.0477 |
| grasp | 1.00 | 1.00 | 0.0121 |
| lift_clear | 1.00 | 1.00 | 0.1154 |
| transport_approach | 0.00 | 1.00 | 0.0978 |
| place_descend | 0.00 | 0.67 | 0.0805 |
| release | 1.00 | 0.67 | 0.0238 |
| retract | 1.00 | 1.00 | 0.0383 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_grasp | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.506, 0.002, 0.088) | (0.511, 0.002, 0.030)→(0.511, 0.002, 0.026) | 0.244→0.246 | 1.00 / 4.000 | 9.426 | 0.123 |
| descend_to_grasp | descend | 1.00 / step_budget | (0.506, 0.002, 0.088)→(0.505, 0.002, 0.040) | (0.511, 0.002, 0.026)→(0.511, 0.002, 0.026) | 0.246→0.246 | 1.00 / 42.667 | 0.140 | 0.197 |
| grasp | grasp | 1.00 / step_budget | (0.505, 0.002, 0.040)→(0.497, 0.002, 0.031) | (0.511, 0.002, 0.026)→(0.511, 0.002, 0.026) | 0.246→0.246 | 1.00 / 20.667 | 0.127 | 0.622 |
| lift_clear | lift | 1.00 / step_budget | (0.497, 0.002, 0.031)→(0.493, 0.002, 0.147) | (0.511, 0.002, 0.026)→(0.508, 0.002, 0.129) | 0.246→0.220 | 1.00 / 16.000 | 0.075 | 364.473 |
| transport_approach | approach | 0.00 / step_budget | (0.493, 0.002, 0.147)→(0.551, 0.068, 0.190) | (0.508, 0.002, 0.129)→(0.495, -0.034, -5.273) | 0.220→5.516 | 1.00 / 7.000 | 3246.884 | 245.347 |
| place_descend | descend | 0.00 / step_budget | (0.551, 0.068, 0.190)→(0.593, 0.134, 0.190) | (0.495, -0.034, -5.273)→(0.486, -0.027, -23.704) | 5.516→23.866 | 0.67 / 2.667 | 0.082 | 36.654 |
| release | release | 1.00 / step_budget | (0.593, 0.134, 0.190)→(0.589, 0.134, 0.213) | (0.486, -0.027, -23.704)→(0.480, -0.035, -28.946) | 23.866→29.108 | 0.67 / 2.667 | 0.082 | 0.082 |
| retract | retract | 1.00 / step_budget | (0.589, 0.134, 0.213)→(0.587, 0.133, 0.251) | (0.480, -0.035, -28.946)→(0.467, -0.053, -42.821) | 29.108→42.983 | 1.00 / 4.000 | 0.123 | 0.138 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.463
- phase_score: 0.371
- phase_breakdown.reach_grasp_score: 0.498
- phase_breakdown.reach_goal_score: 0.316
- grasp_place_fitness: 0.703

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.703
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.463
- **Median Q (composite search score)**: 0.158
- **K-run variance**: 0.0083
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.237


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.81395,"average_solve_count":129.0,"average_success_count":129.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_grasp.approach_speed":0.39193,"descend_to_grasp.descend_depth":-0.00161,"lift_clear.lift_height":0.14776,"place_descend.place_z_offset":0.04623,"transport_approach.transport_speed":0.4906},"optimized_scores":{"best_composite_score":0.05084,"best_fitness_score":0.48084,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":10,"reported_contact_groups":[{"body_a":"world","body_b":"hand","contact_count":50.0,"contact_point_centroid":[0.52977,-0.07059,-0.00479],"force_p95":997.24762,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1093.41884,"mean_force":263.7397,"phase_index":4.0,"phase_name":"transport_approach","phase_type":"approach","tcp_position_centroid":[0.48147,-0.02053,-0.01391]},{"body_a":"world","body_b":"link6","contact_count":633.0,"contact_point_centroid":[0.64495,0.11024,-0.00023],"force_p95":518.17533,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":743.98077,"mean_force":326.84826,"phase_index":4.0,"phase_name":"transport_approach","phase_type":"approach","tcp_position_centroid":[0.51616,0.07895,0.1953]},{"body_a":"world","body_b":"link5","contact_count":280.0,"contact_point_centroid":[0.56929,0.13675,-8e-05],"force_p95":200.40752,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":733.46884,"mean_force":141.22657,"phase_index":5.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.61795,0.19347,0.28845]},{"body_a":"world","body_b":"link6","contact_count":990.0,"contact_point_centroid":[0.65165,0.20172,-0.00025],"force_p95":461.00952,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":701.7495,"mean_force":320.54799,"phase_index":5.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.61869,0.18489,0.2907]},{"body_a":"world","body_b":"link5","contact_count":69.0,"contact_point_centroid":[0.51462,0.14782,-0.00018],"force_p95":464.48108,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":530.61939,"mean_force":325.29043,"phase_index":4.0,"phase_name":"transport_approach","phase_type":"approach","tcp_position_centroid":[0.54839,0.07748,0.27573]},{"body_a":"world","body_b":"link7","contact_count":114.0,"contact_point_centroid":[0.59073,-0.00462,-0.00019],"force_p95":337.15779,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":474.62892,"mean_force":226.51029,"phase_index":4.0,"phase_name":"transport_approach","phase_type":"approach","tcp_position_centroid":[0.466,-0.01335,0.01303]},{"body_a":"link5","body_b":"hand","contact_count":5.0,"contact_point_centroid":[0.47982,0.12482,0.19852],"force_p95":327.74559,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":333.07375,"mean_force":286.48917,"phase_index":4.0,"phase_name":"transport_approach","phase_type":"approach","tcp_position_centroid":[0.51639,0.02805,0.24195]},{"body_a":"world","body_b":"link6","contact_count":84.0,"contact_point_centroid":[0.67686,0.2229,-0.0001],"force_p95":66.63785,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":109.71618,"mean_force":46.27379,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.6312,0.19815,0.28916]},{"body_a":"world","body_b":"link5","contact_count":69.0,"contact_point_centroid":[0.58426,0.14188,-3e-05],"force_p95":32.27161,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":93.44788,"mean_force":16.08648,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.63118,0.19816,0.28913]},{"body_a":"world","body_b":"right_finger","contact_count":890.0,"contact_point_centroid":[0.48167,0.00081,-0.01029],"force_p95":11.54131,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":35.04949,"mean_force":4.1334,"phase_index":4.0,"phase_name":"transport_approach","phase_type":"approach","tcp_position_centroid":[0.48111,-0.02031,-0.00988]},{"body_a":"world","body_b":"left_finger","contact_count":908.0,"contact_point_centroid":[0.48544,-0.04106,-0.01012],"force_p95":11.61495,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":33.83732,"mean_force":4.1003,"phase_index":4.0,"phase_name":"transport_approach","phase_type":"approach","tcp_position_centroid":[0.48103,-0.02027,-0.00958]},{"body_a":"world","body_b":"grasp_target","contact_count":245.0,"contact_point_centroid":[0.50013,-0.02071,-0.02745],"force_p95":3.84744,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":5.00931,"mean_force":1.02556,"phase_index":4.0,"phase_name":"transport_approach","phase_type":"approach","tcp_position_centroid":[0.48425,-0.02074,-0.00664]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1166.0,"contact_point_centroid":[0.49337,-0.04124,0.06374],"force_p95":1.01142,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.83261,"mean_force":0.30227,"phase_index":4.0,"phase_name":"transport_approach","phase_type":"approach","tcp_position_centroid":[0.48904,-0.02302,0.06744]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":994.0,"contact_point_centroid":[0.49158,-0.00465,0.07878],"force_p95":0.83199,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.40395,"mean_force":0.28037,"phase_index":4.0,"phase_name":"transport_approach","phase_type":"approach","tcp_position_centroid":[0.48963,-0.02335,0.08292]},{"body_a":"grasp_target","body_b":"hand","contact_count":20.0,"contact_point_centroid":[0.52286,-0.0378,-0.00708],"force_p95":1.2435,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.28763,"mean_force":0.83176,"phase_index":4.0,"phase_name":"transport_approach","phase_type":"approach","tcp_position_centroid":[0.48429,-0.02098,-0.02312]},{"body_a":"world","body_b":"grasp_target","contact_count":121.0,"contact_point_centroid":[0.45524,-0.025,-0.00113],"force_p95":0.51651,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.69084,"mean_force":0.08107,"phase_index":3.0,"phase_name":"lift_clear","phase_type":"lift","tcp_position_centroid":[0.44517,-0.02547,0.02771]}],"total_contact_groups":26},"final_pose_error":0.01303,"key_states":{"actual_goal_position":[0.63013,0.20822,0.11412],"final_object_position":[0.27881,-0.334,-128.49457],"final_tcp_position":[0.63207,0.19765,0.35115],"realised_goal_position":[0.63013,0.20822,0.11412],"realised_object_initial_position":[0.45856,-0.02632,0.03]},"peak_contact_force":9740.40769,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":540.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.03],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30252,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_grasp","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":784.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_grasp","tcp_end":[0.45719,-0.02443,0.08962],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.06365,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":46.0,"n_steps":196.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.13966,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":12033.0,"raw_peak_contact_force":0.20823,"subtask_id":"reach_grasp","tcp_end":[0.45405,-0.02578,0.03311],"tcp_start":[0.45719,-0.02443,0.08962],"tcp_to_object_dist_end":0.00842,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":20.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.45844,-0.02558,0.02576],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30322,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.15924,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":24251.0,"raw_peak_contact_force":0.69084,"tcp_end":[0.44648,-0.02552,0.02592],"tcp_start":[0.45405,-0.02578,0.03311],"tcp_to_object_dist_end":0.01196,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":6.0,"n_steps":843.0,"n_steps_budget":930.0,"object_pos_end":[0.45806,-0.02515,0.14533],"object_pos_start":[0.45844,-0.02558,0.02576],"object_to_goal_dist_end":0.29161,"object_to_goal_dist_start":0.30322,"object_z_max":0.14525,"peak_contact_force":0.0,"phase_name":"lift_clear","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":8126.0,"raw_peak_contact_force":1093.41884,"tcp_end":[0.44289,-0.02535,0.16258],"tcp_start":[0.44648,-0.02552,0.02592],"tcp_to_object_dist_end":0.02298,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.41965,-0.13114,-16.05992],"object_pos_start":[0.45806,-0.02515,0.14533],"object_to_goal_dist_end":16.17897,"object_to_goal_dist_start":0.29161,"object_z_max":0.14536,"peak_contact_force":9740.40769,"phase_name":"transport_approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":5564.0,"raw_peak_contact_force":733.46884,"subtask_id":"reach_goal","tcp_end":[0.61467,0.17334,0.29343],"tcp_start":[0.44289,-0.02535,0.16258],"tcp_to_object_dist_end":16.35735,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.33455,-0.25371,-71.14516],"object_pos_start":[0.41965,-0.13114,-16.05992],"object_to_goal_dist_end":71.26139,"object_to_goal_dist_start":16.17897,"object_z_max":-16.05992,"peak_contact_force":0.0,"phase_name":"place_descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":375.0,"raw_peak_contact_force":109.71618,"subtask_id":"reach_goal","tcp_end":[0.63143,0.19789,0.28899],"tcp_start":[0.61467,0.17334,0.29343],"tcp_to_object_dist_end":71.4362,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.31753,-0.27823,-86.87101],"object_pos_start":[0.33455,-0.25371,-71.14516],"object_to_goal_dist_end":86.98705,"object_to_goal_dist_start":71.26139,"object_z_max":-71.14516,"peak_contact_force":0.0,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.63164,0.19782,0.31417],"tcp_start":[0.63143,0.19789,0.28899],"tcp_to_object_dist_end":87.18705,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":455.0,"n_steps_budget":600.0,"object_pos_end":[0.27881,-0.334,-128.49457],"object_pos_start":[0.31753,-0.27823,-86.87101],"object_to_goal_dist_end":128.61031,"object_to_goal_dist_start":86.98705,"object_z_max":-86.87101,"peak_contact_force":0.12263,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2156.0,"raw_peak_contact_force":0.13845,"tcp_end":[0.63207,0.19765,0.35115],"tcp_start":[0.63164,0.19782,0.31417],"tcp_to_object_dist_end":128.84729,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":20.0,"average_failure_rate":0.15504,"average_mean_iterations":34.12403,"average_solve_count":129.0,"average_success_count":109.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_grasp.approach_speed":0.29098,"descend_to_grasp.descend_depth":0.00819,"lift_clear.lift_height":0.12532,"place_descend.place_z_offset":0.012,"transport_approach.transport_speed":0.30215},"optimized_scores":{"best_composite_score":0.15806,"best_fitness_score":0.58806,"best_task_score":0.22689},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":2573.0,"contact_point_centroid":[0.55574,0.05571,-0.00231],"force_p95":0.13563,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.44527,"mean_force":0.14182,"phase_index":5.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.56263,0.05385,0.1575]},{"body_a":"world","body_b":"grasp_target","contact_count":145.0,"contact_point_centroid":[0.54143,0.00061,-0.00111],"force_p95":0.41883,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.64185,"mean_force":0.08782,"phase_index":3.0,"phase_name":"lift_clear","phase_type":"lift","tcp_position_centroid":[0.52755,0.00082,0.03333]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":9632.0,"contact_point_centroid":[0.52866,-0.01799,0.08287],"force_p95":0.11078,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.3303,"mean_force":0.07536,"phase_index":3.0,"phase_name":"lift_clear","phase_type":"lift","tcp_position_centroid":[0.5249,0.00078,0.08102]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":10019.0,"contact_point_centroid":[0.52879,0.01949,0.08172],"force_p95":0.10788,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31157,"mean_force":0.07297,"phase_index":3.0,"phase_name":"lift_clear","phase_type":"lift","tcp_position_centroid":[0.52493,0.00078,0.07996]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2073.0,"contact_point_centroid":[0.5376,-0.00371,0.1415],"force_p95":0.18156,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22088,"mean_force":0.11884,"phase_index":5.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.53272,0.01446,0.14485]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2703.0,"contact_point_centroid":[0.53762,0.03388,0.14123],"force_p95":0.14525,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19892,"mean_force":0.09447,"phase_index":5.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.53368,0.01595,0.1451]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.5443,0.00101,-0.00203],"force_p95":0.13231,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.15716,"mean_force":0.12539,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.53046,0.00088,0.03311]},{"body_a":"world","body_b":"grasp_target","contact_count":2332.0,"contact_point_centroid":[0.54431,0.00113,-0.00194],"force_p95":0.13103,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12284,"phase_index":0.0,"phase_name":"approach_grasp","phase_type":"approach","tcp_position_centroid":[0.5174,0.00049,0.19249]},{"body_a":"world","body_b":"grasp_target","contact_count":612.0,"contact_point_centroid":[0.54431,0.00113,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.53639,0.00099,0.06409]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.55581,0.05601,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.57441,0.07364,0.16668]},{"body_a":"world","body_b":"grasp_target","contact_count":1820.0,"contact_point_centroid":[0.55581,0.05601,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":7.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.56964,0.07292,0.20582]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4114.0,"contact_point_centroid":[0.53046,-0.01835,0.03435],"force_p95":0.07619,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11777,"mean_force":0.05178,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.52922,0.00086,0.03168]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4879.0,"contact_point_centroid":[0.53037,0.01993,0.03347],"force_p95":0.06825,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09079,"mean_force":0.04475,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.52922,0.00086,0.03168]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2488.0,"contact_point_centroid":[0.56457,0.05581,0.16047],"force_p95":0.01134,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01504,"mean_force":0.01057,"phase_index":5.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.56417,0.05581,0.15819]},{"body_a":"left_finger","body_b":"right_finger","contact_count":221.0,"contact_point_centroid":[0.57763,0.07413,0.16448],"force_p95":0.01091,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01093,"mean_force":0.01007,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.57726,0.07412,0.16222]}],"total_contact_groups":15},"final_pose_error":0.01172,"key_states":{"actual_goal_position":[0.64762,0.15808,0.1911],"final_object_position":[0.55581,0.05601,0.01602],"final_tcp_position":[0.56944,0.07288,0.22557],"realised_goal_position":[0.64762,0.15808,0.1911],"realised_object_initial_position":[0.54431,0.00113,0.03]},"peak_contact_force":1.44527,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":584.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.03],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.24751,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_grasp","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":612.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_grasp","tcp_end":[0.53706,0.00099,0.08675],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.06116,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":153.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.13033,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":10793.0,"raw_peak_contact_force":0.15716,"subtask_id":"reach_grasp","tcp_end":[0.53778,0.00101,0.0417],"tcp_start":[0.53706,0.00099,0.08675],"tcp_to_object_dist_end":0.01699,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":20.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54418,0.00074,0.02588],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25052,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.11563,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":19796.0,"raw_peak_contact_force":0.64185,"tcp_end":[0.52919,0.00086,0.03164],"tcp_start":[0.53778,0.00101,0.0417],"tcp_to_object_dist_end":0.01606,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":20.0,"n_steps":723.0,"n_steps_budget":810.0,"object_pos_end":[0.53989,0.0009,0.12758],"object_pos_start":[0.54418,0.00074,0.02588],"object_to_goal_dist_end":0.20087,"object_to_goal_dist_start":0.25052,"object_z_max":0.12748,"peak_contact_force":0.11582,"phase_name":"lift_clear","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.52512,0.00079,0.14449],"tcp_start":[0.52919,0.00086,0.03164],"tcp_to_object_dist_end":0.02245,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":0.0,"n_steps_budget":1000.0,"object_pos_end":[0.53989,0.0009,0.12758],"object_pos_start":[0.53989,0.0009,0.12758],"object_to_goal_dist_end":0.20087,"object_to_goal_dist_start":0.20087,"peak_contact_force":0.12263,"phase_name":"transport_approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":9837.0,"raw_peak_contact_force":1.44527,"subtask_id":"reach_goal","tcp_end":[0.52512,0.00079,0.14449],"tcp_start":[0.52512,0.00079,0.14449],"tcp_to_object_dist_end":0.02245,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.55581,0.05601,0.01602],"object_pos_start":[0.53989,0.0009,0.12758],"object_to_goal_dist_end":0.22249,"object_to_goal_dist_start":0.20087,"object_z_max":0.12762,"peak_contact_force":0.12263,"phase_name":"place_descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1021.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_goal","tcp_end":[0.5786,0.0741,0.16468],"tcp_start":[0.52512,0.00079,0.14449],"tcp_to_object_dist_end":0.15148,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.55581,0.05601,0.01602],"object_pos_start":[0.55581,0.05601,0.01602],"object_to_goal_dist_end":0.22249,"object_to_goal_dist_start":0.22249,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1820.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.57275,0.07337,0.1868],"tcp_start":[0.5786,0.0741,0.16468],"tcp_to_object_dist_end":0.1725,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":455.0,"n_steps_budget":600.0,"object_pos_end":[0.55581,0.05601,0.01602],"object_pos_start":[0.55581,0.05601,0.01602],"object_to_goal_dist_end":0.22249,"object_to_goal_dist_start":0.22249,"object_z_max":0.01602,"peak_contact_force":0.12262,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2332.0,"raw_peak_contact_force":0.13845,"tcp_end":[0.56944,0.07288,0.22557],"tcp_start":[0.57275,0.07337,0.1868],"tcp_to_object_dist_end":0.21067,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":20.0,"average_failure_rate":0.15504,"average_mean_iterations":34.12403,"average_solve_count":129.0,"average_success_count":109.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_grasp.approach_speed":0.3089,"descend_to_grasp.descend_depth":0.012,"lift_clear.lift_height":0.10898,"place_descend.place_z_offset":0.01053,"transport_approach.transport_speed":0.28028},"optimized_scores":{"best_composite_score":0.27333,"best_fitness_score":0.70333,"best_task_score":0.46308},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":1424.0,"contact_point_centroid":[0.56754,0.11755,-0.00245],"force_p95":0.2862,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.12565,"mean_force":0.14533,"phase_index":5.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.5605,0.11663,0.11742]},{"body_a":"world","body_b":"grasp_target","contact_count":143.0,"contact_point_centroid":[0.52759,0.02844,-0.0012],"force_p95":0.39671,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.53435,"mean_force":0.07929,"phase_index":3.0,"phase_name":"lift_clear","phase_type":"lift","tcp_position_centroid":[0.51432,0.02926,0.038]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8471.0,"contact_point_centroid":[0.51507,0.0103,0.08063],"force_p95":0.10908,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31898,"mean_force":0.07186,"phase_index":3.0,"phase_name":"lift_clear","phase_type":"lift","tcp_position_centroid":[0.51175,0.0291,0.07863]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8756.0,"contact_point_centroid":[0.5152,0.04788,0.07948],"force_p95":0.10496,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31445,"mean_force":0.07057,"phase_index":3.0,"phase_name":"lift_clear","phase_type":"lift","tcp_position_centroid":[0.5118,0.0291,0.07763]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4890.0,"contact_point_centroid":[0.53333,0.04338,0.12373],"force_p95":0.15928,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29467,"mean_force":0.10678,"phase_index":5.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.52793,0.06177,0.12416]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53055,0.03056,-0.00212],"force_p95":0.15805,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.22533,"mean_force":0.13198,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.51715,0.02945,0.03756]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5766.0,"contact_point_centroid":[0.5341,0.08045,0.12318],"force_p95":0.13702,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20581,"mean_force":0.09161,"phase_index":5.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.52827,0.06234,0.12409]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4077.0,"contact_point_centroid":[0.51701,0.01017,0.03893],"force_p95":0.08048,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14905,"mean_force":0.05185,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.51595,0.02938,0.03619]},{"body_a":"world","body_b":"grasp_target","contact_count":2300.0,"contact_point_centroid":[0.5305,0.03079,-0.00194],"force_p95":0.13153,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12284,"phase_index":0.0,"phase_name":"approach_grasp","phase_type":"approach","tcp_position_centroid":[0.51098,0.01417,0.19292]},{"body_a":"world","body_b":"grasp_target","contact_count":572.0,"contact_point_centroid":[0.5305,0.03079,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.52324,0.02922,0.06648]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.56779,0.11759,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.56462,0.13034,0.11778]},{"body_a":"world","body_b":"grasp_target","contact_count":1820.0,"contact_point_centroid":[0.56779,0.11759,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":7.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.55923,0.12902,0.15707]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4996.0,"contact_point_centroid":[0.51692,0.04853,0.03798],"force_p95":0.07319,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08147,"mean_force":0.04456,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.51596,0.02938,0.0362]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1161.0,"contact_point_centroid":[0.56325,0.12034,0.11932],"force_p95":0.01187,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01615,"mean_force":0.01063,"phase_index":5.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.56272,0.12032,0.117]},{"body_a":"left_finger","body_b":"right_finger","contact_count":223.0,"contact_point_centroid":[0.56819,0.13117,0.11552],"force_p95":0.01093,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01095,"mean_force":0.01,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.56774,0.13115,0.11319]}],"total_contact_groups":15},"final_pose_error":0.01179,"key_states":{"actual_goal_position":[0.60153,0.17858,0.10809],"final_object_position":[0.56779,0.11759,0.01602],"final_tcp_position":[0.55897,0.12895,0.17683],"realised_goal_position":[0.60153,0.17858,0.10809],"realised_object_initial_position":[0.5305,0.03079,0.03]},"peak_contact_force":28.03421,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":576.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.03],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18162,"object_z_max":0.03,"peak_contact_force":28.03421,"phase_name":"approach_grasp","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":572.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_grasp","tcp_end":[0.52411,0.02864,0.08733],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.06168,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":143.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.15121,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":10873.0,"raw_peak_contact_force":0.22533,"subtask_id":"reach_grasp","tcp_end":[0.52428,0.02992,0.04576],"tcp_start":[0.52411,0.02864,0.08733],"tcp_to_object_dist_end":0.02071,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":22.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53043,0.02953,0.02559],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.1846,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.10759,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":17370.0,"raw_peak_contact_force":0.53435,"tcp_end":[0.51592,0.02937,0.03616],"tcp_start":[0.52428,0.02992,0.04576],"tcp_to_object_dist_end":0.01796,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":22.0,"n_steps":603.0,"n_steps_budget":690.0,"object_pos_end":[0.52562,0.02921,0.11371],"object_pos_start":[0.53043,0.02953,0.02559],"object_to_goal_dist_end":0.16765,"object_to_goal_dist_start":0.1846,"object_z_max":0.1136,"peak_contact_force":0.10787,"phase_name":"lift_clear","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.51182,0.02911,0.13278],"tcp_start":[0.51592,0.02937,0.03616],"tcp_to_object_dist_end":0.02354,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":0.0,"n_steps_budget":1000.0,"object_pos_end":[0.52562,0.02921,0.11371],"object_pos_start":[0.52562,0.02921,0.11371],"object_to_goal_dist_end":0.16765,"object_to_goal_dist_start":0.16765,"peak_contact_force":0.12263,"phase_name":"transport_approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":13241.0,"raw_peak_contact_force":1.12565,"subtask_id":"reach_goal","tcp_end":[0.51182,0.02911,0.13278],"tcp_start":[0.51182,0.02911,0.13278],"tcp_to_object_dist_end":0.02354,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.56779,0.11759,0.01602],"object_pos_start":[0.52562,0.02921,0.11371],"object_to_goal_dist_end":0.11548,"object_to_goal_dist_start":0.16765,"object_z_max":0.11375,"peak_contact_force":0.12263,"phase_name":"place_descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1023.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_goal","tcp_end":[0.56934,0.13138,0.11574],"tcp_start":[0.51182,0.02911,0.13278],"tcp_to_object_dist_end":0.10068,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.56779,0.11759,0.01602],"object_pos_start":[0.56779,0.11759,0.01602],"object_to_goal_dist_end":0.11548,"object_to_goal_dist_start":0.11548,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1820.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.56274,0.12986,0.13797],"tcp_start":[0.56934,0.13138,0.11574],"tcp_to_object_dist_end":0.12267,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":455.0,"n_steps_budget":600.0,"object_pos_end":[0.56779,0.11759,0.01602],"object_pos_start":[0.56779,0.11759,0.01602],"object_to_goal_dist_end":0.11548,"object_to_goal_dist_start":0.11548,"object_z_max":0.01602,"peak_contact_force":0.12262,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2300.0,"raw_peak_contact_force":0.13845,"tcp_end":[0.55897,0.12895,0.17683],"tcp_start":[0.56274,0.12986,0.13797],"tcp_to_object_dist_end":0.16146,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```