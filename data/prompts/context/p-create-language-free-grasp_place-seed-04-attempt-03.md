## Search State

- **Seed**: 4
- **Iteration**: 4 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 3 | approach → descend → grasp → lift → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 3 | 0.2450 | 0.21 | ❌ rejected |
| 2 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 1 | 0.3623 | 0.24 | ✅ accepted |
| 1 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 0 | 0.3139 | 0.21 | ❌ rejected |
| 0 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 0 | 0.3139 | 0.21 | ✅ accepted |

**Proposal policy**: task_score is 0.21 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.245) — your mutation base

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
    - 0.0
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
    - 0.15
    tolerance: 0.005
    orientation:
      mode: keep_current
  parameters:
    lift_z:
      type: scalar
      range:
      - 0.1
      - 0.2
      default: 0.15
      binds_to:
      - path: target.offset.z
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
    - 0.08
    tolerance: 0.005
    orientation:
      mode: keep_current
  subtask_id: reach_pre_place
- id: descend_2
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
    tolerance: 0.005
    orientation:
      mode: keep_current
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
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.0], tolerance=0.005
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
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.15], tolerance=0.005
  - orientation: mode=keep_current
  - parameter_bindings:
    - lift_z: status=consumed; consumers=target.offset.z (replace)
  - guards:
    - id=lift_check, when=after_phase, predicate=object_lifted, on_failure=retry, threshold=0.05
  - retries: max_attempts=2, strategy=repeat
- **approach_2** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.08], tolerance=0.005
  - orientation: mode=keep_current
  - parameter_bindings: none
- **descend_2** (`descend`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], tolerance=0.005
  - orientation: mode=keep_current
  - parameter_bindings: none
- **release_1** (`release`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - orientation: mode=none
  - parameter_bindings: none
- **retract_1** (`retract`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.15], tolerance=0.005
  - orientation: mode=keep_current
  - parameter_bindings: none

## Design Metrics

- **Composite score**: 0.245
- **task_score** (E): 0.207
- **fitness_score**: 0.575  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.330

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1678 |
| descend_1 | 1.00 | 1.00 | 0.1005 |
| grasp_1 | 1.00 | 1.00 | 0.0123 |
| lift_1 | 1.00 | 0.67 | 0.1063 |
| lift_higher | 0.33 | 1.00 | 0.0038 |
| approach_2 | 0.67 | 1.00 | 0.0014 |
| descend_2 | 1.00 | 1.00 | 0.0899 |
| release_1 | 1.00 | 1.00 | 0.0205 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.516, 0.004, 0.135) | (0.526, 0.005, 0.030)→(0.526, 0.005, 0.026) | 0.246→0.249 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.516, 0.004, 0.135)→(0.520, 0.005, 0.035) | (0.526, 0.005, 0.026)→(0.526, 0.005, 0.026) | 0.249→0.249 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_1 | grasp | 1.00 / step_budget | (0.520, 0.005, 0.035)→(0.511, 0.005, 0.026) | (0.526, 0.005, 0.026)→(0.526, 0.005, 0.025) | 0.249→0.249 | 1.00 / 40.333 | 0.150 | 0.198 |
| lift_1 | lift | 1.00 / step_budget | (0.511, 0.005, 0.026)→(0.521, 0.005, 0.132) | (0.526, 0.005, 0.025)→(0.539, 0.006, 0.116) | 0.249→0.203 | 0.67 / 16.333 | 0.082 | 0.664 |
| lift_higher | lift | 0.33 / step_budget | (0.528, 0.015, 0.250)→(0.526, 0.016, 0.247) | (0.539, 0.006, 0.116)→(0.528, 0.019, 0.016) | 0.203→0.245 | 1.00 / 8.333 | 94250.358 | 1.542 |
| approach_2 | approach | 0.67 / step_budget | (0.609, 0.172, 0.272)→(0.609, 0.173, 0.273) | (0.528, 0.019, 0.016)→(0.528, 0.019, 0.016) | 0.245→0.245 | 1.00 / 8.667 | 185252.399 | 0.123 |
| descend_2 | descend | 1.00 / step_budget | (0.609, 0.173, 0.273)→(0.608, 0.173, 0.183) | (0.528, 0.019, 0.016)→(0.528, 0.019, 0.016) | 0.245→0.245 | 1.00 / 8.333 | 91001.405 | 0.123 |
| release_1 | release | 1.00 / step_budget | (0.608, 0.173, 0.183)→(0.603, 0.172, 0.202) | (0.528, 0.019, 0.016)→(0.528, 0.019, 0.016) | 0.245→0.245 | 1.00 / 4.000 | 0.123 | 0.123 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.296
- phase_score: 0.641
- phase_breakdown.reach_pre_grasp_score: 0.560
- phase_breakdown.lift_clearance_score: 0.134
- phase_breakdown.place_goal_score: 0.858
- phase_breakdown.reach_pre_place_score: 0.794
- grasp_place_fitness: 0.624

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.624
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.296
- **Median Q (composite search score)**: 0.235
- **K-run variance**: 0.0013
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 10.0
- **Final σ (mean)**: 0.520


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.52766,"average_solve_count":235.0,"average_success_count":235.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_2.approach_speed":0.26594,"lift_1.lift_z":0.14012,"lift_higher.lift_higher_z":0.22395},"optimized_scores":{"best_composite_score":0.2349,"best_fitness_score":0.5649,"best_task_score":0.20355},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":4645.0,"contact_point_centroid":[0.55689,0.02336,-0.00218],"force_p95":0.12381,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.30944,"mean_force":0.13216,"phase_index":4.0,"phase_name":"lift_higher","phase_type":"lift","tcp_position_centroid":[0.54277,0.00455,0.24369]},{"body_a":"world","body_b":"grasp_target","contact_count":348.0,"contact_point_centroid":[0.54262,0.00067,-0.00159],"force_p95":0.18535,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.37472,"mean_force":0.09192,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52496,0.00077,0.04287]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8369.0,"contact_point_centroid":[0.53469,-0.01784,0.08738],"force_p95":0.1342,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.34692,"mean_force":0.08598,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52977,0.00073,0.08582]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8636.0,"contact_point_centroid":[0.53493,0.01923,0.0881],"force_p95":0.12067,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33012,"mean_force":0.08419,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52991,0.00073,0.08681]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.54428,0.00104,-0.00205],"force_p95":0.1371,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.15539,"mean_force":0.12678,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52839,0.00084,0.04371]},{"body_a":"world","body_b":"grasp_target","contact_count":3996.0,"contact_point_centroid":[0.54431,0.00113,-0.00196],"force_p95":0.12459,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12275,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.5152,0.00044,0.21539]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3983.0,"contact_point_centroid":[0.5294,-0.01809,0.04542],"force_p95":0.09713,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12395,"mean_force":0.0546,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52717,0.00082,0.04227]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.54431,0.00113,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.53079,0.00086,0.09454]},{"body_a":"world","body_b":"grasp_target","contact_count":7884.0,"contact_point_centroid":[0.55692,0.02343,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"approach_2","phase_type":"approach","tcp_position_centroid":[0.61759,0.11862,0.26041]},{"body_a":"world","body_b":"grasp_target","contact_count":1172.0,"contact_point_centroid":[0.55692,0.02343,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.64376,0.15685,0.23715]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.55692,0.02343,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":7.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.63978,0.15578,0.19306]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4138.0,"contact_point_centroid":[0.52982,0.01966,0.04477],"force_p95":0.0903,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09489,"mean_force":0.05329,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52717,0.00082,0.04228]},{"body_a":"left_finger","body_b":"right_finger","contact_count":4669.0,"contact_point_centroid":[0.5434,0.00477,0.2506],"force_p95":0.01103,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01638,"mean_force":0.01053,"phase_index":4.0,"phase_name":"lift_higher","phase_type":"lift","tcp_position_centroid":[0.54311,0.00477,0.24835]},{"body_a":"left_finger","body_b":"right_finger","contact_count":8428.0,"contact_point_centroid":[0.61821,0.11874,0.26267],"force_p95":0.01099,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0128,"mean_force":0.01043,"phase_index":5.0,"phase_name":"approach_2","phase_type":"approach","tcp_position_centroid":[0.61767,0.11872,0.26043]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1278.0,"contact_point_centroid":[0.64454,0.15688,0.23908],"force_p95":0.01091,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01268,"mean_force":0.01025,"phase_index":6.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.64376,0.15685,0.23686]},{"body_a":"left_finger","body_b":"right_finger","contact_count":219.0,"contact_point_centroid":[0.6431,0.15658,0.19235],"force_p95":0.01096,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01097,"mean_force":0.01013,"phase_index":7.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.64229,0.15654,0.19011]}],"total_contact_groups":16},"final_pose_error":0.0049,"key_states":{"actual_goal_position":[0.64762,0.15808,0.1911],"final_object_position":[0.55692,0.02343,0.01602],"final_tcp_position":[0.6438,0.15696,0.19395],"realised_goal_position":[0.64762,0.15808,0.1911],"realised_object_initial_position":[0.54431,0.00113,0.03]},"peak_contact_force":273004.16078,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.03],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.24751,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3996.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_pre_grasp","tcp_end":[0.52806,0.00077,0.15679],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.13178,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.53533,0.00096,0.05194],"tcp_start":[0.52806,0.00077,0.15679],"tcp_to_object_dist_end":0.02743,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":36.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54446,0.00077,0.02572],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25048,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.13902,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":9921.0,"raw_peak_contact_force":0.15539,"tcp_end":[0.52714,0.00082,0.04224],"tcp_start":[0.53533,0.00096,0.05194],"tcp_to_object_dist_end":0.02394,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":751.0,"n_steps_budget":780.0,"object_pos_end":[0.54996,0.00508,0.11468],"object_pos_start":[0.54446,0.00077,0.02572],"object_to_goal_dist_end":0.19695,"object_to_goal_dist_start":0.25048,"object_z_max":0.12094,"peak_contact_force":0.0,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":17353.0,"raw_peak_contact_force":0.37472,"subtask_id":"lift_clearance","tcp_end":[0.53951,0.0007,0.15288],"tcp_start":[0.52714,0.00082,0.04224],"tcp_to_object_dist_end":0.03985,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1223.0,"n_steps_budget":1000.0,"object_pos_end":[0.55692,0.02343,0.01602],"object_pos_start":[0.54996,0.00508,0.11468],"object_to_goal_dist_end":0.23878,"object_to_goal_dist_start":0.19695,"object_z_max":0.11468,"peak_contact_force":0.12263,"phase_name":"lift_higher","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":9314.0,"raw_peak_contact_force":1.30944,"tcp_end":[0.55152,0.02013,0.24388],"tcp_start":[0.55195,0.0195,0.24757],"tcp_to_object_dist_end":0.22795,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":1971.0,"n_steps_budget":1000.0,"object_pos_end":[0.55692,0.02343,0.01602],"object_pos_start":[0.55692,0.02343,0.01602],"object_to_goal_dist_end":0.23878,"object_to_goal_dist_start":0.23878,"object_z_max":0.01602,"peak_contact_force":273004.16078,"phase_name":"approach_2","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":16312.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_pre_place","tcp_end":[0.64504,0.1572,0.28073],"tcp_start":[0.64473,0.15673,0.2802],"tcp_to_object_dist_end":0.30941,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":293.0,"n_steps_budget":1000.0,"object_pos_end":[0.55692,0.02343,0.01602],"object_pos_start":[0.55692,0.02343,0.01602],"object_to_goal_dist_end":0.23878,"object_to_goal_dist_start":0.23878,"object_z_max":0.01602,"peak_contact_force":273003.97042,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2450.0,"raw_peak_contact_force":0.12263,"subtask_id":"place_goal","tcp_end":[0.6438,0.15696,0.19395],"tcp_start":[0.64504,0.1572,0.28073],"tcp_to_object_dist_end":0.23883,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.55692,0.02343,0.01602],"object_pos_start":[0.55692,0.02343,0.01602],"object_to_goal_dist_end":0.23878,"object_to_goal_dist_start":0.23878,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1019.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.63836,0.15532,0.21213],"tcp_start":[0.6438,0.15696,0.19395],"tcp_to_object_dist_end":0.24998,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.43983,"average_solve_count":241.0,"average_success_count":241.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_2.approach_speed":0.22952,"lift_1.lift_z":0.11725,"lift_higher.lift_higher_z":0.24527},"optimized_scores":{"best_composite_score":0.29403,"best_fitness_score":0.62403,"best_task_score":0.29575},"replay_outcomes":[{"contacts":{"omitted_contact_groups":2,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":3075.0,"contact_point_centroid":[0.52256,0.04197,-0.00227],"force_p95":0.13046,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.64006,"mean_force":0.13916,"phase_index":4.0,"phase_name":"lift_higher","phase_type":"lift","tcp_position_centroid":[0.53187,0.02946,0.24232]},{"body_a":"world","body_b":"grasp_target","contact_count":342.0,"contact_point_centroid":[0.52731,0.02904,-0.00164],"force_p95":0.36197,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.73932,"mean_force":0.12477,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51402,0.02924,0.021]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":11860.0,"contact_point_centroid":[0.52028,0.04794,0.06494],"force_p95":0.10697,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30165,"mean_force":0.06685,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51748,0.02909,0.06346]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":11442.0,"contact_point_centroid":[0.52039,0.01023,0.0679],"force_p95":0.10982,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28746,"mean_force":0.06808,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51779,0.02909,0.06636]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53055,0.0304,-0.00212],"force_p95":0.15988,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.25215,"mean_force":0.13286,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51756,0.02952,0.02166]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2758.0,"contact_point_centroid":[0.52715,0.04692,0.14561],"force_p95":0.16573,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24398,"mean_force":0.1068,"phase_index":4.0,"phase_name":"lift_higher","phase_type":"lift","tcp_position_centroid":[0.52419,0.02885,0.14917]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2517.0,"contact_point_centroid":[0.5272,0.01065,0.14326],"force_p95":0.17232,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2356,"mean_force":0.1041,"phase_index":4.0,"phase_name":"lift_higher","phase_type":"lift","tcp_position_centroid":[0.52407,0.02886,0.14669]},{"body_a":"world","body_b":"grasp_target","contact_count":3996.0,"contact_point_centroid":[0.5305,0.03079,-0.00196],"force_p95":0.12459,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12275,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51066,0.01403,0.20762]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4041.0,"contact_point_centroid":[0.51727,0.01024,0.02303],"force_p95":0.08062,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13595,"mean_force":0.05192,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51632,0.02943,0.02028]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.5305,0.03079,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.52164,0.02792,0.07295]},{"body_a":"world","body_b":"grasp_target","contact_count":6660.0,"contact_point_centroid":[0.52238,0.04201,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"approach_2","phase_type":"approach","tcp_position_centroid":[0.57946,0.1441,0.20457]},{"body_a":"world","body_b":"grasp_target","contact_count":2104.0,"contact_point_centroid":[0.52238,0.04201,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.59609,0.17683,0.13934]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.52238,0.04201,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":7.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.59166,0.17547,0.10322]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4997.0,"contact_point_centroid":[0.51718,0.0486,0.02208],"force_p95":0.0728,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09225,"mean_force":0.04494,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51633,0.02943,0.02029]},{"body_a":"left_finger","body_b":"right_finger","contact_count":3036.0,"contact_point_centroid":[0.53275,0.02952,0.24878],"force_p95":0.01117,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01612,"mean_force":0.01055,"phase_index":4.0,"phase_name":"lift_higher","phase_type":"lift","tcp_position_centroid":[0.53223,0.02951,0.24658]},{"body_a":"left_finger","body_b":"right_finger","contact_count":7130.0,"contact_point_centroid":[0.57988,0.14389,0.20694],"force_p95":0.011,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01284,"mean_force":0.01042,"phase_index":5.0,"phase_name":"approach_2","phase_type":"approach","tcp_position_centroid":[0.57934,0.14387,0.20465]}],"total_contact_groups":18},"final_pose_error":0.00765,"key_states":{"actual_goal_position":[0.60153,0.17858,0.10809],"final_object_position":[0.52238,0.04201,0.01602],"final_tcp_position":[0.59666,0.17706,0.10238],"realised_goal_position":[0.60153,0.17858,0.10809],"realised_object_initial_position":[0.5305,0.03079,0.03]},"peak_contact_force":273004.15662,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.03],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18162,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3996.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_pre_grasp","tcp_end":[0.52109,0.02528,0.1369],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.11141,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.52468,0.02999,0.02959],"tcp_start":[0.52109,0.02528,0.1369],"tcp_to_object_dist_end":0.00688,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53034,0.02932,0.0256],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.1848,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.151,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10838.0,"raw_peak_contact_force":0.25215,"tcp_end":[0.51629,0.02943,0.02025],"tcp_start":[0.52468,0.02999,0.02959],"tcp_to_object_dist_end":0.01504,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":751.0,"n_steps_budget":780.0,"object_pos_end":[0.54601,0.02919,0.12163],"object_pos_start":[0.53034,0.02932,0.0256],"object_to_goal_dist_end":0.15995,"object_to_goal_dist_start":0.1848,"object_z_max":0.12154,"peak_contact_force":0.12427,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":23644.0,"raw_peak_contact_force":0.73932,"subtask_id":"lift_clearance","tcp_end":[0.52541,0.02906,0.13027],"tcp_start":[0.51629,0.02943,0.02025],"tcp_to_object_dist_end":0.02234,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1106.0,"n_steps_budget":1000.0,"object_pos_end":[0.52238,0.04201,0.01602],"object_pos_start":[0.54601,0.02919,0.12163],"object_to_goal_dist_end":0.18274,"object_to_goal_dist_start":0.15995,"object_z_max":0.14418,"peak_contact_force":9748.84237,"phase_name":"lift_higher","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":11386.0,"raw_peak_contact_force":1.64006,"tcp_end":[0.52465,0.03734,0.26501],"tcp_start":[0.52632,0.03645,0.2683],"tcp_to_object_dist_end":0.24905,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":1665.0,"n_steps_budget":1000.0,"object_pos_end":[0.52238,0.04201,0.01602],"object_pos_start":[0.52238,0.04201,0.01602],"object_to_goal_dist_end":0.18274,"object_to_goal_dist_start":0.18274,"object_z_max":0.01602,"peak_contact_force":273004.15662,"phase_name":"approach_2","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":13790.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_pre_place","tcp_end":[0.5977,0.1773,0.19889],"tcp_start":[0.59767,0.17713,0.19832],"tcp_to_object_dist_end":0.23962,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":526.0,"n_steps_budget":1000.0,"object_pos_end":[0.52238,0.04201,0.01602],"object_pos_start":[0.52238,0.04201,0.01602],"object_to_goal_dist_end":0.18274,"object_to_goal_dist_start":0.18274,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4357.0,"raw_peak_contact_force":0.12263,"subtask_id":"place_goal","tcp_end":[0.59666,0.17706,0.10238],"tcp_start":[0.5977,0.1773,0.19889],"tcp_to_object_dist_end":0.17667,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.52238,0.04201,0.01602],"object_pos_start":[0.52238,0.04201,0.01602],"object_to_goal_dist_end":0.18274,"object_to_goal_dist_start":0.18274,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1024.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.58968,0.17482,0.12288],"tcp_start":[0.59666,0.17706,0.10238],"tcp_to_object_dist_end":0.18326,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.524,"average_solve_count":250.0,"average_success_count":250.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_2.approach_speed":0.08465,"lift_1.lift_z":0.09887,"lift_higher.lift_higher_z":0.20892},"optimized_scores":{"best_composite_score":0.20609,"best_fitness_score":0.53609,"best_task_score":0.12264},"replay_outcomes":[{"contacts":{"omitted_contact_groups":4,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":2656.0,"contact_point_centroid":[0.50446,-0.0085,-0.00233],"force_p95":0.12785,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.67589,"mean_force":0.14013,"phase_index":4.0,"phase_name":"lift_higher","phase_type":"lift","tcp_position_centroid":[0.50764,-0.01474,0.23334]},{"body_a":"world","body_b":"grasp_target","contact_count":355.0,"contact_point_centroid":[0.50052,-0.0153,-0.00175],"force_p95":0.41295,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.87832,"mean_force":0.13905,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48844,-0.01544,0.01616]},{"body_a":"grasp_target","body_b":"hand","contact_count":538.0,"contact_point_centroid":[0.50386,-0.01114,0.08719],"force_p95":0.11561,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.37537,"mean_force":0.0646,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.4907,-0.01536,0.04864]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4669.0,"contact_point_centroid":[0.50169,0.00312,0.13934],"force_p95":0.16254,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32933,"mean_force":0.09773,"phase_index":4.0,"phase_name":"lift_higher","phase_type":"lift","tcp_position_centroid":[0.49804,-0.01519,0.14075]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":10540.0,"contact_point_centroid":[0.49332,0.00369,0.05776],"force_p95":0.10437,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27415,"mean_force":0.06413,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49149,-0.01534,0.05568]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4475.0,"contact_point_centroid":[0.50109,-0.03364,0.13727],"force_p95":0.16479,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26707,"mean_force":0.09601,"phase_index":4.0,"phase_name":"lift_higher","phase_type":"lift","tcp_position_centroid":[0.49786,-0.01519,0.13896]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":11869.0,"contact_point_centroid":[0.49295,-0.03421,0.05509],"force_p95":0.10144,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24613,"mean_force":0.05782,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49129,-0.01535,0.05363]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50364,-0.01548,-0.00228],"force_p95":0.16148,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.18723,"mean_force":0.14209,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49188,-0.0155,0.01623]},{"body_a":"world","body_b":"grasp_target","contact_count":3584.0,"contact_point_centroid":[0.50382,-0.01567,-0.00196],"force_p95":0.12593,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12276,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49856,-0.00759,0.20286]},{"body_a":"world","body_b":"grasp_target","contact_count":2656.0,"contact_point_centroid":[0.50382,-0.01567,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49767,-0.01532,0.05844]},{"body_a":"world","body_b":"grasp_target","contact_count":8048.0,"contact_point_centroid":[0.50432,-0.0085,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":5.0,"phase_name":"approach_2","phase_type":"approach","tcp_position_centroid":[0.54373,0.09215,0.27913]},{"body_a":"world","body_b":"grasp_target","contact_count":1236.0,"contact_point_centroid":[0.50432,-0.0085,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.5839,0.18589,0.29537]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.50432,-0.0085,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":7.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.58092,0.1851,0.25252]},{"body_a":"grasp_target","body_b":"hand","contact_count":377.0,"contact_point_centroid":[0.50847,-0.01746,0.05424],"force_p95":0.08627,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11867,"mean_force":0.07812,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49103,-0.01549,0.01536]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4119.0,"contact_point_centroid":[0.49101,0.00379,0.01744],"force_p95":0.07709,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09093,"mean_force":0.05179,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49068,-0.01549,0.015]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5376.0,"contact_point_centroid":[0.49036,-0.03455,0.01735],"force_p95":0.0637,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08406,"mean_force":0.04102,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49068,-0.01549,0.015]}],"total_contact_groups":20},"final_pose_error":0.00494,"key_states":{"actual_goal_position":[0.58691,0.18745,0.24812],"final_object_position":[0.50432,-0.0085,0.01602],"final_tcp_position":[0.58402,0.18628,0.25195],"realised_goal_position":[0.58691,0.18745,0.24812],"realised_object_initial_position":[0.50382,-0.01567,0.03]},"peak_contact_force":273002.10996,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":897.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.03],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.30942,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3584.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_pre_grasp","tcp_end":[0.49945,-0.01498,0.11224],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.08633,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":664.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2656.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.49872,-0.01559,0.02332],"tcp_start":[0.49945,-0.01498,0.11224],"tcp_to_object_dist_end":0.00577,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50294,-0.01529,0.02514],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31285,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.15944,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11672.0,"raw_peak_contact_force":0.18723,"tcp_end":[0.49065,-0.01548,0.01496],"tcp_start":[0.49872,-0.01559,0.02332],"tcp_to_object_dist_end":0.01595,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":26.0,"n_steps":661.0,"n_steps_budget":690.0,"object_pos_end":[0.51997,-0.01532,0.11229],"object_pos_start":[0.50294,-0.01529,0.02514],"object_to_goal_dist_end":0.25307,"object_to_goal_dist_start":0.31285,"object_z_max":0.1122,"peak_contact_force":0.12136,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":23302.0,"raw_peak_contact_force":0.87832,"subtask_id":"lift_clearance","tcp_end":[0.49799,-0.01524,0.11198],"tcp_start":[0.49065,-0.01548,0.01496],"tcp_to_object_dist_end":0.02198,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":1140.0,"n_steps_budget":1000.0,"object_pos_end":[0.50432,-0.0085,0.01602],"object_pos_start":[0.51997,-0.01532,0.11229],"object_to_goal_dist_end":0.31478,"object_to_goal_dist_start":0.25307,"object_z_max":0.14906,"peak_contact_force":273002.10996,"phase_name":"lift_higher","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":14391.0,"raw_peak_contact_force":1.67589,"tcp_end":[0.50328,-0.01031,0.23112],"tcp_start":[0.50441,-0.01069,0.23466],"tcp_to_object_dist_end":0.21511,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":2012.0,"n_steps_budget":1000.0,"object_pos_end":[0.50432,-0.0085,0.01602],"object_pos_start":[0.50432,-0.0085,0.01602],"object_to_goal_dist_end":0.31478,"object_to_goal_dist_start":0.31478,"object_z_max":0.01602,"peak_contact_force":9748.87913,"phase_name":"approach_2","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":16642.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_pre_place","tcp_end":[0.58471,0.18597,0.3385],"tcp_start":[0.58367,0.18336,0.33757],"tcp_to_object_dist_end":0.38506,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":309.0,"n_steps_budget":1000.0,"object_pos_end":[0.50432,-0.0085,0.01602],"object_pos_start":[0.50432,-0.0085,0.01602],"object_to_goal_dist_end":0.31478,"object_to_goal_dist_start":0.31478,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2570.0,"raw_peak_contact_force":0.12263,"subtask_id":"place_goal","tcp_end":[0.58402,0.18628,0.25195],"tcp_start":[0.58471,0.18597,0.3385],"tcp_to_object_dist_end":0.31615,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50432,-0.0085,0.01602],"object_pos_start":[0.50432,-0.0085,0.01602],"object_to_goal_dist_end":0.31478,"object_to_goal_dist_start":0.31478,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1027.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.5799,0.18465,0.27225],"tcp_start":[0.58402,0.18628,0.25195],"tcp_to_object_dist_end":0.32965,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```