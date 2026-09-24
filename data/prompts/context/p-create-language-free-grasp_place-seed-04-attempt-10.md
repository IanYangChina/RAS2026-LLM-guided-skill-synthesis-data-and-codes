## Search State

- **Seed**: 4
- **Iteration**: 11 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 10 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | impedance_control | admittance_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 7 | 0.2304 | 0.34 | ✅ accepted |
| 9 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 5 | -0.0137 | 0.22 | ❌ rejected |
| 8 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | impedance_control | impedance_control | admittance_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 7 | 0.2055 | 0.28 | ✅ accepted |
| 7 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | impedance_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 5 | 0.2108 | 0.26 | ✅ accepted |
| 6 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | impedance_control | impedance_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 3 | 0.2640 | 0.25 | ✅ accepted |

**Proposal policy**: task_score is 0.34 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.230) — your mutation base

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

- **Composite score**: 0.230
- **task_score** (E): 0.342
- **fitness_score**: 0.635  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.125
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.530

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1678 |
| descend_1 | 1.00 | 1.00 | 0.0817 |
| grasp_1 | 1.00 | 1.00 | 0.0122 |
| lift_1 | 0.00 | 1.00 | 0.0957 |
| approach_2 | 0.33 | 0.33 | 0.0544 |
| descend_2 | 1.00 | 1.00 | 0.0015 |
| release_1 | 1.00 | 1.00 | 0.0219 |
| retract_1 | 1.00 | 1.00 | 0.0827 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.516, 0.004, 0.135) | (0.526, 0.005, 0.030)→(0.526, 0.005, 0.026) | 0.246→0.249 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.516, 0.004, 0.135)→(0.521, 0.005, 0.054) | (0.526, 0.005, 0.026)→(0.526, 0.005, 0.026) | 0.249→0.249 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_1 | grasp | 1.00 / step_budget | (0.521, 0.005, 0.054)→(0.513, 0.005, 0.045) | (0.526, 0.005, 0.026)→(0.526, 0.005, 0.026) | 0.249→0.249 | 1.00 / 44.667 | 0.136 | 0.172 |
| lift_1 | lift | 0.00 / step_budget | (0.513, 0.005, 0.045)→(0.515, 0.005, 0.140) | (0.526, 0.005, 0.026)→(0.521, 0.005, 0.114) | 0.249→0.211 | 1.00 / 37.333 | 0.079 | 0.423 |
| approach_2 | approach | 0.33 / guard_failure | (0.553, 0.071, 0.230)→(0.575, 0.114, 0.255) | (0.521, 0.005, 0.114)→(0.589, 0.124, 0.099) | 0.211→0.143 | 0.33 / 5.333 | 0.055 | 0.227 |
| descend_2 | descend | 1.00 / force_exceeded | (0.575, 0.114, 0.255)→(0.575, 0.114, 0.254) | (0.589, 0.124, 0.094)→(0.590, 0.126, 0.074) | 0.147→0.163 | 1.00 / 5.667 | 622.987 | 0.077 |
| release_1 | release | 1.00 / step_budget | (0.575, 0.114, 0.254)→(0.571, 0.113, 0.275) | (0.590, 0.126, 0.074)→(0.592, 0.135, 0.016) | 0.163→0.174 | 1.00 / 4.000 | 0.125 | 1.834 |
| retract_1 | retract | 1.00 / step_budget | (0.571, 0.113, 0.275)→(0.608, 0.171, 0.321) | (0.592, 0.135, 0.016)→(0.592, 0.134, 0.016) | 0.174→0.174 | 1.00 / 4.000 | 0.123 | 0.125 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.540
- phase_score: 0.268
- phase_breakdown.lift_clearance_score: 0.097
- phase_breakdown.place_goal_score: 0.111
- phase_breakdown.reach_pre_grasp_score: 0.560
- phase_breakdown.reach_pre_place_score: 0.459
- grasp_place_fitness: 0.736

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.736
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.540
- **Median Q (composite search score)**: 0.203
- **K-run variance**: 0.0054
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.206


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.61481,"average_solve_count":135.0,"average_success_count":135.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_2.transport_speed":0.26883,"approach_2.transport_z_offset":0.17556,"descend_2.place_force_threshold":3.77158,"descend_2.place_speed":0.03133,"descend_2.place_z_offset":0.011,"lift_1.lift_height":0.24904,"lift_1.lift_speed":0.05906},"optimized_scores":{"best_composite_score":0.2026,"best_fitness_score":0.6076,"best_task_score":0.29076},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":790.0,"contact_point_centroid":[0.61772,0.10521,-0.00353],"force_p95":0.72722,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.01324,"mean_force":0.18653,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.59427,0.09252,0.26614]},{"body_a":"world","body_b":"grasp_target","contact_count":215.0,"contact_point_centroid":[0.54045,0.00065,-0.00115],"force_p95":0.21244,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.40757,"mean_force":0.07068,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52848,0.00085,0.04772]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":18911.0,"contact_point_centroid":[0.52971,-0.01826,0.09414],"force_p95":0.07752,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28314,"mean_force":0.05352,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52912,0.00085,0.09315]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":19395.0,"contact_point_centroid":[0.53029,0.01995,0.09359],"force_p95":0.07602,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27115,"mean_force":0.05252,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52908,0.00085,0.09213]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8343.0,"contact_point_centroid":[0.55601,0.01478,0.18026],"force_p95":0.1294,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22194,"mean_force":0.08317,"phase_index":4.0,"phase_name":"approach_2","phase_type":"approach","tcp_position_centroid":[0.55306,0.03331,0.18244]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8574.0,"contact_point_centroid":[0.55736,0.05285,0.18205],"force_p95":0.12439,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21197,"mean_force":0.08032,"phase_index":4.0,"phase_name":"approach_2","phase_type":"approach","tcp_position_centroid":[0.55384,0.03437,0.18392]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.54431,0.00113,-0.00203],"force_p95":0.13256,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.15292,"mean_force":0.1255,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.5315,0.0009,0.04756]},{"body_a":"world","body_b":"grasp_target","contact_count":3996.0,"contact_point_centroid":[0.54431,0.00113,-0.00196],"force_p95":0.12459,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12275,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.5152,0.00044,0.21539]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.54431,0.00113,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.53236,0.00089,0.09781]},{"body_a":"world","body_b":"grasp_target","contact_count":2408.0,"contact_point_centroid":[0.61784,0.10525,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":7.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.6164,0.12207,0.30383]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4951.0,"contact_point_centroid":[0.53151,-0.01832,0.04826],"force_p95":0.06907,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10568,"mean_force":0.04421,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53028,0.00088,0.04611]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5033.0,"contact_point_centroid":[0.53168,0.0201,0.04906],"force_p95":0.06688,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08563,"mean_force":0.04331,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53028,0.00088,0.04611]},{"body_a":"left_finger","body_b":"right_finger","contact_count":27.0,"contact_point_centroid":[0.59549,0.09279,0.26247],"force_p95":0.01621,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01621,"mean_force":0.0114,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.59545,0.09278,0.26003]}],"total_contact_groups":13},"final_pose_error":0.01423,"key_states":{"actual_goal_position":[0.64762,0.15808,0.1911],"final_object_position":[0.61784,0.10525,0.01602],"final_tcp_position":[0.64254,0.15334,0.32868],"realised_goal_position":[0.64762,0.15808,0.1911],"realised_object_initial_position":[0.54431,0.00113,0.03]},"peak_contact_force":5.02632,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.03],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.24751,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3996.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_pre_grasp","tcp_end":[0.52806,0.00077,0.15679],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.13178,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.53851,0.00103,0.05599],"tcp_start":[0.52806,0.00077,0.15679],"tcp_to_object_dist_end":0.03053,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54422,0.00107,0.02586],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.2503,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.1348,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11784.0,"raw_peak_contact_force":0.15292,"tcp_end":[0.53025,0.00088,0.04607],"tcp_start":[0.53851,0.00103,0.05599],"tcp_to_object_dist_end":0.02457,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":38.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53645,0.00114,0.11408],"object_pos_start":[0.54422,0.00107,0.02586],"object_to_goal_dist_end":0.20718,"object_to_goal_dist_start":0.2503,"object_z_max":0.11397,"peak_contact_force":0.07778,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":38521.0,"raw_peak_contact_force":0.40757,"subtask_id":"lift_clearance","tcp_end":[0.53225,0.0009,0.14164],"tcp_start":[0.53025,0.00088,0.04607],"tcp_to_object_dist_end":0.02788,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":841.0,"n_steps_budget":1000.0,"object_pos_end":[0.61481,0.10662,0.05977],"object_pos_start":[0.53645,0.00114,0.11408],"object_to_goal_dist_end":0.14482,"object_to_goal_dist_start":0.20718,"object_z_max":0.2134,"peak_contact_force":0.0,"phase_name":"approach_2","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":16917.0,"raw_peak_contact_force":0.22194,"subtask_id":"reach_pre_place","tcp_end":[0.59733,0.09282,0.26593],"tcp_start":[0.59735,0.09279,0.26595],"tcp_to_object_dist_end":0.20736,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":7.0,"n_steps_budget":1000.0,"object_pos_end":[0.61654,0.10876,0.027],"object_pos_start":[0.61519,0.1071,0.05277],"object_to_goal_dist_end":0.17415,"object_to_goal_dist_start":0.15096,"object_z_max":0.05277,"peak_contact_force":5.02632,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"place_goal","tcp_end":[0.59736,0.09306,0.2652],"tcp_start":[0.59733,0.09282,0.26593],"tcp_to_object_dist_end":0.23948,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.61784,0.10525,0.01602],"object_pos_start":[0.61654,0.10876,0.027],"object_to_goal_dist_end":0.18529,"object_to_goal_dist_start":0.17415,"object_z_max":0.027,"peak_contact_force":0.12261,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":817.0,"raw_peak_contact_force":2.01324,"tcp_end":[0.59327,0.09229,0.28593],"tcp_start":[0.59736,0.09306,0.2652],"tcp_to_object_dist_end":0.27134,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":602.0,"n_steps_budget":660.0,"object_pos_end":[0.61784,0.10525,0.01602],"object_pos_start":[0.61784,0.10525,0.01602],"object_to_goal_dist_end":0.18529,"object_to_goal_dist_start":0.18529,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2408.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.64254,0.15334,0.32868],"tcp_start":[0.59327,0.09229,0.28593],"tcp_to_object_dist_end":0.3173,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.63704,"average_solve_count":135.0,"average_success_count":135.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_2.transport_speed":0.23482,"approach_2.transport_z_offset":0.13043,"descend_2.place_force_threshold":5.28272,"descend_2.place_speed":0.05387,"descend_2.place_z_offset":0.01807,"lift_1.lift_height":0.21469,"lift_1.lift_speed":0.06087},"optimized_scores":{"best_composite_score":0.33114,"best_fitness_score":0.73614,"best_task_score":0.5402},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":437.0,"contact_point_centroid":[0.59817,0.18455,-0.00433],"force_p95":0.99597,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.75244,"mean_force":0.24109,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.58221,0.1567,0.2204]},{"body_a":"world","body_b":"grasp_target","contact_count":200.0,"contact_point_centroid":[0.52716,0.02918,-0.00119],"force_p95":0.23722,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.44228,"mean_force":0.07098,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51561,0.02964,0.04491]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":18405.0,"contact_point_centroid":[0.51789,0.01046,0.09392],"force_p95":0.08186,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29086,"mean_force":0.05508,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51655,0.02952,0.09197]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":18737.0,"contact_point_centroid":[0.51814,0.04859,0.09272],"force_p95":0.0796,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29045,"mean_force":0.05442,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51649,0.02952,0.09077]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":34.0,"contact_point_centroid":[0.59204,0.14039,0.20796],"force_p95":0.22047,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24351,"mean_force":0.13583,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.58687,0.15815,0.21447]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":127.0,"contact_point_centroid":[0.59337,0.13987,0.21115],"force_p95":0.1738,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23052,"mean_force":0.12051,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.58736,0.15806,0.21685]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":131.0,"contact_point_centroid":[0.59174,0.17466,0.2078],"force_p95":0.14049,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22957,"mean_force":0.05785,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.58647,0.15806,0.21357]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":11339.0,"contact_point_centroid":[0.55278,0.10479,0.17219],"force_p95":0.12461,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21635,"mean_force":0.08219,"phase_index":4.0,"phase_name":"approach_2","phase_type":"approach","tcp_position_centroid":[0.54799,0.08631,0.17335]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53052,0.03063,-0.00209],"force_p95":0.14746,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.20281,"mean_force":0.12936,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51849,0.02985,0.04461]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":10936.0,"contact_point_centroid":[0.55179,0.0665,0.17128],"force_p95":0.13212,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19237,"mean_force":0.08469,"phase_index":4.0,"phase_name":"approach_2","phase_type":"approach","tcp_position_centroid":[0.54729,0.08503,0.17255]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":128.0,"contact_point_centroid":[0.59278,0.17599,0.21151],"force_p95":0.15263,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18945,"mean_force":0.11022,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.58735,0.15806,0.21684]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4094.0,"contact_point_centroid":[0.51785,0.01056,0.046],"force_p95":0.07895,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14073,"mean_force":0.05186,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51728,0.02977,0.04322]},{"body_a":"world","body_b":"grasp_target","contact_count":3996.0,"contact_point_centroid":[0.5305,0.03079,-0.00196],"force_p95":0.12459,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12275,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51066,0.01403,0.20762]},{"body_a":"world","body_b":"grasp_target","contact_count":2052.0,"contact_point_centroid":[0.59781,0.18506,-0.00199],"force_p95":0.1233,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12943,"mean_force":0.12272,"phase_index":7.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.58847,0.16605,0.23897]},{"body_a":"world","body_b":"grasp_target","contact_count":3472.0,"contact_point_centroid":[0.5305,0.03079,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.52213,0.02815,0.08547]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4945.0,"contact_point_centroid":[0.51786,0.04888,0.04503],"force_p95":0.07153,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07507,"mean_force":0.0446,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51729,0.02977,0.04322]}],"total_contact_groups":16},"final_pose_error":0.0114,"key_states":{"actual_goal_position":[0.60153,0.17858,0.10809],"final_object_position":[0.59781,0.18506,0.01602],"final_tcp_position":[0.59705,0.17584,0.24797],"realised_goal_position":[0.60153,0.17858,0.10809],"realised_object_initial_position":[0.5305,0.03079,0.03]},"peak_contact_force":1573.09317,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.03],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18162,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3996.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_pre_grasp","tcp_end":[0.52109,0.02528,0.1369],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.11141,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":868.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3472.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.5253,0.0303,0.05254],"tcp_start":[0.52109,0.02528,0.1369],"tcp_to_object_dist_end":0.02703,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53043,0.02991,0.02569],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18425,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.14305,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10839.0,"raw_peak_contact_force":0.20281,"tcp_end":[0.51725,0.02977,0.04318],"tcp_start":[0.5253,0.0303,0.05254],"tcp_to_object_dist_end":0.0219,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":31.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.52775,0.02967,0.11769],"object_pos_start":[0.53043,0.02991,0.02569],"object_to_goal_dist_end":0.16647,"object_to_goal_dist_start":0.18425,"object_z_max":0.11758,"peak_contact_force":0.0908,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":37342.0,"raw_peak_contact_force":0.44228,"subtask_id":"lift_clearance","tcp_end":[0.52013,0.02957,0.14275],"tcp_start":[0.51725,0.02977,0.04318],"tcp_to_object_dist_end":0.0262,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":16.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.59306,0.15831,0.17936],"object_pos_start":[0.52775,0.02967,0.11769],"object_to_goal_dist_end":0.07458,"object_to_goal_dist_start":0.16647,"object_z_max":0.17933,"peak_contact_force":0.1637,"phase_name":"approach_2","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":22275.0,"raw_peak_contact_force":0.21635,"subtask_id":"reach_pre_place","tcp_end":[0.58736,0.15779,0.21784],"tcp_start":[0.52013,0.02957,0.14275],"tcp_to_object_dist_end":0.0389,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":14.0,"n_steps":16.0,"n_steps_budget":1000.0,"object_pos_end":[0.59339,0.15934,0.17534],"object_pos_start":[0.59306,0.15831,0.17936],"object_to_goal_dist_end":0.07042,"object_to_goal_dist_start":0.07458,"object_z_max":0.17936,"peak_contact_force":1573.09317,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":255.0,"raw_peak_contact_force":0.23052,"subtask_id":"place_goal","tcp_end":[0.5871,0.15819,0.21498],"tcp_start":[0.58736,0.15779,0.21784],"tcp_to_object_dist_end":0.04015,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.59804,0.18514,0.01616],"object_pos_start":[0.59339,0.15934,0.17534],"object_to_goal_dist_end":0.09223,"object_to_goal_dist_start":0.07042,"object_z_max":0.17534,"peak_contact_force":0.12978,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":602.0,"raw_peak_contact_force":1.75244,"tcp_end":[0.58206,0.15665,0.23563],"tcp_start":[0.5871,0.15819,0.21498],"tcp_to_object_dist_end":0.22189,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":513.0,"n_steps_budget":600.0,"object_pos_end":[0.59781,0.18506,0.01602],"object_pos_start":[0.59804,0.18514,0.01616],"object_to_goal_dist_end":0.09237,"object_to_goal_dist_start":0.09223,"object_z_max":0.01616,"peak_contact_force":0.12263,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2052.0,"raw_peak_contact_force":0.12943,"tcp_end":[0.59705,0.17584,0.24797],"tcp_start":[0.58206,0.15665,0.23563],"tcp_to_object_dist_end":0.23214,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.58621,"average_solve_count":145.0,"average_success_count":145.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_2.transport_speed":0.42613,"approach_2.transport_z_offset":0.17548,"descend_2.place_force_threshold":5.71105,"descend_2.place_speed":0.06232,"descend_2.place_z_offset":0.01935,"lift_1.lift_height":0.19356,"lift_1.lift_speed":0.05618},"optimized_scores":{"best_composite_score":0.15733,"best_fitness_score":0.56233,"best_task_score":0.19491},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":798.0,"contact_point_centroid":[0.55905,0.11321,-0.0037],"force_p95":0.76316,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.73602,"mean_force":0.18621,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.53802,0.09148,0.28333]},{"body_a":"world","body_b":"grasp_target","contact_count":187.0,"contact_point_centroid":[0.50031,-0.0153,-0.00114],"force_p95":0.2425,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.41842,"mean_force":0.06903,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48964,-0.01544,0.04639]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":20413.0,"contact_point_centroid":[0.49105,-0.03449,0.0911],"force_p95":0.07279,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2714,"mean_force":0.04981,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49056,-0.01538,0.08931]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":19065.0,"contact_point_centroid":[0.49103,0.00377,0.09196],"force_p95":0.07595,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26934,"mean_force":0.0529,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49061,-0.01538,0.09008]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":7185.0,"contact_point_centroid":[0.51163,0.00216,0.18331],"force_p95":0.11126,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24207,"mean_force":0.06852,"phase_index":4.0,"phase_name":"approach_2","phase_type":"approach","tcp_position_centroid":[0.50788,0.02094,0.18324]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":7360.0,"contact_point_centroid":[0.51224,0.04155,0.18559],"force_p95":0.1095,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22712,"mean_force":0.07001,"phase_index":4.0,"phase_name":"approach_2","phase_type":"approach","tcp_position_centroid":[0.50874,0.0228,0.18583]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50381,-0.0156,-0.00203],"force_p95":0.13071,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.16011,"mean_force":0.1252,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49233,-0.01548,0.04606]},{"body_a":"world","body_b":"grasp_target","contact_count":3584.0,"contact_point_centroid":[0.50382,-0.01567,-0.00196],"force_p95":0.12593,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12276,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49856,-0.00759,0.20286]},{"body_a":"world","body_b":"grasp_target","contact_count":3368.0,"contact_point_centroid":[0.55907,0.11315,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12264,"mean_force":0.12262,"phase_index":7.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.55882,0.13606,0.34145]},{"body_a":"world","body_b":"grasp_target","contact_count":1916.0,"contact_point_centroid":[0.50382,-0.01567,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49781,-0.0153,0.07671]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5097.0,"contact_point_centroid":[0.49045,0.00385,0.04904],"force_p95":0.06525,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0816,"mean_force":0.04292,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49117,-0.01547,0.04481]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5850.0,"contact_point_centroid":[0.49056,-0.0347,0.04808],"force_p95":0.0599,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07735,"mean_force":0.03803,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49117,-0.01547,0.04481]},{"body_a":"left_finger","body_b":"right_finger","contact_count":87.0,"contact_point_centroid":[0.53941,0.09175,0.27903],"force_p95":0.01519,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01559,"mean_force":0.01163,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.53923,0.09175,0.27703]}],"total_contact_groups":13},"final_pose_error":0.01344,"key_states":{"actual_goal_position":[0.58691,0.18745,0.24812],"final_object_position":[0.55907,0.11315,0.01602],"final_tcp_position":[0.58355,0.18249,0.38608],"realised_goal_position":[0.58691,0.18745,0.24812],"realised_object_initial_position":[0.50382,-0.01567,0.03]},"peak_contact_force":290.84259,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":897.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.03],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.30942,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3584.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_pre_grasp","tcp_end":[0.49945,-0.01498,0.11224],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.08633,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":479.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1916.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.49888,-0.01557,0.0532],"tcp_start":[0.49945,-0.01498,0.11224],"tcp_to_object_dist_end":0.02763,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":49.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50373,-0.01539,0.02587],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31218,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.12955,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12747.0,"raw_peak_contact_force":0.16011,"tcp_end":[0.49114,-0.01547,0.04477],"tcp_start":[0.49888,-0.01557,0.0532],"tcp_to_object_dist_end":0.02271,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49893,-0.01541,0.11116],"object_pos_start":[0.50373,-0.01539,0.02587],"object_to_goal_dist_end":0.2601,"object_to_goal_dist_start":0.31218,"object_z_max":0.11107,"peak_contact_force":0.06849,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":39665.0,"raw_peak_contact_force":0.41842,"subtask_id":"lift_clearance","tcp_end":[0.49407,-0.01536,0.13667],"tcp_start":[0.49114,-0.01547,0.04477],"tcp_to_object_dist_end":0.02597,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":623.0,"n_steps_budget":1000.0,"object_pos_end":[0.55823,0.10729,0.05672],"object_pos_start":[0.49893,-0.01541,0.11116],"object_to_goal_dist_end":0.20948,"object_to_goal_dist_start":0.2601,"object_z_max":0.22265,"peak_contact_force":0.0,"phase_name":"approach_2","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":14545.0,"raw_peak_contact_force":0.24207,"subtask_id":"reach_pre_place","tcp_end":[0.54078,0.0912,0.28134],"tcp_start":[0.54075,0.09106,0.28125],"tcp_to_object_dist_end":0.22588,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":8.0,"n_steps_budget":1000.0,"object_pos_end":[0.55977,0.11041,0.01878],"object_pos_start":[0.55854,0.10792,0.04945],"object_to_goal_dist_end":0.24345,"object_to_goal_dist_start":0.21587,"object_z_max":0.04945,"peak_contact_force":290.84259,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"place_goal","tcp_end":[0.54086,0.0919,0.28095],"tcp_start":[0.54078,0.0912,0.28134],"tcp_to_object_dist_end":0.2635,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.55907,0.11315,0.01602],"object_pos_start":[0.55977,0.11041,0.01878],"object_to_goal_dist_end":0.24528,"object_to_goal_dist_start":0.24345,"object_z_max":0.01878,"peak_contact_force":0.12261,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":885.0,"raw_peak_contact_force":1.73602,"tcp_end":[0.53707,0.09125,0.30374],"tcp_start":[0.54086,0.0919,0.28095],"tcp_to_object_dist_end":0.28939,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":842.0,"n_steps_budget":900.0,"object_pos_end":[0.55907,0.11315,0.01602],"object_pos_start":[0.55907,0.11315,0.01602],"object_to_goal_dist_end":0.24528,"object_to_goal_dist_start":0.24528,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3368.0,"raw_peak_contact_force":0.12264,"tcp_end":[0.58355,0.18249,0.38608],"tcp_start":[0.53707,0.09125,0.30374],"tcp_to_object_dist_end":0.3773,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```