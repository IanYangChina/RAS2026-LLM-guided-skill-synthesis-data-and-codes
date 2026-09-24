## Search State

- **Seed**: 6
- **Iteration**: 10 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 9 | approach → descend → grasp → lift → approach | arc_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | 4 | 0.2215 | 0.24 | ❌ rejected |
| 8 | approach → descend → grasp → lift → approach → release → retract | arc_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 5 | 0.2250 | 0.29 | ✅ accepted |
| 7 | approach → descend → grasp → lift → approach → descend → release → retract | arc_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 7 | 0.0617 | 0.24 | ❌ rejected |
| 6 | approach → descend → grasp → lift → push → release → retract | arc_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 5 | 0.2161 | 0.28 | ✅ accepted |
| 5 | align → lift → push → approach → approach → descend → grasp → rotate | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | arc_cartesian | linear_cartesian | — | impedance_motion | position_control | position_control | impedance_control | force_threshold_switch | position_control | admittance_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 6 | -0.1417 | 0.25 | ❌ rejected |

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
      default: 0.2
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
  subtask_id: grasp_lift
- id: transport_1
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
  parameters:
    release_duration:
      type: scalar
      range:
      - 0.1
      - 0.5
      default: 0.2
      binds_to:
      - path: duration.max_time
        mode: replace
  subtask_id: reach_goal
- id: retract_1
  type: retract
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: world
    offset:
    - 0.5
    - 0.0
    - 0.5
    tolerance: 0.05
    orientation:
      mode: keep_current

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
- **transport_1** (`approach`)
  - target: source=yaml, anchor=task_goal, entity=placement_surface, offset=[0.0, 0.0, 0.0], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - transport_speed: status=consumed; consumers=generator.speed (replace)
- **release_1** (`release`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings:
    - release_duration: status=consumed; consumers=duration.max_time (replace)
- **retract_1** (`retract`)
  - target: source=yaml, anchor=world, offset=[0.5, 0.0, 0.5], tolerance=0.05
  - orientation: mode=keep_current
  - parameter_bindings: none

## Design Metrics

- **Composite score**: 0.221
- **task_score** (E): 0.244
- **fitness_score**: 0.511  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Complexity Penalty**: 0.290

## Per-Phase Performance

| Phase | Normal Term. Rate | Mean Displacement (m) |
| ------- | ------------------- | ------------------------ |
| approach_1 | 1.00 | 0.1218 |
| descend_1 | 1.00 | 0.1451 |
| grasp_1 | 1.00 | 0.0118 |
| lift_1 | 1.00 | 0.2171 |
| transport_1 | 1.00 | 0.2049 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end |
| --- | --- | --- | --- | --- | --- |
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.497, 0.040, 0.189) | (0.500, 0.024, 0.030)→(0.500, 0.024, 0.026) | 0.269→0.271 |
| descend_1 | descend | 1.00 / step_budget | (0.497, 0.040, 0.189)→(0.495, 0.025, 0.045) | (0.500, 0.024, 0.026)→(0.500, 0.024, 0.026) | 0.271→0.271 |
| grasp_1 | grasp | 1.00 / step_budget | (0.495, 0.025, 0.045)→(0.487, 0.025, 0.036) | (0.500, 0.024, 0.026)→(0.500, 0.025, 0.026) | 0.271→0.271 |
| lift_1 | lift | 1.00 / step_budget | (0.487, 0.025, 0.036)→(0.484, 0.025, 0.254) | (0.500, 0.025, 0.026)→(0.500, 0.032, 0.139) | 0.271→0.232 |
| transport_1 | approach | 1.00 / step_budget | (0.484, 0.025, 0.254)→(0.590, 0.186, 0.207) | (0.500, 0.032, 0.139)→(0.545, 0.098, 0.015) | 0.232→0.228 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.404
- phase_score: 0.608
- phase_breakdown.reach_goal_score: 0.749
- phase_breakdown.approach_object_score: 0.081
- phase_breakdown.grasp_lift_score: 0.726
- grasp_place_fitness: 0.666

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.666
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.404
- **Median Q (composite search score)**: 0.289
- **K-run variance**: 0.0259
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.314


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.17219,"average_solve_count":151.0,"average_success_count":151.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.arc_height":0.07086,"descend_1.descend_offset_z":0.00922,"lift_1.lift_height":0.30398,"transport_1.transport_speed":0.15163},"optimized_scores":{"best_composite_score":-0.00035,"best_fitness_score":0.28965,"best_task_score":0.12989},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":569.0,"contact_point_centroid":[0.50103,0.00305,-0.00432],"force_p95":1.09769,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.13487,"mean_force":0.24195,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48867,-0.01377,0.2629]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8589.0,"contact_point_centroid":[0.49084,0.0051,0.12561],"force_p95":0.12792,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32705,"mean_force":0.0785,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48738,-0.01375,0.12386]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":9286.0,"contact_point_centroid":[0.4907,-0.03249,0.1218],"force_p95":0.12622,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30969,"mean_force":0.07418,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48737,-0.01375,0.12051]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50388,-0.01538,-0.00217],"force_p95":0.1715,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24175,"mean_force":0.13517,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.4921,-0.01382,0.03624]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3832.0,"contact_point_centroid":[0.49186,0.00548,0.03794],"force_p95":0.08565,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15435,"mean_force":0.05512,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49094,-0.0138,0.03501]},{"body_a":"world","body_b":"grasp_target","contact_count":1128.0,"contact_point_centroid":[0.50382,-0.01567,-0.00188],"force_p95":0.13644,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12306,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.4996,0.0251,0.24224]},{"body_a":"world","body_b":"grasp_target","contact_count":2656.0,"contact_point_centroid":[0.49968,0.00785,-0.00199],"force_p95":0.12269,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12573,"mean_force":0.12262,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.53362,0.08219,0.28164]},{"body_a":"world","body_b":"grasp_target","contact_count":1760.0,"contact_point_centroid":[0.50382,-0.01567,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49834,-0.0051,0.11264]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5525.0,"contact_point_centroid":[0.49074,-0.0329,0.03765],"force_p95":0.07053,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08124,"mean_force":0.04066,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49094,-0.0138,0.03501]},{"body_a":"left_finger","body_b":"right_finger","contact_count":410.0,"contact_point_centroid":[0.48895,-0.01377,0.3056],"force_p95":0.01393,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01606,"mean_force":0.01133,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48857,-0.01377,0.30345]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2820.0,"contact_point_centroid":[0.5343,0.08286,0.28367],"force_p95":0.01103,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01276,"mean_force":0.0105,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.53394,0.08286,0.2814]}],"total_contact_groups":11},"final_pose_error":0.01498,"key_states":{"actual_goal_position":[0.58691,0.18745,0.24812],"final_object_position":[0.49968,0.00785,0.01602],"final_tcp_position":[0.57886,0.17541,0.24927],"realised_goal_position":[0.58691,0.18745,0.24812],"realised_object_initial_position":[0.50382,-0.01567,0.03]},"phases":[{"n_steps":283.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.03],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.30942,"object_z_max":0.03,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"approach_object","tcp_end":[0.5002,0.00356,0.18303],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.15822,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":440.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"approach_object","tcp_end":[0.49901,-0.01384,0.04368],"tcp_start":[0.5002,0.00356,0.18303],"tcp_to_object_dist_end":0.0184,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50376,-0.01401,0.02544],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31158,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","subtask_id":"grasp_lift","tcp_end":[0.49091,-0.0138,0.03498],"tcp_start":[0.49901,-0.01384,0.04368],"tcp_to_object_dist_end":0.016,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":897.0,"n_steps_budget":1000.0,"object_pos_end":[0.49968,0.00798,0.01597],"object_pos_start":[0.50376,-0.01401,0.02544],"object_to_goal_dist_end":0.30612,"object_to_goal_dist_start":0.31158,"object_z_max":0.21861,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","subtask_id":"grasp_lift","tcp_end":[0.48877,-0.01378,0.31934],"tcp_start":[0.49091,-0.0138,0.03498],"tcp_to_object_dist_end":0.30435,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":664.0,"n_steps_budget":1000.0,"object_pos_end":[0.49968,0.00785,0.01602],"object_pos_start":[0.49968,0.00798,0.01597],"object_to_goal_dist_end":0.30616,"object_to_goal_dist_start":0.30612,"object_z_max":0.01602,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"reach_goal","tcp_end":[0.57886,0.17541,0.24927],"tcp_start":[0.48877,-0.01378,0.31934],"tcp_to_object_dist_end":0.29792,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.26891,"average_solve_count":119.0,"average_success_count":119.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.arc_height":0.06174,"descend_1.descend_offset_z":0.02025,"lift_1.lift_height":0.20324,"transport_1.transport_speed":0.24004},"optimized_scores":{"best_composite_score":0.37567,"best_fitness_score":0.66567,"best_task_score":0.40406},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":12.0,"contact_point_centroid":[0.62504,0.15026,-0.0023],"force_p95":1.28523,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.38672,"mean_force":1.01246,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.61575,0.16345,0.14636]},{"body_a":"world","body_b":"grasp_target","contact_count":75.0,"contact_point_centroid":[0.51016,0.04018,-0.00137],"force_p95":0.40647,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.42644,"mean_force":0.09532,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49833,0.04007,0.04689]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4575.0,"contact_point_centroid":[0.55625,0.07883,0.18538],"force_p95":0.1494,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.40747,"mean_force":0.10239,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.55077,0.09692,0.18911]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4150.0,"contact_point_centroid":[0.55484,0.11365,0.18622],"force_p95":0.16471,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.3848,"mean_force":0.11052,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.54934,0.09548,0.19]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8412.0,"contact_point_centroid":[0.49946,0.05884,0.12694],"force_p95":0.11157,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30398,"mean_force":0.07321,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49601,0.03987,0.12518]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":9328.0,"contact_point_centroid":[0.49943,0.02106,0.12565],"force_p95":0.10598,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27891,"mean_force":0.0671,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49601,0.03987,0.12394]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.51251,0.03979,-0.00205],"force_p95":0.13608,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.1739,"mean_force":0.12642,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.50074,0.04028,0.04687]},{"body_a":"world","body_b":"grasp_target","contact_count":1280.0,"contact_point_centroid":[0.51251,0.03972,-0.0019],"force_p95":0.13566,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12301,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50169,0.05184,0.25976]},{"body_a":"world","body_b":"grasp_target","contact_count":1676.0,"contact_point_centroid":[0.51251,0.03972,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50639,0.04839,0.12152]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4603.0,"contact_point_centroid":[0.50021,0.05941,0.04837],"force_p95":0.06885,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0973,"mean_force":0.04711,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49958,0.04019,0.04559]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5146.0,"contact_point_centroid":[0.50026,0.02102,0.0478],"force_p95":0.06522,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08236,"mean_force":0.04277,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49958,0.04019,0.04559]}],"total_contact_groups":11},"final_pose_error":0.01495,"key_states":{"actual_goal_position":[0.62757,0.17252,0.14502],"final_object_position":[0.62013,0.14761,0.0116],"final_tcp_position":[0.61606,0.1638,0.14612],"realised_goal_position":[0.62757,0.17252,0.14502],"realised_object_initial_position":[0.51251,0.03972,0.03]},"phases":[{"n_steps":321.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.03],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21001,"object_z_max":0.03,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"approach_object","tcp_end":[0.50769,0.05608,0.18998],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.16484,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":419.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"approach_object","tcp_end":[0.5076,0.04091,0.05463],"tcp_start":[0.50769,0.05608,0.18998],"tcp_to_object_dist_end":0.02905,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51243,0.04011,0.02581],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21214,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","subtask_id":"grasp_lift","tcp_end":[0.49955,0.04019,0.04556],"tcp_start":[0.5076,0.04091,0.05463],"tcp_to_object_dist_end":0.02357,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":587.0,"n_steps_budget":1000.0,"object_pos_end":[0.51142,0.04001,0.20239],"object_pos_start":[0.51243,0.04011,0.02581],"object_to_goal_dist_end":0.18532,"object_to_goal_dist_start":0.21214,"object_z_max":0.20214,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","subtask_id":"grasp_lift","tcp_end":[0.49651,0.03991,0.22925],"tcp_start":[0.49955,0.04019,0.04556],"tcp_to_object_dist_end":0.03072,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":561.0,"n_steps_budget":1000.0,"object_pos_end":[0.62013,0.14761,0.0116],"object_pos_start":[0.51142,0.04001,0.20239],"object_to_goal_dist_end":0.13593,"object_to_goal_dist_start":0.18532,"object_z_max":0.20264,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"reach_goal","tcp_end":[0.61606,0.1638,0.14612],"tcp_start":[0.49651,0.03991,0.22925],"tcp_to_object_dist_end":0.13555,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.06349,"average_solve_count":126.0,"average_success_count":126.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.arc_height":0.08579,"descend_1.descend_offset_z":0.00211,"lift_1.lift_height":0.20287,"transport_1.transport_speed":0.21819},"optimized_scores":{"best_composite_score":0.28914,"best_fitness_score":0.57914,"best_task_score":0.19815},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":1705.0,"contact_point_centroid":[0.51455,0.13715,-0.00267],"force_p95":0.28592,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.13884,"mean_force":0.15094,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.54237,0.17019,0.22134]},{"body_a":"world","body_b":"grasp_target","contact_count":72.0,"contact_point_centroid":[0.47969,0.0487,-0.00132],"force_p95":0.61237,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.6397,"mean_force":0.15069,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46929,0.04832,0.03025]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":7943.0,"contact_point_centroid":[0.46981,0.06708,0.11224],"force_p95":0.11185,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33726,"mean_force":0.07365,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46698,0.04808,0.11008]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1326.0,"contact_point_centroid":[0.48382,0.04978,0.20942],"force_p95":0.21455,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30856,"mean_force":0.12741,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.4786,0.06812,0.21168]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8869.0,"contact_point_centroid":[0.46981,0.02934,0.10905],"force_p95":0.10757,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29774,"mean_force":0.06707,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.467,0.04808,0.10734]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1671.0,"contact_point_centroid":[0.48557,0.08909,0.20902],"force_p95":0.18334,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26352,"mean_force":0.11071,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.48038,0.07117,0.21178]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.48268,0.04873,-0.00202],"force_p95":0.12892,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.14392,"mean_force":0.12464,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47163,0.04856,0.03008]},{"body_a":"world","body_b":"grasp_target","contact_count":1152.0,"contact_point_centroid":[0.4827,0.04873,-0.00189],"force_p95":0.13644,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12305,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49295,0.04787,0.2608]},{"body_a":"world","body_b":"grasp_target","contact_count":1988.0,"contact_point_centroid":[0.4827,0.04873,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.47934,0.05497,0.11515]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4149.0,"contact_point_centroid":[0.47068,0.06776,0.03104],"force_p95":0.07634,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0975,"mean_force":0.05223,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.4705,0.04845,0.02895]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5325.0,"contact_point_centroid":[0.47012,0.02943,0.03124],"force_p95":0.0634,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0869,"mean_force":0.04069,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.4705,0.04845,0.02895]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1607.0,"contact_point_centroid":[0.54666,0.17614,0.22433],"force_p95":0.01155,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01613,"mean_force":0.01057,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.54616,0.17612,0.222]}],"total_contact_groups":12},"final_pose_error":0.01493,"key_states":{"actual_goal_position":[0.58187,0.22885,0.23048],"final_object_position":[0.51441,0.13715,0.01602],"final_tcp_position":[0.5739,0.21981,0.22668],"realised_goal_position":[0.58187,0.22885,0.23048],"realised_object_initial_position":[0.4827,0.04873,0.03]},"phases":[{"n_steps":289.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.03],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28719,"object_z_max":0.03,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"approach_object","tcp_end":[0.48287,0.06095,0.19528],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.16971,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":497.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"approach_object","tcp_end":[0.47836,0.04928,0.03697],"tcp_start":[0.48287,0.06095,0.19528],"tcp_to_object_dist_end":0.01179,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.48257,0.04871,0.0259],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.29012,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","subtask_id":"grasp_lift","tcp_end":[0.47047,0.04845,0.02892],"tcp_start":[0.47836,0.04928,0.03697],"tcp_to_object_dist_end":0.01247,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":563.0,"n_steps_budget":1000.0,"object_pos_end":[0.4875,0.04827,0.19986],"object_pos_start":[0.48257,0.04871,0.0259],"object_to_goal_dist_end":0.20605,"object_to_goal_dist_start":0.29012,"object_z_max":0.19959,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","subtask_id":"grasp_lift","tcp_end":[0.46739,0.04812,0.21211],"tcp_start":[0.47047,0.04845,0.02892],"tcp_to_object_dist_end":0.02354,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":694.0,"n_steps_budget":1000.0,"object_pos_end":[0.51441,0.13715,0.01602],"object_pos_start":[0.4875,0.04827,0.19986],"object_to_goal_dist_end":0.24281,"object_to_goal_dist_start":0.20605,"object_z_max":0.2002,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"reach_goal","tcp_end":[0.5739,0.21981,0.22668],"tcp_start":[0.46739,0.04812,0.21211],"tcp_to_object_dist_end":0.23398,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```