## Search State

- **Seed**: 4
- **Iteration**: 5 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 4 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 13 | -0.1769 | 0.36 | ❌ rejected |
| 3 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 12 | 0.1213 | 0.74 | ❌ rejected |
| 2 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 12 | 0.2195 | 0.93 | ✅ accepted |
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

> ⚠️ **SUBTASK STRUCTURE CAUTION**: The current best task_score is 0.934, which indicates the subtask decomposition is already effective.
> Preserve the current subtask decomposition unless the evidence shows a subtask change is necessary. Prefer refining phases, parameters, control modes, or termination conditions first.
> Unnecessary subtask redesign when performance is already high often causes regression.

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

## Current Skill (Q=-0.177) — your mutation base

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
      - 0.4
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
      - 0.3
      default: 0.15
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
    - 0.02
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
    place_z_offset:
      type: scalar
      range:
      - 0.0
      - 0.04
      default: 0.02
      binds_to:
      - path: target.offset.z
        mode: replace
    speed:
      type: scalar
      range:
      - 0.05
      - 0.3
      default: 0.1
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: place_at_goal

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
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.02], tolerance=0.01
  - orientation: mode=align_axis, axis=[0.0, 0.0, -1.0], align_with=world_z, tolerance=0.1
  - parameter_bindings:
    - place_z_offset: status=consumed; consumers=target.offset.z (replace)
    - speed: status=consumed; consumers=generator.speed (replace)

## Design Metrics

- **Composite score**: -0.177
- **task_score** (E): 0.362
- **fitness_score**: 0.653  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.830

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_object | 1.00 | 1.00 | 0.1735 |
| descend_to_grasp | 1.00 | 1.00 | 0.0792 |
| grasp | 1.00 | 1.00 | 0.0127 |
| lift | 1.00 | 1.00 | 0.1567 |
| approach_goal | 0.33 | 0.67 | 0.1544 |
| descend_to_place | 1.00 | 1.00 | 0.0861 |
| release | 1.00 | 1.00 | 0.0209 |
| retract | 1.00 | 1.00 | 0.0491 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.520, 0.005, 0.130) | (0.526, 0.005, 0.030)→(0.526, 0.005, 0.026) | 0.246→0.249 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_to_grasp | descend | 1.00 / step_budget | (0.520, 0.005, 0.130)→(0.534, 0.003, 0.052) | (0.526, 0.005, 0.026)→(0.526, 0.005, 0.026) | 0.249→0.249 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp | grasp | 1.00 / step_budget | (0.534, 0.003, 0.052)→(0.526, 0.003, 0.043) | (0.526, 0.005, 0.026)→(0.526, 0.004, 0.025) | 0.249→0.250 | 1.00 / 43.000 | 0.172 | 0.239 |
| lift | lift | 1.00 / step_budget | (0.526, 0.003, 0.043)→(0.523, 0.004, 0.199) | (0.526, 0.004, 0.025)→(0.535, 0.004, 0.178) | 0.250→0.202 | 1.00 / 33.000 | 0.093 | 0.622 |
| approach_goal | approach | 0.33 / step_budget | (0.523, 0.004, 0.199)→(0.586, 0.125, 0.258) | (0.535, 0.004, 0.178)→(0.590, 0.133, 0.154) | 0.202→0.105 | 0.67 / 17.667 | 0.074 | 0.196 |
| descend_to_place | descend | 1.00 / step_budget | (0.586, 0.125, 0.258)→(0.606, 0.170, 0.201) | (0.590, 0.133, 0.154)→(0.609, 0.174, 0.047) | 0.105→0.140 | 1.00 / 15.000 | 0.118 | 1.453 |
| release | release | 1.00 / step_budget | (0.606, 0.170, 0.201)→(0.601, 0.168, 0.221) | (0.609, 0.174, 0.047)→(0.603, 0.178, 0.020) | 0.140→0.165 | 1.00 / 4.000 | 0.127 | 0.503 |
| retract | retract | 1.00 / step_budget | (0.601, 0.168, 0.221)→(0.609, 0.173, 0.269) | (0.603, 0.178, 0.020)→(0.603, 0.178, 0.019) | 0.165→0.165 | 1.00 / 4.000 | 0.123 | 0.132 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: 1.000
- terminal_score: 0.565
- phase_score: 0.598
- phase_breakdown.approach_goal_score: 0.298
- phase_breakdown.place_at_goal_score: 0.172
- phase_breakdown.grasp_at_object_score: 0.703
- phase_breakdown.reach_pre_grasp_score: 0.724
- phase_breakdown.lift_clearance_score: 0.892
- grasp_place_fitness: 0.755

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.755
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.565
- **Median Q (composite search score)**: -0.201
- **K-run variance**: 0.0057
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.345


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.30833,"average_solve_count":120.0,"average_success_count":120.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.approach_goal_height":0.12416,"approach_goal.speed":0.23162,"approach_object.approach_height":0.07336,"approach_object.speed":0.29944,"descend_to_grasp.descend_z":0.02051,"descend_to_grasp.lateral_offset_x":0.01685,"descend_to_grasp.lateral_offset_y":-0.00288,"descend_to_grasp.speed":0.21856,"descend_to_place.place_z_offset":0.00926,"descend_to_place.speed":0.13476,"lift.lift_height":0.25559,"lift.speed":0.24778,"retract.retract_speed":0.14055},"optimized_scores":{"best_composite_score":-0.20062,"best_fitness_score":0.62938,"best_task_score":0.30851},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":910.0,"contact_point_centroid":[0.64082,0.17758,-0.00343],"force_p95":0.80472,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.05353,"mean_force":0.19865,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.6385,0.14855,0.25194]},{"body_a":"world","body_b":"grasp_target","contact_count":91.0,"contact_point_centroid":[0.5409,-0.00163,-0.00162],"force_p95":0.53731,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.69945,"mean_force":0.10764,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.54252,-0.0015,0.04281]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":10057.0,"contact_point_centroid":[0.54125,0.01792,0.14099],"force_p95":0.0982,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.41235,"mean_force":0.05833,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.54061,-0.00121,0.13884]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":10610.0,"contact_point_centroid":[0.54123,-0.02025,0.14381],"force_p95":0.09316,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.37163,"mean_force":0.05496,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.54063,-0.0012,0.14184]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":9811.0,"contact_point_centroid":[0.58431,0.04044,0.27333],"force_p95":0.1236,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.291,"mean_force":0.08618,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.57929,0.05899,0.27363]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.54428,0.00092,-0.00225],"force_p95":0.18491,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24625,"mean_force":0.14061,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.54516,-0.00147,0.04232]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":10542.0,"contact_point_centroid":[0.58443,0.07817,0.27362],"force_p95":0.12052,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20791,"mean_force":0.08076,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.57973,0.05964,0.27385]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4780.0,"contact_point_centroid":[0.54402,-0.02068,0.04274],"force_p95":0.07663,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14427,"mean_force":0.04485,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.54394,-0.00148,0.04083]},{"body_a":"world","body_b":"grasp_target","contact_count":2144.0,"contact_point_centroid":[0.54431,0.00113,-0.00193],"force_p95":0.13219,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12285,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.51749,0.0005,0.20385]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.64062,0.1784,-0.00199],"force_p95":0.12264,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12264,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.63853,0.15354,0.20734]},{"body_a":"world","body_b":"grasp_target","contact_count":892.0,"contact_point_centroid":[0.54431,0.00113,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.54337,-0.00016,0.07948]},{"body_a":"world","body_b":"grasp_target","contact_count":1936.0,"contact_point_centroid":[0.64062,0.1784,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":7.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.63973,0.15477,0.25036]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5115.0,"contact_point_centroid":[0.54401,0.01787,0.04277],"force_p95":0.07796,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0795,"mean_force":0.0442,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.54395,-0.00148,0.04084]},{"body_a":"left_finger","body_b":"right_finger","contact_count":844.0,"contact_point_centroid":[0.63901,0.14924,0.2486],"force_p95":0.01264,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0164,"mean_force":0.01083,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.63889,0.14922,0.2463]},{"body_a":"left_finger","body_b":"right_finger","contact_count":217.0,"contact_point_centroid":[0.64111,0.1543,0.20619],"force_p95":0.011,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01101,"mean_force":0.01023,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.64088,0.15428,0.20398]}],"total_contact_groups":15},"final_pose_error":0.01442,"key_states":{"actual_goal_position":[0.64762,0.15808,0.1911],"final_object_position":[0.64062,0.1784,0.01602],"final_tcp_position":[0.64429,0.1569,0.27712],"realised_goal_position":[0.64762,0.15808,0.1911],"realised_object_initial_position":[0.54431,0.00113,0.03]},"peak_contact_force":2.05353,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":537.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.03],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.24751,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2144.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_pre_grasp","tcp_end":[0.53715,0.001,0.11012],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.08441,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":223.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":892.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_at_object","tcp_end":[0.55231,-0.00135,0.05116],"tcp_start":[0.53715,0.001,0.11012],"tcp_to_object_dist_end":0.0265,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54416,-0.00075,0.02509],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25198,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.17531,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11695.0,"raw_peak_contact_force":0.24625,"subtask_id":"grasp_at_object","tcp_end":[0.54391,-0.00148,0.0408],"tcp_start":[0.55231,-0.00135,0.05116],"tcp_to_object_dist_end":0.01572,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":560.0,"n_steps_budget":630.0,"object_pos_end":[0.56068,-0.00039,0.23854],"object_pos_start":[0.54416,-0.00075,0.02509],"object_to_goal_dist_end":0.18688,"object_to_goal_dist_start":0.25198,"object_z_max":0.23825,"peak_contact_force":0.10787,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":20758.0,"raw_peak_contact_force":0.69945,"subtask_id":"lift_clearance","tcp_end":[0.54166,-0.00083,0.25916],"tcp_start":[0.54391,-0.00148,0.0408],"tcp_to_object_dist_end":0.02807,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.63803,0.16206,0.04995],"object_pos_start":[0.56068,-0.00039,0.23854],"object_to_goal_dist_end":0.14153,"object_to_goal_dist_start":0.18688,"object_z_max":0.25812,"peak_contact_force":0.0,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":20353.0,"raw_peak_contact_force":0.291,"subtask_id":"approach_goal","tcp_end":[0.63565,0.14277,0.30132],"tcp_start":[0.54166,-0.00083,0.25916],"tcp_to_object_dist_end":0.25211,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":244.0,"n_steps_budget":1000.0,"object_pos_end":[0.64062,0.1784,0.01602],"object_pos_start":[0.63803,0.16206,0.04995],"object_to_goal_dist_end":0.1764,"object_to_goal_dist_start":0.14153,"object_z_max":0.04995,"peak_contact_force":0.12264,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1754.0,"raw_peak_contact_force":2.05353,"subtask_id":"place_at_goal","tcp_end":[0.64253,0.15462,0.20812],"tcp_start":[0.63565,0.14277,0.30132],"tcp_to_object_dist_end":0.19358,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.64062,0.1784,0.01602],"object_pos_start":[0.64062,0.1784,0.01602],"object_to_goal_dist_end":0.1764,"object_to_goal_dist_start":0.1764,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1017.0,"raw_peak_contact_force":0.12264,"subtask_id":"place_at_goal","tcp_end":[0.63717,0.15309,0.2266],"tcp_start":[0.64253,0.15462,0.20812],"tcp_to_object_dist_end":0.21212,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":484.0,"n_steps_budget":600.0,"object_pos_end":[0.64062,0.1784,0.01602],"object_pos_start":[0.64062,0.1784,0.01602],"object_to_goal_dist_end":0.1764,"object_to_goal_dist_start":0.1764,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1936.0,"raw_peak_contact_force":0.12263,"subtask_id":"place_at_goal","tcp_end":[0.64429,0.1569,0.27712],"tcp_start":[0.63717,0.15309,0.2266],"tcp_to_object_dist_end":0.26201,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.91667,"average_solve_count":156.0,"average_success_count":156.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.approach_goal_height":0.11432,"approach_goal.speed":0.09827,"approach_object.approach_height":0.07794,"approach_object.speed":0.08044,"descend_to_grasp.descend_z":0.02173,"descend_to_grasp.lateral_offset_x":0.01872,"descend_to_grasp.lateral_offset_y":0.00013,"descend_to_grasp.speed":0.13751,"descend_to_place.place_z_offset":0.03216,"descend_to_place.speed":0.22602,"lift.lift_height":0.1788,"lift.speed":0.33874,"retract.retract_speed":0.28555},"optimized_scores":{"best_composite_score":-0.07464,"best_fitness_score":0.75536,"best_task_score":0.56455},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":293.0,"contact_point_centroid":[0.57758,0.18372,-0.00432],"force_p95":0.78401,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.26346,"mean_force":0.23423,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.58804,0.17008,0.14856]},{"body_a":"world","body_b":"grasp_target","contact_count":84.0,"contact_point_centroid":[0.52611,0.02946,-0.00147],"force_p95":0.48532,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.62754,"mean_force":0.10841,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.53101,0.02957,0.04446]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8686.0,"contact_point_centroid":[0.52787,0.04873,0.11624],"force_p95":0.07539,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.3759,"mean_force":0.05064,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52787,0.02957,0.11404]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8220.0,"contact_point_centroid":[0.52778,0.01041,0.11385],"force_p95":0.0788,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.35548,"mean_force":0.0526,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.5279,0.02957,0.1117]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":983.0,"contact_point_centroid":[0.59118,0.19021,0.13311],"force_p95":0.09669,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.34612,"mean_force":0.06185,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.59225,0.17151,0.13492]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":651.0,"contact_point_centroid":[0.59099,0.15256,0.13327],"force_p95":0.11331,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29802,"mean_force":0.07423,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.59232,0.17153,0.13502]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5807.0,"contact_point_centroid":[0.58105,0.16734,0.16728],"force_p95":0.08762,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2144,"mean_force":0.05885,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.5822,0.14878,0.16783]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53047,0.0307,-0.00211],"force_p95":0.15113,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.20705,"mean_force":0.13116,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.53359,0.02974,0.044]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4667.0,"contact_point_centroid":[0.58015,0.1296,0.16699],"force_p95":0.11126,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20248,"mean_force":0.07574,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.58211,0.14861,0.16807]},{"body_a":"world","body_b":"grasp_target","contact_count":1848.0,"contact_point_centroid":[0.5773,0.18417,-0.00198],"force_p95":0.1284,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.15109,"mean_force":0.12252,"phase_index":7.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.59147,0.17328,0.17682]},{"body_a":"world","body_b":"grasp_target","contact_count":2448.0,"contact_point_centroid":[0.5305,0.03079,-0.00194],"force_p95":0.13067,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12283,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.51099,0.01405,0.20678]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4816.0,"contact_point_centroid":[0.53247,0.01047,0.0445],"force_p95":0.07176,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12435,"mean_force":0.0448,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.53239,0.02967,0.04257]},{"body_a":"world","body_b":"grasp_target","contact_count":956.0,"contact_point_centroid":[0.5305,0.03079,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.53107,0.02927,0.0827]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":16928.0,"contact_point_centroid":[0.54957,0.06334,0.19279],"force_p95":0.08193,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11222,"mean_force":0.05732,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.55043,0.08249,0.19182]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":20005.0,"contact_point_centroid":[0.55054,0.10161,0.19282],"force_p95":0.07224,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08925,"mean_force":0.04859,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.55051,0.08265,0.19186]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4955.0,"contact_point_centroid":[0.53245,0.0489,0.04444],"force_p95":0.07236,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07405,"mean_force":0.04462,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.53239,0.02967,0.04257]}],"total_contact_groups":16},"final_pose_error":0.01304,"key_states":{"actual_goal_position":[0.60153,0.17858,0.10809],"final_object_position":[0.57729,0.18418,0.02602],"final_tcp_position":[0.59691,0.17674,0.19603],"realised_goal_position":[0.60153,0.17858,0.10809],"realised_object_initial_position":[0.5305,0.03079,0.03]},"peak_contact_force":1.26346,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":613.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.03],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18162,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2448.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_pre_grasp","tcp_end":[0.52427,0.02844,0.11527],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.0895,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":239.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":956.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_at_object","tcp_end":[0.54058,0.03022,0.05248],"tcp_start":[0.52427,0.02844,0.11527],"tcp_to_object_dist_end":0.02833,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53037,0.02999,0.02557],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18427,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.14681,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11571.0,"raw_peak_contact_force":0.20705,"subtask_id":"grasp_at_object","tcp_end":[0.53236,0.02966,0.04253],"tcp_start":[0.54058,0.03022,0.05248],"tcp_to_object_dist_end":0.01708,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":39.0,"n_steps":417.0,"n_steps_budget":600.0,"object_pos_end":[0.53508,0.02981,0.16476],"object_pos_start":[0.53037,0.02999,0.02557],"object_to_goal_dist_end":0.17251,"object_to_goal_dist_start":0.18427,"object_z_max":0.16449,"peak_contact_force":0.08236,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":16990.0,"raw_peak_contact_force":0.62754,"subtask_id":"lift_clearance","tcp_end":[0.52729,0.02974,0.18462],"tcp_start":[0.53236,0.02966,0.04253],"tcp_to_object_dist_end":0.02133,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":36.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5739,0.1263,0.17596],"object_pos_start":[0.53508,0.02981,0.16476],"object_to_goal_dist_end":0.09002,"object_to_goal_dist_start":0.17251,"object_z_max":0.17594,"peak_contact_force":0.09289,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":36933.0,"raw_peak_contact_force":0.11222,"subtask_id":"approach_goal","tcp_end":[0.5722,0.12604,0.20196],"tcp_start":[0.52729,0.02974,0.18462],"tcp_to_object_dist_end":0.02605,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":29.0,"n_steps":343.0,"n_steps_budget":1000.0,"object_pos_end":[0.59454,0.17247,0.11016],"object_pos_start":[0.5739,0.1263,0.17596],"object_to_goal_dist_end":0.00952,"object_to_goal_dist_start":0.09002,"object_z_max":0.17596,"peak_contact_force":0.10944,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":10474.0,"raw_peak_contact_force":0.2144,"subtask_id":"place_at_goal","tcp_end":[0.5943,0.1719,0.1386],"tcp_start":[0.5722,0.12604,0.20196],"tcp_to_object_dist_end":0.02845,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.57757,0.18355,0.02649],"object_pos_start":[0.59454,0.17247,0.11016],"object_to_goal_dist_end":0.08519,"object_to_goal_dist_start":0.00952,"object_z_max":0.11016,"peak_contact_force":0.1365,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1927.0,"raw_peak_contact_force":1.26346,"subtask_id":"place_at_goal","tcp_end":[0.58795,0.17005,0.15945],"tcp_start":[0.5943,0.1719,0.1386],"tcp_to_object_dist_end":0.13405,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":462.0,"n_steps_budget":600.0,"object_pos_end":[0.57729,0.18418,0.02602],"object_pos_start":[0.57757,0.18355,0.02649],"object_to_goal_dist_end":0.08576,"object_to_goal_dist_start":0.08519,"object_z_max":0.02653,"peak_contact_force":0.12263,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1848.0,"raw_peak_contact_force":0.15109,"subtask_id":"place_at_goal","tcp_end":[0.59691,0.17674,0.19603],"tcp_start":[0.58795,0.17005,0.15945],"tcp_to_object_dist_end":0.1713,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.19328,"average_solve_count":119.0,"average_success_count":119.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.approach_goal_height":0.10697,"approach_goal.speed":0.21954,"approach_object.approach_height":0.12589,"approach_object.speed":0.34506,"descend_to_grasp.descend_z":0.02008,"descend_to_grasp.lateral_offset_x":0.0123,"descend_to_grasp.lateral_offset_y":-0.00476,"descend_to_grasp.speed":0.20183,"descend_to_place.place_z_offset":0.01621,"descend_to_place.speed":0.14713,"lift.lift_height":0.14909,"lift.speed":0.24949,"retract.retract_speed":0.17201},"optimized_scores":{"best_composite_score":-0.25533,"best_fitness_score":0.57467,"best_task_score":0.21206},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":761.0,"contact_point_centroid":[0.59118,0.17213,-0.00366],"force_p95":0.75977,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.09132,"mean_force":0.19113,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.57806,0.17326,0.25771]},{"body_a":"world","body_b":"grasp_target","contact_count":83.0,"contact_point_centroid":[0.50094,-0.01981,-0.00168],"force_p95":0.39468,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.53927,"mean_force":0.08047,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.50076,-0.01944,0.04689]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6807.0,"contact_point_centroid":[0.49938,9e-05,0.09986],"force_p95":0.08393,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.35638,"mean_force":0.05276,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.49933,-0.01888,0.09808]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5644.0,"contact_point_centroid":[0.4985,-0.03809,0.1001],"force_p95":0.09185,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32402,"mean_force":0.06081,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.49933,-0.01887,0.09902]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50382,-0.01595,-0.00232],"force_p95":0.20569,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.26236,"mean_force":0.14558,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.50314,-0.0195,0.04612]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2761.0,"contact_point_centroid":[0.56508,0.11252,0.25937],"force_p95":0.14267,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24101,"mean_force":0.10594,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.55908,0.13062,0.26303]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2763.0,"contact_point_centroid":[0.56568,0.15077,0.25855],"force_p95":0.1337,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21947,"mean_force":0.10745,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.55998,0.13272,0.26269]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":14994.0,"contact_point_centroid":[0.52333,0.05683,0.20469],"force_p95":0.10922,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18396,"mean_force":0.0652,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.52086,0.03811,0.20419]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":14199.0,"contact_point_centroid":[0.52142,0.01703,0.2014],"force_p95":0.12791,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18041,"mean_force":0.06856,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.51987,0.03588,0.202]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4052.0,"contact_point_centroid":[0.5012,-0.0387,0.04636],"force_p95":0.08661,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16105,"mean_force":0.05206,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.502,-0.01948,0.04486]},{"body_a":"world","body_b":"grasp_target","contact_count":1508.0,"contact_point_centroid":[0.50382,-0.01567,-0.00191],"force_p95":0.13496,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12295,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.499,-0.00682,0.23254]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.59127,0.17226,-0.00199],"force_p95":0.12264,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12264,"mean_force":0.12262,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.57938,0.18182,0.258]},{"body_a":"world","body_b":"grasp_target","contact_count":1420.0,"contact_point_centroid":[0.50382,-0.01567,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.5035,-0.01674,0.10854]},{"body_a":"world","body_b":"grasp_target","contact_count":1988.0,"contact_point_centroid":[0.59127,0.17226,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":7.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.58047,0.18356,0.30503]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5174.0,"contact_point_centroid":[0.50207,-0.00015,0.04673],"force_p95":0.08191,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08393,"mean_force":0.04392,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.50201,-0.01948,0.04487]},{"body_a":"left_finger","body_b":"right_finger","contact_count":618.0,"contact_point_centroid":[0.57924,0.17558,0.25972],"force_p95":0.01385,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0153,"mean_force":0.01095,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.57912,0.17557,0.25749]}],"total_contact_groups":17},"final_pose_error":0.01326,"key_states":{"actual_goal_position":[0.58691,0.18745,0.24812],"final_object_position":[0.59127,0.17226,0.01602],"final_tcp_position":[0.58441,0.18624,0.33515],"realised_goal_position":[0.58691,0.18745,0.24812],"realised_object_initial_position":[0.50382,-0.01567,0.03]},"peak_contact_force":2.09132,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":378.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.03],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.30942,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1508.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_pre_grasp","tcp_end":[0.49984,-0.01402,0.1649],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.13895,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":355.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1420.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_at_object","tcp_end":[0.50989,-0.01963,0.05375],"tcp_start":[0.49984,-0.01402,0.1649],"tcp_to_object_dist_end":0.02867,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.5037,-0.01834,0.02483],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31485,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.19533,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11026.0,"raw_peak_contact_force":0.26236,"subtask_id":"grasp_at_object","tcp_end":[0.50197,-0.01947,0.04483],"tcp_start":[0.50989,-0.01963,0.05375],"tcp_to_object_dist_end":0.0201,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":332.0,"n_steps_budget":600.0,"object_pos_end":[0.5099,-0.01761,0.13169],"object_pos_start":[0.5037,-0.01834,0.02483],"object_to_goal_dist_end":0.24807,"object_to_goal_dist_start":0.31485,"object_z_max":0.13142,"peak_contact_force":0.0874,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":12534.0,"raw_peak_contact_force":0.53927,"subtask_id":"lift_clearance","tcp_end":[0.50006,-0.01836,0.15447],"tcp_start":[0.50197,-0.01947,0.04483],"tcp_to_object_dist_end":0.02483,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":17.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.55716,0.1093,0.23676],"object_pos_start":[0.5099,-0.01761,0.13169],"object_to_goal_dist_end":0.08438,"object_to_goal_dist_start":0.24807,"object_z_max":0.23667,"peak_contact_force":0.1286,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":29193.0,"raw_peak_contact_force":0.18396,"subtask_id":"approach_goal","tcp_end":[0.55069,0.1075,0.27092],"tcp_start":[0.50006,-0.01836,0.15447],"tcp_to_object_dist_end":0.03481,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":626.0,"n_steps_budget":1000.0,"object_pos_end":[0.59127,0.17227,0.01602],"object_pos_start":[0.55716,0.1093,0.23676],"object_to_goal_dist_end":0.23263,"object_to_goal_dist_start":0.08438,"object_z_max":0.23677,"peak_contact_force":0.12263,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":6903.0,"raw_peak_contact_force":2.09132,"subtask_id":"place_at_goal","tcp_end":[0.58235,0.18281,0.25674],"tcp_start":[0.55069,0.1075,0.27092],"tcp_to_object_dist_end":0.24112,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.59127,0.17226,0.01602],"object_pos_start":[0.59127,0.17227,0.01602],"object_to_goal_dist_end":0.23263,"object_to_goal_dist_start":0.23263,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1026.0,"raw_peak_contact_force":0.12264,"subtask_id":"place_at_goal","tcp_end":[0.57832,0.18138,0.27781],"tcp_start":[0.58235,0.18281,0.25674],"tcp_to_object_dist_end":0.26227,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":497.0,"n_steps_budget":600.0,"object_pos_end":[0.59127,0.17226,0.01602],"object_pos_start":[0.59127,0.17226,0.01602],"object_to_goal_dist_end":0.23263,"object_to_goal_dist_start":0.23263,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1988.0,"raw_peak_contact_force":0.12263,"subtask_id":"place_at_goal","tcp_end":[0.58441,0.18624,0.33515],"tcp_start":[0.57832,0.18138,0.27781],"tcp_to_object_dist_end":0.31951,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```