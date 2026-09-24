## Search State

- **Seed**: 6
- **Iteration**: 12 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 11 | approach → descend → grasp → lift → lift → approach → descend | arc_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 6 | 0.2213 | 0.40 | ✅ accepted |
| 10 | approach → descend → grasp → lift → approach → release → retract | arc_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 5 | 0.2241 | 0.29 | ❌ rejected |
| 9 | approach → descend → grasp → lift → approach | arc_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | 4 | 0.2215 | 0.24 | ❌ rejected |
| 8 | approach → descend → grasp → lift → approach → release → retract | arc_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 5 | 0.2250 | 0.29 | ✅ accepted |
| 7 | approach → descend → grasp → lift → approach → descend → release → retract | arc_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 7 | 0.0617 | 0.24 | ❌ rejected |

**Proposal policy**: task_score is 0.40 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.221) — your mutation base

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
  - 0.15
  weight: 0.2
- id: grasp_lift
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.2
  weight: 0.3
- id: reach_goal
  weight: 0.5
phases:
- id: approach_1
  type: approach
  generator: arc_cartesian
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
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    arc_height:
      type: scalar
      range:
      - 0.02
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.arc_height
        mode: replace
  subtask_id: approach_object
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
    - 0.01
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    descend_offset_z:
      type: scalar
      range:
      - 0.0
      - 0.03
      default: 0.01
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: approach_object
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
  guards:
  - id: bilateral_grasp
    when: after_phase
    predicate: bilateral_grasp
    threshold: 0.5
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: repeat
  subtask_id: grasp_lift
- id: lift_1
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
      distance: 0.2
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
      - 0.1
      - 0.35
      default: 0.25
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
  subtask_id: grasp_lift
- id: ascend_above_goal
  type: lift
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: world
    offset:
    - 0.5
    - 0.0
    - 0.35
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    ascent_speed:
      type: scalar
      range:
      - 0.02
      - 0.15
      default: 0.08
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: reach_goal
- id: transport_over_goal
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    entity: placement_surface
    offset:
    - 0.0
    - 0.0
    - 0.0
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    transport_speed:
      type: scalar
      range:
      - 0.02
      - 0.15
      default: 0.08
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: reach_goal
- id: descend_to_goal_height
  type: descend
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    entity: placement_surface
    offset:
    - 0.0
    - 0.0
    - -0.12
    tolerance: 0.015
    orientation:
      mode: keep_current
  parameters:
    descend_offset_z:
      type: scalar
      range:
      - -0.2
      - -0.02
      default: -0.12
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: reach_goal

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.15], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - arc_height: status=consumed; consumers=generator.arc_height (replace)
- **descend_1** (`descend`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.01], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - descend_offset_z: status=consumed; consumers=target.offset.z (replace)
- **grasp_1** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings: none
  - guards:
    - id=bilateral_grasp, when=after_phase, predicate=bilateral_grasp, on_failure=retry, threshold=0.5
  - retries: max_attempts=2, strategy=repeat
- **lift_1** (`lift`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=world_z, distance=0.2, mode=add_to_offset, sign=positive}, tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset_along_axis.distance (replace)
- **ascend_above_goal** (`lift`)
  - target: source=yaml, anchor=world, offset=[0.5, 0.0, 0.35], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - ascent_speed: status=consumed; consumers=generator.speed (replace)
- **transport_over_goal** (`approach`)
  - target: source=yaml, anchor=task_goal, entity=placement_surface, offset=[0.0, 0.0, 0.0], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - transport_speed: status=consumed; consumers=generator.speed (replace)
- **descend_to_goal_height** (`descend`)
  - target: source=yaml, anchor=task_goal, entity=placement_surface, offset=[0.0, 0.0, -0.12], tolerance=0.015
  - orientation: mode=keep_current
  - parameter_bindings:
    - descend_offset_z: status=consumed; consumers=target.offset.z (replace)

## Design Metrics

- **Composite score**: 0.221
- **task_score** (E): 0.397
- **fitness_score**: 0.671  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Complexity Penalty**: 0.450

## Per-Phase Performance

| Phase | Normal Term. Rate | Mean Displacement (m) |
| ------- | ------------------- | ------------------------ |
| approach_1 | 1.00 | 0.1194 |
| descend_1 | 1.00 | 0.1471 |
| grasp_1 | 1.00 | 0.0118 |
| lift_1 | 1.00 | 0.1404 |
| ascend_above_goal | 1.00 | 0.1592 |
| transport_over_goal | 1.00 | 0.2380 |
| descend_to_goal_height | 1.00 | 0.0643 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end |
| --- | --- | --- | --- | --- | --- |
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.497, 0.039, 0.191) | (0.500, 0.024, 0.030)→(0.500, 0.024, 0.026) | 0.269→0.271 |
| descend_1 | descend | 1.00 / step_budget | (0.497, 0.039, 0.191)→(0.495, 0.025, 0.045) | (0.500, 0.024, 0.026)→(0.500, 0.024, 0.026) | 0.271→0.271 |
| grasp_1 | grasp | 1.00 / step_budget | (0.495, 0.025, 0.045)→(0.487, 0.025, 0.036) | (0.500, 0.024, 0.026)→(0.500, 0.025, 0.026) | 0.271→0.271 |
| lift_1 | lift | 1.00 / step_budget | (0.487, 0.025, 0.036)→(0.484, 0.025, 0.177) | (0.500, 0.025, 0.026)→(0.500, 0.028, 0.120) | 0.271→0.218 |
| ascend_above_goal | lift | 1.00 / step_budget | (0.484, 0.025, 0.177)→(0.497, 0.003, 0.331) | (0.500, 0.028, 0.120)→(0.507, 0.018, 0.210) | 0.218→0.225 |
| transport_over_goal | approach | 1.00 / step_budget | (0.497, 0.003, 0.331)→(0.588, 0.180, 0.210) | (0.507, 0.018, 0.210)→(0.559, 0.149, 0.092) | 0.225→0.145 |
| descend_to_goal_height | descend | 1.00 / step_budget | (0.588, 0.180, 0.210)→(0.592, 0.190, 0.146) | (0.559, 0.149, 0.092)→(0.561, 0.155, 0.073) | 0.145→0.164 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.735
- phase_score: 0.410
- phase_breakdown.reach_goal_score: 0.691
- phase_breakdown.approach_object_score: 0.079
- phase_breakdown.grasp_lift_score: 0.164
- grasp_place_fitness: 0.833

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.833
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.735
- **Median Q (composite search score)**: 0.147
- **K-run variance**: 0.0131
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.383


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.48699,"average_solve_count":269.0,"average_success_count":269.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.arc_height":0.04682,"ascend_above_goal.ascent_speed":0.02889,"descend_1.descend_offset_z":0.00476,"descend_to_goal_height.descend_offset_z":-0.08713,"lift_1.lift_height":0.12104,"transport_over_goal.transport_speed":0.10534},"optimized_scores":{"best_composite_score":0.13423,"best_fitness_score":0.58423,"best_task_score":0.21261},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":610.0,"contact_point_centroid":[0.59109,0.19391,-0.00422],"force_p95":0.93244,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.93971,"mean_force":0.20895,"phase_index":6.0,"phase_name":"descend_to_goal_height","phase_type":"descend","tcp_position_centroid":[0.57839,0.17653,0.20849]},{"body_a":"world","body_b":"grasp_target","contact_count":80.0,"contact_point_centroid":[0.5008,-0.01325,-0.00145],"force_p95":0.59851,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.61882,"mean_force":0.1395,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48955,-0.01391,0.03213]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5031.0,"contact_point_centroid":[0.48912,0.0052,0.07806],"force_p95":0.10888,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33038,"mean_force":0.06689,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48721,-0.01387,0.07554]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5628.0,"contact_point_centroid":[0.48914,-0.03277,0.07659],"force_p95":0.10248,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31443,"mean_force":0.06178,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48722,-0.01387,0.07483]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3669.0,"contact_point_centroid":[0.53059,0.04595,0.2926],"force_p95":0.17068,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28204,"mean_force":0.10101,"phase_index":5.0,"phase_name":"transport_over_goal","phase_type":"approach","tcp_position_centroid":[0.5266,0.06412,0.29641]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3814.0,"contact_point_centroid":[0.53191,0.08543,0.291],"force_p95":0.1556,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25375,"mean_force":0.09664,"phase_index":5.0,"phase_name":"transport_over_goal","phase_type":"approach","tcp_position_centroid":[0.5281,0.06737,0.29485]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50388,-0.01535,-0.00216],"force_p95":0.16937,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24577,"mean_force":0.13502,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49204,-0.01393,0.03183]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4055.0,"contact_point_centroid":[0.49135,0.00533,0.03336],"force_p95":0.08302,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15245,"mean_force":0.05203,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49087,-0.01392,0.0306]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":9455.0,"contact_point_centroid":[0.4947,-0.02585,0.23199],"force_p95":0.10626,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15188,"mean_force":0.07499,"phase_index":4.0,"phase_name":"ascend_above_goal","phase_type":"lift","tcp_position_centroid":[0.4905,-0.00721,0.23115]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":9452.0,"contact_point_centroid":[0.4948,0.01144,0.23241],"force_p95":0.1065,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15014,"mean_force":0.07469,"phase_index":4.0,"phase_name":"ascend_above_goal","phase_type":"lift","tcp_position_centroid":[0.49054,-0.00717,0.23178]},{"body_a":"world","body_b":"grasp_target","contact_count":1064.0,"contact_point_centroid":[0.50382,-0.01567,-0.00188],"force_p95":0.1365,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12309,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49963,0.02184,0.24324]},{"body_a":"world","body_b":"grasp_target","contact_count":1844.0,"contact_point_centroid":[0.50382,-0.01567,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.4983,-0.00539,0.11158]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5292.0,"contact_point_centroid":[0.49101,-0.03308,0.03292],"force_p95":0.07211,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08429,"mean_force":0.04257,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49088,-0.01392,0.03061]},{"body_a":"left_finger","body_b":"right_finger","contact_count":465.0,"contact_point_centroid":[0.5796,0.17803,0.20067],"force_p95":0.0132,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01631,"mean_force":0.01085,"phase_index":6.0,"phase_name":"descend_to_goal_height","phase_type":"descend","tcp_position_centroid":[0.57902,0.17802,0.19832]}],"total_contact_groups":14},"final_pose_error":0.01482,"key_states":{"actual_goal_position":[0.58691,0.18745,0.24812],"final_object_position":[0.59109,0.19383,0.016],"final_tcp_position":[0.5812,0.18235,0.17367],"realised_goal_position":[0.58691,0.18745,0.24812],"realised_object_initial_position":[0.50382,-0.01567,0.03]},"phases":[{"n_steps":267.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.03],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.30942,"object_z_max":0.03,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"approach_object","tcp_end":[0.50018,0.00306,0.18516],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.16028,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":461.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"approach_object","tcp_end":[0.499,-0.01396,0.03927],"tcp_start":[0.50018,0.00306,0.18516],"tcp_to_object_dist_end":0.0142,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50373,-0.01397,0.02545],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31156,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","subtask_id":"grasp_lift","tcp_end":[0.49084,-0.01392,0.03057],"tcp_start":[0.499,-0.01396,0.03927],"tcp_to_object_dist_end":0.01387,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":320.0,"n_steps_budget":780.0,"object_pos_end":[0.50492,-0.01383,0.12293],"object_pos_start":[0.50373,-0.01397,0.02545],"object_to_goal_dist_end":0.25082,"object_to_goal_dist_start":0.31156,"object_z_max":0.12266,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","subtask_id":"grasp_lift","tcp_end":[0.48703,-0.01385,0.13199],"tcp_start":[0.49084,-0.01392,0.03057],"tcp_to_object_dist_end":0.02006,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":706.0,"n_steps_budget":1000.0,"object_pos_end":[0.50846,-0.001,0.31155],"object_pos_start":[0.50492,-0.01383,0.12293],"object_to_goal_dist_end":0.21376,"object_to_goal_dist_start":0.25082,"object_z_max":0.31128,"phase_name":"ascend_above_goal","phase_peak_obstacle_force":0.0,"phase_type":"lift","subtask_id":"reach_goal","tcp_end":[0.49718,-0.00091,0.33032],"tcp_start":[0.48703,-0.01385,0.13199],"tcp_to_object_dist_end":0.0219,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":484.0,"n_steps_budget":1000.0,"object_pos_end":[0.58846,0.18421,0.06277],"object_pos_start":[0.50846,-0.001,0.31155],"object_to_goal_dist_end":0.18539,"object_to_goal_dist_start":0.21376,"object_z_max":0.31172,"phase_name":"transport_over_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"reach_goal","tcp_end":[0.57677,0.17055,0.24758],"tcp_start":[0.49718,-0.00091,0.33032],"tcp_to_object_dist_end":0.18569,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":164.0,"n_steps_budget":1000.0,"object_pos_end":[0.59109,0.19383,0.016],"object_pos_start":[0.58846,0.18421,0.06277],"object_to_goal_dist_end":0.23224,"object_to_goal_dist_start":0.18539,"object_z_max":0.06277,"phase_name":"descend_to_goal_height","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"reach_goal","tcp_end":[0.5812,0.18235,0.17367],"tcp_start":[0.57677,0.17055,0.24758],"tcp_to_object_dist_end":0.1584,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.91089,"average_solve_count":202.0,"average_success_count":202.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.arc_height":0.08409,"ascend_above_goal.ascent_speed":0.14288,"descend_1.descend_offset_z":0.00866,"descend_to_goal_height.descend_offset_z":-0.10875,"lift_1.lift_height":0.2432,"transport_over_goal.transport_speed":0.12378},"optimized_scores":{"best_composite_score":0.14659,"best_fitness_score":0.59659,"best_task_score":0.24195},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":898.0,"contact_point_centroid":[0.50878,0.05217,-0.0034],"force_p95":0.66974,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.79687,"mean_force":0.18037,"phase_index":4.0,"phase_name":"ascend_above_goal","phase_type":"lift","tcp_position_centroid":[0.49618,0.01996,0.29796]},{"body_a":"world","body_b":"grasp_target","contact_count":72.0,"contact_point_centroid":[0.50961,0.03993,-0.00136],"force_p95":0.53279,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.56632,"mean_force":0.13043,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49815,0.03965,0.03533]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8441.0,"contact_point_centroid":[0.49917,0.05829,0.12362],"force_p95":0.12523,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33842,"mean_force":0.07894,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49574,0.03944,0.12199]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8988.0,"contact_point_centroid":[0.49913,0.02075,0.11773],"force_p95":0.12484,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30417,"mean_force":0.07401,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49575,0.03944,0.11634]},{"body_a":"world","body_b":"grasp_target","contact_count":1124.0,"contact_point_centroid":[0.51251,0.03972,-0.00188],"force_p95":0.13644,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12306,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50194,0.04414,0.25818]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.5125,0.0398,-0.00202],"force_p95":0.12859,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13572,"mean_force":0.12455,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.50056,0.03986,0.0354]},{"body_a":"world","body_b":"grasp_target","contact_count":2248.0,"contact_point_centroid":[0.50869,0.05197,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12264,"mean_force":0.12263,"phase_index":5.0,"phase_name":"transport_over_goal","phase_type":"approach","tcp_position_centroid":[0.55475,0.0813,0.23994]},{"body_a":"world","body_b":"grasp_target","contact_count":1860.0,"contact_point_centroid":[0.51251,0.03972,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.5062,0.0466,0.11756]},{"body_a":"world","body_b":"grasp_target","contact_count":884.0,"contact_point_centroid":[0.50869,0.05197,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"descend_to_goal_height","phase_type":"descend","tcp_position_centroid":[0.61595,0.16337,0.09964]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4130.0,"contact_point_centroid":[0.49988,0.05898,0.03681],"force_p95":0.07547,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09673,"mean_force":0.05177,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49938,0.03976,0.03413]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4864.0,"contact_point_centroid":[0.49998,0.0207,0.03604],"force_p95":0.06801,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08841,"mean_force":0.04465,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49938,0.03976,0.03413]},{"body_a":"left_finger","body_b":"right_finger","contact_count":780.0,"contact_point_centroid":[0.49675,0.01717,0.30643],"force_p95":0.01316,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01578,"mean_force":0.0108,"phase_index":4.0,"phase_name":"ascend_above_goal","phase_type":"lift","tcp_position_centroid":[0.49634,0.01716,0.30413]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2413.0,"contact_point_centroid":[0.5549,0.08096,0.24258],"force_p95":0.01097,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01285,"mean_force":0.01039,"phase_index":5.0,"phase_name":"transport_over_goal","phase_type":"approach","tcp_position_centroid":[0.55448,0.08094,0.24035]},{"body_a":"left_finger","body_b":"right_finger","contact_count":941.0,"contact_point_centroid":[0.61638,0.16342,0.10157],"force_p95":0.01099,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01102,"mean_force":0.01047,"phase_index":6.0,"phase_name":"descend_to_goal_height","phase_type":"descend","tcp_position_centroid":[0.61597,0.1634,0.09933]}],"total_contact_groups":14},"final_pose_error":0.01464,"key_states":{"actual_goal_position":[0.62757,0.17252,0.14502],"final_object_position":[0.50869,0.05197,0.01602],"final_tcp_position":[0.62023,0.16864,0.04834],"realised_goal_position":[0.62757,0.17252,0.14502],"realised_object_initial_position":[0.51251,0.03972,0.03]},"phases":[{"n_steps":282.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.03],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21001,"object_z_max":0.03,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"approach_object","tcp_end":[0.50748,0.05295,0.19404],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.16862,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":465.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"approach_object","tcp_end":[0.50755,0.04049,0.04314],"tcp_start":[0.50748,0.05295,0.19404],"tcp_to_object_dist_end":0.01784,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51239,0.03993,0.02591],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21221,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","subtask_id":"grasp_lift","tcp_end":[0.49935,0.03976,0.03409],"tcp_start":[0.50755,0.04049,0.04314],"tcp_to_object_dist_end":0.01539,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":713.0,"n_steps_budget":1000.0,"object_pos_end":[0.51363,0.0489,0.11669],"object_pos_start":[0.51239,0.03993,0.02591],"object_to_goal_dist_end":0.17049,"object_to_goal_dist_start":0.21221,"object_z_max":0.21114,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","subtask_id":"grasp_lift","tcp_end":[0.49659,0.03951,0.2575],"tcp_start":[0.49935,0.03976,0.03409],"tcp_to_object_dist_end":0.14215,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":255.0,"n_steps_budget":600.0,"object_pos_end":[0.50869,0.05197,0.01602],"object_pos_start":[0.51363,0.0489,0.11669],"object_to_goal_dist_end":0.21285,"object_to_goal_dist_start":0.17049,"object_z_max":0.11669,"phase_name":"ascend_above_goal","phase_peak_obstacle_force":0.0,"phase_type":"lift","subtask_id":"reach_goal","tcp_end":[0.49753,0.00547,0.3312],"tcp_start":[0.49659,0.03951,0.2575],"tcp_to_object_dist_end":0.31879,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":562.0,"n_steps_budget":1000.0,"object_pos_end":[0.50869,0.05197,0.01602],"object_pos_start":[0.50869,0.05197,0.01602],"object_to_goal_dist_end":0.21285,"object_to_goal_dist_start":0.21285,"object_z_max":0.01602,"phase_name":"transport_over_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"reach_goal","tcp_end":[0.61421,0.15886,0.15091],"tcp_start":[0.49753,0.00547,0.3312],"tcp_to_object_dist_end":0.20188,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":221.0,"n_steps_budget":1000.0,"object_pos_end":[0.50869,0.05197,0.01602],"object_pos_start":[0.50869,0.05197,0.01602],"object_to_goal_dist_end":0.21285,"object_to_goal_dist_start":0.21285,"object_z_max":0.01602,"phase_name":"descend_to_goal_height","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"reach_goal","tcp_end":[0.62023,0.16864,0.04834],"tcp_start":[0.61421,0.15886,0.15091],"tcp_to_object_dist_end":0.16461,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.18551,"average_solve_count":345.0,"average_success_count":345.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.arc_height":0.05013,"ascend_above_goal.ascent_speed":0.03128,"descend_1.descend_offset_z":0.01788,"descend_to_goal_height.descend_offset_z":-0.02023,"lift_1.lift_height":0.11558,"transport_over_goal.transport_speed":0.04064},"optimized_scores":{"best_composite_score":0.38302,"best_fitness_score":0.83302,"best_task_score":0.73521},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":73.0,"contact_point_centroid":[0.48025,0.04827,-0.00132],"force_p95":0.41154,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.42983,"mean_force":0.10549,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46957,0.04847,0.04613]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":505.0,"contact_point_centroid":[0.57942,0.19543,0.22314],"force_p95":0.14288,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.37148,"mean_force":0.08744,"phase_index":6.0,"phase_name":"descend_to_goal_height","phase_type":"descend","tcp_position_centroid":[0.57315,0.2139,0.22473]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":457.0,"contact_point_centroid":[0.57922,0.23237,0.22292],"force_p95":0.1546,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.35819,"mean_force":0.0961,"phase_index":6.0,"phase_name":"descend_to_goal_height","phase_type":"descend","tcp_position_centroid":[0.57309,0.21376,0.225]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5798.0,"contact_point_centroid":[0.4683,0.02919,0.09304],"force_p95":0.09315,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29306,"mean_force":0.05695,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46729,0.04823,0.09039]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5748.0,"contact_point_centroid":[0.46811,0.06742,0.09023],"force_p95":0.1003,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28961,"mean_force":0.05794,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46735,0.04824,0.0876]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":9495.0,"contact_point_centroid":[0.48358,0.00646,0.23525],"force_p95":0.10584,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19272,"mean_force":0.07176,"phase_index":4.0,"phase_name":"ascend_above_goal","phase_type":"lift","tcp_position_centroid":[0.48014,0.02516,0.23531]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":9826.0,"contact_point_centroid":[0.48364,0.04469,0.23221],"force_p95":0.09892,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1918,"mean_force":0.06996,"phase_index":4.0,"phase_name":"ascend_above_goal","phase_type":"lift","tcp_position_centroid":[0.47954,0.02602,0.23161]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.48269,0.04871,-0.00202],"force_p95":0.12939,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.15244,"mean_force":0.12467,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47186,0.04871,0.04599]},{"body_a":"world","body_b":"grasp_target","contact_count":1148.0,"contact_point_centroid":[0.4827,0.04873,-0.00188],"force_p95":0.13644,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12305,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49293,0.04777,0.26069]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":7567.0,"contact_point_centroid":[0.53976,0.08938,0.27759],"force_p95":0.10361,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12897,"mean_force":0.07695,"phase_index":5.0,"phase_name":"transport_over_goal","phase_type":"approach","tcp_position_centroid":[0.53401,0.10806,0.27783]},{"body_a":"world","body_b":"grasp_target","contact_count":1784.0,"contact_point_centroid":[0.4827,0.04873,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.47943,0.05502,0.12332]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":7642.0,"contact_point_centroid":[0.5399,0.12688,0.27729],"force_p95":0.09914,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11058,"mean_force":0.07529,"phase_index":5.0,"phase_name":"transport_over_goal","phase_type":"approach","tcp_position_centroid":[0.53407,0.10822,0.27776]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5388.0,"contact_point_centroid":[0.4701,0.06783,0.04789],"force_p95":0.06347,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08358,"mean_force":0.04099,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47076,0.0486,0.04485]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5033.0,"contact_point_centroid":[0.4704,0.02936,0.04788],"force_p95":0.06941,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0765,"mean_force":0.04339,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47076,0.0486,0.04485]}],"total_contact_groups":14},"final_pose_error":0.01484,"key_states":{"actual_goal_position":[0.58187,0.22885,0.23048],"final_object_position":[0.58229,0.21821,0.18559],"final_tcp_position":[0.57476,0.21794,0.21736],"realised_goal_position":[0.58187,0.22885,0.23048],"realised_object_initial_position":[0.4827,0.04873,0.03]},"phases":[{"n_steps":288.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.03],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28719,"object_z_max":0.03,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"approach_object","tcp_end":[0.48288,0.06087,0.19529],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.16971,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":446.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"approach_object","tcp_end":[0.47847,0.04941,0.05293],"tcp_start":[0.48288,0.06087,0.19529],"tcp_to_object_dist_end":0.02725,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.48261,0.04852,0.0259],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.29022,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","subtask_id":"grasp_lift","tcp_end":[0.47073,0.0486,0.04482],"tcp_start":[0.47847,0.04941,0.05293],"tcp_to_object_dist_end":0.02234,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":298.0,"n_steps_budget":750.0,"object_pos_end":[0.48248,0.04847,0.1196],"object_pos_start":[0.48261,0.04852,0.0259],"object_to_goal_dist_end":0.23391,"object_to_goal_dist_start":0.29022,"object_z_max":0.11933,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","subtask_id":"grasp_lift","tcp_end":[0.46712,0.04822,0.141],"tcp_start":[0.47073,0.0486,0.04482],"tcp_to_object_dist_end":0.02633,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":693.0,"n_steps_budget":1000.0,"object_pos_end":[0.50312,0.00326,0.30275],"object_pos_start":[0.48248,0.04847,0.1196],"object_to_goal_dist_end":0.24963,"object_to_goal_dist_start":0.23391,"object_z_max":0.30249,"phase_name":"ascend_above_goal","phase_peak_obstacle_force":0.0,"phase_type":"lift","subtask_id":"reach_goal","tcp_end":[0.49592,0.00303,0.33086],"tcp_start":[0.46712,0.04822,0.141],"tcp_to_object_dist_end":0.02902,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":612.0,"n_steps_budget":1000.0,"object_pos_end":[0.57889,0.2108,0.19861],"object_pos_start":[0.50312,0.00326,0.30275],"object_to_goal_dist_end":0.03675,"object_to_goal_dist_start":0.24963,"object_z_max":0.30291,"phase_name":"transport_over_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"reach_goal","tcp_end":[0.57284,0.21107,0.23012],"tcp_start":[0.49592,0.00303,0.33086],"tcp_to_object_dist_end":0.03208,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":43.0,"n_steps_budget":1000.0,"object_pos_end":[0.58229,0.21821,0.18559],"object_pos_start":[0.57889,0.2108,0.19861],"object_to_goal_dist_end":0.04614,"object_to_goal_dist_start":0.03675,"object_z_max":0.19861,"phase_name":"descend_to_goal_height","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"reach_goal","tcp_end":[0.57476,0.21794,0.21736],"tcp_start":[0.57284,0.21107,0.23012],"tcp_to_object_dist_end":0.03265,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```