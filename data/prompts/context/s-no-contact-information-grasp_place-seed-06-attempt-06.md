## Search State

- **Seed**: 6
- **Iteration**: 7 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 6 | approach → descend → grasp → lift → push → release → retract | arc_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 5 | 0.2161 | 0.28 | ✅ accepted |
| 5 | align → lift → push → approach → approach → descend → grasp → rotate | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | arc_cartesian | linear_cartesian | — | impedance_motion | position_control | position_control | impedance_control | force_threshold_switch | position_control | admittance_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 6 | -0.1417 | 0.25 | ❌ rejected |
| 4 | approach → descend → grasp → approach → release → retract | linear_cartesian | linear_cartesian | — | arc_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | time_limit | pose_tolerance | 6 | -0.1449 | 0.17 | ❌ rejected |
| 3 | approach → descend → grasp → lift → approach → release | arc_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | admittance_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 6 | 0.0707 | 0.25 | ❌ rejected |
| 2 | align → lift → push → approach → approach → descend → grasp → rotate | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | arc_cartesian | linear_cartesian | — | impedance_motion | position_control | position_control | impedance_control | force_threshold_switch | position_control | admittance_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 6 | -0.1415 | 0.25 | ✅ accepted |

**Proposal policy**: task_score is 0.28 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.216) — your mutation base

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
  offset:
  - 0.0
  - 0.0
  - 0.2
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
  type: push
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
    - 0.2
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
- **transport_1** (`push`)
  - target: source=yaml, anchor=task_goal, entity=placement_surface, offset=[0.0, 0.0, 0.2], tolerance=0.02
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

- **Composite score**: 0.216
- **task_score** (E): 0.279
- **fitness_score**: 0.616  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Complexity Penalty**: 0.400

## Per-Phase Performance

| Phase | Normal Term. Rate | Mean Displacement (m) |
| ------- | ------------------- | ------------------------ |
| approach_1 | 1.00 | 0.1162 |
| descend_1 | 1.00 | 0.1526 |
| grasp_1 | 1.00 | 0.0118 |
| lift_1 | 1.00 | 0.1260 |
| transport_1 | 0.33 | 0.2716 |
| release_1 | 1.00 | 0.0212 |
| retract_1 | 1.00 | 0.1739 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end |
| --- | --- | --- | --- | --- | --- |
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.497, 0.036, 0.193) | (0.500, 0.024, 0.030)→(0.500, 0.024, 0.026) | 0.269→0.271 |
| descend_1 | descend | 1.00 / step_budget | (0.497, 0.036, 0.193)→(0.495, 0.025, 0.041) | (0.500, 0.024, 0.026)→(0.500, 0.024, 0.026) | 0.271→0.271 |
| grasp_1 | grasp | 1.00 / step_budget | (0.495, 0.025, 0.041)→(0.487, 0.025, 0.033) | (0.500, 0.024, 0.026)→(0.500, 0.025, 0.026) | 0.271→0.272 |
| lift_1 | lift | 1.00 / step_budget | (0.487, 0.025, 0.033)→(0.483, 0.024, 0.159) | (0.500, 0.025, 0.026)→(0.501, 0.024, 0.146) | 0.272→0.211 |
| transport_1 | push | 0.33 / step_budget | (0.483, 0.024, 0.159)→(0.582, 0.170, 0.363) | (0.501, 0.024, 0.146)→(0.583, 0.157, 0.043) | 0.211→0.175 |
| release_1 | release | 1.00 / step_budget | (0.582, 0.170, 0.363)→(0.581, 0.170, 0.384) | (0.583, 0.157, 0.043)→(0.584, 0.157, 0.016) | 0.175→0.201 |
| retract_1 | retract | 1.00 / step_budget | (0.581, 0.170, 0.384)→(0.518, 0.035, 0.471) | (0.584, 0.157, 0.016)→(0.584, 0.157, 0.016) | 0.201→0.201 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.420
- phase_score: 0.457
- phase_breakdown.reach_goal_score: 0.781
- phase_breakdown.approach_object_score: 0.059
- phase_breakdown.grasp_lift_score: 0.182
- grasp_place_fitness: 0.688

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.688
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.420
- **Median Q (composite search score)**: 0.197
- **K-run variance**: 0.0028
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.395


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.49787,"average_solve_count":235.0,"average_success_count":235.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.arc_height":0.08221,"descend_1.descend_offset_z":0.0102,"lift_1.lift_height":0.16134,"release_1.release_duration":0.32111,"transport_1.transport_speed":0.05651},"optimized_scores":{"best_composite_score":0.16329,"best_fitness_score":0.56329,"best_task_score":0.17872},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":1227.0,"contact_point_centroid":[0.55809,0.07782,-0.00307],"force_p95":0.55142,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.31896,"mean_force":0.17478,"phase_index":4.0,"phase_name":"transport_1","phase_type":"push","tcp_position_centroid":[0.55571,0.12674,0.36]},{"body_a":"world","body_b":"grasp_target","contact_count":79.0,"contact_point_centroid":[0.50112,-0.01316,-0.00147],"force_p95":0.52303,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54217,"mean_force":0.12147,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48965,-0.01389,0.03737]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6493.0,"contact_point_centroid":[0.48991,0.00514,0.10017],"force_p95":0.11106,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32522,"mean_force":0.07184,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48731,-0.01385,0.09776]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":7235.0,"contact_point_centroid":[0.4899,-0.03268,0.09845],"force_p95":0.10615,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30673,"mean_force":0.06646,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48732,-0.01385,0.09672]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5318.0,"contact_point_centroid":[0.51286,0.04955,0.23185],"force_p95":0.14833,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26008,"mean_force":0.09991,"phase_index":4.0,"phase_name":"transport_1","phase_type":"push","tcp_position_centroid":[0.50717,0.03117,0.233]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50388,-0.01543,-0.00217],"force_p95":0.1699,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.23954,"mean_force":0.13487,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49212,-0.01392,0.03711]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5698.0,"contact_point_centroid":[0.51323,0.01376,0.23278],"force_p95":0.13065,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19776,"mean_force":0.09477,"phase_index":4.0,"phase_name":"transport_1","phase_type":"push","tcp_position_centroid":[0.50762,0.03199,0.23416]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3995.0,"contact_point_centroid":[0.49155,0.00538,0.0386],"force_p95":0.08339,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1589,"mean_force":0.05313,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49096,-0.0139,0.03588]},{"body_a":"world","body_b":"grasp_target","contact_count":1044.0,"contact_point_centroid":[0.50382,-0.01567,-0.00187],"force_p95":0.1365,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12309,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49964,0.02094,0.24369]},{"body_a":"world","body_b":"grasp_target","contact_count":1784.0,"contact_point_centroid":[0.50382,-0.01567,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49832,-0.0055,0.11458]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.55806,0.07785,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.56721,0.15089,0.39438]},{"body_a":"world","body_b":"grasp_target","contact_count":592.0,"contact_point_centroid":[0.55806,0.07785,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.54379,0.0969,0.44046]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5533.0,"contact_point_centroid":[0.49073,-0.03302,0.03855],"force_p95":0.0701,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07447,"mean_force":0.04051,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49097,-0.0139,0.03589]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1204.0,"contact_point_centroid":[0.55707,0.12883,0.36506],"force_p95":0.01257,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01635,"mean_force":0.01063,"phase_index":4.0,"phase_name":"transport_1","phase_type":"push","tcp_position_centroid":[0.55678,0.12882,0.36277]},{"body_a":"left_finger","body_b":"right_finger","contact_count":223.0,"contact_point_centroid":[0.56814,0.15135,0.39244],"force_p95":0.01096,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01274,"mean_force":0.01,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.5678,0.15134,0.39025]}],"total_contact_groups":15},"final_pose_error":0.04934,"key_states":{"actual_goal_position":[0.58691,0.18745,0.24812],"final_object_position":[0.55806,0.07785,0.01602],"final_tcp_position":[0.51834,0.03696,0.47294],"realised_goal_position":[0.58691,0.18745,0.24812],"realised_object_initial_position":[0.50382,-0.01567,0.03]},"phases":[{"n_steps":262.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.03],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.30942,"object_z_max":0.03,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"approach_object","tcp_end":[0.50019,0.00282,0.18584],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.16093,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":446.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"approach_object","tcp_end":[0.49902,-0.01394,0.04455],"tcp_start":[0.50019,0.00282,0.18584],"tcp_to_object_dist_end":0.01922,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50376,-0.01412,0.02545],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31165,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","subtask_id":"grasp_lift","tcp_end":[0.49093,-0.0139,0.03585],"tcp_start":[0.49902,-0.01394,0.04455],"tcp_to_object_dist_end":0.01652,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":447.0,"n_steps_budget":1000.0,"object_pos_end":[0.50475,-0.01394,0.16105],"object_pos_start":[0.50376,-0.01412,0.02545],"object_to_goal_dist_end":0.23428,"object_to_goal_dist_start":0.31165,"object_z_max":0.16078,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","subtask_id":"grasp_lift","tcp_end":[0.48746,-0.01384,0.17751],"tcp_start":[0.49093,-0.0139,0.03585],"tcp_to_object_dist_end":0.02388,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.55806,0.07785,0.01602],"object_pos_start":[0.50475,-0.01394,0.16105],"object_to_goal_dist_end":0.25829,"object_to_goal_dist_start":0.23428,"object_z_max":0.27392,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"push","subtask_id":"reach_goal","tcp_end":[0.56829,0.15118,0.3925],"tcp_start":[0.48746,-0.01384,0.17751],"tcp_to_object_dist_end":0.38369,"terminated_normally":false,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.55806,0.07785,0.01602],"object_pos_start":[0.55806,0.07785,0.01602],"object_to_goal_dist_end":0.25829,"object_to_goal_dist_start":0.25829,"object_z_max":0.01602,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","subtask_id":"reach_goal","tcp_end":[0.56705,0.15067,0.4143],"tcp_start":[0.56829,0.15118,0.3925],"tcp_to_object_dist_end":0.40498,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":148.0,"n_steps_budget":1000.0,"object_pos_end":[0.55806,0.07785,0.01602],"object_pos_start":[0.55806,0.07785,0.01602],"object_to_goal_dist_end":0.25829,"object_to_goal_dist_start":0.25829,"object_z_max":0.01602,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","tcp_end":[0.51834,0.03696,0.47294],"tcp_start":[0.56705,0.15067,0.4143],"tcp_to_object_dist_end":0.46046,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.48855,"average_solve_count":262.0,"average_success_count":262.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.arc_height":0.09219,"descend_1.descend_offset_z":0.00454,"lift_1.lift_height":0.13624,"release_1.release_duration":0.1612,"transport_1.transport_speed":0.04511},"optimized_scores":{"best_composite_score":0.28816,"best_fitness_score":0.68816,"best_task_score":0.41998},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":298.0,"contact_point_centroid":[0.61805,0.18658,-0.00684],"force_p95":1.48623,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.32882,"mean_force":0.33612,"phase_index":4.0,"phase_name":"transport_1","phase_type":"push","tcp_position_centroid":[0.61561,0.16152,0.32103]},{"body_a":"world","body_b":"grasp_target","contact_count":75.0,"contact_point_centroid":[0.50935,0.03958,-0.00132],"force_p95":0.59208,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.63103,"mean_force":0.13628,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49805,0.03947,0.03128]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5519.0,"contact_point_centroid":[0.49788,0.0583,0.08394],"force_p95":0.10866,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.34302,"mean_force":0.07079,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49555,0.03926,0.08162]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6184.0,"contact_point_centroid":[0.498,0.02048,0.08195],"force_p95":0.10457,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30066,"mean_force":0.06423,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49558,0.03927,0.08024]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8459.0,"contact_point_centroid":[0.5469,0.07051,0.21403],"force_p95":0.13737,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24132,"mean_force":0.08771,"phase_index":4.0,"phase_name":"transport_1","phase_type":"push","tcp_position_centroid":[0.54239,0.08889,0.21505]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8596.0,"contact_point_centroid":[0.54904,0.10938,0.21697],"force_p95":0.12962,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21163,"mean_force":0.0871,"phase_index":4.0,"phase_name":"transport_1","phase_type":"push","tcp_position_centroid":[0.54453,0.09103,0.21815]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.51249,0.03977,-0.00202],"force_p95":0.12962,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.14076,"mean_force":0.12453,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.50049,0.03969,0.03126]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.61773,0.18649,-0.00192],"force_p95":0.13614,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.14052,"mean_force":0.12274,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.61845,0.16555,0.32823]},{"body_a":"world","body_b":"grasp_target","contact_count":1080.0,"contact_point_centroid":[0.51251,0.03972,-0.00188],"force_p95":0.1365,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12308,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50203,0.04148,0.25763]},{"body_a":"world","body_b":"grasp_target","contact_count":1924.0,"contact_point_centroid":[0.51251,0.03972,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50616,0.04574,0.11582]},{"body_a":"world","body_b":"grasp_target","contact_count":888.0,"contact_point_centroid":[0.61773,0.1865,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.57152,0.0991,0.4027]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4140.0,"contact_point_centroid":[0.49983,0.05881,0.03267],"force_p95":0.0753,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09374,"mean_force":0.0518,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49931,0.03959,0.02999]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4849.0,"contact_point_centroid":[0.49994,0.02054,0.0319],"force_p95":0.06862,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09023,"mean_force":0.04464,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49931,0.03959,0.02999]},{"body_a":"left_finger","body_b":"right_finger","contact_count":208.0,"contact_point_centroid":[0.61773,0.1631,0.32543],"force_p95":0.01491,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01823,"mean_force":0.0117,"phase_index":4.0,"phase_name":"transport_1","phase_type":"push","tcp_position_centroid":[0.61719,0.16308,0.3233]},{"body_a":"left_finger","body_b":"right_finger","contact_count":228.0,"contact_point_centroid":[0.62011,0.16616,0.32755],"force_p95":0.01092,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0127,"mean_force":0.00987,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.61961,0.16614,0.32504]}],"total_contact_groups":15},"final_pose_error":0.04908,"key_states":{"actual_goal_position":[0.62757,0.17252,0.14502],"final_object_position":[0.61773,0.1865,0.01602],"final_tcp_position":[0.52249,0.02863,0.46708],"realised_goal_position":[0.62757,0.17252,0.14502],"realised_object_initial_position":[0.51251,0.03972,0.03]},"phases":[{"n_steps":271.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.03],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21001,"object_z_max":0.03,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"approach_object","tcp_end":[0.50742,0.05141,0.19497],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.16944,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":481.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"approach_object","tcp_end":[0.50753,0.04032,0.03899],"tcp_start":[0.50742,0.05141,0.19497],"tcp_to_object_dist_end":0.0139,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51238,0.03978,0.02591],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21231,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","subtask_id":"grasp_lift","tcp_end":[0.49928,0.03959,0.02996],"tcp_start":[0.50753,0.04032,0.03899],"tcp_to_object_dist_end":0.01371,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":373.0,"n_steps_budget":870.0,"object_pos_end":[0.51402,0.03946,0.13721],"object_pos_start":[0.51238,0.03978,0.02591],"object_to_goal_dist_end":0.1751,"object_to_goal_dist_start":0.21231,"object_z_max":0.13695,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","subtask_id":"grasp_lift","tcp_end":[0.49553,0.03926,0.14655],"tcp_start":[0.49928,0.03959,0.02996],"tcp_to_object_dist_end":0.02072,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":978.0,"n_steps_budget":1000.0,"object_pos_end":[0.61759,0.18576,0.0174],"object_pos_start":[0.51402,0.03946,0.13721],"object_to_goal_dist_end":0.1287,"object_to_goal_dist_start":0.1751,"object_z_max":0.26758,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"push","subtask_id":"reach_goal","tcp_end":[0.62029,0.16614,0.32776],"tcp_start":[0.49553,0.03926,0.14655],"tcp_to_object_dist_end":0.31099,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.61773,0.1865,0.01602],"object_pos_start":[0.61759,0.18576,0.0174],"object_to_goal_dist_end":0.13013,"object_to_goal_dist_start":0.1287,"object_z_max":0.0174,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","subtask_id":"reach_goal","tcp_end":[0.61793,0.16524,0.34752],"tcp_start":[0.62029,0.16614,0.32776],"tcp_to_object_dist_end":0.33218,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":222.0,"n_steps_budget":1000.0,"object_pos_end":[0.61773,0.1865,0.01602],"object_pos_start":[0.61773,0.1865,0.01602],"object_to_goal_dist_end":0.13013,"object_to_goal_dist_start":0.13013,"object_z_max":0.01602,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","tcp_end":[0.52249,0.02863,0.46708],"tcp_start":[0.61793,0.16524,0.34752],"tcp_to_object_dist_end":0.48729,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.51867,"average_solve_count":241.0,"average_success_count":241.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.arc_height":0.02997,"descend_1.descend_offset_z":0.00526,"lift_1.lift_height":0.13905,"release_1.release_duration":0.35272,"transport_1.transport_speed":0.05486},"optimized_scores":{"best_composite_score":0.19691,"best_fitness_score":0.59691,"best_task_score":0.23715},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":711.0,"contact_point_centroid":[0.57554,0.20511,-0.00454],"force_p95":0.93137,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.56123,"mean_force":0.21736,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.55733,0.19301,0.37189]},{"body_a":"world","body_b":"grasp_target","contact_count":73.0,"contact_point_centroid":[0.47957,0.04741,-0.00138],"force_p95":0.5791,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.6031,"mean_force":0.14149,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46937,0.0477,0.03346]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6267.0,"contact_point_centroid":[0.46864,0.06653,0.08561],"force_p95":0.10557,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30853,"mean_force":0.06252,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46709,0.04747,0.08356]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6210.0,"contact_point_centroid":[0.4689,0.02852,0.08805],"force_p95":0.10161,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29529,"mean_force":0.06261,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46707,0.04747,0.08596]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":9296.0,"contact_point_centroid":[0.50807,0.0895,0.23938],"force_p95":0.14461,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27705,"mean_force":0.09,"phase_index":4.0,"phase_name":"transport_1","phase_type":"push","tcp_position_centroid":[0.50311,0.1079,0.23987]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.48271,0.04856,-0.00207],"force_p95":0.14405,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.21711,"mean_force":0.12842,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47171,0.04795,0.03324]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":9630.0,"contact_point_centroid":[0.51022,0.12989,0.2446],"force_p95":0.12743,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17126,"mean_force":0.08694,"phase_index":4.0,"phase_name":"transport_1","phase_type":"push","tcp_position_centroid":[0.50543,0.1115,0.24531]},{"body_a":"world","body_b":"grasp_target","contact_count":952.0,"contact_point_centroid":[0.4827,0.04873,-0.00186],"force_p95":0.13699,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12314,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49252,0.03571,0.25714]},{"body_a":"world","body_b":"grasp_target","contact_count":764.0,"contact_point_centroid":[0.57554,0.20522,-0.00199],"force_p95":0.12264,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12266,"mean_force":0.12262,"phase_index":6.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.53594,0.11862,0.42836]},{"body_a":"world","body_b":"grasp_target","contact_count":1988.0,"contact_point_centroid":[0.4827,0.04873,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.47974,0.05068,0.11848]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5050.0,"contact_point_centroid":[0.47032,0.0286,0.03476],"force_p95":0.06759,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10678,"mean_force":0.04292,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47059,0.04784,0.03211]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5428.0,"contact_point_centroid":[0.47013,0.06711,0.0342],"force_p95":0.06688,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08458,"mean_force":0.04122,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47059,0.04784,0.03211]},{"body_a":"left_finger","body_b":"right_finger","contact_count":72.0,"contact_point_centroid":[0.55853,0.19349,0.36822],"force_p95":0.01553,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01605,"mean_force":0.01181,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.55794,0.19346,0.3657]}],"total_contact_groups":13},"final_pose_error":0.04917,"key_states":{"actual_goal_position":[0.58187,0.22885,0.23048],"final_object_position":[0.57554,0.20522,0.01602],"final_tcp_position":[0.51328,0.03835,0.47225],"realised_goal_position":[0.58187,0.22885,0.23048],"realised_object_initial_position":[0.4827,0.04873,0.03]},"phases":[{"n_steps":239.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.03],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28719,"object_z_max":0.03,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"approach_object","tcp_end":[0.48361,0.053,0.19926],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.1733,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":497.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"approach_object","tcp_end":[0.47844,0.04864,0.04015],"tcp_start":[0.48361,0.053,0.19926],"tcp_to_object_dist_end":0.01476,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.48259,0.04795,0.02574],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.29069,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","subtask_id":"grasp_lift","tcp_end":[0.47056,0.04783,0.03208],"tcp_start":[0.47844,0.04864,0.04015],"tcp_to_object_dist_end":0.0136,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":367.0,"n_steps_budget":870.0,"object_pos_end":[0.48477,0.04773,0.14115],"object_pos_start":[0.48259,0.04795,0.02574],"object_to_goal_dist_end":0.22409,"object_to_goal_dist_start":0.29069,"object_z_max":0.14088,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","subtask_id":"grasp_lift","tcp_end":[0.46705,0.04746,0.15174],"tcp_start":[0.47056,0.04783,0.03208],"tcp_to_object_dist_end":0.02064,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.57191,0.2075,0.09553],"object_pos_start":[0.48477,0.04773,0.14115],"object_to_goal_dist_end":0.137,"object_to_goal_dist_start":0.22409,"object_z_max":0.32006,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"push","subtask_id":"reach_goal","tcp_end":[0.55879,0.19365,0.36981],"tcp_start":[0.46705,0.04746,0.15174],"tcp_to_object_dist_end":0.27495,"terminated_normally":false,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.57554,0.20523,0.01602],"object_pos_start":[0.57191,0.2075,0.09553],"object_to_goal_dist_end":0.21586,"object_to_goal_dist_start":0.137,"object_z_max":0.09553,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","subtask_id":"reach_goal","tcp_end":[0.55717,0.19282,0.39147],"tcp_start":[0.55879,0.19365,0.36981],"tcp_to_object_dist_end":0.37611,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":191.0,"n_steps_budget":1000.0,"object_pos_end":[0.57554,0.20522,0.01602],"object_pos_start":[0.57554,0.20523,0.01602],"object_to_goal_dist_end":0.21586,"object_to_goal_dist_start":0.21586,"object_z_max":0.01602,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","tcp_end":[0.51328,0.03835,0.47225],"tcp_start":[0.55717,0.19282,0.39147],"tcp_to_object_dist_end":0.48976,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```