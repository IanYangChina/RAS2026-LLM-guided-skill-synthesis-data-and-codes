## Search State

- **Seed**: 0
- **Iteration**: 9 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 8 | approach → descend → grasp → lift → approach → descend → release | arc_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | impedance_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 6 | 0.2085 | 0.38 | ❌ rejected |
| 7 | approach → descend → grasp → lift → approach → descend → release | arc_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 6 | 0.1637 | 0.28 | ❌ rejected |
| 6 | approach → descend → grasp → lift → approach → descend → release | arc_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | impedance_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 6 | 0.2085 | 0.38 | ❌ rejected |
| 5 | approach → descend → grasp → lift → approach → descend → release | arc_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 6 | 0.1766 | 0.31 | ❌ rejected |
| 4 | approach → descend → grasp → lift → approach → descend → release | arc_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 6 | 0.2352 | 0.43 | ✅ accepted |

**Proposal policy**: task_score is 0.38 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.209) — your mutation base

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

- **Composite score**: 0.209
- **task_score** (E): 0.377
- **fitness_score**: 0.659  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.450

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1240 |
| descend_1 | 1.00 | 1.00 | 0.1326 |
| grasp_1 | 1.00 | 1.00 | 0.0120 |
| lift_1 | 1.00 | 1.00 | 0.1115 |
| transport_1 | 0.00 | 1.00 | 0.1366 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.495, 0.007, 0.180) | (0.497, 0.001, 0.030)→(0.497, 0.001, 0.026) | 0.263→0.265 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.495, 0.007, 0.180)→(0.493, 0.001, 0.048) | (0.497, 0.001, 0.026)→(0.497, 0.001, 0.026) | 0.265→0.265 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_1 | grasp | 1.00 / step_budget | (0.493, 0.001, 0.048)→(0.484, 0.001, 0.039) | (0.497, 0.001, 0.026)→(0.497, 0.001, 0.026) | 0.265→0.265 | 1.00 / 41.667 | 0.155 | 0.220 |
| lift_1 | lift | 1.00 / step_budget | (0.484, 0.001, 0.039)→(0.492, 0.001, 0.151) | (0.497, 0.001, 0.026)→(0.507, 0.001, 0.132) | 0.265→0.216 | 1.00 / 21.667 | 0.118 | 0.474 |
| transport_1 | approach | 0.00 / guard_failure | (0.492, 0.001, 0.151)→(0.522, 0.061, 0.266) | (0.507, 0.001, 0.132)→(0.532, 0.060, 0.236) | 0.216→0.148 | 1.00 / 9.000 | 0.010 | 0.263 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.439
- phase_score: 0.099
- phase_breakdown.reach_goal_score: 0.056
- phase_breakdown.reach_object_score: 0.273
- grasp_place_fitness: 0.676

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.676
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.439
- **Median Q (composite search score)**: 0.209
- **K-run variance**: 0.0002
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.335


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.46711,"average_solve_count":152.0,"average_success_count":152.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.14651,"descend_1.grasp_offset":0.02005,"lift_1.lift_height":0.13865,"release_1.release_duration":0.63353,"transport_1.transport_height":0.21348,"transport_1.transport_speed":0.05244},"optimized_scores":{"best_composite_score":0.22649,"best_fitness_score":0.67649,"best_task_score":0.43928},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":84.0,"contact_point_centroid":[0.51251,-0.02008,-0.00151],"force_p95":0.2925,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.33598,"mean_force":0.06166,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49968,-0.0214,0.05226]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3408.0,"contact_point_centroid":[0.50532,-0.00264,0.08901],"force_p95":0.14186,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33587,"mean_force":0.09353,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.50226,-0.02145,0.09108]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5524.0,"contact_point_centroid":[0.51759,-0.0135,0.2233],"force_p95":0.14796,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26786,"mean_force":0.10663,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.51247,0.00454,0.22648]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4993.0,"contact_point_centroid":[0.50406,-0.03971,0.09043],"force_p95":0.1308,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25465,"mean_force":0.07054,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.5022,-0.02145,0.09066]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5068.0,"contact_point_centroid":[0.51837,0.02421,0.22761],"force_p95":0.14371,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23778,"mean_force":0.11227,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.5129,0.00612,0.23106]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.51372,-0.02296,-0.00216],"force_p95":0.16996,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.215,"mean_force":0.13429,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.50184,-0.02145,0.05189]},{"body_a":"world","body_b":"grasp_target","contact_count":844.0,"contact_point_centroid":[0.5137,-0.02302,-0.00185],"force_p95":0.13728,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12321,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50369,-0.00127,0.24705]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3672.0,"contact_point_centroid":[0.50259,-0.00231,0.0504],"force_p95":0.10714,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12908,"mean_force":0.06014,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.5007,-0.02142,0.05062]},{"body_a":"world","body_b":"grasp_target","contact_count":1240.0,"contact_point_centroid":[0.5137,-0.02302,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50758,-0.01716,0.12624]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5000.0,"contact_point_centroid":[0.50112,-0.0402,0.05092],"force_p95":0.07136,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0752,"mean_force":0.04257,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.5007,-0.02142,0.05062]}],"total_contact_groups":10},"final_pose_error":0.16801,"key_states":{"actual_goal_position":[0.5541,0.15165,0.22199],"final_object_position":[0.53001,0.04141,0.27191],"final_tcp_position":[0.52322,0.04295,0.31115],"realised_goal_position":[0.5541,0.15165,0.22199],"realised_object_initial_position":[0.5137,-0.02302,0.03]},"peak_contact_force":0.33598,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":212.0,"n_steps_budget":1000.0,"object_pos_end":[0.5137,-0.02302,0.02602],"object_pos_start":[0.5137,-0.02302,0.03],"object_to_goal_dist_end":0.26561,"object_to_goal_dist_start":0.26269,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":844.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.50846,-0.01284,0.19283],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.16721,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":310.0,"n_steps_budget":1000.0,"object_pos_end":[0.5137,-0.02302,0.02602],"object_pos_start":[0.5137,-0.02302,0.02602],"object_to_goal_dist_end":0.26561,"object_to_goal_dist_start":0.26561,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1240.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.50887,-0.02158,0.05993],"tcp_start":[0.50846,-0.01284,0.19283],"tcp_to_object_dist_end":0.03428,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":39.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51365,-0.02173,0.0253],"object_pos_start":[0.5137,-0.02302,0.02602],"object_to_goal_dist_end":0.2653,"object_to_goal_dist_start":0.26561,"object_z_max":0.02602,"peak_contact_force":0.17146,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10472.0,"raw_peak_contact_force":0.215,"tcp_end":[0.50067,-0.02142,0.05058],"tcp_start":[0.50887,-0.02158,0.05993],"tcp_to_object_dist_end":0.02842,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":20.0,"n_steps":313.0,"n_steps_budget":720.0,"object_pos_end":[0.51913,-0.02293,0.1139],"object_pos_start":[0.51365,-0.02173,0.0253],"object_to_goal_dist_end":0.20829,"object_to_goal_dist_start":0.2653,"object_z_max":0.11365,"peak_contact_force":0.13463,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":8485.0,"raw_peak_contact_force":0.33598,"subtask_id":"reach_object","tcp_end":[0.50827,-0.02159,0.14475],"tcp_start":[0.50067,-0.02142,0.05058],"tcp_to_object_dist_end":0.03274,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":638.0,"n_steps_budget":1000.0,"object_pos_end":[0.53001,0.04141,0.27191],"object_pos_start":[0.51913,-0.02293,0.1139],"object_to_goal_dist_end":0.12339,"object_to_goal_dist_start":0.20829,"object_z_max":0.27185,"peak_contact_force":0.01017,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":10592.0,"raw_peak_contact_force":0.26786,"subtask_id":"reach_goal","tcp_end":[0.52322,0.04295,0.31115],"tcp_start":[0.50827,-0.02159,0.14475],"tcp_to_object_dist_end":0.03985,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.01942,"average_solve_count":103.0,"average_success_count":103.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.09451,"descend_1.grasp_offset":0.00124,"lift_1.lift_height":0.11622,"release_1.release_duration":0.53838,"transport_1.transport_height":0.20947,"transport_1.transport_speed":0.15736},"optimized_scores":{"best_composite_score":0.19022,"best_fitness_score":0.64022,"best_task_score":0.32665},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":78.0,"contact_point_centroid":[0.49924,0.04332,-0.00139],"force_p95":0.48432,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54734,"mean_force":0.11163,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48729,0.04386,0.03393]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2849.0,"contact_point_centroid":[0.5048,0.08073,0.16258],"force_p95":0.16541,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30008,"mean_force":0.09911,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.49922,0.06203,0.16171]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5216.0,"contact_point_centroid":[0.49154,0.06259,0.07377],"force_p95":0.10396,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29668,"mean_force":0.06146,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48977,0.04364,0.07188]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4683.0,"contact_point_centroid":[0.49205,0.02464,0.07571],"force_p95":0.10429,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29546,"mean_force":0.06672,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48994,0.04364,0.07342]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3272.0,"contact_point_centroid":[0.50522,0.04412,0.16311],"force_p95":0.143,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27827,"mean_force":0.08948,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.49936,0.0625,0.16265]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50121,0.04481,-0.00209],"force_p95":0.15001,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.21867,"mean_force":0.12995,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.48942,0.04409,0.03375]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4079.0,"contact_point_centroid":[0.48874,0.02478,0.03536],"force_p95":0.07945,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14233,"mean_force":0.05185,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.48827,0.04398,0.03254]},{"body_a":"world","body_b":"grasp_target","contact_count":1260.0,"contact_point_centroid":[0.50118,0.04505,-0.00189],"force_p95":0.13606,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12301,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49834,0.02992,0.22592]},{"body_a":"world","body_b":"grasp_target","contact_count":968.0,"contact_point_centroid":[0.50118,0.04505,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.4961,0.0451,0.09267]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4956.0,"contact_point_centroid":[0.48875,0.06311,0.03435],"force_p95":0.07205,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08546,"mean_force":0.04474,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.48827,0.04398,0.03255]}],"total_contact_groups":10},"final_pose_error":0.22447,"key_states":{"actual_goal_position":[0.56442,0.24486,0.14677],"final_object_position":[0.52455,0.08646,0.18532],"final_tcp_position":[0.50744,0.08685,0.20733],"realised_goal_position":[0.56442,0.24486,0.14677],"realised_object_initial_position":[0.50118,0.04505,0.03]},"peak_contact_force":0.54734,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":316.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.03],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.23992,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1260.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.49787,0.04565,0.144],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.11803,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":242.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":968.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.49649,0.04475,0.04142],"tcp_start":[0.49787,0.04565,0.144],"tcp_to_object_dist_end":0.0161,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50109,0.044,0.02568],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.24294,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"peak_contact_force":0.14408,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10835.0,"raw_peak_contact_force":0.21867,"tcp_end":[0.48824,0.04398,0.03251],"tcp_start":[0.49649,0.04475,0.04142],"tcp_to_object_dist_end":0.01455,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":298.0,"n_steps_budget":720.0,"object_pos_end":[0.51312,0.04384,0.11241],"object_pos_start":[0.50109,0.044,0.02568],"object_to_goal_dist_end":0.21029,"object_to_goal_dist_start":0.24294,"object_z_max":0.11216,"peak_contact_force":0.10622,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":9977.0,"raw_peak_contact_force":0.54734,"subtask_id":"reach_object","tcp_end":[0.49557,0.04362,0.1229],"tcp_start":[0.48824,0.04398,0.03251],"tcp_to_object_dist_end":0.02045,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":283.0,"n_steps_budget":1000.0,"object_pos_end":[0.52455,0.08646,0.18532],"object_pos_start":[0.51312,0.04384,0.11241],"object_to_goal_dist_end":0.16783,"object_to_goal_dist_start":0.21029,"object_z_max":0.18538,"peak_contact_force":0.01017,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":6121.0,"raw_peak_contact_force":0.30008,"subtask_id":"reach_goal","tcp_end":[0.50744,0.08685,0.20733],"tcp_start":[0.49557,0.04362,0.1229],"tcp_to_object_dist_end":0.02787,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.5443,"average_solve_count":158.0,"average_success_count":158.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.15752,"descend_1.grasp_offset":0.00249,"lift_1.lift_height":0.17755,"release_1.release_duration":0.44097,"transport_1.transport_height":0.1548,"transport_1.transport_speed":0.05154},"optimized_scores":{"best_composite_score":0.20886,"best_fitness_score":0.65886,"best_task_score":0.36439},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":75.0,"contact_point_centroid":[0.47385,-0.0183,-0.00142],"force_p95":0.49829,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.53876,"mean_force":0.11858,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46339,-0.01886,0.03603]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":7669.0,"contact_point_centroid":[0.46792,-0.03777,0.10029],"force_p95":0.10483,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28305,"mean_force":0.06443,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46567,-0.01887,0.09857]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":7072.0,"contact_point_centroid":[0.46796,0.00012,0.10186],"force_p95":0.10925,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28173,"mean_force":0.06849,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46575,-0.01888,0.09953]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.47619,-0.01998,-0.00211],"force_p95":0.15508,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.22547,"mean_force":0.13139,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46555,-0.0189,0.03567]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4354.0,"contact_point_centroid":[0.50293,0.0305,0.22691],"force_p95":0.15078,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22106,"mean_force":0.1012,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.4972,0.01212,0.22798]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4650.0,"contact_point_centroid":[0.50301,-0.00598,0.22681],"force_p95":0.13325,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2026,"mean_force":0.09621,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.49739,0.01229,0.22813]},{"body_a":"world","body_b":"grasp_target","contact_count":748.0,"contact_point_centroid":[0.47616,-0.02015,-0.00183],"force_p95":0.13759,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12328,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48921,-0.00071,0.2532]},{"body_a":"world","body_b":"grasp_target","contact_count":1540.0,"contact_point_centroid":[0.47616,-0.02015,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.47427,-0.01471,0.1233]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4803.0,"contact_point_centroid":[0.46445,0.00034,0.03688],"force_p95":0.07002,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12224,"mean_force":0.04494,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46445,-0.01888,0.03458]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5232.0,"contact_point_centroid":[0.46431,-0.03814,0.0364],"force_p95":0.069,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07613,"mean_force":0.0428,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46446,-0.01888,0.03459]}],"total_contact_groups":10},"final_pose_error":0.15722,"key_states":{"actual_goal_position":[0.63142,0.15919,0.19002],"final_object_position":[0.54189,0.05345,0.2511],"final_tcp_position":[0.53521,0.05427,0.2781],"realised_goal_position":[0.63142,0.15919,0.19002],"realised_object_initial_position":[0.47616,-0.02015,0.03]},"peak_contact_force":0.53876,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":188.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.03],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28614,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":748.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.47829,-0.01051,0.20435],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.17861,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":385.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1540.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.47237,-0.01902,0.0426],"tcp_start":[0.47829,-0.01051,0.20435],"tcp_to_object_dist_end":0.01705,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":45.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.47608,-0.0191,0.0256],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28802,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.15026,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11835.0,"raw_peak_contact_force":0.22547,"tcp_end":[0.46443,-0.01888,0.03455],"tcp_start":[0.47237,-0.01902,0.0426],"tcp_to_object_dist_end":0.0147,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":22.0,"n_steps":465.0,"n_steps_budget":1000.0,"object_pos_end":[0.48971,-0.01902,0.16875],"object_pos_start":[0.47608,-0.0191,0.0256],"object_to_goal_dist_end":0.22868,"object_to_goal_dist_start":0.28802,"object_z_max":0.16849,"peak_contact_force":0.11258,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":14816.0,"raw_peak_contact_force":0.53876,"subtask_id":"reach_object","tcp_end":[0.47177,-0.01898,0.18386],"tcp_start":[0.46443,-0.01888,0.03455],"tcp_to_object_dist_end":0.02345,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":474.0,"n_steps_budget":1000.0,"object_pos_end":[0.54189,0.05345,0.2511],"object_pos_start":[0.48971,-0.01902,0.16875],"object_to_goal_dist_end":0.15143,"object_to_goal_dist_start":0.22868,"object_z_max":0.25151,"peak_contact_force":0.01017,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":9004.0,"raw_peak_contact_force":0.22106,"subtask_id":"reach_goal","tcp_end":[0.53521,0.05427,0.2781],"tcp_start":[0.47177,-0.01898,0.18386],"tcp_to_object_dist_end":0.02782,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```