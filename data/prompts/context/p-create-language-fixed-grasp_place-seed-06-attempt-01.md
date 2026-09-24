## Search State

- **Seed**: 6
- **Iteration**: 2 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 1 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 3 | 0.2721 | 0.19 | ❌ rejected |
| 0 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 2 | 0.3367 | 0.22 | ✅ accepted |

**Proposal policy**: task_score is 0.19 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

**Mode**: fixed (subtask targets are defined by the task configuration)

Available subtask IDs for phase binding:
| Subtask ID | Anchor | Target offset (m) | Metric | CMA-ES offset param |
|---|---|---|---|---|
| approach_1 | object | (0.00, 0.00, 0.00) | distance | approach_height |
| descend_1 | object | (0.00, 0.00, 0.02) | distance | grasp_z_offset |
| grasp_1 | object | (0.00, 0.00, 0.02) | contact | — |
| transport_arc | goal | (0.00, 0.00, 0.00) | distance | — |
| release_1 | goal | (0.00, 0.00, 0.00) | distance | — |

Annotate phases with `subtask_id: <id>` to bind them to a subtask target.
- A phase bound to a subtask receives a navigation waypoint computed from that subtask's anchor and offset.
- Only the **last phase** bound to a given subtask is used for subtask scoring.
- Phases without `subtask_id` are not scored against subtasks but still execute normally.

## Current Skill (Q=0.272) — your mutation base

```yaml
skill: grasp_place
dsl_version: 2
skill_type: arm_gripper
phases:
- id: approach_1
  type: approach
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
    - 0.0
    tolerance: 0.01
    orientation:
      mode: keep_current
  subtask_id: approach_1
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
    - 0.0
    tolerance: 0.01
    orientation:
      mode: keep_current
  subtask_id: descend_1
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
    orientation:
      mode: keep_current
  subtask_id: grasp_1
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
      distance: 0.1
      axis: world_z
      mode: add_to_offset
      sign: positive
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    lift_height:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.1
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
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
    tolerance: 0.01
    orientation:
      mode: keep_current
  subtask_id: transport_arc
- id: place_descend_1
  type: descend
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
      distance: 0.07
      axis: world_z
      mode: add_to_offset
      sign: negative
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    place_height:
      type: scalar
      range:
      - 0.02
      - 0.15
      default: 0.07
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
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
    orientation:
      mode: keep_current
  subtask_id: release_1

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.0], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings: none
- **descend_1** (`descend`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.0], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings: none
- **grasp_1** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings: none
- **lift_1** (`lift`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=world_z, distance=0.1, mode=add_to_offset, sign=positive}, tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset_along_axis.distance (replace)
- **transport_1** (`approach`)
  - target: source=yaml, anchor=task_goal, entity=placement_surface, offset=[0.0, 0.0, 0.0], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings: none
- **place_descend_1** (`descend`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=world_z, distance=0.07, mode=add_to_offset, sign=negative}, tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - place_height: status=consumed; consumers=target.offset_along_axis.distance (replace)
- **release_1** (`release`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings: none

## Design Metrics

- **Composite score**: 0.272
- **task_score** (E): 0.187
- **fitness_score**: 0.572  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.300

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.2650 |
| descend_1 | 1.00 | 1.00 | 0.0045 |
| grasp_1 | 1.00 | 1.00 | 0.0117 |
| lift_1 | 1.00 | 1.00 | 0.0988 |
| transport_1 | 0.00 | 1.00 | 0.1033 |
| place_descend_1 | 1.00 | 1.00 | 0.0968 |
| release_1 | 1.00 | 1.00 | 0.0251 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.495, 0.023, 0.038) | (0.500, 0.024, 0.030)→(0.500, 0.024, 0.026) | 0.269→0.271 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.495, 0.023, 0.038)→(0.494, 0.023, 0.034) | (0.500, 0.024, 0.026)→(0.500, 0.024, 0.026) | 0.271→0.271 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_1 | grasp | 1.00 / step_budget | (0.494, 0.023, 0.034)→(0.486, 0.023, 0.026) | (0.500, 0.024, 0.026)→(0.500, 0.023, 0.025) | 0.271→0.273 | 1.00 / 41.333 | 0.170 | 0.266 |
| lift_1 | lift | 1.00 / step_budget | (0.486, 0.023, 0.026)→(0.482, 0.022, 0.124) | (0.500, 0.023, 0.025)→(0.500, 0.023, 0.113) | 0.273→0.225 | 1.00 / 24.333 | 0.109 | 0.720 |
| transport_1 | approach | 0.00 / step_budget | (0.482, 0.022, 0.124)→(0.521, 0.082, 0.194) | (0.500, 0.023, 0.113)→(0.495, 0.055, 0.016) | 0.225→0.262 | 1.00 / 8.333 | 3249.666 | 1.523 |
| place_descend_1 | descend | 1.00 / step_budget | (0.521, 0.082, 0.194)→(0.517, 0.081, 0.097) | (0.495, 0.055, 0.016)→(0.495, 0.055, 0.016) | 0.262→0.262 | 1.00 / 8.667 | 91002.030 | 0.123 |
| release_1 | release | 1.00 / step_budget | (0.517, 0.081, 0.097)→(0.510, 0.080, 0.121) | (0.495, 0.055, 0.016)→(0.495, 0.055, 0.016) | 0.262→0.262 | 1.00 / 4.000 | 0.123 | 0.123 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.286
- phase_score: 0.345
- phase_breakdown.transport_arc_score: 0.126
- phase_breakdown.approach_1_score: 0.820
- phase_breakdown.grasp_1_score: 1.000
- phase_breakdown.release_1_score: 0.097
- phase_breakdown.descend_1_score: 0.704
- grasp_place_fitness: 0.621

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.621
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.286
- **Median Q (composite search score)**: 0.257
- **K-run variance**: 0.0012
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 10.0
- **Final σ (mean)**: 0.621


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.63265,"average_solve_count":147.0,"average_success_count":147.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"lift_1.lift_height":0.11562,"place_descend_1.place_height":0.10887,"transport_1.transport_arc_height":0.29812},"optimized_scores":{"best_composite_score":0.23843,"best_fitness_score":0.53843,"best_task_score":0.1202},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":2347.0,"contact_point_centroid":[0.4896,-0.00659,-0.00239],"force_p95":0.1517,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.61101,"mean_force":0.14366,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.50076,0.02175,0.19465]},{"body_a":"world","body_b":"grasp_target","contact_count":137.0,"contact_point_centroid":[0.50077,-0.0143,-0.00113],"force_p95":0.52166,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.72681,"mean_force":0.09086,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48857,-0.01487,0.02742]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":9768.0,"contact_point_centroid":[0.4888,0.00403,0.07431],"force_p95":0.10909,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33661,"mean_force":0.06932,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48597,-0.01482,0.0727]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3453.0,"contact_point_centroid":[0.49037,-0.02607,0.14278],"force_p95":0.14891,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32127,"mean_force":0.09698,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.48627,-0.00788,0.14555]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":10561.0,"contact_point_centroid":[0.48883,-0.03357,0.07333],"force_p95":0.10393,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.3104,"mean_force":0.06504,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.486,-0.01482,0.0722]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3161.0,"contact_point_centroid":[0.49026,0.01045,0.1431],"force_p95":0.15844,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24702,"mean_force":0.10137,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.48623,-0.00784,0.14572]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50383,-0.01544,-0.00207],"force_p95":0.14455,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.21802,"mean_force":0.12856,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49128,-0.0149,0.02688]},{"body_a":"world","body_b":"grasp_target","contact_count":3220.0,"contact_point_centroid":[0.50382,-0.01567,-0.00195],"force_p95":0.12703,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12278,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49845,-0.00738,0.1679]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4083.0,"contact_point_centroid":[0.49084,0.00431,0.02839],"force_p95":0.07818,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12773,"mean_force":0.05184,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49011,-0.01489,0.02566]},{"body_a":"world","body_b":"grasp_target","contact_count":88.0,"contact_point_centroid":[0.50382,-0.01567,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49831,-0.01489,0.03659]},{"body_a":"world","body_b":"grasp_target","contact_count":1200.0,"contact_point_centroid":[0.48952,-0.00655,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"place_descend_1","phase_type":"descend","tcp_position_centroid":[0.50844,0.04218,0.16689]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.48952,-0.00655,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.50254,0.04162,0.12012]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4937.0,"contact_point_centroid":[0.49084,-0.034,0.02749],"force_p95":0.07026,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08731,"mean_force":0.04475,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49011,-0.01489,0.02566]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2264.0,"contact_point_centroid":[0.50199,0.02365,0.19953],"force_p95":0.01148,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01587,"mean_force":0.01054,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.50174,0.02365,0.19715]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1275.0,"contact_point_centroid":[0.50868,0.04219,0.16915],"force_p95":0.01099,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01282,"mean_force":0.01049,"phase_index":5.0,"phase_name":"place_descend_1","phase_type":"descend","tcp_position_centroid":[0.50844,0.04218,0.16682]},{"body_a":"left_finger","body_b":"right_finger","contact_count":224.0,"contact_point_centroid":[0.50574,0.04187,0.1164],"force_p95":0.0109,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01091,"mean_force":0.00997,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.50533,0.04187,0.1141]}],"total_contact_groups":16},"final_pose_error":0.00991,"key_states":{"actual_goal_position":[0.58691,0.18745,0.24812],"final_object_position":[0.48952,-0.00655,0.01602],"final_tcp_position":[0.50731,0.04204,0.11667],"realised_goal_position":[0.58691,0.18745,0.24812],"realised_object_initial_position":[0.50382,-0.01567,0.03]},"peak_contact_force":1.61101,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":806.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.03],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.30942,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3220.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.49912,-0.01482,0.03851],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.01338,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":22.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":88.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.49821,-0.01497,0.03422],"tcp_start":[0.49912,-0.01482,0.03851],"tcp_to_object_dist_end":0.00995,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50368,-0.0148,0.02575],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31189,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.1396,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10820.0,"raw_peak_contact_force":0.21802,"subtask_id":"grasp_1","tcp_end":[0.49008,-0.01489,0.02563],"tcp_start":[0.49821,-0.01497,0.03422],"tcp_to_object_dist_end":0.0136,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":24.0,"n_steps":663.0,"n_steps_budget":750.0,"object_pos_end":[0.5037,-0.01485,0.11802],"object_pos_start":[0.50368,-0.0148,0.02575],"object_to_goal_dist_end":0.25451,"object_to_goal_dist_start":0.31189,"object_z_max":0.11792,"peak_contact_force":0.1121,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":20466.0,"raw_peak_contact_force":0.72681,"tcp_end":[0.48606,-0.01481,0.12961],"tcp_start":[0.49008,-0.01489,0.02563],"tcp_to_object_dist_end":0.0211,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.48952,-0.00655,0.01602],"object_pos_start":[0.5037,-0.01485,0.11802],"object_to_goal_dist_end":0.31779,"object_to_goal_dist_start":0.25451,"object_z_max":0.13873,"peak_contact_force":0.12263,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":11225.0,"raw_peak_contact_force":1.61101,"subtask_id":"transport_arc","tcp_end":[0.51129,0.04239,0.21648],"tcp_start":[0.48606,-0.01481,0.12961],"tcp_to_object_dist_end":0.20749,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":300.0,"n_steps_budget":1000.0,"object_pos_end":[0.48952,-0.00655,0.01602],"object_pos_start":[0.48952,-0.00655,0.01602],"object_to_goal_dist_end":0.31779,"object_to_goal_dist_start":0.31779,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"place_descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2475.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.50731,0.04204,0.11667],"tcp_start":[0.51129,0.04239,0.21648],"tcp_to_object_dist_end":0.11317,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.48952,-0.00655,0.01602],"object_pos_start":[0.48952,-0.00655,0.01602],"object_to_goal_dist_end":0.31779,"object_to_goal_dist_start":0.31779,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1024.0,"raw_peak_contact_force":0.12263,"subtask_id":"release_1","tcp_end":[0.50082,0.04146,0.14122],"tcp_start":[0.50731,0.04204,0.11667],"tcp_to_object_dist_end":0.13456,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.60714,"average_solve_count":140.0,"average_success_count":140.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"lift_1.lift_height":0.10859,"place_descend_1.place_height":0.07217,"transport_1.transport_arc_height":0.29986},"optimized_scores":{"best_composite_score":0.32078,"best_fitness_score":0.62078,"best_task_score":0.28644},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":2547.0,"contact_point_centroid":[0.51965,0.08949,-0.0023],"force_p95":0.13088,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.35387,"mean_force":0.13951,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.53388,0.0807,0.15002]},{"body_a":"world","body_b":"grasp_target","contact_count":146.0,"contact_point_centroid":[0.50898,0.03532,-0.00133],"force_p95":0.52774,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.71687,"mean_force":0.09788,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49669,0.03696,0.02678]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":7912.0,"contact_point_centroid":[0.49798,0.01794,0.07111],"force_p95":0.11249,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.36712,"mean_force":0.07705,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49419,0.03676,0.06884]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":9140.0,"contact_point_centroid":[0.49737,0.05553,0.06868],"force_p95":0.10686,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.34451,"mean_force":0.06892,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49422,0.03676,0.06708]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.51264,0.03918,-0.00225],"force_p95":0.19559,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.28627,"mean_force":0.14158,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49953,0.03719,0.02603]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2910.0,"contact_point_centroid":[0.50594,0.0659,0.12621],"force_p95":0.16472,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26964,"mean_force":0.10535,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.50196,0.04782,0.12917]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2686.0,"contact_point_centroid":[0.50547,0.02869,0.1258],"force_p95":0.16786,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23434,"mean_force":0.1035,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.50113,0.04686,0.1284]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3566.0,"contact_point_centroid":[0.5001,0.01792,0.02794],"force_p95":0.09159,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16443,"mean_force":0.05794,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49834,0.0371,0.02476]},{"body_a":"world","body_b":"grasp_target","contact_count":3296.0,"contact_point_centroid":[0.51251,0.03972,-0.00195],"force_p95":0.12693,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12277,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50254,0.01861,0.1676]},{"body_a":"world","body_b":"grasp_target","contact_count":92.0,"contact_point_centroid":[0.51251,0.03972,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50655,0.0375,0.03612]},{"body_a":"world","body_b":"grasp_target","contact_count":748.0,"contact_point_centroid":[0.51961,0.08962,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"place_descend_1","phase_type":"descend","tcp_position_centroid":[0.5508,0.10025,0.12562]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.51961,0.08962,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.54411,0.09894,0.09554]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4901.0,"contact_point_centroid":[0.49949,0.05634,0.02667],"force_p95":0.08099,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08793,"mean_force":0.04671,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49835,0.0371,0.02477]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2407.0,"contact_point_centroid":[0.5364,0.08288,0.15337],"force_p95":0.01125,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01565,"mean_force":0.01066,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.53602,0.08287,0.15108]},{"body_a":"left_finger","body_b":"right_finger","contact_count":793.0,"contact_point_centroid":[0.55132,0.10026,0.12772],"force_p95":0.01098,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01267,"mean_force":0.0105,"phase_index":5.0,"phase_name":"place_descend_1","phase_type":"descend","tcp_position_centroid":[0.55079,0.10025,0.12549]},{"body_a":"left_finger","body_b":"right_finger","contact_count":228.0,"contact_point_centroid":[0.54767,0.09956,0.09286],"force_p95":0.01098,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.011,"mean_force":0.00984,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.54722,0.09954,0.09028]}],"total_contact_groups":16},"final_pose_error":0.00986,"key_states":{"actual_goal_position":[0.62757,0.17252,0.14502],"final_object_position":[0.51961,0.08962,0.01602],"final_tcp_position":[0.54936,0.09994,0.0933],"realised_goal_position":[0.62757,0.17252,0.14502],"realised_object_initial_position":[0.51251,0.03972,0.03]},"peak_contact_force":9748.75244,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":825.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.03],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21001,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3296.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.50733,0.03737,0.03815],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.0134,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":23.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":92.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.50652,0.03773,0.03362],"tcp_start":[0.50733,0.03737,0.03815],"tcp_to_object_dist_end":0.00988,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":38.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51241,0.03713,0.02521],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21435,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.17807,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10267.0,"raw_peak_contact_force":0.28627,"subtask_id":"grasp_1","tcp_end":[0.49831,0.03709,0.02473],"tcp_start":[0.50652,0.03773,0.03362],"tcp_to_object_dist_end":0.0141,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":603.0,"n_steps_budget":690.0,"object_pos_end":[0.51203,0.03695,0.11044],"object_pos_start":[0.51241,0.03713,0.02521],"object_to_goal_dist_end":0.18145,"object_to_goal_dist_start":0.21435,"object_z_max":0.11034,"peak_contact_force":0.1104,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":17198.0,"raw_peak_contact_force":0.71687,"tcp_end":[0.49421,0.03677,0.12137],"tcp_start":[0.49831,0.03709,0.02473],"tcp_to_object_dist_end":0.0209,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51961,0.08962,0.01602],"object_pos_start":[0.51203,0.03695,0.11044],"object_to_goal_dist_end":0.18754,"object_to_goal_dist_start":0.18145,"object_z_max":0.11332,"peak_contact_force":9748.75244,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":10550.0,"raw_peak_contact_force":1.35387,"subtask_id":"transport_arc","tcp_end":[0.5537,0.10076,0.15666],"tcp_start":[0.49421,0.03677,0.12137],"tcp_to_object_dist_end":0.14514,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":187.0,"n_steps_budget":1000.0,"object_pos_end":[0.51961,0.08962,0.01602],"object_pos_start":[0.51961,0.08962,0.01602],"object_to_goal_dist_end":0.18754,"object_to_goal_dist_start":0.18754,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"place_descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1541.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.54936,0.09994,0.0933],"tcp_start":[0.5537,0.10076,0.15666],"tcp_to_object_dist_end":0.08345,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51961,0.08962,0.01602],"object_pos_start":[0.51961,0.08962,0.01602],"object_to_goal_dist_end":0.18754,"object_to_goal_dist_start":0.18754,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1028.0,"raw_peak_contact_force":0.12263,"subtask_id":"release_1","tcp_end":[0.5422,0.09856,0.11612],"tcp_start":[0.54936,0.09994,0.0933],"tcp_to_object_dist_end":0.10301,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.64474,"average_solve_count":152.0,"average_success_count":152.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"lift_1.lift_height":0.10686,"place_descend_1.place_height":0.13587,"transport_1.transport_arc_height":0.27511},"optimized_scores":{"best_composite_score":0.25701,"best_fitness_score":0.55701,"best_task_score":0.15375},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":1922.0,"contact_point_centroid":[0.47666,0.08119,-0.00245],"force_p95":0.22138,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.60495,"mean_force":0.14718,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.48802,0.08476,0.19201]},{"body_a":"world","body_b":"grasp_target","contact_count":146.0,"contact_point_centroid":[0.47922,0.04386,-0.00139],"force_p95":0.50143,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.71571,"mean_force":0.09526,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46872,0.0454,0.02858]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":9718.0,"contact_point_centroid":[0.46873,0.06409,0.06998],"force_p95":0.10494,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33524,"mean_force":0.06502,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46636,0.04518,0.06823]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.48283,0.04822,-0.0023],"force_p95":0.20708,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.29443,"mean_force":0.14516,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47143,0.04567,0.02756]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":9308.0,"contact_point_centroid":[0.46886,0.0263,0.07245],"force_p95":0.10747,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2944,"mean_force":0.06627,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46636,0.04518,0.07051]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4320.0,"contact_point_centroid":[0.47345,0.03532,0.14188],"force_p95":0.15425,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28509,"mean_force":0.09541,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.46855,0.05362,0.14293]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4641.0,"contact_point_centroid":[0.47336,0.07253,0.14296],"force_p95":0.15138,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.255,"mean_force":0.09479,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.4689,0.05423,0.14429]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4602.0,"contact_point_centroid":[0.47064,0.02633,0.0296],"force_p95":0.07905,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15344,"mean_force":0.04644,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47031,0.04556,0.02643]},{"body_a":"world","body_b":"grasp_target","contact_count":3252.0,"contact_point_centroid":[0.4827,0.04873,-0.00195],"force_p95":0.12703,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12278,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48852,0.02284,0.16791]},{"body_a":"world","body_b":"grasp_target","contact_count":92.0,"contact_point_centroid":[0.4827,0.04873,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.47832,0.046,0.03685]},{"body_a":"world","body_b":"grasp_target","contact_count":1548.0,"contact_point_centroid":[0.47653,0.08123,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"place_descend_1","phase_type":"descend","tcp_position_centroid":[0.49592,0.10137,0.14511]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.47653,0.08123,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.48988,0.10014,0.08531]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5466.0,"contact_point_centroid":[0.47023,0.06505,0.02883],"force_p95":0.07907,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08568,"mean_force":0.0428,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47032,0.04557,0.02644]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1754.0,"contact_point_centroid":[0.48961,0.08677,0.19658],"force_p95":0.01208,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01646,"mean_force":0.01083,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.4893,0.08676,0.19433]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1649.0,"contact_point_centroid":[0.49619,0.10139,0.14748],"force_p95":0.01099,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01269,"mean_force":0.01046,"phase_index":5.0,"phase_name":"place_descend_1","phase_type":"descend","tcp_position_centroid":[0.49593,0.10137,0.14517]},{"body_a":"left_finger","body_b":"right_finger","contact_count":219.0,"contact_point_centroid":[0.49317,0.10075,0.08129],"force_p95":0.01099,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01101,"mean_force":0.01015,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.49283,0.10073,0.07918]}],"total_contact_groups":16},"final_pose_error":0.00993,"key_states":{"actual_goal_position":[0.58187,0.22885,0.23048],"final_object_position":[0.47653,0.08123,0.01602],"final_tcp_position":[0.49485,0.10113,0.08163],"realised_goal_position":[0.58187,0.22885,0.23048],"realised_object_initial_position":[0.4827,0.04873,0.03]},"peak_contact_force":273005.84472,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":814.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.03],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28719,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3252.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.47923,0.04585,0.03883],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.01358,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":23.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":92.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.47812,0.04628,0.03436],"tcp_start":[0.47923,0.04585,0.03883],"tcp_to_object_dist_end":0.00983,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":45.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.48262,0.04588,0.02499],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.29251,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.19188,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11868.0,"raw_peak_contact_force":0.29443,"subtask_id":"grasp_1","tcp_end":[0.47028,0.04556,0.0264],"tcp_start":[0.47812,0.04628,0.03436],"tcp_to_object_dist_end":0.01242,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":26.0,"n_steps":603.0,"n_steps_budget":690.0,"object_pos_end":[0.4833,0.04548,0.11107],"object_pos_start":[0.48262,0.04588,0.02499],"object_to_goal_dist_end":0.24,"object_to_goal_dist_start":0.29251,"object_z_max":0.11097,"peak_contact_force":0.10336,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":19172.0,"raw_peak_contact_force":0.71571,"tcp_end":[0.46633,0.04519,0.12195],"tcp_start":[0.47028,0.04556,0.0264],"tcp_to_object_dist_end":0.02016,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.47653,0.08123,0.01602],"object_pos_start":[0.4833,0.04548,0.11107],"object_to_goal_dist_end":0.28087,"object_to_goal_dist_start":0.24,"object_z_max":0.14245,"peak_contact_force":0.12263,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":12637.0,"raw_peak_contact_force":1.60495,"subtask_id":"transport_arc","tcp_end":[0.49902,0.10196,0.20853],"tcp_start":[0.46633,0.04519,0.12195],"tcp_to_object_dist_end":0.19492,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":387.0,"n_steps_budget":1000.0,"object_pos_end":[0.47653,0.08123,0.01602],"object_pos_start":[0.47653,0.08123,0.01602],"object_to_goal_dist_end":0.28087,"object_to_goal_dist_start":0.28087,"object_z_max":0.01602,"peak_contact_force":273005.84472,"phase_name":"place_descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3197.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.49485,0.10113,0.08163],"tcp_start":[0.49902,0.10196,0.20853],"tcp_to_object_dist_end":0.07097,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.47653,0.08123,0.01602],"object_pos_start":[0.47653,0.08123,0.01602],"object_to_goal_dist_end":0.28087,"object_to_goal_dist_start":0.28087,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1019.0,"raw_peak_contact_force":0.12263,"subtask_id":"release_1","tcp_end":[0.48808,0.09977,0.10652],"tcp_start":[0.49485,0.10113,0.08163],"tcp_to_object_dist_end":0.0931,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```