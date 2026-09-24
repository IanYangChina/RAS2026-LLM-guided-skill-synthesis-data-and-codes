## Search State

- **Seed**: 6
- **Iteration**: 13 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 12 | approach → descend → grasp → lift → approach → descend → release | arc_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 7 | 0.0977 | 0.24 | ❌ rejected |
| 11 | approach → descend → grasp → lift → lift → approach → descend | arc_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 6 | 0.2213 | 0.40 | ✅ accepted |
| 10 | approach → descend → grasp → lift → approach → release → retract | arc_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 5 | 0.2241 | 0.29 | ❌ rejected |
| 9 | approach → descend → grasp → lift → approach | arc_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | 4 | 0.2215 | 0.24 | ❌ rejected |
| 8 | approach → descend → grasp → lift → approach → release → retract | arc_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 5 | 0.2250 | 0.29 | ✅ accepted |

**Proposal policy**: task_score is 0.24 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.098) — your mutation base

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

- **Composite score**: 0.098
- **task_score** (E): 0.242
- **fitness_score**: 0.598  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Complexity Penalty**: 0.500

## Per-Phase Performance

| Phase | Normal Term. Rate | Mean Displacement (m) |
| ------- | ------------------- | ------------------------ |
| approach_1 | 1.00 | 0.1180 |
| descend_1 | 1.00 | 0.1537 |
| grasp_1 | 1.00 | 0.0118 |
| lift_1 | 1.00 | 0.1021 |
| transport_over_goal | 0.67 | 0.2773 |
| descend_to_goal | 1.00 | 0.1732 |
| release_1 | 1.00 | 0.0207 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end |
| --- | --- | --- | --- | --- | --- |
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.497, 0.038, 0.193) | (0.500, 0.024, 0.030)→(0.500, 0.024, 0.026) | 0.269→0.271 |
| descend_1 | descend | 1.00 / step_budget | (0.497, 0.038, 0.193)→(0.495, 0.025, 0.040) | (0.500, 0.024, 0.026)→(0.500, 0.024, 0.026) | 0.271→0.271 |
| grasp_1 | grasp | 1.00 / step_budget | (0.495, 0.025, 0.040)→(0.487, 0.025, 0.031) | (0.500, 0.024, 0.026)→(0.500, 0.025, 0.026) | 0.271→0.271 |
| lift_1 | lift | 1.00 / step_budget | (0.487, 0.025, 0.031)→(0.483, 0.024, 0.134) | (0.500, 0.025, 0.026)→(0.501, 0.025, 0.124) | 0.271→0.219 |
| transport_over_goal | approach | 0.67 / step_budget | (0.483, 0.024, 0.134)→(0.586, 0.179, 0.337) | (0.501, 0.025, 0.124)→(0.546, 0.108, 0.118) | 0.219→0.184 |
| descend_to_goal | descend | 1.00 / step_budget | (0.586, 0.179, 0.337)→(0.594, 0.193, 0.165) | (0.546, 0.108, 0.118)→(0.546, 0.117, 0.057) | 0.184→0.182 |
| release_1 | release | 1.00 / step_budget | (0.594, 0.193, 0.165)→(0.588, 0.191, 0.185) | (0.546, 0.117, 0.057)→(0.543, 0.116, 0.019) | 0.182→0.220 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.321
- phase_score: 0.358
- phase_breakdown.reach_goal_score: 0.620
- phase_breakdown.approach_object_score: 0.060
- phase_breakdown.grasp_lift_score: 0.120
- grasp_place_fitness: 0.639

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.639
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.321
- **Median Q (composite search score)**: 0.100
- **K-run variance**: 0.0012
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.370


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.91667,"average_solve_count":180.0,"average_success_count":180.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.arc_height":0.02613,"descend_1.descend_offset_z":0.00033,"descend_to_goal.descend_place_z":-0.04431,"lift_1.lift_height":0.13739,"release_1.release_duration":0.71871,"transport_over_goal.arc_height":0.02188,"transport_over_goal.transport_speed":0.13072},"optimized_scores":{"best_composite_score":0.05474,"best_fitness_score":0.55474,"best_task_score":0.15073},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":2566.0,"contact_point_centroid":[0.51401,0.04112,-0.00241],"force_p95":0.14377,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.94587,"mean_force":0.14676,"phase_index":4.0,"phase_name":"transport_over_goal","phase_type":"approach","tcp_position_centroid":[0.5448,0.10589,0.31493]},{"body_a":"world","body_b":"grasp_target","contact_count":78.0,"contact_point_centroid":[0.50055,-0.01381,-0.0014],"force_p95":0.66905,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.69438,"mean_force":0.15634,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.4895,-0.01438,0.02762]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5605.0,"contact_point_centroid":[0.48935,0.00468,0.08062],"force_p95":0.10949,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33509,"mean_force":0.06922,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.4871,-0.01434,0.07817]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2630.0,"contact_point_centroid":[0.4992,0.02227,0.17562],"force_p95":0.17624,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32415,"mean_force":0.10205,"phase_index":4.0,"phase_name":"transport_over_goal","phase_type":"approach","tcp_position_centroid":[0.4934,0.0038,0.17586]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6222.0,"contact_point_centroid":[0.48939,-0.03319,0.07861],"force_p95":0.10452,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31766,"mean_force":0.06401,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48711,-0.01434,0.0769]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2608.0,"contact_point_centroid":[0.49917,-0.0146,0.1758],"force_p95":0.17791,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30571,"mean_force":0.1041,"phase_index":4.0,"phase_name":"transport_over_goal","phase_type":"approach","tcp_position_centroid":[0.49349,0.00389,0.17603]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50385,-0.01537,-0.00212],"force_p95":0.15815,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.23875,"mean_force":0.13215,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49199,-0.0144,0.02739]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4062.0,"contact_point_centroid":[0.4913,0.00481,0.02892],"force_p95":0.0804,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14234,"mean_force":0.05188,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49081,-0.01439,0.02617]},{"body_a":"world","body_b":"grasp_target","contact_count":864.0,"contact_point_centroid":[0.50382,-0.01567,-0.00185],"force_p95":0.13725,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12319,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49973,0.00962,0.24768]},{"body_a":"world","body_b":"grasp_target","contact_count":1984.0,"contact_point_centroid":[0.50382,-0.01567,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49829,-0.00788,0.11307]},{"body_a":"world","body_b":"grasp_target","contact_count":1372.0,"contact_point_centroid":[0.5136,0.04143,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.582,0.18061,0.30171]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.5136,0.04143,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.57976,0.18378,0.2184]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4987.0,"contact_point_centroid":[0.49136,-0.03354,0.02803],"force_p95":0.07212,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08678,"mean_force":0.04477,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49082,-0.01439,0.02617]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2564.0,"contact_point_centroid":[0.54723,0.10985,0.32189],"force_p95":0.01104,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01598,"mean_force":0.01054,"phase_index":4.0,"phase_name":"transport_over_goal","phase_type":"approach","tcp_position_centroid":[0.54683,0.10985,0.31961]},{"body_a":"left_finger","body_b":"right_finger","contact_count":219.0,"contact_point_centroid":[0.58236,0.18463,0.21627],"force_p95":0.01103,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01276,"mean_force":0.01014,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.58192,0.18461,0.21417]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1464.0,"contact_point_centroid":[0.5824,0.18062,0.30393],"force_p95":0.01099,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01257,"mean_force":0.01045,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.582,0.18061,0.30164]}],"total_contact_groups":16},"final_pose_error":0.01491,"key_states":{"actual_goal_position":[0.58691,0.18745,0.24812],"final_object_position":[0.5136,0.04143,0.01602],"final_tcp_position":[0.58354,0.1851,0.21813],"realised_goal_position":[0.58691,0.18745,0.24812],"realised_object_initial_position":[0.50382,-0.01567,0.03]},"phases":[{"n_steps":217.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.03],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.30942,"object_z_max":0.03,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"approach_object","tcp_end":[0.50026,-0.00133,0.19344],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.16807,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":496.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"approach_object","tcp_end":[0.49899,-0.01444,0.03482],"tcp_start":[0.50026,-0.00133,0.19344],"tcp_to_object_dist_end":0.01011,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50369,-0.01434,0.0256],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31171,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","subtask_id":"grasp_lift","tcp_end":[0.49078,-0.01439,0.02614],"tcp_start":[0.49899,-0.01444,0.03482],"tcp_to_object_dist_end":0.01292,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":372.0,"n_steps_budget":870.0,"object_pos_end":[0.50654,-0.01432,0.13821],"object_pos_start":[0.50369,-0.01434,0.0256],"object_to_goal_dist_end":0.24341,"object_to_goal_dist_start":0.31171,"object_z_max":0.13795,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","subtask_id":"grasp_lift","tcp_end":[0.48706,-0.01432,0.14414],"tcp_start":[0.49078,-0.01439,0.02614],"tcp_to_object_dist_end":0.02036,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":999.0,"n_steps_budget":1000.0,"object_pos_end":[0.5136,0.04143,0.01602],"object_pos_start":[0.50654,-0.01432,0.13821],"object_to_goal_dist_end":0.28384,"object_to_goal_dist_start":0.24341,"object_z_max":0.19179,"phase_name":"transport_over_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"reach_goal","tcp_end":[0.58092,0.17659,0.38264],"tcp_start":[0.48706,-0.01432,0.14414],"tcp_to_object_dist_end":0.3965,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":343.0,"n_steps_budget":1000.0,"object_pos_end":[0.5136,0.04143,0.01602],"object_pos_start":[0.5136,0.04143,0.01602],"object_to_goal_dist_end":0.28384,"object_to_goal_dist_start":0.28384,"object_z_max":0.01602,"phase_name":"descend_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"reach_goal","tcp_end":[0.58354,0.1851,0.21813],"tcp_start":[0.58092,0.17659,0.38264],"tcp_to_object_dist_end":0.25765,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.5136,0.04143,0.01602],"object_pos_start":[0.5136,0.04143,0.01602],"object_to_goal_dist_end":0.28384,"object_to_goal_dist_start":0.28384,"object_z_max":0.01602,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","subtask_id":"reach_goal","tcp_end":[0.57852,0.18328,0.23825],"tcp_start":[0.58354,0.1851,0.21813],"tcp_to_object_dist_end":0.27152,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.91071,"average_solve_count":168.0,"average_success_count":168.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.arc_height":0.09129,"descend_1.descend_offset_z":0.00512,"descend_to_goal.descend_place_z":-0.05181,"lift_1.lift_height":0.11426,"release_1.release_duration":0.4669,"transport_over_goal.arc_height":0.02033,"transport_over_goal.transport_speed":0.12012},"optimized_scores":{"best_composite_score":0.13854,"best_fitness_score":0.63854,"best_task_score":0.32137},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":1757.0,"contact_point_centroid":[0.55836,0.08566,-0.00255],"force_p95":0.26228,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.84476,"mean_force":0.15155,"phase_index":4.0,"phase_name":"transport_over_goal","phase_type":"approach","tcp_position_centroid":[0.57598,0.12255,0.2459]},{"body_a":"world","body_b":"grasp_target","contact_count":73.0,"contact_point_centroid":[0.50929,0.03959,-0.00134],"force_p95":0.58531,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.62241,"mean_force":0.14145,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49807,0.0395,0.0319]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4771.0,"contact_point_centroid":[0.49745,0.05838,0.07618],"force_p95":0.10606,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.34331,"mean_force":0.06724,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.4956,0.03929,0.0738]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5355.0,"contact_point_centroid":[0.49758,0.02045,0.07418],"force_p95":0.10064,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30142,"mean_force":0.06086,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49563,0.03929,0.07242]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2507.0,"contact_point_centroid":[0.51335,0.07291,0.15406],"force_p95":0.17456,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2841,"mean_force":0.10002,"phase_index":4.0,"phase_name":"transport_over_goal","phase_type":"approach","tcp_position_centroid":[0.50773,0.05421,0.15317]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2976.0,"contact_point_centroid":[0.51452,0.03682,0.15508],"force_p95":0.14857,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27602,"mean_force":0.0893,"phase_index":4.0,"phase_name":"transport_over_goal","phase_type":"approach","tcp_position_centroid":[0.50858,0.05511,0.15478]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.51249,0.03977,-0.00202],"force_p95":0.12939,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.1407,"mean_force":0.12451,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.5005,0.03971,0.03193]},{"body_a":"world","body_b":"grasp_target","contact_count":1084.0,"contact_point_centroid":[0.51251,0.03972,-0.00188],"force_p95":0.1365,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12308,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50204,0.04179,0.25754]},{"body_a":"world","body_b":"grasp_target","contact_count":1912.0,"contact_point_centroid":[0.51251,0.03972,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50616,0.04581,0.1162]},{"body_a":"world","body_b":"grasp_target","contact_count":1436.0,"contact_point_centroid":[0.55817,0.08571,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.61873,0.1663,0.195]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.55817,0.08571,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.61647,0.16847,0.10607]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4135.0,"contact_point_centroid":[0.49984,0.05883,0.03334],"force_p95":0.07526,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09272,"mean_force":0.05183,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49933,0.03961,0.03066]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4854.0,"contact_point_centroid":[0.49994,0.02056,0.03257],"force_p95":0.06856,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08861,"mean_force":0.04462,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49933,0.03961,0.03066]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1644.0,"contact_point_centroid":[0.58129,0.12737,0.25323],"force_p95":0.0115,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01634,"mean_force":0.01056,"phase_index":4.0,"phase_name":"transport_over_goal","phase_type":"approach","tcp_position_centroid":[0.58086,0.12736,0.25109]},{"body_a":"left_finger","body_b":"right_finger","contact_count":218.0,"contact_point_centroid":[0.62026,0.1695,0.10453],"force_p95":0.01104,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01277,"mean_force":0.01014,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.61967,0.16947,0.10234]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1532.0,"contact_point_centroid":[0.61916,0.16633,0.19705],"force_p95":0.01101,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01275,"mean_force":0.01045,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.61873,0.16631,0.1948]}],"total_contact_groups":16},"final_pose_error":0.01487,"key_states":{"actual_goal_position":[0.62757,0.17252,0.14502],"final_object_position":[0.55817,0.08571,0.01602],"final_tcp_position":[0.62202,0.1701,0.10679],"realised_goal_position":[0.62757,0.17252,0.14502],"realised_object_initial_position":[0.51251,0.03972,0.03]},"phases":[{"n_steps":272.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.03],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21001,"object_z_max":0.03,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"approach_object","tcp_end":[0.50743,0.05153,0.19478],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.16924,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":478.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"approach_object","tcp_end":[0.50753,0.04034,0.03966],"tcp_start":[0.50743,0.05153,0.19478],"tcp_to_object_dist_end":0.01453,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51238,0.0398,0.02591],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.2123,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","subtask_id":"grasp_lift","tcp_end":[0.4993,0.03961,0.03062],"tcp_start":[0.50753,0.04034,0.03966],"tcp_to_object_dist_end":0.01391,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":303.0,"n_steps_budget":720.0,"object_pos_end":[0.51309,0.03949,0.11685],"object_pos_start":[0.51238,0.0398,0.02591],"object_to_goal_dist_end":0.17776,"object_to_goal_dist_start":0.2123,"object_z_max":0.11658,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","subtask_id":"grasp_lift","tcp_end":[0.49539,0.03927,0.1253],"tcp_start":[0.4993,0.03961,0.03062],"tcp_to_object_dist_end":0.01961,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":780.0,"n_steps_budget":1000.0,"object_pos_end":[0.55817,0.08571,0.01602],"object_pos_start":[0.51309,0.03949,0.11685],"object_to_goal_dist_end":0.17028,"object_to_goal_dist_start":0.17776,"object_z_max":0.16598,"phase_name":"transport_over_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"reach_goal","tcp_end":[0.61693,0.16315,0.28105],"tcp_start":[0.49539,0.03927,0.1253],"tcp_to_object_dist_end":0.28229,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":359.0,"n_steps_budget":1000.0,"object_pos_end":[0.55817,0.08571,0.01602],"object_pos_start":[0.55817,0.08571,0.01602],"object_to_goal_dist_end":0.17028,"object_to_goal_dist_start":0.17028,"object_z_max":0.01602,"phase_name":"descend_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"reach_goal","tcp_end":[0.62202,0.1701,0.10679],"tcp_start":[0.61693,0.16315,0.28105],"tcp_to_object_dist_end":0.13942,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.55817,0.08571,0.01602],"object_pos_start":[0.55817,0.08571,0.01602],"object_to_goal_dist_end":0.17028,"object_to_goal_dist_start":0.17028,"object_z_max":0.01602,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","subtask_id":"reach_goal","tcp_end":[0.61451,0.16785,0.12558],"tcp_start":[0.62202,0.1701,0.10679],"tcp_to_object_dist_end":0.14807,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.58547,"average_solve_count":234.0,"average_success_count":234.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.arc_height":0.06494,"descend_1.descend_offset_z":0.01097,"descend_to_goal.descend_place_z":-0.07288,"lift_1.lift_height":0.11291,"release_1.release_duration":0.82154,"transport_over_goal.arc_height":0.02671,"transport_over_goal.transport_speed":0.05584},"optimized_scores":{"best_composite_score":0.09992,"best_fitness_score":0.59992,"best_task_score":0.25304},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":256.0,"contact_point_centroid":[0.55453,0.22175,-0.0054],"force_p95":0.94479,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.2669,"mean_force":0.27254,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.57053,0.22151,0.18098]},{"body_a":"world","body_b":"grasp_target","contact_count":72.0,"contact_point_centroid":[0.47989,0.04883,-0.00134],"force_p95":0.46838,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54972,"mean_force":0.11882,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46938,0.04873,0.03899]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":661.0,"contact_point_centroid":[0.57117,0.20414,0.16263],"force_p95":0.12474,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.34286,"mean_force":0.08049,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.57411,0.22316,0.16594]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4836.0,"contact_point_centroid":[0.4684,0.0677,0.08448],"force_p95":0.10294,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33104,"mean_force":0.06422,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46709,0.0485,0.08212]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5631.0,"contact_point_centroid":[0.46831,0.02961,0.08295],"force_p95":0.09227,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28697,"mean_force":0.05658,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46711,0.0485,0.08108]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":826.0,"contact_point_centroid":[0.57252,0.24171,0.16258],"force_p95":0.107,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28256,"mean_force":0.06848,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.57418,0.2232,0.16608]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5287.0,"contact_point_centroid":[0.56989,0.2285,0.24882],"force_p95":0.12858,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25252,"mean_force":0.07803,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.56851,0.21105,0.25079]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4072.0,"contact_point_centroid":[0.57051,0.19119,0.25555],"force_p95":0.18205,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24847,"mean_force":0.12504,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.56783,0.20992,0.25793]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.48269,0.04876,-0.00203],"force_p95":0.2269,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.23056,"mean_force":0.16325,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47168,0.04898,0.03884]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":11927.0,"contact_point_centroid":[0.50866,0.09127,0.24221],"force_p95":0.11396,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18142,"mean_force":0.07986,"phase_index":4.0,"phase_name":"transport_over_goal","phase_type":"approach","tcp_position_centroid":[0.50376,0.1098,0.24146]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":11658.0,"contact_point_centroid":[0.5104,0.13093,0.24609],"force_p95":0.1093,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1664,"mean_force":0.08086,"phase_index":4.0,"phase_name":"transport_over_goal","phase_type":"approach","tcp_position_centroid":[0.50539,0.1123,0.24514]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4753.0,"contact_point_centroid":[0.4704,0.06815,0.04009],"force_p95":0.07869,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13959,"mean_force":0.05499,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47058,0.04887,0.0377]},{"body_a":"world","body_b":"grasp_target","contact_count":1324.0,"contact_point_centroid":[0.4827,0.04873,-0.0019],"force_p95":0.13564,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.123,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49328,0.05619,0.26336]},{"body_a":"world","body_b":"grasp_target","contact_count":1840.0,"contact_point_centroid":[0.4827,0.04873,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.47904,0.05711,0.11787]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5357.0,"contact_point_centroid":[0.47018,0.02971,0.03992],"force_p95":0.06997,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10751,"mean_force":0.04799,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47058,0.04887,0.0377]}],"total_contact_groups":15},"final_pose_error":0.01498,"key_states":{"actual_goal_position":[0.58187,0.22885,0.23048],"final_object_position":[0.5563,0.22147,0.02608],"final_tcp_position":[0.57632,0.22391,0.17061],"realised_goal_position":[0.58187,0.22885,0.23048],"realised_object_initial_position":[0.4827,0.04873,0.03]},"phases":[{"n_steps":332.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.03],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28719,"object_z_max":0.03,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"approach_object","tcp_end":[0.48218,0.06476,0.19135],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.16611,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":460.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"approach_object","tcp_end":[0.47836,0.0497,0.04575],"tcp_start":[0.48218,0.06476,0.19135],"tcp_to_object_dist_end":0.02023,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.48261,0.04895,0.02587],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.28997,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","subtask_id":"grasp_lift","tcp_end":[0.47055,0.04887,0.03767],"tcp_start":[0.47836,0.0497,0.04575],"tcp_to_object_dist_end":0.01687,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":290.0,"n_steps_budget":720.0,"object_pos_end":[0.48306,0.04864,0.11654],"object_pos_start":[0.48261,0.04895,0.02587],"object_to_goal_dist_end":0.23499,"object_to_goal_dist_start":0.28997,"object_z_max":0.11627,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","subtask_id":"grasp_lift","tcp_end":[0.46688,0.04848,0.13113],"tcp_start":[0.47055,0.04887,0.03767],"tcp_to_object_dist_end":0.02179,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.56606,0.19646,0.32212],"object_pos_start":[0.48306,0.04864,0.11654],"object_to_goal_dist_end":0.09847,"object_to_goal_dist_start":0.23499,"object_z_max":0.32199,"phase_name":"transport_over_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"reach_goal","tcp_end":[0.56039,0.19673,0.34818],"tcp_start":[0.46688,0.04848,0.13113],"tcp_to_object_dist_end":0.02668,"terminated_normally":false,"termination_reason":"step_budget"},{"n_steps":389.0,"n_steps_budget":1000.0,"object_pos_end":[0.56693,0.22374,0.13882],"object_pos_start":[0.56606,0.19646,0.32212],"object_to_goal_dist_end":0.09301,"object_to_goal_dist_start":0.09847,"object_z_max":0.32213,"phase_name":"descend_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"reach_goal","tcp_end":[0.57632,0.22391,0.17061],"tcp_start":[0.56039,0.19673,0.34818],"tcp_to_object_dist_end":0.03315,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.5563,0.22147,0.02608],"object_pos_start":[0.56693,0.22374,0.13882],"object_to_goal_dist_end":0.20613,"object_to_goal_dist_start":0.09301,"object_z_max":0.13882,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","subtask_id":"reach_goal","tcp_end":[0.57046,0.22149,0.1906],"tcp_start":[0.57632,0.22391,0.17061],"tcp_to_object_dist_end":0.16513,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```