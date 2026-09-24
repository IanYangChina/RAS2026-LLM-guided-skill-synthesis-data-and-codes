## Search State

- **Seed**: 0
- **Iteration**: 15 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 14 | approach → descend → grasp → lift → approach → descend → release | arc_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 7 | 0.1186 | 0.29 | ❌ rejected |
| 13 | approach → descend → grasp → lift → approach → descend → release | arc_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 6 | 0.1749 | 0.30 | ❌ rejected |
| 12 | approach → descend → grasp → lift → approach → grasp → descend → release | arc_cartesian | linear_cartesian | — | arc_cartesian | arc_cartesian | — | linear_cartesian | — | position_control | position_control | position_control | impedance_control | impedance_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | time_limit | 7 | 0.1268 | 0.37 | ❌ rejected |
| 11 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 6 | 0.1606 | 0.30 | ❌ rejected |
| 10 | approach → contact → grasp → lift → approach → descend → release | arc_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | force_threshold_switch | position_control | position_control | position_control | position_control | position_control | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 6 | 0.1204 | 0.21 | ❌ rejected |

**Proposal policy**: task_score is 0.29 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.119) — your mutation base

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

- **Composite score**: 0.119
- **task_score** (E): 0.292
- **fitness_score**: 0.619  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.500

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.0666 |
| descend_1 | 1.00 | 1.00 | 0.2082 |
| grasp_1 | 1.00 | 1.00 | 0.0120 |
| lift_1 | 1.00 | 1.00 | 0.1365 |
| transport_1 | 1.00 | 0.67 | 0.2385 |
| place_descend_1 | 1.00 | 1.00 | 0.0953 |
| release_1 | 1.00 | 1.00 | 0.0212 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.499, 0.003, 0.254) | (0.497, 0.001, 0.030)→(0.497, 0.001, 0.026) | 0.263→0.265 | 1.00 / 4.000 | 0.125 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.499, 0.003, 0.254)→(0.493, 0.001, 0.046) | (0.497, 0.001, 0.026)→(0.497, 0.001, 0.026) | 0.265→0.265 | 1.00 / 4.000 | 27.129 | 0.125 |
| grasp_1 | grasp | 1.00 / step_budget | (0.493, 0.001, 0.046)→(0.485, 0.001, 0.037) | (0.497, 0.001, 0.026)→(0.497, 0.001, 0.025) | 0.265→0.266 | 1.00 / 45.667 | 0.159 | 0.231 |
| lift_1 | lift | 1.00 / step_budget | (0.485, 0.001, 0.037)→(0.492, 0.001, 0.174) | (0.497, 0.001, 0.025)→(0.509, 0.001, 0.156) | 0.266→0.209 | 1.00 / 23.333 | 0.108 | 0.523 |
| transport_1 | approach | 1.00 / step_budget | (0.492, 0.001, 0.174)→(0.577, 0.175, 0.305) | (0.509, 0.001, 0.156)→(0.567, 0.131, 0.044) | 0.209→0.159 | 0.67 / 5.333 | 3249.599 | 1.329 |
| place_descend_1 | descend | 1.00 / step_budget | (0.577, 0.175, 0.305)→(0.579, 0.182, 0.210) | (0.567, 0.131, 0.044)→(0.570, 0.135, 0.016) | 0.159→0.187 | 1.00 / 8.667 | 185253.912 | 0.707 |
| release_1 | release | 1.00 / step_budget | (0.579, 0.182, 0.210)→(0.574, 0.180, 0.230) | (0.570, 0.135, 0.016)→(0.570, 0.135, 0.016) | 0.187→0.187 | 1.00 / 4.000 | 0.123 | 0.123 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.310
- phase_score: 0.494
- phase_breakdown.reach_goal_score: 0.570
- phase_breakdown.reach_object_score: 0.187
- grasp_place_fitness: 0.632

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.632
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.339
- **Median Q (composite search score)**: 0.132
- **K-run variance**: 0.0004
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.432


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.04348,"average_solve_count":138.0,"average_success_count":138.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.10677,"descend_1.grasp_offset":5e-05,"lift_1.lift_height":0.16457,"place_descend_1.place_height":0.01208,"release_1.release_duration":0.78707,"transport_1.transport_height":0.10014,"transport_1.transport_speed":0.21636},"optimized_scores":{"best_composite_score":0.09091,"best_fitness_score":0.59091,"best_task_score":0.22758},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":1226.0,"contact_point_centroid":[0.53249,0.07168,-0.00287],"force_p95":0.45116,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.83299,"mean_force":0.16418,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.53809,0.09894,0.26994]},{"body_a":"world","body_b":"grasp_target","contact_count":80.0,"contact_point_centroid":[0.51084,-0.02057,-0.00145],"force_p95":0.51157,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.5729,"mean_force":0.11805,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49914,-0.02124,0.03232]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1664.0,"contact_point_centroid":[0.51906,0.02215,0.1873],"force_p95":0.18702,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31724,"mean_force":0.10887,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.51316,0.00372,0.18862]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6344.0,"contact_point_centroid":[0.50525,-0.00232,0.09522],"force_p95":0.11234,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30633,"mean_force":0.07465,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.5021,-0.02122,0.09295]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6918.0,"contact_point_centroid":[0.50504,-0.04001,0.09241],"force_p95":0.10898,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29969,"mean_force":0.07008,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.50193,-0.02122,0.09071]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1765.0,"contact_point_centroid":[0.51876,-0.01619,0.18596],"force_p95":0.18129,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28367,"mean_force":0.1058,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.51286,0.00216,0.18747]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.51376,-0.02271,-0.00216],"force_p95":0.16931,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24569,"mean_force":0.13494,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.50143,-0.0213,0.03207]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4056.0,"contact_point_centroid":[0.50091,-0.00206,0.03356],"force_p95":0.08198,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15219,"mean_force":0.05194,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.50025,-0.02127,0.0308]},{"body_a":"world","body_b":"grasp_target","contact_count":1144.0,"contact_point_centroid":[0.5137,-0.02302,-0.00188],"force_p95":0.13644,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12305,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.5037,0.00102,0.22696]},{"body_a":"world","body_b":"grasp_target","contact_count":1064.0,"contact_point_centroid":[0.5137,-0.02302,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50755,-0.01721,0.09653]},{"body_a":"world","body_b":"grasp_target","contact_count":748.0,"contact_point_centroid":[0.53223,0.07166,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":5.0,"phase_name":"place_descend_1","phase_type":"descend","tcp_position_centroid":[0.54935,0.14434,0.27519]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.53223,0.07166,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.54692,0.14758,0.24411]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5035.0,"contact_point_centroid":[0.50091,-0.04045,0.03264],"force_p95":0.07431,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08409,"mean_force":0.04461,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.50026,-0.02127,0.03081]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1078.0,"contact_point_centroid":[0.54048,0.1064,0.27874],"force_p95":0.01271,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01709,"mean_force":0.01074,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.54014,0.1064,0.27646]},{"body_a":"left_finger","body_b":"right_finger","contact_count":809.0,"contact_point_centroid":[0.54977,0.14433,0.2776],"force_p95":0.01095,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01278,"mean_force":0.01031,"phase_index":5.0,"phase_name":"place_descend_1","phase_type":"descend","tcp_position_centroid":[0.54935,0.14432,0.27542]},{"body_a":"left_finger","body_b":"right_finger","contact_count":223.0,"contact_point_centroid":[0.54943,0.14823,0.2415],"force_p95":0.01094,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01095,"mean_force":0.01,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.54889,0.14822,0.23927]}],"total_contact_groups":16},"final_pose_error":0.00972,"key_states":{"actual_goal_position":[0.5541,0.15165,0.22199],"final_object_position":[0.53223,0.07166,0.01602],"final_tcp_position":[0.55033,0.14852,0.24247],"realised_goal_position":[0.5541,0.15165,0.22199],"realised_object_initial_position":[0.5137,-0.02302,0.03]},"peak_contact_force":9748.93729,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":287.0,"n_steps_budget":1000.0,"object_pos_end":[0.5137,-0.02302,0.02602],"object_pos_start":[0.5137,-0.02302,0.03],"object_to_goal_dist_end":0.26561,"object_to_goal_dist_start":0.26269,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1144.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.50869,-0.0131,0.15316],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.12762,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":266.0,"n_steps_budget":1000.0,"object_pos_end":[0.5137,-0.02302,0.02602],"object_pos_start":[0.5137,-0.02302,0.02602],"object_to_goal_dist_end":0.26561,"object_to_goal_dist_start":0.26561,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1064.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.50867,-0.02141,0.04007],"tcp_start":[0.50869,-0.0131,0.15316],"tcp_to_object_dist_end":0.01501,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51361,-0.02139,0.02546],"object_pos_start":[0.5137,-0.02302,0.02602],"object_to_goal_dist_end":0.26496,"object_to_goal_dist_start":0.26561,"object_z_max":0.02602,"peak_contact_force":0.15995,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10891.0,"raw_peak_contact_force":0.24569,"tcp_end":[0.50023,-0.02127,0.03077],"tcp_start":[0.50867,-0.02141,0.04007],"tcp_to_object_dist_end":0.0144,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":24.0,"n_steps":458.0,"n_steps_budget":990.0,"object_pos_end":[0.52784,-0.02141,0.15769],"object_pos_start":[0.51361,-0.02139,0.02546],"object_to_goal_dist_end":0.18648,"object_to_goal_dist_start":0.26496,"object_z_max":0.15744,"peak_contact_force":0.11013,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":13342.0,"raw_peak_contact_force":0.5729,"subtask_id":"reach_object","tcp_end":[0.50884,-0.02128,0.17064],"tcp_start":[0.50023,-0.02127,0.03077],"tcp_to_object_dist_end":0.02299,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":576.0,"n_steps_budget":1000.0,"object_pos_end":[0.53223,0.07166,0.01602],"object_pos_start":[0.52784,-0.02141,0.15769],"object_to_goal_dist_end":0.22204,"object_to_goal_dist_start":0.18648,"object_z_max":0.18781,"peak_contact_force":0.12263,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":5733.0,"raw_peak_contact_force":1.83299,"subtask_id":"reach_goal","tcp_end":[0.54945,0.14074,0.30622],"tcp_start":[0.50884,-0.02128,0.17064],"tcp_to_object_dist_end":0.29881,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":187.0,"n_steps_budget":1000.0,"object_pos_end":[0.53223,0.07166,0.01602],"object_pos_start":[0.53223,0.07166,0.01602],"object_to_goal_dist_end":0.22204,"object_to_goal_dist_start":0.22204,"object_z_max":0.01602,"peak_contact_force":9748.93729,"phase_name":"place_descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1557.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_goal","tcp_end":[0.55033,0.14852,0.24247],"tcp_start":[0.54945,0.14074,0.30622],"tcp_to_object_dist_end":0.23982,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53223,0.07166,0.01602],"object_pos_start":[0.53223,0.07166,0.01602],"object_to_goal_dist_end":0.22204,"object_to_goal_dist_start":0.22204,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1023.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.5458,0.14721,0.26439],"tcp_start":[0.55033,0.14852,0.24247],"tcp_to_object_dist_end":0.25996,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.91018,"average_solve_count":167.0,"average_success_count":167.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.29937,"descend_1.grasp_offset":0.0148,"lift_1.lift_height":0.18052,"place_descend_1.place_height":0.01383,"release_1.release_duration":0.6243,"transport_1.transport_height":0.20102,"transport_1.transport_speed":0.30447},"optimized_scores":{"best_composite_score":0.13243,"best_fitness_score":0.63243,"best_task_score":0.33931},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":1496.0,"contact_point_centroid":[0.53225,0.15463,-0.00277],"force_p95":0.3488,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.81824,"mean_force":0.15529,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.5408,0.17968,0.28933]},{"body_a":"world","body_b":"grasp_target","contact_count":81.0,"contact_point_centroid":[0.49927,0.04229,-0.00151],"force_p95":0.38416,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.43184,"mean_force":0.08634,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48779,0.04275,0.04771]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1741.0,"contact_point_centroid":[0.50977,0.08587,0.20206],"force_p95":0.16164,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.38144,"mean_force":0.09322,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.50317,0.06738,0.20249]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":7560.0,"contact_point_centroid":[0.49295,0.06172,0.10726],"force_p95":0.10885,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28522,"mean_force":0.06589,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49026,0.0428,0.10569]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6851.0,"contact_point_centroid":[0.49253,0.02385,0.10853],"force_p95":0.11142,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25785,"mean_force":0.06978,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49037,0.04281,0.10749]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50125,0.04491,-0.00218],"force_p95":0.1726,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.23194,"mean_force":0.13594,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49,0.04296,0.04738]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1704.0,"contact_point_centroid":[0.50878,0.04638,0.20045],"force_p95":0.15461,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22933,"mean_force":0.08707,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.50241,0.0649,0.2007]},{"body_a":"world","body_b":"grasp_target","contact_count":436.0,"contact_point_centroid":[0.50118,0.04505,-0.00171],"force_p95":0.13814,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12376,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49884,0.01329,0.30893]},{"body_a":"world","body_b":"grasp_target","contact_count":2436.0,"contact_point_centroid":[0.50118,0.04505,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12264,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49715,0.03635,0.18621]},{"body_a":"world","body_b":"grasp_target","contact_count":1744.0,"contact_point_centroid":[0.53212,0.15461,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"place_descend_1","phase_type":"descend","tcp_position_centroid":[0.5595,0.23771,0.25106]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.53212,0.15461,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.55644,0.24035,0.17003]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4809.0,"contact_point_centroid":[0.4881,0.02356,0.04825],"force_p95":0.07289,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12041,"mean_force":0.04521,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.48887,0.04286,0.04617]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6011.0,"contact_point_centroid":[0.48914,0.06213,0.04879],"force_p95":0.06861,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07153,"mean_force":0.03759,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.48888,0.04286,0.04617]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1434.0,"contact_point_centroid":[0.54339,0.18551,0.2962],"force_p95":0.01146,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01616,"mean_force":0.01054,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.54281,0.18549,0.29391]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1872.0,"contact_point_centroid":[0.56008,0.23774,0.25324],"force_p95":0.01096,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01284,"mean_force":0.01039,"phase_index":5.0,"phase_name":"place_descend_1","phase_type":"descend","tcp_position_centroid":[0.5595,0.23771,0.251]},{"body_a":"left_finger","body_b":"right_finger","contact_count":221.0,"contact_point_centroid":[0.55941,0.24157,0.16789],"force_p95":0.01099,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.011,"mean_force":0.01007,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.55889,0.24154,0.16573]}],"total_contact_groups":16},"final_pose_error":0.00985,"key_states":{"actual_goal_position":[0.56442,0.24486,0.14677],"final_object_position":[0.53212,0.15461,0.01602],"final_tcp_position":[0.56062,0.24227,0.16931],"realised_goal_position":[0.56442,0.24486,0.14677],"realised_object_initial_position":[0.50118,0.04505,0.03]},"peak_contact_force":273006.92964,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":110.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.03],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.23992,"object_z_max":0.03,"peak_contact_force":0.1224,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":436.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.49886,0.02932,0.31759],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.292,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":609.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2436.0,"raw_peak_contact_force":0.12264,"subtask_id":"reach_object","tcp_end":[0.49694,0.04356,0.05509],"tcp_start":[0.49886,0.02932,0.31759],"tcp_to_object_dist_end":0.02941,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":48.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50117,0.04354,0.02534],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.24347,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"peak_contact_force":0.16884,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12620.0,"raw_peak_contact_force":0.23194,"tcp_end":[0.48884,0.04286,0.04614],"tcp_start":[0.49694,0.04356,0.05509],"tcp_to_object_dist_end":0.02418,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":455.0,"n_steps_budget":1000.0,"object_pos_end":[0.5111,0.04381,0.16006],"object_pos_start":[0.50117,0.04354,0.02534],"object_to_goal_dist_end":0.20843,"object_to_goal_dist_start":0.24347,"object_z_max":0.1598,"peak_contact_force":0.10812,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":14492.0,"raw_peak_contact_force":0.43184,"subtask_id":"reach_object","tcp_end":[0.49667,0.04316,0.18641],"tcp_start":[0.48884,0.04286,0.04614],"tcp_to_object_dist_end":0.03004,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":633.0,"n_steps_budget":1000.0,"object_pos_end":[0.53212,0.15461,0.01602],"object_pos_start":[0.5111,0.04381,0.16006],"object_to_goal_dist_end":0.16213,"object_to_goal_dist_start":0.20843,"object_z_max":0.18945,"peak_contact_force":9748.67419,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":6375.0,"raw_peak_contact_force":1.81824,"subtask_id":"reach_goal","tcp_end":[0.55952,0.23397,0.33195],"tcp_start":[0.49667,0.04316,0.18641],"tcp_to_object_dist_end":0.3269,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":436.0,"n_steps_budget":1000.0,"object_pos_end":[0.53212,0.15461,0.01602],"object_pos_start":[0.53212,0.15461,0.01602],"object_to_goal_dist_end":0.16213,"object_to_goal_dist_start":0.16213,"object_z_max":0.01602,"peak_contact_force":273006.92964,"phase_name":"place_descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3616.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_goal","tcp_end":[0.56062,0.24227,0.16931],"tcp_start":[0.55952,0.23397,0.33195],"tcp_to_object_dist_end":0.17886,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53212,0.15461,0.01602],"object_pos_start":[0.53212,0.15461,0.01602],"object_to_goal_dist_end":0.16213,"object_to_goal_dist_start":0.16213,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1021.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.55498,0.23963,0.18995],"tcp_start":[0.56062,0.24227,0.16931],"tcp_to_object_dist_end":0.19494,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.96129,"average_solve_count":155.0,"average_success_count":155.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.25045,"descend_1.grasp_offset":0.0026,"lift_1.lift_height":0.15735,"place_descend_1.place_height":0.01974,"release_1.release_duration":0.48414,"transport_1.transport_height":0.10005,"transport_1.transport_speed":0.18687},"optimized_scores":{"best_composite_score":0.13245,"best_fitness_score":0.63245,"best_task_score":0.31039},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":558.0,"contact_point_centroid":[0.64463,0.17785,-0.00445],"force_p95":0.95352,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.87454,"mean_force":0.21542,"phase_index":5.0,"phase_name":"place_descend_1","phase_type":"descend","tcp_position_centroid":[0.62337,0.15311,0.24308]},{"body_a":"world","body_b":"grasp_target","contact_count":74.0,"contact_point_centroid":[0.47406,-0.01867,-0.00142],"force_p95":0.49926,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.56318,"mean_force":0.12195,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46407,-0.01904,0.03624]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":7436.0,"contact_point_centroid":[0.5418,0.0735,0.21202],"force_p95":0.12991,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33439,"mean_force":0.08371,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.53596,0.05521,0.21093]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6199.0,"contact_point_centroid":[0.53669,0.03126,0.20873],"force_p95":0.15445,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29817,"mean_force":0.09596,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.53124,0.04991,0.20737]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":7109.0,"contact_point_centroid":[0.4677,-0.03803,0.09301],"force_p95":0.10139,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28542,"mean_force":0.06017,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46609,-0.01905,0.09128]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6614.0,"contact_point_centroid":[0.46766,1e-05,0.09412],"force_p95":0.10463,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26288,"mean_force":0.06363,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46615,-0.01905,0.09185]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.47618,-0.02003,-0.0021],"force_p95":0.15037,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.21633,"mean_force":0.13009,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46621,-0.01909,0.03593]},{"body_a":"world","body_b":"grasp_target","contact_count":168.0,"contact_point_centroid":[0.47616,-0.02015,-0.00121],"force_p95":0.13839,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12386,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49481,-0.00347,0.29655]},{"body_a":"world","body_b":"grasp_target","contact_count":2304.0,"contact_point_centroid":[0.47616,-0.02015,-0.00199],"force_p95":0.12264,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13053,"mean_force":0.12275,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.47986,-0.01389,0.16604]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.64471,0.17776,-0.00199],"force_p95":0.12282,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12341,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.62227,0.155,0.21696]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5284.0,"contact_point_centroid":[0.46444,0.00015,0.03613],"force_p95":0.06689,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11865,"mean_force":0.0411,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46511,-0.01906,0.03485]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5269.0,"contact_point_centroid":[0.46478,-0.03836,0.03631],"force_p95":0.06787,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08232,"mean_force":0.04244,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46511,-0.01906,0.03485]},{"body_a":"left_finger","body_b":"right_finger","contact_count":470.0,"contact_point_centroid":[0.62413,0.1537,0.23928],"force_p95":0.01415,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01608,"mean_force":0.0109,"phase_index":5.0,"phase_name":"place_descend_1","phase_type":"descend","tcp_position_centroid":[0.62386,0.15369,0.23706]},{"body_a":"left_finger","body_b":"right_finger","contact_count":220.0,"contact_point_centroid":[0.62485,0.15574,0.21569],"force_p95":0.01097,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01098,"mean_force":0.01008,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.62452,0.15572,0.21346]}],"total_contact_groups":14},"final_pose_error":0.00986,"key_states":{"actual_goal_position":[0.63142,0.15919,0.19002],"final_object_position":[0.64471,0.17776,0.01602],"final_tcp_position":[0.62608,0.15607,0.21743],"realised_goal_position":[0.63142,0.15919,0.19002],"realised_object_initial_position":[0.47616,-0.02015,0.03]},"peak_contact_force":273005.86949,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":43.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02597],"object_pos_start":[0.47616,-0.02015,0.03],"object_to_goal_dist_end":0.28841,"object_to_goal_dist_start":0.28614,"object_z_max":0.03,"peak_contact_force":0.13103,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":168.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.48836,-0.00862,0.29056],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.26512,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":576.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.02597],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28841,"object_z_max":0.02602,"peak_contact_force":81.14225,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2304.0,"raw_peak_contact_force":0.13053,"subtask_id":"reach_object","tcp_end":[0.47303,-0.01921,0.04289],"tcp_start":[0.48836,-0.00862,0.29056],"tcp_to_object_dist_end":0.01718,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":48.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.47607,-0.01926,0.02565],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28809,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.14722,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12353.0,"raw_peak_contact_force":0.21633,"tcp_end":[0.46508,-0.01906,0.03482],"tcp_start":[0.47303,-0.01921,0.04289],"tcp_to_object_dist_end":0.01431,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":401.0,"n_steps_budget":930.0,"object_pos_end":[0.48884,-0.01922,0.15001],"object_pos_start":[0.47607,-0.01926,0.02565],"object_to_goal_dist_end":0.23186,"object_to_goal_dist_start":0.28809,"object_z_max":0.14975,"peak_contact_force":0.10603,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":13797.0,"raw_peak_contact_force":0.56318,"subtask_id":"reach_object","tcp_end":[0.47152,-0.01914,0.1636],"tcp_start":[0.46508,-0.01906,0.03482],"tcp_to_object_dist_end":0.02201,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":708.0,"n_steps_budget":1000.0,"object_pos_end":[0.6379,0.16654,0.09873],"object_pos_start":[0.48884,-0.01922,0.15001],"object_to_goal_dist_end":0.09181,"object_to_goal_dist_start":0.23186,"object_z_max":0.23005,"peak_contact_force":0.0,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":13635.0,"raw_peak_contact_force":0.33439,"subtask_id":"reach_goal","tcp_end":[0.62155,0.14998,0.27562],"tcp_start":[0.47152,-0.01914,0.1636],"tcp_to_object_dist_end":0.17841,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":162.0,"n_steps_budget":1000.0,"object_pos_end":[0.64471,0.17778,0.01599],"object_pos_start":[0.6379,0.16654,0.09873],"object_to_goal_dist_end":0.17552,"object_to_goal_dist_start":0.09181,"object_z_max":0.09873,"peak_contact_force":273005.86949,"phase_name":"place_descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1028.0,"raw_peak_contact_force":1.87454,"subtask_id":"reach_goal","tcp_end":[0.62608,0.15607,0.21743],"tcp_start":[0.62155,0.14998,0.27562],"tcp_to_object_dist_end":0.20346,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.64471,0.17776,0.01602],"object_pos_start":[0.64471,0.17778,0.01599],"object_to_goal_dist_end":0.17549,"object_to_goal_dist_start":0.17552,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1020.0,"raw_peak_contact_force":0.12341,"tcp_end":[0.62098,0.15457,0.23635],"tcp_start":[0.62608,0.15607,0.21743],"tcp_to_object_dist_end":0.22282,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```