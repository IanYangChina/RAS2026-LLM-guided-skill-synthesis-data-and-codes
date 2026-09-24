## Search State

- **Seed**: 6
- **Iteration**: 10 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 9 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 11 | -0.0663 | 0.31 | ❌ rejected |
| 8 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | force_threshold_switch | position_control | position_control | position_control | position_control | position_control | pose_tolerance | force_exceeded | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 10 | -0.3272 | 0.17 | ❌ rejected |
| 7 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | time_limit | pose_tolerance | pose_tolerance | time_limit | 10 | -0.4748 | 0.17 | ❌ rejected |
| 6 | approach → descend → grasp → lift → approach → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | time_limit | 9 | 0.0512 | 0.29 | ❌ rejected |
| 5 | approach → descend → grasp → lift → approach → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | time_limit | 8 | 0.1050 | 0.30 | ❌ rejected |

**Proposal policy**: task_score is 0.31 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=-0.066) — your mutation base

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

- **Composite score**: -0.066
- **task_score** (E): 0.314
- **fitness_score**: 0.634  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.700

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_to_object | 1.00 | 1.00 | 0.2652 |
| descend_to_grasp | 1.00 | 1.00 | 0.0030 |
| grasp_object | 1.00 | 1.00 | 0.0122 |
| lift_object | 0.33 | 1.00 | 0.1393 |
| transport_to_goal | 0.67 | 1.00 | 0.1835 |
| descend_to_release | 1.00 | 1.00 | 0.0798 |
| release_object | 1.00 | 1.00 | 0.0218 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_to_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.495, 0.023, 0.038) | (0.500, 0.024, 0.030)→(0.500, 0.024, 0.026) | 0.269→0.271 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_to_grasp | descend | 1.00 / step_budget | (0.495, 0.023, 0.038)→(0.494, 0.023, 0.036) | (0.500, 0.024, 0.026)→(0.500, 0.024, 0.026) | 0.271→0.271 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_object | grasp | 1.00 / step_budget | (0.494, 0.023, 0.036)→(0.485, 0.022, 0.027) | (0.500, 0.024, 0.026)→(0.500, 0.023, 0.025) | 0.271→0.273 | 1.00 / 42.000 | 0.175 | 0.243 |
| lift_object | lift | 0.33 / step_budget | (0.485, 0.022, 0.027)→(0.482, 0.022, 0.166) | (0.500, 0.023, 0.025)→(0.493, 0.023, 0.154) | 0.273→0.221 | 1.00 / 34.667 | 0.090 | 0.727 |
| transport_to_goal | approach | 0.67 / step_budget | (0.482, 0.022, 0.166)→(0.573, 0.159, 0.218) | (0.493, 0.023, 0.154)→(0.577, 0.161, 0.199) | 0.221→0.044 | 1.00 / 34.333 | 0.097 | 0.285 |
| descend_to_release | descend | 1.00 / step_budget | (0.573, 0.159, 0.218)→(0.591, 0.190, 0.148) | (0.577, 0.161, 0.199)→(0.592, 0.192, 0.127) | 0.044→0.082 | 1.00 / 36.667 | 0.092 | 0.303 |
| release_object | release | 1.00 / step_budget | (0.591, 0.190, 0.148)→(0.585, 0.188, 0.169) | (0.592, 0.192, 0.127)→(0.587, 0.189, 0.027) | 0.082→0.181 | 1.00 / 2.000 | 0.192 | 1.227 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.456
- phase_score: 0.537
- phase_breakdown.transport_arc_score: 0.474
- phase_breakdown.release_1_score: 0.569
- phase_breakdown.approach_1_score: 0.822
- phase_breakdown.grasp_1_score: 1.000
- phase_breakdown.descend_1_score: 0.000
- grasp_place_fitness: 0.704

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.704
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.456
- **Median Q (composite search score)**: -0.093
- **K-run variance**: 0.0025
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.308


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.87234,"average_solve_count":141.0,"average_success_count":141.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_to_object.speed":0.07508,"descend_to_grasp.grasp_z_offset":0.0209,"descend_to_grasp.speed":0.04476,"descend_to_release.release_z_offset":-0.0652,"descend_to_release.speed":0.04327,"grasp_object.max_time":0.45019,"lift_object.lift_height":0.27516,"lift_object.speed":0.04606,"release_object.max_time":0.34709,"transport_to_goal.arc_height":0.1192,"transport_to_goal.speed":0.10634},"optimized_scores":{"best_composite_score":-0.1102,"best_fitness_score":0.5898,"best_task_score":0.22669},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":172.0,"contact_point_centroid":[0.56318,0.17517,-0.00793],"force_p95":1.3103,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.40562,"mean_force":0.42437,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.57453,0.17874,0.19531]},{"body_a":"world","body_b":"grasp_target","contact_count":147.0,"contact_point_centroid":[0.50062,-0.01518,-0.00112],"force_p95":0.41365,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.66121,"mean_force":0.09591,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.48795,-0.01524,0.03205]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":17434.0,"contact_point_centroid":[0.48621,-0.03438,0.10689],"force_p95":0.08053,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33043,"mean_force":0.05751,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.48539,-0.0152,0.10435]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":20293.0,"contact_point_centroid":[0.48698,0.00378,0.10372],"force_p95":0.0751,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32677,"mean_force":0.05071,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.48539,-0.0152,0.10199]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":7211.0,"contact_point_centroid":[0.56369,0.1736,0.22491],"force_p95":0.08912,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27973,"mean_force":0.05708,"phase_index":5.0,"phase_name":"descend_to_release","phase_type":"descend","tcp_position_centroid":[0.56691,0.15482,0.22172]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1274.0,"contact_point_centroid":[0.57429,0.19868,0.18409],"force_p95":0.06789,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25417,"mean_force":0.04193,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.57824,0.18003,0.18029]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8100.0,"contact_point_centroid":[0.57171,0.13591,0.22288],"force_p95":0.08541,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23069,"mean_force":0.05199,"phase_index":5.0,"phase_name":"descend_to_release","phase_type":"descend","tcp_position_centroid":[0.56661,0.15427,0.22249]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":17762.0,"contact_point_centroid":[0.51846,0.03108,0.24316],"force_p95":0.08715,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22863,"mean_force":0.05666,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.51554,0.04985,0.24219]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1404.0,"contact_point_centroid":[0.58364,0.16143,0.18124],"force_p95":0.06407,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22481,"mean_force":0.03854,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.57823,0.18003,0.18027]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":17503.0,"contact_point_centroid":[0.51382,0.06507,0.24148],"force_p95":0.0855,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19044,"mean_force":0.05675,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.51367,0.04614,0.24007]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50381,-0.01573,-0.00203],"force_p95":0.13497,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.15991,"mean_force":0.12564,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.4908,-0.01526,0.03162]},{"body_a":"world","body_b":"grasp_target","contact_count":3016.0,"contact_point_centroid":[0.50382,-0.01567,-0.00195],"force_p95":0.12823,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12279,"phase_index":0.0,"phase_name":"approach_to_object","phase_type":"approach","tcp_position_centroid":[0.49833,-0.00737,0.16827]},{"body_a":"world","body_b":"grasp_target","contact_count":244.0,"contact_point_centroid":[0.50382,-0.01567,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.49753,-0.01507,0.03783]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5316.0,"contact_point_centroid":[0.49047,0.00381,0.03233],"force_p95":0.06597,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09795,"mean_force":0.04109,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.48955,-0.01525,0.0303]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4161.0,"contact_point_centroid":[0.48919,-0.03452,0.03303],"force_p95":0.07846,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08951,"mean_force":0.05184,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.48956,-0.01525,0.0303]}],"total_contact_groups":15},"final_pose_error":0.00994,"key_states":{"actual_goal_position":[0.58691,0.18745,0.24812],"final_object_position":[0.56797,0.17586,0.0266],"final_tcp_position":[0.58,0.18034,0.18376],"realised_goal_position":[0.58691,0.18745,0.24812],"realised_object_initial_position":[0.50382,-0.01567,0.03]},"peak_contact_force":1.40562,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":755.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.03],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.30942,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_to_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3016.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.49877,-0.01484,0.03842],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.01342,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":61.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":244.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.49777,-0.0153,0.03901],"tcp_start":[0.49877,-0.01484,0.03842],"tcp_to_object_dist_end":0.01434,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50368,-0.01564,0.02586],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31236,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.13491,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11277.0,"raw_peak_contact_force":0.15991,"subtask_id":"grasp_1","tcp_end":[0.48952,-0.01525,0.03027],"tcp_start":[0.49777,-0.0153,0.03901],"tcp_to_object_dist_end":0.01484,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49596,-0.01554,0.1674],"object_pos_start":[0.50368,-0.01564,0.02586],"object_to_goal_dist_end":0.23663,"object_to_goal_dist_start":0.31236,"object_z_max":0.16722,"peak_contact_force":0.08316,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":37874.0,"raw_peak_contact_force":0.66121,"tcp_end":[0.48579,-0.0152,0.18037],"tcp_start":[0.48952,-0.01525,0.03027],"tcp_to_object_dist_end":0.01649,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":36.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.55977,0.12938,0.24842],"object_pos_start":[0.49596,-0.01554,0.1674],"object_to_goal_dist_end":0.0641,"object_to_goal_dist_start":0.23663,"object_z_max":0.25104,"peak_contact_force":0.0851,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":35265.0,"raw_peak_contact_force":0.22863,"subtask_id":"transport_arc","tcp_end":[0.55465,0.12748,0.26777],"tcp_start":[0.48579,-0.0152,0.18037],"tcp_to_object_dist_end":0.02011,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":384.0,"n_steps_budget":1000.0,"object_pos_end":[0.57771,0.18128,0.16145],"object_pos_start":[0.55977,0.12938,0.24842],"object_to_goal_dist_end":0.08738,"object_to_goal_dist_start":0.0641,"object_z_max":0.24842,"peak_contact_force":0.06881,"phase_name":"descend_to_release","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":15311.0,"raw_peak_contact_force":0.27973,"tcp_end":[0.58,0.18034,0.18376],"tcp_start":[0.55465,0.12748,0.26777],"tcp_to_object_dist_end":0.02245,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.56797,0.17586,0.0266],"object_pos_start":[0.57771,0.18128,0.16145],"object_to_goal_dist_end":0.22262,"object_to_goal_dist_start":0.08738,"object_z_max":0.16145,"peak_contact_force":0.13364,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2850.0,"raw_peak_contact_force":1.40562,"subtask_id":"release_1","tcp_end":[0.57446,0.17872,0.20503],"tcp_start":[0.58,0.18034,0.18376],"tcp_to_object_dist_end":0.17857,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.29126,"average_solve_count":206.0,"average_success_count":206.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_to_object.speed":0.02511,"descend_to_grasp.grasp_z_offset":0.00057,"descend_to_grasp.speed":0.0516,"descend_to_release.release_z_offset":-0.04365,"descend_to_release.speed":0.04798,"grasp_object.max_time":0.46562,"lift_object.lift_height":0.18392,"lift_object.speed":0.05455,"release_object.max_time":0.41143,"transport_to_goal.arc_height":0.18956,"transport_to_goal.speed":0.09207},"optimized_scores":{"best_composite_score":0.00397,"best_fitness_score":0.70397,"best_task_score":0.45625},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":183.0,"contact_point_centroid":[0.6105,0.17607,-0.0058],"force_p95":0.85728,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.97684,"mean_force":0.36059,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.61199,0.16589,0.10946]},{"body_a":"world","body_b":"grasp_target","contact_count":168.0,"contact_point_centroid":[0.50872,0.03567,-0.00146],"force_p95":0.44013,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.86563,"mean_force":0.11864,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.49563,0.03687,0.02638]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":925.0,"contact_point_centroid":[0.61635,0.18659,0.10012],"force_p95":0.12003,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.46845,"mean_force":0.07363,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.61648,0.16718,0.09823]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2736.0,"contact_point_centroid":[0.60958,0.17791,0.13031],"force_p95":0.13504,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.4614,"mean_force":0.08897,"phase_index":5.0,"phase_name":"descend_to_release","phase_type":"descend","tcp_position_centroid":[0.60961,0.15857,0.12984]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":13610.0,"contact_point_centroid":[0.49568,0.05592,0.10545],"force_p95":0.11075,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.39336,"mean_force":0.07244,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.49337,0.0367,0.10324]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":12620.0,"contact_point_centroid":[0.54762,0.11246,0.18919],"force_p95":0.12309,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.35699,"mean_force":0.08401,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.54665,0.09318,0.18759]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1120.0,"contact_point_centroid":[0.62263,0.1495,0.0979],"force_p95":0.11107,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.35159,"mean_force":0.05802,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.61662,0.16722,0.09843]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":16063.0,"contact_point_centroid":[0.55447,0.07812,0.18661],"force_p95":0.09303,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31032,"mean_force":0.06139,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.54941,0.09602,0.18699]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3343.0,"contact_point_centroid":[0.61603,0.14129,0.1282],"force_p95":0.12441,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30461,"mean_force":0.07239,"phase_index":5.0,"phase_name":"descend_to_release","phase_type":"descend","tcp_position_centroid":[0.60976,0.15872,0.12939]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":18590.0,"contact_point_centroid":[0.4962,0.01823,0.10346],"force_p95":0.09107,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30455,"mean_force":0.05465,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.49336,0.0367,0.10258]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.51272,0.03949,-0.00226],"force_p95":0.19616,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.27976,"mean_force":0.14222,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.49872,0.03712,0.02583]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5176.0,"contact_point_centroid":[0.49908,0.01823,0.02643],"force_p95":0.06612,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21223,"mean_force":0.04091,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.49746,0.03703,0.02449]},{"body_a":"world","body_b":"grasp_target","contact_count":3596.0,"contact_point_centroid":[0.51251,0.03972,-0.00196],"force_p95":0.12574,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12276,"phase_index":0.0,"phase_name":"approach_to_object","phase_type":"approach","tcp_position_centroid":[0.50226,0.01859,0.16752]},{"body_a":"world","body_b":"grasp_target","contact_count":84.0,"contact_point_centroid":[0.51251,0.03972,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.50618,0.03747,0.03596]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3949.0,"contact_point_centroid":[0.49887,0.05654,0.02725],"force_p95":0.09485,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10712,"mean_force":0.05901,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.49748,0.03703,0.02451]}],"total_contact_groups":15},"final_pose_error":0.0099,"key_states":{"actual_goal_position":[0.62757,0.17252,0.14502],"final_object_position":[0.61876,0.17139,0.02765],"final_tcp_position":[0.61898,0.16773,0.10253],"realised_goal_position":[0.62757,0.17252,0.14502],"realised_object_initial_position":[0.51251,0.03972,0.03]},"peak_contact_force":0.97684,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":900.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.03],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21001,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_to_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3596.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.50695,0.03738,0.03773],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.01317,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":21.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":84.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.50609,0.03767,0.03379],"tcp_start":[0.50695,0.03738,0.03773],"tcp_to_object_dist_end":0.01029,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":42.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51265,0.03776,0.02511],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21389,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.1879,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10925.0,"raw_peak_contact_force":0.27976,"subtask_id":"grasp_1","tcp_end":[0.49743,0.03702,0.02446],"tcp_start":[0.50609,0.03767,0.03379],"tcp_to_object_dist_end":0.01524,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":30.0,"n_steps":977.0,"n_steps_budget":1000.0,"object_pos_end":[0.50702,0.03765,0.18211],"object_pos_start":[0.51265,0.03776,0.02511],"object_to_goal_dist_end":0.18466,"object_to_goal_dist_start":0.21389,"object_z_max":0.18198,"peak_contact_force":0.10689,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":32368.0,"raw_peak_contact_force":0.86563,"tcp_end":[0.49396,0.03675,0.19556],"tcp_start":[0.49743,0.03702,0.02446],"tcp_to_object_dist_end":0.01877,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":27.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.60882,0.15193,0.14004],"object_pos_start":[0.50702,0.03765,0.18211],"object_to_goal_dist_end":0.02829,"object_to_goal_dist_start":0.18466,"object_z_max":0.18218,"peak_contact_force":0.12727,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":28683.0,"raw_peak_contact_force":0.35699,"subtask_id":"transport_arc","tcp_end":[0.60249,0.15,0.16094],"tcp_start":[0.49396,0.03675,0.19556],"tcp_to_object_dist_end":0.02192,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":28.0,"n_steps":228.0,"n_steps_budget":1000.0,"object_pos_end":[0.62213,0.16924,0.07885],"object_pos_start":[0.60882,0.15193,0.14004],"object_to_goal_dist_end":0.06648,"object_to_goal_dist_start":0.02829,"object_z_max":0.14004,"peak_contact_force":0.12922,"phase_name":"descend_to_release","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":6079.0,"raw_peak_contact_force":0.4614,"tcp_end":[0.61898,0.16773,0.10253],"tcp_start":[0.60249,0.15,0.16094],"tcp_to_object_dist_end":0.02394,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.61876,0.17139,0.02765],"object_pos_start":[0.62213,0.16924,0.07885],"object_to_goal_dist_end":0.11771,"object_to_goal_dist_start":0.06648,"object_z_max":0.07885,"peak_contact_force":0.30028,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2228.0,"raw_peak_contact_force":0.97684,"subtask_id":"release_1","tcp_end":[0.61181,0.16585,0.12263],"tcp_start":[0.61898,0.16773,0.10253],"tcp_to_object_dist_end":0.0954,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.61871,"average_solve_count":139.0,"average_success_count":139.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_to_object.speed":0.08269,"descend_to_grasp.grasp_z_offset":0.00169,"descend_to_grasp.speed":0.03323,"descend_to_release.release_z_offset":-0.07563,"descend_to_release.speed":0.03148,"grasp_object.max_time":0.53086,"lift_object.lift_height":0.15942,"lift_object.speed":0.02913,"release_object.max_time":0.24559,"transport_to_goal.arc_height":0.17705,"transport_to_goal.speed":0.14379},"optimized_scores":{"best_composite_score":-0.09259,"best_fitness_score":0.60741,"best_task_score":0.25827},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":138.0,"contact_point_centroid":[0.56741,0.21954,-0.00922],"force_p95":1.23458,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.2975,"mean_force":0.51423,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.56896,0.22067,0.16907]},{"body_a":"world","body_b":"grasp_target","contact_count":200.0,"contact_point_centroid":[0.47741,0.04348,-0.00142],"force_p95":0.45233,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.65443,"mean_force":0.11937,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.46737,0.0452,0.02875]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":16882.0,"contact_point_centroid":[0.46491,0.06419,0.07763],"force_p95":0.08409,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31804,"mean_force":0.05911,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.46496,0.04499,0.07498]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.48292,0.04842,-0.00233],"force_p95":0.21142,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.28889,"mean_force":0.14646,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.47053,0.04551,0.02784]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":20372.0,"contact_point_centroid":[0.51063,0.09575,0.19212],"force_p95":0.07572,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27045,"mean_force":0.04951,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.50629,0.1142,0.19128]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":20965.0,"contact_point_centroid":[0.467,0.02608,0.07565],"force_p95":0.07819,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26549,"mean_force":0.04866,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.46497,0.04499,0.07417]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1103.0,"contact_point_centroid":[0.56733,0.24033,0.15932],"force_p95":0.07723,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23218,"mean_force":0.04731,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.57286,0.22227,0.1547]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1294.0,"contact_point_centroid":[0.57888,0.20402,0.1547],"force_p95":0.07381,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2209,"mean_force":0.04252,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.57285,0.22227,0.15468]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4922.0,"contact_point_centroid":[0.47128,0.02648,0.02792],"force_p95":0.0777,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21397,"mean_force":0.04328,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.46932,0.0454,0.02662]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":16652.0,"contact_point_centroid":[0.50343,0.13204,0.19322],"force_p95":0.09026,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18218,"mean_force":0.06054,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.50559,0.11311,0.19035]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4662.0,"contact_point_centroid":[0.56105,0.22851,0.19559],"force_p95":0.07927,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16648,"mean_force":0.05469,"phase_index":5.0,"phase_name":"descend_to_release","phase_type":"descend","tcp_position_centroid":[0.56647,0.21037,0.19146]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5455.0,"contact_point_centroid":[0.57227,0.19212,0.19191],"force_p95":0.07499,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16578,"mean_force":0.04961,"phase_index":5.0,"phase_name":"descend_to_release","phase_type":"descend","tcp_position_centroid":[0.56646,0.21034,0.19156]},{"body_a":"world","body_b":"grasp_target","contact_count":2952.0,"contact_point_centroid":[0.4827,0.04873,-0.00195],"force_p95":0.12843,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12279,"phase_index":0.0,"phase_name":"approach_to_object","phase_type":"approach","tcp_position_centroid":[0.48843,0.02274,0.16831]},{"body_a":"world","body_b":"grasp_target","contact_count":80.0,"contact_point_centroid":[0.4827,0.04873,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.47796,0.04592,0.03698]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4143.0,"contact_point_centroid":[0.46966,0.06491,0.0291],"force_p95":0.09497,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10011,"mean_force":0.05475,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.46933,0.0454,0.02663]}],"total_contact_groups":15},"final_pose_error":0.00995,"key_states":{"actual_goal_position":[0.58187,0.22885,0.23048],"final_object_position":[0.57332,0.22107,0.02775],"final_tcp_position":[0.57475,0.22284,0.15835],"realised_goal_position":[0.58187,0.22885,0.23048],"realised_object_initial_position":[0.4827,0.04873,0.03]},"peak_contact_force":1.2975,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":739.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.03],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28719,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_to_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2952.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.47886,0.04581,0.03864],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.01351,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":20.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":80.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.47765,0.04614,0.03504],"tcp_start":[0.47886,0.04581,0.03864],"tcp_to_object_dist_end":0.01066,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.4828,0.0462,0.0249],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.2923,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.20154,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10865.0,"raw_peak_contact_force":0.28889,"subtask_id":"grasp_1","tcp_end":[0.46929,0.04539,0.02659],"tcp_start":[0.47765,0.04614,0.03504],"tcp_to_object_dist_end":0.01364,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.47529,0.04597,0.1132],"object_pos_start":[0.4828,0.0462,0.0249],"object_to_goal_dist_end":0.242,"object_to_goal_dist_start":0.2923,"object_z_max":0.1131,"peak_contact_force":0.08097,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":38047.0,"raw_peak_contact_force":0.65443,"tcp_end":[0.46512,0.045,0.12307],"tcp_start":[0.46929,0.04539,0.02659],"tcp_to_object_dist_end":0.01421,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.56329,0.20108,0.20935],"object_pos_start":[0.47529,0.04597,0.1132],"object_to_goal_dist_end":0.03953,"object_to_goal_dist_start":0.242,"object_z_max":0.21021,"peak_contact_force":0.07966,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":37024.0,"raw_peak_contact_force":0.27045,"subtask_id":"transport_arc","tcp_end":[0.56049,0.19922,0.22679],"tcp_start":[0.46512,0.045,0.12307],"tcp_to_object_dist_end":0.01776,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":39.0,"n_steps":259.0,"n_steps_budget":1000.0,"object_pos_end":[0.57707,0.22533,0.13972],"object_pos_start":[0.56329,0.20108,0.20935],"object_to_goal_dist_end":0.09096,"object_to_goal_dist_start":0.03953,"object_z_max":0.20935,"peak_contact_force":0.07808,"phase_name":"descend_to_release","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":10117.0,"raw_peak_contact_force":0.16648,"tcp_end":[0.57475,0.22284,0.15835],"tcp_start":[0.56049,0.19922,0.22679],"tcp_to_object_dist_end":0.01894,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.57332,0.22107,0.02775],"object_pos_start":[0.57707,0.22533,0.13972],"object_to_goal_dist_end":0.20306,"object_to_goal_dist_start":0.09096,"object_z_max":0.13972,"peak_contact_force":0.14059,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2535.0,"raw_peak_contact_force":1.2975,"subtask_id":"release_1","tcp_end":[0.56888,0.22064,0.17936],"tcp_start":[0.57475,0.22284,0.15835],"tcp_to_object_dist_end":0.15168,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```