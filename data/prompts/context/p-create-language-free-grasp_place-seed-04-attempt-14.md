## Search State

- **Seed**: 4
- **Iteration**: 15 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 14 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 6 | 0.1391 | 0.31 | ❌ rejected |
| 13 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | admittance_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 7 | 0.2304 | 0.34 | ✅ accepted |
| 12 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | impedance_control | admittance_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 7 | 0.2299 | 0.34 | ❌ rejected |
| 11 | approach → descend → grasp → lift → grasp → approach → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | — | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | time_limit | pose_tolerance | time_limit | pose_tolerance | 3 | 0.2898 | 0.31 | ❌ rejected |
| 10 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | impedance_control | admittance_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 7 | 0.2304 | 0.34 | ✅ accepted |

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

## Current Skill (Q=0.139) — your mutation base

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
  - 0.18
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
      distance: 0.15
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
      - 0.1
      - 0.25
      default: 0.15
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
  control: position_control
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
  - id: grasp_hold_guard
    when: after_phase
    predicate: bilateral_grasp
    threshold: 0.001
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
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=world_z, distance=0.15, mode=replace_offset_projection, sign=positive}, tolerance=0.01
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
    - id=grasp_hold_guard, when=after_phase, predicate=bilateral_grasp, on_failure=retry, threshold=0.001
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

- **Composite score**: 0.139
- **task_score** (E): 0.309
- **fitness_score**: 0.619  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.480

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1678 |
| descend_1 | 1.00 | 1.00 | 0.0817 |
| grasp_1 | 1.00 | 1.00 | 0.0122 |
| lift_1 | 1.00 | 1.00 | 0.1156 |
| approach_2 | 0.67 | 1.00 | 0.0021 |
| descend_2 | 1.00 | 1.00 | 0.1835 |
| release_1 | 1.00 | 1.00 | 0.0203 |
| retract_1 | 1.00 | 1.00 | 0.1067 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.516, 0.004, 0.135) | (0.526, 0.005, 0.030)→(0.526, 0.005, 0.026) | 0.246→0.249 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.516, 0.004, 0.135)→(0.521, 0.005, 0.054) | (0.526, 0.005, 0.026)→(0.526, 0.005, 0.026) | 0.249→0.249 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_1 | grasp | 1.00 / step_budget | (0.521, 0.005, 0.054)→(0.513, 0.005, 0.045) | (0.526, 0.005, 0.026)→(0.526, 0.005, 0.026) | 0.249→0.249 | 1.00 / 44.667 | 0.136 | 0.172 |
| lift_1 | lift | 1.00 / step_budget | (0.513, 0.005, 0.045)→(0.521, 0.005, 0.160) | (0.526, 0.005, 0.026)→(0.536, 0.005, 0.136) | 0.249→0.199 | 1.00 / 25.000 | 0.100 | 0.420 |
| approach_2 | approach | 0.67 / step_budget | (0.610, 0.173, 0.373)→(0.611, 0.174, 0.375) | (0.536, 0.005, 0.136)→(0.565, 0.092, 0.016) | 0.199→0.192 | 1.00 / 8.000 | 3249.725 | 1.767 |
| descend_2 | descend | 1.00 / step_budget | (0.611, 0.174, 0.375)→(0.609, 0.174, 0.191) | (0.565, 0.092, 0.016)→(0.565, 0.092, 0.016) | 0.192→0.192 | 1.00 / 8.000 | 3249.686 | 0.123 |
| release_1 | release | 1.00 / step_budget | (0.609, 0.174, 0.191)→(0.603, 0.172, 0.211) | (0.565, 0.092, 0.016)→(0.565, 0.092, 0.016) | 0.192→0.192 | 1.00 / 4.000 | 0.123 | 0.123 |
| retract_1 | retract | 1.00 / step_budget | (0.603, 0.172, 0.211)→(0.610, 0.174, 0.317) | (0.565, 0.092, 0.016)→(0.565, 0.092, 0.016) | 0.192→0.192 | 1.00 / 4.000 | 0.123 | 0.123 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.509
- phase_score: 0.600
- phase_breakdown.lift_clearance_score: 0.114
- phase_breakdown.place_goal_score: 0.822
- phase_breakdown.reach_pre_grasp_score: 0.560
- phase_breakdown.reach_pre_place_score: 0.683
- grasp_place_fitness: 0.720

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.720
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.509
- **Median Q (composite search score)**: 0.108
- **K-run variance**: 0.0054
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.418


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.44484,"average_solve_count":281.0,"average_success_count":281.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_2.transport_speed":0.48985,"approach_2.transport_z_offset":0.19103,"descend_2.place_speed":0.02134,"descend_2.placement_tolerance":0.01087,"lift_1.lift_height":0.15562,"lift_1.lift_speed":0.12355},"optimized_scores":{"best_composite_score":0.10783,"best_fitness_score":0.58783,"best_task_score":0.2512},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":7651.0,"contact_point_centroid":[0.582,0.06872,-0.00214],"force_p95":0.12275,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.61027,"mean_force":0.12922,"phase_index":4.0,"phase_name":"approach_2","phase_type":"approach","tcp_position_centroid":[0.62677,0.1299,0.34136]},{"body_a":"world","body_b":"grasp_target","contact_count":81.0,"contact_point_centroid":[0.54269,0.00089,-0.00132],"force_p95":0.37501,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.40042,"mean_force":0.07852,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52925,0.00086,0.04745]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3003.0,"contact_point_centroid":[0.55223,0.03355,0.17677],"force_p95":0.14021,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29806,"mean_force":0.08354,"phase_index":4.0,"phase_name":"approach_2","phase_type":"approach","tcp_position_centroid":[0.54605,0.01494,0.17701]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2973.0,"contact_point_centroid":[0.55212,-0.00387,0.17645],"force_p95":0.14434,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28714,"mean_force":0.08317,"phase_index":4.0,"phase_name":"approach_2","phase_type":"approach","tcp_position_centroid":[0.5459,0.01473,0.17673]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5717.0,"contact_point_centroid":[0.53497,-0.01804,0.09766],"force_p95":0.1118,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2849,"mean_force":0.0723,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.5322,0.00089,0.09617]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6280.0,"contact_point_centroid":[0.53533,0.01975,0.09751],"force_p95":0.10609,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2725,"mean_force":0.06721,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.53218,0.00089,0.09576]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.54431,0.00113,-0.00203],"force_p95":0.13256,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.15292,"mean_force":0.1255,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.5315,0.0009,0.04756]},{"body_a":"world","body_b":"grasp_target","contact_count":3996.0,"contact_point_centroid":[0.54431,0.00113,-0.00196],"force_p95":0.12459,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12275,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.5152,0.00044,0.21539]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.54431,0.00113,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.53236,0.00089,0.09781]},{"body_a":"world","body_b":"grasp_target","contact_count":1996.0,"contact_point_centroid":[0.58201,0.06874,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.64552,0.1572,0.29698]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.58201,0.06874,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.64029,0.15589,0.19917]},{"body_a":"world","body_b":"grasp_target","contact_count":2888.0,"contact_point_centroid":[0.58201,0.06874,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":7.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.64066,0.15593,0.26697]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4951.0,"contact_point_centroid":[0.53151,-0.01832,0.04826],"force_p95":0.06907,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10568,"mean_force":0.04421,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53028,0.00088,0.04611]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5033.0,"contact_point_centroid":[0.53168,0.0201,0.04906],"force_p95":0.06688,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08563,"mean_force":0.04331,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53028,0.00088,0.04611]},{"body_a":"left_finger","body_b":"right_finger","contact_count":7956.0,"contact_point_centroid":[0.62889,0.13218,0.34694],"force_p95":0.01099,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01651,"mean_force":0.01046,"phase_index":4.0,"phase_name":"approach_2","phase_type":"approach","tcp_position_centroid":[0.62838,0.13216,0.34468]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2136.0,"contact_point_centroid":[0.64616,0.15723,0.29892],"force_p95":0.01095,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01269,"mean_force":0.01042,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.64552,0.1572,0.29671]}],"total_contact_groups":17},"final_pose_error":0.01614,"key_states":{"actual_goal_position":[0.64762,0.15808,0.1911],"final_object_position":[0.58201,0.06874,0.01602],"final_tcp_position":[0.64555,0.15732,0.32512],"realised_goal_position":[0.64762,0.15808,0.1911],"realised_object_initial_position":[0.54431,0.00113,0.03]},"peak_contact_force":273011.03406,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.03],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.24751,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3996.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_pre_grasp","tcp_end":[0.52806,0.00077,0.15679],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.13178,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.53851,0.00103,0.05599],"tcp_start":[0.52806,0.00077,0.15679],"tcp_to_object_dist_end":0.03053,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54422,0.00107,0.02586],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.2503,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.1348,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11784.0,"raw_peak_contact_force":0.15292,"tcp_end":[0.53025,0.00088,0.04607],"tcp_start":[0.53851,0.00103,0.05599],"tcp_to_object_dist_end":0.02457,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":24.0,"n_steps":394.0,"n_steps_budget":720.0,"object_pos_end":[0.5538,0.00115,0.13692],"object_pos_start":[0.54422,0.00107,0.02586],"object_to_goal_dist_end":0.19071,"object_to_goal_dist_start":0.2503,"object_z_max":0.13668,"peak_contact_force":0.09936,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":12078.0,"raw_peak_contact_force":0.40042,"subtask_id":"lift_clearance","tcp_end":[0.53914,0.00099,0.16235],"tcp_start":[0.53025,0.00088,0.04607],"tcp_to_object_dist_end":0.02934,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":2265.0,"n_steps_budget":1000.0,"object_pos_end":[0.58201,0.06874,0.01602],"object_pos_start":[0.5538,0.00115,0.13692],"object_to_goal_dist_end":0.20723,"object_to_goal_dist_start":0.19071,"object_z_max":0.17006,"peak_contact_force":0.12263,"phase_name":"approach_2","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":21583.0,"raw_peak_contact_force":1.61027,"subtask_id":"reach_pre_place","tcp_end":[0.64689,0.15757,0.39179],"tcp_start":[0.64629,0.15684,0.39057],"tcp_to_object_dist_end":0.39154,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":499.0,"n_steps_budget":1000.0,"object_pos_end":[0.58201,0.06874,0.01602],"object_pos_start":[0.58201,0.06874,0.01602],"object_to_goal_dist_end":0.20723,"object_to_goal_dist_start":0.20723,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4132.0,"raw_peak_contact_force":0.12263,"subtask_id":"place_goal","tcp_end":[0.64432,0.15708,0.20026],"tcp_start":[0.64689,0.15757,0.39179],"tcp_to_object_dist_end":0.21361,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.58201,0.06874,0.01602],"object_pos_start":[0.58201,0.06874,0.01602],"object_to_goal_dist_end":0.20723,"object_to_goal_dist_start":0.20723,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1021.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.6389,0.15544,0.21828],"tcp_start":[0.64432,0.15708,0.20026],"tcp_to_object_dist_end":0.2273,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":722.0,"n_steps_budget":780.0,"object_pos_end":[0.58201,0.06874,0.01602],"object_pos_start":[0.58201,0.06874,0.01602],"object_to_goal_dist_end":0.20723,"object_to_goal_dist_start":0.20723,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2888.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.64555,0.15732,0.32512],"tcp_start":[0.6389,0.15544,0.21828],"tcp_to_object_dist_end":0.32776,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.38372,"average_solve_count":258.0,"average_success_count":258.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_2.transport_speed":0.30619,"approach_2.transport_z_offset":0.15046,"descend_2.place_speed":0.03438,"descend_2.placement_tolerance":0.01087,"lift_1.lift_height":0.15373,"lift_1.lift_speed":0.1282},"optimized_scores":{"best_composite_score":0.24045,"best_fitness_score":0.72045,"best_task_score":0.50883},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":5875.0,"contact_point_centroid":[0.58928,0.13803,-0.00217],"force_p95":0.12313,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.77525,"mean_force":0.13032,"phase_index":4.0,"phase_name":"approach_2","phase_type":"approach","tcp_position_centroid":[0.5913,0.16464,0.25037]},{"body_a":"world","body_b":"grasp_target","contact_count":79.0,"contact_point_centroid":[0.52838,0.02947,-0.00137],"force_p95":0.42064,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.44664,"mean_force":0.08671,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51623,0.02968,0.04461]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6675.0,"contact_point_centroid":[0.54663,0.04684,0.17946],"force_p95":0.13786,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.40169,"mean_force":0.08567,"phase_index":4.0,"phase_name":"approach_2","phase_type":"approach","tcp_position_centroid":[0.54073,0.06552,0.17834]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5664.0,"contact_point_centroid":[0.52184,0.01067,0.09749],"force_p95":0.10854,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.3099,"mean_force":0.07105,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.5191,0.02957,0.09529]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6030.0,"contact_point_centroid":[0.52142,0.04845,0.09456],"force_p95":0.10807,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29404,"mean_force":0.06803,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51886,0.02957,0.09265]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":7829.0,"contact_point_centroid":[0.54852,0.08728,0.18106],"force_p95":0.10706,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2426,"mean_force":0.07551,"phase_index":4.0,"phase_name":"approach_2","phase_type":"approach","tcp_position_centroid":[0.5424,0.06886,0.18041]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53052,0.03063,-0.00209],"force_p95":0.14746,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.20281,"mean_force":0.12936,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51849,0.02985,0.04461]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4094.0,"contact_point_centroid":[0.51785,0.01056,0.046],"force_p95":0.07895,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14073,"mean_force":0.05186,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51728,0.02977,0.04322]},{"body_a":"world","body_b":"grasp_target","contact_count":3996.0,"contact_point_centroid":[0.5305,0.03079,-0.00196],"force_p95":0.12459,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12275,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51066,0.01403,0.20762]},{"body_a":"world","body_b":"grasp_target","contact_count":3472.0,"contact_point_centroid":[0.5305,0.03079,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.52213,0.02815,0.08547]},{"body_a":"world","body_b":"grasp_target","contact_count":1736.0,"contact_point_centroid":[0.58931,0.13802,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.59685,0.17695,0.19328]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.58931,0.13802,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.59179,0.17545,0.11693]},{"body_a":"world","body_b":"grasp_target","contact_count":2888.0,"contact_point_centroid":[0.58931,0.13802,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":7.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.59198,0.17547,0.18571]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4945.0,"contact_point_centroid":[0.51786,0.04888,0.04503],"force_p95":0.07153,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07507,"mean_force":0.0446,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51729,0.02977,0.04322]},{"body_a":"left_finger","body_b":"right_finger","contact_count":6083.0,"contact_point_centroid":[0.59249,0.16602,0.25382],"force_p95":0.011,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01526,"mean_force":0.01046,"phase_index":4.0,"phase_name":"approach_2","phase_type":"approach","tcp_position_centroid":[0.59198,0.166,0.25153]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1861.0,"contact_point_centroid":[0.59741,0.177,0.19565],"force_p95":0.01095,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01271,"mean_force":0.0104,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.59685,0.17695,0.19334]}],"total_contact_groups":17},"final_pose_error":0.01535,"key_states":{"actual_goal_position":[0.60153,0.17858,0.10809],"final_object_position":[0.58931,0.13802,0.01602],"final_tcp_position":[0.59802,0.17736,0.24319],"realised_goal_position":[0.60153,0.17858,0.10809],"realised_object_initial_position":[0.5305,0.03079,0.03]},"peak_contact_force":9748.92927,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.03],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18162,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3996.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_pre_grasp","tcp_end":[0.52109,0.02528,0.1369],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.11141,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":868.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3472.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.5253,0.0303,0.05254],"tcp_start":[0.52109,0.02528,0.1369],"tcp_to_object_dist_end":0.02703,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53043,0.02991,0.02569],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18425,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.14305,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10839.0,"raw_peak_contact_force":0.20281,"tcp_end":[0.51725,0.02977,0.04318],"tcp_start":[0.5253,0.0303,0.05254],"tcp_to_object_dist_end":0.0219,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":384.0,"n_steps_budget":690.0,"object_pos_end":[0.54082,0.02991,0.1374],"object_pos_start":[0.53043,0.02991,0.02569],"object_to_goal_dist_end":0.16324,"object_to_goal_dist_start":0.18425,"object_z_max":0.13715,"peak_contact_force":0.11402,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":11773.0,"raw_peak_contact_force":0.44664,"subtask_id":"lift_clearance","tcp_end":[0.52547,0.02964,0.16013],"tcp_start":[0.51725,0.02977,0.04318],"tcp_to_object_dist_end":0.02743,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":2167.0,"n_steps_budget":1000.0,"object_pos_end":[0.58931,0.13802,0.01602],"object_pos_start":[0.54082,0.02991,0.1374],"object_to_goal_dist_end":0.10135,"object_to_goal_dist_start":0.16324,"object_z_max":0.17229,"peak_contact_force":9748.92927,"phase_name":"approach_2","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":26462.0,"raw_peak_contact_force":1.77525,"subtask_id":"reach_pre_place","tcp_end":[0.59863,0.17749,0.26928],"tcp_start":[0.59829,0.17673,0.26828],"tcp_to_object_dist_end":0.25649,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":434.0,"n_steps_budget":1000.0,"object_pos_end":[0.58931,0.13802,0.01602],"object_pos_start":[0.58931,0.13802,0.01602],"object_to_goal_dist_end":0.10135,"object_to_goal_dist_start":0.10135,"object_z_max":0.01602,"peak_contact_force":9748.81178,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3597.0,"raw_peak_contact_force":0.12263,"subtask_id":"place_goal","tcp_end":[0.59693,0.1771,0.11662],"tcp_start":[0.59863,0.17749,0.26928],"tcp_to_object_dist_end":0.10819,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.58931,0.13802,0.01602],"object_pos_start":[0.58931,0.13802,0.01602],"object_to_goal_dist_end":0.10135,"object_to_goal_dist_start":0.10135,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1024.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.58992,0.17483,0.13666],"tcp_start":[0.59693,0.1771,0.11662],"tcp_to_object_dist_end":0.12613,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":722.0,"n_steps_budget":780.0,"object_pos_end":[0.58931,0.13802,0.01602],"object_pos_start":[0.58931,0.13802,0.01602],"object_to_goal_dist_end":0.10135,"object_to_goal_dist_start":0.10135,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2888.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.59802,0.17736,0.24319],"tcp_start":[0.58992,0.17483,0.13666],"tcp_to_object_dist_end":0.23072,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.79279,"average_solve_count":222.0,"average_success_count":222.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_2.transport_speed":0.32547,"approach_2.transport_z_offset":0.20455,"descend_2.place_speed":0.09011,"descend_2.placement_tolerance":0.0106,"lift_1.lift_height":0.15098,"lift_1.lift_speed":0.09826},"optimized_scores":{"best_composite_score":0.06899,"best_fitness_score":0.54899,"best_task_score":0.16822},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":7660.0,"contact_point_centroid":[0.52415,0.07041,-0.00215],"force_p95":0.12283,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.91472,"mean_force":0.13049,"phase_index":4.0,"phase_name":"approach_2","phase_type":"approach","tcp_position_centroid":[0.56521,0.14022,0.38424]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3676.0,"contact_point_centroid":[0.5097,0.02034,0.17944],"force_p95":0.12959,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.57001,"mean_force":0.07966,"phase_index":4.0,"phase_name":"approach_2","phase_type":"approach","tcp_position_centroid":[0.50335,0.00165,0.17795]},{"body_a":"world","body_b":"grasp_target","contact_count":76.0,"contact_point_centroid":[0.50237,-0.01543,-0.00133],"force_p95":0.35986,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.41194,"mean_force":0.08681,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49017,-0.01545,0.04609]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6317.0,"contact_point_centroid":[0.49476,0.00366,0.09661],"force_p95":0.10422,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27023,"mean_force":0.06258,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49264,-0.01538,0.09387]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6506.0,"contact_point_centroid":[0.4947,-0.03441,0.0951],"force_p95":0.1033,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27007,"mean_force":0.0616,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49257,-0.01538,0.09284]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3608.0,"contact_point_centroid":[0.50921,-0.01819,0.17813],"force_p95":0.13115,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26966,"mean_force":0.07686,"phase_index":4.0,"phase_name":"approach_2","phase_type":"approach","tcp_position_centroid":[0.50289,0.00054,0.17641]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50381,-0.0156,-0.00203],"force_p95":0.13071,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.16011,"mean_force":0.1252,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49233,-0.01548,0.04606]},{"body_a":"world","body_b":"grasp_target","contact_count":3584.0,"contact_point_centroid":[0.50382,-0.01567,-0.00196],"force_p95":0.12593,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12276,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49856,-0.00759,0.20286]},{"body_a":"world","body_b":"grasp_target","contact_count":1916.0,"contact_point_centroid":[0.50382,-0.01567,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49781,-0.0153,0.07671]},{"body_a":"world","body_b":"grasp_target","contact_count":2128.0,"contact_point_centroid":[0.52408,0.07052,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.58607,0.18669,0.36164]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.52408,0.07052,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.58133,0.18526,0.25791]},{"body_a":"world","body_b":"grasp_target","contact_count":2888.0,"contact_point_centroid":[0.52408,0.07052,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":7.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.58172,0.18533,0.32642]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5097.0,"contact_point_centroid":[0.49045,0.00385,0.04904],"force_p95":0.06525,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0816,"mean_force":0.04292,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49117,-0.01547,0.04481]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5850.0,"contact_point_centroid":[0.49056,-0.0347,0.04808],"force_p95":0.0599,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07735,"mean_force":0.03803,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49117,-0.01547,0.04481]},{"body_a":"left_finger","body_b":"right_finger","contact_count":8103.0,"contact_point_centroid":[0.56631,0.14179,0.38893],"force_p95":0.011,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01566,"mean_force":0.01042,"phase_index":4.0,"phase_name":"approach_2","phase_type":"approach","tcp_position_centroid":[0.56592,0.14178,0.38664]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2271.0,"contact_point_centroid":[0.58657,0.18672,0.36385],"force_p95":0.01098,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01285,"mean_force":0.01044,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.58607,0.18669,0.36162]}],"total_contact_groups":17},"final_pose_error":0.01465,"key_states":{"actual_goal_position":[0.58691,0.18745,0.24812],"final_object_position":[0.52408,0.07052,0.01602],"final_tcp_position":[0.58555,0.18672,0.38355],"realised_goal_position":[0.58691,0.18745,0.24812],"realised_object_initial_position":[0.50382,-0.01567,0.03]},"peak_contact_force":273007.94786,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":897.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.03],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.30942,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3584.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_pre_grasp","tcp_end":[0.49945,-0.01498,0.11224],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.08633,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":479.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1916.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.49888,-0.01557,0.0532],"tcp_start":[0.49945,-0.01498,0.11224],"tcp_to_object_dist_end":0.02763,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":49.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50373,-0.01539,0.02587],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31218,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.12955,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12747.0,"raw_peak_contact_force":0.16011,"tcp_end":[0.49114,-0.01547,0.04477],"tcp_start":[0.49888,-0.01557,0.0532],"tcp_to_object_dist_end":0.02271,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":28.0,"n_steps":369.0,"n_steps_budget":870.0,"object_pos_end":[0.51464,-0.01532,0.13478],"object_pos_start":[0.50373,-0.01539,0.02587],"object_to_goal_dist_end":0.24328,"object_to_goal_dist_start":0.31218,"object_z_max":0.13451,"peak_contact_force":0.08706,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":12899.0,"raw_peak_contact_force":0.41194,"subtask_id":"lift_clearance","tcp_end":[0.49872,-0.01534,0.15758],"tcp_start":[0.49114,-0.01547,0.04477],"tcp_to_object_dist_end":0.02781,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":2314.0,"n_steps_budget":1000.0,"object_pos_end":[0.52408,0.07052,0.01602],"object_pos_start":[0.51464,-0.01532,0.13478],"object_to_goal_dist_end":0.26738,"object_to_goal_dist_start":0.24328,"object_z_max":0.1781,"peak_contact_force":0.12263,"phase_name":"approach_2","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":23047.0,"raw_peak_contact_force":1.91472,"subtask_id":"reach_pre_place","tcp_end":[0.58699,0.18696,0.46364],"tcp_start":[0.58607,0.18515,0.4609],"tcp_to_object_dist_end":0.46678,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":532.0,"n_steps_budget":1000.0,"object_pos_end":[0.52408,0.07052,0.01602],"object_pos_start":[0.52408,0.07052,0.01602],"object_to_goal_dist_end":0.26738,"object_to_goal_dist_start":0.26738,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4399.0,"raw_peak_contact_force":0.12263,"subtask_id":"place_goal","tcp_end":[0.58443,0.18646,0.25753],"tcp_start":[0.58699,0.18696,0.46364],"tcp_to_object_dist_end":0.27461,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.52408,0.07052,0.01602],"object_pos_start":[0.52408,0.07052,0.01602],"object_to_goal_dist_end":0.26738,"object_to_goal_dist_start":0.26738,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1026.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.58033,0.18482,0.27766],"tcp_start":[0.58443,0.18646,0.25753],"tcp_to_object_dist_end":0.29101,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":722.0,"n_steps_budget":780.0,"object_pos_end":[0.52408,0.07052,0.01602],"object_pos_start":[0.52408,0.07052,0.01602],"object_to_goal_dist_end":0.26738,"object_to_goal_dist_start":0.26738,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2888.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.58555,0.18672,0.38355],"tcp_start":[0.58033,0.18482,0.27766],"tcp_to_object_dist_end":0.39034,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```