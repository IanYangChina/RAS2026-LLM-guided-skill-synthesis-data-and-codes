## Search State

- **Seed**: 6
- **Iteration**: 8 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 7 | approach → descend → grasp → lift → approach → descend → release → retract | arc_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 7 | 0.0617 | 0.24 | ❌ rejected |
| 6 | approach → descend → grasp → lift → push → release → retract | arc_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 5 | 0.2161 | 0.28 | ✅ accepted |
| 5 | align → lift → push → approach → approach → descend → grasp → rotate | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | arc_cartesian | linear_cartesian | — | impedance_motion | position_control | position_control | impedance_control | force_threshold_switch | position_control | admittance_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 6 | -0.1417 | 0.25 | ❌ rejected |
| 4 | approach → descend → grasp → approach → release → retract | linear_cartesian | linear_cartesian | — | arc_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | time_limit | pose_tolerance | 6 | -0.1449 | 0.17 | ❌ rejected |
| 3 | approach → descend → grasp → lift → approach → release | arc_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | admittance_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 6 | 0.0707 | 0.25 | ❌ rejected |

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

## Current Skill (Q=0.062) — your mutation base

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

- **Composite score**: 0.062
- **task_score** (E): 0.237
- **fitness_score**: 0.592  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Complexity Penalty**: 0.530

## Per-Phase Performance

| Phase | Normal Term. Rate | Mean Displacement (m) |
| ------- | ------------------- | ------------------------ |
| approach_1 | 1.00 | 0.1187 |
| descend_1 | 1.00 | 0.1475 |
| grasp_1 | 1.00 | 0.0118 |
| lift_1 | 1.00 | 0.1525 |
| transport_approach | 0.00 | 0.0016 |
| place_descend | 0.00 | 0.1210 |
| release_1 | 1.00 | 0.0234 |
| retract_1 | 1.00 | 0.2413 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end |
| --- | --- | --- | --- | --- | --- |
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.497, 0.038, 0.192) | (0.500, 0.024, 0.030)→(0.500, 0.024, 0.026) | 0.269→0.271 |
| descend_1 | descend | 1.00 / step_budget | (0.497, 0.038, 0.192)→(0.495, 0.025, 0.045) | (0.500, 0.024, 0.026)→(0.500, 0.024, 0.026) | 0.271→0.271 |
| grasp_1 | grasp | 1.00 / step_budget | (0.495, 0.025, 0.045)→(0.487, 0.025, 0.036) | (0.500, 0.024, 0.026)→(0.500, 0.025, 0.026) | 0.271→0.271 |
| lift_1 | lift | 1.00 / step_budget | (0.487, 0.025, 0.036)→(0.484, 0.024, 0.189) | (0.500, 0.025, 0.026)→(0.499, 0.024, 0.168) | 0.271→0.207 |
| transport_approach | approach | 0.00 / guard_failure | (0.481, 0.023, 0.198)→(0.481, 0.023, 0.199) | (0.499, 0.024, 0.168)→(0.497, 0.023, 0.177) | 0.207→0.208 |
| place_descend | descend | 0.00 / step_budget | (0.481, 0.023, 0.199)→(0.545, 0.120, 0.216) | (0.496, 0.022, 0.177)→(0.535, 0.084, 0.055) | 0.209→0.210 |
| release_1 | release | 1.00 / step_budget | (0.545, 0.120, 0.216)→(0.540, 0.119, 0.239) | (0.535, 0.084, 0.055)→(0.540, 0.084, 0.016) | 0.210→0.234 |
| retract_1 | retract | 1.00 / step_budget | (0.540, 0.119, 0.239)→(0.507, 0.018, 0.454) | (0.540, 0.084, 0.016)→(0.540, 0.084, 0.016) | 0.234→0.234 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.387
- phase_score: 0.181
- phase_breakdown.placement_score: 0.169
- phase_breakdown.approach_object_score: 0.072
- phase_breakdown.grasp_lift_score: 0.272
- grasp_place_fitness: 0.664

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.664
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.387
- **Median Q (composite search score)**: 0.044
- **K-run variance**: 0.0028
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.554


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.97368,"average_solve_count":190.0,"average_success_count":190.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.arc_height":0.05482,"descend_1.descend_offset_z":0.00182,"lift_1.lift_height":0.2325,"place_descend.place_z_offset":0.05684,"release_1.release_duration":0.19986,"transport_approach.arc_height_transport":0.14862,"transport_approach.transport_speed":0.10847},"optimized_scores":{"best_composite_score":0.00683,"best_fitness_score":0.53683,"best_task_score":0.11554},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":3637.0,"contact_point_centroid":[0.49149,-0.01701,-0.00232],"force_p95":0.12554,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.09727,"mean_force":0.13849,"phase_index":5.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.5168,0.05133,0.25623]},{"body_a":"world","body_b":"grasp_target","contact_count":80.0,"contact_point_centroid":[0.50073,-0.01315,-0.00144],"force_p95":0.64849,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.67227,"mean_force":0.14852,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48948,-0.01386,0.02928]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8600.0,"contact_point_centroid":[0.4907,0.00502,0.11922],"force_p95":0.14147,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33295,"mean_force":0.08099,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48721,-0.01381,0.11763]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":21.0,"contact_point_centroid":[0.49378,-0.03184,0.23516],"force_p95":0.33116,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33116,"mean_force":0.14683,"phase_index":4.0,"phase_name":"transport_approach","phase_type":"approach","tcp_position_centroid":[0.48777,-0.01392,0.24102]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":9338.0,"contact_point_centroid":[0.49057,-0.03255,0.11611],"force_p95":0.13772,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32142,"mean_force":0.07636,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48721,-0.01381,0.11497]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":12.0,"contact_point_centroid":[0.49448,-0.03244,0.23482],"force_p95":0.29767,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29767,"mean_force":0.16315,"phase_index":5.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.48699,-0.01448,0.24161]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50388,-0.01531,-0.00217],"force_p95":0.17267,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.25712,"mean_force":0.13582,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49199,-0.01388,0.02896]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":14.0,"contact_point_centroid":[0.49546,0.00346,0.2339],"force_p95":0.21473,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21983,"mean_force":0.13719,"phase_index":4.0,"phase_name":"transport_approach","phase_type":"approach","tcp_position_centroid":[0.48791,-0.01383,0.24087]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3894.0,"contact_point_centroid":[0.49162,0.00534,0.03057],"force_p95":0.08374,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15369,"mean_force":0.05389,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49082,-0.01387,0.02773]},{"body_a":"world","body_b":"grasp_target","contact_count":1160.0,"contact_point_centroid":[0.50382,-0.01567,-0.00189],"force_p95":0.13644,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12305,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49958,0.02643,0.24158]},{"body_a":"world","body_b":"grasp_target","contact_count":1844.0,"contact_point_centroid":[0.50382,-0.01567,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49829,-0.00515,0.10858]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.49142,-0.01703,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.538,0.09889,0.27336]},{"body_a":"world","body_b":"grasp_target","contact_count":824.0,"contact_point_centroid":[0.49142,-0.01703,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":7.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.5224,0.0598,0.36963]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5044.0,"contact_point_centroid":[0.49134,-0.03303,0.02961],"force_p95":0.07462,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08748,"mean_force":0.0446,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49083,-0.01387,0.02774]},{"body_a":"left_finger","body_b":"right_finger","contact_count":3657.0,"contact_point_centroid":[0.51845,0.0541,0.25928],"force_p95":0.01114,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01638,"mean_force":0.01057,"phase_index":5.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.51817,0.0541,0.25705]},{"body_a":"left_finger","body_b":"right_finger","contact_count":221.0,"contact_point_centroid":[0.5403,0.09937,0.27072],"force_p95":0.01096,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01262,"mean_force":0.01009,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.53987,0.09937,0.26847]}],"total_contact_groups":16},"final_pose_error":0.04991,"key_states":{"actual_goal_position":[0.58691,0.18745,0.24812],"final_object_position":[0.49142,-0.01703,0.01602],"final_tcp_position":[0.50827,0.01873,0.45448],"realised_goal_position":[0.58691,0.18745,0.24812],"realised_object_initial_position":[0.50382,-0.01567,0.03]},"phases":[{"n_steps":291.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.03],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.30942,"object_z_max":0.03,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"approach_object","tcp_end":[0.50019,0.00351,0.18204],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.15724,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":461.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"approach_object","tcp_end":[0.49898,-0.01391,0.03639],"tcp_start":[0.50019,0.00351,0.18204],"tcp_to_object_dist_end":0.01158,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50372,-0.01393,0.02544],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31155,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","subtask_id":"grasp_lift","tcp_end":[0.49079,-0.01387,0.0277],"tcp_start":[0.49898,-0.01391,0.03639],"tcp_to_object_dist_end":0.01312,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":671.0,"n_steps_budget":1000.0,"object_pos_end":[0.50296,-0.0143,0.21737],"object_pos_start":[0.50372,-0.01393,0.02544],"object_to_goal_dist_end":0.22067,"object_to_goal_dist_start":0.31155,"object_z_max":0.21744,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","subtask_id":"grasp_lift","tcp_end":[0.48788,-0.01382,0.24068],"tcp_start":[0.49079,-0.01387,0.0277],"tcp_to_object_dist_end":0.02777,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":7.0,"n_steps_budget":1000.0,"object_pos_end":[0.50254,-0.01495,0.21648],"object_pos_start":[0.50296,-0.0143,0.21737],"object_to_goal_dist_end":0.22155,"object_to_goal_dist_start":0.22067,"object_z_max":0.21737,"phase_name":"transport_approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"placement","tcp_end":[0.48709,-0.01436,0.24154],"tcp_start":[0.48764,-0.014,0.24124],"tcp_to_object_dist_end":0.02944,"terminated_normally":false,"termination_reason":"guard_failure"},{"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49142,-0.01703,0.01602],"object_pos_start":[0.50218,-0.01545,0.21528],"object_to_goal_dist_end":0.32373,"object_to_goal_dist_start":0.22232,"object_z_max":0.21528,"phase_name":"place_descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"placement","tcp_end":[0.54083,0.09931,0.27076],"tcp_start":[0.48709,-0.01436,0.24154],"tcp_to_object_dist_end":0.28437,"terminated_normally":false,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.49142,-0.01703,0.01602],"object_pos_start":[0.49142,-0.01703,0.01602],"object_to_goal_dist_end":0.32373,"object_to_goal_dist_start":0.32373,"object_z_max":0.01602,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","subtask_id":"placement","tcp_end":[0.53698,0.09864,0.29376],"tcp_start":[0.54083,0.09931,0.27076],"tcp_to_object_dist_end":0.30429,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":206.0,"n_steps_budget":1000.0,"object_pos_end":[0.49142,-0.01703,0.01602],"object_pos_start":[0.49142,-0.01703,0.01602],"object_to_goal_dist_end":0.32373,"object_to_goal_dist_start":0.32373,"object_z_max":0.01602,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","tcp_end":[0.50827,0.01873,0.45448],"tcp_start":[0.53698,0.09864,0.29376],"tcp_to_object_dist_end":0.44024,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.85714,"average_solve_count":203.0,"average_success_count":203.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.arc_height":0.09252,"descend_1.descend_offset_z":0.0142,"lift_1.lift_height":0.147,"place_descend.place_z_offset":0.02415,"release_1.release_duration":0.12231,"transport_approach.arc_height_transport":0.05047,"transport_approach.transport_speed":0.02745},"optimized_scores":{"best_composite_score":0.13406,"best_fitness_score":0.66406,"best_task_score":0.3872},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":462.0,"contact_point_centroid":[0.5931,0.12384,-0.004],"force_p95":1.01406,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.54176,"mean_force":0.22762,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.56879,0.1214,0.17128]},{"body_a":"world","body_b":"grasp_target","contact_count":75.0,"contact_point_centroid":[0.51005,0.03963,-0.00132],"force_p95":0.45913,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.4895,"mean_force":0.10642,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49822,0.03957,0.04093]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5969.0,"contact_point_centroid":[0.49824,0.05838,0.09855],"force_p95":0.10955,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32955,"mean_force":0.0719,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49578,0.03936,0.09622]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":9570.0,"contact_point_centroid":[0.53931,0.06383,0.17001],"force_p95":0.15022,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.3031,"mean_force":0.09452,"phase_index":5.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.53377,0.08228,0.16967]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6663.0,"contact_point_centroid":[0.49831,0.02058,0.09608],"force_p95":0.10587,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2845,"mean_force":0.06575,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49581,0.03936,0.09434]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":10400.0,"contact_point_centroid":[0.53933,0.10053,0.16962],"force_p95":0.1283,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23954,"mean_force":0.08761,"phase_index":5.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.53367,0.08219,0.16967]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":27.0,"contact_point_centroid":[0.58115,0.1053,0.15836],"force_p95":0.20787,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22209,"mean_force":0.134,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.57423,0.12268,0.16509]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":587.0,"contact_point_centroid":[0.5002,0.05833,0.17446],"force_p95":0.12338,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19146,"mean_force":0.08813,"phase_index":4.0,"phase_name":"transport_approach","phase_type":"approach","tcp_position_centroid":[0.49495,0.03962,0.17228]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":591.0,"contact_point_centroid":[0.50025,0.02101,0.17367],"force_p95":0.12514,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18113,"mean_force":0.08859,"phase_index":4.0,"phase_name":"transport_approach","phase_type":"approach","tcp_position_centroid":[0.49498,0.0396,0.17192]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":108.0,"contact_point_centroid":[0.57943,0.13825,0.15937],"force_p95":0.14493,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16028,"mean_force":0.05594,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.57387,0.12266,0.16445]},{"body_a":"world","body_b":"grasp_target","contact_count":1076.0,"contact_point_centroid":[0.51251,0.03972,-0.00188],"force_p95":0.1365,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12308,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50202,0.04137,0.25777]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.5125,0.03978,-0.00202],"force_p95":0.12832,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12859,"mean_force":0.12448,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.50064,0.03978,0.04093]},{"body_a":"world","body_b":"grasp_target","contact_count":1312.0,"contact_point_centroid":[0.59317,0.12323,-0.00199],"force_p95":0.12341,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12466,"mean_force":0.12269,"phase_index":7.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.5386,0.06896,0.31539]},{"body_a":"world","body_b":"grasp_target","contact_count":1808.0,"contact_point_centroid":[0.51251,0.03972,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50619,0.04585,0.12105]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4132.0,"contact_point_centroid":[0.49994,0.0589,0.04234],"force_p95":0.07523,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09793,"mean_force":0.05182,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49948,0.03968,0.03965]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4862.0,"contact_point_centroid":[0.50005,0.02063,0.04157],"force_p95":0.06822,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08757,"mean_force":0.04459,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49948,0.03968,0.03965]}],"total_contact_groups":16},"final_pose_error":0.04987,"key_states":{"actual_goal_position":[0.62757,0.17252,0.14502],"final_object_position":[0.59317,0.12323,0.01602],"final_tcp_position":[0.51002,0.01542,0.45364],"realised_goal_position":[0.62757,0.17252,0.14502],"realised_object_initial_position":[0.51251,0.03972,0.03]},"phases":[{"n_steps":270.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.03],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21001,"object_z_max":0.03,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"approach_object","tcp_end":[0.50741,0.05152,0.19532],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.16979,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":452.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"approach_object","tcp_end":[0.50758,0.0404,0.04868],"tcp_start":[0.50741,0.05152,0.19532],"tcp_to_object_dist_end":0.0232,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.5124,0.03987,0.02591],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21224,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","subtask_id":"grasp_lift","tcp_end":[0.49945,0.03968,0.03962],"tcp_start":[0.50758,0.0404,0.04868],"tcp_to_object_dist_end":0.01886,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":408.0,"n_steps_budget":930.0,"object_pos_end":[0.51213,0.03949,0.14825],"object_pos_start":[0.5124,0.03987,0.02591],"object_to_goal_dist_end":0.17616,"object_to_goal_dist_start":0.21224,"object_z_max":0.14798,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","subtask_id":"grasp_lift","tcp_end":[0.49587,0.03937,0.16713],"tcp_start":[0.49945,0.03968,0.03962],"tcp_to_object_dist_end":0.02492,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":48.0,"n_steps_budget":1000.0,"object_pos_end":[0.50981,0.04007,0.15835],"object_pos_start":[0.51213,0.03949,0.14825],"object_to_goal_dist_end":0.17773,"object_to_goal_dist_start":0.17616,"object_z_max":0.15892,"phase_name":"transport_approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"placement","tcp_end":[0.49434,0.04005,0.1788],"tcp_start":[0.49456,0.03998,0.17789],"tcp_to_object_dist_end":0.02564,"terminated_normally":false,"termination_reason":"guard_failure"},{"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5791,0.12284,0.13458],"object_pos_start":[0.50952,0.04009,0.15922],"object_to_goal_dist_end":0.07019,"object_to_goal_dist_start":0.17797,"object_z_max":0.15945,"phase_name":"place_descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"placement","tcp_end":[0.57431,0.12261,0.1653],"tcp_start":[0.49434,0.04005,0.1788],"tcp_to_object_dist_end":0.0311,"terminated_normally":false,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.59315,0.12312,0.01605],"object_pos_start":[0.5791,0.12284,0.13458],"object_to_goal_dist_end":0.14234,"object_to_goal_dist_start":0.07019,"object_z_max":0.13458,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","subtask_id":"placement","tcp_end":[0.56851,0.12133,0.18725],"tcp_start":[0.57431,0.12261,0.1653],"tcp_to_object_dist_end":0.17298,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":328.0,"n_steps_budget":1000.0,"object_pos_end":[0.59317,0.12323,0.01602],"object_pos_start":[0.59315,0.12312,0.01605],"object_to_goal_dist_end":0.14232,"object_to_goal_dist_start":0.14234,"object_z_max":0.01605,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","tcp_end":[0.51002,0.01542,0.45364],"tcp_start":[0.56851,0.12133,0.18725],"tcp_to_object_dist_end":0.45831,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.8984,"average_solve_count":187.0,"average_success_count":187.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.arc_height":0.04148,"descend_1.descend_offset_z":0.01412,"lift_1.lift_height":0.13631,"place_descend.place_z_offset":0.02439,"release_1.release_duration":0.40418,"transport_approach.arc_height_transport":0.09669,"transport_approach.transport_speed":0.11739},"optimized_scores":{"best_composite_score":0.04432,"best_fitness_score":0.57432,"best_task_score":0.20868},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":217.0,"contact_point_centroid":[0.53397,0.14529,-0.00718],"force_p95":1.03804,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.8591,"mean_force":0.34632,"phase_index":5.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.5189,0.13608,0.21066]},{"body_a":"world","body_b":"grasp_target","contact_count":73.0,"contact_point_centroid":[0.48024,0.04841,-0.00134],"force_p95":0.44468,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.4663,"mean_force":0.10463,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46952,0.04815,0.04225]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5707.0,"contact_point_centroid":[0.46889,0.06704,0.09652],"force_p95":0.1064,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31786,"mean_force":0.06751,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46722,0.04791,0.0942]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":7916.0,"contact_point_centroid":[0.49052,0.06517,0.19097],"force_p95":0.15166,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29831,"mean_force":0.09845,"phase_index":5.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.48499,0.0837,0.19022]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6488.0,"contact_point_centroid":[0.46896,0.02907,0.09433],"force_p95":0.10123,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27492,"mean_force":0.06066,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46724,0.04792,0.09253]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":731.0,"contact_point_centroid":[0.4691,0.0637,0.16914],"force_p95":0.1442,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25541,"mean_force":0.0952,"phase_index":4.0,"phase_name":"transport_approach","phase_type":"approach","tcp_position_centroid":[0.46391,0.04506,0.1674]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":732.0,"contact_point_centroid":[0.46918,0.0265,0.1693],"force_p95":0.1405,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23165,"mean_force":0.09468,"phase_index":4.0,"phase_name":"transport_approach","phase_type":"approach","tcp_position_centroid":[0.46389,0.04502,0.16752]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":9634.0,"contact_point_centroid":[0.49202,0.10363,0.19108],"force_p95":0.12331,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19458,"mean_force":0.08184,"phase_index":5.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.48608,0.08542,0.19085]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.48269,0.04872,-0.00203],"force_p95":0.13262,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.15969,"mean_force":0.12535,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47182,0.04839,0.04208]},{"body_a":"world","body_b":"grasp_target","contact_count":1052.0,"contact_point_centroid":[0.4827,0.04873,-0.00188],"force_p95":0.1365,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12309,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49277,0.04252,0.25929]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.53453,0.14514,-0.00196],"force_p95":0.12456,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12478,"mean_force":0.11891,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.51698,0.13758,0.21462]},{"body_a":"world","body_b":"grasp_target","contact_count":1856.0,"contact_point_centroid":[0.4827,0.04873,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.47961,0.05334,0.12233]},{"body_a":"world","body_b":"grasp_target","contact_count":1116.0,"contact_point_centroid":[0.53453,0.14514,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":7.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50893,0.07954,0.34087]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4403.0,"contact_point_centroid":[0.4707,0.06757,0.0433],"force_p95":0.07358,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09417,"mean_force":0.04935,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47072,0.04828,0.04094]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5079.0,"contact_point_centroid":[0.47066,0.02922,0.04297],"force_p95":0.06611,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09253,"mean_force":0.04266,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47071,0.04828,0.04094]},{"body_a":"left_finger","body_b":"right_finger","contact_count":222.0,"contact_point_centroid":[0.51965,0.13829,0.21173],"force_p95":0.01537,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01922,"mean_force":0.01112,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.51923,0.13826,0.20936]}],"total_contact_groups":16},"final_pose_error":0.04911,"key_states":{"actual_goal_position":[0.58187,0.22885,0.23048],"final_object_position":[0.53453,0.14514,0.01602],"final_tcp_position":[0.50359,0.02005,0.45531],"realised_goal_position":[0.58187,0.22885,0.23048],"realised_object_initial_position":[0.4827,0.04873,0.03]},"phases":[{"n_steps":264.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.03],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28719,"object_z_max":0.03,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"approach_object","tcp_end":[0.48326,0.05784,0.19741],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.17163,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":464.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"approach_object","tcp_end":[0.47847,0.04909,0.049],"tcp_start":[0.48326,0.05784,0.19741],"tcp_to_object_dist_end":0.02337,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.4826,0.04855,0.02587],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.29023,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","subtask_id":"grasp_lift","tcp_end":[0.47069,0.04828,0.04091],"tcp_start":[0.47847,0.04909,0.049],"tcp_to_object_dist_end":0.01919,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":362.0,"n_steps_budget":870.0,"object_pos_end":[0.48314,0.04819,0.13892],"object_pos_start":[0.4826,0.04855,0.02587],"object_to_goal_dist_end":0.22532,"object_to_goal_dist_start":0.29023,"object_z_max":0.13864,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","subtask_id":"grasp_lift","tcp_end":[0.46719,0.04791,0.15779],"tcp_start":[0.47069,0.04828,0.04091],"tcp_to_object_dist_end":0.02471,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":63.0,"n_steps_budget":1000.0,"object_pos_end":[0.47812,0.04317,0.15495],"object_pos_start":[0.48314,0.04819,0.13892],"object_to_goal_dist_end":0.22572,"object_to_goal_dist_start":0.22532,"object_z_max":0.15745,"phase_name":"transport_approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"placement","tcp_end":[0.46093,0.04208,0.17787],"tcp_start":[0.46198,0.04296,0.17494],"tcp_to_object_dist_end":0.02867,"terminated_normally":false,"termination_reason":"guard_failure"},{"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53469,0.14518,0.01452],"object_pos_start":[0.47693,0.04228,0.15772],"object_to_goal_dist_end":0.23636,"object_to_goal_dist_start":0.22609,"object_z_max":0.17642,"phase_name":"place_descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"placement","tcp_end":[0.52045,0.13844,0.2116],"tcp_start":[0.46093,0.04208,0.17787],"tcp_to_object_dist_end":0.1977,"terminated_normally":false,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53453,0.14514,0.01602],"object_pos_start":[0.53469,0.14518,0.01452],"object_to_goal_dist_end":0.23504,"object_to_goal_dist_start":0.23636,"object_z_max":0.01664,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","subtask_id":"placement","tcp_end":[0.51567,0.13719,0.23523],"tcp_start":[0.52045,0.13844,0.2116],"tcp_to_object_dist_end":0.22016,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":279.0,"n_steps_budget":1000.0,"object_pos_end":[0.53453,0.14514,0.01602],"object_pos_start":[0.53453,0.14514,0.01602],"object_to_goal_dist_end":0.23504,"object_to_goal_dist_start":0.23504,"object_z_max":0.01602,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","tcp_end":[0.50359,0.02005,0.45531],"tcp_start":[0.51567,0.13719,0.23523],"tcp_to_object_dist_end":0.4578,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```