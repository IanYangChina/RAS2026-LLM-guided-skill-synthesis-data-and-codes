## Search State

- **Seed**: 6
- **Iteration**: 14 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 13 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | impedance_control | impedance_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 3 | 0.3291 | 0.30 | ❌ rejected |
| 12 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | impedance_control | impedance_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 6 | 0.2176 | 0.38 | ❌ rejected |
| 11 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | impedance_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 3 | 0.3717 | 0.39 | ❌ rejected |
| 10 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | impedance_control | impedance_control | impedance_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 3 | 0.3289 | 0.30 | ❌ rejected |
| 9 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | impedance_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 3 | 0.3783 | 0.40 | ✅ accepted |

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
- Frozen realised-scene SHA-256: `584133b5261cffac0dd4282704ff39e97bf4d452e60b02507679bbdea5a4de22`
- Frozen object start: [0.5038164351471943, -0.015672913018666156, 0.03]
- Frozen task target: [0.5869067239795378, 0.18744967655878825, 0.24811674852797]
- Goal object position: (0.5869067239795378, 0.18744967655878825, 0.24811674852797)
- place_goal_position (task success criterion — final object 3D position must be close to the realised airborne target here): (0.5869067239795378, 0.18744967655878825, 0.24811674852797)
- Grasp/lift components are optimiser fitness diagnostics only; canonical task_score is final object-to-realised-target proximity.
- Object initial pose: (0.5038164351471943, -0.015672913018666156, 0.03)
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
  frozen_object_start: [0.5038, -0.0157, 0.03]
  frozen_task_target: [0.5869, 0.1874, 0.2481]
  frozen_object_starts: {'grasp_target': [0.5038164351471943, -0.015672913018666156, 0.03]}
  frozen_targets: {'place_target': [0.5869067239795378, 0.18744967655878825, 0.24811674852797]}
  goal_tolerance_m: 0.02
  force_limit_n: 20
  force_scale_n: 5
  realized_scene_sha256: 584133b5261cffac0dd4282704ff39e97bf4d452e60b02507679bbdea5a4de22

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
| `object` | offset from object initial position (0.5038164351471943, -0.015672913018666156, 0.03) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.5869067239795378, 0.18744967655878825, 0.24811674852797) | final destination targets |
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

## Current Skill (Q=0.329) — your mutation base

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
  weight: 0.3
- id: touch_object
  anchor: object
  weight: 0.2
- id: lift_object
  anchor: object
  target_entity: object
  offset:
  - 0.0
  - 0.0
  - 0.15
  weight: 0.1
- id: pre_place
  offset:
  - 0.0
  - 0.0
  - 0.05
  weight: 0.2
- id: place
  target_entity: object
  weight: 0.2
phases:
- id: approach_1
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
    - 0.05
    orientation:
      mode: keep_current
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
    - 0.0
    orientation:
      mode: keep_current
  subtask_id: touch_object
- id: grasp
  type: grasp
  control: position_control
  termination: time_limit
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
  guards:
  - id: grasp_ok
    when: after_phase
    predicate: bilateral_grasp
    threshold: 1.0
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: repeat
- id: lift
  type: lift
  generator: linear_cartesian
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.2
      axis: world_z
      mode: add_to_offset
      sign: positive
    tolerance: 0.03
    orientation:
      mode: keep_current
  parameters:
    lift_height:
      type: scalar
      range:
      - 0.1
      - 0.3
      default: 0.2
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    lift_tolerance:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.03
      binds_to:
      - path: termination.pose_tolerance
        mode: replace
  guards:
  - id: object_raised
    when: after_phase
    predicate: object_lifted
    threshold: 0.05
    on_failure: abort
  subtask_id: lift_object
- id: transport
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
    - 0.05
    tolerance: 0.03
    orientation:
      mode: keep_current
  parameters:
    transport_speed:
      type: scalar
      range:
      - 0.01
      - 0.15
      default: 0.04
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: object_still_lifted
    when: before_phase
    predicate: object_lifted
    threshold: 0.05
    on_failure: abort
  - id: object_during_transport
    when: during_phase
    predicate: object_lifted
    threshold: 0.01
    on_failure: abort
  subtask_id: pre_place
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
    tolerance: 0.02
    orientation:
      mode: keep_current
  guards:
  - id: object_still_lifted_before_descend
    when: before_phase
    predicate: object_lifted
    threshold: 0.05
    on_failure: abort
  subtask_id: place
- id: release
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

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.05]
  - orientation: mode=keep_current
  - parameter_bindings: none
- **descend_1** (`descend`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings: none
- **grasp** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings: none
  - guards:
    - id=grasp_ok, when=after_phase, predicate=bilateral_grasp, on_failure=retry, threshold=1.0
  - retries: max_attempts=2, strategy=repeat
- **lift** (`lift`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=world_z, distance=0.2, mode=add_to_offset, sign=positive}, tolerance=0.03
  - orientation: mode=keep_current
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - lift_tolerance: status=consumed; consumers=termination.pose_tolerance (replace)
  - guards:
    - id=object_raised, when=after_phase, predicate=object_lifted, on_failure=abort, threshold=0.05
- **transport** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.05], tolerance=0.03
  - orientation: mode=keep_current
  - parameter_bindings:
    - transport_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=object_still_lifted, when=before_phase, predicate=object_lifted, on_failure=abort, threshold=0.05
    - id=object_during_transport, when=during_phase, predicate=object_lifted, on_failure=abort, threshold=0.01
- **descend_2** (`descend`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings: none
  - guards:
    - id=object_still_lifted_before_descend, when=before_phase, predicate=object_lifted, on_failure=abort, threshold=0.05
- **release** (`release`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings: none

## Design Metrics

- **Composite score**: 0.329
- **task_score** (E): 0.301
- **fitness_score**: 0.629  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.300

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.2154 |
| descend_1 | 1.00 | 1.00 | 0.0544 |
| grasp | 1.00 | 1.00 | 0.0118 |
| lift | 1.00 | 1.00 | 0.1931 |
| transport | 0.67 | 0.67 | 0.1820 |
| descend_2 | 1.00 | 0.50 | 0.0291 |
| release | 1.00 | 1.00 | 0.0202 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.496, 0.023, 0.089) | (0.500, 0.024, 0.030)→(0.500, 0.024, 0.026) | 0.269→0.271 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.496, 0.023, 0.089)→(0.494, 0.024, 0.034) | (0.500, 0.024, 0.026)→(0.500, 0.024, 0.026) | 0.271→0.271 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp | grasp | 1.00 / step_budget | (0.494, 0.024, 0.034)→(0.486, 0.023, 0.026) | (0.500, 0.024, 0.026)→(0.500, 0.023, 0.026) | 0.271→0.272 | 1.00 / 41.667 | 0.151 | 0.229 |
| lift | lift | 1.00 / step_budget | (0.486, 0.023, 0.026)→(0.485, 0.023, 0.219) | (0.500, 0.023, 0.026)→(0.508, 0.023, 0.215) | 0.272→0.199 | 1.00 / 21.333 | 0.132 | 0.705 |
| transport | approach | 0.67 / step_budget | (0.485, 0.023, 0.219)→(0.582, 0.172, 0.245) | (0.508, 0.023, 0.215)→(0.595, 0.166, 0.153) | 0.199→0.092 | 0.67 / 12.333 | 0.116 | 0.257 |
| descend_2 | descend | 1.00 / step_budget | (0.587, 0.180, 0.227)→(0.594, 0.190, 0.201) | (0.603, 0.180, 0.210)→(0.610, 0.190, 0.171) | 0.031→0.021 | 0.50 / 4.500 | 0.107 | 0.432 |
| release | release | 1.00 / step_budget | (0.594, 0.190, 0.201)→(0.589, 0.189, 0.220) | (0.610, 0.190, 0.171)→(0.609, 0.200, 0.016) | 0.021→0.172 | 1.00 / 4.000 | 0.124 | 1.652 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.423
- phase_score: 0.736
- phase_breakdown.touch_object_score: 0.870
- phase_breakdown.place_score: 0.675
- phase_breakdown.lift_object_score: 0.701
- phase_breakdown.reach_object_score: 0.820
- phase_breakdown.pre_place_score: 0.553
- grasp_place_fitness: 0.689

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.689
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.423
- **Median Q (composite search score)**: 0.299
- **K-run variance**: 0.0018
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 10.0
- **Final σ (mean)**: 0.567


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `daf90631fcbaf423e19452d0c9b90b9715013985cc94ef12ca0cd881e96195aa`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.05,0.05],"goal_z_delta":0.15,"object_xy_delta":[0.05,0.05]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `94660347aa4f41f6801e53bd449f8df59691da8bebfa4fef4947a3513fe04781`; realized-scene SHA-256: `584133b5261cffac0dd4282704ff39e97bf4d452e60b02507679bbdea5a4de22`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50382,-0.01567,0.03]},{"name":"goal","value":[0.58691,0.18745,0.24812]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.50382,-0.01567,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.58691,0.18745,0.24812]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.41277,"average_solve_count":235.0,"average_success_count":235.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"lift.lift_height":0.25975,"lift.lift_tolerance":0.05618,"transport.transport_speed":0.03098},"optimized_scores":{"best_composite_score":0.29864,"best_fitness_score":0.59864,"best_task_score":0.24032},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":62.0,"contact_point_centroid":[0.50083,-0.01523,-0.00148],"force_p95":0.66414,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.70259,"mean_force":0.32164,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.48868,-0.01527,0.02669]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3389.0,"contact_point_centroid":[0.49059,0.00374,0.11464],"force_p95":0.12673,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33899,"mean_force":0.07895,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.4878,-0.01524,0.11206]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3733.0,"contact_point_centroid":[0.49059,-0.0341,0.11164],"force_p95":0.12312,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30969,"mean_force":0.07345,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.48777,-0.01525,0.1098]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2204.0,"contact_point_centroid":[0.52076,0.05842,0.24945],"force_p95":0.19981,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.309,"mean_force":0.12439,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.51452,0.03989,0.2489]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3129.0,"contact_point_centroid":[0.52158,0.02422,0.2489],"force_p95":0.17389,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25381,"mean_force":0.10316,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.5156,0.04218,0.24949]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50381,-0.0155,-0.00203],"force_p95":0.13392,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.16578,"mean_force":0.12579,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.49138,-0.0153,0.02691]},{"body_a":"world","body_b":"grasp_target","contact_count":2584.0,"contact_point_centroid":[0.50382,-0.01567,-0.00194],"force_p95":0.13005,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12281,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49865,-0.00721,0.1939]},{"body_a":"world","body_b":"grasp_target","contact_count":736.0,"contact_point_centroid":[0.50382,-0.01567,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49783,-0.01497,0.06149]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4107.0,"contact_point_centroid":[0.4909,0.00391,0.02843],"force_p95":0.07632,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11356,"mean_force":0.05174,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.4902,-0.01529,0.02569]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4896.0,"contact_point_centroid":[0.49093,-0.03437,0.02751],"force_p95":0.0686,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0896,"mean_force":0.04476,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.49021,-0.01529,0.02569]}],"total_contact_groups":10},"final_pose_error":0.03852,"key_states":{"actual_goal_position":[0.58691,0.18745,0.24812],"final_object_position":[0.57785,0.13918,0.03996],"final_tcp_position":[0.57068,0.15664,0.28165],"realised_goal_position":[0.58691,0.18745,0.24812],"realised_object_initial_position":[0.50382,-0.01567,0.03]},"peak_contact_force":0.70259,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":647.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.03],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.30942,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2584.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.49943,-0.0146,0.08888],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.06302,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":184.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":736.0,"raw_peak_contact_force":0.12263,"subtask_id":"touch_object","tcp_end":[0.49836,-0.01538,0.0343],"tcp_start":[0.49943,-0.0146,0.08888],"tcp_to_object_dist_end":0.00992,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50367,-0.01516,0.02587],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31205,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.13119,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10803.0,"raw_peak_contact_force":0.16578,"tcp_end":[0.49017,-0.01529,0.02566],"tcp_start":[0.49836,-0.01538,0.0343],"tcp_to_object_dist_end":0.0135,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":21.0,"n_steps":240.0,"n_steps_budget":1000.0,"object_pos_end":[0.51298,-0.01523,0.23197],"object_pos_start":[0.50367,-0.01516,0.02587],"object_to_goal_dist_end":0.21634,"object_to_goal_dist_start":0.31205,"object_z_max":0.23112,"peak_contact_force":0.13437,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":7184.0,"raw_peak_contact_force":0.70259,"subtask_id":"lift_object","tcp_end":[0.48928,-0.01524,0.2358],"tcp_start":[0.49017,-0.01529,0.02566],"tcp_to_object_dist_end":0.02402,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":381.0,"n_steps_budget":1000.0,"object_pos_end":[0.57785,0.13918,0.03996],"object_pos_start":[0.51298,-0.01523,0.23197],"object_to_goal_dist_end":0.21387,"object_to_goal_dist_start":0.21634,"object_z_max":0.24627,"peak_contact_force":0.0,"phase_name":"transport","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":5333.0,"raw_peak_contact_force":0.309,"subtask_id":"pre_place","tcp_end":[0.57068,0.15664,0.28165],"tcp_start":[0.48928,-0.01524,0.2358],"tcp_to_object_dist_end":0.24242,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `fe7e0be33c0bb4db9d2bbbb069b6113d0e5a69a675a0d70bc1f582243e99e3cf`; realized-scene SHA-256: `8a4edc50bf1a337961423afe5cdf858aa28147f944f8fcd30a2ce1adc75d1bd6`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.51251,0.03972,0.03]},{"name":"goal","value":[0.62757,0.17252,0.14502]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.51251,0.03972,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.62757,0.17252,0.14502]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.35983,"average_solve_count":239.0,"average_success_count":239.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"lift.lift_height":0.21302,"lift.lift_tolerance":0.0653,"transport.transport_speed":0.03479},"optimized_scores":{"best_composite_score":0.38938,"best_fitness_score":0.68938,"best_task_score":0.42276},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":545.0,"contact_point_centroid":[0.63246,0.17001,-0.0036],"force_p95":0.76261,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.46231,"mean_force":0.20172,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.60977,0.16158,0.15903]},{"body_a":"world","body_b":"grasp_target","contact_count":63.0,"contact_point_centroid":[0.50945,0.0377,-0.00166],"force_p95":0.69183,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.72337,"mean_force":0.32579,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.49706,0.03795,0.02609]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":410.0,"contact_point_centroid":[0.61528,0.13904,0.17143],"force_p95":0.25227,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.44629,"mean_force":0.15891,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.61031,0.15724,0.1751]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":537.0,"contact_point_centroid":[0.61572,0.17546,0.17036],"force_p95":0.2328,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.44613,"mean_force":0.13967,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.61053,0.15747,0.17438]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":64.0,"contact_point_centroid":[0.62013,0.17879,0.14987],"force_p95":0.26115,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.39945,"mean_force":0.07883,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.61496,0.16325,0.15564]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6.0,"contact_point_centroid":[0.62313,0.14619,0.15047],"force_p95":0.33915,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.34324,"mean_force":0.20962,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.61579,0.16318,0.15752]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3140.0,"contact_point_centroid":[0.4983,0.0567,0.09282],"force_p95":0.11791,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33102,"mean_force":0.071,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.49586,0.03777,0.09089]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2758.0,"contact_point_centroid":[0.49844,0.01876,0.09545],"force_p95":0.12574,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32889,"mean_force":0.07749,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.49589,0.03777,0.09276]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.51258,0.03935,-0.00215],"force_p95":0.16782,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.25863,"mean_force":0.13469,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.4998,0.03818,0.02632]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3654.0,"contact_point_centroid":[0.5538,0.07309,0.18758],"force_p95":0.12489,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21556,"mean_force":0.09046,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.54789,0.09158,0.18657]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3351.0,"contact_point_centroid":[0.55786,0.11465,0.18767],"force_p95":0.13087,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19603,"mean_force":0.09556,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.55212,0.09603,0.18648]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4044.0,"contact_point_centroid":[0.49945,0.01888,0.02782],"force_p95":0.08189,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14903,"mean_force":0.05194,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.49861,0.03808,0.02505]},{"body_a":"world","body_b":"grasp_target","contact_count":2672.0,"contact_point_centroid":[0.51251,0.03972,-0.00194],"force_p95":0.12957,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12281,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50266,0.01826,0.1933]},{"body_a":"world","body_b":"grasp_target","contact_count":728.0,"contact_point_centroid":[0.51251,0.03972,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50614,0.03776,0.06086]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5025.0,"contact_point_centroid":[0.49939,0.05727,0.02685],"force_p95":0.07443,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08715,"mean_force":0.0448,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.49862,0.03808,0.02506]}],"total_contact_groups":15},"final_pose_error":0.01964,"key_states":{"actual_goal_position":[0.62757,0.17252,0.14502],"final_object_position":[0.63244,0.16994,0.016],"final_tcp_position":[0.61583,0.16315,0.15768],"realised_goal_position":[0.62757,0.17252,0.14502],"realised_object_initial_position":[0.51251,0.03972,0.03]},"peak_contact_force":1.46231,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":669.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.03],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21001,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2672.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.50754,0.03694,0.08814],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.06239,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":182.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":728.0,"raw_peak_contact_force":0.12263,"subtask_id":"touch_object","tcp_end":[0.50686,0.03875,0.03398],"tcp_start":[0.50754,0.03694,0.08814],"tcp_to_object_dist_end":0.00981,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51239,0.03807,0.0255],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21361,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.15785,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10869.0,"raw_peak_contact_force":0.25863,"tcp_end":[0.49859,0.03807,0.02502],"tcp_start":[0.50686,0.03875,0.03398],"tcp_to_object_dist_end":0.01381,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":190.0,"n_steps_budget":1000.0,"object_pos_end":[0.51873,0.03778,0.18673],"object_pos_start":[0.51239,0.03807,0.0255],"object_to_goal_dist_end":0.17816,"object_to_goal_dist_start":0.21361,"object_z_max":0.18586,"peak_contact_force":0.11317,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":5961.0,"raw_peak_contact_force":0.72337,"subtask_id":"lift_object","tcp_end":[0.49714,0.03781,0.18865],"tcp_start":[0.49859,0.03807,0.02502],"tcp_to_object_dist_end":0.02167,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":17.0,"n_steps":311.0,"n_steps_budget":1000.0,"object_pos_end":[0.6263,0.15282,0.17359],"object_pos_start":[0.51873,0.03778,0.18673],"object_to_goal_dist_end":0.03473,"object_to_goal_dist_start":0.17816,"object_z_max":0.19012,"peak_contact_force":0.21134,"phase_name":"transport","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":7005.0,"raw_peak_contact_force":0.21556,"subtask_id":"pre_place","tcp_end":[0.607,0.15311,0.18636],"tcp_start":[0.49714,0.03781,0.18865],"tcp_to_object_dist_end":0.02314,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":68.0,"n_steps_budget":1000.0,"object_pos_end":[0.63385,0.16365,0.13637],"object_pos_start":[0.6263,0.15282,0.17359],"object_to_goal_dist_end":0.0139,"object_to_goal_dist_start":0.03473,"object_z_max":0.17359,"peak_contact_force":0.21397,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":947.0,"raw_peak_contact_force":0.44629,"subtask_id":"place","tcp_end":[0.61583,0.16315,0.15768],"tcp_start":[0.607,0.15311,0.18636],"tcp_to_object_dist_end":0.02791,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.63244,0.16994,0.016],"object_pos_start":[0.63385,0.16365,0.13637],"object_to_goal_dist_end":0.12914,"object_to_goal_dist_start":0.0139,"object_z_max":0.13637,"peak_contact_force":0.12353,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":615.0,"raw_peak_contact_force":1.46231,"tcp_end":[0.60927,0.16142,0.17654],"tcp_start":[0.61583,0.16315,0.15768],"tcp_to_object_dist_end":0.16243,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `28f75809d7d1d0a11ca1a36dd459ad950e5a80b6bae34006f33ac9620425f5e5`; realized-scene SHA-256: `f44a4a1356de6cb8b5dec75995af4354e38cafd01c85526c1c2a33c8dd2e5b1c`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.4827,0.04873,0.03]},{"name":"goal","value":[0.58187,0.22885,0.23048]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.4827,0.04873,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.58187,0.22885,0.23048]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.36923,"average_solve_count":260.0,"average_success_count":260.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"lift.lift_height":0.25541,"lift.lift_tolerance":0.04461,"transport.transport_speed":0.03378},"optimized_scores":{"best_composite_score":0.29917,"best_fitness_score":0.59917,"best_task_score":0.23926},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":538.0,"contact_point_centroid":[0.5865,0.22985,-0.0045],"force_p95":0.96589,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.84183,"mean_force":0.22356,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.56869,0.21574,0.24617]},{"body_a":"world","body_b":"grasp_target","contact_count":63.0,"contact_point_centroid":[0.47964,0.04657,-0.00165],"force_p95":0.66846,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.68893,"mean_force":0.3264,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.46837,0.04665,0.0277]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":335.0,"contact_point_centroid":[0.57288,0.22792,0.25582],"force_p95":0.22944,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.41817,"mean_force":0.12072,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.56847,0.20991,0.26121]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":261.0,"contact_point_centroid":[0.57321,0.19231,0.25589],"force_p95":0.23393,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.41269,"mean_force":0.13284,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.56855,0.21003,0.26089]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3463.0,"contact_point_centroid":[0.46995,0.02743,0.11221],"force_p95":0.1254,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.3279,"mean_force":0.0752,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.46768,0.04646,0.1095]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3898.0,"contact_point_centroid":[0.46991,0.06541,0.11203],"force_p95":0.11649,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32496,"mean_force":0.06956,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.46769,0.04646,0.11014]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.48277,0.0483,-0.00218],"force_p95":0.17608,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.26157,"mean_force":0.1365,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.47102,0.04692,0.02769]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4061.0,"contact_point_centroid":[0.51835,0.10011,0.24659],"force_p95":0.15424,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24668,"mean_force":0.09682,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.51244,0.1185,0.24678]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3643.0,"contact_point_centroid":[0.52109,0.14199,0.24767],"force_p95":0.15138,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22565,"mean_force":0.10488,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.51551,0.1235,0.24793]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3630.0,"contact_point_centroid":[0.47121,0.02755,0.02972],"force_p95":0.09073,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15621,"mean_force":0.05749,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.46989,0.04681,0.02656]},{"body_a":"world","body_b":"grasp_target","contact_count":2632.0,"contact_point_centroid":[0.4827,0.04873,-0.00194],"force_p95":0.12979,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12281,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48892,0.02238,0.19368]},{"body_a":"world","body_b":"grasp_target","contact_count":744.0,"contact_point_centroid":[0.4827,0.04873,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.47769,0.04634,0.06155]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5464.0,"contact_point_centroid":[0.46974,0.06591,0.02917],"force_p95":0.073,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08779,"mean_force":0.04146,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.46989,0.04681,0.02656]}],"total_contact_groups":13},"final_pose_error":0.01975,"key_states":{"actual_goal_position":[0.58187,0.22885,0.23048],"final_object_position":[0.58616,0.22986,0.016],"final_tcp_position":[0.57296,0.21736,0.24384],"realised_goal_position":[0.58187,0.22885,0.23048],"realised_object_initial_position":[0.4827,0.04873,0.03]},"peak_contact_force":1.84183,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":659.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.03],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28719,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2632.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.47974,0.04532,0.08873],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.06288,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":186.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":744.0,"raw_peak_contact_force":0.12263,"subtask_id":"touch_object","tcp_end":[0.47773,0.04758,0.03452],"tcp_start":[0.47974,0.04532,0.08873],"tcp_to_object_dist_end":0.00992,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.48262,0.04672,0.02542],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.29168,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.16296,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10894.0,"raw_peak_contact_force":0.26157,"tcp_end":[0.46986,0.0468,0.02653],"tcp_start":[0.47773,0.04758,0.03452],"tcp_to_object_dist_end":0.01281,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":20.0,"n_steps":233.0,"n_steps_budget":1000.0,"object_pos_end":[0.49172,0.04647,0.2277],"object_pos_start":[0.48262,0.04672,0.02542],"object_to_goal_dist_end":0.20347,"object_to_goal_dist_start":0.29168,"object_z_max":0.22683,"peak_contact_force":0.1494,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":7424.0,"raw_peak_contact_force":0.68893,"subtask_id":"lift_object","tcp_end":[0.46913,0.04654,0.23205],"tcp_start":[0.46986,0.0468,0.02653],"tcp_to_object_dist_end":0.02301,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":20.0,"n_steps":373.0,"n_steps_budget":1000.0,"object_pos_end":[0.57956,0.20664,0.24653],"object_pos_start":[0.49172,0.04647,0.2277],"object_to_goal_dist_end":0.0275,"object_to_goal_dist_start":0.20347,"object_z_max":0.24646,"peak_contact_force":0.13555,"phase_name":"transport","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":7704.0,"raw_peak_contact_force":0.24668,"subtask_id":"pre_place","tcp_end":[0.56694,0.20672,0.26751],"tcp_start":[0.46913,0.04654,0.23205],"tcp_to_object_dist_end":0.02449,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":59.0,"n_steps_budget":1000.0,"object_pos_end":[0.58604,0.21723,0.2053],"object_pos_start":[0.57956,0.20664,0.24653],"object_to_goal_dist_end":0.02804,"object_to_goal_dist_start":0.0275,"object_z_max":0.24653,"peak_contact_force":0.0,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":596.0,"raw_peak_contact_force":0.41817,"subtask_id":"place","tcp_end":[0.57296,0.21736,0.24384],"tcp_start":[0.56694,0.20672,0.26751],"tcp_to_object_dist_end":0.04069,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.58616,0.22986,0.016],"object_pos_start":[0.58604,0.21723,0.2053],"object_to_goal_dist_end":0.21453,"object_to_goal_dist_start":0.02804,"object_z_max":0.2053,"peak_contact_force":0.12358,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":538.0,"raw_peak_contact_force":1.84183,"tcp_end":[0.56842,0.21559,0.26366],"tcp_start":[0.57296,0.21736,0.24384],"tcp_to_object_dist_end":0.24871,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```