## Search State

- **Seed**: 4
- **Iteration**: 2 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 1 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 14 | -0.2274 | 0.36 | ✅ accepted |
| 0 | push → align → release → insert → lift | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | impedance_control | position_control | admittance_control | impedance_control | position_control | time_limit | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 6 | 0.0580 | 0.20 | ✅ accepted |

**Proposal policy**: task_score is 0.36 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=-0.227) — your mutation base

```yaml
skill: grasp_place
dsl_version: 2
skill_type: arm_gripper
subtasks:
- id: reach_pre_grasp
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.1
  weight: 0.2
- id: grasp_at_object
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.03
  weight: 0.3
- id: lift_clearance
  anchor: object
  target_entity: object
  offset:
  - 0.0
  - 0.0
  - 0.15
  weight: 0.2
- id: approach_goal
  offset:
  - 0.0
  - 0.0
  - 0.1
  weight: 0.1
- id: place_at_goal
  target_entity: object
  weight: 0.2
phases:
- id: approach_object
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
    - 0.1
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
    approach_height:
      type: scalar
      range:
      - 0.05
      - 0.15
      default: 0.1
      binds_to:
      - path: target.offset.z
        mode: replace
    speed:
      type: scalar
      range:
      - 0.05
      - 0.5
      default: 0.2
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: reach_pre_grasp
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
    - 0.03
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
    descend_z:
      type: scalar
      range:
      - 0.02
      - 0.05
      default: 0.03
      binds_to:
      - path: target.offset.z
        mode: replace
    lateral_offset_x:
      type: scalar
      range:
      - -0.02
      - 0.02
      default: 0.0
      binds_to:
      - path: target.offset.x
        mode: add
    lateral_offset_y:
      type: scalar
      range:
      - -0.02
      - 0.02
      default: 0.0
      binds_to:
      - path: target.offset.y
        mode: add
    speed:
      type: scalar
      range:
      - 0.05
      - 0.5
      default: 0.1
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: grasp_at_object
- id: grasp
  type: grasp
  control: position_control
  termination: grasp_success
  end_effector_action: force_grasp
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.0
    - 0.03
    tolerance: 0.02
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - -1.0
      align_with: world_z
      tolerance: 0.1
  guards:
  - id: grasp_guard
    when: after_phase
    predicate: bilateral_grasp
    threshold: 0.5
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: repeat
  subtask_id: grasp_at_object
- id: lift
  type: lift
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.0
    - 0.2
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
    lift_height:
      type: scalar
      range:
      - 0.1
      - 0.3
      default: 0.2
      binds_to:
      - path: target.offset.z
        mode: replace
    speed:
      type: scalar
      range:
      - 0.05
      - 0.5
      default: 0.15
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: lifted_guard
    when: after_phase
    predicate: object_lifted
    threshold: 0.02
    on_failure: retry
  retries:
    max_attempts: 1
    strategy: repeat
  subtask_id: lift_clearance
- id: approach_goal
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
    approach_goal_height:
      type: scalar
      range:
      - 0.05
      - 0.15
      default: 0.1
      binds_to:
      - path: target.offset.z
        mode: replace
    speed:
      type: scalar
      range:
      - 0.05
      - 0.5
      default: 0.2
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: approach_goal
- id: descend_to_place
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
    place_z:
      type: scalar
      range:
      - -0.02
      - 0.02
      default: 0.0
      binds_to:
      - path: target.offset.z
        mode: replace
    speed:
      type: scalar
      range:
      - 0.05
      - 0.5
      default: 0.1
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: place_at_goal
- id: release
  type: release
  control: position_control
  termination: pose_tolerance
  end_effector_action: open
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.0
    tolerance: 0.02
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - -1.0
      align_with: world_z
      tolerance: 0.1
  subtask_id: place_at_goal
- id: retract
  type: retract
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
    retract_height:
      type: scalar
      range:
      - 0.05
      - 0.15
      default: 0.1
      binds_to:
      - path: target.offset.z
        mode: replace
    speed:
      type: scalar
      range:
      - 0.05
      - 0.5
      default: 0.2
      binds_to:
      - path: generator.speed
        mode: replace

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_object** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.1], tolerance=0.01
  - orientation: mode=align_axis, axis=[0.0, 0.0, -1.0], align_with=world_z, tolerance=0.1
  - parameter_bindings:
    - approach_height: status=consumed; consumers=target.offset.z (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
- **descend_to_grasp** (`descend`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.03], tolerance=0.01
  - orientation: mode=align_axis, axis=[0.0, 0.0, -1.0], align_with=world_z, tolerance=0.1
  - parameter_bindings:
    - descend_z: status=consumed; consumers=target.offset.z (replace)
    - lateral_offset_x: status=consumed; consumers=target.offset.x (add)
    - lateral_offset_y: status=consumed; consumers=target.offset.y (add)
    - speed: status=consumed; consumers=generator.speed (replace)
- **grasp** (`grasp`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.03], tolerance=0.02
  - orientation: mode=align_axis, axis=[0.0, 0.0, -1.0], align_with=world_z, tolerance=0.1
  - parameter_bindings: none
  - guards:
    - id=grasp_guard, when=after_phase, predicate=bilateral_grasp, on_failure=retry, threshold=0.5
  - retries: max_attempts=2, strategy=repeat
- **lift** (`lift`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.2], tolerance=0.02
  - orientation: mode=align_axis, axis=[0.0, 0.0, -1.0], align_with=world_z, tolerance=0.1
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset.z (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=lifted_guard, when=after_phase, predicate=object_lifted, on_failure=retry, threshold=0.02
  - retries: max_attempts=1, strategy=repeat
- **approach_goal** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.1], tolerance=0.01
  - orientation: mode=align_axis, axis=[0.0, 0.0, -1.0], align_with=world_z, tolerance=0.1
  - parameter_bindings:
    - approach_goal_height: status=consumed; consumers=target.offset.z (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
- **descend_to_place** (`descend`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], tolerance=0.01
  - orientation: mode=align_axis, axis=[0.0, 0.0, -1.0], align_with=world_z, tolerance=0.1
  - parameter_bindings:
    - place_z: status=consumed; consumers=target.offset.z (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
- **release** (`release`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], tolerance=0.02
  - orientation: mode=align_axis, axis=[0.0, 0.0, -1.0], align_with=world_z, tolerance=0.1
  - parameter_bindings: none
- **retract** (`retract`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.1], tolerance=0.02
  - orientation: mode=align_axis, axis=[0.0, 0.0, -1.0], align_with=world_z, tolerance=0.1
  - parameter_bindings:
    - retract_height: status=consumed; consumers=target.offset.z (replace)
    - speed: status=consumed; consumers=generator.speed (replace)

## Design Metrics

- **Composite score**: -0.227
- **task_score** (E): 0.362
- **fitness_score**: 0.653  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.880

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_object | 1.00 | 1.00 | 0.1641 |
| descend_to_grasp | 1.00 | 1.00 | 0.0880 |
| grasp | 1.00 | 1.00 | 0.0127 |
| lift | 1.00 | 1.00 | 0.1251 |
| approach_goal | 0.67 | 1.00 | 0.1856 |
| descend_to_place | 1.00 | 1.00 | 0.0667 |
| release | 1.00 | 1.00 | 0.0209 |
| retract | 1.00 | 1.00 | 0.0647 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.520, 0.005, 0.140) | (0.526, 0.005, 0.030)→(0.526, 0.005, 0.026) | 0.246→0.249 | 1.00 / 4.000 | 10.215 | 0.138 |
| descend_to_grasp | descend | 1.00 / step_budget | (0.520, 0.005, 0.140)→(0.534, 0.006, 0.053) | (0.526, 0.005, 0.026)→(0.526, 0.005, 0.026) | 0.249→0.249 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp | grasp | 1.00 / step_budget | (0.534, 0.006, 0.053)→(0.526, 0.006, 0.043) | (0.526, 0.005, 0.026)→(0.526, 0.006, 0.026) | 0.249→0.249 | 1.00 / 44.667 | 0.148 | 0.189 |
| lift | lift | 1.00 / step_budget | (0.526, 0.006, 0.043)→(0.523, 0.006, 0.168) | (0.526, 0.006, 0.026)→(0.532, 0.006, 0.148) | 0.249→0.195 | 1.00 / 40.000 | 0.075 | 0.592 |
| approach_goal | approach | 0.67 / step_budget | (0.523, 0.006, 0.168)→(0.597, 0.149, 0.255) | (0.532, 0.006, 0.148)→(0.605, 0.151, 0.128) | 0.195→0.120 | 1.00 / 19.333 | 0.188 | 0.817 |
| descend_to_place | descend | 1.00 / step_budget | (0.597, 0.149, 0.255)→(0.606, 0.169, 0.193) | (0.605, 0.151, 0.128)→(0.607, 0.162, 0.087) | 0.120→0.097 | 1.00 / 20.000 | 91003.378 | 0.273 |
| release | release | 1.00 / step_budget | (0.606, 0.169, 0.193)→(0.600, 0.167, 0.213) | (0.607, 0.162, 0.087)→(0.601, 0.165, 0.019) | 0.097→0.166 | 1.00 / 4.000 | 0.114 | 0.922 |
| retract | retract | 1.00 / step_budget | (0.600, 0.167, 0.213)→(0.608, 0.173, 0.277) | (0.601, 0.165, 0.019)→(0.601, 0.165, 0.019) | 0.166→0.165 | 1.00 / 4.000 | 0.123 | 0.127 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: 1.000
- terminal_score: 0.564
- phase_score: 0.586
- phase_breakdown.approach_goal_score: 0.438
- phase_breakdown.place_at_goal_score: 0.569
- phase_breakdown.grasp_at_object_score: 0.716
- phase_breakdown.reach_pre_grasp_score: 0.595
- phase_breakdown.lift_clearance_score: 0.471
- grasp_place_fitness: 0.755

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.755
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.564
- **Median Q (composite search score)**: -0.252
- **K-run variance**: 0.0057
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.327


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.98113,"average_solve_count":159.0,"average_success_count":159.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.approach_goal_height":0.09925,"approach_goal.speed":0.2671,"approach_object.approach_height":0.08011,"approach_object.speed":0.06749,"descend_to_grasp.descend_z":0.02207,"descend_to_grasp.lateral_offset_x":0.01922,"descend_to_grasp.lateral_offset_y":0.00394,"descend_to_grasp.speed":0.41135,"descend_to_place.place_z":0.00284,"descend_to_place.speed":0.25379,"lift.lift_height":0.1757,"lift.speed":0.32349,"retract.retract_height":0.12708,"retract.speed":0.45422},"optimized_scores":{"best_composite_score":-0.25179,"best_fitness_score":0.62821,"best_task_score":0.31044},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":195.0,"contact_point_centroid":[0.63514,0.16577,-0.00679],"force_p95":1.24928,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.80229,"mean_force":0.38576,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.63606,0.15233,0.21128]},{"body_a":"world","body_b":"grasp_target","contact_count":93.0,"contact_point_centroid":[0.54046,0.00389,-0.00166],"force_p95":0.50458,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.66108,"mean_force":0.10618,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.5448,0.00407,0.04413]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8670.0,"contact_point_centroid":[0.54159,-0.01541,0.11405],"force_p95":0.07842,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.38013,"mean_force":0.05116,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.5416,0.00364,0.11183]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":7539.0,"contact_point_centroid":[0.54205,0.02289,0.11088],"force_p95":0.08301,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.36311,"mean_force":0.05663,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.54168,0.00366,0.10818]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":596.0,"contact_point_centroid":[0.63673,0.17271,0.19081],"force_p95":0.16852,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.36071,"mean_force":0.11223,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.63943,0.15339,0.19526]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2285.0,"contact_point_centroid":[0.63709,0.16601,0.23129],"force_p95":0.13936,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27349,"mean_force":0.08995,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.63713,0.14739,0.23489]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":874.0,"contact_point_centroid":[0.63817,0.13525,0.19207],"force_p95":0.08516,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26395,"mean_force":0.05624,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.63971,0.15348,0.19581]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.54426,0.00136,-0.00228],"force_p95":0.19224,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.25195,"mean_force":0.14277,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.54753,0.00417,0.04352]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2539.0,"contact_point_centroid":[0.63732,0.12903,0.22997],"force_p95":0.13898,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24005,"mean_force":0.08206,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.6373,0.14764,0.23352]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":15924.0,"contact_point_centroid":[0.58414,0.08865,0.22101],"force_p95":0.09837,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22327,"mean_force":0.06305,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.58391,0.06959,0.22116]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":18259.0,"contact_point_centroid":[0.5829,0.04957,0.22064],"force_p95":0.09246,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22218,"mean_force":0.05435,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.5831,0.06842,0.22037]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4774.0,"contact_point_centroid":[0.54636,0.02334,0.0439],"force_p95":0.07769,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1463,"mean_force":0.04489,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.54631,0.00414,0.04201]},{"body_a":"world","body_b":"grasp_target","contact_count":2552.0,"contact_point_centroid":[0.54431,0.00113,-0.00194],"force_p95":0.13027,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12282,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.51726,0.00049,0.2074]},{"body_a":"world","body_b":"grasp_target","contact_count":1320.0,"contact_point_centroid":[0.63762,0.16387,-0.00199],"force_p95":0.12391,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12488,"mean_force":0.1202,"phase_index":7.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.63926,0.15436,0.25842]},{"body_a":"world","body_b":"grasp_target","contact_count":980.0,"contact_point_centroid":[0.54431,0.00113,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.54451,0.00261,0.08342]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5136.0,"contact_point_centroid":[0.54641,-0.01525,0.04393],"force_p95":0.07919,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08096,"mean_force":0.04423,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.54632,0.00414,0.04202]}],"total_contact_groups":16},"final_pose_error":0.01994,"key_states":{"actual_goal_position":[0.64762,0.15808,0.1911],"final_object_position":[0.63762,0.16387,0.01602],"final_tcp_position":[0.64423,0.15676,0.29858],"realised_goal_position":[0.64762,0.15808,0.1911],"realised_object_initial_position":[0.54431,0.00113,0.03]},"peak_contact_force":30.39851,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":639.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.03],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.24751,"object_z_max":0.03,"peak_contact_force":30.39851,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2552.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_pre_grasp","tcp_end":[0.53712,0.001,0.11701],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.09128,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":245.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.12262,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":980.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_at_object","tcp_end":[0.55467,0.00433,0.05241],"tcp_start":[0.53712,0.001,0.11701],"tcp_to_object_dist_end":0.02854,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54412,0.00326,0.02499],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.24956,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.18071,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11710.0,"raw_peak_contact_force":0.25195,"subtask_id":"grasp_at_object","tcp_end":[0.54628,0.00414,0.04198],"tcp_start":[0.55467,0.00433,0.05241],"tcp_to_object_dist_end":0.01715,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":39.0,"n_steps":417.0,"n_steps_budget":600.0,"object_pos_end":[0.54853,0.00308,0.16107],"object_pos_start":[0.54412,0.00326,0.02499],"object_to_goal_dist_end":0.18641,"object_to_goal_dist_start":0.24956,"object_z_max":0.1608,"peak_contact_force":0.0816,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":16302.0,"raw_peak_contact_force":0.66108,"subtask_id":"lift_clearance","tcp_end":[0.54095,0.00327,0.18095],"tcp_start":[0.54628,0.00414,0.04198],"tcp_to_object_dist_end":0.02127,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.63982,0.14142,0.23789],"object_pos_start":[0.54853,0.00308,0.16107],"object_to_goal_dist_end":0.05028,"object_to_goal_dist_start":0.18641,"object_z_max":0.23781,"peak_contact_force":0.10393,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":34183.0,"raw_peak_contact_force":0.22327,"subtask_id":"approach_goal","tcp_end":[0.63429,0.1417,0.27051],"tcp_start":[0.54095,0.00327,0.18095],"tcp_to_object_dist_end":0.03308,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":26.0,"n_steps":199.0,"n_steps_budget":1000.0,"object_pos_end":[0.64044,0.15332,0.16544],"object_pos_start":[0.63982,0.14142,0.23789],"object_to_goal_dist_end":0.02708,"object_to_goal_dist_start":0.05028,"object_z_max":0.2379,"peak_contact_force":0.11255,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4824.0,"raw_peak_contact_force":0.27349,"subtask_id":"place_at_goal","tcp_end":[0.64158,0.15384,0.20029],"tcp_start":[0.63429,0.1417,0.27051],"tcp_to_object_dist_end":0.03488,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.63776,0.16411,0.01382],"object_pos_start":[0.64044,0.15332,0.16544],"object_to_goal_dist_end":0.17766,"object_to_goal_dist_start":0.02708,"object_z_max":0.16544,"peak_contact_force":0.08766,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1665.0,"raw_peak_contact_force":1.80229,"subtask_id":"place_at_goal","tcp_end":[0.63602,0.15233,0.21888],"tcp_start":[0.64158,0.15384,0.20029],"tcp_to_object_dist_end":0.20541,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":330.0,"n_steps_budget":600.0,"object_pos_end":[0.63762,0.16387,0.01602],"object_pos_start":[0.63776,0.16411,0.01382],"object_to_goal_dist_end":0.17547,"object_to_goal_dist_start":0.17766,"object_z_max":0.01651,"peak_contact_force":0.12263,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1320.0,"raw_peak_contact_force":0.12488,"tcp_end":[0.64423,0.15676,0.29858],"tcp_start":[0.63602,0.15233,0.21888],"tcp_to_object_dist_end":0.28272,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.67284,"average_solve_count":162.0,"average_success_count":162.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.approach_goal_height":0.08896,"approach_goal.speed":0.17232,"approach_object.approach_height":0.11797,"approach_object.speed":0.0514,"descend_to_grasp.descend_z":0.02051,"descend_to_grasp.lateral_offset_x":0.01535,"descend_to_grasp.lateral_offset_y":0.00124,"descend_to_grasp.speed":0.30269,"descend_to_place.place_z":-0.00174,"descend_to_place.speed":0.34537,"lift.lift_height":0.13612,"lift.speed":0.29614,"retract.retract_height":0.13369,"retract.speed":0.47231},"optimized_scores":{"best_composite_score":-0.12533,"best_fitness_score":0.75467,"best_task_score":0.56423},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":358.0,"contact_point_centroid":[0.57839,0.16993,-0.00336],"force_p95":0.53862,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.8411,"mean_force":0.18853,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.58772,0.17096,0.11843]},{"body_a":"world","body_b":"grasp_target","contact_count":81.0,"contact_point_centroid":[0.52628,0.03044,-0.0014],"force_p95":0.50549,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.59508,"mean_force":0.10942,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.5292,0.03058,0.04492]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6604.0,"contact_point_centroid":[0.52671,0.04963,0.09507],"force_p95":0.07472,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.36772,"mean_force":0.051,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52676,0.03043,0.09288]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":830.0,"contact_point_centroid":[0.59234,0.19103,0.1035],"force_p95":0.0919,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.34792,"mean_force":0.06346,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.59219,0.17246,0.10674]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6545.0,"contact_point_centroid":[0.52686,0.01128,0.09486],"force_p95":0.07413,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.34711,"mean_force":0.05107,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52676,0.03043,0.09257]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":665.0,"contact_point_centroid":[0.59049,0.15353,0.10384],"force_p95":0.11099,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33234,"mean_force":0.07722,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.59215,0.17244,0.10668]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3447.0,"contact_point_centroid":[0.58771,0.1803,0.14431],"force_p95":0.11402,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20813,"mean_force":0.071,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.58851,0.16176,0.14612]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3096.0,"contact_point_centroid":[0.58724,0.14297,0.14374],"force_p95":0.12957,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20083,"mean_force":0.08057,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.58857,0.16192,0.14552]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53048,0.03077,-0.00203],"force_p95":0.13003,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.14598,"mean_force":0.12538,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.53167,0.03076,0.04475]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":20409.0,"contact_point_centroid":[0.55509,0.11303,0.16107],"force_p95":0.07296,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14315,"mean_force":0.04899,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.5554,0.09397,0.1598]},{"body_a":"world","body_b":"grasp_target","contact_count":2100.0,"contact_point_centroid":[0.5305,0.03079,-0.00193],"force_p95":0.13221,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12286,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.51078,0.01371,0.22694]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":18296.0,"contact_point_centroid":[0.55522,0.07625,0.16157],"force_p95":0.08035,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13753,"mean_force":0.0539,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.55614,0.09541,0.1603]},{"body_a":"world","body_b":"grasp_target","contact_count":1392.0,"contact_point_centroid":[0.57792,0.16986,-0.00199],"force_p95":0.12416,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13213,"mean_force":0.12271,"phase_index":7.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.59106,0.17352,0.17657]},{"body_a":"world","body_b":"grasp_target","contact_count":1324.0,"contact_point_centroid":[0.5305,0.03079,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.52999,0.02951,0.10323]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4864.0,"contact_point_centroid":[0.53054,0.04988,0.0452],"force_p95":0.06834,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0891,"mean_force":0.04482,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.53048,0.03068,0.04333]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4856.0,"contact_point_centroid":[0.53056,0.01149,0.04527],"force_p95":0.06824,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08821,"mean_force":0.0447,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.53048,0.03068,0.04333]}],"total_contact_groups":16},"final_pose_error":0.01994,"key_states":{"actual_goal_position":[0.60153,0.17858,0.10809],"final_object_position":[0.57792,0.16986,0.02602],"final_tcp_position":[0.59702,0.17675,0.22244],"realised_goal_position":[0.60153,0.17858,0.10809],"realised_object_initial_position":[0.5305,0.03079,0.03]},"peak_contact_force":0.8411,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":526.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.03],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18162,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2100.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_pre_grasp","tcp_end":[0.52412,0.02796,0.155],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.12917,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":331.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1324.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_at_object","tcp_end":[0.5387,0.03124,0.05326],"tcp_start":[0.52412,0.02796,0.155],"tcp_to_object_dist_end":0.02845,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53039,0.0307,0.02585],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18355,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.1295,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11520.0,"raw_peak_contact_force":0.14598,"subtask_id":"grasp_at_object","tcp_end":[0.53045,0.03068,0.0433],"tcp_start":[0.5387,0.03124,0.05326],"tcp_to_object_dist_end":0.01744,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":317.0,"n_steps_budget":600.0,"object_pos_end":[0.53398,0.03053,0.12322],"object_pos_start":[0.53039,0.0307,0.02585],"object_to_goal_dist_end":0.16343,"object_to_goal_dist_start":0.18355,"object_z_max":0.12296,"peak_contact_force":0.06761,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":13230.0,"raw_peak_contact_force":0.59508,"subtask_id":"lift_clearance","tcp_end":[0.52665,0.03044,0.14257],"tcp_start":[0.53045,0.03068,0.0433],"tcp_to_object_dist_end":0.02069,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":31.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.58749,0.15298,0.15288],"object_pos_start":[0.53398,0.03053,0.12322],"object_to_goal_dist_end":0.05346,"object_to_goal_dist_start":0.16343,"object_z_max":0.15286,"peak_contact_force":0.08979,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":38705.0,"raw_peak_contact_force":0.14315,"subtask_id":"approach_goal","tcp_end":[0.58521,0.15273,0.18028],"tcp_start":[0.52665,0.03044,0.14257],"tcp_to_object_dist_end":0.0275,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":25.0,"n_steps":236.0,"n_steps_budget":1000.0,"object_pos_end":[0.59267,0.17309,0.08068],"object_pos_start":[0.58749,0.15298,0.15288],"object_to_goal_dist_end":0.02932,"object_to_goal_dist_start":0.05346,"object_z_max":0.15288,"peak_contact_force":0.10156,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":6543.0,"raw_peak_contact_force":0.20813,"subtask_id":"place_at_goal","tcp_end":[0.59449,0.17297,0.11064],"tcp_start":[0.58521,0.15273,0.18028],"tcp_to_object_dist_end":0.03001,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.57749,0.16979,0.02625],"object_pos_start":[0.59267,0.17309,0.08068],"object_to_goal_dist_end":0.08574,"object_to_goal_dist_start":0.02932,"object_z_max":0.08068,"peak_contact_force":0.13216,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1853.0,"raw_peak_contact_force":0.8411,"subtask_id":"place_at_goal","tcp_end":[0.58755,0.17091,0.13139],"tcp_start":[0.59449,0.17297,0.11064],"tcp_to_object_dist_end":0.10562,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":348.0,"n_steps_budget":600.0,"object_pos_end":[0.57792,0.16986,0.02602],"object_pos_start":[0.57749,0.16979,0.02625],"object_to_goal_dist_end":0.08584,"object_to_goal_dist_start":0.08574,"object_z_max":0.02625,"peak_contact_force":0.12263,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1392.0,"raw_peak_contact_force":0.13213,"tcp_end":[0.59702,0.17675,0.22244],"tcp_start":[0.58755,0.17091,0.13139],"tcp_to_object_dist_end":0.19747,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.14286,"average_solve_count":119.0,"average_success_count":119.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.approach_goal_height":0.10253,"approach_goal.speed":0.292,"approach_object.approach_height":0.10861,"approach_object.speed":0.3133,"descend_to_grasp.descend_z":0.02001,"descend_to_grasp.lateral_offset_x":0.01055,"descend_to_grasp.lateral_offset_y":-0.00101,"descend_to_grasp.speed":0.3293,"descend_to_place.place_z":0.01796,"descend_to_place.speed":0.2782,"lift.lift_height":0.1753,"lift.speed":0.32591,"retract.retract_height":0.08082,"retract.speed":0.17749},"optimized_scores":{"best_composite_score":-0.30505,"best_fitness_score":0.57495,"best_task_score":0.21051},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":88.0,"contact_point_centroid":[0.58877,0.15975,-0.01049],"force_p95":1.45197,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.0842,"mean_force":0.82718,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.56958,0.15122,0.31371]},{"body_a":"world","body_b":"grasp_target","contact_count":75.0,"contact_point_centroid":[0.50045,-0.01615,-0.00135],"force_p95":0.41285,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.52031,"mean_force":0.09082,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.49913,-0.01618,0.04648]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":7956.0,"contact_point_centroid":[0.49854,0.00302,0.11264],"force_p95":0.0799,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33817,"mean_force":0.05243,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.49846,-0.01603,0.11085]},{"body_a":"world","body_b":"grasp_target","contact_count":780.0,"contact_point_centroid":[0.58772,0.15992,-0.00285],"force_p95":0.12592,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.33736,"mean_force":0.11436,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.57517,0.16586,0.29101]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":7085.0,"contact_point_centroid":[0.49801,-0.03521,0.11213],"force_p95":0.08567,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.3106,"mean_force":0.05789,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.49848,-0.01603,0.11034]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":10822.0,"contact_point_centroid":[0.52488,0.02367,0.22447],"force_p95":0.13196,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28638,"mean_force":0.07673,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.52248,0.04247,0.22494]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":12572.0,"contact_point_centroid":[0.52504,0.06256,0.22571],"force_p95":0.12908,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25881,"mean_force":0.06652,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.52307,0.04392,0.22608]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.5038,-0.01573,-0.00205],"force_p95":0.13519,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.16807,"mean_force":0.12669,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.50137,-0.0162,0.04614]},{"body_a":"world","body_b":"grasp_target","contact_count":1672.0,"contact_point_centroid":[0.50382,-0.01567,-0.00192],"force_p95":0.13434,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12292,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.49892,-0.00696,0.22343]},{"body_a":"world","body_b":"grasp_target","contact_count":1224.0,"contact_point_centroid":[0.50382,-0.01567,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.50258,-0.01522,0.09983]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.58775,0.15988,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.57812,0.17888,0.26913]},{"body_a":"world","body_b":"grasp_target","contact_count":396.0,"contact_point_centroid":[0.58775,0.15988,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":7.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.57939,0.18111,0.29859]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5320.0,"contact_point_centroid":[0.49981,-0.03536,0.04758],"force_p95":0.06375,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09342,"mean_force":0.0409,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.50023,-0.01618,0.04488]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4900.0,"contact_point_centroid":[0.50029,0.0031,0.0468],"force_p95":0.06911,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08707,"mean_force":0.04501,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.50023,-0.01618,0.04489]},{"body_a":"left_finger","body_b":"right_finger","contact_count":782.0,"contact_point_centroid":[0.57526,0.1665,0.29195],"force_p95":0.01304,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01607,"mean_force":0.01086,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.5754,0.1665,0.28974]},{"body_a":"left_finger","body_b":"right_finger","contact_count":217.0,"contact_point_centroid":[0.58006,0.17965,0.26693],"force_p95":0.01101,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01103,"mean_force":0.01023,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.5799,0.17964,0.26495]}],"total_contact_groups":16},"final_pose_error":0.01993,"key_states":{"actual_goal_position":[0.58691,0.18745,0.24812],"final_object_position":[0.58775,0.15988,0.01602],"final_tcp_position":[0.58222,0.18401,0.30988],"realised_goal_position":[0.58691,0.18745,0.24812],"realised_object_initial_position":[0.50382,-0.01567,0.03]},"peak_contact_force":273009.92004,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":419.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.03],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.30942,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1672.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_pre_grasp","tcp_end":[0.49972,-0.01422,0.14737],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.12143,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":306.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1224.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_at_object","tcp_end":[0.5081,-0.0163,0.05373],"tcp_start":[0.49972,-0.01422,0.14737],"tcp_to_object_dist_end":0.02804,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":46.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50372,-0.01599,0.02579],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31263,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.13356,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12020.0,"raw_peak_contact_force":0.16807,"subtask_id":"grasp_at_object","tcp_end":[0.5002,-0.01618,0.04485],"tcp_start":[0.5081,-0.0163,0.05373],"tcp_to_object_dist_end":0.01938,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":38.0,"n_steps":391.0,"n_steps_budget":600.0,"object_pos_end":[0.51228,-0.01588,0.15925],"object_pos_start":[0.50372,-0.01599,0.02579],"object_to_goal_dist_end":0.23411,"object_to_goal_dist_start":0.31263,"object_z_max":0.15898,"peak_contact_force":0.07706,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":15116.0,"raw_peak_contact_force":0.52031,"subtask_id":"lift_clearance","tcp_end":[0.50026,-0.01593,0.18166],"tcp_start":[0.5002,-0.01618,0.04485],"tcp_to_object_dist_end":0.02543,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.58831,0.15896,-0.00545],"object_pos_start":[0.51228,-0.01588,0.15925],"object_to_goal_dist_end":0.25517,"object_to_goal_dist_start":0.23411,"object_z_max":0.26021,"peak_contact_force":0.37002,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":23482.0,"raw_peak_contact_force":2.0842,"subtask_id":"approach_goal","tcp_end":[0.57057,0.15312,0.31535],"tcp_start":[0.50026,-0.01593,0.18166],"tcp_to_object_dist_end":0.32135,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":195.0,"n_steps_budget":1000.0,"object_pos_end":[0.58775,0.15988,0.01602],"object_pos_start":[0.58831,0.15896,-0.00545],"object_to_goal_dist_end":0.23373,"object_to_goal_dist_start":0.25517,"object_z_max":0.01682,"peak_contact_force":273009.92004,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1562.0,"raw_peak_contact_force":0.33736,"subtask_id":"place_at_goal","tcp_end":[0.58111,0.17977,0.26814],"tcp_start":[0.57057,0.15312,0.31535],"tcp_to_object_dist_end":0.25299,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.58775,0.15988,0.01602],"object_pos_start":[0.58775,0.15988,0.01602],"object_to_goal_dist_end":0.23373,"object_to_goal_dist_start":0.23373,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1017.0,"raw_peak_contact_force":0.12263,"subtask_id":"place_at_goal","tcp_end":[0.57714,0.17845,0.28901],"tcp_start":[0.58111,0.17977,0.26814],"tcp_to_object_dist_end":0.27383,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":99.0,"n_steps_budget":600.0,"object_pos_end":[0.58775,0.15988,0.01602],"object_pos_start":[0.58775,0.15988,0.01602],"object_to_goal_dist_end":0.23373,"object_to_goal_dist_start":0.23373,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":396.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.58222,0.18401,0.30988],"tcp_start":[0.57714,0.17845,0.28901],"tcp_to_object_dist_end":0.2949,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```