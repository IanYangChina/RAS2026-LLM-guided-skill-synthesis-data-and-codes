## Search State

- **Seed**: 6
- **Iteration**: 15 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 14 | approach → descend → grasp → lift → lift → approach → descend | arc_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 6 | 0.1899 | 0.33 | ❌ rejected |
| 13 | approach → descend → grasp → lift → approach → descend → release | arc_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 7 | 0.1252 | 0.30 | ❌ rejected |
| 12 | approach → descend → grasp → lift → approach → descend → release | arc_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 7 | 0.0977 | 0.24 | ❌ rejected |
| 11 | approach → descend → grasp → lift → lift → approach → descend | arc_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 6 | 0.2213 | 0.40 | ✅ accepted |
| 10 | approach → descend → grasp → lift → approach → release → retract | arc_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 5 | 0.2241 | 0.29 | ❌ rejected |

**Proposal policy**: task_score is 0.33 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.190) — your mutation base

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

- **Composite score**: 0.190
- **task_score** (E): 0.334
- **fitness_score**: 0.640  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Complexity Penalty**: 0.450

## Per-Phase Performance

| Phase | Normal Term. Rate | Mean Displacement (m) |
| ------- | ------------------- | ------------------------ |
| approach_1 | 1.00 | 0.1205 |
| descend_1 | 1.00 | 0.1464 |
| grasp_1 | 1.00 | 0.0118 |
| lift_1 | 1.00 | 0.0918 |
| ascend_above_goal | 1.00 | 0.2059 |
| transport_over_goal | 1.00 | 0.2385 |
| descend_to_goal_height | 1.00 | 0.1132 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end |
| --- | --- | --- | --- | --- | --- |
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.497, 0.040, 0.191) | (0.500, 0.024, 0.030)→(0.500, 0.024, 0.026) | 0.269→0.271 |
| descend_1 | descend | 1.00 / step_budget | (0.497, 0.040, 0.191)→(0.495, 0.025, 0.045) | (0.500, 0.024, 0.026)→(0.500, 0.024, 0.026) | 0.271→0.271 |
| grasp_1 | grasp | 1.00 / step_budget | (0.495, 0.025, 0.045)→(0.487, 0.025, 0.037) | (0.500, 0.024, 0.026)→(0.500, 0.025, 0.026) | 0.271→0.271 |
| lift_1 | lift | 1.00 / step_budget | (0.487, 0.025, 0.037)→(0.483, 0.025, 0.128) | (0.500, 0.025, 0.026)→(0.500, 0.025, 0.114) | 0.271→0.223 |
| ascend_above_goal | lift | 1.00 / step_budget | (0.483, 0.025, 0.128)→(0.497, 0.001, 0.330) | (0.500, 0.025, 0.114)→(0.506, 0.002, 0.308) | 0.223→0.243 |
| transport_over_goal | approach | 1.00 / step_budget | (0.497, 0.001, 0.330)→(0.588, 0.180, 0.209) | (0.506, 0.002, 0.308)→(0.596, 0.175, 0.108) | 0.243→0.105 |
| descend_to_goal_height | descend | 1.00 / step_budget | (0.588, 0.180, 0.209)→(0.593, 0.192, 0.097) | (0.596, 0.175, 0.108)→(0.594, 0.182, 0.033) | 0.105→0.176 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.522
- phase_score: 0.153
- phase_breakdown.reach_goal_score: 0.219
- phase_breakdown.approach_object_score: 0.059
- phase_breakdown.grasp_lift_score: 0.104
- grasp_place_fitness: 0.739

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.739
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.522
- **Median Q (composite search score)**: 0.152
- **K-run variance**: 0.0050
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.474


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.47893,"average_solve_count":261.0,"average_success_count":261.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.arc_height":0.04297,"ascend_above_goal.ascent_speed":0.05679,"descend_1.descend_offset_z":0.00951,"descend_to_goal_height.descend_offset_z":-0.11428,"lift_1.lift_height":0.10746,"transport_over_goal.transport_speed":0.06271},"optimized_scores":{"best_composite_score":0.12889,"best_fitness_score":0.57889,"best_task_score":0.20868},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":40.0,"contact_point_centroid":[0.59362,0.15103,-0.00696],"force_p95":1.50765,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.63415,"mean_force":1.09014,"phase_index":5.0,"phase_name":"transport_over_goal","phase_type":"approach","tcp_position_centroid":[0.57582,0.16855,0.24848]},{"body_a":"world","body_b":"grasp_target","contact_count":880.0,"contact_point_centroid":[0.5944,0.15095,-0.00328],"force_p95":0.32431,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.98629,"mean_force":0.13869,"phase_index":6.0,"phase_name":"descend_to_goal_height","phase_type":"descend","tcp_position_centroid":[0.5782,0.17636,0.19774]},{"body_a":"world","body_b":"grasp_target","contact_count":79.0,"contact_point_centroid":[0.5011,-0.01314,-0.00146],"force_p95":0.5316,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54996,"mean_force":0.12316,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48964,-0.01393,0.03671]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4601.0,"contact_point_centroid":[0.48892,0.00522,0.07784],"force_p95":0.10679,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32617,"mean_force":0.06471,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48735,-0.01389,0.07527]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5180.0,"contact_point_centroid":[0.48891,-0.03284,0.07662],"force_p95":0.0992,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30758,"mean_force":0.05939,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48735,-0.01389,0.07482]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2899.0,"contact_point_centroid":[0.52888,0.07554,0.29769],"force_p95":0.1771,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25899,"mean_force":0.12102,"phase_index":5.0,"phase_name":"transport_over_goal","phase_type":"approach","tcp_position_centroid":[0.52341,0.05733,0.29956]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50388,-0.01542,-0.00216],"force_p95":0.16831,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.23503,"mean_force":0.13451,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49211,-0.01395,0.03645]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3647.0,"contact_point_centroid":[0.53071,0.04376,0.29499],"force_p95":0.14079,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22319,"mean_force":0.09937,"phase_index":5.0,"phase_name":"transport_over_goal","phase_type":"approach","tcp_position_centroid":[0.52538,0.06159,0.29752]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":9578.0,"contact_point_centroid":[0.49498,0.01163,0.23107],"force_p95":0.10861,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17185,"mean_force":0.07546,"phase_index":4.0,"phase_name":"ascend_above_goal","phase_type":"lift","tcp_position_centroid":[0.4907,-0.00701,0.2302]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":9711.0,"contact_point_centroid":[0.49494,-0.02569,0.23028],"force_p95":0.10639,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17025,"mean_force":0.07477,"phase_index":4.0,"phase_name":"ascend_above_goal","phase_type":"lift","tcp_position_centroid":[0.49065,-0.00706,0.22929]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4071.0,"contact_point_centroid":[0.49139,0.00535,0.03798],"force_p95":0.08322,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15666,"mean_force":0.05216,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49095,-0.01394,0.03522]},{"body_a":"world","body_b":"grasp_target","contact_count":1020.0,"contact_point_centroid":[0.50382,-0.01567,-0.00187],"force_p95":0.13691,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12311,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49965,0.01959,0.24419]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50382,-0.01567,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49832,-0.00566,0.11455]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5528.0,"contact_point_centroid":[0.49073,-0.03308,0.03789],"force_p95":0.06984,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07621,"mean_force":0.0406,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49095,-0.01394,0.03523]},{"body_a":"left_finger","body_b":"right_finger","contact_count":787.0,"contact_point_centroid":[0.57889,0.17728,0.19171],"force_p95":0.01279,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01633,"mean_force":0.01082,"phase_index":6.0,"phase_name":"descend_to_goal_height","phase_type":"descend","tcp_position_centroid":[0.57854,0.17727,0.18952]}],"total_contact_groups":15},"final_pose_error":0.0149,"key_states":{"actual_goal_position":[0.58691,0.18745,0.24812],"final_object_position":[0.59443,0.15113,0.01602],"final_tcp_position":[0.58134,0.18305,0.14694],"realised_goal_position":[0.58691,0.18745,0.24812],"realised_object_initial_position":[0.50382,-0.01567,0.03]},"phases":[{"n_steps":256.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.03],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.30942,"object_z_max":0.03,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"approach_object","tcp_end":[0.50019,0.00257,0.18674],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.1618,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":450.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"approach_object","tcp_end":[0.49902,-0.01398,0.04389],"tcp_start":[0.50019,0.00257,0.18674],"tcp_to_object_dist_end":0.01858,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50376,-0.01412,0.02546],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31164,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","subtask_id":"grasp_lift","tcp_end":[0.49092,-0.01394,0.03519],"tcp_start":[0.49902,-0.01398,0.04389],"tcp_to_object_dist_end":0.01611,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":279.0,"n_steps_budget":690.0,"object_pos_end":[0.5038,-0.01396,0.11057],"object_pos_start":[0.50376,-0.01412,0.02546],"object_to_goal_dist_end":0.25766,"object_to_goal_dist_start":0.31164,"object_z_max":0.1103,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","subtask_id":"grasp_lift","tcp_end":[0.48705,-0.01388,0.12331],"tcp_start":[0.49092,-0.01394,0.03519],"tcp_to_object_dist_end":0.02104,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":724.0,"n_steps_budget":1000.0,"object_pos_end":[0.50672,-0.00101,0.30866],"object_pos_start":[0.5038,-0.01396,0.11057],"object_to_goal_dist_end":0.21357,"object_to_goal_dist_start":0.25766,"object_z_max":0.30839,"phase_name":"ascend_above_goal","phase_peak_obstacle_force":0.0,"phase_type":"lift","subtask_id":"reach_goal","tcp_end":[0.49721,-0.00089,0.33022],"tcp_start":[0.48705,-0.01388,0.12331],"tcp_to_object_dist_end":0.02357,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":508.0,"n_steps_budget":1000.0,"object_pos_end":[0.59462,0.15384,-0.00392],"object_pos_start":[0.50672,-0.00101,0.30866],"object_to_goal_dist_end":0.25438,"object_to_goal_dist_start":0.21357,"object_z_max":0.30883,"phase_name":"transport_over_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"reach_goal","tcp_end":[0.57667,0.17037,0.24765],"tcp_start":[0.49721,-0.00089,0.33022],"tcp_to_object_dist_end":0.25275,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":220.0,"n_steps_budget":1000.0,"object_pos_end":[0.59443,0.15113,0.01602],"object_pos_start":[0.59462,0.15384,-0.00392],"object_to_goal_dist_end":0.23504,"object_to_goal_dist_start":0.25438,"object_z_max":0.01684,"phase_name":"descend_to_goal_height","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"reach_goal","tcp_end":[0.58134,0.18305,0.14694],"tcp_start":[0.57667,0.17037,0.24765],"tcp_to_object_dist_end":0.13539,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.53358,"average_solve_count":268.0,"average_success_count":268.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.arc_height":0.07245,"ascend_above_goal.ascent_speed":0.02099,"descend_1.descend_offset_z":0.00436,"descend_to_goal_height.descend_offset_z":-0.0873,"lift_1.lift_height":0.10795,"transport_over_goal.transport_speed":0.13375},"optimized_scores":{"best_composite_score":0.289,"best_fitness_score":0.739,"best_task_score":0.52156},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":74.0,"contact_point_centroid":[0.50906,0.04001,-0.00134],"force_p95":0.59609,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.63358,"mean_force":0.14051,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49806,0.0398,0.03115]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4547.0,"contact_point_centroid":[0.49734,0.0587,0.07297],"force_p95":0.10533,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.34225,"mean_force":0.06627,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.4956,0.03959,0.07057]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2730.0,"contact_point_centroid":[0.61637,0.14434,0.10866],"force_p95":0.1202,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31039,"mean_force":0.0744,"phase_index":6.0,"phase_name":"descend_to_goal_height","phase_type":"descend","tcp_position_centroid":[0.6163,0.16355,0.10739]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5150.0,"contact_point_centroid":[0.49742,0.02073,0.07122],"force_p95":0.09895,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30386,"mean_force":0.05948,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49563,0.03959,0.06945]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3557.0,"contact_point_centroid":[0.61695,0.18201,0.1102],"force_p95":0.09757,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27703,"mean_force":0.05675,"phase_index":6.0,"phase_name":"descend_to_goal_height","phase_type":"descend","tcp_position_centroid":[0.61614,0.16332,0.1095]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":7698.0,"contact_point_centroid":[0.55756,0.06351,0.23658],"force_p95":0.11807,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24487,"mean_force":0.07597,"phase_index":5.0,"phase_name":"transport_over_goal","phase_type":"approach","tcp_position_centroid":[0.55708,0.0826,0.23607]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":10340.0,"contact_point_centroid":[0.56008,0.10319,0.23432],"force_p95":0.10197,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23921,"mean_force":0.05785,"phase_index":5.0,"phase_name":"transport_over_goal","phase_type":"approach","tcp_position_centroid":[0.55851,0.08455,0.23382]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.5125,0.03983,-0.00203],"force_p95":0.13137,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.15426,"mean_force":0.12519,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.5005,0.04001,0.03115]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":10030.0,"contact_point_centroid":[0.49939,0.0387,0.227],"force_p95":0.10358,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15202,"mean_force":0.07563,"phase_index":4.0,"phase_name":"ascend_above_goal","phase_type":"lift","tcp_position_centroid":[0.49482,0.02012,0.22602]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":9570.0,"contact_point_centroid":[0.49824,0.00236,0.22125],"force_p95":0.11497,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14584,"mean_force":0.08003,"phase_index":4.0,"phase_name":"ascend_above_goal","phase_type":"lift","tcp_position_centroid":[0.49469,0.02104,0.22066]},{"body_a":"world","body_b":"grasp_target","contact_count":1216.0,"contact_point_centroid":[0.51251,0.03972,-0.00189],"force_p95":0.13606,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12303,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50177,0.04873,0.25921]},{"body_a":"world","body_b":"grasp_target","contact_count":1892.0,"contact_point_centroid":[0.51251,0.03972,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50625,0.04773,0.11435]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4114.0,"contact_point_centroid":[0.49985,0.05913,0.03255],"force_p95":0.07601,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11474,"mean_force":0.05187,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49932,0.03991,0.02987]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4884.0,"contact_point_centroid":[0.49993,0.02085,0.03178],"force_p95":0.0679,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08694,"mean_force":0.04461,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49932,0.03991,0.02987]}],"total_contact_groups":14},"final_pose_error":0.01466,"key_states":{"actual_goal_position":[0.62757,0.17252,0.14502],"final_object_position":[0.61577,0.16792,0.04821],"final_tcp_position":[0.62002,0.1682,0.06953],"realised_goal_position":[0.62757,0.17252,0.14502],"realised_object_initial_position":[0.51251,0.03972,0.03]},"phases":[{"n_steps":305.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.03],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21001,"object_z_max":0.03,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"approach_object","tcp_end":[0.50759,0.05505,0.19173],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.16649,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":473.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"approach_object","tcp_end":[0.50754,0.04065,0.03887],"tcp_start":[0.50759,0.05505,0.19173],"tcp_to_object_dist_end":0.01381,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51238,0.04006,0.02588],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21215,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","subtask_id":"grasp_lift","tcp_end":[0.49929,0.03991,0.02984],"tcp_start":[0.50754,0.04065,0.03887],"tcp_to_object_dist_end":0.01367,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":284.0,"n_steps_budget":690.0,"object_pos_end":[0.51299,0.03975,0.11092],"object_pos_start":[0.51238,0.04006,0.02588],"object_to_goal_dist_end":0.17866,"object_to_goal_dist_start":0.21215,"object_z_max":0.11065,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","subtask_id":"grasp_lift","tcp_end":[0.49533,0.03957,0.11827],"tcp_start":[0.49929,0.03991,0.02984],"tcp_to_object_dist_end":0.01913,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":757.0,"n_steps_budget":1000.0,"object_pos_end":[0.50925,0.00218,0.31255],"object_pos_start":[0.51299,0.03975,0.11092],"object_to_goal_dist_end":0.26661,"object_to_goal_dist_start":0.17866,"object_z_max":0.31229,"phase_name":"ascend_above_goal","phase_peak_obstacle_force":0.0,"phase_type":"lift","subtask_id":"reach_goal","tcp_end":[0.49773,0.00227,0.33048],"tcp_start":[0.49533,0.03957,0.11827],"tcp_to_object_dist_end":0.02131,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":562.0,"n_steps_budget":1000.0,"object_pos_end":[0.61409,0.15875,0.12991],"object_pos_start":[0.50925,0.00218,0.31255],"object_to_goal_dist_end":0.02449,"object_to_goal_dist_start":0.26661,"object_z_max":0.31268,"phase_name":"transport_over_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"reach_goal","tcp_end":[0.61441,0.15894,0.15041],"tcp_start":[0.49773,0.00227,0.33048],"tcp_to_object_dist_end":0.02051,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":176.0,"n_steps_budget":1000.0,"object_pos_end":[0.61577,0.16792,0.04821],"object_pos_start":[0.61409,0.15875,0.12991],"object_to_goal_dist_end":0.09764,"object_to_goal_dist_start":0.02449,"object_z_max":0.12991,"phase_name":"descend_to_goal_height","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"reach_goal","tcp_end":[0.62002,0.1682,0.06953],"tcp_start":[0.61441,0.15894,0.15041],"tcp_to_object_dist_end":0.02174,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.28611,"average_solve_count":360.0,"average_success_count":360.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.arc_height":0.07795,"ascend_above_goal.ascent_speed":0.03394,"descend_1.descend_offset_z":0.01808,"descend_to_goal_height.descend_offset_z":-0.16931,"lift_1.lift_height":0.11827,"transport_over_goal.transport_speed":0.0381},"optimized_scores":{"best_composite_score":0.1517,"best_fitness_score":0.6017,"best_task_score":0.27274},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":72.0,"contact_point_centroid":[0.47995,0.04867,-0.00133],"force_p95":0.39547,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.48041,"mean_force":0.10196,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46955,0.04863,0.04621]},{"body_a":"world","body_b":"grasp_target","contact_count":4.0,"contact_point_centroid":[0.57404,0.21094,-0.00057],"force_p95":0.47515,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.47824,"mean_force":0.44241,"phase_index":6.0,"phase_name":"descend_to_goal_height","phase_type":"descend","tcp_position_centroid":[0.57629,0.22474,0.0755]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3688.0,"contact_point_centroid":[0.57606,0.23529,0.14883],"force_p95":0.1463,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.3706,"mean_force":0.09108,"phase_index":6.0,"phase_name":"descend_to_goal_height","phase_type":"descend","tcp_position_centroid":[0.57368,0.21762,0.1524]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3315.0,"contact_point_centroid":[0.57611,0.19878,0.15241],"force_p95":0.20039,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.36295,"mean_force":0.11577,"phase_index":6.0,"phase_name":"descend_to_goal_height","phase_type":"descend","tcp_position_centroid":[0.57357,0.21733,0.15565]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6002.0,"contact_point_centroid":[0.46847,0.02937,0.09338],"force_p95":0.09424,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29374,"mean_force":0.0568,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46728,0.0484,0.0909]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5769.0,"contact_point_centroid":[0.46818,0.06759,0.09231],"force_p95":0.09946,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29303,"mean_force":0.05863,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46733,0.0484,0.08946]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.48269,0.04876,-0.00202],"force_p95":0.22444,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.23357,"mean_force":0.16354,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47184,0.04887,0.04606]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":9305.0,"contact_point_centroid":[0.48391,0.00627,0.23771],"force_p95":0.10579,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17854,"mean_force":0.07191,"phase_index":4.0,"phase_name":"ascend_above_goal","phase_type":"lift","tcp_position_centroid":[0.48034,0.02497,0.23786]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":9411.0,"contact_point_centroid":[0.48413,0.04433,0.23563],"force_p95":0.09882,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17759,"mean_force":0.07144,"phase_index":4.0,"phase_name":"ascend_above_goal","phase_type":"lift","tcp_position_centroid":[0.47988,0.02564,0.23503]},{"body_a":"world","body_b":"grasp_target","contact_count":1216.0,"contact_point_centroid":[0.4827,0.04873,-0.00189],"force_p95":0.13606,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12303,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49306,0.05079,0.26178]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":7590.0,"contact_point_centroid":[0.53995,0.08977,0.27729],"force_p95":0.10556,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13042,"mean_force":0.07697,"phase_index":5.0,"phase_name":"transport_over_goal","phase_type":"approach","tcp_position_centroid":[0.53411,0.10845,0.27759]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":7674.0,"contact_point_centroid":[0.53992,0.12704,0.27709],"force_p95":0.09923,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12624,"mean_force":0.07514,"phase_index":5.0,"phase_name":"transport_over_goal","phase_type":"approach","tcp_position_centroid":[0.53409,0.10839,0.27762]},{"body_a":"world","body_b":"grasp_target","contact_count":1776.0,"contact_point_centroid":[0.4827,0.04873,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.47935,0.05604,0.12294]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5228.0,"contact_point_centroid":[0.4701,0.06804,0.04823],"force_p95":0.07342,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10817,"mean_force":0.05076,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47074,0.04876,0.04492]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5359.0,"contact_point_centroid":[0.47043,0.02954,0.04779],"force_p95":0.07234,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10277,"mean_force":0.04851,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47074,0.04876,0.04492]}],"total_contact_groups":15},"final_pose_error":0.01487,"key_states":{"actual_goal_position":[0.58187,0.22885,0.23048],"final_object_position":[0.57202,0.22618,0.03586],"final_tcp_position":[0.5763,0.22483,0.07437],"realised_goal_position":[0.58187,0.22885,0.23048],"realised_object_initial_position":[0.4827,0.04873,0.03]},"phases":[{"n_steps":305.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.03],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28719,"object_z_max":0.03,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"approach_object","tcp_end":[0.48268,0.06273,0.1942],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.16876,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":444.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"approach_object","tcp_end":[0.47845,0.04958,0.05299],"tcp_start":[0.48268,0.06273,0.1942],"tcp_to_object_dist_end":0.02732,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.48259,0.04869,0.02591],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.29012,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","subtask_id":"grasp_lift","tcp_end":[0.47071,0.04876,0.04489],"tcp_start":[0.47845,0.04958,0.05299],"tcp_to_object_dist_end":0.02239,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":306.0,"n_steps_budget":750.0,"object_pos_end":[0.48244,0.04866,0.12192],"object_pos_start":[0.48259,0.04869,0.02591],"object_to_goal_dist_end":0.23268,"object_to_goal_dist_start":0.29012,"object_z_max":0.12164,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","subtask_id":"grasp_lift","tcp_end":[0.46713,0.04838,0.14361],"tcp_start":[0.47071,0.04876,0.04489],"tcp_to_object_dist_end":0.02655,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":684.0,"n_steps_budget":1000.0,"object_pos_end":[0.50293,0.00333,0.30242],"object_pos_start":[0.48244,0.04866,0.12192],"object_to_goal_dist_end":0.24954,"object_to_goal_dist_start":0.23268,"object_z_max":0.30216,"phase_name":"ascend_above_goal","phase_peak_obstacle_force":0.0,"phase_type":"lift","subtask_id":"reach_goal","tcp_end":[0.49587,0.00311,0.33071],"tcp_start":[0.46713,0.04838,0.14361],"tcp_to_object_dist_end":0.02916,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":612.0,"n_steps_budget":1000.0,"object_pos_end":[0.57884,0.21107,0.19823],"object_pos_start":[0.50293,0.00333,0.30242],"object_to_goal_dist_end":0.03696,"object_to_goal_dist_start":0.24954,"object_z_max":0.30258,"phase_name":"transport_over_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"reach_goal","tcp_end":[0.57292,0.21129,0.23001],"tcp_start":[0.49587,0.00311,0.33071],"tcp_to_object_dist_end":0.03233,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":333.0,"n_steps_budget":1000.0,"object_pos_end":[0.57202,0.22618,0.03586],"object_pos_start":[0.57884,0.21107,0.19823],"object_to_goal_dist_end":0.19489,"object_to_goal_dist_start":0.03696,"object_z_max":0.19823,"phase_name":"descend_to_goal_height","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"reach_goal","tcp_end":[0.5763,0.22483,0.07437],"tcp_start":[0.57292,0.21129,0.23001],"tcp_to_object_dist_end":0.03876,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```