## Search State

- **Seed**: 6
- **Iteration**: 7 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 6 | approach → descend → grasp → lift → approach → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | time_limit | 9 | 0.0512 | 0.29 | ❌ rejected |
| 5 | approach → descend → grasp → lift → approach → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | time_limit | 8 | 0.1050 | 0.30 | ❌ rejected |
| 4 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 10 | -0.0191 | 0.31 | ❌ rejected |
| 3 | approach → descend → grasp → lift → approach → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | time_limit | 8 | 0.2021 | 0.49 | ✅ accepted |
| 2 | approach → descend → grasp → lift → approach → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | time_limit | 8 | -0.1415 | 0.25 | ✅ accepted |

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

## Current Skill (Q=0.051) — your mutation base

```yaml
skill: grasp_place
dsl_version: 2
skill_type: arm_gripper
phases:
- id: approach_to_object
  type: approach
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
  parameters:
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: add
  subtask_id: approach_1
- id: descend_to_grasp
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
  parameters:
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.03
      binds_to:
      - path: generator.speed
        mode: add
  subtask_id: descend_1
- id: grasp_object
  type: grasp
  control: position_control
  termination: time_limit
  end_effector_action: force_grasp
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.0
    - 0.0
  parameters:
    max_time:
      type: scalar
      range:
      - 0.1
      - 1.0
      default: 0.5
      binds_to:
      - path: duration.max_time
        mode: add
  subtask_id: grasp_1
- id: lift_object
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
  parameters:
    lift_height:
      type: scalar
      range:
      - 0.05
      - 0.3
      default: 0.15
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: add
- id: transport_to_goal
  type: approach
  generator: arc_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.0
  parameters:
    arc_height:
      type: scalar
      range:
      - 0.05
      - 0.3
      default: 0.15
      binds_to:
      - path: generator.arc_height
        mode: add
    speed:
      type: scalar
      range:
      - 0.01
      - 0.2
      default: 0.08
      binds_to:
      - path: generator.speed
        mode: add
  subtask_id: transport_arc
- id: release_at_goal
  type: release
  control: position_control
  termination: time_limit
  end_effector_action: open
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.0
  parameters:
    max_time:
      type: scalar
      range:
      - 0.1
      - 1.0
      default: 0.3
      binds_to:
      - path: duration.max_time
        mode: add
  guards:
  - id: object_still_grasped
    when: before_phase
    predicate: bilateral_grasp
    threshold: 0.5
    on_failure: retry
  retries:
    max_attempts: 1
    strategy: offset_target
    offset:
    - 0.0
    - 0.0
    - 0.01
  subtask_id: release_1

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_to_object** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.0]
  - parameter_bindings:
    - speed: status=consumed; consumers=generator.speed (add)
- **descend_to_grasp** (`descend`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.0]
  - parameter_bindings:
    - speed: status=consumed; consumers=generator.speed (add)
- **grasp_object** (`grasp`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.0]
  - parameter_bindings:
    - max_time: status=consumed; consumers=duration.max_time (add)
- **lift_object** (`lift`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=world_z, distance=0.2, mode=add_to_offset, sign=positive}
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - speed: status=consumed; consumers=generator.speed (add)
- **transport_to_goal** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0]
  - parameter_bindings:
    - arc_height: status=consumed; consumers=generator.arc_height (add)
    - speed: status=consumed; consumers=generator.speed (add)
- **release_at_goal** (`release`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0]
  - parameter_bindings:
    - max_time: status=consumed; consumers=duration.max_time (add)
  - guards:
    - id=object_still_grasped, when=before_phase, predicate=bilateral_grasp, on_failure=retry, threshold=0.5
  - retries: max_attempts=1, strategy=offset_target, offset=[0.0, 0.0, 0.01]

## Design Metrics

- **Composite score**: 0.051
- **task_score** (E): 0.288
- **fitness_score**: 0.621  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.570

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_to_object | 1.00 | 1.00 | 0.2652 |
| descend_to_grasp | 1.00 | 1.00 | 0.0046 |
| grasp_object | 1.00 | 1.00 | 0.0124 |
| lift_object | 0.67 | 1.00 | 0.1313 |
| transport_to_goal | 1.00 | 1.00 | 0.2046 |
| release_at_goal | 1.00 | 1.00 | 0.0163 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_to_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.495, 0.023, 0.038) | (0.500, 0.024, 0.030)→(0.500, 0.024, 0.026) | 0.269→0.271 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_to_grasp | descend | 1.00 / step_budget | (0.495, 0.023, 0.038)→(0.494, 0.023, 0.034) | (0.500, 0.024, 0.026)→(0.500, 0.024, 0.026) | 0.271→0.271 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_object | grasp | 1.00 / step_budget | (0.494, 0.023, 0.034)→(0.485, 0.023, 0.025) | (0.500, 0.024, 0.026)→(0.500, 0.023, 0.025) | 0.271→0.273 | 1.00 / 42.000 | 0.176 | 0.251 |
| lift_object | lift | 0.67 / step_budget | (0.485, 0.023, 0.025)→(0.482, 0.022, 0.156) | (0.500, 0.023, 0.025)→(0.495, 0.023, 0.145) | 0.273→0.221 | 1.00 / 30.667 | 0.101 | 0.761 |
| transport_to_goal | approach | 1.00 / step_budget | (0.482, 0.022, 0.156)→(0.580, 0.170, 0.237) | (0.495, 0.023, 0.145)→(0.584, 0.160, 0.136) | 0.221→0.094 | 1.00 / 28.667 | 3249.589 | 0.920 |
| release_at_goal | release | 1.00 / step_budget | (0.580, 0.170, 0.237)→(0.576, 0.169, 0.250) | (0.584, 0.160, 0.136)→(0.582, 0.158, 0.016) | 0.094→0.197 | 1.00 / 4.667 | 0.131 | 1.209 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.446
- phase_score: 0.605
- phase_breakdown.transport_arc_score: 0.529
- phase_breakdown.release_1_score: 0.353
- phase_breakdown.approach_1_score: 0.820
- phase_breakdown.grasp_1_score: 1.000
- phase_breakdown.descend_1_score: 0.699
- grasp_place_fitness: 0.699

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.699
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.446
- **Median Q (composite search score)**: 0.021
- **K-run variance**: 0.0031
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.259


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.53676,"average_solve_count":136.0,"average_success_count":136.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_to_object.speed":0.0461,"descend_to_grasp.speed":0.03819,"grasp_object.max_time":0.63144,"lift_object.lift_height":0.16729,"lift_object.speed":0.02982,"release_at_goal.max_time":0.70294,"transport_to_goal.arc_height":0.21358,"transport_to_goal.speed":0.17837,"transport_to_goal.target_z_offset":0.02121},"optimized_scores":{"best_composite_score":0.00395,"best_fitness_score":0.57395,"best_task_score":0.19386},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":132.0,"contact_point_centroid":[0.57297,0.1507,-0.00993],"force_p95":1.66196,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.144,"mean_force":0.62679,"phase_index":5.0,"phase_name":"release_at_goal","phase_type":"release","tcp_position_centroid":[0.56251,0.15107,0.27672]},{"body_a":"world","body_b":"grasp_target","contact_count":179.0,"contact_point_centroid":[0.49827,-0.01444,-0.00114],"force_p95":0.48237,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.66814,"mean_force":0.12409,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.48747,-0.01495,0.02632]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":16676.0,"contact_point_centroid":[0.52284,0.03946,0.20587],"force_p95":0.08737,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30121,"mean_force":0.05971,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.51881,0.05807,0.2051]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":17597.0,"contact_point_centroid":[0.48543,-0.03409,0.0758],"force_p95":0.0796,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28399,"mean_force":0.05711,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.48481,-0.01492,0.07328]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":20296.0,"contact_point_centroid":[0.48627,0.00407,0.07285],"force_p95":0.07543,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28098,"mean_force":0.05077,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.48482,-0.01492,0.07105]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50383,-0.01566,-0.00205],"force_p95":0.14099,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.1841,"mean_force":0.12715,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.49053,-0.01497,0.02604]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":16411.0,"contact_point_centroid":[0.51852,0.07561,0.20487],"force_p95":0.0893,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18173,"mean_force":0.06009,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.51806,0.05662,0.20371]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1118.0,"contact_point_centroid":[0.5622,0.17086,0.25874],"force_p95":0.07256,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16719,"mean_force":0.04685,"phase_index":5.0,"phase_name":"release_at_goal","phase_type":"release","tcp_position_centroid":[0.56537,0.15204,0.25709]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1179.0,"contact_point_centroid":[0.5711,0.13365,0.25682],"force_p95":0.07051,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16137,"mean_force":0.04434,"phase_index":5.0,"phase_name":"release_at_goal","phase_type":"release","tcp_position_centroid":[0.56531,0.15201,0.25695]},{"body_a":"world","body_b":"grasp_target","contact_count":3240.0,"contact_point_centroid":[0.50382,-0.01567,-0.00195],"force_p95":0.12703,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12278,"phase_index":0.0,"phase_name":"approach_to_object","phase_type":"approach","tcp_position_centroid":[0.49825,-0.00736,0.1684]},{"body_a":"world","body_b":"grasp_target","contact_count":92.0,"contact_point_centroid":[0.50382,-0.01567,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.49798,-0.01491,0.03637]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5293.0,"contact_point_centroid":[0.49027,0.00408,0.02684],"force_p95":0.064,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10186,"mean_force":0.04106,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.48928,-0.01496,0.02475]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4185.0,"contact_point_centroid":[0.48902,-0.03426,0.02753],"force_p95":0.07757,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08855,"mean_force":0.05192,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.48929,-0.01496,0.02475]}],"total_contact_groups":13},"final_pose_error":0.04185,"key_states":{"actual_goal_position":[0.58691,0.18745,0.24812],"final_object_position":[0.57331,0.15316,0.0048],"final_tcp_position":[0.56661,0.15208,0.25994],"realised_goal_position":[0.58691,0.18745,0.24812],"realised_object_initial_position":[0.50382,-0.01567,0.03]},"peak_contact_force":2.144,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":811.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.03],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.30942,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_to_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3240.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.49882,-0.01484,0.03844],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.01341,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":23.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":92.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.49789,-0.01501,0.03379],"tcp_start":[0.49882,-0.01484,0.03844],"tcp_to_object_dist_end":0.0098,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50367,-0.01534,0.0258],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31221,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.14038,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11278.0,"raw_peak_contact_force":0.1841,"subtask_id":"grasp_1","tcp_end":[0.48925,-0.01496,0.02471],"tcp_start":[0.49789,-0.01501,0.03379],"tcp_to_object_dist_end":0.01446,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.4964,-0.01528,0.11343],"object_pos_start":[0.50367,-0.01534,0.0258],"object_to_goal_dist_end":0.25967,"object_to_goal_dist_start":0.31221,"object_z_max":0.11333,"peak_contact_force":0.08131,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":38072.0,"raw_peak_contact_force":0.66814,"tcp_end":[0.48497,-0.01492,0.12172],"tcp_start":[0.48925,-0.01496,0.02471],"tcp_to_object_dist_end":0.01413,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":38.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.57291,0.15416,0.24283],"object_pos_start":[0.4964,-0.01528,0.11343],"object_to_goal_dist_end":0.03649,"object_to_goal_dist_start":0.25967,"object_z_max":0.24282,"peak_contact_force":0.07261,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":33087.0,"raw_peak_contact_force":0.30121,"subtask_id":"transport_arc","tcp_end":[0.56661,0.15208,0.25994],"tcp_start":[0.48497,-0.01492,0.12172],"tcp_to_object_dist_end":0.01835,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.57331,0.15316,0.0048],"object_pos_start":[0.57291,0.15416,0.24283],"object_to_goal_dist_end":0.2461,"object_to_goal_dist_start":0.03649,"object_z_max":0.24283,"peak_contact_force":0.13301,"phase_name":"release_at_goal","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2429.0,"raw_peak_contact_force":2.144,"subtask_id":"release_1","tcp_end":[0.56248,0.15107,0.28202],"tcp_start":[0.56661,0.15208,0.25994],"tcp_to_object_dist_end":0.27744,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.75373,"average_solve_count":134.0,"average_success_count":134.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_to_object.speed":0.04773,"descend_to_grasp.speed":0.064,"grasp_object.max_time":0.69971,"lift_object.lift_height":0.16186,"lift_object.speed":0.0465,"release_at_goal.max_time":0.47866,"transport_to_goal.arc_height":0.20904,"transport_to_goal.speed":0.16548,"transport_to_goal.target_z_offset":0.02528},"optimized_scores":{"best_composite_score":0.12909,"best_fitness_score":0.69909,"best_task_score":0.44636},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":130.0,"contact_point_centroid":[0.60286,0.15725,-0.00989],"force_p95":1.29381,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.35602,"mean_force":0.55465,"phase_index":5.0,"phase_name":"release_at_goal","phase_type":"release","tcp_position_centroid":[0.60625,0.15814,0.18047]},{"body_a":"world","body_b":"grasp_target","contact_count":165.0,"contact_point_centroid":[0.5088,0.03549,-0.00137],"force_p95":0.48831,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.79991,"mean_force":0.10867,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.49573,0.03691,0.02619]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":15763.0,"contact_point_centroid":[0.49468,0.05597,0.09712],"force_p95":0.11245,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.41635,"mean_force":0.0653,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.49328,0.03673,0.09517]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":20081.0,"contact_point_centroid":[0.49571,0.01822,0.09767],"force_p95":0.08818,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31954,"mean_force":0.05091,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.49331,0.03673,0.09633]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":19213.0,"contact_point_centroid":[0.55804,0.08277,0.18183],"force_p95":0.09228,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28232,"mean_force":0.0532,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.55425,0.101,0.18155]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.51271,0.03949,-0.00226],"force_p95":0.19549,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.27978,"mean_force":0.14204,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.49879,0.03716,0.02538]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":13289.0,"contact_point_centroid":[0.5552,0.12159,0.18352],"force_p95":0.11618,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26064,"mean_force":0.07722,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.55572,0.10248,0.18114]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1108.0,"contact_point_centroid":[0.60647,0.17805,0.16966],"force_p95":0.08545,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24208,"mean_force":0.04744,"phase_index":5.0,"phase_name":"release_at_goal","phase_type":"release","tcp_position_centroid":[0.61026,0.15933,0.16613]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1344.0,"contact_point_centroid":[0.61418,0.14056,0.16695],"force_p95":0.0833,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21915,"mean_force":0.04053,"phase_index":5.0,"phase_name":"release_at_goal","phase_type":"release","tcp_position_centroid":[0.61027,0.15933,0.16615]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5176.0,"contact_point_centroid":[0.49913,0.01826,0.02597],"force_p95":0.06597,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21062,"mean_force":0.04089,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.49753,0.03706,0.02404]},{"body_a":"world","body_b":"grasp_target","contact_count":3312.0,"contact_point_centroid":[0.51251,0.03972,-0.00195],"force_p95":0.12693,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12277,"phase_index":0.0,"phase_name":"approach_to_object","phase_type":"approach","tcp_position_centroid":[0.50235,0.01856,0.16782]},{"body_a":"world","body_b":"grasp_target","contact_count":92.0,"contact_point_centroid":[0.51251,0.03972,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.50623,0.03747,0.03591]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3959.0,"contact_point_centroid":[0.49889,0.05657,0.02683],"force_p95":0.0948,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10709,"mean_force":0.05909,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.49754,0.03706,0.02406]}],"total_contact_groups":13},"final_pose_error":0.02024,"key_states":{"actual_goal_position":[0.62757,0.17252,0.14502],"final_object_position":[0.60456,0.15728,0.02722],"final_tcp_position":[0.61201,0.15959,0.16965],"realised_goal_position":[0.62757,0.17252,0.14502],"realised_object_initial_position":[0.51251,0.03972,0.03]},"peak_contact_force":1.35602,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":829.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.03],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21001,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_to_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3312.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.50703,0.03735,0.03795],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.01335,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":23.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":92.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.50618,0.0377,0.03337],"tcp_start":[0.50703,0.03735,0.03795],"tcp_to_object_dist_end":0.0099,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":42.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51264,0.03776,0.02512],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21388,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.18739,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10935.0,"raw_peak_contact_force":0.27978,"subtask_id":"grasp_1","tcp_end":[0.4975,0.03706,0.02401],"tcp_start":[0.50618,0.0377,0.03337],"tcp_to_object_dist_end":0.0152,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":31.0,"n_steps":993.0,"n_steps_budget":1000.0,"object_pos_end":[0.50706,0.03735,0.16355],"object_pos_start":[0.51264,0.03776,0.02512],"object_to_goal_dist_end":0.18204,"object_to_goal_dist_start":0.21388,"object_z_max":0.16344,"peak_contact_force":0.11664,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":36009.0,"raw_peak_contact_force":0.79991,"tcp_end":[0.4938,0.03677,0.17412],"tcp_start":[0.4975,0.03706,0.02401],"tcp_to_object_dist_end":0.01697,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.61187,0.16046,0.15029],"object_pos_start":[0.50706,0.03735,0.16355],"object_to_goal_dist_end":0.02048,"object_to_goal_dist_start":0.18204,"object_z_max":0.17268,"peak_contact_force":0.08758,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":32502.0,"raw_peak_contact_force":0.28232,"subtask_id":"transport_arc","tcp_end":[0.61201,0.15959,0.16965],"tcp_start":[0.4938,0.03677,0.17412],"tcp_to_object_dist_end":0.01938,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.60456,0.15728,0.02722],"object_pos_start":[0.61187,0.16046,0.15029],"object_to_goal_dist_end":0.121,"object_to_goal_dist_start":0.02048,"object_z_max":0.15029,"peak_contact_force":0.13685,"phase_name":"release_at_goal","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2582.0,"raw_peak_contact_force":1.35602,"subtask_id":"release_1","tcp_end":[0.60618,0.15812,0.1902],"tcp_start":[0.61201,0.15959,0.16965],"tcp_to_object_dist_end":0.16299,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.736,"average_solve_count":125.0,"average_success_count":125.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_to_object.speed":0.04967,"descend_to_grasp.speed":0.05198,"grasp_object.max_time":0.5827,"lift_object.lift_height":0.15932,"lift_object.speed":0.05729,"release_at_goal.max_time":0.10111,"transport_to_goal.arc_height":0.18447,"transport_to_goal.speed":0.18148,"transport_to_goal.target_z_offset":0.05559},"optimized_scores":{"best_composite_score":0.02051,"best_fitness_score":0.59051,"best_task_score":0.22403},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":473.0,"contact_point_centroid":[0.56821,0.1642,-0.00492],"force_p95":1.02428,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.17624,"mean_force":0.23771,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.55472,0.1889,0.28072]},{"body_a":"world","body_b":"grasp_target","contact_count":168.0,"contact_point_centroid":[0.47903,0.04394,-0.00151],"force_p95":0.44723,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.81401,"mean_force":0.11285,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.46755,0.04531,0.02785]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8201.0,"contact_point_centroid":[0.49891,0.07211,0.22496],"force_p95":0.13988,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.42723,"mean_force":0.08939,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.49113,0.08921,0.22659]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6387.0,"contact_point_centroid":[0.49235,0.10573,0.22394],"force_p95":0.15679,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.35648,"mean_force":0.10879,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.48957,0.08671,0.22405]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":10830.0,"contact_point_centroid":[0.46757,0.06429,0.09281],"force_p95":0.10902,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.3444,"mean_force":0.07458,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.46529,0.0451,0.09047]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":13565.0,"contact_point_centroid":[0.46914,0.02661,0.08797],"force_p95":0.1009,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29716,"mean_force":0.06103,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.46527,0.0451,0.0869]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.48291,0.04842,-0.00232],"force_p95":0.20983,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.28865,"mean_force":0.14603,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.47058,0.0456,0.02699]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4919.0,"contact_point_centroid":[0.47132,0.02657,0.02708],"force_p95":0.07852,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21098,"mean_force":0.04329,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.46936,0.04549,0.02578]},{"body_a":"world","body_b":"grasp_target","contact_count":3244.0,"contact_point_centroid":[0.4827,0.04873,-0.00195],"force_p95":0.12703,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12278,"phase_index":0.0,"phase_name":"approach_to_object","phase_type":"approach","tcp_position_centroid":[0.48834,0.02275,0.16821]},{"body_a":"world","body_b":"grasp_target","contact_count":200.0,"contact_point_centroid":[0.56807,0.16432,-0.002],"force_p95":0.12474,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12556,"mean_force":0.12328,"phase_index":5.0,"phase_name":"release_at_goal","phase_type":"release","tcp_position_centroid":[0.56042,0.19948,0.27863]},{"body_a":"world","body_b":"grasp_target","contact_count":88.0,"contact_point_centroid":[0.4827,0.04873,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.47799,0.04597,0.03665]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4137.0,"contact_point_centroid":[0.46969,0.06499,0.02825],"force_p95":0.09521,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09889,"mean_force":0.0548,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.46938,0.04549,0.02579]},{"body_a":"left_finger","body_b":"right_finger","contact_count":351.0,"contact_point_centroid":[0.55661,0.19202,0.28335],"force_p95":0.01441,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01757,"mean_force":0.01131,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.55679,0.19221,0.28095]},{"body_a":"left_finger","body_b":"right_finger","contact_count":214.0,"contact_point_centroid":[0.56047,0.19936,0.28094],"force_p95":0.011,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01102,"mean_force":0.01045,"phase_index":5.0,"phase_name":"release_at_goal","phase_type":"release","tcp_position_centroid":[0.56041,0.19948,0.27859]}],"total_contact_groups":14},"final_pose_error":0.03608,"key_states":{"actual_goal_position":[0.58187,0.22885,0.23048],"final_object_position":[0.56807,0.16433,0.01601],"final_tcp_position":[0.56143,0.19952,0.28121],"realised_goal_position":[0.58187,0.22885,0.23048],"realised_object_initial_position":[0.4827,0.04873,0.03]},"peak_contact_force":9748.60665,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":812.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.03],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28719,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_to_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3244.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.47888,0.04583,0.03853],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.01339,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":22.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":88.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.47775,0.04623,0.03426],"tcp_start":[0.47888,0.04583,0.03853],"tcp_to_object_dist_end":0.00993,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.48279,0.04623,0.02493],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.29227,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.20016,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10856.0,"raw_peak_contact_force":0.28865,"subtask_id":"grasp_1","tcp_end":[0.46934,0.04548,0.02575],"tcp_start":[0.47775,0.04623,0.03426],"tcp_to_object_dist_end":0.0135,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":24.0,"n_steps":801.0,"n_steps_budget":870.0,"object_pos_end":[0.48044,0.04628,0.15727],"object_pos_start":[0.48279,0.04623,0.02493],"object_to_goal_dist_end":0.22132,"object_to_goal_dist_start":0.29227,"object_z_max":0.15714,"peak_contact_force":0.10511,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":24563.0,"raw_peak_contact_force":0.81401,"tcp_end":[0.46578,0.04515,0.17248],"tcp_start":[0.46934,0.04548,0.02575],"tcp_to_object_dist_end":0.02116,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.56812,0.16424,0.01607],"object_pos_start":[0.48044,0.04628,0.15727],"object_to_goal_dist_end":0.22436,"object_to_goal_dist_start":0.22132,"object_z_max":0.24865,"peak_contact_force":9748.60665,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":15412.0,"raw_peak_contact_force":2.17624,"subtask_id":"transport_arc","tcp_end":[0.56143,0.19952,0.28121],"tcp_start":[0.46578,0.04515,0.17248],"tcp_to_object_dist_end":0.26755,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.56807,0.16433,0.01601],"object_pos_start":[0.56812,0.16424,0.01607],"object_to_goal_dist_end":0.2244,"object_to_goal_dist_start":0.22436,"object_z_max":0.01607,"peak_contact_force":0.12275,"phase_name":"release_at_goal","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":414.0,"raw_peak_contact_force":0.12556,"subtask_id":"release_1","tcp_end":[0.55966,0.1991,0.27648],"tcp_start":[0.56143,0.19952,0.28121],"tcp_to_object_dist_end":0.26292,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```