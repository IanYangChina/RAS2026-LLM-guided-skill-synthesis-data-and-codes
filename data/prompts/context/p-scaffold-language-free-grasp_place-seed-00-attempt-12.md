## Search State

- **Seed**: 0
- **Iteration**: 13 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 12 | approach → descend → grasp → lift → approach → grasp → descend → release | arc_cartesian | linear_cartesian | — | arc_cartesian | arc_cartesian | — | linear_cartesian | — | position_control | position_control | position_control | impedance_control | impedance_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | time_limit | 7 | 0.1268 | 0.37 | ❌ rejected |
| 11 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 6 | 0.1606 | 0.30 | ❌ rejected |
| 10 | approach → contact → grasp → lift → approach → descend → release | arc_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | force_threshold_switch | position_control | position_control | position_control | position_control | position_control | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 6 | 0.1204 | 0.21 | ❌ rejected |
| 9 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 7 | -0.2217 | 0.17 | ❌ rejected |
| 8 | approach → descend → grasp → lift → approach → descend → release | arc_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | impedance_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 6 | 0.2085 | 0.38 | ❌ rejected |

**Proposal policy**: task_score is 0.37 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.127) — your mutation base

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

- **Composite score**: 0.127
- **task_score** (E): 0.365
- **fitness_score**: 0.657  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.530

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.0678 |
| descend_1 | 1.00 | 1.00 | 0.1956 |
| grasp_1 | 1.00 | 1.00 | 0.0120 |
| lift_1 | 1.00 | 1.00 | 0.1153 |
| transport_1 | 0.00 | 1.00 | 0.0805 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.496, 0.001, 0.240) | (0.497, 0.001, 0.030)→(0.497, 0.001, 0.026) | 0.263→0.265 | 1.00 / 4.000 | 16.889 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.496, 0.001, 0.240)→(0.493, 0.001, 0.045) | (0.497, 0.001, 0.026)→(0.497, 0.001, 0.026) | 0.265→0.265 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_1 | grasp | 1.00 / step_budget | (0.493, 0.001, 0.045)→(0.485, 0.001, 0.036) | (0.497, 0.001, 0.026)→(0.497, 0.001, 0.026) | 0.265→0.266 | 1.00 / 45.333 | 0.153 | 0.222 |
| lift_1 | lift | 1.00 / step_budget | (0.485, 0.001, 0.036)→(0.492, 0.005, 0.151) | (0.497, 0.001, 0.026)→(0.509, 0.005, 0.136) | 0.266→0.210 | 1.00 / 23.667 | 55983.984 | 0.545 |
| transport_1 | approach | 0.00 / guard_failure | (0.492, 0.005, 0.151)→(0.514, 0.050, 0.211) | (0.509, 0.005, 0.136)→(0.531, 0.052, 0.184) | 0.210→0.151 | 1.00 / 4.667 | 0.005 | 0.325 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.368
- phase_score: 0.060
- phase_breakdown.reach_goal_score: 0.050
- phase_breakdown.reach_object_score: 0.099
- grasp_place_fitness: 0.660

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.660
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.380
- **Median Q (composite search score)**: 0.129
- **K-run variance**: 0.0000
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.428


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.93814,"average_solve_count":97.0,"average_success_count":97.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.14148,"descend_1.pre_grasp_offset":0.00169,"lift_1.lift_height":0.13854,"place_descend_1.place_speed":0.19135,"release_1.release_duration":0.33957,"transport_1.transport_height":0.11091,"transport_1.transport_speed":0.37051},"optimized_scores":{"best_composite_score":0.13042,"best_fitness_score":0.66042,"best_task_score":0.36794},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":82.0,"contact_point_centroid":[0.5114,-0.02034,-0.00141],"force_p95":0.46748,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.5797,"mean_force":0.18401,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49938,-0.02083,0.03379]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1461.0,"contact_point_centroid":[0.51522,-0.02529,0.16689],"force_p95":0.19139,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32766,"mean_force":0.10249,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.50928,-0.00676,0.16636]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6067.0,"contact_point_centroid":[0.50451,-0.03171,0.08222],"force_p95":0.1068,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30464,"mean_force":0.06689,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.50196,-0.01286,0.08046]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5559.0,"contact_point_centroid":[0.50481,0.00621,0.08509],"force_p95":0.10965,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29993,"mean_force":0.07074,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.50217,-0.01274,0.08278]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1525.0,"contact_point_centroid":[0.51549,0.01256,0.1681],"force_p95":0.19016,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28373,"mean_force":0.09999,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.50938,-0.00595,0.1679]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.51375,-0.02276,-0.00214],"force_p95":0.1617,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.23577,"mean_force":0.13297,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.50158,-0.02159,0.03356]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4069.0,"contact_point_centroid":[0.50099,-0.00235,0.03505],"force_p95":0.08087,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15058,"mean_force":0.05189,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.50041,-0.02156,0.0323]},{"body_a":"world","body_b":"grasp_target","contact_count":884.0,"contact_point_centroid":[0.5137,-0.02302,-0.00185],"force_p95":0.13709,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12318,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50371,-0.00102,0.24438]},{"body_a":"world","body_b":"grasp_target","contact_count":1364.0,"contact_point_centroid":[0.5137,-0.02302,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50752,-0.0173,0.11437]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5002.0,"contact_point_centroid":[0.50103,-0.04071,0.03414],"force_p95":0.07312,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08427,"mean_force":0.0446,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.50041,-0.02156,0.0323]}],"total_contact_groups":10},"final_pose_error":0.20095,"key_states":{"actual_goal_position":[0.5541,0.15165,0.22199],"final_object_position":[0.53227,0.01098,0.17478],"final_tcp_position":[0.51289,0.00985,0.19661],"realised_goal_position":[0.5541,0.15165,0.22199],"realised_object_initial_position":[0.5137,-0.02302,0.03]},"peak_contact_force":50.4236,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":222.0,"n_steps_budget":1000.0,"object_pos_end":[0.5137,-0.02302,0.02602],"object_pos_start":[0.5137,-0.02302,0.03],"object_to_goal_dist_end":0.26561,"object_to_goal_dist_start":0.26269,"object_z_max":0.03,"peak_contact_force":50.4236,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":884.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.50852,-0.013,0.18755],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.16193,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":341.0,"n_steps_budget":1000.0,"object_pos_end":[0.5137,-0.02302,0.02602],"object_pos_start":[0.5137,-0.02302,0.02602],"object_to_goal_dist_end":0.26561,"object_to_goal_dist_start":0.26561,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1364.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.5088,-0.02171,0.04156],"tcp_start":[0.50852,-0.013,0.18755],"tcp_to_object_dist_end":0.01635,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51361,-0.02165,0.02554],"object_pos_start":[0.5137,-0.02302,0.02602],"object_to_goal_dist_end":0.26508,"object_to_goal_dist_start":0.26561,"object_z_max":0.02602,"peak_contact_force":0.15393,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10871.0,"raw_peak_contact_force":0.23577,"tcp_end":[0.50038,-0.02156,0.03226],"tcp_start":[0.5088,-0.02171,0.04156],"tcp_to_object_dist_end":0.01484,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":379.0,"n_steps_budget":840.0,"object_pos_end":[0.52668,-0.01764,0.13321],"object_pos_start":[0.51361,-0.02165,0.02554],"object_to_goal_dist_end":0.19312,"object_to_goal_dist_start":0.26508,"object_z_max":0.13297,"peak_contact_force":0.1146,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":11708.0,"raw_peak_contact_force":0.5797,"subtask_id":"reach_object","tcp_end":[0.50848,-0.01744,0.14542],"tcp_start":[0.50038,-0.02156,0.03226],"tcp_to_object_dist_end":0.02192,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":152.0,"n_steps_budget":1000.0,"object_pos_end":[0.53227,0.01098,0.17478],"object_pos_start":[0.52668,-0.01764,0.13321],"object_to_goal_dist_end":0.14998,"object_to_goal_dist_start":0.19312,"object_z_max":0.17495,"peak_contact_force":0.0,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2986.0,"raw_peak_contact_force":0.32766,"subtask_id":"reach_goal","tcp_end":[0.51289,0.00985,0.19661],"tcp_start":[0.50848,-0.01744,0.14542],"tcp_to_object_dist_end":0.02921,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.95327,"average_solve_count":107.0,"average_success_count":107.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.22328,"descend_1.pre_grasp_offset":0.01012,"lift_1.lift_height":0.15751,"place_descend_1.place_speed":0.36294,"release_1.release_duration":0.5791,"transport_1.transport_height":0.10541,"transport_1.transport_speed":0.25684},"optimized_scores":{"best_composite_score":0.12856,"best_fitness_score":0.65856,"best_task_score":0.38002},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":84.0,"contact_point_centroid":[0.49955,0.04331,-0.00147],"force_p95":0.38705,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.47623,"mean_force":0.1518,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48775,0.04346,0.04284]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2051.0,"contact_point_centroid":[0.50959,0.09247,0.18428],"force_p95":0.141,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30945,"mean_force":0.09214,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.50356,0.07391,0.18368]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6613.0,"contact_point_centroid":[0.49214,0.07105,0.09507],"force_p95":0.10702,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29522,"mean_force":0.06549,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49011,0.05207,0.09311]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6356.0,"contact_point_centroid":[0.4926,0.03326,0.09728],"force_p95":0.10697,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27123,"mean_force":0.06752,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49028,0.05219,0.09517]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1994.0,"contact_point_centroid":[0.50919,0.05393,0.18342],"force_p95":0.16386,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27098,"mean_force":0.09343,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.5031,0.0724,0.1826]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50125,0.04485,-0.00219],"force_p95":0.17335,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.23811,"mean_force":0.13628,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.48989,0.04293,0.04246]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5031.0,"contact_point_centroid":[0.48856,0.02358,0.04416],"force_p95":0.07128,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15567,"mean_force":0.04301,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.48875,0.04283,0.04125]},{"body_a":"world","body_b":"grasp_target","contact_count":392.0,"contact_point_centroid":[0.50118,0.04505,-0.00168],"force_p95":0.13818,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12392,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49921,0.01526,0.28586]},{"body_a":"world","body_b":"grasp_target","contact_count":2020.0,"contact_point_centroid":[0.50118,0.04505,-0.00199],"force_p95":0.12264,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12264,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49691,0.03737,0.15835]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5517.0,"contact_point_centroid":[0.48847,0.06219,0.0436],"force_p95":0.07248,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07661,"mean_force":0.04118,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.48876,0.04283,0.04126]}],"total_contact_groups":10},"final_pose_error":0.15426,"key_states":{"actual_goal_position":[0.56442,0.24486,0.14677],"final_object_position":[0.52861,0.10777,0.17815],"final_tcp_position":[0.51417,0.10648,0.20614],"realised_goal_position":[0.56442,0.24486,0.14677],"realised_object_initial_position":[0.50118,0.04505,0.03]},"peak_contact_force":167951.73011,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":99.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02601],"object_pos_start":[0.50118,0.04505,0.03],"object_to_goal_dist_end":0.24189,"object_to_goal_dist_start":0.23992,"object_z_max":0.03,"peak_contact_force":0.12222,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":392.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.49889,0.0314,0.2676],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.24198,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":505.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.02601],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.24189,"object_z_max":0.02602,"peak_contact_force":0.12262,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2020.0,"raw_peak_contact_force":0.12264,"subtask_id":"reach_object","tcp_end":[0.49687,0.04353,0.05014],"tcp_start":[0.49889,0.0314,0.2676],"tcp_to_object_dist_end":0.02455,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":47.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50115,0.04344,0.02535],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.24355,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"peak_contact_force":0.16645,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12348.0,"raw_peak_contact_force":0.23811,"tcp_end":[0.48873,0.04282,0.04122],"tcp_start":[0.49687,0.04353,0.05014],"tcp_to_object_dist_end":0.02016,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":25.0,"n_steps":405.0,"n_steps_budget":900.0,"object_pos_end":[0.51218,0.04771,0.14322],"object_pos_start":[0.50115,0.04344,0.02535],"object_to_goal_dist_end":0.20399,"object_to_goal_dist_start":0.24355,"object_z_max":0.14297,"peak_contact_force":167951.73011,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":13053.0,"raw_peak_contact_force":0.47623,"subtask_id":"reach_object","tcp_end":[0.49636,0.04736,0.16386],"tcp_start":[0.48873,0.04282,0.04122],"tcp_to_object_dist_end":0.02601,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":194.0,"n_steps_budget":1000.0,"object_pos_end":[0.52861,0.10777,0.17815],"object_pos_start":[0.51218,0.04771,0.14322],"object_to_goal_dist_end":0.14513,"object_to_goal_dist_start":0.20399,"object_z_max":0.17833,"peak_contact_force":0.01017,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4045.0,"raw_peak_contact_force":0.30945,"subtask_id":"reach_goal","tcp_end":[0.51417,0.10648,0.20614],"tcp_start":[0.49636,0.04736,0.16386],"tcp_to_object_dist_end":0.03151,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.88785,"average_solve_count":107.0,"average_success_count":107.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.21606,"descend_1.pre_grasp_offset":0.0018,"lift_1.lift_height":0.13598,"place_descend_1.place_speed":0.1438,"release_1.release_duration":0.11485,"transport_1.transport_height":0.15114,"transport_1.transport_speed":0.26798},"optimized_scores":{"best_composite_score":0.12138,"best_fitness_score":0.65138,"best_task_score":0.34745},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":74.0,"contact_point_centroid":[0.47401,-0.01841,-0.00137],"force_p95":0.49987,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.57968,"mean_force":0.1891,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46367,-0.01879,0.03527]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3168.0,"contact_point_centroid":[0.49464,0.02468,0.18441],"force_p95":0.14056,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33721,"mean_force":0.08745,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.48879,0.00628,0.18393]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2764.0,"contact_point_centroid":[0.49307,-0.01392,0.18216],"force_p95":0.16649,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31462,"mean_force":0.09736,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.48741,0.00471,0.18114]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6355.0,"contact_point_centroid":[0.46714,-0.02987,0.08382],"force_p95":0.10042,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2875,"mean_force":0.05876,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46582,-0.01085,0.08204]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5906.0,"contact_point_centroid":[0.46732,0.00811,0.08559],"force_p95":0.10069,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27007,"mean_force":0.06169,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46594,-0.01097,0.08328]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.47617,-0.02005,-0.00206],"force_p95":0.14188,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.19332,"mean_force":0.12783,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46573,-0.01944,0.03502]},{"body_a":"world","body_b":"grasp_target","contact_count":348.0,"contact_point_centroid":[0.47616,-0.02015,-0.00164],"force_p95":0.13823,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12415,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.4905,-0.00707,0.28434]},{"body_a":"world","body_b":"grasp_target","contact_count":2088.0,"contact_point_centroid":[0.47616,-0.02015,-0.00199],"force_p95":0.12264,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12264,"mean_force":0.12261,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.47604,-0.01688,0.15248]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5302.0,"contact_point_centroid":[0.46406,-0.00016,0.03565],"force_p95":0.06524,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10081,"mean_force":0.04115,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46463,-0.01941,0.03393]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5416.0,"contact_point_centroid":[0.46407,-0.0387,0.03555],"force_p95":0.06546,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07603,"mean_force":0.04113,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46464,-0.01941,0.03393]}],"total_contact_groups":10},"final_pose_error":0.20471,"key_states":{"actual_goal_position":[0.63142,0.15919,0.19002],"final_object_position":[0.53085,0.03695,0.19927],"final_tcp_position":[0.51396,0.03393,0.22972],"realised_goal_position":[0.63142,0.15919,0.19002],"realised_object_initial_position":[0.47616,-0.02015,0.03]},"peak_contact_force":0.57968,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":88.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02599],"object_pos_start":[0.47616,-0.02015,0.03],"object_to_goal_dist_end":0.2884,"object_to_goal_dist_start":0.28614,"object_z_max":0.03,"peak_contact_force":0.12209,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":348.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.48145,-0.01425,0.26436],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.23851,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":522.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.02599],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.2884,"object_z_max":0.02602,"peak_contact_force":0.12262,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2088.0,"raw_peak_contact_force":0.12264,"subtask_id":"reach_object","tcp_end":[0.47256,-0.01958,0.04196],"tcp_start":[0.48145,-0.01425,0.26436],"tcp_to_object_dist_end":0.01635,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":48.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.47605,-0.01955,0.02576],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28821,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.1398,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12518.0,"raw_peak_contact_force":0.19332,"tcp_end":[0.46461,-0.01941,0.0339],"tcp_start":[0.47256,-0.01958,0.04196],"tcp_to_object_dist_end":0.01405,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":347.0,"n_steps_budget":810.0,"object_pos_end":[0.48839,-0.0154,0.13134],"object_pos_start":[0.47605,-0.01955,0.02576],"object_to_goal_dist_end":0.2332,"object_to_goal_dist_start":0.28821,"object_z_max":0.13108,"peak_contact_force":0.10781,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":12335.0,"raw_peak_contact_force":0.57968,"subtask_id":"reach_object","tcp_end":[0.47121,-0.01522,0.14307],"tcp_start":[0.46461,-0.01941,0.0339],"tcp_to_object_dist_end":0.02081,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":285.0,"n_steps_budget":1000.0,"object_pos_end":[0.53085,0.03695,0.19927],"object_pos_start":[0.48839,-0.0154,0.13134],"object_to_goal_dist_end":0.15857,"object_to_goal_dist_start":0.2332,"object_z_max":0.20219,"peak_contact_force":0.00565,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":5932.0,"raw_peak_contact_force":0.33721,"subtask_id":"reach_goal","tcp_end":[0.51396,0.03393,0.22972],"tcp_start":[0.47121,-0.01522,0.14307],"tcp_to_object_dist_end":0.03495,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```