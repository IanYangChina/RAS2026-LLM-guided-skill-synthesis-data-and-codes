## Search State

- **Seed**: 6
- **Iteration**: 9 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 8 | approach → descend → grasp → lift → approach → release → retract | arc_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 5 | 0.2250 | 0.29 | ✅ accepted |
| 7 | approach → descend → grasp → lift → approach → descend → release → retract | arc_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 7 | 0.0617 | 0.24 | ❌ rejected |
| 6 | approach → descend → grasp → lift → push → release → retract | arc_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 5 | 0.2161 | 0.28 | ✅ accepted |
| 5 | align → lift → push → approach → approach → descend → grasp → rotate | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | arc_cartesian | linear_cartesian | — | impedance_motion | position_control | position_control | impedance_control | force_threshold_switch | position_control | admittance_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 6 | -0.1417 | 0.25 | ❌ rejected |
| 4 | approach → descend → grasp → approach → release → retract | linear_cartesian | linear_cartesian | — | arc_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | time_limit | pose_tolerance | 6 | -0.1449 | 0.17 | ❌ rejected |

**Proposal policy**: task_score is 0.29 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.225) — your mutation base

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

- **Composite score**: 0.225
- **task_score** (E): 0.291
- **fitness_score**: 0.625  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Complexity Penalty**: 0.400

## Per-Phase Performance

| Phase | Normal Term. Rate | Mean Displacement (m) |
| ------- | ------------------- | ------------------------ |
| approach_1 | 1.00 | 0.1181 |
| descend_1 | 1.00 | 0.1575 |
| grasp_1 | 1.00 | 0.0118 |
| lift_1 | 1.00 | 0.1263 |
| transport_1 | 1.00 | 0.2004 |
| release_1 | 1.00 | 0.0215 |
| retract_1 | 1.00 | 0.2993 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end |
| --- | --- | --- | --- | --- | --- |
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.497, 0.038, 0.193) | (0.500, 0.024, 0.030)→(0.500, 0.024, 0.026) | 0.269→0.271 |
| descend_1 | descend | 1.00 / step_budget | (0.497, 0.038, 0.193)→(0.495, 0.025, 0.036) | (0.500, 0.024, 0.026)→(0.500, 0.024, 0.026) | 0.271→0.271 |
| grasp_1 | grasp | 1.00 / step_budget | (0.495, 0.025, 0.036)→(0.487, 0.025, 0.027) | (0.500, 0.024, 0.026)→(0.500, 0.025, 0.026) | 0.271→0.271 |
| lift_1 | lift | 1.00 / step_budget | (0.487, 0.025, 0.027)→(0.483, 0.024, 0.153) | (0.500, 0.025, 0.026)→(0.503, 0.025, 0.146) | 0.271→0.210 |
| transport_1 | approach | 1.00 / step_budget | (0.483, 0.024, 0.153)→(0.588, 0.184, 0.197) | (0.503, 0.025, 0.146)→(0.595, 0.181, 0.164) | 0.210→0.047 |
| release_1 | release | 1.00 / step_budget | (0.588, 0.184, 0.197)→(0.583, 0.183, 0.218) | (0.595, 0.181, 0.164)→(0.595, 0.189, 0.016) | 0.047→0.192 |
| retract_1 | retract | 1.00 / step_budget | (0.583, 0.183, 0.218)→(0.512, 0.023, 0.458) | (0.595, 0.189, 0.016)→(0.594, 0.189, 0.016) | 0.192→0.192 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.423
- phase_score: 0.355
- phase_breakdown.reach_goal_score: 0.582
- phase_breakdown.approach_object_score: 0.058
- phase_breakdown.grasp_lift_score: 0.173
- grasp_place_fitness: 0.690

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.690
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.423
- **Median Q (composite search score)**: 0.200
- **K-run variance**: 0.0022
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.595


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.51095,"average_solve_count":274.0,"average_success_count":274.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.arc_height":0.09986,"descend_1.descend_offset_z":0.00024,"lift_1.lift_height":0.14877,"release_1.release_duration":0.46102,"transport_1.transport_speed":0.02183},"optimized_scores":{"best_composite_score":0.18509,"best_fitness_score":0.58509,"best_task_score":0.2115},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":545.0,"contact_point_centroid":[0.58743,0.16665,-0.0042],"force_p95":0.89466,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.85759,"mean_force":0.21651,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.5743,0.17406,0.23867]},{"body_a":"world","body_b":"grasp_target","contact_count":77.0,"contact_point_centroid":[0.50082,-0.01343,-0.00145],"force_p95":0.67437,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.69955,"mean_force":0.16084,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48949,-0.01412,0.02753]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5995.0,"contact_point_centroid":[0.48952,0.00492,0.08512],"force_p95":0.1109,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33451,"mean_force":0.07068,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48709,-0.01408,0.0827]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8068.0,"contact_point_centroid":[0.53115,0.05319,0.18795],"force_p95":0.13267,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32478,"mean_force":0.08829,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.52673,0.07154,0.18917]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6677.0,"contact_point_centroid":[0.48955,-0.03291,0.08329],"force_p95":0.10539,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32079,"mean_force":0.06525,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.4871,-0.01408,0.08157]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50387,-0.01533,-0.00215],"force_p95":0.16528,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24675,"mean_force":0.13407,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49197,-0.01415,0.02733]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":7649.0,"contact_point_centroid":[0.5329,0.09414,0.18955],"force_p95":0.13591,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22029,"mean_force":0.09041,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.52877,0.07574,0.19097]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4049.0,"contact_point_centroid":[0.49129,0.00508,0.02886],"force_p95":0.0815,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14867,"mean_force":0.05195,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.4908,-0.01413,0.0261]},{"body_a":"world","body_b":"grasp_target","contact_count":960.0,"contact_point_centroid":[0.50382,-0.01567,-0.00186],"force_p95":0.13692,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12314,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49967,0.01617,0.24546]},{"body_a":"world","body_b":"grasp_target","contact_count":1144.0,"contact_point_centroid":[0.58696,0.16664,-0.00199],"force_p95":0.12279,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12347,"mean_force":0.12263,"phase_index":6.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.54284,0.1006,0.35274]},{"body_a":"world","body_b":"grasp_target","contact_count":1936.0,"contact_point_centroid":[0.50382,-0.01567,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49828,-0.00633,0.11096]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5017.0,"contact_point_centroid":[0.49135,-0.0333,0.02796],"force_p95":0.07315,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08774,"mean_force":0.04474,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49081,-0.01413,0.02611]}],"total_contact_groups":12},"final_pose_error":0.04942,"key_states":{"actual_goal_position":[0.58691,0.18745,0.24812],"final_object_position":[0.58696,0.16664,0.01602],"final_tcp_position":[0.51176,0.02467,0.45882],"realised_goal_position":[0.58691,0.18745,0.24812],"realised_object_initial_position":[0.50382,-0.01567,0.03]},"phases":[{"n_steps":241.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.03],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.30942,"object_z_max":0.03,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"approach_object","tcp_end":[0.5002,0.00149,0.18904],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.16396,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":484.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"approach_object","tcp_end":[0.49898,-0.01418,0.03475],"tcp_start":[0.5002,0.00149,0.18904],"tcp_to_object_dist_end":0.0101,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.5037,-0.01411,0.02551],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31161,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","subtask_id":"grasp_lift","tcp_end":[0.49077,-0.01413,0.02607],"tcp_start":[0.49898,-0.01418,0.03475],"tcp_to_object_dist_end":0.01294,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":407.0,"n_steps_budget":930.0,"object_pos_end":[0.50696,-0.01402,0.14843],"object_pos_start":[0.5037,-0.01411,0.02551],"object_to_goal_dist_end":0.23858,"object_to_goal_dist_start":0.31161,"object_z_max":0.14816,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","subtask_id":"grasp_lift","tcp_end":[0.48713,-0.01407,0.15524],"tcp_start":[0.49077,-0.01413,0.02607],"tcp_to_object_dist_end":0.02097,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":757.0,"n_steps_budget":1000.0,"object_pos_end":[0.5862,0.16627,0.1806],"object_pos_start":[0.50696,-0.01402,0.14843],"object_to_goal_dist_end":0.07077,"object_to_goal_dist_start":0.23858,"object_z_max":0.20691,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"reach_goal","tcp_end":[0.57845,0.17516,0.23514],"tcp_start":[0.48713,-0.01407,0.15524],"tcp_to_object_dist_end":0.0558,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.58697,0.16662,0.016],"object_pos_start":[0.5862,0.16627,0.1806],"object_to_goal_dist_end":0.23305,"object_to_goal_dist_start":0.07077,"object_z_max":0.1806,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","subtask_id":"reach_goal","tcp_end":[0.574,0.17394,0.25635],"tcp_start":[0.57845,0.17516,0.23514],"tcp_to_object_dist_end":0.24082,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":286.0,"n_steps_budget":1000.0,"object_pos_end":[0.58696,0.16664,0.01602],"object_pos_start":[0.58697,0.16662,0.016],"object_to_goal_dist_end":0.23303,"object_to_goal_dist_start":0.23305,"object_z_max":0.01602,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","tcp_end":[0.51176,0.02467,0.45882],"tcp_start":[0.574,0.17394,0.25635],"tcp_to_object_dist_end":0.47105,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.03061,"average_solve_count":196.0,"average_success_count":196.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.arc_height":0.07505,"descend_1.descend_offset_z":0.00326,"lift_1.lift_height":0.13489,"release_1.release_duration":0.19061,"transport_1.transport_speed":0.14971},"optimized_scores":{"best_composite_score":0.29005,"best_fitness_score":0.69005,"best_task_score":0.42281},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":203.0,"contact_point_centroid":[0.61304,0.16682,-0.0055],"force_p95":1.11668,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.33799,"mean_force":0.37522,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.6072,0.15955,0.14725]},{"body_a":"world","body_b":"grasp_target","contact_count":72.0,"contact_point_centroid":[0.50949,0.03999,-0.00136],"force_p95":0.61891,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.65715,"mean_force":0.15321,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49805,0.03973,0.02989]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5475.0,"contact_point_centroid":[0.4978,0.05857,0.08223],"force_p95":0.1085,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.34415,"mean_force":0.07034,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49553,0.03952,0.07987]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6175.0,"contact_point_centroid":[0.49791,0.02073,0.08031],"force_p95":0.10412,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30666,"mean_force":0.06358,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49556,0.03953,0.0786]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5491.0,"contact_point_centroid":[0.56027,0.085,0.13964],"force_p95":0.12362,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24417,"mean_force":0.08913,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.55705,0.10389,0.13862]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1233.0,"contact_point_centroid":[0.6123,0.17996,0.13307],"force_p95":0.08643,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24295,"mean_force":0.05004,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.61163,0.16101,0.13323]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":871.0,"contact_point_centroid":[0.61434,0.14195,0.13484],"force_p95":0.09254,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22589,"mean_force":0.05732,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.61171,0.16104,0.13337]},{"body_a":"world","body_b":"grasp_target","contact_count":1528.0,"contact_point_centroid":[0.62668,0.16702,-0.00198],"force_p95":0.12869,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.19041,"mean_force":0.12262,"phase_index":6.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.5596,0.08929,0.3006]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6958.0,"contact_point_centroid":[0.56213,0.12374,0.13935],"force_p95":0.10355,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18628,"mean_force":0.06835,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.55844,0.10533,0.13853]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.51249,0.03982,-0.00202],"force_p95":0.13005,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.14686,"mean_force":0.12484,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.50048,0.03995,0.02995]},{"body_a":"world","body_b":"grasp_target","contact_count":1196.0,"contact_point_centroid":[0.51251,0.03972,-0.00189],"force_p95":0.13615,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12304,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50181,0.04762,0.25894]},{"body_a":"world","body_b":"grasp_target","contact_count":1912.0,"contact_point_centroid":[0.51251,0.03972,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50622,0.04745,0.11398]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4121.0,"contact_point_centroid":[0.49981,0.05906,0.03136],"force_p95":0.07599,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09791,"mean_force":0.0518,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.4993,0.03985,0.02868]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4870.0,"contact_point_centroid":[0.49994,0.02079,0.03059],"force_p95":0.06789,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08558,"mean_force":0.04468,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.4993,0.03985,0.02868]}],"total_contact_groups":14},"final_pose_error":0.04968,"key_states":{"actual_goal_position":[0.62757,0.17252,0.14502],"final_object_position":[0.62669,0.16703,0.01602],"final_tcp_position":[0.51313,0.01758,0.45542],"realised_goal_position":[0.62757,0.17252,0.14502],"realised_object_initial_position":[0.51251,0.03972,0.03]},"phases":[{"n_steps":300.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.03],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21001,"object_z_max":0.03,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"approach_object","tcp_end":[0.50755,0.05456,0.19227],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.16698,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":478.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"approach_object","tcp_end":[0.50753,0.04059,0.03767],"tcp_start":[0.50755,0.05456,0.19227],"tcp_to_object_dist_end":0.0127,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51237,0.04001,0.0259],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21218,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","subtask_id":"grasp_lift","tcp_end":[0.49927,0.03985,0.02865],"tcp_start":[0.50753,0.04059,0.03767],"tcp_to_object_dist_end":0.01339,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":368.0,"n_steps_budget":840.0,"object_pos_end":[0.51422,0.03976,0.13593],"object_pos_start":[0.51237,0.04001,0.0259],"object_to_goal_dist_end":0.1748,"object_to_goal_dist_start":0.21218,"object_z_max":0.13567,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","subtask_id":"grasp_lift","tcp_end":[0.4955,0.03952,0.14392],"tcp_start":[0.49927,0.03985,0.02865],"tcp_to_object_dist_end":0.02035,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":468.0,"n_steps_budget":1000.0,"object_pos_end":[0.6182,0.16124,0.11617],"object_pos_start":[0.51422,0.03976,0.13593],"object_to_goal_dist_end":0.03237,"object_to_goal_dist_start":0.1748,"object_z_max":0.13623,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"reach_goal","tcp_end":[0.6136,0.16111,0.13694],"tcp_start":[0.4955,0.03952,0.14392],"tcp_to_object_dist_end":0.02127,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.62729,0.16601,0.01604],"object_pos_start":[0.6182,0.16124,0.11617],"object_to_goal_dist_end":0.12915,"object_to_goal_dist_start":0.03237,"object_z_max":0.11617,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","subtask_id":"reach_goal","tcp_end":[0.60712,0.15953,0.15702],"tcp_start":[0.6136,0.16111,0.13694],"tcp_to_object_dist_end":0.14257,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":382.0,"n_steps_budget":1000.0,"object_pos_end":[0.62669,0.16703,0.01602],"object_pos_start":[0.62729,0.16601,0.01604],"object_to_goal_dist_end":0.12913,"object_to_goal_dist_start":0.12915,"object_z_max":0.01613,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","tcp_end":[0.51313,0.01758,0.45542],"tcp_start":[0.60712,0.15953,0.15702],"tcp_to_object_dist_end":0.47781,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.608,"average_solve_count":250.0,"average_success_count":250.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.arc_height":0.09748,"descend_1.descend_offset_z":0.00014,"lift_1.lift_height":0.15378,"release_1.release_duration":0.2677,"transport_1.transport_speed":0.05486},"optimized_scores":{"best_composite_score":0.19994,"best_fitness_score":0.59994,"best_task_score":0.23872},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":358.0,"contact_point_centroid":[0.57001,0.23286,-0.00525],"force_p95":0.97593,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.95584,"mean_force":0.2581,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.56738,0.21495,0.22655]},{"body_a":"world","body_b":"grasp_target","contact_count":71.0,"contact_point_centroid":[0.47988,0.04807,-0.00135],"force_p95":0.66362,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.69474,"mean_force":0.16814,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46931,0.04813,0.02814]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":290.0,"contact_point_centroid":[0.57408,0.23335,0.21137],"force_p95":0.19795,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32434,"mean_force":0.10018,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.5711,0.21681,0.21673]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6676.0,"contact_point_centroid":[0.46881,0.06694,0.08631],"force_p95":0.10772,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30763,"mean_force":0.06503,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46697,0.04789,0.0842]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6822.0,"contact_point_centroid":[0.46907,0.029,0.08809],"force_p95":0.10374,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30437,"mean_force":0.06378,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46695,0.04789,0.08612]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":115.0,"contact_point_centroid":[0.57619,0.19912,0.21219],"force_p95":0.22395,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29241,"mean_force":0.13192,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.57151,0.21695,0.21767]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":7752.0,"contact_point_centroid":[0.51923,0.10887,0.18553],"force_p95":0.14866,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22072,"mean_force":0.08733,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.51498,0.12728,0.18627]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":7574.0,"contact_point_centroid":[0.52207,0.14989,0.18695],"force_p95":0.13114,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17605,"mean_force":0.08897,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.51764,0.13148,0.18778]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.48268,0.04859,-0.00203],"force_p95":0.13284,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.15788,"mean_force":0.12541,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47163,0.04838,0.02802]},{"body_a":"world","body_b":"grasp_target","contact_count":1084.0,"contact_point_centroid":[0.4827,0.04873,-0.00188],"force_p95":0.1365,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12308,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49281,0.04423,0.25972]},{"body_a":"world","body_b":"grasp_target","contact_count":1288.0,"contact_point_centroid":[0.56935,0.23306,-0.00198],"force_p95":0.12436,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12513,"mean_force":0.12282,"phase_index":6.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.53843,0.12246,0.34518]},{"body_a":"world","body_b":"grasp_target","contact_count":2032.0,"contact_point_centroid":[0.4827,0.04873,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.47946,0.05384,0.11472]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5371.0,"contact_point_centroid":[0.47007,0.06753,0.02906],"force_p95":0.06509,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09742,"mean_force":0.04138,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47051,0.04827,0.02689]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5068.0,"contact_point_centroid":[0.47026,0.02904,0.0296],"force_p95":0.06616,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09414,"mean_force":0.04283,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.4705,0.04827,0.02688]}],"total_contact_groups":14},"final_pose_error":0.04928,"key_states":{"actual_goal_position":[0.58187,0.22885,0.23048],"final_object_position":[0.56935,0.23306,0.01602],"final_tcp_position":[0.50984,0.02741,0.46024],"realised_goal_position":[0.58187,0.22885,0.23048],"realised_object_initial_position":[0.4827,0.04873,0.03]},"phases":[{"n_steps":272.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.03],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28719,"object_z_max":0.03,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"approach_object","tcp_end":[0.48313,0.05889,0.1967],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.17099,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":508.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"approach_object","tcp_end":[0.47837,0.04909,0.0349],"tcp_start":[0.48313,0.05889,0.1967],"tcp_to_object_dist_end":0.00989,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.48256,0.04828,0.02588],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.2904,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","subtask_id":"grasp_lift","tcp_end":[0.47048,0.04826,0.02685],"tcp_start":[0.47837,0.04909,0.0349],"tcp_to_object_dist_end":0.01213,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":412.0,"n_steps_budget":960.0,"object_pos_end":[0.48653,0.04809,0.15464],"object_pos_start":[0.48256,0.04828,0.02588],"object_to_goal_dist_end":0.21799,"object_to_goal_dist_start":0.2904,"object_z_max":0.15437,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","subtask_id":"grasp_lift","tcp_end":[0.46703,0.0479,0.16123],"tcp_start":[0.47048,0.04826,0.02685],"tcp_to_object_dist_end":0.02059,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":690.0,"n_steps_budget":1000.0,"object_pos_end":[0.57996,0.21641,0.1956],"object_pos_start":[0.48653,0.04809,0.15464],"object_to_goal_dist_end":0.03708,"object_to_goal_dist_start":0.21799,"object_z_max":0.19557,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"reach_goal","tcp_end":[0.57194,0.21664,0.21842],"tcp_start":[0.46703,0.0479,0.16123],"tcp_to_object_dist_end":0.02419,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.56933,0.23306,0.01652],"object_pos_start":[0.57996,0.21641,0.1956],"object_to_goal_dist_end":0.21437,"object_to_goal_dist_start":0.03708,"object_z_max":0.1956,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","subtask_id":"reach_goal","tcp_end":[0.5673,0.21492,0.23951],"tcp_start":[0.57194,0.21664,0.21842],"tcp_to_object_dist_end":0.22373,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":322.0,"n_steps_budget":1000.0,"object_pos_end":[0.56935,0.23306,0.01602],"object_pos_start":[0.56933,0.23306,0.01652],"object_to_goal_dist_end":0.21487,"object_to_goal_dist_start":0.21437,"object_z_max":0.01652,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","tcp_end":[0.50984,0.02741,0.46024],"tcp_start":[0.5673,0.21492,0.23951],"tcp_to_object_dist_end":0.49312,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```