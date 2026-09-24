## Search State

- **Seed**: 0
- **Iteration**: 6 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 5 | approach → descend → grasp → lift → approach → descend → release | arc_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 6 | 0.1766 | 0.31 | ❌ rejected |
| 4 | approach → descend → grasp → lift → approach → descend → release | arc_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 6 | 0.2352 | 0.43 | ✅ accepted |
| 3 | approach → descend → grasp → lift → approach → descend → release | arc_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 5 | 0.1902 | 0.23 | ✅ accepted |
| 2 | approach → descend → grasp → lift → release | arc_cartesian | linear_cartesian | — | linear_cartesian | — | force_threshold_switch | admittance_control | position_control | position_control | admittance_control | pose_tolerance | contact_detected | grasp_success | pose_tolerance | pose_tolerance | 4 | 0.2706 | 0.17 | ✅ accepted |
| 1 | approach → descend → grasp → lift → release | arc_cartesian | linear_cartesian | — | linear_cartesian | — | force_threshold_switch | admittance_control | position_control | position_control | admittance_control | pose_tolerance | contact_detected | grasp_success | pose_tolerance | pose_tolerance | 4 | 0.2702 | 0.17 | ✅ accepted |

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
- Frozen realised-scene SHA-256: `f07a678caf5b8ea43212ad5a337315ad102b1ae725b01cf669f7af9bd0eea2ea`
- Frozen object start: [0.5136961687321454, -0.02302132862361297, 0.03]
- Frozen task target: [0.5540973523936195, 0.15165276355285293, 0.22199053588004086]
- Goal object position: (0.5540973523936195, 0.15165276355285293, 0.22199053588004086)
- place_goal_position (task success criterion — final object 3D position must be close to the realised airborne target here): (0.5540973523936195, 0.15165276355285293, 0.22199053588004086)
- Grasp/lift components are optimiser fitness diagnostics only; canonical task_score is final object-to-realised-target proximity.
- Object initial pose: (0.5136961687321454, -0.02302132862361297, 0.03)
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
  frozen_object_start: [0.5137, -0.023, 0.03]
  frozen_task_target: [0.5541, 0.1517, 0.222]
  frozen_object_starts: {'grasp_target': [0.5136961687321454, -0.02302132862361297, 0.03]}
  frozen_targets: {'place_target': [0.5540973523936195, 0.15165276355285293, 0.22199053588004086]}
  goal_tolerance_m: 0.02
  force_limit_n: 20
  force_scale_n: 5
  realized_scene_sha256: f07a678caf5b8ea43212ad5a337315ad102b1ae725b01cf669f7af9bd0eea2ea

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
| `object` | offset from object initial position (0.5136961687321454, -0.02302132862361297, 0.03) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.5540973523936195, 0.15165276355285293, 0.22199053588004086) | final destination targets |
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

## Current Skill (Q=0.177) — your mutation base

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
  - 0.05
  weight: 0.2
- id: reach_goal
  weight: 0.8
phases:
- id: approach_1
  type: approach
  generator: arc_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.0
    - 0.1
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    approach_height:
      type: scalar
      range:
      - 0.05
      - 0.3
      default: 0.1
      binds_to:
      - path: target.offset.z
        mode: replace
  guards:
  - id: contact_guard
    when: during_phase
    predicate: force_below
    threshold: 20.0
    on_failure: abort
  subtask_id: reach_object
- id: descend_1
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
    - 0.02
    tolerance: 0.015
    orientation:
      mode: keep_current
  parameters:
    grasp_offset:
      type: scalar
      range:
      - 0.0
      - 0.05
      default: 0.02
      binds_to:
      - path: target.offset.z
        mode: replace
  guards:
  - id: contact_guard
    when: during_phase
    predicate: force_below
    threshold: 20.0
    on_failure: abort
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
  retries:
    max_attempts: 1
    strategy: offset_target
    offset:
    - 0.005
    - 0.005
    - 0.0
- id: lift_1
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
      - 0.3
      default: 0.15
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
  subtask_id: reach_object
- id: transport_1
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
      - 0.3
      default: 0.15
      binds_to:
      - path: target.offset.z
        mode: replace
    transport_speed:
      type: scalar
      range:
      - 0.1
      - 0.5
      default: 0.3
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: grasp_hold_guard
    when: during_phase
    predicate: bilateral_grasp
    threshold: 2.0
    on_failure: abort
  subtask_id: reach_goal
- id: place_descend_1
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
      mode: keep_current
  subtask_id: reach_goal
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
    release_duration:
      type: scalar
      range:
      - 0.1
      - 1.0
      default: 0.5
      binds_to:
      - path: duration.max_time
        mode: replace

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.1], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_height: status=consumed; consumers=target.offset.z (replace)
  - guards:
    - id=contact_guard, when=during_phase, predicate=force_below, on_failure=abort, threshold=20.0
- **descend_1** (`descend`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.02], tolerance=0.015
  - orientation: mode=keep_current
  - parameter_bindings:
    - grasp_offset: status=consumed; consumers=target.offset.z (replace)
  - guards:
    - id=contact_guard, when=during_phase, predicate=force_below, on_failure=abort, threshold=20.0
- **grasp_1** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings: none
  - retries: max_attempts=1, strategy=offset_target, offset=[0.005, 0.005, 0.0]
- **lift_1** (`lift`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=world_z, distance=0.15, mode=add_to_offset, sign=positive}, tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset_along_axis.distance (replace)
- **transport_1** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.15], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - transport_height: status=consumed; consumers=target.offset.z (replace)
    - transport_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=grasp_hold_guard, when=during_phase, predicate=bilateral_grasp, on_failure=abort, threshold=2.0
- **place_descend_1** (`descend`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings: none
- **release_1** (`release`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings:
    - release_duration: status=consumed; consumers=duration.max_time (replace)

## Design Metrics

- **Composite score**: 0.177
- **task_score** (E): 0.307
- **fitness_score**: 0.627  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.450

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1014 |
| descend_1 | 1.00 | 1.00 | 0.1588 |
| grasp_1 | 1.00 | 1.00 | 0.0120 |
| lift_1 | 1.00 | 1.00 | 0.1359 |
| transport_1 | 1.00 | 1.00 | 0.2338 |
| place_descend_1 | 1.00 | 1.00 | 0.0888 |
| release_1 | 1.00 | 1.00 | 0.0213 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.497, 0.007, 0.204) | (0.497, 0.001, 0.030)→(0.497, 0.001, 0.026) | 0.263→0.265 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.497, 0.007, 0.204)→(0.493, 0.001, 0.046) | (0.497, 0.001, 0.026)→(0.497, 0.001, 0.026) | 0.265→0.265 | 1.00 / 4.000 | 41.536 | 0.123 |
| grasp_1 | grasp | 1.00 / step_budget | (0.493, 0.001, 0.046)→(0.484, 0.001, 0.037) | (0.497, 0.001, 0.026)→(0.497, 0.001, 0.026) | 0.265→0.265 | 1.00 / 44.333 | 0.146 | 0.211 |
| lift_1 | lift | 1.00 / step_budget | (0.484, 0.001, 0.037)→(0.492, 0.001, 0.173) | (0.497, 0.001, 0.026)→(0.510, 0.001, 0.155) | 0.265→0.212 | 1.00 / 23.333 | 0.109 | 0.513 |
| transport_1 | approach | 1.00 / step_budget | (0.492, 0.001, 0.173)→(0.576, 0.174, 0.283) | (0.510, 0.001, 0.155)→(0.565, 0.131, 0.016) | 0.212→0.182 | 1.00 / 8.333 | 91003.184 | 2.122 |
| place_descend_1 | descend | 1.00 / step_budget | (0.576, 0.174, 0.283)→(0.579, 0.182, 0.194) | (0.565, 0.131, 0.016)→(0.564, 0.130, 0.016) | 0.182→0.182 | 1.00 / 8.667 | 182004.576 | 0.126 |
| release_1 | release | 1.00 / step_budget | (0.579, 0.182, 0.194)→(0.573, 0.180, 0.215) | (0.564, 0.130, 0.016)→(0.564, 0.130, 0.016) | 0.182→0.182 | 1.00 / 4.000 | 0.123 | 0.123 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.410
- phase_score: 0.071
- phase_breakdown.reach_goal_score: 0.058
- phase_breakdown.reach_object_score: 0.122
- grasp_place_fitness: 0.668

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.668
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.410
- **Median Q (composite search score)**: 0.174
- **K-run variance**: 0.0011
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Parameters at lower bound**: transport_1.transport_height
- **Final σ (mean)**: 0.326


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `096c354712624ed6bd8f9b9cbbbc2b7d35a94d9c1517cfb8353e2e383be5aaf0`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.05,0.05],"goal_z_delta":0.15,"object_xy_delta":[0.05,0.05]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `3798aa6551d21849355469c7d63897f628ac7de9267c18bb4301fe6cfaae0164`; realized-scene SHA-256: `f07a678caf5b8ea43212ad5a337315ad102b1ae725b01cf669f7af9bd0eea2ea`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.5137,-0.02302,0.03]},{"name":"goal","value":[0.5541,0.15165,0.22199]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.5137,-0.02302,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.5541,0.15165,0.22199]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.90385,"average_solve_count":156.0,"average_success_count":156.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.16722,"descend_1.grasp_offset":0.00203,"lift_1.lift_height":0.1312,"release_1.release_duration":0.72127,"transport_1.transport_height":0.12897,"transport_1.transport_speed":0.13168},"optimized_scores":{"best_composite_score":0.13755,"best_fitness_score":0.58755,"best_task_score":0.22251},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":1793.0,"contact_point_centroid":[0.53942,0.06129,-0.00259],"force_p95":0.25257,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.04104,"mean_force":0.1491,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.53781,0.09904,0.28014]},{"body_a":"world","body_b":"grasp_target","contact_count":79.0,"contact_point_centroid":[0.51156,-0.021,-0.00141],"force_p95":0.47198,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54031,"mean_force":0.10633,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49942,-0.02166,0.03415]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5105.0,"contact_point_centroid":[0.50462,-0.00264,0.08182],"force_p95":0.10946,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30304,"mean_force":0.07066,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.50215,-0.02162,0.0794]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5666.0,"contact_point_centroid":[0.5045,-0.04047,0.07962],"force_p95":0.10437,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29107,"mean_force":0.06544,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.50202,-0.02163,0.07794]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3057.0,"contact_point_centroid":[0.51881,0.02544,0.16843],"force_p95":0.14214,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26702,"mean_force":0.09139,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.51299,0.00705,0.16847]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2743.0,"contact_point_centroid":[0.51825,-0.01346,0.16667],"force_p95":0.17349,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25318,"mean_force":0.09893,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.51257,0.00512,0.16627]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.51374,-0.02277,-0.00212],"force_p95":0.15765,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.22601,"mean_force":0.13192,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.50164,-0.02172,0.03396]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4074.0,"contact_point_centroid":[0.50103,-0.00248,0.03546],"force_p95":0.08034,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14594,"mean_force":0.05187,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.50047,-0.02169,0.03269]},{"body_a":"world","body_b":"grasp_target","contact_count":692.0,"contact_point_centroid":[0.5137,-0.02302,-0.00182],"force_p95":0.13762,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12333,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50367,-0.0024,0.25732]},{"body_a":"world","body_b":"grasp_target","contact_count":1592.0,"contact_point_centroid":[0.5137,-0.02302,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50745,-0.01729,0.12718]},{"body_a":"world","body_b":"grasp_target","contact_count":1144.0,"contact_point_centroid":[0.53932,0.06126,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":5.0,"phase_name":"place_descend_1","phase_type":"descend","tcp_position_centroid":[0.54989,0.14595,0.28316]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.53932,0.06126,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.54715,0.14854,0.23278]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4987.0,"contact_point_centroid":[0.50107,-0.04083,0.03454],"force_p95":0.07249,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08117,"mean_force":0.04463,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.50047,-0.02169,0.0327]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1684.0,"contact_point_centroid":[0.53965,0.1041,0.28859],"force_p95":0.01164,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0163,"mean_force":0.01063,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.53922,0.1041,0.28634]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1220.0,"contact_point_centroid":[0.55028,0.14598,0.28525],"force_p95":0.01099,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01271,"mean_force":0.01046,"phase_index":5.0,"phase_name":"place_descend_1","phase_type":"descend","tcp_position_centroid":[0.54989,0.14597,0.28291]},{"body_a":"left_finger","body_b":"right_finger","contact_count":225.0,"contact_point_centroid":[0.54986,0.1492,0.23037],"force_p95":0.01092,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01095,"mean_force":0.00991,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.54921,0.14918,0.22793]}],"total_contact_groups":16},"final_pose_error":0.01,"key_states":{"actual_goal_position":[0.5541,0.15165,0.22199],"final_object_position":[0.53932,0.06126,0.01602],"final_tcp_position":[0.55071,0.14955,0.23116],"realised_goal_position":[0.5541,0.15165,0.22199],"realised_object_initial_position":[0.5137,-0.02302,0.03]},"peak_contact_force":273009.34344,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":174.0,"n_steps_budget":1000.0,"object_pos_end":[0.5137,-0.02302,0.02602],"object_pos_start":[0.5137,-0.02302,0.03],"object_to_goal_dist_end":0.26561,"object_to_goal_dist_start":0.26269,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":692.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.50826,-0.01282,0.21305],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.18739,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":398.0,"n_steps_budget":1000.0,"object_pos_end":[0.5137,-0.02302,0.02602],"object_pos_start":[0.5137,-0.02302,0.02602],"object_to_goal_dist_end":0.26561,"object_to_goal_dist_start":0.26561,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1592.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.50886,-0.02185,0.04197],"tcp_start":[0.50826,-0.01282,0.21305],"tcp_to_object_dist_end":0.01671,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.5136,-0.02177,0.02559],"object_pos_start":[0.5137,-0.02302,0.02602],"object_to_goal_dist_end":0.26512,"object_to_goal_dist_start":0.26561,"object_z_max":0.02602,"peak_contact_force":0.15067,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10861.0,"raw_peak_contact_force":0.22601,"tcp_end":[0.50044,-0.02169,0.03266],"tcp_start":[0.50886,-0.02185,0.04197],"tcp_to_object_dist_end":0.01494,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":347.0,"n_steps_budget":780.0,"object_pos_end":[0.52624,-0.02175,0.12573],"object_pos_start":[0.5136,-0.02177,0.02559],"object_to_goal_dist_end":0.20028,"object_to_goal_dist_start":0.26512,"object_z_max":0.12548,"peak_contact_force":0.10942,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":10850.0,"raw_peak_contact_force":0.54031,"subtask_id":"reach_object","tcp_end":[0.5083,-0.02165,0.13774],"tcp_start":[0.50044,-0.02169,0.03266],"tcp_to_object_dist_end":0.02159,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":812.0,"n_steps_budget":1000.0,"object_pos_end":[0.53932,0.06126,0.01602],"object_pos_start":[0.52624,-0.02175,0.12573],"object_to_goal_dist_end":0.22542,"object_to_goal_dist_start":0.20028,"object_z_max":0.18001,"peak_contact_force":273009.34344,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":9277.0,"raw_peak_contact_force":2.04104,"subtask_id":"reach_goal","tcp_end":[0.55009,0.14288,0.33373],"tcp_start":[0.5083,-0.02165,0.13774],"tcp_to_object_dist_end":0.3282,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":286.0,"n_steps_budget":1000.0,"object_pos_end":[0.53932,0.06126,0.01602],"object_pos_start":[0.53932,0.06126,0.01602],"object_to_goal_dist_end":0.22542,"object_to_goal_dist_start":0.22542,"object_z_max":0.01602,"peak_contact_force":273005.41513,"phase_name":"place_descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2364.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_goal","tcp_end":[0.55071,0.14955,0.23116],"tcp_start":[0.55009,0.14288,0.33373],"tcp_to_object_dist_end":0.23283,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53932,0.06126,0.01602],"object_pos_start":[0.53932,0.06126,0.01602],"object_to_goal_dist_end":0.22542,"object_to_goal_dist_start":0.22542,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1025.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.54596,0.14815,0.25306],"tcp_start":[0.55071,0.14955,0.23116],"tcp_to_object_dist_end":0.25256,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `ed2df336ade3d991e9495251c8398520a59dd014a70bd2d7bb71dc7aefccaa8a`; realized-scene SHA-256: `a2ed2c4162d37489f2d2d0fa0373774d72c951d58f2469e0ba2d602ff46b6cfb`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50118,0.04505,0.03]},{"name":"goal","value":[0.56442,0.24486,0.14677]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.50118,0.04505,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.56442,0.24486,0.14677]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.02963,"average_solve_count":135.0,"average_success_count":135.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.07159,"descend_1.grasp_offset":0.0148,"lift_1.lift_height":0.17857,"release_1.release_duration":0.58627,"transport_1.transport_height":0.10285,"transport_1.transport_speed":0.24256},"optimized_scores":{"best_composite_score":0.21827,"best_fitness_score":0.66827,"best_task_score":0.41009},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":225.0,"contact_point_centroid":[0.5667,0.21642,-0.00699],"force_p95":1.39442,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.94517,"mean_force":0.36748,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.55412,0.22056,0.23494]},{"body_a":"world","body_b":"grasp_target","contact_count":77.0,"contact_point_centroid":[0.49903,0.04398,-0.00136],"force_p95":0.35902,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.40794,"mean_force":0.08104,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48712,0.04413,0.04723]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":7340.0,"contact_point_centroid":[0.49287,0.06285,0.1069],"force_p95":0.10686,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27819,"mean_force":0.0665,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48984,0.04397,0.10507]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6571.0,"contact_point_centroid":[0.49264,0.02504,0.10843],"force_p95":0.11116,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27003,"mean_force":0.07205,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48998,0.04397,0.10702]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3776.0,"contact_point_centroid":[0.52129,0.08602,0.19957],"force_p95":0.15142,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26601,"mean_force":0.09089,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.51495,0.10462,0.19986]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4160.0,"contact_point_centroid":[0.52188,0.12544,0.19994],"force_p95":0.12826,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21113,"mean_force":0.08302,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.51576,0.10714,0.20057]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.5012,0.04496,-0.00207],"force_p95":0.1434,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.18884,"mean_force":0.128,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.48929,0.04435,0.04701]},{"body_a":"world","body_b":"grasp_target","contact_count":1432.0,"contact_point_centroid":[0.50118,0.04505,-0.00191],"force_p95":0.13533,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12297,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49821,0.03196,0.21446]},{"body_a":"world","body_b":"grasp_target","contact_count":952.0,"contact_point_centroid":[0.5672,0.21708,-0.00194],"force_p95":0.13003,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13325,"mean_force":0.11978,"phase_index":5.0,"phase_name":"place_descend_1","phase_type":"descend","tcp_position_centroid":[0.55769,0.23513,0.19633]},{"body_a":"world","body_b":"grasp_target","contact_count":628.0,"contact_point_centroid":[0.50118,0.04505,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49613,0.04573,0.08781]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.5672,0.21707,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.5553,0.23889,0.15518]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4350.0,"contact_point_centroid":[0.48845,0.025,0.04779],"force_p95":0.07559,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12258,"mean_force":0.04965,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.48817,0.04425,0.0458]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5405.0,"contact_point_centroid":[0.48901,0.06338,0.04823],"force_p95":0.06705,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07475,"mean_force":0.04075,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.48817,0.04425,0.0458]},{"body_a":"left_finger","body_b":"right_finger","contact_count":20.0,"contact_point_centroid":[0.55737,0.22953,0.23972],"force_p95":0.0165,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0165,"mean_force":0.01566,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.5571,0.22951,0.23764]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1013.0,"contact_point_centroid":[0.5582,0.23514,0.19873],"force_p95":0.01182,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0146,"mean_force":0.01066,"phase_index":5.0,"phase_name":"place_descend_1","phase_type":"descend","tcp_position_centroid":[0.55769,0.23511,0.1965]},{"body_a":"left_finger","body_b":"right_finger","contact_count":220.0,"contact_point_centroid":[0.55848,0.24018,0.15311],"force_p95":0.01102,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01103,"mean_force":0.0101,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.5579,0.24014,0.15092]}],"total_contact_groups":16},"final_pose_error":0.00982,"key_states":{"actual_goal_position":[0.56442,0.24486,0.14677],"final_object_position":[0.5672,0.21707,0.01602],"final_tcp_position":[0.55968,0.24082,0.15437],"realised_goal_position":[0.56442,0.24486,0.14677],"realised_object_initial_position":[0.50118,0.04505,0.03]},"peak_contact_force":273008.19087,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":359.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.03],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.23992,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1432.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.4977,0.04659,0.12085],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.09491,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":157.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"peak_contact_force":43.34231,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":628.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.49623,0.04502,0.05471],"tcp_start":[0.4977,0.04659,0.12085],"tcp_to_object_dist_end":0.02912,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50111,0.04439,0.02574],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.24258,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"peak_contact_force":0.14225,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11555.0,"raw_peak_contact_force":0.18884,"tcp_end":[0.48814,0.04425,0.04577],"tcp_start":[0.49623,0.04502,0.05471],"tcp_to_object_dist_end":0.02387,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":26.0,"n_steps":451.0,"n_steps_budget":990.0,"object_pos_end":[0.51157,0.04445,0.1592],"object_pos_start":[0.50111,0.04439,0.02574],"object_to_goal_dist_end":0.20764,"object_to_goal_dist_start":0.24258,"object_z_max":0.15894,"peak_contact_force":0.09835,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":13988.0,"raw_peak_contact_force":0.40794,"subtask_id":"reach_object","tcp_end":[0.49656,0.04405,0.18498],"tcp_start":[0.48814,0.04425,0.04577],"tcp_to_object_dist_end":0.02984,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":508.0,"n_steps_budget":1000.0,"object_pos_end":[0.56791,0.2191,0.01506],"object_pos_start":[0.51157,0.04445,0.1592],"object_to_goal_dist_end":0.13426,"object_to_goal_dist_start":0.20764,"object_z_max":0.18593,"peak_contact_force":0.08448,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":8181.0,"raw_peak_contact_force":1.94517,"subtask_id":"reach_goal","tcp_end":[0.55735,0.23036,0.23788],"tcp_start":[0.49656,0.04405,0.18498],"tcp_to_object_dist_end":0.22336,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":238.0,"n_steps_budget":1000.0,"object_pos_end":[0.5672,0.21707,0.01602],"object_pos_start":[0.56791,0.2191,0.01506],"object_to_goal_dist_end":0.13371,"object_to_goal_dist_start":0.13426,"object_z_max":0.01686,"peak_contact_force":273008.19087,"phase_name":"place_descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1965.0,"raw_peak_contact_force":0.13325,"subtask_id":"reach_goal","tcp_end":[0.55968,0.24082,0.15437],"tcp_start":[0.55735,0.23036,0.23788],"tcp_to_object_dist_end":0.14057,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.5672,0.21707,0.01602],"object_pos_start":[0.5672,0.21707,0.01602],"object_to_goal_dist_end":0.13371,"object_to_goal_dist_start":0.13371,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1020.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.55376,0.23814,0.17511],"tcp_start":[0.55968,0.24082,0.15437],"tcp_to_object_dist_end":0.16104,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `291bc6f2bd023fc25503740a7343328e565e43fc71fa3c9c5d2fdbe2d4351fd2`; realized-scene SHA-256: `67b45068113fe0ef6f199d4981822d51bd0bd66bb4f388f7402a08094b41852a`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.47616,-0.02015,0.03]},{"name":"goal","value":[0.63142,0.15919,0.19002]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.47616,-0.02015,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.63142,0.15919,0.19002]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.94904,"average_solve_count":157.0,"average_success_count":157.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.23272,"descend_1.grasp_offset":0.0001,"lift_1.lift_height":0.18861,"release_1.release_duration":0.68874,"transport_1.transport_height":0.1,"transport_1.transport_speed":0.20181},"optimized_scores":{"best_composite_score":0.17407,"best_fitness_score":0.62407,"best_task_score":0.28968},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":843.0,"contact_point_centroid":[0.58662,0.1117,-0.00351],"force_p95":0.69802,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.38058,"mean_force":0.18169,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.59728,0.12293,0.26348]},{"body_a":"world","body_b":"grasp_target","contact_count":73.0,"contact_point_centroid":[0.47368,-0.01897,-0.00141],"force_p95":0.55241,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.59129,"mean_force":0.13411,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46377,-0.01923,0.03361]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3021.0,"contact_point_centroid":[0.51089,0.00169,0.21129],"force_p95":0.17502,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27848,"mean_force":0.10539,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.50533,0.02016,0.21181]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8287.0,"contact_point_centroid":[0.46812,-0.03813,0.10337],"force_p95":0.10508,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27489,"mean_force":0.06446,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46588,-0.01922,0.10166]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":7737.0,"contact_point_centroid":[0.46815,-0.00023,0.10483],"force_p95":0.10931,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27075,"mean_force":0.06804,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46596,-0.01922,0.10261]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3458.0,"contact_point_centroid":[0.51338,0.04092,0.21233],"force_p95":0.15497,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26202,"mean_force":0.09362,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.50749,0.02268,0.21295]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.47618,-0.02002,-0.00208],"force_p95":0.14647,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.21912,"mean_force":0.12917,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46593,-0.01928,0.03334]},{"body_a":"world","body_b":"grasp_target","contact_count":252.0,"contact_point_centroid":[0.47616,-0.02015,-0.00149],"force_p95":0.13832,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12478,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49262,-0.00536,0.29104]},{"body_a":"world","body_b":"grasp_target","contact_count":2228.0,"contact_point_centroid":[0.47616,-0.02015,-0.00199],"force_p95":0.12264,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12353,"mean_force":0.1226,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.4779,-0.01552,0.15883]},{"body_a":"world","body_b":"grasp_target","contact_count":848.0,"contact_point_centroid":[0.58665,0.11165,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"place_descend_1","phase_type":"descend","tcp_position_centroid":[0.62261,0.15235,0.23774]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.58665,0.11165,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.62195,0.15513,0.19742]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5292.0,"contact_point_centroid":[0.46423,-1e-05,0.03381],"force_p95":0.06583,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10581,"mean_force":0.04116,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46483,-0.01926,0.03226]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5438.0,"contact_point_centroid":[0.46423,-0.03855,0.0337],"force_p95":0.06588,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07797,"mean_force":0.0411,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46484,-0.01926,0.03226]},{"body_a":"left_finger","body_b":"right_finger","contact_count":703.0,"contact_point_centroid":[0.60304,0.12874,0.26867],"force_p95":0.01325,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01649,"mean_force":0.01086,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.60252,0.12874,0.26643]},{"body_a":"left_finger","body_b":"right_finger","contact_count":220.0,"contact_point_centroid":[0.62496,0.15591,0.19616],"force_p95":0.01097,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01099,"mean_force":0.01014,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.62438,0.15589,0.19389]},{"body_a":"left_finger","body_b":"right_finger","contact_count":917.0,"contact_point_centroid":[0.62291,0.15235,0.24015],"force_p95":0.01094,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01098,"mean_force":0.01032,"phase_index":5.0,"phase_name":"place_descend_1","phase_type":"descend","tcp_position_centroid":[0.6226,0.15234,0.23783]}],"total_contact_groups":16},"final_pose_error":0.00995,"key_states":{"actual_goal_position":[0.63142,0.15919,0.19002],"final_object_position":[0.58665,0.11165,0.01602],"final_tcp_position":[0.62605,0.15628,0.19786],"realised_goal_position":[0.63142,0.15919,0.19002],"realised_object_initial_position":[0.47616,-0.02015,0.03]},"peak_contact_force":81.14225,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":64.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02588],"object_pos_start":[0.47616,-0.02015,0.03],"object_to_goal_dist_end":0.28846,"object_to_goal_dist_start":0.28614,"object_z_max":0.03,"peak_contact_force":0.12371,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":252.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.48478,-0.0117,0.27862],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.25303,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":557.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.02588],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28846,"object_z_max":0.02602,"peak_contact_force":81.14225,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2228.0,"raw_peak_contact_force":0.12353,"subtask_id":"reach_object","tcp_end":[0.47278,-0.01941,0.04029],"tcp_start":[0.48478,-0.0117,0.27862],"tcp_to_object_dist_end":0.01468,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":48.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.47606,-0.0194,0.0257],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28816,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.14363,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12530.0,"raw_peak_contact_force":0.21912,"tcp_end":[0.46481,-0.01926,0.03223],"tcp_start":[0.47278,-0.01941,0.04029],"tcp_to_object_dist_end":0.01301,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":21.0,"n_steps":506.0,"n_steps_budget":1000.0,"object_pos_end":[0.49069,-0.01934,0.1815],"object_pos_start":[0.47606,-0.0194,0.0257],"object_to_goal_dist_end":0.22749,"object_to_goal_dist_start":0.28816,"object_z_max":0.18124,"peak_contact_force":0.11944,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":16097.0,"raw_peak_contact_force":0.59129,"subtask_id":"reach_object","tcp_end":[0.47193,-0.01929,0.19498],"tcp_start":[0.46481,-0.01926,0.03223],"tcp_to_object_dist_end":0.0231,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":644.0,"n_steps_budget":1000.0,"object_pos_end":[0.58665,0.11165,0.01602],"object_pos_start":[0.49069,-0.01934,0.1815],"object_to_goal_dist_end":0.18585,"object_to_goal_dist_start":0.22749,"object_z_max":0.21017,"peak_contact_force":0.12262,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":8025.0,"raw_peak_contact_force":2.38058,"subtask_id":"reach_goal","tcp_end":[0.62075,0.14905,0.27665],"tcp_start":[0.47193,-0.01929,0.19498],"tcp_to_object_dist_end":0.2655,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":212.0,"n_steps_budget":1000.0,"object_pos_end":[0.58665,0.11165,0.01602],"object_pos_start":[0.58665,0.11165,0.01602],"object_to_goal_dist_end":0.18585,"object_to_goal_dist_start":0.18585,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"place_descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1765.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_goal","tcp_end":[0.62605,0.15628,0.19786],"tcp_start":[0.62075,0.14905,0.27665],"tcp_to_object_dist_end":0.19134,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.58665,0.11165,0.01602],"object_pos_start":[0.58665,0.11165,0.01602],"object_to_goal_dist_end":0.18585,"object_to_goal_dist_start":0.18585,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1020.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.62053,0.15468,0.21682],"tcp_start":[0.62605,0.15628,0.19786],"tcp_to_object_dist_end":0.20813,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```