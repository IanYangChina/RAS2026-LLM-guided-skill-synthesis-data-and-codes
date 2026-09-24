## Search State

- **Seed**: 0
- **Iteration**: 4 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 3 | approach → descend → grasp → lift → approach → descend → release | arc_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 5 | 0.1902 | 0.23 | ✅ accepted |
| 2 | approach → descend → grasp → lift → release | arc_cartesian | linear_cartesian | — | linear_cartesian | — | force_threshold_switch | admittance_control | position_control | position_control | admittance_control | pose_tolerance | contact_detected | grasp_success | pose_tolerance | pose_tolerance | 4 | 0.2706 | 0.17 | ✅ accepted |
| 1 | approach → descend → grasp → lift → release | arc_cartesian | linear_cartesian | — | linear_cartesian | — | force_threshold_switch | admittance_control | position_control | position_control | admittance_control | pose_tolerance | contact_detected | grasp_success | pose_tolerance | pose_tolerance | 4 | 0.2702 | 0.17 | ✅ accepted |
| 0 | approach → descend → grasp → lift → release | arc_cartesian | linear_cartesian | — | linear_cartesian | — | force_threshold_switch | admittance_control | position_control | position_control | admittance_control | pose_tolerance | contact_detected | grasp_success | pose_tolerance | pose_tolerance | 4 | 0.2701 | 0.17 | ✅ accepted |

**Proposal policy**: task_score is 0.23 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.190) — your mutation base

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
  generator: arc_cartesian
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

- **Composite score**: 0.190
- **task_score** (E): 0.232
- **fitness_score**: 0.590  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.400

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.0758 |
| descend_1 | 1.00 | 1.00 | 0.1903 |
| grasp_1 | 1.00 | 1.00 | 0.0120 |
| lift_1 | 1.00 | 1.00 | 0.1007 |
| transport_1 | 1.00 | 1.00 | 0.2484 |
| place_descend_1 | 1.00 | 1.00 | 0.0927 |
| release_1 | 1.00 | 1.00 | 0.0213 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.496, 0.001, 0.235) | (0.497, 0.001, 0.030)→(0.497, 0.001, 0.026) | 0.263→0.265 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.496, 0.001, 0.235)→(0.493, 0.001, 0.045) | (0.497, 0.001, 0.026)→(0.497, 0.001, 0.026) | 0.265→0.265 | 1.00 / 4.000 | 27.129 | 0.123 |
| grasp_1 | grasp | 1.00 / step_budget | (0.493, 0.001, 0.045)→(0.485, 0.001, 0.036) | (0.497, 0.001, 0.026)→(0.497, 0.001, 0.025) | 0.265→0.266 | 1.00 / 45.333 | 0.160 | 0.237 |
| lift_1 | lift | 1.00 / step_budget | (0.485, 0.001, 0.036)→(0.492, 0.001, 0.137) | (0.497, 0.001, 0.025)→(0.509, 0.001, 0.122) | 0.266→0.217 | 1.00 / 23.000 | 0.109 | 0.514 |
| transport_1 | approach | 1.00 / step_budget | (0.492, 0.001, 0.137)→(0.575, 0.172, 0.286) | (0.509, 0.001, 0.122)→(0.536, 0.058, 0.016) | 0.217→0.221 | 1.00 / 8.667 | 91004.380 | 1.868 |
| place_descend_1 | descend | 1.00 / step_budget | (0.575, 0.172, 0.286)→(0.579, 0.182, 0.194) | (0.536, 0.058, 0.016)→(0.536, 0.058, 0.016) | 0.221→0.221 | 1.00 / 8.333 | 3249.700 | 0.123 |
| release_1 | release | 1.00 / step_budget | (0.579, 0.182, 0.194)→(0.573, 0.180, 0.215) | (0.536, 0.058, 0.016)→(0.536, 0.058, 0.016) | 0.221→0.221 | 1.00 / 4.000 | 0.123 | 0.123 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.295
- phase_score: 0.716
- phase_breakdown.reach_goal_score: 0.819
- phase_breakdown.reach_object_score: 0.302
- grasp_place_fitness: 0.618

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.618
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.295
- **Median Q (composite search score)**: 0.177
- **K-run variance**: 0.0004
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.425


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.90683,"average_solve_count":161.0,"average_success_count":161.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.12286,"descend_1.grasp_offset":0.00305,"lift_1.lift_height":0.12651,"release_1.release_duration":0.45356,"transport_1.transport_height":0.10333},"optimized_scores":{"best_composite_score":0.17662,"best_fitness_score":0.57662,"best_task_score":0.20241},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":1696.0,"contact_point_centroid":[0.53507,0.03065,-0.00263],"force_p95":0.28118,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.88513,"mean_force":0.15073,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.53365,0.08426,0.2733]},{"body_a":"world","body_b":"grasp_target","contact_count":80.0,"contact_point_centroid":[0.51192,-0.02069,-0.00144],"force_p95":0.45394,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.52516,"mean_force":0.10177,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49934,-0.02139,0.03508]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4866.0,"contact_point_centroid":[0.50448,-0.00239,0.08006],"force_p95":0.1098,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29963,"mean_force":0.07037,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.50207,-0.02138,0.07761]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5409.0,"contact_point_centroid":[0.50443,-0.04023,0.07811],"force_p95":0.10417,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29088,"mean_force":0.0653,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.50196,-0.02138,0.07645]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2623.0,"contact_point_centroid":[0.51573,0.01471,0.16714],"force_p95":0.17661,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26113,"mean_force":0.10117,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.50991,-0.00387,0.16639]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3061.0,"contact_point_centroid":[0.51588,-0.02147,0.16765],"force_p95":0.14419,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25883,"mean_force":0.09173,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.5101,-0.00315,0.16755]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.51375,-0.02276,-0.00215],"force_p95":0.1648,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.23782,"mean_force":0.13378,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.50154,-0.02144,0.03486]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4067.0,"contact_point_centroid":[0.50098,-0.0022,0.03635],"force_p95":0.08135,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1525,"mean_force":0.0519,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.50037,-0.02142,0.03359]},{"body_a":"world","body_b":"grasp_target","contact_count":1024.0,"contact_point_centroid":[0.5137,-0.02302,-0.00187],"force_p95":0.13685,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.1231,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50371,5e-05,0.23503]},{"body_a":"world","body_b":"grasp_target","contact_count":1184.0,"contact_point_centroid":[0.5137,-0.02302,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50756,-0.01729,0.10583]},{"body_a":"world","body_b":"grasp_target","contact_count":928.0,"contact_point_centroid":[0.53493,0.03072,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":5.0,"phase_name":"place_descend_1","phase_type":"descend","tcp_position_centroid":[0.5489,0.14316,0.27165]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.53493,0.03072,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.54677,0.14754,0.23231]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5018.0,"contact_point_centroid":[0.501,-0.04058,0.03543],"force_p95":0.07367,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08267,"mean_force":0.04454,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.50038,-0.02142,0.0336]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1595.0,"contact_point_centroid":[0.53556,0.09015,0.28094],"force_p95":0.01152,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01622,"mean_force":0.01059,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.53527,0.09015,0.27861]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1007.0,"contact_point_centroid":[0.54942,0.14314,0.27408],"force_p95":0.01095,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01278,"mean_force":0.0103,"phase_index":5.0,"phase_name":"place_descend_1","phase_type":"descend","tcp_position_centroid":[0.5489,0.14314,0.27182]},{"body_a":"left_finger","body_b":"right_finger","contact_count":224.0,"contact_point_centroid":[0.54952,0.14822,0.22982],"force_p95":0.01087,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01089,"mean_force":0.00993,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.54885,0.14821,0.22749]}],"total_contact_groups":16},"final_pose_error":0.00993,"key_states":{"actual_goal_position":[0.5541,0.15165,0.22199],"final_object_position":[0.53493,0.03072,0.01602],"final_tcp_position":[0.55033,0.14852,0.23063],"realised_goal_position":[0.5541,0.15165,0.22199],"realised_object_initial_position":[0.5137,-0.02302,0.03]},"peak_contact_force":273012.89366,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":257.0,"n_steps_budget":1000.0,"object_pos_end":[0.5137,-0.02302,0.02602],"object_pos_start":[0.5137,-0.02302,0.03],"object_to_goal_dist_end":0.26561,"object_to_goal_dist_start":0.26269,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1024.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.50864,-0.01312,0.169],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.14341,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":296.0,"n_steps_budget":1000.0,"object_pos_end":[0.5137,-0.02302,0.02602],"object_pos_start":[0.5137,-0.02302,0.02602],"object_to_goal_dist_end":0.26561,"object_to_goal_dist_start":0.26561,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1184.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.50875,-0.02156,0.04285],"tcp_start":[0.50864,-0.01312,0.169],"tcp_to_object_dist_end":0.01761,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51362,-0.02156,0.0255],"object_pos_start":[0.5137,-0.02302,0.02602],"object_to_goal_dist_end":0.26505,"object_to_goal_dist_start":0.26561,"object_z_max":0.02602,"peak_contact_force":0.15661,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10885.0,"raw_peak_contact_force":0.23782,"tcp_end":[0.50034,-0.02141,0.03356],"tcp_start":[0.50875,-0.02156,0.04285],"tcp_to_object_dist_end":0.01553,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":329.0,"n_steps_budget":750.0,"object_pos_end":[0.52584,-0.02151,0.12016],"object_pos_start":[0.51362,-0.02156,0.0255],"object_to_goal_dist_end":0.20286,"object_to_goal_dist_start":0.26505,"object_z_max":0.11991,"peak_contact_force":0.10989,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":10355.0,"raw_peak_contact_force":0.52516,"subtask_id":"reach_object","tcp_end":[0.50817,-0.02144,0.13282],"tcp_start":[0.50034,-0.02141,0.03356],"tcp_to_object_dist_end":0.02174,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":786.0,"n_steps_budget":1000.0,"object_pos_end":[0.53493,0.03072,0.01602],"object_pos_start":[0.52584,-0.02151,0.12016],"object_to_goal_dist_end":0.23962,"object_to_goal_dist_start":0.20286,"object_z_max":0.18185,"peak_contact_force":273012.89366,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":8975.0,"raw_peak_contact_force":1.88513,"subtask_id":"reach_goal","tcp_end":[0.54865,0.13841,0.31161],"tcp_start":[0.50817,-0.02144,0.13282],"tcp_to_object_dist_end":0.31489,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":232.0,"n_steps_budget":1000.0,"object_pos_end":[0.53493,0.03072,0.01602],"object_pos_start":[0.53493,0.03072,0.01602],"object_to_goal_dist_end":0.23962,"object_to_goal_dist_start":0.23962,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"place_descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1935.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_goal","tcp_end":[0.55033,0.14852,0.23063],"tcp_start":[0.54865,0.13841,0.31161],"tcp_to_object_dist_end":0.2453,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53493,0.03072,0.01602],"object_pos_start":[0.53493,0.03072,0.01602],"object_to_goal_dist_end":0.23962,"object_to_goal_dist_start":0.23962,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1024.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.54558,0.14715,0.2526],"tcp_start":[0.55033,0.14852,0.23063],"tcp_to_object_dist_end":0.2639,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.8,"average_solve_count":170.0,"average_success_count":170.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.27355,"descend_1.grasp_offset":0.0076,"lift_1.lift_height":0.13354,"release_1.release_duration":0.94313,"transport_1.transport_height":0.10112},"optimized_scores":{"best_composite_score":0.21846,"best_fitness_score":0.61846,"best_task_score":0.29452},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":1437.0,"contact_point_centroid":[0.5387,0.11891,-0.00271],"force_p95":0.33846,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.79337,"mean_force":0.15592,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.53779,0.1739,0.22379]},{"body_a":"world","body_b":"grasp_target","contact_count":83.0,"contact_point_centroid":[0.49933,0.04203,-0.00151],"force_p95":0.45571,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.49246,"mean_force":0.09765,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.4877,0.04245,0.04037]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5697.0,"contact_point_centroid":[0.49188,0.06149,0.0841],"force_p95":0.10567,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30089,"mean_force":0.06298,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49008,0.04248,0.08212]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2409.0,"contact_point_centroid":[0.50751,0.08673,0.16284],"force_p95":0.1498,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28236,"mean_force":0.0969,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.50183,0.068,0.16161]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5366.0,"contact_point_centroid":[0.49213,0.02348,0.08656],"force_p95":0.10563,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26137,"mean_force":0.06521,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49028,0.04249,0.08418]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2885.0,"contact_point_centroid":[0.50845,0.05168,0.16385],"force_p95":0.13345,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26056,"mean_force":0.08484,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.50244,0.06999,0.16328]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50127,0.04482,-0.00222],"force_p95":0.18159,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.25056,"mean_force":0.13832,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.48987,0.04266,0.03998]},{"body_a":"world","body_b":"grasp_target","contact_count":296.0,"contact_point_centroid":[0.50118,0.04505,-0.00158],"force_p95":0.13832,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.1245,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49905,0.0114,0.30051]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4954.0,"contact_point_centroid":[0.48864,0.02332,0.04168],"force_p95":0.0734,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13128,"mean_force":0.04358,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.48873,0.04256,0.03877]},{"body_a":"world","body_b":"grasp_target","contact_count":2348.0,"contact_point_centroid":[0.50118,0.04505,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12264,"mean_force":0.1226,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49705,0.03435,0.17364]},{"body_a":"world","body_b":"grasp_target","contact_count":956.0,"contact_point_centroid":[0.53863,0.11893,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"place_descend_1","phase_type":"descend","tcp_position_centroid":[0.55741,0.2344,0.19659]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.53863,0.11893,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.55526,0.23872,0.15526]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5423.0,"contact_point_centroid":[0.48862,0.06194,0.04115],"force_p95":0.07472,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07887,"mean_force":0.04207,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.48874,0.04256,0.03878]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1316.0,"contact_point_centroid":[0.54118,0.18221,0.22938],"force_p95":0.01226,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01545,"mean_force":0.01049,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.54069,0.18219,0.22705]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1027.0,"contact_point_centroid":[0.55798,0.2344,0.19893],"force_p95":0.01094,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01265,"mean_force":0.01039,"phase_index":5.0,"phase_name":"place_descend_1","phase_type":"descend","tcp_position_centroid":[0.5574,0.23438,0.19676]},{"body_a":"left_finger","body_b":"right_finger","contact_count":218.0,"contact_point_centroid":[0.55817,0.23999,0.15317],"force_p95":0.01095,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01097,"mean_force":0.01019,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.55783,0.23995,0.15094]}],"total_contact_groups":16},"final_pose_error":0.00998,"key_states":{"actual_goal_position":[0.56442,0.24486,0.14677],"final_object_position":[0.53863,0.11893,0.01602],"final_tcp_position":[0.55964,0.24063,0.15446],"realised_goal_position":[0.56442,0.24486,0.14677],"realised_object_initial_position":[0.50118,0.04505,0.03]},"peak_contact_force":9748.85569,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":75.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02593],"object_pos_start":[0.50118,0.04505,0.03],"object_to_goal_dist_end":0.24193,"object_to_goal_dist_start":0.23992,"object_z_max":0.03,"peak_contact_force":0.12241,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":296.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.49888,0.02563,0.30008],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.27484,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":587.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.02593],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.24193,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2348.0,"raw_peak_contact_force":0.12264,"subtask_id":"reach_object","tcp_end":[0.49688,0.04326,0.04766],"tcp_start":[0.49888,0.02563,0.30008],"tcp_to_object_dist_end":0.02214,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":47.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50115,0.0432,0.02526],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.2438,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"peak_contact_force":0.17315,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12177.0,"raw_peak_contact_force":0.25056,"tcp_end":[0.48871,0.04256,0.03874],"tcp_start":[0.49688,0.04326,0.04766],"tcp_to_object_dist_end":0.01836,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":330.0,"n_steps_budget":780.0,"object_pos_end":[0.51227,0.04332,0.12231],"object_pos_start":[0.50115,0.0432,0.02526],"object_to_goal_dist_end":0.20962,"object_to_goal_dist_start":0.2438,"object_z_max":0.12205,"peak_contact_force":0.10821,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":11146.0,"raw_peak_contact_force":0.49246,"subtask_id":"reach_object","tcp_end":[0.49592,0.04278,0.13955],"tcp_start":[0.48871,0.04256,0.03874],"tcp_to_object_dist_end":0.02376,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":689.0,"n_steps_budget":1000.0,"object_pos_end":[0.53863,0.11893,0.01602],"object_pos_start":[0.51227,0.04332,0.12231],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.20962,"object_z_max":0.16275,"peak_contact_force":0.12263,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":8047.0,"raw_peak_contact_force":1.79337,"subtask_id":"reach_goal","tcp_end":[0.55689,0.22915,0.23836],"tcp_start":[0.49592,0.04278,0.13955],"tcp_to_object_dist_end":0.24883,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":239.0,"n_steps_budget":1000.0,"object_pos_end":[0.53863,0.11893,0.01602],"object_pos_start":[0.53863,0.11893,0.01602],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18336,"object_z_max":0.01602,"peak_contact_force":9748.85569,"phase_name":"place_descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1983.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_goal","tcp_end":[0.55964,0.24063,0.15446],"tcp_start":[0.55689,0.22915,0.23836],"tcp_to_object_dist_end":0.18552,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53863,0.11893,0.01602],"object_pos_start":[0.53863,0.11893,0.01602],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18336,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1018.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.55372,0.23797,0.1752],"tcp_start":[0.55964,0.24063,0.15446],"tcp_to_object_dist_end":0.19934,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.91525,"average_solve_count":177.0,"average_success_count":177.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.18886,"descend_1.grasp_offset":0.00413,"lift_1.lift_height":0.13111,"release_1.release_duration":0.92376,"transport_1.transport_height":0.13163},"optimized_scores":{"best_composite_score":0.17547,"best_fitness_score":0.57547,"best_task_score":0.20055},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":2290.0,"contact_point_centroid":[0.53348,0.02425,-0.00246],"force_p95":0.15986,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.9264,"mean_force":0.14441,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.56493,0.08766,0.27079]},{"body_a":"world","body_b":"grasp_target","contact_count":76.0,"contact_point_centroid":[0.47364,-0.0187,-0.0014],"force_p95":0.4663,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.52296,"mean_force":0.11373,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46364,-0.01896,0.03776]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2936.0,"contact_point_centroid":[0.48994,-0.01994,0.16857],"force_p95":0.15409,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27818,"mean_force":0.09172,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.48414,-0.0015,0.16792]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2740.0,"contact_point_centroid":[0.49032,0.01755,0.16981],"force_p95":0.15084,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2734,"mean_force":0.09554,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.48455,-0.00102,0.16876]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6025.0,"contact_point_centroid":[0.46715,-0.03802,0.08362],"force_p95":0.09615,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27117,"mean_force":0.05757,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46587,-0.019,0.0819]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5506.0,"contact_point_centroid":[0.46709,0.00012,0.08453],"force_p95":0.10191,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26282,"mean_force":0.06155,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46591,-0.019,0.08211]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.47619,-0.02003,-0.00211],"force_p95":0.15273,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.2215,"mean_force":0.13075,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46573,-0.01901,0.03742]},{"body_a":"world","body_b":"grasp_target","contact_count":524.0,"contact_point_centroid":[0.47616,-0.02015,-0.00176],"force_p95":0.13797,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12356,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49042,-0.00225,0.26887]},{"body_a":"world","body_b":"grasp_target","contact_count":1804.0,"contact_point_centroid":[0.47616,-0.02015,-0.00199],"force_p95":0.12264,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12264,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.47539,-0.01461,0.13952]},{"body_a":"world","body_b":"grasp_target","contact_count":1164.0,"contact_point_centroid":[0.53339,0.02429,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":5.0,"phase_name":"place_descend_1","phase_type":"descend","tcp_position_centroid":[0.62271,0.15196,0.2543]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.53339,0.02429,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.62243,0.15545,0.19784]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5289.0,"contact_point_centroid":[0.46406,0.00027,0.03807],"force_p95":0.0667,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11286,"mean_force":0.04119,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46463,-0.01898,0.03633]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5462.0,"contact_point_centroid":[0.46408,-0.03828,0.03794],"force_p95":0.06695,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07422,"mean_force":0.04102,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46464,-0.01898,0.03633]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2216.0,"contact_point_centroid":[0.56989,0.09285,0.27769],"force_p95":0.01128,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01651,"mean_force":0.01053,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.56967,0.09285,0.27539]},{"body_a":"left_finger","body_b":"right_finger","contact_count":217.0,"contact_point_centroid":[0.62531,0.15622,0.19653],"force_p95":0.01109,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01294,"mean_force":0.01028,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.62484,0.1562,0.19428]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1249.0,"contact_point_centroid":[0.62318,0.15197,0.25647],"force_p95":0.01094,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01265,"mean_force":0.01039,"phase_index":5.0,"phase_name":"place_descend_1","phase_type":"descend","tcp_position_centroid":[0.62271,0.15196,0.2543]}],"total_contact_groups":16},"final_pose_error":0.00998,"key_states":{"actual_goal_position":[0.63142,0.15919,0.19002],"final_object_position":[0.53339,0.02429,0.01602],"final_tcp_position":[0.62653,0.15661,0.19832],"realised_goal_position":[0.63142,0.15919,0.19002],"realised_object_initial_position":[0.47616,-0.02015,0.03]},"peak_contact_force":81.14225,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":132.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.03],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28614,"object_z_max":0.03,"peak_contact_force":0.12261,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":524.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.48029,-0.01018,0.23541],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.20967,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":451.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":81.14225,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1804.0,"raw_peak_contact_force":0.12264,"subtask_id":"reach_object","tcp_end":[0.47253,-0.01913,0.04436],"tcp_start":[0.48029,-0.01018,0.23541],"tcp_to_object_dist_end":0.01873,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":48.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.47608,-0.01924,0.02562],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28809,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.14905,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12551.0,"raw_peak_contact_force":0.2215,"tcp_end":[0.46461,-0.01898,0.0363],"tcp_start":[0.47253,-0.01913,0.04436],"tcp_to_object_dist_end":0.01568,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":320.0,"n_steps_budget":780.0,"object_pos_end":[0.48765,-0.01908,0.12365],"object_pos_start":[0.47608,-0.01924,0.02562],"object_to_goal_dist_end":0.23845,"object_to_goal_dist_start":0.28809,"object_z_max":0.12338,"peak_contact_force":0.1086,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":11607.0,"raw_peak_contact_force":0.52296,"subtask_id":"reach_object","tcp_end":[0.47104,-0.01911,0.13743],"tcp_start":[0.46461,-0.01898,0.0363],"tcp_to_object_dist_end":0.02159,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":928.0,"n_steps_budget":1000.0,"object_pos_end":[0.53339,0.02429,0.01602],"object_pos_start":[0.48765,-0.01908,0.12365],"object_to_goal_dist_end":0.241,"object_to_goal_dist_start":0.23845,"object_z_max":0.1795,"peak_contact_force":0.12263,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":10182.0,"raw_peak_contact_force":1.9264,"subtask_id":"reach_goal","tcp_end":[0.62027,0.14797,0.30947],"tcp_start":[0.47104,-0.01911,0.13743],"tcp_to_object_dist_end":0.33009,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":291.0,"n_steps_budget":1000.0,"object_pos_end":[0.53339,0.02429,0.01602],"object_pos_start":[0.53339,0.02429,0.01602],"object_to_goal_dist_end":0.241,"object_to_goal_dist_start":0.241,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"place_descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2413.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_goal","tcp_end":[0.62653,0.15661,0.19832],"tcp_start":[0.62027,0.14797,0.30947],"tcp_to_object_dist_end":0.24375,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53339,0.02429,0.01602],"object_pos_start":[0.53339,0.02429,0.01602],"object_to_goal_dist_end":0.241,"object_to_goal_dist_start":0.241,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1017.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.62102,0.15499,0.21723],"tcp_start":[0.62653,0.15661,0.19832],"tcp_to_object_dist_end":0.25544,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```