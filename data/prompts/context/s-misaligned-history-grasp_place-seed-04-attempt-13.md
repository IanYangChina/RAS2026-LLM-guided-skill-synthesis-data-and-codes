## Search State

- **Seed**: 4
- **Iteration**: 14 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 13 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | impedance_control | impedance_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 10  | 0.1491 | 0.20 | ❌ rejected |
| 12 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 5  | 0.0580 | 0.20 | ❌ rejected |
| 11 | push → align → release → insert → lift | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | impedance_control | position_control | admittance_control | impedance_control | position_control | time_limit | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 6  | 0.0580 | 0.20 | ❌ rejected |
| 10 | push → align → release → insert → lift | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | impedance_control | position_control | admittance_control | impedance_control | position_control | time_limit | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 6  | 0.0580 | 0.20 | ❌ rejected |
| 9 | push → align → release → insert → lift | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | impedance_control | position_control | admittance_control | impedance_control | position_control | time_limit | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 6  | -0.0408 | 0.35 | ✅ accepted |

**Proposal policy**: task_score is 0.35 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `1959b3932a54fd3d3850620783d44a63a35b8fa059f78d939fdbdef5fbfc64e8`
- Frozen object start: [0.5443056105572368, 0.0011327552814361583, 0.03]
- Frozen task target: [0.6476243705707704, 0.15808360238956023, 0.19110337479925443]
- Goal object position: (0.6476243705707704, 0.15808360238956023, 0.19110337479925443)
- place_goal_position (task success criterion — final object 3D position must be close to the realised airborne target here): (0.6476243705707704, 0.15808360238956023, 0.19110337479925443)
- Grasp/lift components are optimiser fitness diagnostics only; canonical task_score is final object-to-realised-target proximity.
- Object initial pose: (0.5443056105572368, 0.0011327552814361583, 0.03)
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
  frozen_object_start: [0.5443, 0.0011, 0.03]
  frozen_task_target: [0.6476, 0.1581, 0.1911]
  frozen_object_starts: {'grasp_target': [0.5443056105572368, 0.0011327552814361583, 0.03]}
  frozen_targets: {'place_target': [0.6476243705707704, 0.15808360238956023, 0.19110337479925443]}
  goal_tolerance_m: 0.02
  force_limit_n: 20
  force_scale_n: 5
  realized_scene_sha256: 1959b3932a54fd3d3850620783d44a63a35b8fa059f78d939fdbdef5fbfc64e8

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
| `object` | offset from object initial position (0.5443056105572368, 0.0011327552814361583, 0.03) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.6476243705707704, 0.15808360238956023, 0.19110337479925443) | final destination targets |
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

## Current Skill (Q=-0.041) — your mutation base

```yaml
skill: grasp_place
dsl_version: 2
skill_type: arm_gripper
subtasks:
- id: reach_object
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.15
  weight: 0.3
- id: grasp_object
  anchor: object
  weight: 0.2
- id: lift_object
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.15
  weight: 0.2
- id: transport_object
  offset:
  - 0.0
  - 0.0
  - 0.2
  weight: 0.2
- id: place_at_goal
  weight: 0.1
phases:
- id: approach_1
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    entity: grip_target
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.15
      axis: world_z
      mode: add_to_offset
      sign: positive
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    approach_height:
      type: scalar
      range:
      - 0.08
      - 0.3
      default: 0.15
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    approach_speed:
      type: scalar
      range:
      - 0.1
      - 0.5
      default: 0.3
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: reach_object
- id: descend_1
  type: descend
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    entity: grip_target
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.02
      axis: world_z
      mode: add_to_offset
      sign: positive
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    descend_speed:
      type: scalar
      range:
      - 0.05
      - 0.3
      default: 0.15
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: reach_object
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
    orientation:
      mode: keep_current
  subtask_id: grasp_object
- id: lift_1
  type: lift
  generator: linear_cartesian
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    entity: grip_target
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.15
      axis: world_z
      mode: add_to_offset
      sign: positive
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    lift_height:
      type: scalar
      range:
      - 0.05
      - 0.25
      default: 0.15
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    lift_speed:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.1
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: lift_object
- id: transport_1
  type: approach
  generator: linear_cartesian
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    entity: place_target
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.2
      axis: world_z
      mode: add_to_offset
      sign: positive
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    transport_height:
      type: scalar
      range:
      - 0.1
      - 0.3
      default: 0.2
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    transport_speed:
      type: scalar
      range:
      - 0.1
      - 0.4
      default: 0.25
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: transport_object
- id: descend_2
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
    - 0.01
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    place_descent_speed:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.1
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: place_at_goal
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
    orientation:
      mode: keep_current
  parameters:
    release_pause:
      type: scalar
      range:
      - 0.05
      - 0.3
      default: 0.15
      binds_to:
      - path: duration.max_time
        mode: replace
  subtask_id: place_at_goal
- id: retract_1
  type: retract
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
    offset_along_axis:
      distance: 0.3
      axis: world_z
      mode: add_to_offset
      sign: positive
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    retract_speed:
      type: scalar
      range:
      - 0.1
      - 0.4
      default: 0.25
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: place_at_goal

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, entity=grip_target, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=world_z, distance=0.15, mode=add_to_offset, sign=positive}, tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_height: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - approach_speed: status=consumed; consumers=generator.speed (replace)
- **descend_1** (`descend`)
  - target: source=yaml, anchor=task_object, entity=grip_target, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=world_z, distance=0.02, mode=add_to_offset, sign=positive}, tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - descend_speed: status=consumed; consumers=generator.speed (replace)
- **grasp_1** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings: none
- **lift_1** (`lift`)
  - target: source=yaml, anchor=task_object, entity=grip_target, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=world_z, distance=0.15, mode=add_to_offset, sign=positive}, tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - lift_speed: status=consumed; consumers=generator.speed (replace)
- **transport_1** (`approach`)
  - target: source=yaml, anchor=task_goal, entity=place_target, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=world_z, distance=0.2, mode=add_to_offset, sign=positive}, tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - transport_height: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - transport_speed: status=consumed; consumers=generator.speed (replace)
- **descend_2** (`descend`)
  - target: source=yaml, anchor=task_goal, entity=place_target, offset=[0.0, 0.0, 0.01], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - place_descent_speed: status=consumed; consumers=generator.speed (replace)
- **release_1** (`release`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings:
    - release_pause: status=consumed; consumers=duration.max_time (replace)
- **retract_1** (`retract`)
  - target: source=yaml, anchor=task_goal, entity=place_target, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=world_z, distance=0.3, mode=add_to_offset, sign=positive}, tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - retract_speed: status=consumed; consumers=generator.speed (replace)

## Design Metrics

- **Composite score**: -0.041
- **task_score** (E): 0.350
- **fitness_score**: 0.639  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.680

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.0528 |
| descend_1 | 1.00 | 1.00 | 0.2190 |
| grasp_1 | 1.00 | 1.00 | 0.0126 |
| lift_1 | 1.00 | 1.00 | 0.1237 |
| transport_1 | 1.00 | 1.00 | 0.2425 |
| descend_2 | 1.00 | 1.00 | 0.0997 |
| release_1 | 1.00 | 1.00 | 0.0203 |
| retract_1 | 1.00 | 1.00 | 0.2371 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.520, 0.006, 0.274) | (0.526, 0.005, 0.030)→(0.526, 0.005, 0.026) | 0.246→0.249 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.520, 0.006, 0.274)→(0.521, 0.005, 0.055) | (0.526, 0.005, 0.026)→(0.526, 0.005, 0.026) | 0.249→0.249 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_1 | grasp | 1.00 / step_budget | (0.521, 0.005, 0.055)→(0.513, 0.005, 0.045) | (0.526, 0.005, 0.026)→(0.526, 0.005, 0.026) | 0.249→0.249 | 1.00 / 44.000 | 0.136 | 0.173 |
| lift_1 | lift | 1.00 / step_budget | (0.513, 0.005, 0.045)→(0.521, 0.005, 0.168) | (0.526, 0.005, 0.026)→(0.532, 0.005, 0.145) | 0.249→0.215 | 1.00 / 33.000 | 0.086 | 0.414 |
| transport_1 | approach | 1.00 / step_budget | (0.521, 0.005, 0.168)→(0.605, 0.164, 0.300) | (0.532, 0.005, 0.145)→(0.591, 0.133, 0.069) | 0.215→0.165 | 1.00 / 14.333 | 91002.352 | 1.536 |
| descend_2 | descend | 1.00 / step_budget | (0.605, 0.164, 0.300)→(0.608, 0.172, 0.201) | (0.591, 0.133, 0.069)→(0.591, 0.137, 0.042) | 0.165→0.149 | 1.00 / 13.333 | 3249.652 | 0.169 |
| release_1 | release | 1.00 / step_budget | (0.608, 0.172, 0.201)→(0.602, 0.170, 0.220) | (0.591, 0.137, 0.042)→(0.587, 0.136, 0.019) | 0.149→0.171 | 1.00 / 4.000 | 0.125 | 0.449 |
| retract_1 | retract | 1.00 / step_budget | (0.602, 0.170, 0.220)→(0.613, 0.175, 0.457) | (0.587, 0.136, 0.019)→(0.587, 0.136, 0.019) | 0.171→0.171 | 1.00 / 4.000 | 0.123 | 0.126 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.564
- phase_score: 0.256
- phase_breakdown.transport_object_score: 0.119
- phase_breakdown.reach_object_score: 0.081
- phase_breakdown.grasp_object_score: 0.671
- phase_breakdown.place_at_goal_score: 0.004
- phase_breakdown.lift_object_score: 0.365
- grasp_place_fitness: 0.746

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.746
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.564
- **Median Q (composite search score)**: -0.075
- **K-run variance**: 0.0060
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.356


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `104d9d5641b6f93313b49acc931f841aa27a6ce63eca9eff4a16c33838e2c9c3`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.05,0.05],"goal_z_delta":0.15,"object_xy_delta":[0.05,0.05]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `9de75aa839370ff688dada9a37e29517e2f368ed4f09f6a013379103594581cf`; realized-scene SHA-256: `1959b3932a54fd3d3850620783d44a63a35b8fa059f78d939fdbdef5fbfc64e8`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.54431,0.00113,0.03]},{"name":"goal","value":[0.64762,0.15808,0.1911]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.54431,0.00113,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.64762,0.15808,0.1911]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":1.0,"average_failure_rate":0.00532,"average_mean_iterations":4.63298,"average_solve_count":188.0,"average_success_count":187.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.23334,"approach_1.approach_speed":0.43008,"descend_1.descend_speed":0.05164,"descend_2.place_descent_speed":0.14942,"lift_1.lift_height":0.13175,"lift_1.lift_speed":0.14212,"release_1.release_pause":0.20905,"retract_1.retract_speed":0.2575,"transport_1.transport_height":0.14559,"transport_1.transport_speed":0.29135},"optimized_scores":{"best_composite_score":-0.07544,"best_fitness_score":0.60456,"best_task_score":0.28005},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":1316.0,"contact_point_centroid":[0.60777,0.09321,-0.00283],"force_p95":0.39814,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.03779,"mean_force":0.15867,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.61818,0.11802,0.27855]},{"body_a":"world","body_b":"grasp_target","contact_count":80.0,"contact_point_centroid":[0.54244,0.00032,-0.00132],"force_p95":0.38762,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.41484,"mean_force":0.07622,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52947,0.00086,0.04558]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3667.0,"contact_point_centroid":[0.56464,0.05132,0.17463],"force_p95":0.12308,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.35294,"mean_force":0.07815,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.55843,0.03279,0.17368]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5042.0,"contact_point_centroid":[0.53491,-0.01812,0.08737],"force_p95":0.10623,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29196,"mean_force":0.06778,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.53229,0.00077,0.08544]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3218.0,"contact_point_centroid":[0.5631,0.01192,0.17264],"force_p95":0.14345,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28653,"mean_force":0.08613,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.55697,0.03059,0.17109]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5019.0,"contact_point_centroid":[0.53461,0.0197,0.08687],"force_p95":0.10761,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27542,"mean_force":0.06798,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.53223,0.00077,0.08474]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.5443,0.00103,-0.00203],"force_p95":0.13142,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.1475,"mean_force":0.12524,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53166,0.0009,0.04569]},{"body_a":"world","body_b":"grasp_target","contact_count":952.0,"contact_point_centroid":[0.54431,0.00113,-0.00186],"force_p95":0.13699,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12314,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51652,0.00045,0.28031]},{"body_a":"world","body_b":"grasp_target","contact_count":2696.0,"contact_point_centroid":[0.54431,0.00113,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.53545,0.00096,0.15761]},{"body_a":"world","body_b":"grasp_target","contact_count":1072.0,"contact_point_centroid":[0.60771,0.09326,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.64209,0.15324,0.26571]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.60771,0.09326,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.63975,0.15497,0.209]},{"body_a":"world","body_b":"grasp_target","contact_count":2248.0,"contact_point_centroid":[0.60771,0.09326,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":7.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.64195,0.15578,0.33744]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4119.0,"contact_point_centroid":[0.53125,-0.01832,0.04696],"force_p95":0.07619,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10402,"mean_force":0.05177,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53045,0.00088,0.04425]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4872.0,"contact_point_centroid":[0.53122,0.01996,0.04609],"force_p95":0.06822,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09353,"mean_force":0.04474,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53045,0.00088,0.04425]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1199.0,"contact_point_centroid":[0.62217,0.12306,0.28711],"force_p95":0.0123,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01588,"mean_force":0.01064,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.62175,0.12305,0.28478]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1145.0,"contact_point_centroid":[0.64245,0.15326,0.26765],"force_p95":0.01097,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01273,"mean_force":0.01043,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.6421,0.15325,0.26556]}],"total_contact_groups":17},"final_pose_error":0.03687,"key_states":{"actual_goal_position":[0.64762,0.15808,0.1911],"final_object_position":[0.60771,0.09326,0.01602],"final_tcp_position":[0.64864,0.15802,0.45425],"realised_goal_position":[0.64762,0.15808,0.1911],"realised_object_initial_position":[0.54431,0.00113,0.03]},"peak_contact_force":273006.8267,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":239.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.03],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.24751,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":952.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.5344,0.00091,0.26302],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.23721,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":674.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2696.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.53887,0.00104,0.05438],"tcp_start":[0.5344,0.00091,0.26302],"tcp_to_object_dist_end":0.02887,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54421,0.00078,0.02587],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25048,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.12992,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10791.0,"raw_peak_contact_force":0.1475,"subtask_id":"grasp_object","tcp_end":[0.53042,0.00088,0.04421],"tcp_start":[0.53887,0.00104,0.05438],"tcp_to_object_dist_end":0.02295,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":322.0,"n_steps_budget":600.0,"object_pos_end":[0.55401,0.00081,0.11607],"object_pos_start":[0.54421,0.00078,0.02587],"object_to_goal_dist_end":0.19782,"object_to_goal_dist_start":0.25048,"object_z_max":0.11582,"peak_contact_force":0.10518,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":10141.0,"raw_peak_contact_force":0.41484,"subtask_id":"lift_object","tcp_end":[0.53868,0.00072,0.13847],"tcp_start":[0.53042,0.00088,0.04421],"tcp_to_object_dist_end":0.02714,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":712.0,"n_steps_budget":1000.0,"object_pos_end":[0.60771,0.09326,0.01602],"object_pos_start":[0.55401,0.00081,0.11607],"object_to_goal_dist_end":0.19092,"object_to_goal_dist_start":0.19782,"object_z_max":0.18155,"peak_contact_force":273006.8267,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":9400.0,"raw_peak_contact_force":2.03779,"subtask_id":"transport_object","tcp_end":[0.64156,0.15093,0.31927],"tcp_start":[0.53868,0.00072,0.13847],"tcp_to_object_dist_end":0.31054,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":268.0,"n_steps_budget":1000.0,"object_pos_end":[0.60771,0.09326,0.01602],"object_pos_start":[0.60771,0.09326,0.01602],"object_to_goal_dist_end":0.19092,"object_to_goal_dist_start":0.19092,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2217.0,"raw_peak_contact_force":0.12263,"subtask_id":"place_at_goal","tcp_end":[0.64367,0.15608,0.21004],"tcp_start":[0.64156,0.15093,0.31927],"tcp_to_object_dist_end":0.20709,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.60771,0.09326,0.01602],"object_pos_start":[0.60771,0.09326,0.01602],"object_to_goal_dist_end":0.19092,"object_to_goal_dist_start":0.19092,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1018.0,"raw_peak_contact_force":0.12263,"subtask_id":"place_at_goal","tcp_end":[0.63842,0.15454,0.22815],"tcp_start":[0.64367,0.15608,0.21004],"tcp_to_object_dist_end":0.22293,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":562.0,"n_steps_budget":660.0,"object_pos_end":[0.60771,0.09326,0.01602],"object_pos_start":[0.60771,0.09326,0.01602],"object_to_goal_dist_end":0.19092,"object_to_goal_dist_start":0.19092,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2248.0,"raw_peak_contact_force":0.12263,"subtask_id":"place_at_goal","tcp_end":[0.64864,0.15802,0.45425],"tcp_start":[0.63842,0.15454,0.22815],"tcp_to_object_dist_end":0.44488,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `349f925163f8e9284ad51ad55d38356f2e3c8deb4dc54e8ff12260e5f6d4b0f8`; realized-scene SHA-256: `e32d7866764afb23ec7c7faebb4bcca0aa39fbf2f1ab61f3c9c527b297153af9`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.5305,0.03079,0.03]},{"name":"goal","value":[0.60153,0.17858,0.10809]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.5305,0.03079,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.60153,0.17858,0.10809]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.74359,"average_solve_count":195.0,"average_success_count":195.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.29819,"approach_1.approach_speed":0.42845,"descend_1.descend_speed":0.26205,"descend_2.place_descent_speed":0.1306,"lift_1.lift_height":0.22384,"lift_1.lift_speed":0.05057,"release_1.release_pause":0.17917,"retract_1.retract_speed":0.18754,"transport_1.transport_height":0.10041,"transport_1.transport_speed":0.23188},"optimized_scores":{"best_composite_score":0.0661,"best_fitness_score":0.7461,"best_task_score":0.56412},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":333.0,"contact_point_centroid":[0.5777,0.17124,-0.00378],"force_p95":0.60625,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.10132,"mean_force":0.20276,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.58879,0.17246,0.1327]},{"body_a":"world","body_b":"grasp_target","contact_count":91.0,"contact_point_centroid":[0.52701,0.02932,-0.00145],"force_p95":0.40819,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.42605,"mean_force":0.1336,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51614,0.0297,0.04602]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":820.0,"contact_point_centroid":[0.59217,0.19237,0.11653],"force_p95":0.09399,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31088,"mean_force":0.06494,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.5932,0.17393,0.12052]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":627.0,"contact_point_centroid":[0.59091,0.155,0.1177],"force_p95":0.12059,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30092,"mean_force":0.08176,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.59321,0.17393,0.12054]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":14037.0,"contact_point_centroid":[0.51984,0.04878,0.13433],"force_p95":0.07757,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28291,"mean_force":0.05208,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51954,0.02967,0.13226]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":12896.0,"contact_point_centroid":[0.51969,0.01051,0.13812],"force_p95":0.07965,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26427,"mean_force":0.05539,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.5198,0.02968,0.13609]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2871.0,"contact_point_centroid":[0.59175,0.18661,0.16076],"force_p95":0.13259,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2619,"mean_force":0.08343,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.59225,0.16817,0.16403]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2528.0,"contact_point_centroid":[0.59076,0.14922,0.16241],"force_p95":0.13989,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21931,"mean_force":0.08999,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.59219,0.16805,0.16489]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53052,0.0307,-0.00209],"force_p95":0.14689,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.20281,"mean_force":0.12926,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51831,0.02986,0.04617]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6858.0,"contact_point_centroid":[0.55705,0.11325,0.21559],"force_p95":0.08206,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17857,"mean_force":0.05262,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.55709,0.09424,0.21503]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6392.0,"contact_point_centroid":[0.55683,0.07505,0.2158],"force_p95":0.09274,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17851,"mean_force":0.05741,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.55709,0.0942,0.21508]},{"body_a":"world","body_b":"grasp_target","contact_count":1852.0,"contact_point_centroid":[0.5305,0.03079,-0.00192],"force_p95":0.13354,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12289,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51316,0.01549,0.3093]},{"body_a":"world","body_b":"grasp_target","contact_count":3212.0,"contact_point_centroid":[0.57738,0.17114,-0.00199],"force_p95":0.12329,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13242,"mean_force":0.12265,"phase_index":7.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.59285,0.17464,0.26581]},{"body_a":"world","body_b":"grasp_target","contact_count":2600.0,"contact_point_centroid":[0.5305,0.03079,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.52482,0.02923,0.18623]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4824.0,"contact_point_centroid":[0.51807,0.01054,0.04741],"force_p95":0.07024,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10667,"mean_force":0.04508,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51713,0.02978,0.0448]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5430.0,"contact_point_centroid":[0.51728,0.04901,0.04743],"force_p95":0.06706,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.06892,"mean_force":0.04092,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51713,0.02978,0.04481]}],"total_contact_groups":16},"final_pose_error":0.01977,"key_states":{"actual_goal_position":[0.60153,0.17858,0.10809],"final_object_position":[0.57738,0.17114,0.02602],"final_tcp_position":[0.60042,0.17788,0.38836],"realised_goal_position":[0.60153,0.17858,0.10809],"realised_object_initial_position":[0.5305,0.03079,0.03]},"peak_contact_force":1.10132,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":464.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.03],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18162,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1852.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.52576,0.02825,0.31978],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.29381,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":650.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2600.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.52542,0.03033,0.05448],"tcp_start":[0.52576,0.02825,0.31978],"tcp_to_object_dist_end":0.02891,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":46.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53044,0.03009,0.02568],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18411,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.14465,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12054.0,"raw_peak_contact_force":0.20281,"subtask_id":"grasp_object","tcp_end":[0.5171,0.02978,0.04477],"tcp_start":[0.52542,0.03033,0.05448],"tcp_to_object_dist_end":0.02329,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":38.0,"n_steps":679.0,"n_steps_budget":1000.0,"object_pos_end":[0.53355,0.03008,0.20594],"object_pos_start":[0.53044,0.03009,0.02568],"object_to_goal_dist_end":0.19039,"object_to_goal_dist_start":0.18411,"object_z_max":0.20569,"peak_contact_force":0.07613,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":27024.0,"raw_peak_contact_force":0.42605,"subtask_id":"lift_object","tcp_end":[0.52651,0.02985,0.23016],"tcp_start":[0.5171,0.02978,0.04477],"tcp_to_object_dist_end":0.02522,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":26.0,"n_steps":357.0,"n_steps_budget":1000.0,"object_pos_end":[0.59051,0.16273,0.17364],"object_pos_start":[0.53355,0.03008,0.20594],"object_to_goal_dist_end":0.06833,"object_to_goal_dist_start":0.19039,"object_z_max":0.20616,"peak_contact_force":0.10742,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":13250.0,"raw_peak_contact_force":0.17857,"subtask_id":"transport_object","tcp_end":[0.59118,0.16268,0.20321],"tcp_start":[0.52651,0.02985,0.23016],"tcp_to_object_dist_end":0.02958,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":24.0,"n_steps":227.0,"n_steps_budget":1000.0,"object_pos_end":[0.58971,0.17393,0.09355],"object_pos_start":[0.59051,0.16273,0.17364],"object_to_goal_dist_end":0.01931,"object_to_goal_dist_start":0.06833,"object_z_max":0.17364,"peak_contact_force":0.10793,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":5399.0,"raw_peak_contact_force":0.2619,"subtask_id":"place_at_goal","tcp_end":[0.5955,0.17451,0.12466],"tcp_start":[0.59118,0.16268,0.20321],"tcp_to_object_dist_end":0.03165,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.57709,0.1711,0.02635],"object_pos_start":[0.58971,0.17393,0.09355],"object_to_goal_dist_end":0.08564,"object_to_goal_dist_start":0.01931,"object_z_max":0.09355,"peak_contact_force":0.13108,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1780.0,"raw_peak_contact_force":1.10132,"subtask_id":"place_at_goal","tcp_end":[0.58866,0.17242,0.14486],"tcp_start":[0.5955,0.17451,0.12466],"tcp_to_object_dist_end":0.11908,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":803.0,"n_steps_budget":900.0,"object_pos_end":[0.57738,0.17114,0.02602],"object_pos_start":[0.57709,0.1711,0.02635],"object_to_goal_dist_end":0.08587,"object_to_goal_dist_start":0.08564,"object_z_max":0.02635,"peak_contact_force":0.12263,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3212.0,"raw_peak_contact_force":0.13242,"subtask_id":"place_at_goal","tcp_end":[0.60042,0.17788,0.38836],"tcp_start":[0.58866,0.17242,0.14486],"tcp_to_object_dist_end":0.36314,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `a1798e4fdcacfe8740623adfe3f78d2bc74e0d14c8233e64f02c40cf2a534ecc`; realized-scene SHA-256: `584133b5261cffac0dd4282704ff39e97bf4d452e60b02507679bbdea5a4de22`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50382,-0.01567,0.03]},{"name":"goal","value":[0.58691,0.18745,0.24812]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.50382,-0.01567,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.58691,0.18745,0.24812]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.14286,"average_solve_count":161.0,"average_success_count":161.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.19906,"approach_1.approach_speed":0.35509,"descend_1.descend_speed":0.17337,"descend_2.place_descent_speed":0.17475,"lift_1.lift_height":0.12967,"lift_1.lift_speed":0.05962,"release_1.release_pause":0.18992,"retract_1.retract_speed":0.1602,"transport_1.transport_height":0.14694,"transport_1.transport_speed":0.3012},"optimized_scores":{"best_composite_score":-0.11318,"best_fitness_score":0.56682,"best_task_score":0.20688},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":791.0,"contact_point_centroid":[0.57638,0.14412,-0.0037],"force_p95":0.77822,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.39044,"mean_force":0.1936,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.5726,0.15703,0.34934]},{"body_a":"world","body_b":"grasp_target","contact_count":84.0,"contact_point_centroid":[0.50192,-0.015,-0.00139],"force_p95":0.35564,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.40106,"mean_force":0.10117,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49019,-0.01527,0.04708]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":7086.0,"contact_point_centroid":[0.52415,0.02101,0.20227],"force_p95":0.11516,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.34295,"mean_force":0.07164,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.52005,0.03975,0.20181]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6961.0,"contact_point_centroid":[0.52559,0.06161,0.20589],"force_p95":0.10997,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27525,"mean_force":0.07374,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.52141,0.04283,0.20567]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6011.0,"contact_point_centroid":[0.49332,0.00395,0.09186],"force_p95":0.08313,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27494,"mean_force":0.05793,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49308,-0.01524,0.08956]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6855.0,"contact_point_centroid":[0.49343,-0.03434,0.09039],"force_p95":0.07865,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25632,"mean_force":0.05216,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49296,-0.01524,0.08839]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50382,-0.01562,-0.00204],"force_p95":0.13494,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.16956,"mean_force":0.12609,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49221,-0.01529,0.04717]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.50382,-0.01567,-0.00184],"force_p95":0.1373,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12324,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49947,-0.00585,0.2697]},{"body_a":"world","body_b":"grasp_target","contact_count":2036.0,"contact_point_centroid":[0.50382,-0.01567,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49852,-0.01392,0.14521]},{"body_a":"world","body_b":"grasp_target","contact_count":1136.0,"contact_point_centroid":[0.57625,0.14415,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.58301,0.18209,0.32338]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.57625,0.14415,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.58099,0.18427,0.26773]},{"body_a":"world","body_b":"grasp_target","contact_count":3124.0,"contact_point_centroid":[0.57625,0.14415,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":7.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.58315,0.18529,0.40623]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4605.0,"contact_point_centroid":[0.49204,0.00396,0.04867],"force_p95":0.06942,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09277,"mean_force":0.04719,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49107,-0.01528,0.04594]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5374.0,"contact_point_centroid":[0.49205,-0.03446,0.04835],"force_p95":0.06435,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08197,"mean_force":0.04098,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49107,-0.01528,0.04594]},{"body_a":"left_finger","body_b":"right_finger","contact_count":708.0,"contact_point_centroid":[0.57449,0.16052,0.35604],"force_p95":0.01264,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0161,"mean_force":0.01086,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.57418,0.16052,0.35372]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1215.0,"contact_point_centroid":[0.58347,0.1821,0.32582],"force_p95":0.01095,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01274,"mean_force":0.01042,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.58301,0.18208,0.32348]}],"total_contact_groups":17},"final_pose_error":0.01992,"key_states":{"actual_goal_position":[0.58691,0.18745,0.24812],"final_object_position":[0.57625,0.14415,0.01602],"final_tcp_position":[0.58868,0.18769,0.52827],"realised_goal_position":[0.58691,0.18745,0.24812],"realised_object_initial_position":[0.50382,-0.01567,0.03]},"peak_contact_force":9748.72547,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":201.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.03],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.30942,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":800.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.50025,-0.01251,0.23774],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.21177,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":509.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2036.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.49906,-0.01538,0.05467],"tcp_start":[0.50025,-0.01251,0.23774],"tcp_to_object_dist_end":0.02905,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":45.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50373,-0.01532,0.02583],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31217,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.13395,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11779.0,"raw_peak_contact_force":0.16956,"subtask_id":"grasp_object","tcp_end":[0.49104,-0.01528,0.04591],"tcp_start":[0.49906,-0.01538,0.05467],"tcp_to_object_dist_end":0.02376,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":38.0,"n_steps":323.0,"n_steps_budget":1000.0,"object_pos_end":[0.50837,-0.01532,0.11386],"object_pos_start":[0.50373,-0.01532,0.02583],"object_to_goal_dist_end":0.25555,"object_to_goal_dist_start":0.31217,"object_z_max":0.11361,"peak_contact_force":0.07786,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":12950.0,"raw_peak_contact_force":0.40106,"subtask_id":"lift_object","tcp_end":[0.49836,-0.01526,0.13651],"tcp_start":[0.49104,-0.01528,0.04591],"tcp_to_object_dist_end":0.02476,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":831.0,"n_steps_budget":1000.0,"object_pos_end":[0.57625,0.14415,0.01602],"object_pos_start":[0.50837,-0.01532,0.11386],"object_to_goal_dist_end":0.23634,"object_to_goal_dist_start":0.25555,"object_z_max":0.25424,"peak_contact_force":0.1226,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":15546.0,"raw_peak_contact_force":2.39044,"subtask_id":"transport_object","tcp_end":[0.58263,0.17932,0.37731],"tcp_start":[0.49836,-0.01526,0.13651],"tcp_to_object_dist_end":0.36305,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":284.0,"n_steps_budget":1000.0,"object_pos_end":[0.57625,0.14415,0.01602],"object_pos_start":[0.57625,0.14415,0.01602],"object_to_goal_dist_end":0.23634,"object_to_goal_dist_start":0.23634,"object_z_max":0.01602,"peak_contact_force":9748.72547,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2351.0,"raw_peak_contact_force":0.12263,"subtask_id":"place_at_goal","tcp_end":[0.58399,0.18538,0.26731],"tcp_start":[0.58263,0.17932,0.37731],"tcp_to_object_dist_end":0.25476,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.57625,0.14415,0.01602],"object_pos_start":[0.57625,0.14415,0.01602],"object_to_goal_dist_end":0.23634,"object_to_goal_dist_start":0.23634,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1014.0,"raw_peak_contact_force":0.12263,"subtask_id":"place_at_goal","tcp_end":[0.58005,0.18386,0.28751],"tcp_start":[0.58399,0.18538,0.26731],"tcp_to_object_dist_end":0.2744,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":781.0,"n_steps_budget":1000.0,"object_pos_end":[0.57625,0.14415,0.01602],"object_pos_start":[0.57625,0.14415,0.01602],"object_to_goal_dist_end":0.23634,"object_to_goal_dist_start":0.23634,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3124.0,"raw_peak_contact_force":0.12263,"subtask_id":"place_at_goal","tcp_end":[0.58868,0.18769,0.52827],"tcp_start":[0.58005,0.18386,0.28751],"tcp_to_object_dist_end":0.51425,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```