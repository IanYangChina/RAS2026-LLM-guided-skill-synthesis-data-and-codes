## Search State

- **Seed**: 0
- **Iteration**: 12 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 11 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 6 | 0.1606 | 0.30 | ❌ rejected |
| 10 | approach → contact → grasp → lift → approach → descend → release | arc_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | force_threshold_switch | position_control | position_control | position_control | position_control | position_control | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 6 | 0.1204 | 0.21 | ❌ rejected |
| 9 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 7 | -0.2217 | 0.17 | ❌ rejected |
| 8 | approach → descend → grasp → lift → approach → descend → release | arc_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | impedance_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 6 | 0.2085 | 0.38 | ❌ rejected |
| 7 | approach → descend → grasp → lift → approach → descend → release | arc_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 6 | 0.1637 | 0.28 | ❌ rejected |

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

## Current Skill (Q=0.161) — your mutation base

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

- **Composite score**: 0.161
- **task_score** (E): 0.298
- **fitness_score**: 0.611  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.450

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.0616 |
| pre_grasp_descend | 1.00 | 1.00 | 0.1911 |
| grasp_1 | 1.00 | 1.00 | 0.0117 |
| lift_1 | 1.00 | 1.00 | 0.1310 |
| transport_1 | 1.00 | 0.67 | 0.2572 |
| place_descend_1 | 1.00 | 1.00 | 0.1284 |
| release_1 | 1.00 | 1.00 | 0.0213 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.498, -0.001, 0.247) | (0.497, 0.001, 0.030)→(0.497, 0.001, 0.026) | 0.263→0.265 | 1.00 / 4.000 | 0.123 | 0.138 |
| pre_grasp_descend | descend | 1.00 / step_budget | (0.498, -0.001, 0.247)→(0.493, 0.001, 0.056) | (0.497, 0.001, 0.026)→(0.497, 0.001, 0.026) | 0.265→0.265 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_1 | grasp | 1.00 / step_budget | (0.493, 0.001, 0.056)→(0.485, 0.000, 0.047) | (0.497, 0.001, 0.026)→(0.497, 0.000, 0.026) | 0.265→0.266 | 1.00 / 44.000 | 0.150 | 0.202 |
| lift_1 | lift | 1.00 / step_budget | (0.485, 0.000, 0.047)→(0.481, 0.000, 0.178) | (0.497, 0.000, 0.026)→(0.495, 0.000, 0.152) | 0.266→0.217 | 1.00 / 24.333 | 55983.980 | 0.413 |
| transport_1 | approach | 1.00 / step_budget | (0.481, 0.000, 0.178)→(0.577, 0.175, 0.323) | (0.495, 0.000, 0.152)→(0.550, 0.135, 0.054) | 0.217→0.147 | 0.67 / 5.667 | 94253.829 | 1.424 |
| place_descend_1 | descend | 1.00 / step_budget | (0.577, 0.175, 0.323)→(0.579, 0.183, 0.195) | (0.550, 0.135, 0.054)→(0.554, 0.146, 0.016) | 0.147→0.186 | 1.00 / 8.000 | 0.123 | 0.687 |
| release_1 | release | 1.00 / step_budget | (0.579, 0.183, 0.195)→(0.574, 0.181, 0.215) | (0.554, 0.146, 0.016)→(0.554, 0.146, 0.016) | 0.186→0.186 | 1.00 / 4.000 | 0.123 | 0.123 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.407
- phase_score: 0.678
- phase_breakdown.reach_goal_score: 0.821
- phase_breakdown.reach_object_score: 0.106
- grasp_place_fitness: 0.665

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.665
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.407
- **Median Q (composite search score)**: 0.140
- **K-run variance**: 0.0015
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.0942,"average_solve_count":138.0,"average_success_count":138.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.13081,"lift_1.lift_height":0.13795,"pre_grasp_descend.grasp_z_offset":0.02225,"release_1.release_duration":0.3955,"transport_1.transport_height":0.16452,"transport_1.transport_speed":0.40611},"optimized_scores":{"best_composite_score":0.12648,"best_fitness_score":0.57648,"best_task_score":0.2313},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":1483.0,"contact_point_centroid":[0.53331,0.07839,-0.0028],"force_p95":0.37113,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.67457,"mean_force":0.15458,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.53495,0.09832,0.31294]},{"body_a":"world","body_b":"grasp_target","contact_count":77.0,"contact_point_centroid":[0.51146,-0.02203,-0.00137],"force_p95":0.37115,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.39147,"mean_force":0.08317,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49938,-0.02225,0.04916]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5716.0,"contact_point_centroid":[0.49953,-0.00322,0.10006],"force_p95":0.11019,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28948,"mean_force":0.07152,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49701,-0.02218,0.09934]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6257.0,"contact_point_centroid":[0.4994,-0.04107,0.0999],"force_p95":0.10595,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27716,"mean_force":0.06646,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49701,-0.02218,0.09909]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2115.0,"contact_point_centroid":[0.50867,-0.01799,0.19141],"force_p95":0.15408,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27704,"mean_force":0.08879,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.50248,0.00057,0.19143]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2224.0,"contact_point_centroid":[0.50936,0.02103,0.19338],"force_p95":0.14548,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24443,"mean_force":0.08683,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.50307,0.00251,0.19373]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.51371,-0.02296,-0.00206],"force_p95":0.14154,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.18358,"mean_force":0.12763,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.50181,-0.02231,0.04908]},{"body_a":"world","body_b":"grasp_target","contact_count":936.0,"contact_point_centroid":[0.5137,-0.02302,-0.00186],"force_p95":0.13709,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12315,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50356,-0.00904,0.24106]},{"body_a":"world","body_b":"grasp_target","contact_count":1512.0,"contact_point_centroid":[0.5137,-0.02302,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"pre_grasp_descend","phase_type":"descend","tcp_position_centroid":[0.50726,-0.02067,0.11719]},{"body_a":"world","body_b":"grasp_target","contact_count":1520.0,"contact_point_centroid":[0.53328,0.07839,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"place_descend_1","phase_type":"descend","tcp_position_centroid":[0.55013,0.14617,0.30062]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.53328,0.07839,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.5473,0.14884,0.23258]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4351.0,"contact_point_centroid":[0.50122,-0.0031,0.04907],"force_p95":0.0737,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11658,"mean_force":0.04946,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.50066,-0.02228,0.0478]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4910.0,"contact_point_centroid":[0.50117,-0.04143,0.04892],"force_p95":0.06993,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08191,"mean_force":0.04454,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.50066,-0.02228,0.0478]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1399.0,"contact_point_centroid":[0.53717,0.10381,0.32211],"force_p95":0.01205,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01596,"mean_force":0.0106,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.53683,0.10381,0.31985]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1640.0,"contact_point_centroid":[0.5505,0.14618,0.30287],"force_p95":0.01095,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01274,"mean_force":0.01034,"phase_index":5.0,"phase_name":"place_descend_1","phase_type":"descend","tcp_position_centroid":[0.55013,0.14617,0.30059]},{"body_a":"left_finger","body_b":"right_finger","contact_count":224.0,"contact_point_centroid":[0.54995,0.14951,0.23003],"force_p95":0.01094,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01097,"mean_force":0.00995,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.54937,0.14949,0.22776]}],"total_contact_groups":16},"final_pose_error":0.00969,"key_states":{"actual_goal_position":[0.5541,0.15165,0.22199],"final_object_position":[0.53328,0.07839,0.01602],"final_tcp_position":[0.55086,0.14987,0.23095],"realised_goal_position":[0.5541,0.15165,0.22199],"realised_object_initial_position":[0.5137,-0.02302,0.03]},"peak_contact_force":167951.73011,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":235.0,"n_steps_budget":1000.0,"object_pos_end":[0.5137,-0.02302,0.02602],"object_pos_start":[0.5137,-0.02302,0.03],"object_to_goal_dist_end":0.26561,"object_to_goal_dist_start":0.26269,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":936.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.50845,-0.01895,0.17925],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.15337,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":378.0,"n_steps_budget":1000.0,"object_pos_end":[0.5137,-0.02302,0.02602],"object_pos_start":[0.5137,-0.02302,0.02602],"object_to_goal_dist_end":0.26561,"object_to_goal_dist_start":0.26561,"object_z_max":0.02602,"peak_contact_force":0.12262,"phase_name":"pre_grasp_descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1512.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.5087,-0.02247,0.05687],"tcp_start":[0.50845,-0.01895,0.17925],"tcp_to_object_dist_end":0.03126,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":42.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51363,-0.02248,0.02575],"object_pos_start":[0.5137,-0.02302,0.02602],"object_to_goal_dist_end":0.26546,"object_to_goal_dist_start":0.26561,"object_z_max":0.02602,"peak_contact_force":0.14007,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11061.0,"raw_peak_contact_force":0.18358,"tcp_end":[0.50063,-0.02228,0.04777],"tcp_start":[0.5087,-0.02247,0.05687],"tcp_to_object_dist_end":0.02556,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":26.0,"n_steps":380.0,"n_steps_budget":870.0,"object_pos_end":[0.51085,-0.02243,0.13958],"object_pos_start":[0.51363,-0.02248,0.02575],"object_to_goal_dist_end":0.1974,"object_to_goal_dist_start":0.26546,"object_z_max":0.13931,"peak_contact_force":167951.73011,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":12050.0,"raw_peak_contact_force":0.39147,"subtask_id":"reach_object","tcp_end":[0.49703,-0.02217,0.16632],"tcp_start":[0.50063,-0.02228,0.04777],"tcp_to_object_dist_end":0.0301,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":663.0,"n_steps_budget":1000.0,"object_pos_end":[0.53328,0.07839,0.01602],"object_pos_start":[0.51085,-0.02243,0.13958],"object_to_goal_dist_end":0.2196,"object_to_goal_dist_start":0.1974,"object_z_max":0.19325,"peak_contact_force":9748.87828,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":7221.0,"raw_peak_contact_force":1.67457,"subtask_id":"reach_goal","tcp_end":[0.55022,0.14295,0.36895],"tcp_start":[0.49703,-0.02217,0.16632],"tcp_to_object_dist_end":0.35919,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":380.0,"n_steps_budget":1000.0,"object_pos_end":[0.53328,0.07839,0.01602],"object_pos_start":[0.53328,0.07839,0.01602],"object_to_goal_dist_end":0.2196,"object_to_goal_dist_start":0.2196,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"place_descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3160.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_goal","tcp_end":[0.55086,0.14987,0.23095],"tcp_start":[0.55022,0.14295,0.36895],"tcp_to_object_dist_end":0.22719,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53328,0.07839,0.01602],"object_pos_start":[0.53328,0.07839,0.01602],"object_to_goal_dist_end":0.2196,"object_to_goal_dist_start":0.2196,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1024.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.54611,0.14845,0.25287],"tcp_start":[0.55086,0.14987,0.23095],"tcp_to_object_dist_end":0.24733,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.8951,"average_solve_count":143.0,"average_success_count":143.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.25172,"lift_1.lift_height":0.16373,"pre_grasp_descend.grasp_z_offset":0.02123,"release_1.release_duration":0.13543,"transport_1.transport_height":0.10243,"transport_1.transport_speed":0.28415},"optimized_scores":{"best_composite_score":0.21505,"best_fitness_score":0.66505,"best_task_score":0.40692},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":797.0,"contact_point_centroid":[0.57302,0.27655,-0.00341],"force_p95":0.70294,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.81444,"mean_force":0.19069,"phase_index":5.0,"phase_name":"place_descend_1","phase_type":"descend","tcp_position_centroid":[0.55745,0.23589,0.18923]},{"body_a":"world","body_b":"grasp_target","contact_count":80.0,"contact_point_centroid":[0.49892,0.04254,-0.00149],"force_p95":0.39131,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.42737,"mean_force":0.09103,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48747,0.04272,0.04864]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4247.0,"contact_point_centroid":[0.51852,0.10092,0.2063],"force_p95":0.14861,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31692,"mean_force":0.09985,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.5134,0.11932,0.20833]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":7447.0,"contact_point_centroid":[0.48764,0.06144,0.11046],"force_p95":0.10931,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.301,"mean_force":0.0673,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48523,0.04252,0.10938]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6839.0,"contact_point_centroid":[0.48743,0.02357,0.11104],"force_p95":0.11121,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27607,"mean_force":0.07077,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48522,0.04252,0.11033]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50125,0.04491,-0.00218],"force_p95":0.17283,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.23021,"mean_force":0.1357,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.4899,0.04295,0.04832]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4535.0,"contact_point_centroid":[0.519,0.13833,0.20659],"force_p95":0.14097,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20501,"mean_force":0.09421,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.51367,0.12015,0.20848]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4209.0,"contact_point_centroid":[0.48901,0.02359,0.04853],"force_p95":0.07922,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14366,"mean_force":0.05106,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.48877,0.04285,0.04709]},{"body_a":"world","body_b":"grasp_target","contact_count":296.0,"contact_point_centroid":[0.50118,0.04505,-0.00158],"force_p95":0.13832,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.1245,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49915,0.01152,0.29324]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.57274,0.27687,-0.00199],"force_p95":0.12264,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12265,"mean_force":0.12262,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.55518,0.2389,0.15519]},{"body_a":"world","body_b":"grasp_target","contact_count":2820.0,"contact_point_centroid":[0.50118,0.04505,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12264,"mean_force":0.1226,"phase_index":1.0,"phase_name":"pre_grasp_descend","phase_type":"descend","tcp_position_centroid":[0.4967,0.03463,0.16914]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5565.0,"contact_point_centroid":[0.48835,0.06203,0.04895],"force_p95":0.07101,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07446,"mean_force":0.04012,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.48878,0.04285,0.0471]},{"body_a":"left_finger","body_b":"right_finger","contact_count":637.0,"contact_point_centroid":[0.55819,0.23699,0.18297],"force_p95":0.0128,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01564,"mean_force":0.01089,"phase_index":5.0,"phase_name":"place_descend_1","phase_type":"descend","tcp_position_centroid":[0.55786,0.23696,0.18077]},{"body_a":"left_finger","body_b":"right_finger","contact_count":222.0,"contact_point_centroid":[0.55814,0.24017,0.15339],"force_p95":0.01102,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01103,"mean_force":0.01008,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.55775,0.24013,0.15086]}],"total_contact_groups":14},"final_pose_error":0.00989,"key_states":{"actual_goal_position":[0.56442,0.24486,0.14677],"final_object_position":[0.57274,0.27687,0.01602],"final_tcp_position":[0.55956,0.24082,0.15438],"realised_goal_position":[0.56442,0.24486,0.14677],"realised_object_initial_position":[0.50118,0.04505,0.03]},"peak_contact_force":1.81444,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":75.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02593],"object_pos_start":[0.50118,0.04505,0.03],"object_to_goal_dist_end":0.24193,"object_to_goal_dist_start":0.23992,"object_z_max":0.03,"peak_contact_force":0.12241,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":296.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.4988,0.02583,0.28531],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.2601,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":705.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.02593],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.24193,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"pre_grasp_descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2820.0,"raw_peak_contact_force":0.12264,"subtask_id":"reach_object","tcp_end":[0.49668,0.04353,0.05576],"tcp_start":[0.4988,0.02583,0.28531],"tcp_to_object_dist_end":0.03012,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50118,0.04356,0.02536],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.24344,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"peak_contact_force":0.16815,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11574.0,"raw_peak_contact_force":0.23021,"tcp_end":[0.48875,0.04285,0.04706],"tcp_start":[0.49668,0.04353,0.05576],"tcp_to_object_dist_end":0.02502,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":24.0,"n_steps":454.0,"n_steps_budget":1000.0,"object_pos_end":[0.49896,0.04329,0.1638],"object_pos_start":[0.50118,0.04356,0.02536],"object_to_goal_dist_end":0.21262,"object_to_goal_dist_start":0.24344,"object_z_max":0.16352,"peak_contact_force":0.10435,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":14366.0,"raw_peak_contact_force":0.42737,"subtask_id":"reach_object","tcp_end":[0.48541,0.04254,0.19109],"tcp_start":[0.48875,0.04285,0.04706],"tcp_to_object_dist_end":0.03048,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":512.0,"n_steps_budget":1000.0,"object_pos_end":[0.5622,0.24555,0.12991],"object_pos_start":[0.49896,0.04329,0.1638],"object_to_goal_dist_end":0.01702,"object_to_goal_dist_start":0.21262,"object_z_max":0.19301,"peak_contact_force":0.0,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":8782.0,"raw_peak_contact_force":0.31692,"subtask_id":"reach_goal","tcp_end":[0.55664,0.23039,0.23795],"tcp_start":[0.48541,0.04254,0.19109],"tcp_to_object_dist_end":0.10924,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":239.0,"n_steps_budget":1000.0,"object_pos_end":[0.57273,0.27686,0.01602],"object_pos_start":[0.5622,0.24555,0.12991],"object_to_goal_dist_end":0.13487,"object_to_goal_dist_start":0.01702,"object_z_max":0.12991,"peak_contact_force":0.12264,"phase_name":"place_descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1434.0,"raw_peak_contact_force":1.81444,"subtask_id":"reach_goal","tcp_end":[0.55956,0.24082,0.15438],"tcp_start":[0.55664,0.23039,0.23795],"tcp_to_object_dist_end":0.14358,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.57274,0.27687,0.01602],"object_pos_start":[0.57273,0.27686,0.01602],"object_to_goal_dist_end":0.13487,"object_to_goal_dist_start":0.13487,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1022.0,"raw_peak_contact_force":0.12265,"tcp_end":[0.55364,0.23815,0.17513],"tcp_start":[0.55956,0.24082,0.15438],"tcp_to_object_dist_end":0.16487,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.01163,"average_solve_count":172.0,"average_success_count":172.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.23032,"lift_1.lift_height":0.15002,"pre_grasp_descend.grasp_z_offset":0.02004,"release_1.release_duration":0.91022,"transport_1.transport_height":0.18793,"transport_1.transport_speed":0.18085},"optimized_scores":{"best_composite_score":0.14036,"best_fitness_score":0.59036,"best_task_score":0.25518},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":1810.0,"contact_point_centroid":[0.55596,0.08173,-0.00268],"force_p95":0.26666,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.27902,"mean_force":0.15,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.58183,0.10849,0.31426]},{"body_a":"world","body_b":"grasp_target","contact_count":73.0,"contact_point_centroid":[0.47379,-0.01915,-0.00139],"force_p95":0.40136,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.42166,"mean_force":0.10091,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46369,-0.0193,0.04849]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":7166.0,"contact_point_centroid":[0.46301,-0.03821,0.10559],"force_p95":0.10266,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26366,"mean_force":0.06143,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46146,-0.01922,0.10449]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6514.0,"contact_point_centroid":[0.46314,-0.00018,0.10584],"force_p95":0.10749,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26288,"mean_force":0.06639,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46145,-0.01922,0.10484]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3734.0,"contact_point_centroid":[0.49678,0.032,0.20982],"force_p95":0.12478,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24115,"mean_force":0.08053,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.49059,0.01353,0.21022]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3422.0,"contact_point_centroid":[0.4939,-0.00812,0.20686],"force_p95":0.15422,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22472,"mean_force":0.08687,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.48772,0.01049,0.20696]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.47618,-0.02009,-0.00207],"force_p95":0.14335,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.19206,"mean_force":0.12812,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46596,-0.01935,0.04828]},{"body_a":"world","body_b":"grasp_target","contact_count":264.0,"contact_point_centroid":[0.47616,-0.02015,-0.00152],"force_p95":0.13832,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12472,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49342,-0.00471,0.289]},{"body_a":"world","body_b":"grasp_target","contact_count":2704.0,"contact_point_centroid":[0.47616,-0.02015,-0.00199],"force_p95":0.12264,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12308,"mean_force":0.1226,"phase_index":1.0,"phase_name":"pre_grasp_descend","phase_type":"descend","tcp_position_centroid":[0.478,-0.01516,0.16358]},{"body_a":"world","body_b":"grasp_target","contact_count":1648.0,"contact_point_centroid":[0.55598,0.08171,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":5.0,"phase_name":"place_descend_1","phase_type":"descend","tcp_position_centroid":[0.62509,0.15425,0.28081]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.55598,0.08171,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.62337,0.15627,0.19828]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4833.0,"contact_point_centroid":[0.46439,-7e-05,0.04773],"force_p95":0.06895,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1051,"mean_force":0.0451,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46488,-0.01932,0.04718]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5410.0,"contact_point_centroid":[0.46422,-0.03854,0.04809],"force_p95":0.06526,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07423,"mean_force":0.04088,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46488,-0.01932,0.04718]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1757.0,"contact_point_centroid":[0.58624,0.11264,0.32111],"force_p95":0.01176,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0152,"mean_force":0.01058,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.58584,0.11263,0.31883]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1753.0,"contact_point_centroid":[0.62546,0.15426,0.28288],"force_p95":0.011,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01278,"mean_force":0.01048,"phase_index":5.0,"phase_name":"place_descend_1","phase_type":"descend","tcp_position_centroid":[0.62509,0.15425,0.28063]},{"body_a":"left_finger","body_b":"right_finger","contact_count":219.0,"contact_point_centroid":[0.62607,0.15703,0.19689],"force_p95":0.01101,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01274,"mean_force":0.01013,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.62579,0.15702,0.19477]}],"total_contact_groups":16},"final_pose_error":0.00977,"key_states":{"actual_goal_position":[0.63142,0.15919,0.19002],"final_object_position":[0.55598,0.08171,0.01602],"final_tcp_position":[0.62746,0.15746,0.19878],"realised_goal_position":[0.63142,0.15919,0.19002],"realised_object_initial_position":[0.47616,-0.02015,0.03]},"peak_contact_force":273012.60775,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":67.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02589],"object_pos_start":[0.47616,-0.02015,0.03],"object_to_goal_dist_end":0.28845,"object_to_goal_dist_start":0.28614,"object_z_max":0.03,"peak_contact_force":0.12322,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":264.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.48562,-0.01088,0.27503],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.24949,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":676.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.02589],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28845,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"pre_grasp_descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2704.0,"raw_peak_contact_force":0.12308,"subtask_id":"reach_object","tcp_end":[0.47252,-0.01948,0.05501],"tcp_start":[0.48562,-0.01088,0.27503],"tcp_to_object_dist_end":0.02923,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":46.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.47609,-0.01958,0.02573],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28823,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.14206,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12043.0,"raw_peak_contact_force":0.19206,"tcp_end":[0.46485,-0.01932,0.04715],"tcp_start":[0.47252,-0.01948,0.05501],"tcp_to_object_dist_end":0.02419,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":400.0,"n_steps_budget":960.0,"object_pos_end":[0.47603,-0.01946,0.15219],"object_pos_start":[0.47609,-0.01958,0.02573],"object_to_goal_dist_end":0.23978,"object_to_goal_dist_start":0.28823,"object_z_max":0.15191,"peak_contact_force":0.10584,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":13753.0,"raw_peak_contact_force":0.42166,"subtask_id":"reach_object","tcp_end":[0.46151,-0.01921,0.17757],"tcp_start":[0.46485,-0.01932,0.04715],"tcp_to_object_dist_end":0.02924,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":857.0,"n_steps_budget":1000.0,"object_pos_end":[0.55598,0.08171,0.01602],"object_pos_start":[0.47603,-0.01946,0.15219],"object_to_goal_dist_end":0.20487,"object_to_goal_dist_start":0.23978,"object_z_max":0.20856,"peak_contact_force":273012.60775,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":10723.0,"raw_peak_contact_force":2.27902,"subtask_id":"reach_goal","tcp_end":[0.62355,0.15155,0.36143],"tcp_start":[0.46151,-0.01921,0.17757],"tcp_to_object_dist_end":0.35882,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":412.0,"n_steps_budget":1000.0,"object_pos_end":[0.55598,0.08171,0.01602],"object_pos_start":[0.55598,0.08171,0.01602],"object_to_goal_dist_end":0.20487,"object_to_goal_dist_start":0.20487,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"place_descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3401.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_goal","tcp_end":[0.62746,0.15746,0.19878],"tcp_start":[0.62355,0.15155,0.36143],"tcp_to_object_dist_end":0.21036,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.55598,0.08171,0.01602],"object_pos_start":[0.55598,0.08171,0.01602],"object_to_goal_dist_end":0.20487,"object_to_goal_dist_start":0.20487,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1019.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.62197,0.15581,0.21766],"tcp_start":[0.62746,0.15746,0.19878],"tcp_to_object_dist_end":0.22473,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```