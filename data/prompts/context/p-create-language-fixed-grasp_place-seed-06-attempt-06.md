## Search State

- **Seed**: 6
- **Iteration**: 7 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 6 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 3 | 0.2716 | 0.19 | ❌ rejected |
| 5 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 2 | 0.3370 | 0.22 | ✅ accepted |
| 4 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 5 | -0.0981 | 0.21 | ✅ accepted |
| 3 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 5 | 0.1049 | 0.21 | ✅ accepted |
| 2 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 6 | 0.2067 | 0.22 | ✅ accepted |

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
- **task_score** (E): 0.186
- **fitness_score**: 0.572  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.300

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.2650 |
| descend_1 | 1.00 | 1.00 | 0.0045 |
| grasp_1 | 1.00 | 1.00 | 0.0117 |
| lift_1 | 1.00 | 1.00 | 0.1021 |
| transport_1 | 0.00 | 1.00 | 0.1032 |
| place_descend_1 | 1.00 | 1.00 | 0.0773 |
| release_1 | 1.00 | 1.00 | 0.0249 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.495, 0.023, 0.038) | (0.500, 0.024, 0.030)→(0.500, 0.024, 0.026) | 0.269→0.271 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.495, 0.023, 0.038)→(0.494, 0.023, 0.034) | (0.500, 0.024, 0.026)→(0.500, 0.024, 0.026) | 0.271→0.271 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_1 | grasp | 1.00 / step_budget | (0.494, 0.023, 0.034)→(0.486, 0.023, 0.026) | (0.500, 0.024, 0.026)→(0.500, 0.023, 0.025) | 0.271→0.273 | 1.00 / 41.333 | 0.170 | 0.266 |
| lift_1 | lift | 1.00 / step_budget | (0.486, 0.023, 0.026)→(0.482, 0.022, 0.128) | (0.500, 0.023, 0.025)→(0.500, 0.023, 0.116) | 0.273→0.225 | 1.00 / 24.000 | 0.109 | 0.720 |
| transport_1 | approach | 0.00 / step_budget | (0.482, 0.022, 0.128)→(0.521, 0.082, 0.200) | (0.500, 0.023, 0.116)→(0.494, 0.056, 0.016) | 0.225→0.263 | 1.00 / 8.667 | 182004.581 | 1.535 |
| place_descend_1 | descend | 1.00 / step_budget | (0.521, 0.082, 0.200)→(0.517, 0.081, 0.123) | (0.494, 0.056, 0.016)→(0.494, 0.056, 0.016) | 0.263→0.263 | 1.00 / 8.000 | 3249.674 | 0.123 |
| release_1 | release | 1.00 / step_budget | (0.517, 0.081, 0.123)→(0.510, 0.080, 0.147) | (0.494, 0.056, 0.016)→(0.494, 0.056, 0.016) | 0.263→0.263 | 1.00 / 4.000 | 0.123 | 0.123 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.283
- phase_score: 0.332
- phase_breakdown.transport_arc_score: 0.104
- phase_breakdown.descend_1_score: 0.704
- phase_breakdown.grasp_1_score: 1.000
- phase_breakdown.approach_1_score: 0.820
- phase_breakdown.release_1_score: 0.091
- grasp_place_fitness: 0.619

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.619
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.283
- **Median Q (composite search score)**: 0.257
- **K-run variance**: 0.0012
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 10.0
- **Final σ (mean)**: 0.334


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.62238,"average_solve_count":143.0,"average_success_count":143.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"lift_1.lift_height":0.11074,"place_descend_1.place_height":0.09016,"transport_1.arc_height":0.29872},"optimized_scores":{"best_composite_score":0.23843,"best_fitness_score":0.53843,"best_task_score":0.12022},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":2229.0,"contact_point_centroid":[0.49005,-0.00669,-0.00237],"force_p95":0.16112,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.54575,"mean_force":0.1426,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.50048,0.02128,0.19209]},{"body_a":"world","body_b":"grasp_target","contact_count":137.0,"contact_point_centroid":[0.50077,-0.0143,-0.00113],"force_p95":0.52176,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.72758,"mean_force":0.09093,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48857,-0.01487,0.02742]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3820.0,"contact_point_centroid":[0.49048,-0.02585,0.13999],"force_p95":0.14633,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.4283,"mean_force":0.0962,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.48628,-0.00764,0.14237]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":9381.0,"contact_point_centroid":[0.48872,0.00404,0.07209],"force_p95":0.10893,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33658,"mean_force":0.06897,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48597,-0.01482,0.07045]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":10183.0,"contact_point_centroid":[0.48878,-0.03358,0.07127],"force_p95":0.10338,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31037,"mean_force":0.06454,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.486,-0.01482,0.07012]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3514.0,"contact_point_centroid":[0.49041,0.01066,0.14021],"force_p95":0.16004,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23301,"mean_force":0.10039,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.48622,-0.00765,0.14241]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50383,-0.01544,-0.00207],"force_p95":0.14455,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.21802,"mean_force":0.12856,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49128,-0.0149,0.02688]},{"body_a":"world","body_b":"grasp_target","contact_count":3220.0,"contact_point_centroid":[0.50382,-0.01567,-0.00195],"force_p95":0.12703,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12278,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49845,-0.00738,0.1679]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4083.0,"contact_point_centroid":[0.49084,0.00431,0.02839],"force_p95":0.07818,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12773,"mean_force":0.05184,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49011,-0.01489,0.02566]},{"body_a":"world","body_b":"grasp_target","contact_count":88.0,"contact_point_centroid":[0.50382,-0.01567,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49831,-0.01489,0.03659]},{"body_a":"world","body_b":"grasp_target","contact_count":980.0,"contact_point_centroid":[0.48991,-0.00671,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":5.0,"phase_name":"place_descend_1","phase_type":"descend","tcp_position_centroid":[0.50765,0.04034,0.17306]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.48991,-0.00671,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.50183,0.03978,0.13541]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4937.0,"contact_point_centroid":[0.49084,-0.034,0.02749],"force_p95":0.07026,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08731,"mean_force":0.04475,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49011,-0.01489,0.02566]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2120.0,"contact_point_centroid":[0.50171,0.0233,0.1971],"force_p95":0.01164,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01622,"mean_force":0.01056,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.50151,0.0233,0.19479]},{"body_a":"left_finger","body_b":"right_finger","contact_count":220.0,"contact_point_centroid":[0.50485,0.04002,0.1315],"force_p95":0.01097,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01273,"mean_force":0.01015,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.50455,0.04001,0.12943]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1051.0,"contact_point_centroid":[0.50789,0.04034,0.1755],"force_p95":0.01093,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01256,"mean_force":0.01039,"phase_index":5.0,"phase_name":"place_descend_1","phase_type":"descend","tcp_position_centroid":[0.50765,0.04034,0.17328]}],"total_contact_groups":16},"final_pose_error":0.00977,"key_states":{"actual_goal_position":[0.58691,0.18745,0.24812],"final_object_position":[0.48991,-0.00671,0.01602],"final_tcp_position":[0.50645,0.04018,0.13197],"realised_goal_position":[0.58691,0.18745,0.24812],"realised_object_initial_position":[0.50382,-0.01567,0.03]},"peak_contact_force":273007.14625,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":806.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.03],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.30942,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3220.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.49912,-0.01482,0.03851],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.01338,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":22.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":88.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.49821,-0.01497,0.03422],"tcp_start":[0.49912,-0.01482,0.03851],"tcp_to_object_dist_end":0.00995,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50368,-0.0148,0.02575],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31189,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.1396,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10820.0,"raw_peak_contact_force":0.21802,"subtask_id":"grasp_1","tcp_end":[0.49008,-0.01489,0.02563],"tcp_start":[0.49821,-0.01497,0.03422],"tcp_to_object_dist_end":0.0136,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":24.0,"n_steps":633.0,"n_steps_budget":720.0,"object_pos_end":[0.50374,-0.01477,0.11375],"object_pos_start":[0.50368,-0.0148,0.02575],"object_to_goal_dist_end":0.25664,"object_to_goal_dist_start":0.31189,"object_z_max":0.11365,"peak_contact_force":0.11404,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":19701.0,"raw_peak_contact_force":0.72758,"tcp_end":[0.48603,-0.01481,0.12475],"tcp_start":[0.49008,-0.01489,0.02563],"tcp_to_object_dist_end":0.02085,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.48991,-0.00671,0.01602],"object_pos_start":[0.50374,-0.01477,0.11375],"object_to_goal_dist_end":0.31777,"object_to_goal_dist_start":0.25664,"object_z_max":0.1379,"peak_contact_force":273007.14625,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":11683.0,"raw_peak_contact_force":1.54575,"subtask_id":"transport_arc","tcp_end":[0.51028,0.0405,0.21315],"tcp_start":[0.48603,-0.01481,0.12475],"tcp_to_object_dist_end":0.20372,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":245.0,"n_steps_budget":1000.0,"object_pos_end":[0.48991,-0.00671,0.01602],"object_pos_start":[0.48991,-0.00671,0.01602],"object_to_goal_dist_end":0.31777,"object_to_goal_dist_start":0.31777,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"place_descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2031.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.50645,0.04018,0.13197],"tcp_start":[0.51028,0.0405,0.21315],"tcp_to_object_dist_end":0.12616,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.48991,-0.00671,0.01602],"object_pos_start":[0.48991,-0.00671,0.01602],"object_to_goal_dist_end":0.31777,"object_to_goal_dist_start":0.31777,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1020.0,"raw_peak_contact_force":0.12263,"subtask_id":"release_1","tcp_end":[0.50018,0.03964,0.15649],"tcp_start":[0.50645,0.04018,0.13197],"tcp_to_object_dist_end":0.14827,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.61702,"average_solve_count":141.0,"average_success_count":141.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"lift_1.lift_height":0.1159,"place_descend_1.place_height":0.08194,"transport_1.arc_height":0.19457},"optimized_scores":{"best_composite_score":0.31915,"best_fitness_score":0.61915,"best_task_score":0.28318},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":2481.0,"contact_point_centroid":[0.51465,0.09067,-0.00238],"force_p95":0.20122,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.47619,"mean_force":0.14531,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.52981,0.07639,0.16755]},{"body_a":"world","body_b":"grasp_target","contact_count":150.0,"contact_point_centroid":[0.50907,0.0354,-0.00133],"force_p95":0.50892,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.71367,"mean_force":0.09756,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49667,0.03695,0.02678]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8885.0,"contact_point_centroid":[0.49791,0.01797,0.07487],"force_p95":0.11196,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.36523,"mean_force":0.07545,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49416,0.03676,0.07284]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":9976.0,"contact_point_centroid":[0.49737,0.05554,0.07183],"force_p95":0.10744,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.34324,"mean_force":0.06923,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.4942,0.03676,0.0703]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.51264,0.03918,-0.00225],"force_p95":0.19559,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.28627,"mean_force":0.14158,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49953,0.03719,0.02603]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2474.0,"contact_point_centroid":[0.50262,0.0261,0.13491],"force_p95":0.16649,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27609,"mean_force":0.10418,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.49868,0.04428,0.1381]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2783.0,"contact_point_centroid":[0.50292,0.06292,0.13548],"force_p95":0.15865,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26916,"mean_force":0.10298,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.49923,0.0449,0.13892]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3566.0,"contact_point_centroid":[0.5001,0.01792,0.02794],"force_p95":0.09159,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16443,"mean_force":0.05794,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49834,0.0371,0.02476]},{"body_a":"world","body_b":"grasp_target","contact_count":3296.0,"contact_point_centroid":[0.51251,0.03972,-0.00195],"force_p95":0.12693,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12277,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50254,0.01861,0.1676]},{"body_a":"world","body_b":"grasp_target","contact_count":92.0,"contact_point_centroid":[0.51251,0.03972,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50655,0.0375,0.03612]},{"body_a":"world","body_b":"grasp_target","contact_count":852.0,"contact_point_centroid":[0.51515,0.09167,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":5.0,"phase_name":"place_descend_1","phase_type":"descend","tcp_position_centroid":[0.54685,0.09608,0.14009]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.51515,0.09167,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.54032,0.09484,0.10541]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4901.0,"contact_point_centroid":[0.49949,0.05634,0.02667],"force_p95":0.08099,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08793,"mean_force":0.04671,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49835,0.0371,0.02477]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2512.0,"contact_point_centroid":[0.53131,0.07745,0.17048],"force_p95":0.01119,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01611,"mean_force":0.01059,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.53084,0.07744,0.16827]},{"body_a":"left_finger","body_b":"right_finger","contact_count":899.0,"contact_point_centroid":[0.54731,0.09609,0.14236],"force_p95":0.01103,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01287,"mean_force":0.01056,"phase_index":5.0,"phase_name":"place_descend_1","phase_type":"descend","tcp_position_centroid":[0.54685,0.09608,0.1402]},{"body_a":"left_finger","body_b":"right_finger","contact_count":223.0,"contact_point_centroid":[0.54379,0.09543,0.10233],"force_p95":0.01091,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01093,"mean_force":0.01,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.54334,0.09541,0.10008]}],"total_contact_groups":16},"final_pose_error":0.01,"key_states":{"actual_goal_position":[0.62757,0.17252,0.14502],"final_object_position":[0.51515,0.09167,0.01602],"final_tcp_position":[0.54544,0.09579,0.10307],"realised_goal_position":[0.62757,0.17252,0.14502],"realised_object_initial_position":[0.51251,0.03972,0.03]},"peak_contact_force":1.47619,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":825.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.03],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21001,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3296.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.50733,0.03737,0.03815],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.0134,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":23.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":92.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.50652,0.03773,0.03362],"tcp_start":[0.50733,0.03737,0.03815],"tcp_to_object_dist_end":0.00988,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":38.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51241,0.03713,0.02521],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21435,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.17807,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10267.0,"raw_peak_contact_force":0.28627,"subtask_id":"grasp_1","tcp_end":[0.49831,0.03709,0.02473],"tcp_start":[0.50652,0.03773,0.03362],"tcp_to_object_dist_end":0.0141,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":663.0,"n_steps_budget":750.0,"object_pos_end":[0.5119,0.03702,0.11697],"object_pos_start":[0.51241,0.03713,0.02521],"object_to_goal_dist_end":0.18035,"object_to_goal_dist_start":0.21435,"object_z_max":0.11687,"peak_contact_force":0.11117,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":19011.0,"raw_peak_contact_force":0.71367,"tcp_end":[0.49426,0.03678,0.1288],"tcp_start":[0.49831,0.03709,0.02473],"tcp_to_object_dist_end":0.02125,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51515,0.09167,0.01602],"object_pos_start":[0.5119,0.03702,0.11697],"object_to_goal_dist_end":0.18925,"object_to_goal_dist_start":0.18035,"object_z_max":0.12437,"peak_contact_force":0.12263,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":10250.0,"raw_peak_contact_force":1.47619,"subtask_id":"transport_arc","tcp_end":[0.54975,0.09657,0.17603],"tcp_start":[0.49426,0.03678,0.1288],"tcp_to_object_dist_end":0.16378,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":213.0,"n_steps_budget":1000.0,"object_pos_end":[0.51515,0.09167,0.01602],"object_pos_start":[0.51515,0.09167,0.01602],"object_to_goal_dist_end":0.18925,"object_to_goal_dist_start":0.18925,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"place_descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1751.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.54544,0.09579,0.10307],"tcp_start":[0.54975,0.09657,0.17603],"tcp_to_object_dist_end":0.09226,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51515,0.09167,0.01602],"object_pos_start":[0.51515,0.09167,0.01602],"object_to_goal_dist_end":0.18925,"object_to_goal_dist_start":0.18925,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1023.0,"raw_peak_contact_force":0.12263,"subtask_id":"release_1","tcp_end":[0.53846,0.09449,0.12603],"tcp_start":[0.54544,0.09579,0.10307],"tcp_to_object_dist_end":0.11249,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.625,"average_solve_count":144.0,"average_success_count":144.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"lift_1.lift_height":0.11431,"place_descend_1.place_height":0.08649,"transport_1.arc_height":0.29964},"optimized_scores":{"best_composite_score":0.25708,"best_fitness_score":0.55708,"best_task_score":0.1539},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":2191.0,"contact_point_centroid":[0.47567,0.08219,-0.0024],"force_p95":0.17671,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.58431,"mean_force":0.14469,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.4897,0.08735,0.19246]},{"body_a":"world","body_b":"grasp_target","contact_count":142.0,"contact_point_centroid":[0.47913,0.04377,-0.00139],"force_p95":0.50572,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.71911,"mean_force":0.0955,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46874,0.0454,0.02859]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":9963.0,"contact_point_centroid":[0.46893,0.06409,0.07309],"force_p95":0.10531,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33649,"mean_force":0.0661,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46638,0.04518,0.07133]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":9459.0,"contact_point_centroid":[0.46918,0.02632,0.07531],"force_p95":0.10735,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29635,"mean_force":0.06809,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46638,0.04518,0.07329]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.48283,0.04822,-0.0023],"force_p95":0.20708,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.29443,"mean_force":0.14516,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47143,0.04567,0.02756]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3472.0,"contact_point_centroid":[0.47381,0.03563,0.14471],"force_p95":0.16177,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28199,"mean_force":0.09936,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.46886,0.05387,0.14618]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3759.0,"contact_point_centroid":[0.47375,0.07287,0.14589],"force_p95":0.15367,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25704,"mean_force":0.09866,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.46929,0.05467,0.14769]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4602.0,"contact_point_centroid":[0.47064,0.02633,0.0296],"force_p95":0.07905,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15344,"mean_force":0.04644,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47031,0.04556,0.02643]},{"body_a":"world","body_b":"grasp_target","contact_count":3252.0,"contact_point_centroid":[0.4827,0.04873,-0.00195],"force_p95":0.12703,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12278,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48852,0.02284,0.16791]},{"body_a":"world","body_b":"grasp_target","contact_count":92.0,"contact_point_centroid":[0.4827,0.04873,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.47832,0.046,0.03685]},{"body_a":"world","body_b":"grasp_target","contact_count":940.0,"contact_point_centroid":[0.47556,0.08221,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":5.0,"phase_name":"place_descend_1","phase_type":"descend","tcp_position_centroid":[0.49996,0.10695,0.17173]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.47556,0.08221,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.49427,0.10571,0.13591]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5466.0,"contact_point_centroid":[0.47023,0.06505,0.02883],"force_p95":0.07907,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08568,"mean_force":0.0428,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47032,0.04557,0.02644]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2059.0,"contact_point_centroid":[0.49127,0.08931,0.19681],"force_p95":0.01129,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01626,"mean_force":0.01072,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.49094,0.0893,0.19455]},{"body_a":"left_finger","body_b":"right_finger","contact_count":997.0,"contact_point_centroid":[0.50037,0.10697,0.17422],"force_p95":0.01099,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0128,"mean_force":0.01051,"phase_index":5.0,"phase_name":"place_descend_1","phase_type":"descend","tcp_position_centroid":[0.49998,0.10695,0.17195]},{"body_a":"left_finger","body_b":"right_finger","contact_count":217.0,"contact_point_centroid":[0.49729,0.1063,0.1322],"force_p95":0.01101,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01274,"mean_force":0.01023,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.49693,0.10628,0.12994]}],"total_contact_groups":16},"final_pose_error":0.0098,"key_states":{"actual_goal_position":[0.58187,0.22885,0.23048],"final_object_position":[0.47556,0.08221,0.01602],"final_tcp_position":[0.49879,0.10667,0.13249],"realised_goal_position":[0.58187,0.22885,0.23048],"realised_object_initial_position":[0.4827,0.04873,0.03]},"peak_contact_force":273006.47469,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":814.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.03],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28719,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3252.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.47923,0.04585,0.03883],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.01358,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":23.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":92.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.47812,0.04628,0.03436],"tcp_start":[0.47923,0.04585,0.03883],"tcp_to_object_dist_end":0.00983,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":45.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.48262,0.04588,0.02499],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.29251,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.19188,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11868.0,"raw_peak_contact_force":0.29443,"subtask_id":"grasp_1","tcp_end":[0.47028,0.04556,0.0264],"tcp_start":[0.47812,0.04628,0.03436],"tcp_to_object_dist_end":0.01242,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":25.0,"n_steps":633.0,"n_steps_budget":720.0,"object_pos_end":[0.48325,0.04542,0.11732],"object_pos_start":[0.48262,0.04588,0.02499],"object_to_goal_dist_end":0.23702,"object_to_goal_dist_start":0.29251,"object_z_max":0.11722,"peak_contact_force":0.10287,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":19564.0,"raw_peak_contact_force":0.71911,"tcp_end":[0.46638,0.04519,0.12923],"tcp_start":[0.47028,0.04556,0.0264],"tcp_to_object_dist_end":0.02065,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.47556,0.08221,0.01602],"object_pos_start":[0.48325,0.04542,0.11732],"object_to_goal_dist_end":0.28072,"object_to_goal_dist_start":0.23702,"object_z_max":0.14113,"peak_contact_force":273006.47469,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":11481.0,"raw_peak_contact_force":1.58431,"subtask_id":"transport_arc","tcp_end":[0.50253,0.10745,0.20995],"tcp_start":[0.46638,0.04519,0.12923],"tcp_to_object_dist_end":0.19742,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":235.0,"n_steps_budget":1000.0,"object_pos_end":[0.47556,0.08221,0.01602],"object_pos_start":[0.47556,0.08221,0.01602],"object_to_goal_dist_end":0.28072,"object_to_goal_dist_start":0.28072,"object_z_max":0.01602,"peak_contact_force":9748.77609,"phase_name":"place_descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1937.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.49879,0.10667,0.13249],"tcp_start":[0.50253,0.10745,0.20995],"tcp_to_object_dist_end":0.12126,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.47556,0.08221,0.01602],"object_pos_start":[0.47556,0.08221,0.01602],"object_to_goal_dist_end":0.28072,"object_to_goal_dist_start":0.28072,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1017.0,"raw_peak_contact_force":0.12263,"subtask_id":"release_1","tcp_end":[0.49265,0.10536,0.15698],"tcp_start":[0.49879,0.10667,0.13249],"tcp_to_object_dist_end":0.14387,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```