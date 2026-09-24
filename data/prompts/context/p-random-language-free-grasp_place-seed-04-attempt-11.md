## Search State

- **Seed**: 4
- **Iteration**: 12 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 11 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 8 | 0.0573 | 0.33 | ✅ accepted |
| 10 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | impedance_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 6 | -0.1808 | 0.21 | ❌ rejected |
| 9 | approach → contact → grasp → lift → approach → descend → release → retract | arc_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | force_threshold_switch | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 8 | -0.2250 | 0.20 | ❌ rejected |
| 8 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 6 | -0.2972 | 0.19 | ❌ rejected |
| 7 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 6 | -0.0742 | 0.21 | ✅ accepted |

**Proposal policy**: task_score is 0.33 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.057) — your mutation base

```yaml
skill: grasp_place
dsl_version: 2
skill_type: arm_gripper
subtasks:
- id: approach_object
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.12
  weight: 0.3
- id: place_at_goal
  target_entity: object
  weight: 0.7
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
    - 0.12
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    approach_height:
      type: scalar
      range:
      - 0.08
      - 0.18
      default: 0.12
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: approach_object
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
    - 0.01
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    grasp_z_offset:
      type: scalar
      range:
      - 0.0
      - 0.04
      default: 0.01
      binds_to:
      - path: target.offset.z
        mode: replace
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
  parameters:
    grasp_retry_x:
      type: scalar
      range:
      - -0.02
      - 0.02
      default: 0.0
      binds_to:
      - path: retry.offset.x
        mode: replace
    grasp_retry_y:
      type: scalar
      range:
      - -0.02
      - 0.02
      default: 0.0
      binds_to:
      - path: retry.offset.y
        mode: replace
  guards:
  - id: grasp_contact
    when: during_phase
    predicate: bilateral_grasp
    threshold: 0.1
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.0
    - 0.0
    - 0.0
- id: lift_object
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
      distance: 0.15
      axis: world_z
      mode: replace_offset_projection
      sign: positive
    tolerance: 0.02
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
    - 0.15
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    transport_height:
      type: scalar
      range:
      - 0.1
      - 0.25
      default: 0.15
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: place_at_goal
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
    tolerance: 0.015
    orientation:
      mode: keep_current
  parameters:
    place_height:
      type: scalar
      range:
      - 0.005
      - 0.05
      default: 0.02
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: place_at_goal
- id: release_object
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
- id: retract_after_place
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
      distance: 0.1
      axis: world_z
      mode: replace_offset_projection
      sign: positive
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    retract_height:
      type: scalar
      range:
      - 0.05
      - 0.15
      default: 0.1
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_object** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.12], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_height: status=consumed; consumers=target.offset.z (replace)
- **descend_to_grasp** (`descend`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.01], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - grasp_z_offset: status=consumed; consumers=target.offset.z (replace)
- **grasp_object** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings:
    - grasp_retry_x: status=consumed; consumers=retry.offset.x (replace)
    - grasp_retry_y: status=consumed; consumers=retry.offset.y (replace)
  - guards:
    - id=grasp_contact, when=during_phase, predicate=bilateral_grasp, on_failure=retry, threshold=0.1
  - retries: max_attempts=2, strategy=offset_target, offset=[0.0, 0.0, 0.0]
- **lift_object** (`lift`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=world_z, distance=0.15, mode=replace_offset_projection, sign=positive}, tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset_along_axis.distance (replace)
- **transport_to_goal** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.15], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - transport_height: status=consumed; consumers=target.offset.z (replace)
- **descend_to_place** (`descend`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.02], tolerance=0.015
  - orientation: mode=keep_current
  - parameter_bindings:
    - place_height: status=consumed; consumers=target.offset.z (replace)
- **release_object** (`release`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings: none
- **retract_after_place** (`retract`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=world_z, distance=0.1, mode=replace_offset_projection, sign=positive}, tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - retract_height: status=consumed; consumers=target.offset_along_axis.distance (replace)

## Design Metrics

- **Composite score**: 0.057
- **task_score** (E): 0.331
- **fitness_score**: 0.637  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.580

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_object | 1.00 | 1.00 | 0.1136 |
| descend_to_grasp | 1.00 | 1.00 | 0.1439 |
| grasp_object | 0.00 | 1.00 | 0.0000 |
| lift_object | 1.00 | 1.00 | 0.1538 |
| transport_to_goal | 1.00 | 1.00 | 0.2268 |
| descend_to_place | 1.00 | 1.00 | 0.0877 |
| release_object | 1.00 | 1.00 | 0.0200 |
| retract_after_place | 1.00 | 1.00 | 0.0984 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.519, 0.005, 0.191) | (0.526, 0.005, 0.030)→(0.526, 0.005, 0.026) | 0.246→0.249 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_to_grasp | descend | 1.00 / step_budget | (0.519, 0.005, 0.191)→(0.521, 0.005, 0.047) | (0.526, 0.005, 0.026)→(0.526, 0.005, 0.026) | 0.249→0.249 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_object | grasp | 0.00 / guard_failure | (0.516, 0.005, 0.041)→(0.516, 0.005, 0.041) | (0.526, 0.005, 0.026)→(0.526, 0.005, 0.026) | 0.249→0.249 | 1.00 / 44.667 | 0.137 | 0.180 |
| lift_object | lift | 1.00 / step_budget | (0.516, 0.005, 0.041)→(0.513, 0.005, 0.194) | (0.526, 0.005, 0.026)→(0.528, 0.005, 0.175) | 0.249→0.202 | 1.00 / 24.667 | 0.102 | 0.504 |
| transport_to_goal | approach | 1.00 / step_budget | (0.513, 0.005, 0.194)→(0.604, 0.164, 0.308) | (0.528, 0.005, 0.175)→(0.571, 0.108, 0.071) | 0.202→0.180 | 1.00 / 14.000 | 6499.228 | 1.403 |
| descend_to_place | descend | 1.00 / step_budget | (0.604, 0.164, 0.308)→(0.608, 0.171, 0.221) | (0.571, 0.108, 0.071)→(0.571, 0.111, 0.049) | 0.180→0.158 | 1.00 / 14.000 | 91001.991 | 0.169 |
| release_object | release | 1.00 / step_budget | (0.608, 0.171, 0.221)→(0.603, 0.170, 0.240) | (0.571, 0.111, 0.049)→(0.565, 0.110, 0.020) | 0.158→0.183 | 1.00 / 3.667 | 0.138 | 0.515 |
| retract_after_place | retract | 1.00 / step_budget | (0.603, 0.170, 0.240)→(0.601, 0.169, 0.339) | (0.565, 0.110, 0.020)→(0.564, 0.111, 0.019) | 0.183→0.184 | 1.00 / 4.000 | 0.123 | 0.146 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.564
- phase_score: 0.541
- phase_breakdown.place_at_goal_score: 0.491
- phase_breakdown.approach_object_score: 0.660
- grasp_place_fitness: 0.749

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.749
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.564
- **Median Q (composite search score)**: 0.019
- **K-run variance**: 0.0065
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.329


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.90909,"average_solve_count":198.0,"average_success_count":198.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_height":0.13921,"descend_to_grasp.grasp_z_offset":0.00014,"descend_to_place.place_height":0.02065,"grasp_object.grasp_retry_x":0.00772,"grasp_object.grasp_retry_y":-0.00812,"lift_object.lift_height":0.17642,"retract_after_place.retract_height":0.08269,"transport_to_goal.transport_height":0.16475},"optimized_scores":{"best_composite_score":0.01906,"best_fitness_score":0.59906,"best_task_score":0.25111},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":2148.0,"contact_point_centroid":[0.5778,0.07192,-0.00254],"force_p95":0.17464,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.21419,"mean_force":0.14616,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.6031,0.10127,0.29056]},{"body_a":"world","body_b":"grasp_target","contact_count":77.0,"contact_point_centroid":[0.54134,0.0009,-0.00134],"force_p95":0.50151,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.53344,"mean_force":0.11786,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.53197,0.00089,0.03989]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1676.0,"contact_point_centroid":[0.54567,0.03532,0.20769],"force_p95":0.17532,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32589,"mean_force":0.09738,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.53965,0.01681,0.20779]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8043.0,"contact_point_centroid":[0.53129,0.0199,0.11144],"force_p95":0.10592,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32109,"mean_force":0.06793,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.52934,0.00086,0.10918]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":9033.0,"contact_point_centroid":[0.53122,-0.01801,0.10829],"force_p95":0.10145,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27765,"mean_force":0.06167,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.52934,0.00085,0.10665]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1631.0,"contact_point_centroid":[0.54521,-0.00238,0.20748],"force_p95":0.18545,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27498,"mean_force":0.09917,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.53916,0.01608,0.20718]},{"body_a":"world","body_b":"grasp_target","contact_count":1804.0,"contact_point_centroid":[0.5443,0.00116,-0.00202],"force_p95":0.12795,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.14444,"mean_force":0.12458,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.53359,0.00093,0.03903]},{"body_a":"world","body_b":"grasp_target","contact_count":940.0,"contact_point_centroid":[0.54431,0.00113,-0.00186],"force_p95":0.13709,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12315,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.51578,0.00043,0.24391]},{"body_a":"world","body_b":"grasp_target","contact_count":1048.0,"contact_point_centroid":[0.54431,0.00113,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.53517,0.00094,0.11584]},{"body_a":"world","body_b":"grasp_target","contact_count":916.0,"contact_point_centroid":[0.57771,0.07194,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.64182,0.15248,0.28411]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.57771,0.07194,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.64001,0.15467,0.22436]},{"body_a":"world","body_b":"grasp_target","contact_count":1060.0,"contact_point_centroid":[0.57771,0.07194,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":7.0,"phase_name":"retract_after_place","phase_type":"retract","tcp_position_centroid":[0.63683,0.15363,0.2744]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5292.0,"contact_point_centroid":[0.53305,0.02021,0.0403],"force_p95":0.07422,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09496,"mean_force":0.0497,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.53323,0.00092,0.03863]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6432.0,"contact_point_centroid":[0.53259,-0.01815,0.03991],"force_p95":0.063,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08832,"mean_force":0.04102,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.53323,0.00092,0.03863]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2106.0,"contact_point_centroid":[0.60678,0.10549,0.29704],"force_p95":0.01171,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0141,"mean_force":0.0105,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.60634,0.10548,0.2948]},{"body_a":"left_finger","body_b":"right_finger","contact_count":988.0,"contact_point_centroid":[0.64232,0.1525,0.28639],"force_p95":0.01098,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01275,"mean_force":0.01034,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.64182,0.15248,0.2841]}],"total_contact_groups":17},"final_pose_error":0.01984,"key_states":{"actual_goal_position":[0.64762,0.15808,0.1911],"final_object_position":[0.57771,0.07194,0.01602],"final_tcp_position":[0.6368,0.15356,0.3065],"realised_goal_position":[0.64762,0.15808,0.1911],"realised_object_initial_position":[0.54431,0.00113,0.03]},"peak_contact_force":9748.95898,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":236.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.03],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.24751,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":940.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_object","tcp_end":[0.53379,0.00089,0.18579],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.16011,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":262.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.12262,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1048.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.5384,0.00102,0.04509],"tcp_start":[0.53379,0.00089,0.18579],"tcp_to_object_dist_end":0.01996,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54423,0.00114,0.02592],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25021,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.12787,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":13528.0,"raw_peak_contact_force":0.14444,"tcp_end":[0.53321,0.00092,0.03861],"tcp_start":[0.53321,0.00092,0.03861],"tcp_to_object_dist_end":0.01681,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":25.0,"n_steps":524.0,"n_steps_budget":1000.0,"object_pos_end":[0.54567,0.0009,0.17704],"object_pos_start":[0.54423,0.00114,0.02593],"object_to_goal_dist_end":0.18788,"object_to_goal_dist_start":0.25021,"object_z_max":0.17679,"peak_contact_force":0.10104,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":17153.0,"raw_peak_contact_force":0.53344,"tcp_end":[0.52973,0.00086,0.19558],"tcp_start":[0.53321,0.00092,0.03861],"tcp_to_object_dist_end":0.02444,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":800.0,"n_steps_budget":1000.0,"object_pos_end":[0.57771,0.07194,0.01602],"object_pos_start":[0.54567,0.0009,0.17704],"object_to_goal_dist_end":0.20728,"object_to_goal_dist_start":0.18788,"object_z_max":0.19926,"peak_contact_force":9748.95898,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":7561.0,"raw_peak_contact_force":2.21419,"subtask_id":"place_at_goal","tcp_end":[0.6405,0.14964,0.33933],"tcp_start":[0.52973,0.00086,0.19558],"tcp_to_object_dist_end":0.3384,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":229.0,"n_steps_budget":1000.0,"object_pos_end":[0.57771,0.07194,0.01602],"object_pos_start":[0.57771,0.07194,0.01602],"object_to_goal_dist_end":0.20728,"object_to_goal_dist_start":0.20728,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1904.0,"raw_peak_contact_force":0.12263,"subtask_id":"place_at_goal","tcp_end":[0.64376,0.15574,0.22569],"tcp_start":[0.6405,0.14964,0.33933],"tcp_to_object_dist_end":0.23526,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.57771,0.07194,0.01602],"object_pos_start":[0.57771,0.07194,0.01602],"object_to_goal_dist_end":0.20728,"object_to_goal_dist_start":0.20728,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1030.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.63879,0.15426,0.24353],"tcp_start":[0.64376,0.15574,0.22569],"tcp_to_object_dist_end":0.24954,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":265.0,"n_steps_budget":600.0,"object_pos_end":[0.57771,0.07194,0.01602],"object_pos_start":[0.57771,0.07194,0.01602],"object_to_goal_dist_end":0.20728,"object_to_goal_dist_start":0.20728,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_after_place","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1060.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.6368,0.15356,0.3065],"tcp_start":[0.63879,0.15426,0.24353],"tcp_to_object_dist_end":0.30746,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.90164,"average_solve_count":183.0,"average_success_count":183.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_height":0.12088,"descend_to_grasp.grasp_z_offset":0.00489,"descend_to_place.place_height":0.02206,"grasp_object.grasp_retry_x":0.00019,"grasp_object.grasp_retry_y":0.01952,"lift_object.lift_height":0.18614,"retract_after_place.retract_height":0.12232,"transport_to_goal.transport_height":0.11039},"optimized_scores":{"best_composite_score":0.16921,"best_fitness_score":0.74921,"best_task_score":0.5638},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":225.0,"contact_point_centroid":[0.58328,0.17034,-0.00551],"force_p95":1.01335,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.29889,"mean_force":0.3082,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.58857,0.17175,0.15151]},{"body_a":"world","body_b":"grasp_target","contact_count":81.0,"contact_point_centroid":[0.52789,0.02894,-0.00143],"force_p95":0.44263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.47263,"mean_force":0.09888,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.5187,0.0292,0.04527]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":770.0,"contact_point_centroid":[0.5982,0.15444,0.13801],"force_p95":0.09719,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.39319,"mean_force":0.06827,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.59271,0.17316,0.13814]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":826.0,"contact_point_centroid":[0.59762,0.192,0.13718],"force_p95":0.10052,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.38913,"mean_force":0.06482,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.5927,0.17316,0.13812]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8437.0,"contact_point_centroid":[0.5182,0.04815,0.12017],"force_p95":0.10618,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30973,"mean_force":0.06852,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.51628,0.02904,0.11793]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":9899.0,"contact_point_centroid":[0.51797,0.0102,0.11756],"force_p95":0.09873,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27677,"mean_force":0.05954,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.51627,0.02904,0.11533]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1893.0,"contact_point_centroid":[0.59827,0.18718,0.17792],"force_p95":0.14145,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26256,"mean_force":0.08684,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.5922,0.16859,0.17797]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1780.0,"contact_point_centroid":[0.59831,0.15002,0.17733],"force_p95":0.1438,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25261,"mean_force":0.08952,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.59227,0.16875,0.17674]},{"body_a":"world","body_b":"grasp_target","contact_count":1804.0,"contact_point_centroid":[0.53055,0.03058,-0.00214],"force_p95":0.15606,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.2163,"mean_force":0.13283,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.52038,0.02932,0.04421]},{"body_a":"world","body_b":"grasp_target","contact_count":1549.0,"contact_point_centroid":[0.57669,0.17277,-0.00198],"force_p95":0.15694,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.19176,"mean_force":0.12313,"phase_index":7.0,"phase_name":"retract_after_place","phase_type":"retract","tcp_position_centroid":[0.58568,0.17079,0.21363]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5895.0,"contact_point_centroid":[0.55894,0.07772,0.20971],"force_p95":0.09622,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16244,"mean_force":0.07196,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.55265,0.09644,0.20809]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5720.0,"contact_point_centroid":[0.51926,0.01011,0.0464],"force_p95":0.07541,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14619,"mean_force":0.04558,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.52003,0.02929,0.04382]},{"body_a":"world","body_b":"grasp_target","contact_count":1056.0,"contact_point_centroid":[0.5305,0.03079,-0.00188],"force_p95":0.1365,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12309,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.51037,0.01235,0.23549]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5724.0,"contact_point_centroid":[0.55927,0.11586,0.20956],"force_p95":0.09652,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13183,"mean_force":0.07345,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.553,0.09709,0.20808]},{"body_a":"world","body_b":"grasp_target","contact_count":892.0,"contact_point_centroid":[0.5305,0.03079,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.52298,0.0276,0.10971]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5994.0,"contact_point_centroid":[0.5202,0.04851,0.04568],"force_p95":0.07325,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07488,"mean_force":0.04496,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.52003,0.02929,0.04383]}],"total_contact_groups":16},"final_pose_error":0.01977,"key_states":{"actual_goal_position":[0.60153,0.17858,0.10809],"final_object_position":[0.57663,0.17281,0.02602],"final_tcp_position":[0.58588,0.1708,0.26539],"realised_goal_position":[0.60153,0.17858,0.10809],"realised_object_initial_position":[0.5305,0.03079,0.03]},"peak_contact_force":1.29889,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":265.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.03],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18162,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1056.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_object","tcp_end":[0.52269,0.02574,0.16858],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.14286,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":223.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.12262,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":892.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.52506,0.0296,0.05001],"tcp_start":[0.52269,0.02574,0.16858],"tcp_to_object_dist_end":0.02463,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":46.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53048,0.02976,0.02559],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.1844,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.14839,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":13518.0,"raw_peak_contact_force":0.2163,"tcp_end":[0.52001,0.02929,0.04381],"tcp_start":[0.52001,0.02929,0.04381],"tcp_to_object_dist_end":0.02102,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":26.0,"n_steps":549.0,"n_steps_budget":1000.0,"object_pos_end":[0.53182,0.02928,0.18675],"object_pos_start":[0.53049,0.02973,0.02561],"object_to_goal_dist_end":0.18258,"object_to_goal_dist_start":0.18441,"object_z_max":0.18649,"peak_contact_force":0.09992,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":18417.0,"raw_peak_contact_force":0.47263,"tcp_end":[0.51672,0.02907,0.21036],"tcp_start":[0.52001,0.02929,0.04381],"tcp_to_object_dist_end":0.02803,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":26.0,"n_steps":436.0,"n_steps_budget":1000.0,"object_pos_end":[0.59993,0.16398,0.1821],"object_pos_start":[0.53182,0.02928,0.18675],"object_to_goal_dist_end":0.07545,"object_to_goal_dist_start":0.18258,"object_z_max":0.18698,"peak_contact_force":0.09074,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":11619.0,"raw_peak_contact_force":0.16244,"subtask_id":"place_at_goal","tcp_end":[0.59082,0.16417,0.20987],"tcp_start":[0.51672,0.02907,0.21036],"tcp_to_object_dist_end":0.02923,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":24.0,"n_steps":151.0,"n_steps_budget":1000.0,"object_pos_end":[0.59957,0.17313,0.11354],"object_pos_start":[0.59993,0.16398,0.1821],"object_to_goal_dist_end":0.00796,"object_to_goal_dist_start":0.07545,"object_z_max":0.1821,"peak_contact_force":0.10074,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3673.0,"raw_peak_contact_force":0.26256,"subtask_id":"place_at_goal","tcp_end":[0.59513,0.17374,0.14279],"tcp_start":[0.59082,0.16417,0.20987],"tcp_to_object_dist_end":0.02959,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.58063,0.17127,0.02668],"object_pos_start":[0.59957,0.17313,0.11354],"object_to_goal_dist_end":0.08437,"object_to_goal_dist_start":0.00796,"object_z_max":0.11354,"peak_contact_force":0.1674,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1821.0,"raw_peak_contact_force":1.29889,"tcp_end":[0.58848,0.17172,0.16265],"tcp_start":[0.59513,0.17374,0.14279],"tcp_to_object_dist_end":0.1362,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":388.0,"n_steps_budget":780.0,"object_pos_end":[0.57663,0.17281,0.02602],"object_pos_start":[0.58063,0.17127,0.02668],"object_to_goal_dist_end":0.08596,"object_to_goal_dist_start":0.08437,"object_z_max":0.02668,"peak_contact_force":0.12263,"phase_name":"retract_after_place","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1549.0,"raw_peak_contact_force":0.19176,"tcp_end":[0.58588,0.1708,0.26539],"tcp_start":[0.58848,0.17172,0.16265],"tcp_to_object_dist_end":0.23956,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.91469,"average_solve_count":211.0,"average_success_count":211.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_height":0.1686,"descend_to_grasp.grasp_z_offset":1e-05,"descend_to_place.place_height":0.0327,"grasp_object.grasp_retry_x":0.01954,"grasp_object.grasp_retry_y":-0.00829,"lift_object.lift_height":0.15733,"retract_after_place.retract_height":0.1494,"transport_to_goal.transport_height":0.1449},"optimized_scores":{"best_composite_score":-0.01631,"best_fitness_score":0.56369,"best_task_score":0.17941},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":2307.0,"contact_point_centroid":[0.53672,0.08738,-0.00249],"force_p95":0.15129,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.83249,"mean_force":0.14587,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.55403,0.12192,0.31671]},{"body_a":"world","body_b":"grasp_target","contact_count":74.0,"contact_point_centroid":[0.50113,-0.01492,-0.00139],"force_p95":0.4822,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.50664,"mean_force":0.11159,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.4934,-0.01507,0.04086]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8292.0,"contact_point_centroid":[0.4919,-0.03409,0.10523],"force_p95":0.09289,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.3048,"mean_force":0.05652,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.49095,-0.01502,0.10345]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":7942.0,"contact_point_centroid":[0.49183,0.00407,0.10577],"force_p95":0.09401,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30365,"mean_force":0.05828,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.49097,-0.01503,0.10361]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2981.0,"contact_point_centroid":[0.50805,0.03247,0.20462],"force_p95":0.13947,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28662,"mean_force":0.0911,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.50222,0.01394,0.20383]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2865.0,"contact_point_centroid":[0.50739,-0.00588,0.20361],"force_p95":0.15449,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25881,"mean_force":0.0936,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.50166,0.01266,0.20257]},{"body_a":"world","body_b":"grasp_target","contact_count":1804.0,"contact_point_centroid":[0.50382,-0.01559,-0.00205],"force_p95":0.13689,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.17853,"mean_force":0.12697,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.49498,-0.01509,0.03991]},{"body_a":"world","body_b":"grasp_target","contact_count":636.0,"contact_point_centroid":[0.50382,-0.01567,-0.0018],"force_p95":0.13769,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.1234,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.49991,-0.00558,0.26034]},{"body_a":"world","body_b":"grasp_target","contact_count":1300.0,"contact_point_centroid":[0.50382,-0.01567,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12264,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.4991,-0.01348,0.13153]},{"body_a":"world","body_b":"grasp_target","contact_count":692.0,"contact_point_centroid":[0.53661,0.08736,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.58277,0.1814,0.33713]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.53661,0.08736,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.58154,0.1837,0.29531]},{"body_a":"world","body_b":"grasp_target","contact_count":1904.0,"contact_point_centroid":[0.53661,0.08736,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":7.0,"phase_name":"retract_after_place","phase_type":"retract","tcp_position_centroid":[0.57988,0.18283,0.37899]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5831.0,"contact_point_centroid":[0.4948,0.0041,0.04146],"force_p95":0.06938,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11291,"mean_force":0.04499,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.49463,-0.01508,0.03956]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5904.0,"contact_point_centroid":[0.49482,-0.03428,0.04144],"force_p95":0.06967,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0894,"mean_force":0.04502,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.49463,-0.01508,0.03956]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2274.0,"contact_point_centroid":[0.55648,0.12623,0.32353],"force_p95":0.01126,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01632,"mean_force":0.01059,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.55613,0.12622,0.32124]},{"body_a":"left_finger","body_b":"right_finger","contact_count":738.0,"contact_point_centroid":[0.58314,0.18141,0.33954],"force_p95":0.01098,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01276,"mean_force":0.01045,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.58276,0.1814,0.33722]}],"total_contact_groups":17},"final_pose_error":0.01994,"key_states":{"actual_goal_position":[0.58691,0.18745,0.24812],"final_object_position":[0.53661,0.08736,0.01602],"final_tcp_position":[0.58068,0.183,0.44456],"realised_goal_position":[0.58691,0.18745,0.24812],"realised_object_initial_position":[0.50382,-0.01567,0.03]},"peak_contact_force":273005.74912,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":160.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.03],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.30942,"object_z_max":0.03,"peak_contact_force":0.12264,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":636.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_object","tcp_end":[0.50047,-0.01189,0.21743],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.19148,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":325.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.12262,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1300.0,"raw_peak_contact_force":0.12264,"tcp_end":[0.49953,-0.01514,0.04518],"tcp_start":[0.50047,-0.01189,0.21743],"tcp_to_object_dist_end":0.01964,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50375,-0.01523,0.02583],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.3121,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.13463,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":13539.0,"raw_peak_contact_force":0.17853,"tcp_end":[0.49461,-0.01508,0.03954],"tcp_start":[0.49461,-0.01508,0.03954],"tcp_to_object_dist_end":0.01648,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":437.0,"n_steps_budget":990.0,"object_pos_end":[0.50667,-0.01507,0.16016],"object_pos_start":[0.50376,-0.01522,0.02584],"object_to_goal_dist_end":0.23492,"object_to_goal_dist_start":0.31209,"object_z_max":0.15989,"peak_contact_force":0.10497,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":16308.0,"raw_peak_contact_force":0.50664,"tcp_end":[0.49114,-0.01502,0.17742],"tcp_start":[0.49461,-0.01508,0.03954],"tcp_to_object_dist_end":0.02322,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":951.0,"n_steps_budget":1000.0,"object_pos_end":[0.53661,0.08736,0.01602],"object_pos_start":[0.50667,-0.01507,0.16016],"object_to_goal_dist_end":0.25772,"object_to_goal_dist_start":0.23492,"object_z_max":0.20927,"peak_contact_force":9748.63577,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":10427.0,"raw_peak_contact_force":1.83249,"subtask_id":"place_at_goal","tcp_end":[0.58173,0.17848,0.37614],"tcp_start":[0.49114,-0.01502,0.17742],"tcp_to_object_dist_end":0.37419,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":173.0,"n_steps_budget":1000.0,"object_pos_end":[0.53661,0.08736,0.01602],"object_pos_start":[0.53661,0.08736,0.01602],"object_to_goal_dist_end":0.25772,"object_to_goal_dist_start":0.25772,"object_z_max":0.01602,"peak_contact_force":273005.74912,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1430.0,"raw_peak_contact_force":0.12263,"subtask_id":"place_at_goal","tcp_end":[0.58413,0.18469,0.29506],"tcp_start":[0.58173,0.17848,0.37614],"tcp_to_object_dist_end":0.29932,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53661,0.08736,0.01602],"object_pos_start":[0.53661,0.08736,0.01602],"object_to_goal_dist_end":0.25772,"object_to_goal_dist_start":0.25772,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1025.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.58078,0.18332,0.31509],"tcp_start":[0.58413,0.18469,0.29506],"tcp_to_object_dist_end":0.31718,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":476.0,"n_steps_budget":930.0,"object_pos_end":[0.53661,0.08736,0.01602],"object_pos_start":[0.53661,0.08736,0.01602],"object_to_goal_dist_end":0.25772,"object_to_goal_dist_start":0.25772,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_after_place","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1904.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.58068,0.183,0.44456],"tcp_start":[0.58078,0.18332,0.31509],"tcp_to_object_dist_end":0.44129,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```