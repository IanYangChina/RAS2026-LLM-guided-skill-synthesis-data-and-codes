## Search State

- **Seed**: 6
- **Iteration**: 14 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 13 | approach → descend → grasp → lift → approach → descend → release | arc_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 7 | 0.1252 | 0.30 | ❌ rejected |
| 12 | approach → descend → grasp → lift → approach → descend → release | arc_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 7 | 0.0977 | 0.24 | ❌ rejected |
| 11 | approach → descend → grasp → lift → lift → approach → descend | arc_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 6 | 0.2213 | 0.40 | ✅ accepted |
| 10 | approach → descend → grasp → lift → approach → release → retract | arc_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 5 | 0.2241 | 0.29 | ❌ rejected |
| 9 | approach → descend → grasp → lift → approach | arc_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | 4 | 0.2215 | 0.24 | ❌ rejected |

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

## Current Skill (Q=0.125) — your mutation base

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

- **Composite score**: 0.125
- **task_score** (E): 0.298
- **fitness_score**: 0.625  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Complexity Penalty**: 0.500

## Per-Phase Performance

| Phase | Normal Term. Rate | Mean Displacement (m) |
| ------- | ------------------- | ------------------------ |
| approach_1 | 1.00 | 0.1209 |
| descend_1 | 1.00 | 0.1496 |
| grasp_1 | 1.00 | 0.0118 |
| lift_1 | 1.00 | 0.1324 |
| transport_over_goal | 0.00 | 0.0002 |
| descend_to_goal_height | 1.00 | 0.2231 |
| release_1 | 1.00 | 0.0246 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end |
| --- | --- | --- | --- | --- | --- |
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.497, 0.040, 0.190) | (0.500, 0.024, 0.030)→(0.500, 0.024, 0.026) | 0.269→0.271 |
| descend_1 | descend | 1.00 / step_budget | (0.497, 0.040, 0.190)→(0.495, 0.025, 0.041) | (0.500, 0.024, 0.026)→(0.500, 0.024, 0.026) | 0.271→0.271 |
| grasp_1 | grasp | 1.00 / step_budget | (0.495, 0.025, 0.041)→(0.487, 0.025, 0.033) | (0.500, 0.024, 0.026)→(0.500, 0.025, 0.026) | 0.271→0.271 |
| lift_1 | lift | 1.00 / step_budget | (0.487, 0.025, 0.033)→(0.483, 0.025, 0.165) | (0.500, 0.025, 0.026)→(0.501, 0.025, 0.152) | 0.271→0.211 |
| transport_over_goal | approach | 0.00 / guard_failure | (0.483, 0.025, 0.165)→(0.484, 0.025, 0.165) | (0.501, 0.025, 0.152)→(0.501, 0.025, 0.153) | 0.211→0.211 |
| descend_to_goal_height | descend | 1.00 / step_budget | (0.484, 0.025, 0.165)→(0.590, 0.186, 0.087) | (0.502, 0.025, 0.153)→(0.586, 0.190, 0.004) | 0.211→0.205 |
| release_1 | release | 1.00 / step_budget | (0.590, 0.186, 0.087)→(0.585, 0.184, 0.111) | (0.586, 0.190, 0.004)→(0.586, 0.193, 0.020) | 0.205→0.190 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.442
- phase_score: 0.144
- phase_breakdown.reach_goal_score: 0.075
- phase_breakdown.approach_object_score: 0.070
- phase_breakdown.grasp_lift_score: 0.309
- grasp_place_fitness: 0.693

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.693
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.442
- **Median Q (composite search score)**: 0.100
- **K-run variance**: 0.0023
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.353


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.8705,"average_solve_count":139.0,"average_success_count":139.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.arc_height":0.07752,"descend_1.descend_offset_z":0.00672,"descend_to_goal_height.descend_offset_z":-0.10124,"lift_1.lift_height":0.15046,"release_1.release_duration":0.61182,"transport_over_goal.arc_height":0.05755,"transport_over_goal.transport_speed":0.04393},"optimized_scores":{"best_composite_score":0.08294,"best_fitness_score":0.58294,"best_task_score":0.21247},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":414.0,"contact_point_centroid":[0.58189,0.17727,-0.004],"force_p95":0.97026,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.38674,"mean_force":0.22503,"phase_index":5.0,"phase_name":"descend_to_goal_height","phase_type":"descend","tcp_position_centroid":[0.57308,0.16632,0.14107]},{"body_a":"world","body_b":"grasp_target","contact_count":80.0,"contact_point_centroid":[0.50084,-0.0133,-0.00145],"force_p95":0.56954,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.59127,"mean_force":0.13336,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48958,-0.01386,0.03403]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6086.0,"contact_point_centroid":[0.4897,0.00518,0.09222],"force_p95":0.11052,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32862,"mean_force":0.07072,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48723,-0.01382,0.08979]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6739.0,"contact_point_centroid":[0.48969,-0.03267,0.09031],"force_p95":0.10563,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31224,"mean_force":0.06578,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48724,-0.01382,0.08856]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5688.0,"contact_point_centroid":[0.52431,0.03781,0.15222],"force_p95":0.15939,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24632,"mean_force":0.10548,"phase_index":5.0,"phase_name":"descend_to_goal_height","phase_type":"descend","tcp_position_centroid":[0.51891,0.05624,0.15235]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50388,-0.01537,-0.00217],"force_p95":0.1704,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24422,"mean_force":0.13513,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49206,-0.01389,0.03374]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":7011.0,"contact_point_centroid":[0.52699,0.08047,0.15084],"force_p95":0.13772,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19803,"mean_force":0.08738,"phase_index":5.0,"phase_name":"descend_to_goal_height","phase_type":"descend","tcp_position_centroid":[0.52183,0.06231,0.15165]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3988.0,"contact_point_centroid":[0.4915,0.00539,0.03524],"force_p95":0.08342,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15265,"mean_force":0.05299,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.4909,-0.01387,0.03251]},{"body_a":"world","body_b":"grasp_target","contact_count":1076.0,"contact_point_centroid":[0.50382,-0.01567,-0.00188],"force_p95":0.1365,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12308,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49962,0.02257,0.24318]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.58219,0.17784,-0.00199],"force_p95":0.12375,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12726,"mean_force":0.12284,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.57387,0.17608,0.14129]},{"body_a":"world","body_b":"grasp_target","contact_count":1812.0,"contact_point_centroid":[0.50382,-0.01567,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49831,-0.00523,0.11234]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":25.0,"contact_point_centroid":[0.49269,-0.0324,0.1654],"force_p95":0.10195,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11641,"mean_force":0.082,"phase_index":4.0,"phase_name":"transport_over_goal","phase_type":"approach","tcp_position_centroid":[0.48732,-0.01381,0.1634]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":23.0,"contact_point_centroid":[0.49261,0.00482,0.16527],"force_p95":0.10988,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11626,"mean_force":0.08605,"phase_index":4.0,"phase_name":"transport_over_goal","phase_type":"approach","tcp_position_centroid":[0.48732,-0.01381,0.16339]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5415.0,"contact_point_centroid":[0.49086,-0.03301,0.03501],"force_p95":0.07096,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08365,"mean_force":0.04154,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.4909,-0.01387,0.03251]},{"body_a":"left_finger","body_b":"right_finger","contact_count":137.0,"contact_point_centroid":[0.57714,0.17373,0.1427],"force_p95":0.01589,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01636,"mean_force":0.01252,"phase_index":5.0,"phase_name":"descend_to_goal_height","phase_type":"descend","tcp_position_centroid":[0.57676,0.17373,0.14032]},{"body_a":"left_finger","body_b":"right_finger","contact_count":221.0,"contact_point_centroid":[0.57698,0.17716,0.13945],"force_p95":0.01106,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01133,"mean_force":0.01018,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.57677,0.17715,0.13708]}],"total_contact_groups":16},"final_pose_error":0.01497,"key_states":{"actual_goal_position":[0.58691,0.18745,0.24812],"final_object_position":[0.58219,0.17784,0.01602],"final_tcp_position":[0.57844,0.17723,0.13996],"realised_goal_position":[0.58691,0.18745,0.24812],"realised_object_initial_position":[0.50382,-0.01567,0.03]},"phases":[{"n_steps":270.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.03],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.30942,"object_z_max":0.03,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"approach_object","tcp_end":[0.50019,0.00335,0.18484],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.15999,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":453.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"approach_object","tcp_end":[0.499,-0.01391,0.04117],"tcp_start":[0.50019,0.00335,0.18484],"tcp_to_object_dist_end":0.016,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50375,-0.01399,0.02544],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31157,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","subtask_id":"grasp_lift","tcp_end":[0.49087,-0.01387,0.03248],"tcp_start":[0.499,-0.01391,0.04117],"tcp_to_object_dist_end":0.01467,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":412.0,"n_steps_budget":960.0,"object_pos_end":[0.50539,-0.01389,0.15055],"object_pos_start":[0.50375,-0.01399,0.02544],"object_to_goal_dist_end":0.23812,"object_to_goal_dist_start":0.31157,"object_z_max":0.15028,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","subtask_id":"grasp_lift","tcp_end":[0.48728,-0.01381,0.16331],"tcp_start":[0.49087,-0.01387,0.03248],"tcp_to_object_dist_end":0.02215,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":2.0,"n_steps_budget":1000.0,"object_pos_end":[0.50548,-0.01389,0.15071],"object_pos_start":[0.50539,-0.01389,0.15055],"object_to_goal_dist_end":0.23803,"object_to_goal_dist_start":0.23812,"object_z_max":0.15071,"phase_name":"transport_over_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"reach_goal","tcp_end":[0.48748,-0.01381,0.16361],"tcp_start":[0.48736,-0.01381,0.16349],"tcp_to_object_dist_end":0.02214,"terminated_normally":false,"termination_reason":"guard_failure"},{"n_steps":830.0,"n_steps_budget":1000.0,"object_pos_end":[0.58223,0.17803,0.01617],"object_pos_start":[0.50561,-0.0139,0.15079],"object_to_goal_dist_end":0.23219,"object_to_goal_dist_start":0.23795,"object_z_max":0.15081,"phase_name":"descend_to_goal_height","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"reach_goal","tcp_end":[0.57844,0.17723,0.13996],"tcp_start":[0.48748,-0.01381,0.16361],"tcp_to_object_dist_end":0.12385,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.58219,0.17784,0.01602],"object_pos_start":[0.58223,0.17803,0.01617],"object_to_goal_dist_end":0.23234,"object_to_goal_dist_start":0.23219,"object_z_max":0.01617,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","subtask_id":"reach_goal","tcp_end":[0.57215,0.17547,0.16123],"tcp_start":[0.57844,0.17723,0.13996],"tcp_to_object_dist_end":0.14558,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.04762,"average_solve_count":147.0,"average_success_count":147.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.arc_height":0.06129,"descend_1.descend_offset_z":0.01268,"descend_to_goal_height.descend_offset_z":-0.15765,"lift_1.lift_height":0.15495,"release_1.release_duration":0.58244,"transport_over_goal.arc_height":0.07201,"transport_over_goal.transport_speed":0.04699},"optimized_scores":{"best_composite_score":0.19297,"best_fitness_score":0.69297,"best_task_score":0.44204},"replay_outcomes":[{"contacts":{"omitted_contact_groups":5,"reported_contact_groups":[{"body_a":"world","body_b":"right_finger","contact_count":2988.0,"contact_point_centroid":[0.6118,0.17668,-0.00526],"force_p95":4.75955,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":6.73484,"mean_force":3.37827,"phase_index":5.0,"phase_name":"descend_to_goal_height","phase_type":"descend","tcp_position_centroid":[0.61199,0.15727,-0.00704]},{"body_a":"world","body_b":"left_finger","contact_count":2947.0,"contact_point_centroid":[0.61176,0.13743,-0.00504],"force_p95":4.6069,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":6.15851,"mean_force":3.27944,"phase_index":5.0,"phase_name":"descend_to_goal_height","phase_type":"descend","tcp_position_centroid":[0.61206,0.15732,-0.00714]},{"body_a":"world","body_b":"right_finger","contact_count":2787.0,"contact_point_centroid":[0.61941,0.18134,-0.00534],"force_p95":3.7945,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":3.94298,"mean_force":1.91786,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.61957,0.1615,-0.00705]},{"body_a":"world","body_b":"left_finger","contact_count":2705.0,"contact_point_centroid":[0.61926,0.14155,-0.00513],"force_p95":3.65268,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":3.7916,"mean_force":1.85168,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.61958,0.16151,-0.00734]},{"body_a":"world","body_b":"grasp_target","contact_count":1149.0,"contact_point_centroid":[0.58974,0.13572,-0.01303],"force_p95":1.52742,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.66157,"mean_force":0.95443,"phase_index":5.0,"phase_name":"descend_to_goal_height","phase_type":"descend","tcp_position_centroid":[0.59751,0.14477,0.01471]},{"body_a":"world","body_b":"grasp_target","contact_count":462.0,"contact_point_centroid":[0.6039,0.15922,-0.01382],"force_p95":1.3506,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.38273,"mean_force":0.76724,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.61903,0.16133,-0.00162]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":11347.0,"contact_point_centroid":[0.57013,0.09472,0.06096],"force_p95":0.34574,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.79821,"mean_force":0.14183,"phase_index":5.0,"phase_name":"descend_to_goal_height","phase_type":"descend","tcp_position_centroid":[0.56679,0.11372,0.06052]},{"body_a":"world","body_b":"grasp_target","contact_count":74.0,"contact_point_centroid":[0.50975,0.04056,-0.00136],"force_p95":0.49405,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.51033,"mean_force":0.1171,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.4982,0.03997,0.03942]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8031.0,"contact_point_centroid":[0.56206,0.12238,0.07427],"force_p95":0.16451,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.35339,"mean_force":0.09977,"phase_index":5.0,"phase_name":"descend_to_goal_height","phase_type":"descend","tcp_position_centroid":[0.55718,0.10414,0.07482]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6306.0,"contact_point_centroid":[0.49834,0.05878,0.10057],"force_p95":0.10925,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33121,"mean_force":0.07204,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49577,0.03977,0.09826]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":7006.0,"contact_point_centroid":[0.49836,0.02099,0.09809],"force_p95":0.10626,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29204,"mean_force":0.06617,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49579,0.03977,0.09634]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3252.0,"contact_point_centroid":[0.61886,0.14264,-0.00294],"force_p95":0.19114,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21758,"mean_force":0.09291,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.61943,0.16145,-0.00496]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3144.0,"contact_point_centroid":[0.61996,0.1806,-0.00317],"force_p95":0.15878,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19898,"mean_force":0.09037,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.61934,0.16141,-0.00335]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.51251,0.03983,-0.00204],"force_p95":0.13497,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.16475,"mean_force":0.12603,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.50063,0.04019,0.03942]},{"body_a":"world","body_b":"grasp_target","contact_count":1272.0,"contact_point_centroid":[0.51251,0.03972,-0.0019],"force_p95":0.13583,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12301,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50171,0.05161,0.25961]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":24.0,"contact_point_centroid":[0.50126,0.05846,0.17589],"force_p95":0.11467,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13088,"mean_force":0.08752,"phase_index":4.0,"phase_name":"transport_over_goal","phase_type":"approach","tcp_position_centroid":[0.49595,0.03978,0.17373]}],"total_contact_groups":21},"final_pose_error":0.01495,"key_states":{"actual_goal_position":[0.62757,0.17252,0.14502],"final_object_position":[0.59717,0.16129,0.02694],"final_tcp_position":[0.61784,0.16117,-0.0128],"realised_goal_position":[0.62757,0.17252,0.14502],"realised_object_initial_position":[0.51251,0.03972,0.03]},"phases":[{"n_steps":319.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.03],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21001,"object_z_max":0.03,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"approach_object","tcp_end":[0.50768,0.05592,0.19004],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.16489,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":442.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"approach_object","tcp_end":[0.50758,0.04083,0.04716],"tcp_start":[0.50768,0.05592,0.19004],"tcp_to_object_dist_end":0.02174,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51241,0.04018,0.02584],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21209,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","subtask_id":"grasp_lift","tcp_end":[0.49943,0.04009,0.0381],"tcp_start":[0.50758,0.04083,0.04716],"tcp_to_object_dist_end":0.01785,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":433.0,"n_steps_budget":960.0,"object_pos_end":[0.5125,0.03982,0.15569],"object_pos_start":[0.51241,0.04018,0.02584],"object_to_goal_dist_end":0.17596,"object_to_goal_dist_start":0.21209,"object_z_max":0.15543,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","subtask_id":"grasp_lift","tcp_end":[0.49591,0.03978,0.17364],"tcp_start":[0.49943,0.04009,0.0381],"tcp_to_object_dist_end":0.02444,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":2.0,"n_steps_budget":1000.0,"object_pos_end":[0.51258,0.03983,0.15585],"object_pos_start":[0.5125,0.03982,0.15569],"object_to_goal_dist_end":0.17592,"object_to_goal_dist_start":0.17596,"object_z_max":0.15585,"phase_name":"transport_over_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"reach_goal","tcp_end":[0.49611,0.0398,0.17392],"tcp_start":[0.49599,0.03979,0.17381],"tcp_to_object_dist_end":0.02446,"terminated_normally":false,"termination_reason":"guard_failure"},{"n_steps":865.0,"n_steps_budget":1000.0,"object_pos_end":[0.59829,0.15733,-0.01268],"object_pos_start":[0.5127,0.03984,0.15592],"object_to_goal_dist_end":0.16112,"object_to_goal_dist_start":0.17583,"object_z_max":0.15593,"phase_name":"descend_to_goal_height","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"reach_goal","tcp_end":[0.61784,0.16117,-0.0128],"tcp_start":[0.49611,0.0398,0.17392],"tcp_to_object_dist_end":0.01992,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.59717,0.16129,0.02694],"object_pos_start":[0.59829,0.15733,-0.01268],"object_to_goal_dist_end":0.12245,"object_to_goal_dist_start":0.16112,"object_z_max":0.02677,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","subtask_id":"reach_goal","tcp_end":[0.6159,0.16043,0.01651],"tcp_start":[0.61784,0.16117,-0.0128],"tcp_to_object_dist_end":0.02145,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.87234,"average_solve_count":141.0,"average_success_count":141.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.arc_height":0.04862,"descend_1.descend_offset_z":0.00083,"descend_to_goal_height.descend_offset_z":-0.08821,"lift_1.lift_height":0.15015,"release_1.release_duration":0.74248,"transport_over_goal.arc_height":0.02204,"transport_over_goal.transport_speed":0.06701},"optimized_scores":{"best_composite_score":0.09984,"best_fitness_score":0.59984,"best_task_score":0.23894},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":125.0,"contact_point_centroid":[0.57959,0.23723,-0.00688],"force_p95":1.13936,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.31209,"mean_force":0.47158,"phase_index":5.0,"phase_name":"descend_to_goal_height","phase_type":"descend","tcp_position_centroid":[0.57101,0.21641,0.13552]},{"body_a":"world","body_b":"grasp_target","contact_count":72.0,"contact_point_centroid":[0.47969,0.04868,-0.00133],"force_p95":0.62632,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.65796,"mean_force":0.15121,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46928,0.04827,0.02904]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6086.0,"contact_point_centroid":[0.46894,0.06711,0.0884],"force_p95":0.10817,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33698,"mean_force":0.06908,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46689,0.04803,0.08611]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6931.0,"contact_point_centroid":[0.46895,0.02922,0.08607],"force_p95":0.10332,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29691,"mean_force":0.06186,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46692,0.04803,0.0843]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8055.0,"contact_point_centroid":[0.51667,0.14162,0.14508],"force_p95":0.14046,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25043,"mean_force":0.08887,"phase_index":5.0,"phase_name":"descend_to_goal_height","phase_type":"descend","tcp_position_centroid":[0.51205,0.12342,0.14617]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":7254.0,"contact_point_centroid":[0.51564,0.10402,0.14546],"force_p95":0.15373,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22088,"mean_force":0.09418,"phase_index":5.0,"phase_name":"descend_to_goal_height","phase_type":"descend","tcp_position_centroid":[0.51147,0.12246,0.14632]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.57903,0.23923,-0.00217],"force_p95":0.12759,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.1678,"mean_force":0.11682,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.56835,0.21785,0.13642]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.48268,0.04872,-0.00202],"force_p95":0.12989,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.15153,"mean_force":0.12484,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47159,0.04852,0.02889]},{"body_a":"world","body_b":"grasp_target","contact_count":1132.0,"contact_point_centroid":[0.4827,0.04873,-0.00188],"force_p95":0.13644,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12306,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49291,0.04683,0.26053]},{"body_a":"world","body_b":"grasp_target","contact_count":2008.0,"contact_point_centroid":[0.4827,0.04873,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.47938,0.05469,0.11481]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":23.0,"contact_point_centroid":[0.47211,0.06675,0.1608],"force_p95":0.11249,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11363,"mean_force":0.08786,"phase_index":4.0,"phase_name":"transport_over_goal","phase_type":"approach","tcp_position_centroid":[0.46699,0.04803,0.15844]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":26.0,"contact_point_centroid":[0.47231,0.02957,0.1605],"force_p95":0.09938,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10151,"mean_force":0.07863,"phase_index":4.0,"phase_name":"transport_over_goal","phase_type":"approach","tcp_position_centroid":[0.46699,0.04803,0.15843]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4152.0,"contact_point_centroid":[0.47066,0.06771,0.02988],"force_p95":0.0762,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09359,"mean_force":0.05224,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47047,0.0484,0.02776]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5319.0,"contact_point_centroid":[0.47009,0.02938,0.03009],"force_p95":0.06367,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08737,"mean_force":0.0407,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47047,0.0484,0.02776]},{"body_a":"left_finger","body_b":"right_finger","contact_count":46.0,"contact_point_centroid":[0.57089,0.21866,0.13277],"force_p95":0.01616,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01616,"mean_force":0.01162,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.57018,0.21863,0.13038]}],"total_contact_groups":15},"final_pose_error":0.01486,"key_states":{"actual_goal_position":[0.58187,0.22885,0.23048],"final_object_position":[0.57902,0.23919,0.01602],"final_tcp_position":[0.57286,0.21942,0.13517],"realised_goal_position":[0.58187,0.22885,0.23048],"realised_object_initial_position":[0.4827,0.04873,0.03]},"phases":[{"n_steps":284.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.03],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28719,"object_z_max":0.03,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"approach_object","tcp_end":[0.48296,0.06043,0.19577],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.17015,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":502.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"approach_object","tcp_end":[0.47836,0.04924,0.03579],"tcp_start":[0.48296,0.06043,0.19577],"tcp_to_object_dist_end":0.0107,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.48257,0.04866,0.02589],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.29015,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","subtask_id":"grasp_lift","tcp_end":[0.47044,0.0484,0.02773],"tcp_start":[0.47836,0.04924,0.03579],"tcp_to_object_dist_end":0.01227,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":403.0,"n_steps_budget":960.0,"object_pos_end":[0.48614,0.04826,0.15106],"object_pos_start":[0.48257,0.04866,0.02589],"object_to_goal_dist_end":0.21929,"object_to_goal_dist_start":0.29015,"object_z_max":0.15079,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","subtask_id":"grasp_lift","tcp_end":[0.46695,0.04803,0.15834],"tcp_start":[0.47044,0.0484,0.02773],"tcp_to_object_dist_end":0.02052,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":2.0,"n_steps_budget":1000.0,"object_pos_end":[0.48623,0.04826,0.15123],"object_pos_start":[0.48614,0.04826,0.15106],"object_to_goal_dist_end":0.21918,"object_to_goal_dist_start":0.21929,"object_z_max":0.15123,"phase_name":"transport_over_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"reach_goal","tcp_end":[0.46714,0.04805,0.15865],"tcp_start":[0.46702,0.04804,0.15853],"tcp_to_object_dist_end":0.02049,"terminated_normally":false,"termination_reason":"guard_failure"},{"n_steps":819.0,"n_steps_budget":1000.0,"object_pos_end":[0.57782,0.23579,0.00798],"object_pos_start":[0.48638,0.04827,0.15132],"object_to_goal_dist_end":0.22265,"object_to_goal_dist_start":0.21909,"object_z_max":0.15133,"phase_name":"descend_to_goal_height","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"reach_goal","tcp_end":[0.57286,0.21942,0.13517],"tcp_start":[0.46714,0.04805,0.15865],"tcp_to_object_dist_end":0.12833,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.57902,0.23919,0.01602],"object_pos_start":[0.57782,0.23579,0.00798],"object_to_goal_dist_end":0.21473,"object_to_goal_dist_start":0.22265,"object_z_max":0.01655,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","subtask_id":"reach_goal","tcp_end":[0.56664,0.21711,0.15626],"tcp_start":[0.57286,0.21942,0.13517],"tcp_to_object_dist_end":0.14251,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```