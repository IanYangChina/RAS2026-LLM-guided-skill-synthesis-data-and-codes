## Search State

- **Seed**: 4
- **Iteration**: 12 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 11 | approach → descend → grasp → lift → grasp → approach → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | — | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | time_limit | pose_tolerance | time_limit | pose_tolerance | 3 | 0.2898 | 0.31 | ❌ rejected |
| 10 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | impedance_control | admittance_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 7 | 0.2304 | 0.34 | ✅ accepted |
| 9 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 5 | -0.0137 | 0.22 | ❌ rejected |
| 8 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | impedance_control | impedance_control | admittance_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 7 | 0.2055 | 0.28 | ✅ accepted |
| 7 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | impedance_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 5 | 0.2108 | 0.26 | ✅ accepted |

**Proposal policy**: task_score is 0.31 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.290) — your mutation base

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
  - 0.08
  weight: 0.2
- id: lift_clearance
  anchor: object
  target_entity: object
  metric: goal_progress
  offset:
  - 0.0
  - 0.0
  - 0.15
  weight: 0.2
- id: reach_pre_place
  offset:
  - 0.0
  - 0.0
  - 0.08
  weight: 0.2
- id: place_goal
  target_entity: object
  weight: 0.4
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
    - 0.08
    tolerance: 0.005
    orientation:
      mode: keep_current
  subtask_id: reach_pre_grasp
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
    - 0.03
    tolerance: 0.005
    orientation:
      mode: keep_current
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
      mode: none
  guards:
  - id: bilateral_check
    when: after_phase
    predicate: bilateral_grasp
    threshold: 0.001
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: repeat
- id: lift_1
  type: lift
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
    offset_along_axis:
      distance: 0.25
      axis: world_z
      mode: replace_offset_projection
      sign: positive
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    lift_height:
      type: scalar
      range:
      - 0.15
      - 0.35
      default: 0.25
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    lift_speed:
      type: scalar
      range:
      - 0.02
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
  subtask_id: lift_clearance
- id: approach_2
  type: approach
  generator: linear_cartesian
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.18
    tolerance: 0.008
    orientation:
      mode: keep_current
  parameters:
    transport_speed:
      type: scalar
      range:
      - 0.1
      - 0.5
      default: 0.3
      binds_to:
      - path: generator.speed
        mode: replace
    transport_z_offset:
      type: scalar
      range:
      - 0.12
      - 0.25
      default: 0.18
      binds_to:
      - path: target.offset.z
        mode: replace
  guards:
  - id: transport_guard
    when: during_phase
    predicate: object_lifted
    threshold: 0.03
    on_failure: retry
  - id: object_lost_guard
    when: after_phase
    predicate: object_lifted
    threshold: 0.03
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.0
    - 0.0
    - 0.02
  subtask_id: reach_pre_place
- id: descend_2
  type: descend
  generator: linear_cartesian
  control: admittance_control
  termination: force_exceeded
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.0
    tolerance: 0.005
    orientation:
      mode: keep_current
  parameters:
    place_force_threshold:
      type: scalar
      range:
      - 2.0
      - 8.0
      default: 5.0
      binds_to:
      - path: termination.force_threshold
        mode: replace
    place_speed:
      type: scalar
      range:
      - 0.02
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
    place_z_offset:
      type: scalar
      range:
      - 0.0
      - 0.04
      default: 0.0
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: place_goal
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
      mode: none
- id: retract_1
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
    - 0.15
    tolerance: 0.005
    orientation:
      mode: keep_current

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.08], tolerance=0.005
  - orientation: mode=keep_current
  - parameter_bindings: none
- **descend_1** (`descend`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.03], tolerance=0.005
  - orientation: mode=keep_current
  - parameter_bindings: none
- **grasp_1** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - orientation: mode=none
  - parameter_bindings: none
  - guards:
    - id=bilateral_check, when=after_phase, predicate=bilateral_grasp, on_failure=retry, threshold=0.001
  - retries: max_attempts=2, strategy=repeat
- **lift_1** (`lift`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=world_z, distance=0.25, mode=replace_offset_projection, sign=positive}, tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - lift_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=lift_check, when=after_phase, predicate=object_lifted, on_failure=retry, threshold=0.05
  - retries: max_attempts=2, strategy=repeat
- **approach_2** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.18], tolerance=0.008
  - orientation: mode=keep_current
  - parameter_bindings:
    - transport_speed: status=consumed; consumers=generator.speed (replace)
    - transport_z_offset: status=consumed; consumers=target.offset.z (replace)
  - guards:
    - id=transport_guard, when=during_phase, predicate=object_lifted, on_failure=retry, threshold=0.03
    - id=object_lost_guard, when=after_phase, predicate=object_lifted, on_failure=retry, threshold=0.03
  - retries: max_attempts=2, strategy=offset_target, offset=[0.0, 0.0, 0.02]
- **descend_2** (`descend`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], tolerance=0.005
  - orientation: mode=keep_current
  - parameter_bindings:
    - place_force_threshold: status=consumed; consumers=termination.force_threshold (replace)
    - place_speed: status=consumed; consumers=generator.speed (replace)
    - place_z_offset: status=consumed; consumers=target.offset.z (replace)
- **release_1** (`release`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - orientation: mode=none
  - parameter_bindings: none
- **retract_1** (`retract`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.15], tolerance=0.005
  - orientation: mode=keep_current
  - parameter_bindings: none

## Design Metrics

- **Composite score**: 0.290
- **task_score** (E): 0.311
- **fitness_score**: 0.620  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.330

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1678 |
| descend_1 | 1.00 | 1.00 | 0.0817 |
| grasp_1 | 1.00 | 1.00 | 0.0122 |
| lift_1 | 1.00 | 1.00 | 0.1035 |
| regrasp | 1.00 | 1.00 | 0.0116 |
| approach_2 | 0.33 | 1.00 | 0.0026 |
| release_1 | 1.00 | 1.00 | 0.0208 |
| retract_1 | 1.00 | 1.00 | 0.1045 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.516, 0.004, 0.135) | (0.526, 0.005, 0.030)→(0.526, 0.005, 0.026) | 0.246→0.249 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.516, 0.004, 0.135)→(0.521, 0.005, 0.054) | (0.526, 0.005, 0.026)→(0.526, 0.005, 0.026) | 0.249→0.249 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_1 | grasp | 1.00 / step_budget | (0.521, 0.005, 0.054)→(0.513, 0.005, 0.045) | (0.526, 0.005, 0.026)→(0.526, 0.005, 0.026) | 0.249→0.249 | 1.00 / 44.667 | 0.136 | 0.172 |
| lift_1 | lift | 1.00 / step_budget | (0.513, 0.005, 0.045)→(0.521, 0.005, 0.148) | (0.526, 0.005, 0.026)→(0.534, 0.005, 0.123) | 0.249→0.205 | 1.00 / 27.000 | 0.091 | 0.413 |
| regrasp | grasp | 1.00 / step_budget | (0.521, 0.005, 0.148)→(0.515, 0.005, 0.138) | (0.534, 0.005, 0.123)→(0.522, 0.005, 0.109) | 0.205→0.214 | 1.00 / 26.667 | 0.097 | 0.148 |
| approach_2 | approach | 0.33 / step_budget | (0.607, 0.171, 0.192)→(0.608, 0.173, 0.193) | (0.522, 0.005, 0.109)→(0.562, 0.088, 0.019) | 0.214→0.192 | 1.00 / 8.333 | 91001.470 | 1.221 |
| release_1 | release | 1.00 / step_budget | (0.608, 0.173, 0.193)→(0.603, 0.172, 0.213) | (0.562, 0.088, 0.019)→(0.562, 0.088, 0.019) | 0.192→0.192 | 1.00 / 4.000 | 0.123 | 0.123 |
| retract_1 | retract | 1.00 / step_budget | (0.603, 0.172, 0.213)→(0.610, 0.174, 0.317) | (0.562, 0.088, 0.019)→(0.562, 0.088, 0.019) | 0.192→0.192 | 1.00 / 4.000 | 0.123 | 0.123 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.523
- phase_score: 0.292
- phase_breakdown.lift_clearance_score: 0.114
- phase_breakdown.place_goal_score: 0.000
- phase_breakdown.reach_pre_grasp_score: 0.560
- phase_breakdown.reach_pre_place_score: 0.785
- grasp_place_fitness: 0.728

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.728
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.523
- **Median Q (composite search score)**: 0.249
- **K-run variance**: 0.0059
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 10.0
- **Final σ (mean)**: 0.394


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.62025,"average_solve_count":158.0,"average_success_count":158.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_2.transport_speed":0.10602,"lift_1.lift_height":0.14228,"lift_1.lift_speed":0.12562},"optimized_scores":{"best_composite_score":0.24857,"best_fitness_score":0.57857,"best_task_score":0.23269},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":8421.0,"contact_point_centroid":[0.57604,0.04826,-0.00208],"force_p95":0.12264,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.28222,"mean_force":0.12704,"phase_index":5.0,"phase_name":"approach_2","phase_type":"approach","tcp_position_centroid":[0.60768,0.10958,0.17623]},{"body_a":"world","body_b":"grasp_target","contact_count":173.0,"contact_point_centroid":[0.54235,0.00077,-0.00121],"force_p95":0.21407,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.39855,"mean_force":0.06558,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.5289,0.00086,0.0476]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8149.0,"contact_point_centroid":[0.5347,-0.01801,0.09124],"force_p95":0.10713,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28774,"mean_force":0.07092,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.53183,0.00089,0.09013]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8963.0,"contact_point_centroid":[0.53499,0.01971,0.09047],"force_p95":0.10111,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27141,"mean_force":0.0658,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.53175,0.00089,0.08915]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4423.0,"contact_point_centroid":[0.54323,-0.00618,0.13906],"force_p95":0.12499,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23134,"mean_force":0.08959,"phase_index":5.0,"phase_name":"approach_2","phase_type":"approach","tcp_position_centroid":[0.5374,0.01223,0.14162]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4777.0,"contact_point_centroid":[0.5436,0.03085,0.1394],"force_p95":0.11867,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17679,"mean_force":0.08284,"phase_index":5.0,"phase_name":"approach_2","phase_type":"approach","tcp_position_centroid":[0.53763,0.01259,0.14166]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.54431,0.00113,-0.00203],"force_p95":0.13256,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.15292,"mean_force":0.1255,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.5315,0.0009,0.04756]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5658.0,"contact_point_centroid":[0.53954,0.01958,0.14487],"force_p95":0.09543,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14468,"mean_force":0.07388,"phase_index":4.0,"phase_name":"regrasp","phase_type":"grasp","tcp_position_centroid":[0.53364,0.0009,0.14511]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5645.0,"contact_point_centroid":[0.53952,-0.01778,0.14478],"force_p95":0.09665,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14126,"mean_force":0.07412,"phase_index":4.0,"phase_name":"regrasp","phase_type":"grasp","tcp_position_centroid":[0.53364,0.0009,0.14511]},{"body_a":"world","body_b":"grasp_target","contact_count":3996.0,"contact_point_centroid":[0.54431,0.00113,-0.00196],"force_p95":0.12459,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12275,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.5152,0.00044,0.21539]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.54431,0.00113,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.53236,0.00089,0.09781]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.5761,0.04826,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.63988,0.15565,0.20045]},{"body_a":"world","body_b":"grasp_target","contact_count":2888.0,"contact_point_centroid":[0.5761,0.04826,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":7.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.64043,0.15582,0.26761]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4951.0,"contact_point_centroid":[0.53151,-0.01832,0.04826],"force_p95":0.06907,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10568,"mean_force":0.04421,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53028,0.00088,0.04611]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5033.0,"contact_point_centroid":[0.53168,0.0201,0.04906],"force_p95":0.06688,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08563,"mean_force":0.04331,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53028,0.00088,0.04611]},{"body_a":"left_finger","body_b":"right_finger","contact_count":8662.0,"contact_point_centroid":[0.61023,0.11238,0.17956],"force_p95":0.01101,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01648,"mean_force":0.01048,"phase_index":5.0,"phase_name":"approach_2","phase_type":"approach","tcp_position_centroid":[0.6097,0.11236,0.17731]}],"total_contact_groups":17},"final_pose_error":0.01608,"key_states":{"actual_goal_position":[0.64762,0.15808,0.1911],"final_object_position":[0.5761,0.04826,0.01602],"final_tcp_position":[0.64553,0.15732,0.32517],"realised_goal_position":[0.64762,0.15808,0.1911],"realised_object_initial_position":[0.54431,0.00113,0.03]},"peak_contact_force":9749.03058,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.03],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.24751,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3996.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_pre_grasp","tcp_end":[0.52806,0.00077,0.15679],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.13178,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.53851,0.00103,0.05599],"tcp_start":[0.52806,0.00077,0.15679],"tcp_to_object_dist_end":0.03053,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54422,0.00107,0.02586],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.2503,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.1348,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11784.0,"raw_peak_contact_force":0.15292,"tcp_end":[0.53025,0.00088,0.04607],"tcp_start":[0.53851,0.00103,0.05599],"tcp_to_object_dist_end":0.02457,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":24.0,"n_steps":572.0,"n_steps_budget":630.0,"object_pos_end":[0.55119,0.00126,0.12625],"object_pos_start":[0.54422,0.00107,0.02586],"object_to_goal_dist_end":0.19519,"object_to_goal_dist_start":0.2503,"object_z_max":0.1261,"peak_contact_force":0.09783,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":17285.0,"raw_peak_contact_force":0.39855,"subtask_id":"lift_clearance","tcp_end":[0.53933,0.00099,0.15364],"tcp_start":[0.53025,0.00088,0.04607],"tcp_to_object_dist_end":0.02985,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":26.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53901,0.00101,0.11244],"object_pos_start":[0.55119,0.00126,0.12625],"object_to_goal_dist_end":0.20654,"object_to_goal_dist_start":0.19519,"object_z_max":0.12631,"peak_contact_force":0.10755,"phase_name":"regrasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11303.0,"raw_peak_contact_force":0.14468,"tcp_end":[0.53261,0.00088,0.14359],"tcp_start":[0.53933,0.00099,0.15364],"tcp_to_object_dist_end":0.03181,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":2608.0,"n_steps_budget":1000.0,"object_pos_end":[0.5761,0.04826,0.01602],"object_pos_start":[0.53901,0.00101,0.11244],"object_to_goal_dist_end":0.21871,"object_to_goal_dist_start":0.20654,"object_z_max":0.11244,"peak_contact_force":0.12263,"phase_name":"approach_2","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":26283.0,"raw_peak_contact_force":1.28222,"subtask_id":"reach_pre_place","tcp_end":[0.6436,0.15673,0.20076],"tcp_start":[0.64153,0.15381,0.19992],"tcp_to_object_dist_end":0.22462,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.5761,0.04826,0.01602],"object_pos_start":[0.5761,0.04826,0.01602],"object_to_goal_dist_end":0.21871,"object_to_goal_dist_start":0.21871,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1022.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.63847,0.15521,0.21949],"tcp_start":[0.6436,0.15673,0.20076],"tcp_to_object_dist_end":0.23818,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":722.0,"n_steps_budget":780.0,"object_pos_end":[0.5761,0.04826,0.01602],"object_pos_start":[0.5761,0.04826,0.01602],"object_to_goal_dist_end":0.21871,"object_to_goal_dist_start":0.21871,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2888.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.64553,0.15732,0.32517],"tcp_start":[0.63847,0.15521,0.21949],"tcp_to_object_dist_end":0.3351,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.61111,"average_solve_count":162.0,"average_success_count":162.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_2.transport_speed":0.18648,"lift_1.lift_height":0.14415,"lift_1.lift_speed":0.11372},"optimized_scores":{"best_composite_score":0.39768,"best_fitness_score":0.72768,"best_task_score":0.52328},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":6247.0,"contact_point_centroid":[0.56947,0.13774,-0.00206],"force_p95":0.12443,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.00368,"mean_force":0.12708,"phase_index":5.0,"phase_name":"approach_2","phase_type":"approach","tcp_position_centroid":[0.59099,0.16898,0.11217]},{"body_a":"world","body_b":"grasp_target","contact_count":175.0,"contact_point_centroid":[0.52814,0.02915,-0.00128],"force_p95":0.22869,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.43282,"mean_force":0.06587,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51586,0.02965,0.04476]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":10143.0,"contact_point_centroid":[0.52181,0.01074,0.09496],"force_p95":0.09843,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29173,"mean_force":0.06538,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51886,0.02955,0.09296]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":10132.0,"contact_point_centroid":[0.52103,0.04849,0.09142],"force_p95":0.10364,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28806,"mean_force":0.06597,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51854,0.02955,0.08949]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8172.0,"contact_point_centroid":[0.54786,0.05941,0.12614],"force_p95":0.13768,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26052,"mean_force":0.09647,"phase_index":5.0,"phase_name":"approach_2","phase_type":"approach","tcp_position_centroid":[0.54243,0.07783,0.12799]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8794.0,"contact_point_centroid":[0.54695,0.09389,0.12663],"force_p95":0.13352,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24686,"mean_force":0.08866,"phase_index":5.0,"phase_name":"approach_2","phase_type":"approach","tcp_position_centroid":[0.54124,0.07569,0.12857]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53052,0.03063,-0.00209],"force_p95":0.14746,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.20281,"mean_force":0.12936,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51849,0.02985,0.04461]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5680.0,"contact_point_centroid":[0.52635,0.01061,0.14969],"force_p95":0.09457,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15155,"mean_force":0.07363,"phase_index":4.0,"phase_name":"regrasp","phase_type":"grasp","tcp_position_centroid":[0.52031,0.02929,0.14844]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5702.0,"contact_point_centroid":[0.52633,0.048,0.14958],"force_p95":0.09445,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15135,"mean_force":0.07348,"phase_index":4.0,"phase_name":"regrasp","phase_type":"grasp","tcp_position_centroid":[0.52031,0.02929,0.14844]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4094.0,"contact_point_centroid":[0.51785,0.01056,0.046],"force_p95":0.07895,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14073,"mean_force":0.05186,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51728,0.02977,0.04322]},{"body_a":"world","body_b":"grasp_target","contact_count":3996.0,"contact_point_centroid":[0.5305,0.03079,-0.00196],"force_p95":0.12459,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12275,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51066,0.01403,0.20762]},{"body_a":"world","body_b":"grasp_target","contact_count":3472.0,"contact_point_centroid":[0.5305,0.03079,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.52213,0.02815,0.08547]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.56941,0.13772,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.59187,0.17547,0.11997]},{"body_a":"world","body_b":"grasp_target","contact_count":2768.0,"contact_point_centroid":[0.56941,0.13772,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":7.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.59202,0.17549,0.18714]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4945.0,"contact_point_centroid":[0.51786,0.04888,0.04503],"force_p95":0.07153,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07507,"mean_force":0.0446,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51729,0.02977,0.04322]},{"body_a":"left_finger","body_b":"right_finger","contact_count":6231.0,"contact_point_centroid":[0.59231,0.1704,0.11462],"force_p95":0.01098,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01627,"mean_force":0.01048,"phase_index":5.0,"phase_name":"approach_2","phase_type":"approach","tcp_position_centroid":[0.59165,0.17037,0.11247]}],"total_contact_groups":17},"final_pose_error":0.01547,"key_states":{"actual_goal_position":[0.60153,0.17858,0.10809],"final_object_position":[0.56941,0.13772,0.02602],"final_tcp_position":[0.598,0.17737,0.24308],"realised_goal_position":[0.60153,0.17858,0.10809],"realised_object_initial_position":[0.5305,0.03079,0.03]},"peak_contact_force":273004.16358,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.03],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18162,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3996.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_pre_grasp","tcp_end":[0.52109,0.02528,0.1369],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.11141,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":868.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3472.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.5253,0.0303,0.05254],"tcp_start":[0.52109,0.02528,0.1369],"tcp_to_object_dist_end":0.02703,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53043,0.02991,0.02569],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18425,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.14305,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10839.0,"raw_peak_contact_force":0.20281,"tcp_end":[0.51725,0.02977,0.04318],"tcp_start":[0.5253,0.0303,0.05254],"tcp_to_object_dist_end":0.0219,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":29.0,"n_steps":654.0,"n_steps_budget":720.0,"object_pos_end":[0.53856,0.02985,0.13191],"object_pos_start":[0.53043,0.02991,0.02569],"object_to_goal_dist_end":0.16326,"object_to_goal_dist_start":0.18425,"object_z_max":0.13178,"peak_contact_force":0.08748,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":20450.0,"raw_peak_contact_force":0.43282,"subtask_id":"lift_clearance","tcp_end":[0.52575,0.02964,0.1564],"tcp_start":[0.51725,0.02977,0.04318],"tcp_to_object_dist_end":0.02763,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":24.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.52663,0.02914,0.11843],"object_pos_start":[0.53856,0.02985,0.13191],"object_to_goal_dist_end":0.16748,"object_to_goal_dist_start":0.16326,"object_z_max":0.13196,"peak_contact_force":0.09415,"phase_name":"regrasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11382.0,"raw_peak_contact_force":0.15155,"tcp_end":[0.51916,0.02922,0.14677],"tcp_start":[0.52575,0.02964,0.1564],"tcp_to_object_dist_end":0.0293,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":2461.0,"n_steps_budget":1000.0,"object_pos_end":[0.56866,0.13742,0.02617],"object_pos_start":[0.52663,0.02914,0.11843],"object_to_goal_dist_end":0.09739,"object_to_goal_dist_start":0.16748,"object_z_max":0.11843,"peak_contact_force":273004.16358,"phase_name":"approach_2","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":29444.0,"raw_peak_contact_force":1.00368,"subtask_id":"reach_pre_place","tcp_end":[0.59661,0.17698,0.11902],"tcp_start":[0.59628,0.17614,0.1188],"tcp_to_object_dist_end":0.10472,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.56941,0.13772,0.02602],"object_pos_start":[0.56941,0.13772,0.02602],"object_to_goal_dist_end":0.09715,"object_to_goal_dist_start":0.09715,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1026.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.58998,0.17484,0.13962],"tcp_start":[0.59661,0.17698,0.11902],"tcp_to_object_dist_end":0.12127,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":692.0,"n_steps_budget":750.0,"object_pos_end":[0.56941,0.13772,0.02602],"object_pos_start":[0.56941,0.13772,0.02602],"object_to_goal_dist_end":0.09715,"object_to_goal_dist_start":0.09715,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2768.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.598,0.17737,0.24308],"tcp_start":[0.58998,0.17484,0.13962],"tcp_to_object_dist_end":0.22249,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.61963,"average_solve_count":163.0,"average_success_count":163.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_2.transport_speed":0.19884,"lift_1.lift_height":0.12021,"lift_1.lift_speed":0.13654},"optimized_scores":{"best_composite_score":0.22305,"best_fitness_score":0.55305,"best_task_score":0.17635},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":7969.0,"contact_point_centroid":[0.54184,0.07855,-0.00209],"force_p95":0.12271,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.37844,"mean_force":0.12792,"phase_index":5.0,"phase_name":"approach_2","phase_type":"approach","tcp_position_centroid":[0.56279,0.14407,0.22311]},{"body_a":"world","body_b":"grasp_target","contact_count":149.0,"contact_point_centroid":[0.50188,-0.01528,-0.00122],"force_p95":0.23609,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.40793,"mean_force":0.05935,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48999,-0.01544,0.04628]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":9841.0,"contact_point_centroid":[0.49445,0.00371,0.08658],"force_p95":0.08783,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27035,"mean_force":0.05622,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49261,-0.01537,0.08388]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6045.0,"contact_point_centroid":[0.50733,0.03131,0.13645],"force_p95":0.11166,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26845,"mean_force":0.07521,"phase_index":5.0,"phase_name":"approach_2","phase_type":"approach","tcp_position_centroid":[0.50159,0.01275,0.13694]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":10174.0,"contact_point_centroid":[0.4943,-0.03443,0.08537],"force_p95":0.08709,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26732,"mean_force":0.05455,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49253,-0.01537,0.0831]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5780.0,"contact_point_centroid":[0.50635,-0.00785,0.13536],"force_p95":0.13316,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25763,"mean_force":0.07849,"phase_index":5.0,"phase_name":"approach_2","phase_type":"approach","tcp_position_centroid":[0.50072,0.0108,0.13584]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50381,-0.0156,-0.00203],"force_p95":0.13071,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.16011,"mean_force":0.1252,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49233,-0.01548,0.04606]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5722.0,"contact_point_centroid":[0.49781,0.00345,0.1265],"force_p95":0.10184,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14692,"mean_force":0.07332,"phase_index":4.0,"phase_name":"regrasp","phase_type":"grasp","tcp_position_centroid":[0.49303,-0.01524,0.12604]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6122.0,"contact_point_centroid":[0.49747,-0.03389,0.12634],"force_p95":0.09642,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14652,"mean_force":0.06895,"phase_index":4.0,"phase_name":"regrasp","phase_type":"grasp","tcp_position_centroid":[0.49305,-0.01524,0.12606]},{"body_a":"world","body_b":"grasp_target","contact_count":3584.0,"contact_point_centroid":[0.50382,-0.01567,-0.00196],"force_p95":0.12593,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12276,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49856,-0.00759,0.20286]},{"body_a":"world","body_b":"grasp_target","contact_count":1916.0,"contact_point_centroid":[0.50382,-0.01567,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49781,-0.0153,0.07671]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.54186,0.07857,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.58095,0.18505,0.26012]},{"body_a":"world","body_b":"grasp_target","contact_count":2768.0,"contact_point_centroid":[0.54186,0.07857,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":7.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.58152,0.18524,0.32742]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5097.0,"contact_point_centroid":[0.49045,0.00385,0.04904],"force_p95":0.06525,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0816,"mean_force":0.04292,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49117,-0.01547,0.04481]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5850.0,"contact_point_centroid":[0.49056,-0.0347,0.04808],"force_p95":0.0599,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07735,"mean_force":0.03803,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49117,-0.01547,0.04481]},{"body_a":"left_finger","body_b":"right_finger","contact_count":8251.0,"contact_point_centroid":[0.56468,0.14718,0.22748],"force_p95":0.011,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01631,"mean_force":0.01044,"phase_index":5.0,"phase_name":"approach_2","phase_type":"approach","tcp_position_centroid":[0.56423,0.14717,0.22524]}],"total_contact_groups":17},"final_pose_error":0.01481,"key_states":{"actual_goal_position":[0.58691,0.18745,0.24812],"final_object_position":[0.54186,0.07857,0.01602],"final_tcp_position":[0.58551,0.18673,0.38339],"realised_goal_position":[0.58691,0.18745,0.24812],"realised_object_initial_position":[0.50382,-0.01567,0.03]},"peak_contact_force":1.37844,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":897.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.03],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.30942,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3584.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_pre_grasp","tcp_end":[0.49945,-0.01498,0.11224],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.08633,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":479.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1916.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.49888,-0.01557,0.0532],"tcp_start":[0.49945,-0.01498,0.11224],"tcp_to_object_dist_end":0.02763,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":49.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50373,-0.01539,0.02587],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31218,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.12955,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12747.0,"raw_peak_contact_force":0.16011,"tcp_end":[0.49114,-0.01547,0.04477],"tcp_start":[0.49888,-0.01557,0.0532],"tcp_to_object_dist_end":0.02271,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":28.0,"n_steps":527.0,"n_steps_budget":600.0,"object_pos_end":[0.51251,-0.01535,0.11001],"object_pos_start":[0.50373,-0.01539,0.02587],"object_to_goal_dist_end":0.25639,"object_to_goal_dist_start":0.31218,"object_z_max":0.10989,"peak_contact_force":0.08682,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":20164.0,"raw_peak_contact_force":0.40793,"subtask_id":"lift_clearance","tcp_end":[0.49883,-0.01533,0.13349],"tcp_start":[0.49114,-0.01547,0.04477],"tcp_to_object_dist_end":0.02717,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":30.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.49922,-0.01527,0.09695],"object_pos_start":[0.51251,-0.01535,0.11001],"object_to_goal_dist_end":0.26765,"object_to_goal_dist_start":0.25639,"object_z_max":0.11005,"peak_contact_force":0.09022,"phase_name":"regrasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11844.0,"raw_peak_contact_force":0.14692,"tcp_end":[0.49209,-0.01522,0.12484],"tcp_start":[0.49883,-0.01533,0.13349],"tcp_to_object_dist_end":0.02879,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":2559.0,"n_steps_budget":1000.0,"object_pos_end":[0.54186,0.07857,0.01602],"object_pos_start":[0.49922,-0.01527,0.09695],"object_to_goal_dist_end":0.2603,"object_to_goal_dist_start":0.26765,"object_z_max":0.12283,"peak_contact_force":0.12263,"phase_name":"approach_2","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":28045.0,"raw_peak_contact_force":1.37844,"subtask_id":"reach_pre_place","tcp_end":[0.58379,0.18613,0.25909],"tcp_start":[0.58264,0.18366,0.25737],"tcp_to_object_dist_end":0.26909,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54186,0.07857,0.01602],"object_pos_start":[0.54186,0.07857,0.01602],"object_to_goal_dist_end":0.2603,"object_to_goal_dist_start":0.2603,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1025.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.57994,0.18463,0.27981],"tcp_start":[0.58379,0.18613,0.25909],"tcp_to_object_dist_end":0.28685,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":692.0,"n_steps_budget":750.0,"object_pos_end":[0.54186,0.07857,0.01602],"object_pos_start":[0.54186,0.07857,0.01602],"object_to_goal_dist_end":0.2603,"object_to_goal_dist_start":0.2603,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2768.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.58551,0.18673,0.38339],"tcp_start":[0.57994,0.18463,0.27981],"tcp_to_object_dist_end":0.38544,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```