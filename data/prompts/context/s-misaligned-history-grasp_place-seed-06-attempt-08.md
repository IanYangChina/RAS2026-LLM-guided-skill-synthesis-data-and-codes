## Search State

- **Seed**: 6
- **Iteration**: 9 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 8 | approach → descend → grasp → lift → push → descend | arc_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 10  | -0.1048 | 0.29 | ✅ accepted |
| 7 | approach → descend → grasp → lift → push → descend → release → retract | arc_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 11  | -0.1416 | 0.25 | ❌ rejected |
| 6 | align → lift → push → approach → approach → descend → grasp → rotate | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | arc_cartesian | linear_cartesian | — | impedance_motion | position_control | position_control | impedance_control | force_threshold_switch | position_control | admittance_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 6  | -0.1417 | 0.25 | ❌ rejected |
| 5 | align → lift → push → approach → approach → descend → grasp → rotate | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | arc_cartesian | linear_cartesian | — | impedance_motion | position_control | position_control | impedance_control | force_threshold_switch | position_control | admittance_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 6  | -0.2456 | 0.17 | ❌ rejected |
| 4 | approach → descend → grasp → lift → approach → descend → release → retract | arc_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | admittance_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 7  | 0.3594 | 1.00 | ✅ accepted |

**Proposal policy**: task_score is near-perfect (1.00). Preserve useful working parts and make only evidence-backed refinements. A HOLD is acceptable if you genuinely cannot find a better structure.

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

> ⚠️ **SUBTASK STRUCTURE CAUTION**: The current best task_score is 1.000, which indicates the subtask decomposition is already effective.
> Preserve the current subtask decomposition unless the evidence shows a subtask change is necessary. Prefer refining phases, parameters, control modes, or termination conditions first.
> Unnecessary subtask redesign when performance is already high often causes regression.

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

## Current Skill (Q=0.359) — your mutation base

```yaml
skill: grasp_place
dsl_version: 2
skill_type: arm_gripper
subtasks:
- id: reach_pre_grasp
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.15
  weight: 0.3
- id: reach_goal
  target_entity: object
  weight: 0.7
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
    - 0.15
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    generator.arc_height:
      type: scalar
      range:
      - 0.02
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.arc_height
        mode: replace
    generator.speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: reach_pre_grasp
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
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    generator.speed:
      type: scalar
      range:
      - 0.01
      - 0.05
      default: 0.02
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: reach_pre_grasp
- id: grasp_1
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
  parameters:
    duration.max_time:
      type: scalar
      range:
      - 0.5
      - 2.0
      default: 1.0
      binds_to:
      - path: duration.max_time
        mode: replace
  guards:
  - id: grasp_check
    when: after_phase
    predicate: bilateral_grasp
    threshold: 0.5
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: repeat
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
      distance: 0.25
      axis: world_z
      mode: add_to_offset
      sign: positive
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    generator.speed:
      type: scalar
      range:
      - 0.02
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
    target.offset_along_axis.distance:
      type: scalar
      range:
      - 0.15
      - 0.3
      default: 0.25
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
  guards:
  - id: lift_check
    when: after_phase
    predicate: object_lifted
    threshold: 0.1
    on_failure: retry
  retries:
    max_attempts: 1
    strategy: repeat
  subtask_id: reach_pre_grasp
- id: transport_1
  type: push
  generator: arc_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.05
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    generator.arc_height:
      type: scalar
      range:
      - 0.02
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.arc_height
        mode: replace
    generator.speed:
      type: scalar
      range:
      - 0.02
      - 0.15
      default: 0.08
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: reach_goal
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
    - 0.015
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    generator.speed:
      type: scalar
      range:
      - 0.01
      - 0.05
      default: 0.02
      binds_to:
      - path: generator.speed
        mode: replace
    target.offset.z:
      type: scalar
      range:
      - 0.0
      - 0.03
      default: 0.015
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: reach_goal

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.15], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - generator.arc_height: status=consumed; consumers=generator.arc_height (replace)
    - generator.speed: status=consumed; consumers=generator.speed (replace)
- **descend_1** (`descend`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.0], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - generator.speed: status=consumed; consumers=generator.speed (replace)
- **grasp_1** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings:
    - duration.max_time: status=consumed; consumers=duration.max_time (replace)
  - guards:
    - id=grasp_check, when=after_phase, predicate=bilateral_grasp, on_failure=retry, threshold=0.5
  - retries: max_attempts=2, strategy=repeat
- **lift_1** (`lift`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=world_z, distance=0.25, mode=add_to_offset, sign=positive}, tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - generator.speed: status=consumed; consumers=generator.speed (replace)
    - target.offset_along_axis.distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
  - guards:
    - id=lift_check, when=after_phase, predicate=object_lifted, on_failure=retry, threshold=0.1
  - retries: max_attempts=1, strategy=repeat
- **transport_1** (`push`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.05], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - generator.arc_height: status=consumed; consumers=generator.arc_height (replace)
    - generator.speed: status=consumed; consumers=generator.speed (replace)
- **descend_2** (`descend`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.015], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - generator.speed: status=consumed; consumers=generator.speed (replace)
    - target.offset.z: status=consumed; consumers=target.offset.z (replace)

## Design Metrics

- **Composite score**: 0.359
- **task_score** (E): 1.000
- **fitness_score**: 0.979  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.620

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1257 |
| descend_1 | 1.00 | 1.00 | 0.1486 |
| grasp_1 | 1.00 | 1.00 | 0.0118 |
| lift_1 | 1.00 | 1.00 | 0.2232 |
| transport_1 | 1.00 | 1.00 | 0.1971 |
| descend_2 | 1.00 | 1.00 | 0.0384 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.497, 0.032, 0.183) | (0.500, 0.024, 0.030)→(0.500, 0.024, 0.026) | 0.269→0.271 | 1.00 / 4.000 | 13.908 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.497, 0.032, 0.183)→(0.495, 0.025, 0.034) | (0.500, 0.024, 0.026)→(0.500, 0.024, 0.026) | 0.271→0.271 | 1.00 / 4.000 | 9.069 | 0.123 |
| grasp_1 | grasp | 1.00 / step_budget | (0.495, 0.025, 0.034)→(0.487, 0.024, 0.026) | (0.500, 0.024, 0.026)→(0.500, 0.024, 0.026) | 0.271→0.272 | 1.00 / 43.000 | 0.170 | 0.226 |
| lift_1 | lift | 1.00 / step_budget | (0.487, 0.024, 0.026)→(0.496, 0.024, 0.249) | (0.500, 0.024, 0.026)→(0.507, 0.024, 0.242) | 0.272→0.212 | 1.00 / 43.000 | 0.070 | 0.640 |
| transport_1 | push | 1.00 / step_budget | (0.496, 0.024, 0.249)→(0.590, 0.183, 0.266) | (0.507, 0.024, 0.242)→(0.601, 0.183, 0.251) | 0.212→0.045 | 1.00 / 29.000 | 0.107 | 0.208 |
| descend_2 | descend | 1.00 / step_budget | (0.590, 0.183, 0.266)→(0.593, 0.191, 0.229) | (0.601, 0.183, 0.251)→(0.603, 0.191, 0.211) | 0.045→0.011 | 1.00 / 28.000 | 0.115 | 0.340 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.533
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 1.000
- phase_score: 0.625
- phase_breakdown.reach_pre_grasp_score: 0.485
- phase_breakdown.reach_goal_score: 0.685
- grasp_place_fitness: 0.980

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.980
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 1.000
- **Median Q (composite search score)**: 0.359
- **K-run variance**: 0.0000
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.292


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.08108,"average_solve_count":370.0,"average_success_count":370.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.generator.arc_height":0.09933,"approach_1.generator.speed":0.07095,"descend_1.generator.speed":0.01575,"descend_2.generator.speed":0.03714,"descend_2.target.offset.z":0.01191,"grasp_1.duration.max_time":1.31919,"lift_1.generator.speed":0.0247,"lift_1.target.offset_along_axis.distance":0.24213,"transport_1.generator.arc_height":0.06421,"transport_1.generator.speed":0.06874},"optimized_scores":{"best_composite_score":0.35916,"best_fitness_score":0.97916,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":89.0,"contact_point_centroid":[0.49973,-0.01428,-0.00147],"force_p95":0.57645,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.59984,"mean_force":0.23135,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48966,-0.01472,0.02687]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1258.0,"contact_point_centroid":[0.58221,0.19365,0.2809],"force_p95":0.15425,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.4538,"mean_force":0.1005,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.57926,0.17554,0.28514]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1196.0,"contact_point_centroid":[0.58221,0.15767,0.28024],"force_p95":0.16102,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.42923,"mean_force":0.10059,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.57934,0.17574,0.28439]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":15657.0,"contact_point_centroid":[0.49338,0.00453,0.13998],"force_p95":0.07615,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28078,"mean_force":0.05155,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49344,-0.01463,0.13787]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":16183.0,"contact_point_centroid":[0.49326,-0.03376,0.13697],"force_p95":0.07327,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2695,"mean_force":0.05049,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49329,-0.01463,0.13525]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":9342.0,"contact_point_centroid":[0.53219,0.07539,0.30501],"force_p95":0.11197,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24095,"mean_force":0.07304,"phase_index":4.0,"phase_name":"transport_1","phase_type":"push","tcp_position_centroid":[0.52891,0.05658,0.30428]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":10180.0,"contact_point_centroid":[0.53132,0.03554,0.30369],"force_p95":0.10805,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23738,"mean_force":0.06843,"phase_index":4.0,"phase_name":"transport_1","phase_type":"push","tcp_position_centroid":[0.52789,0.05419,0.30344]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50384,-0.01541,-0.00208],"force_p95":0.14855,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.22226,"mean_force":0.12962,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49183,-0.01474,0.02705]},{"body_a":"world","body_b":"grasp_target","contact_count":1868.0,"contact_point_centroid":[0.50382,-0.01567,-0.00193],"force_p95":0.13354,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12289,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49911,0.01604,0.23729]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4076.0,"contact_point_centroid":[0.49119,0.00447,0.02858],"force_p95":0.07914,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13224,"mean_force":0.05183,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49066,-0.01473,0.02582]},{"body_a":"world","body_b":"grasp_target","contact_count":2072.0,"contact_point_centroid":[0.50382,-0.01567,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49793,-0.01064,0.10677]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4952.0,"contact_point_centroid":[0.49126,-0.03385,0.02767],"force_p95":0.07057,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0872,"mean_force":0.04479,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49066,-0.01473,0.02583]}],"total_contact_groups":12},"final_pose_error":0.00993,"key_states":{"actual_goal_position":[0.58691,0.18745,0.24812],"final_object_position":[0.59218,0.18137,0.24462],"final_tcp_position":[0.58183,0.18141,0.26605],"realised_goal_position":[0.58691,0.18745,0.24812],"realised_object_initial_position":[0.50382,-0.01567,0.03]},"peak_contact_force":41.48021,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":468.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.03],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.30942,"object_z_max":0.03,"peak_contact_force":41.48021,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1868.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_pre_grasp","tcp_end":[0.49996,-0.0066,0.17972],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.15402,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":518.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2072.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_pre_grasp","tcp_end":[0.49882,-0.0148,0.03446],"tcp_start":[0.49996,-0.0066,0.17972],"tcp_to_object_dist_end":0.00985,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50368,-0.01464,0.02571],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31182,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.14269,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10828.0,"raw_peak_contact_force":0.22226,"tcp_end":[0.49063,-0.01473,0.02579],"tcp_start":[0.49882,-0.0148,0.03446],"tcp_to_object_dist_end":0.01305,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":784.0,"n_steps_budget":1000.0,"object_pos_end":[0.51132,-0.0146,0.24167],"object_pos_start":[0.50368,-0.01464,0.02571],"object_to_goal_dist_end":0.21583,"object_to_goal_dist_start":0.31182,"object_z_max":0.2414,"peak_contact_force":0.0699,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":31929.0,"raw_peak_contact_force":0.59984,"subtask_id":"reach_pre_grasp","tcp_end":[0.50008,-0.0146,0.24824],"tcp_start":[0.49063,-0.01473,0.02579],"tcp_to_object_dist_end":0.01302,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":22.0,"n_steps":684.0,"n_steps_budget":1000.0,"object_pos_end":[0.59135,0.17051,0.28572],"object_pos_start":[0.51132,-0.0146,0.24167],"object_to_goal_dist_end":0.04148,"object_to_goal_dist_start":0.21583,"object_z_max":0.31797,"peak_contact_force":0.13969,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":19522.0,"raw_peak_contact_force":0.24095,"subtask_id":"reach_goal","tcp_end":[0.57817,0.17049,0.30398],"tcp_start":[0.50008,-0.0146,0.24824],"tcp_to_object_dist_end":0.02252,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":20.0,"n_steps":123.0,"n_steps_budget":1000.0,"object_pos_end":[0.59218,0.18137,0.24462],"object_pos_start":[0.59135,0.17051,0.28572],"object_to_goal_dist_end":0.00877,"object_to_goal_dist_start":0.04148,"object_z_max":0.28572,"peak_contact_force":0.13121,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2454.0,"raw_peak_contact_force":0.4538,"subtask_id":"reach_goal","tcp_end":[0.58183,0.18141,0.26605],"tcp_start":[0.57817,0.17049,0.30398],"tcp_to_object_dist_end":0.0238,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.21519,"average_solve_count":316.0,"average_success_count":316.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.generator.arc_height":0.06061,"approach_1.generator.speed":0.06103,"descend_1.generator.speed":0.03609,"descend_2.generator.speed":0.03728,"descend_2.target.offset.z":0.02136,"grasp_1.duration.max_time":1.28421,"lift_1.generator.speed":0.04505,"lift_1.target.offset_along_axis.distance":0.27638,"transport_1.generator.arc_height":0.0577,"transport_1.generator.speed":0.10509},"optimized_scores":{"best_composite_score":0.3589,"best_fitness_score":0.9789,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":84.0,"contact_point_centroid":[0.50844,0.03923,-0.00144],"force_p95":0.58709,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.71102,"mean_force":0.24302,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.4982,0.0393,0.02639]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":17434.0,"contact_point_centroid":[0.50231,0.05822,0.1566],"force_p95":0.07806,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30007,"mean_force":0.05393,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.50216,0.03905,0.15469]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":18782.0,"contact_point_centroid":[0.50226,0.01997,0.15729],"force_p95":0.07373,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29075,"mean_force":0.05026,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.50217,0.03905,0.15535]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.51249,0.03956,-0.00203],"force_p95":0.227,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.23238,"mean_force":0.16239,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.50035,0.0395,0.02666]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":7997.0,"contact_point_centroid":[0.56826,0.08629,0.27593],"force_p95":0.09297,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20631,"mean_force":0.06389,"phase_index":4.0,"phase_name":"transport_1","phase_type":"push","tcp_position_centroid":[0.56662,0.10536,0.27441]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8736.0,"contact_point_centroid":[0.56767,0.12367,0.27584],"force_p95":0.08545,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18105,"mean_force":0.05763,"phase_index":4.0,"phase_name":"transport_1","phase_type":"push","tcp_position_centroid":[0.56611,0.10479,0.27522]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2300.0,"contact_point_centroid":[0.62028,0.14828,0.19347],"force_p95":0.07243,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17996,"mean_force":0.0488,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.61988,0.16741,0.19226]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2276.0,"contact_point_centroid":[0.6202,0.18661,0.19308],"force_p95":0.07234,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16926,"mean_force":0.04945,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.61988,0.16742,0.19214]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4110.0,"contact_point_centroid":[0.49978,0.02021,0.02819],"force_p95":0.08592,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15232,"mean_force":0.05943,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49916,0.0394,0.02539]},{"body_a":"world","body_b":"grasp_target","contact_count":2696.0,"contact_point_centroid":[0.51251,0.03972,-0.00195],"force_p95":0.12957,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12281,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50131,0.05195,0.25637]},{"body_a":"world","body_b":"grasp_target","contact_count":1992.0,"contact_point_centroid":[0.51251,0.03972,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50638,0.04425,0.10685]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4888.0,"contact_point_centroid":[0.49978,0.05849,0.02717],"force_p95":0.07715,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11288,"mean_force":0.05355,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49917,0.0394,0.02539]}],"total_contact_groups":12},"final_pose_error":0.00979,"key_states":{"actual_goal_position":[0.62757,0.17252,0.14502],"final_object_position":[0.62699,0.16928,0.15913],"final_tcp_position":[0.62159,0.16932,0.17345],"realised_goal_position":[0.62757,0.17252,0.14502],"realised_object_initial_position":[0.51251,0.03972,0.03]},"peak_contact_force":0.71102,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":675.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.03],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21001,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2696.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_pre_grasp","tcp_end":[0.50821,0.04857,0.18022],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.15452,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":498.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1992.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_pre_grasp","tcp_end":[0.50743,0.04012,0.03437],"tcp_start":[0.50821,0.04857,0.18022],"tcp_to_object_dist_end":0.00978,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51235,0.03929,0.02588],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21266,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.22693,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10798.0,"raw_peak_contact_force":0.23238,"tcp_end":[0.49913,0.0394,0.02536],"tcp_start":[0.50743,0.04012,0.03437],"tcp_to_object_dist_end":0.01323,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":913.0,"n_steps_budget":1000.0,"object_pos_end":[0.52034,0.03913,0.27497],"object_pos_start":[0.51235,0.03929,0.02588],"object_to_goal_dist_end":0.21489,"object_to_goal_dist_start":0.21266,"object_z_max":0.27471,"peak_contact_force":0.07044,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":36300.0,"raw_peak_contact_force":0.71102,"subtask_id":"reach_pre_grasp","tcp_end":[0.50919,0.03906,0.28256],"tcp_start":[0.49913,0.0394,0.02536],"tcp_to_object_dist_end":0.01349,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":489.0,"n_steps_budget":1000.0,"object_pos_end":[0.62503,0.16562,0.19854],"object_pos_start":[0.52034,0.03913,0.27497],"object_to_goal_dist_end":0.05401,"object_to_goal_dist_start":0.21489,"object_z_max":0.28485,"peak_contact_force":0.07406,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":16733.0,"raw_peak_contact_force":0.20631,"subtask_id":"reach_goal","tcp_end":[0.61983,0.166,0.21218],"tcp_start":[0.50919,0.03906,0.28256],"tcp_to_object_dist_end":0.0146,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":42.0,"n_steps":110.0,"n_steps_budget":1000.0,"object_pos_end":[0.62699,0.16928,0.15913],"object_pos_start":[0.62503,0.16562,0.19854],"object_to_goal_dist_end":0.01449,"object_to_goal_dist_start":0.05401,"object_z_max":0.19854,"peak_contact_force":0.07009,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4576.0,"raw_peak_contact_force":0.17996,"subtask_id":"reach_goal","tcp_end":[0.62159,0.16932,0.17345],"tcp_start":[0.61983,0.166,0.21218],"tcp_to_object_dist_end":0.0153,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.94057,"average_solve_count":387.0,"average_success_count":387.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.generator.arc_height":0.03165,"approach_1.generator.speed":0.04681,"descend_1.generator.speed":0.02484,"descend_2.generator.speed":0.02814,"descend_2.target.offset.z":0.01206,"grasp_1.duration.max_time":1.10495,"lift_1.generator.speed":0.03869,"lift_1.target.offset_along_axis.distance":0.20968,"transport_1.generator.arc_height":0.05463,"transport_1.generator.speed":0.06817},"optimized_scores":{"best_composite_score":0.3602,"best_fitness_score":0.9802,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":86.0,"contact_point_centroid":[0.47873,0.04763,-0.0015],"force_p95":0.58225,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.60887,"mean_force":0.24438,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46933,0.04774,0.02758]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1298.0,"contact_point_centroid":[0.57727,0.23571,0.26198],"force_p95":0.16938,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.38744,"mean_force":0.09819,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.57281,0.21728,0.2643]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1242.0,"contact_point_centroid":[0.57717,0.19896,0.26274],"force_p95":0.1757,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.38516,"mean_force":0.09727,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.57278,0.21723,0.26446]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":13247.0,"contact_point_centroid":[0.47265,0.06669,0.12278],"force_p95":0.07442,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28,"mean_force":0.05123,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.47262,0.04753,0.12098]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":13416.0,"contact_point_centroid":[0.47242,0.02838,0.12218],"force_p95":0.07311,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25282,"mean_force":0.05017,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.47258,0.04753,0.12033]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.48271,0.04853,-0.00207],"force_p95":0.14411,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.223,"mean_force":0.12856,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47139,0.04797,0.0278]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":10437.0,"contact_point_centroid":[0.51633,0.09276,0.27206],"force_p95":0.09943,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17561,"mean_force":0.06535,"phase_index":4.0,"phase_name":"transport_1","phase_type":"push","tcp_position_centroid":[0.51318,0.11143,0.27118]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":9414.0,"contact_point_centroid":[0.51651,0.13067,0.27289],"force_p95":0.10433,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16125,"mean_force":0.07133,"phase_index":4.0,"phase_name":"transport_1","phase_type":"push","tcp_position_centroid":[0.51336,0.11174,0.27162]},{"body_a":"world","body_b":"grasp_target","contact_count":1936.0,"contact_point_centroid":[0.4827,0.04873,-0.00193],"force_p95":0.13308,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12288,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49137,0.0388,0.25407]},{"body_a":"world","body_b":"grasp_target","contact_count":2212.0,"contact_point_centroid":[0.4827,0.04873,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.47831,0.0509,0.11115]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5046.0,"contact_point_centroid":[0.47008,0.02862,0.02962],"force_p95":0.06746,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10227,"mean_force":0.04289,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47026,0.04786,0.02666]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5434.0,"contact_point_centroid":[0.4699,0.06714,0.02903],"force_p95":0.06682,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0854,"mean_force":0.04125,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47026,0.04786,0.02667]}],"total_contact_groups":12},"final_pose_error":0.0098,"key_states":{"actual_goal_position":[0.58187,0.22885,0.23048],"final_object_position":[0.58841,0.22248,0.22847],"final_tcp_position":[0.57598,0.22267,0.24735],"realised_goal_position":[0.58187,0.22885,0.23048],"realised_object_initial_position":[0.4827,0.04873,0.03]},"peak_contact_force":26.96273,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":485.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.03],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28719,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1936.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_pre_grasp","tcp_end":[0.48138,0.0534,0.18868],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.16273,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":553.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":26.96273,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2212.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_pre_grasp","tcp_end":[0.4781,0.04866,0.03464],"tcp_start":[0.48138,0.0534,0.18868],"tcp_to_object_dist_end":0.00977,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":47.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.48258,0.04792,0.02574],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.29072,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.14053,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12280.0,"raw_peak_contact_force":0.223,"tcp_end":[0.47023,0.04785,0.02663],"tcp_start":[0.4781,0.04866,0.03464],"tcp_to_object_dist_end":0.01237,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":653.0,"n_steps_budget":1000.0,"object_pos_end":[0.48939,0.04764,0.21043],"object_pos_start":[0.48258,0.04792,0.02574],"object_to_goal_dist_end":0.20444,"object_to_goal_dist_start":0.29072,"object_z_max":0.21016,"peak_contact_force":0.07073,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":26749.0,"raw_peak_contact_force":0.60887,"subtask_id":"reach_pre_grasp","tcp_end":[0.47866,0.0476,0.21599],"tcp_start":[0.47023,0.04785,0.02663],"tcp_to_object_dist_end":0.01208,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":25.0,"n_steps":665.0,"n_steps_budget":1000.0,"object_pos_end":[0.58596,0.21247,0.26768],"object_pos_start":[0.48939,0.04764,0.21043],"object_to_goal_dist_end":0.04085,"object_to_goal_dist_start":0.20444,"object_z_max":0.28663,"peak_contact_force":0.1063,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":19851.0,"raw_peak_contact_force":0.17561,"subtask_id":"reach_goal","tcp_end":[0.57109,0.21243,0.28234],"tcp_start":[0.47866,0.0476,0.21599],"tcp_to_object_dist_end":0.02088,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":22.0,"n_steps":123.0,"n_steps_budget":1000.0,"object_pos_end":[0.58841,0.22248,0.22847],"object_pos_start":[0.58596,0.21247,0.26768],"object_to_goal_dist_end":0.00935,"object_to_goal_dist_start":0.04085,"object_z_max":0.26768,"peak_contact_force":0.14379,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2540.0,"raw_peak_contact_force":0.38744,"subtask_id":"reach_goal","tcp_end":[0.57598,0.22267,0.24735],"tcp_start":[0.57109,0.21243,0.28234],"tcp_to_object_dist_end":0.02261,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```