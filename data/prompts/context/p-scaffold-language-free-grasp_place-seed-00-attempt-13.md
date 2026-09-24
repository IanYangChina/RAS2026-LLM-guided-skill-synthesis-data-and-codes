## Search State

- **Seed**: 0
- **Iteration**: 14 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 13 | approach → descend → grasp → lift → approach → descend → release | arc_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 6 | 0.1749 | 0.30 | ❌ rejected |
| 12 | approach → descend → grasp → lift → approach → grasp → descend → release | arc_cartesian | linear_cartesian | — | arc_cartesian | arc_cartesian | — | linear_cartesian | — | position_control | position_control | position_control | impedance_control | impedance_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | time_limit | 7 | 0.1268 | 0.37 | ❌ rejected |
| 11 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 6 | 0.1606 | 0.30 | ❌ rejected |
| 10 | approach → contact → grasp → lift → approach → descend → release | arc_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | force_threshold_switch | position_control | position_control | position_control | position_control | position_control | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 6 | 0.1204 | 0.21 | ❌ rejected |
| 9 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 7 | -0.2217 | 0.17 | ❌ rejected |

**Proposal policy**: task_score is 0.30 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.175) — your mutation base

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

- **Composite score**: 0.175
- **task_score** (E): 0.301
- **fitness_score**: 0.625  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.450

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.0687 |
| descend_1 | 1.00 | 1.00 | 0.1932 |
| grasp_1 | 1.00 | 1.00 | 0.0120 |
| lift_1 | 1.00 | 1.00 | 0.1082 |
| transport_1 | 0.00 | 1.00 | 0.0447 |
| place_descend_1 | 0.33 | 0.33 | 0.1187 |
| release_1 | 1.00 | 1.00 | 0.0234 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.496, 0.006, 0.237) | (0.497, 0.001, 0.030)→(0.497, 0.001, 0.026) | 0.263→0.265 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.496, 0.006, 0.237)→(0.493, 0.001, 0.044) | (0.497, 0.001, 0.026)→(0.497, 0.001, 0.026) | 0.265→0.265 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_1 | grasp | 1.00 / step_budget | (0.493, 0.001, 0.044)→(0.485, 0.001, 0.036) | (0.497, 0.001, 0.026)→(0.497, 0.001, 0.026) | 0.265→0.265 | 1.00 / 45.333 | 0.152 | 0.226 |
| lift_1 | lift | 1.00 / step_budget | (0.485, 0.001, 0.036)→(0.492, 0.001, 0.143) | (0.497, 0.001, 0.026)→(0.509, 0.001, 0.129) | 0.265→0.213 | 1.00 / 22.667 | 68.723 | 0.524 |
| transport_1 | approach | 0.00 / guard_failure | (0.492, 0.001, 0.143)→(0.501, 0.032, 0.173) | (0.509, 0.001, 0.129)→(0.518, 0.032, 0.155) | 0.213→0.174 | 1.00 / 19.667 | 0.003 | 0.223 |
| place_descend_1 | descend | 0.33 / step_budget | (0.501, 0.032, 0.173)→(0.549, 0.138, 0.175) | (0.518, 0.032, 0.155)→(0.550, 0.114, 0.073) | 0.174→0.143 | 0.33 / 2.667 | 0.041 | 0.741 |
| release_1 | release | 1.00 / step_budget | (0.549, 0.138, 0.175)→(0.544, 0.137, 0.198) | (0.550, 0.114, 0.073)→(0.557, 0.123, 0.016) | 0.143→0.185 | 1.00 / 4.000 | 0.123 | 0.993 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.405
- phase_score: 0.285
- phase_breakdown.reach_goal_score: 0.269
- phase_breakdown.reach_object_score: 0.351
- grasp_place_fitness: 0.675

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.675
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.405
- **Median Q (composite search score)**: 0.157
- **K-run variance**: 0.0013
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.353


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.95312,"average_solve_count":128.0,"average_success_count":128.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.18569,"descend_1.grasp_offset":1e-05,"lift_1.lift_height":0.14923,"release_1.release_duration":0.69339,"transport_1.transport_height":0.1004,"transport_1.transport_speed":0.23051},"optimized_scores":{"best_composite_score":0.14339,"best_fitness_score":0.59339,"best_task_score":0.23196},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":3072.0,"contact_point_centroid":[0.53397,0.07948,-0.00237],"force_p95":0.12566,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.73086,"mean_force":0.13763,"phase_index":5.0,"phase_name":"place_descend_1","phase_type":"descend","tcp_position_centroid":[0.53696,0.10347,0.20938]},{"body_a":"world","body_b":"grasp_target","contact_count":79.0,"contact_point_centroid":[0.51149,-0.02098,-0.0014],"force_p95":0.50632,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.57032,"mean_force":0.11326,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49934,-0.02172,0.03235]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5837.0,"contact_point_centroid":[0.50495,-0.00272,0.08861],"force_p95":0.11067,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30695,"mean_force":0.07277,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.50215,-0.02166,0.08625]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2175.0,"contact_point_centroid":[0.51945,0.02539,0.17828],"force_p95":0.15896,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2957,"mean_force":0.10129,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.51365,0.00689,0.17887]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6448.0,"contact_point_centroid":[0.50485,-0.04048,0.08643],"force_p95":0.1056,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29481,"mean_force":0.0675,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.50203,-0.02166,0.08472]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2155.0,"contact_point_centroid":[0.51934,-0.01258,0.17741],"force_p95":0.17331,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28755,"mean_force":0.10305,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.51346,0.00588,0.17804]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":129.0,"contact_point_centroid":[0.52816,0.05746,0.20122],"force_p95":0.23032,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26471,"mean_force":0.10758,"phase_index":5.0,"phase_name":"place_descend_1","phase_type":"descend","tcp_position_centroid":[0.5217,0.04088,0.20709]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":48.0,"contact_point_centroid":[0.52867,0.02181,0.20103],"force_p95":0.22716,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25088,"mean_force":0.15181,"phase_index":5.0,"phase_name":"place_descend_1","phase_type":"descend","tcp_position_centroid":[0.52163,0.03942,0.20755]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.51373,-0.02276,-0.00212],"force_p95":0.1565,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.22676,"mean_force":0.13166,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.5016,-0.02178,0.03216]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4071.0,"contact_point_centroid":[0.501,-0.00254,0.03366],"force_p95":0.08016,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14412,"mean_force":0.05187,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.50043,-0.02175,0.0309]},{"body_a":"world","body_b":"grasp_target","contact_count":556.0,"contact_point_centroid":[0.5137,-0.02302,-0.00177],"force_p95":0.13792,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.1235,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50359,-0.00322,0.26668]},{"body_a":"world","body_b":"grasp_target","contact_count":1776.0,"contact_point_centroid":[0.5137,-0.02302,-0.00199],"force_p95":0.12264,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12264,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50728,-0.01712,0.13533]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.53394,0.07947,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.54607,0.14603,0.21671]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4983.0,"contact_point_centroid":[0.50105,-0.04089,0.03274],"force_p95":0.07221,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08553,"mean_force":0.04468,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.50043,-0.02175,0.0309]},{"body_a":"left_finger","body_b":"right_finger","contact_count":3042.0,"contact_point_centroid":[0.53828,0.10702,0.21205],"force_p95":0.01106,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01647,"mean_force":0.01051,"phase_index":5.0,"phase_name":"place_descend_1","phase_type":"descend","tcp_position_centroid":[0.53798,0.10701,0.20977]},{"body_a":"left_finger","body_b":"right_finger","contact_count":219.0,"contact_point_centroid":[0.54874,0.14675,0.21422],"force_p95":0.01101,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01102,"mean_force":0.01018,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.54837,0.14675,0.21203]}],"total_contact_groups":16},"final_pose_error":0.00997,"key_states":{"actual_goal_position":[0.5541,0.15165,0.22199],"final_object_position":[0.53394,0.07947,0.01602],"final_tcp_position":[0.54959,0.14691,0.21446],"realised_goal_position":[0.5541,0.15165,0.22199],"realised_object_initial_position":[0.5137,-0.02302,0.03]},"peak_contact_force":205.95318,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":140.0,"n_steps_budget":1000.0,"object_pos_end":[0.5137,-0.02302,0.02602],"object_pos_start":[0.5137,-0.02302,0.03],"object_to_goal_dist_end":0.26561,"object_to_goal_dist_start":0.26269,"object_z_max":0.03,"peak_contact_force":0.12264,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":556.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.50788,-0.01242,0.23151],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.20584,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":444.0,"n_steps_budget":1000.0,"object_pos_end":[0.5137,-0.02302,0.02602],"object_pos_start":[0.5137,-0.02302,0.02602],"object_to_goal_dist_end":0.26561,"object_to_goal_dist_start":0.26561,"object_z_max":0.02602,"peak_contact_force":0.12262,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1776.0,"raw_peak_contact_force":0.12264,"subtask_id":"reach_object","tcp_end":[0.50887,-0.02191,0.04018],"tcp_start":[0.50788,-0.01242,0.23151],"tcp_to_object_dist_end":0.015,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51359,-0.02178,0.02561],"object_pos_start":[0.5137,-0.02302,0.02602],"object_to_goal_dist_end":0.26511,"object_to_goal_dist_start":0.26561,"object_z_max":0.02602,"peak_contact_force":0.14949,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10854.0,"raw_peak_contact_force":0.22676,"tcp_end":[0.5004,-0.02175,0.03087],"tcp_start":[0.50887,-0.02191,0.04018],"tcp_to_object_dist_end":0.0142,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":22.0,"n_steps":410.0,"n_steps_budget":900.0,"object_pos_end":[0.52736,-0.02161,0.14395],"object_pos_start":[0.51359,-0.02178,0.02561],"object_to_goal_dist_end":0.1919,"object_to_goal_dist_start":0.26511,"object_z_max":0.1437,"peak_contact_force":205.95318,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":12364.0,"raw_peak_contact_force":0.57032,"subtask_id":"reach_object","tcp_end":[0.50861,-0.02167,0.15562],"tcp_start":[0.5004,-0.02175,0.03087],"tcp_to_object_dist_end":0.02208,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":213.0,"n_steps_budget":1000.0,"object_pos_end":[0.53681,0.03843,0.18608],"object_pos_start":[0.52736,-0.02161,0.14395],"object_to_goal_dist_end":0.12003,"object_to_goal_dist_start":0.1919,"object_z_max":0.18599,"peak_contact_force":0.01017,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4330.0,"raw_peak_contact_force":0.2957,"subtask_id":"reach_goal","tcp_end":[0.52135,0.03828,0.20747],"tcp_start":[0.50861,-0.02167,0.15562],"tcp_to_object_dist_end":0.02639,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":866.0,"n_steps_budget":1000.0,"object_pos_end":[0.53394,0.07947,0.01602],"object_pos_start":[0.53681,0.03843,0.18608],"object_to_goal_dist_end":0.21918,"object_to_goal_dist_start":0.12003,"object_z_max":0.18608,"peak_contact_force":0.12263,"phase_name":"place_descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":6291.0,"raw_peak_contact_force":1.73086,"subtask_id":"reach_goal","tcp_end":[0.54959,0.14691,0.21446],"tcp_start":[0.52135,0.03828,0.20747],"tcp_to_object_dist_end":0.21017,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53394,0.07947,0.01602],"object_pos_start":[0.53394,0.07947,0.01602],"object_to_goal_dist_end":0.21918,"object_to_goal_dist_start":0.21918,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1019.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.54476,0.14562,0.23697],"tcp_start":[0.54959,0.14691,0.21446],"tcp_to_object_dist_end":0.2309,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.91667,"average_solve_count":120.0,"average_success_count":120.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.179,"descend_1.grasp_offset":0.00658,"lift_1.lift_height":0.12567,"release_1.release_duration":0.55624,"transport_1.transport_height":0.18862,"transport_1.transport_speed":0.42771},"optimized_scores":{"best_composite_score":0.22466,"best_fitness_score":0.67466,"best_task_score":0.40489},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":607.0,"contact_point_centroid":[0.56041,0.20885,-0.00328],"force_p95":0.68863,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.33166,"mean_force":0.19043,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.53444,0.18282,0.14424]},{"body_a":"world","body_b":"grasp_target","contact_count":80.0,"contact_point_centroid":[0.49943,0.04288,-0.00144],"force_p95":0.42486,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.49191,"mean_force":0.10025,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48764,0.04319,0.03952]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5472.0,"contact_point_centroid":[0.49168,0.06212,0.08101],"force_p95":0.10426,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29626,"mean_force":0.06134,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49007,0.04313,0.07909]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4968.0,"contact_point_centroid":[0.4922,0.02411,0.08276],"force_p95":0.10443,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2664,"mean_force":0.06577,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49023,0.04313,0.08048]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8979.0,"contact_point_centroid":[0.52356,0.10496,0.14261],"force_p95":0.1491,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2595,"mean_force":0.09823,"phase_index":5.0,"phase_name":"place_descend_1","phase_type":"descend","tcp_position_centroid":[0.51822,0.12349,0.14203]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50123,0.04485,-0.00215],"force_p95":0.16379,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.23207,"mean_force":0.13369,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.48978,0.04341,0.0392]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":10773.0,"contact_point_centroid":[0.524,0.14159,0.14215],"force_p95":0.12984,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18438,"mean_force":0.08369,"phase_index":5.0,"phase_name":"place_descend_1","phase_type":"descend","tcp_position_centroid":[0.51816,0.12334,0.14203]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":767.0,"contact_point_centroid":[0.50322,0.03413,0.14126],"force_p95":0.11883,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16426,"mean_force":0.08477,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.49789,0.05261,0.13988]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":705.0,"contact_point_centroid":[0.50304,0.07127,0.14185],"force_p95":0.11704,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16125,"mean_force":0.08966,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.49788,0.05258,0.13986]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5033.0,"contact_point_centroid":[0.48849,0.02406,0.041],"force_p95":0.07019,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15634,"mean_force":0.04299,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.48864,0.04331,0.03799]},{"body_a":"world","body_b":"grasp_target","contact_count":652.0,"contact_point_centroid":[0.50118,0.04505,-0.0018],"force_p95":0.13762,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12338,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49912,0.02112,0.26689]},{"body_a":"world","body_b":"grasp_target","contact_count":1684.0,"contact_point_centroid":[0.50118,0.04505,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12264,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.4967,0.04133,0.13687]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5524.0,"contact_point_centroid":[0.4883,0.06263,0.04042],"force_p95":0.07045,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08139,"mean_force":0.04094,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.48865,0.04331,0.038]}],"total_contact_groups":13},"final_pose_error":0.06562,"key_states":{"actual_goal_position":[0.56442,0.24486,0.14677],"final_object_position":[0.56077,0.2091,0.01601],"final_tcp_position":[0.53959,0.18446,0.14034],"realised_goal_position":[0.56442,0.24486,0.14677],"realised_object_initial_position":[0.50118,0.04505,0.03]},"peak_contact_force":1.33166,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":164.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.03],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.23992,"object_z_max":0.03,"peak_contact_force":0.12264,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":652.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.49872,0.03882,0.22769],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.20178,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":421.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"peak_contact_force":0.12262,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1684.0,"raw_peak_contact_force":0.12264,"subtask_id":"reach_object","tcp_end":[0.49681,0.04404,0.04689],"tcp_start":[0.49872,0.03882,0.22769],"tcp_to_object_dist_end":0.02135,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":47.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50113,0.04371,0.02548],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.24327,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"peak_contact_force":0.1578,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12357.0,"raw_peak_contact_force":0.23207,"tcp_end":[0.48862,0.0433,0.03796],"tcp_start":[0.49681,0.04404,0.04689],"tcp_to_object_dist_end":0.01767,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":309.0,"n_steps_budget":720.0,"object_pos_end":[0.51222,0.04372,0.116],"object_pos_start":[0.50113,0.04371,0.02548],"object_to_goal_dist_end":0.21008,"object_to_goal_dist_start":0.24327,"object_z_max":0.11574,"peak_contact_force":0.10685,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":10520.0,"raw_peak_contact_force":0.49191,"subtask_id":"reach_object","tcp_end":[0.49577,0.0433,0.13207],"tcp_start":[0.48862,0.0433,0.03796],"tcp_to_object_dist_end":0.023,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":25.0,"n_steps":64.0,"n_steps_budget":1000.0,"object_pos_end":[0.51727,0.06325,0.13081],"object_pos_start":[0.51222,0.04372,0.116],"object_to_goal_dist_end":0.18832,"object_to_goal_dist_start":0.21008,"object_z_max":0.13062,"peak_contact_force":0.0,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1472.0,"raw_peak_contact_force":0.16426,"subtask_id":"reach_goal","tcp_end":[0.50036,0.06291,0.14839],"tcp_start":[0.49577,0.0433,0.13207],"tcp_to_object_dist_end":0.02439,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.54733,0.18987,0.09748],"object_pos_start":[0.51727,0.06325,0.13081],"object_to_goal_dist_end":0.07581,"object_to_goal_dist_start":0.18832,"object_z_max":0.13092,"peak_contact_force":0.0,"phase_name":"place_descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":19752.0,"raw_peak_contact_force":0.2595,"subtask_id":"reach_goal","tcp_end":[0.53959,0.18446,0.14034],"tcp_start":[0.50036,0.06291,0.14839],"tcp_to_object_dist_end":0.04389,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.56077,0.2091,0.01601],"object_pos_start":[0.54733,0.18987,0.09748],"object_to_goal_dist_end":0.13562,"object_to_goal_dist_start":0.07581,"object_z_max":0.09748,"peak_contact_force":0.12313,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":607.0,"raw_peak_contact_force":1.33166,"tcp_end":[0.53369,0.18255,0.1631],"tcp_start":[0.53959,0.18446,0.14034],"tcp_to_object_dist_end":0.15191,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.91803,"average_solve_count":122.0,"average_success_count":122.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.20669,"descend_1.grasp_offset":0.00542,"lift_1.lift_height":0.13637,"release_1.release_duration":0.90118,"transport_1.transport_height":0.24878,"transport_1.transport_speed":0.49819},"optimized_scores":{"best_composite_score":0.15663,"best_fitness_score":0.60663,"best_task_score":0.26579},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":636.0,"contact_point_centroid":[0.57688,0.07986,-0.00341],"force_p95":0.69716,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.52441,"mean_force":0.19271,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.55348,0.08196,0.17444]},{"body_a":"world","body_b":"grasp_target","contact_count":74.0,"contact_point_centroid":[0.47414,-0.0187,-0.00142],"force_p95":0.46077,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.50978,"mean_force":0.11271,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46378,-0.01898,0.03925]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6174.0,"contact_point_centroid":[0.46729,-0.03804,0.08685],"force_p95":0.09694,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26853,"mean_force":0.05787,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46599,-0.01903,0.08514]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5632.0,"contact_point_centroid":[0.46722,9e-05,0.08747],"force_p95":0.10298,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26095,"mean_force":0.06196,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46601,-0.01903,0.08506]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":9303.0,"contact_point_centroid":[0.5227,0.05557,0.16535],"force_p95":0.15105,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23274,"mean_force":0.09446,"phase_index":5.0,"phase_name":"place_descend_1","phase_type":"descend","tcp_position_centroid":[0.5169,0.03711,0.1649]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.47619,-0.02004,-0.0021],"force_p95":0.15202,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.21956,"mean_force":0.13057,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46588,-0.01903,0.03894]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":732.0,"contact_point_centroid":[0.48194,-0.03049,0.15429],"force_p95":0.14047,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20954,"mean_force":0.08947,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.47664,-0.012,0.15298]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":670.0,"contact_point_centroid":[0.48171,0.00668,0.15508],"force_p95":0.12944,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1752,"mean_force":0.09297,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.47663,-0.01201,0.15297]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":10167.0,"contact_point_centroid":[0.5254,0.02186,0.16543],"force_p95":0.1239,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1726,"mean_force":0.0861,"phase_index":5.0,"phase_name":"place_descend_1","phase_type":"descend","tcp_position_centroid":[0.51963,0.04013,0.16526]},{"body_a":"world","body_b":"grasp_target","contact_count":408.0,"contact_point_centroid":[0.47616,-0.02015,-0.00169],"force_p95":0.13814,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12386,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49128,-0.00284,0.2776]},{"body_a":"world","body_b":"grasp_target","contact_count":1944.0,"contact_point_centroid":[0.47616,-0.02015,-0.00199],"force_p95":0.12264,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12264,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.47626,-0.01442,0.14882]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5293.0,"contact_point_centroid":[0.46418,0.00025,0.03945],"force_p95":0.06665,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11357,"mean_force":0.04118,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46478,-0.019,0.03785]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5456.0,"contact_point_centroid":[0.4642,-0.0383,0.03933],"force_p95":0.06675,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07251,"mean_force":0.04102,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46479,-0.019,0.03785]}],"total_contact_groups":13},"final_pose_error":0.10753,"key_states":{"actual_goal_position":[0.63142,0.15919,0.19002],"final_object_position":[0.57701,0.08003,0.01601],"final_tcp_position":[0.55833,0.08267,0.17088],"realised_goal_position":[0.63142,0.15919,0.19002],"realised_object_initial_position":[0.47616,-0.02015,0.03]},"peak_contact_force":1.52441,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":103.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.03],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28614,"object_z_max":0.03,"peak_contact_force":0.12229,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":408.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.4818,-0.00977,0.2526],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.22689,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":486.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.12262,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1944.0,"raw_peak_contact_force":0.12264,"subtask_id":"reach_object","tcp_end":[0.47266,-0.01915,0.04588],"tcp_start":[0.4818,-0.00977,0.2526],"tcp_to_object_dist_end":0.02019,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":48.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.47608,-0.01928,0.02562],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28811,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.14847,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12549.0,"raw_peak_contact_force":0.21956,"tcp_end":[0.46476,-0.019,0.03782],"tcp_start":[0.47266,-0.01915,0.04588],"tcp_to_object_dist_end":0.01665,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":329.0,"n_steps_budget":780.0,"object_pos_end":[0.48753,-0.01912,0.1272],"object_pos_start":[0.47608,-0.01928,0.02562],"object_to_goal_dist_end":0.23758,"object_to_goal_dist_start":0.28811,"object_z_max":0.12693,"peak_contact_force":0.10843,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":11880.0,"raw_peak_contact_force":0.50978,"subtask_id":"reach_object","tcp_end":[0.47114,-0.01914,0.14267],"tcp_start":[0.46476,-0.019,0.03782],"tcp_to_object_dist_end":0.02253,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":25.0,"n_steps":61.0,"n_steps_budget":1000.0,"object_pos_end":[0.49968,-0.00443,0.14666],"object_pos_start":[0.48753,-0.01912,0.1272],"object_to_goal_dist_end":0.21449,"object_to_goal_dist_start":0.23758,"object_z_max":0.14627,"peak_contact_force":0.0,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1402.0,"raw_peak_contact_force":0.20954,"subtask_id":"reach_goal","tcp_end":[0.48238,-0.00444,0.16366],"tcp_start":[0.47114,-0.01914,0.14267],"tcp_to_object_dist_end":0.02426,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.56942,0.07412,0.10653],"object_pos_start":[0.49968,-0.00443,0.14666],"object_to_goal_dist_end":0.13435,"object_to_goal_dist_start":0.21449,"object_z_max":0.14716,"peak_contact_force":0.0,"phase_name":"place_descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":19470.0,"raw_peak_contact_force":0.23274,"subtask_id":"reach_goal","tcp_end":[0.55833,0.08267,0.17088],"tcp_start":[0.48238,-0.00444,0.16366],"tcp_to_object_dist_end":0.06586,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.57701,0.08003,0.01601],"object_pos_start":[0.56942,0.07412,0.10653],"object_to_goal_dist_end":0.19876,"object_to_goal_dist_start":0.13435,"object_z_max":0.10653,"peak_contact_force":0.12295,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":636.0,"raw_peak_contact_force":1.52441,"tcp_end":[0.55265,0.08182,0.19366],"tcp_start":[0.55833,0.08267,0.17088],"tcp_to_object_dist_end":0.17932,"terminated_normally":true,"termination_reason":"step_budget"}],"success":false}]}
```