## Search State

- **Seed**: 6
- **Iteration**: 2 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 1 | approach → descend → grasp → lift → approach → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | — | position_control | admittance_control | position_control | position_control | position_control | position_control | pose_tolerance | contact_detected | time_limit | pose_tolerance | pose_tolerance | time_limit | 7 | 0.1345 | 0.25 | ✅ accepted |
| 0 | approach → descend → grasp → lift → release | linear_cartesian | linear_cartesian | — | linear_cartesian | — | force_threshold_switch | admittance_control | position_control | position_control | position_control | pose_tolerance | contact_detected | time_limit | pose_tolerance | time_limit | 3 | 0.3184 | 0.17 | ✅ accepted |

**Proposal policy**: task_score is 0.25 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.135) — your mutation base

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
    offset:
    - 0.0
    - 0.0
    - 0.0
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    approach_height:
      type: scalar
      range:
      - 0.05
      - 0.3
      default: 0.15
      binds_to:
      - path: target.offset.z
        mode: replace
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: approach_1
- id: descend_1
  type: descend
  generator: linear_cartesian
  control: admittance_control
  termination: contact_detected
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.0
    - 0.0
    orientation:
      mode: keep_current
  parameters:
    grasp_z_offset:
      type: scalar
      range:
      - 0.005
      - 0.05
      default: 0.02
      binds_to:
      - path: target.offset.z
        mode: replace
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.03
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: descend_1
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
      distance: 0.2
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
      - 0.1
      - 0.3
      default: 0.2
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
        mode: replace
- id: transport_arc
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.0
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: transport_arc
- id: release_1
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
  subtask_id: release_1

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.0], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_height: status=consumed; consumers=target.offset.z (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
- **descend_1** (`descend`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings:
    - grasp_z_offset: status=consumed; consumers=target.offset.z (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
- **grasp_1** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings: none
- **lift_1** (`lift`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=world_z, distance=0.2, mode=add_to_offset, sign=positive}, tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
- **transport_arc** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - speed: status=consumed; consumers=generator.speed (replace)
- **release_1** (`release`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0]
  - parameter_bindings: none

## Design Metrics

- **Composite score**: 0.135
- **task_score** (E): 0.251
- **fitness_score**: 0.605  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.470

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1501 |
| descend_1 | 1.00 | 1.00 | 0.1206 |
| grasp_1 | 1.00 | 1.00 | 0.0115 |
| lift_1 | 0.33 | 1.00 | 0.1049 |
| transport_arc | 0.00 | 0.33 | 0.1051 |
| release_1 | 1.00 | 1.00 | 0.0242 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.496, 0.021, 0.156) | (0.500, 0.024, 0.030)→(0.500, 0.024, 0.026) | 0.269→0.271 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.496, 0.021, 0.156)→(0.495, 0.024, 0.035) | (0.500, 0.024, 0.026)→(0.500, 0.024, 0.026) | 0.271→0.271 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_1 | grasp | 1.00 / step_budget | (0.495, 0.024, 0.035)→(0.487, 0.023, 0.027) | (0.500, 0.024, 0.026)→(0.500, 0.024, 0.026) | 0.271→0.272 | 1.00 / 43.000 | 0.143 | 0.208 |
| lift_1 | lift | 0.33 / step_budget | (0.487, 0.023, 0.027)→(0.483, 0.023, 0.132) | (0.500, 0.024, 0.026)→(0.495, 0.023, 0.120) | 0.272→0.225 | 1.00 / 32.667 | 0.099 | 0.683 |
| transport_arc | approach | 0.00 / step_budget | (0.483, 0.023, 0.132)→(0.536, 0.105, 0.160) | (0.495, 0.023, 0.120)→(0.544, 0.110, 0.042) | 0.225→0.196 | 0.33 / 2.667 | 3249.492 | 0.681 |
| release_1 | release | 1.00 / step_budget | (0.536, 0.105, 0.160)→(0.530, 0.104, 0.183) | (0.544, 0.110, 0.042)→(0.544, 0.112, 0.016) | 0.196→0.217 | 1.00 / 4.000 | 0.123 | 1.009 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: 1.000
- terminal_score: 0.383
- phase_score: 0.347
- phase_breakdown.descend_1_score: 0.777
- phase_breakdown.transport_arc_score: 0.172
- phase_breakdown.grasp_1_score: 1.000
- phase_breakdown.approach_1_score: 0.039
- phase_breakdown.release_1_score: 0.153
- grasp_place_fitness: 0.670

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.670
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.383
- **Median Q (composite search score)**: 0.111
- **K-run variance**: 0.0022
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.294


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.5,"average_solve_count":156.0,"average_success_count":156.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.05366,"approach_1.speed":0.0643,"descend_1.grasp_z_offset":0.00859,"descend_1.speed":0.08776,"lift_1.lift_height":0.14678,"lift_1.speed":0.064,"transport_arc.speed":0.08346},"optimized_scores":{"best_composite_score":0.09274,"best_fitness_score":0.56274,"best_task_score":0.16749},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":516.0,"contact_point_centroid":[0.53282,0.06499,-0.00386],"force_p95":0.95746,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.55988,"mean_force":0.21049,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.52409,0.0676,0.17193]},{"body_a":"world","body_b":"grasp_target","contact_count":159.0,"contact_point_centroid":[0.50048,-0.01546,-0.0011],"force_p95":0.53542,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.75127,"mean_force":0.11153,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48924,-0.01545,0.0248]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":17190.0,"contact_point_centroid":[0.48813,0.00362,0.07569],"force_p95":0.08748,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32956,"mean_force":0.0597,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48653,-0.0154,0.07386]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":17626.0,"contact_point_centroid":[0.48807,-0.03439,0.07434],"force_p95":0.08793,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30641,"mean_force":0.05857,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48654,-0.0154,0.07274]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":9393.0,"contact_point_centroid":[0.50262,0.00117,0.14324],"force_p95":0.13643,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23925,"mean_force":0.08147,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.50056,0.02002,0.1448]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":11464.0,"contact_point_centroid":[0.50322,0.04035,0.14435],"force_p95":0.09395,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16812,"mean_force":0.06671,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.50142,0.02184,0.1458]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.5038,-0.01553,-0.00202],"force_p95":0.13026,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.15645,"mean_force":0.12498,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49203,-0.01548,0.02436]},{"body_a":"world","body_b":"grasp_target","contact_count":2680.0,"contact_point_centroid":[0.50382,-0.01567,-0.00195],"force_p95":0.12957,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12281,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49853,-0.0072,0.19566]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.53296,0.06475,-0.00199],"force_p95":0.12314,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12377,"mean_force":0.12265,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.52265,0.0721,0.17805]},{"body_a":"world","body_b":"grasp_target","contact_count":2660.0,"contact_point_centroid":[0.50382,-0.01567,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49768,-0.01519,0.05284]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4115.0,"contact_point_centroid":[0.4913,0.00374,0.02588],"force_p95":0.07583,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10877,"mean_force":0.05175,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49084,-0.01547,0.02311]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4884.0,"contact_point_centroid":[0.49137,-0.03454,0.02496],"force_p95":0.06787,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08971,"mean_force":0.0447,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49084,-0.01547,0.02311]},{"body_a":"left_finger","body_b":"right_finger","contact_count":265.0,"contact_point_centroid":[0.52565,0.0702,0.17561],"force_p95":0.01444,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01906,"mean_force":0.0116,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.5254,0.0702,0.17343]},{"body_a":"left_finger","body_b":"right_finger","contact_count":216.0,"contact_point_centroid":[0.52574,0.07252,0.17494],"force_p95":0.01103,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01103,"mean_force":0.01026,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.52527,0.07252,0.17272]}],"total_contact_groups":14},"final_pose_error":0.14903,"key_states":{"actual_goal_position":[0.58691,0.18745,0.24812],"final_object_position":[0.53296,0.06475,0.01602],"final_tcp_position":[0.52658,0.07258,0.1748],"realised_goal_position":[0.58691,0.18745,0.24812],"realised_object_initial_position":[0.50382,-0.01567,0.03]},"peak_contact_force":9748.47738,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":671.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.03],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.30942,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2680.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.49936,-0.01459,0.0923],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.06644,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":665.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2660.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.49878,-0.01557,0.03145],"tcp_start":[0.49936,-0.01459,0.0923],"tcp_to_object_dist_end":0.00741,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50367,-0.01532,0.0259],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31213,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.12895,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10799.0,"raw_peak_contact_force":0.15645,"subtask_id":"grasp_1","tcp_end":[0.49081,-0.01546,0.02308],"tcp_start":[0.49878,-0.01557,0.03145],"tcp_to_object_dist_end":0.01317,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":30.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50144,-0.01541,0.11883],"object_pos_start":[0.50367,-0.01532,0.0259],"object_to_goal_dist_end":0.25529,"object_to_goal_dist_start":0.31213,"object_z_max":0.11873,"peak_contact_force":0.10238,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":34975.0,"raw_peak_contact_force":0.75127,"tcp_end":[0.48664,-0.01539,0.12903],"tcp_start":[0.49081,-0.01546,0.02308],"tcp_to_object_dist_end":0.01798,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53296,0.06469,0.016],"object_pos_start":[0.50144,-0.01541,0.11883],"object_to_goal_dist_end":0.26806,"object_to_goal_dist_start":0.25529,"object_z_max":0.14266,"peak_contact_force":9748.47738,"phase_name":"transport_arc","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":21638.0,"raw_peak_contact_force":1.55988,"subtask_id":"transport_arc","tcp_end":[0.52658,0.07258,0.1748],"tcp_start":[0.48664,-0.01539,0.12903],"tcp_to_object_dist_end":0.15912,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53296,0.06475,0.01602],"object_pos_start":[0.53296,0.06469,0.016],"object_to_goal_dist_end":0.26802,"object_to_goal_dist_start":0.26806,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1016.0,"raw_peak_contact_force":0.12377,"subtask_id":"release_1","tcp_end":[0.52112,0.07186,0.19876],"tcp_start":[0.52658,0.07258,0.1748],"tcp_to_object_dist_end":0.18326,"terminated_normally":true,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.65101,"average_solve_count":149.0,"average_success_count":149.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.15498,"approach_1.speed":0.06581,"descend_1.grasp_z_offset":0.0147,"descend_1.speed":0.07782,"lift_1.lift_height":0.21649,"lift_1.speed":0.06771,"transport_arc.speed":0.0711},"optimized_scores":{"best_composite_score":0.19969,"best_fitness_score":0.66969,"best_task_score":0.38262},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":744.0,"contact_point_centroid":[0.57927,0.12971,-0.00301],"force_p95":0.55022,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.27015,"mean_force":0.17431,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.55969,0.11094,0.13878]},{"body_a":"world","body_b":"grasp_target","contact_count":167.0,"contact_point_centroid":[0.50896,0.03756,-0.00119],"force_p95":0.42866,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.64974,"mean_force":0.09291,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49775,0.0384,0.0314]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":17192.0,"contact_point_centroid":[0.49696,0.05721,0.08316],"force_p95":0.08687,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32891,"mean_force":0.05945,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49522,0.0382,0.08161]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":17066.0,"contact_point_centroid":[0.49693,0.01922,0.08463],"force_p95":0.08741,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32568,"mean_force":0.05942,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.4952,0.0382,0.0829]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":10080.0,"contact_point_centroid":[0.53018,0.05441,0.1353],"force_p95":0.1439,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2319,"mean_force":0.08747,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.52624,0.07289,0.13664]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.51254,0.03945,-0.0021],"force_p95":0.1531,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.22487,"mean_force":0.13078,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.50068,0.03865,0.03104]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":10693.0,"contact_point_centroid":[0.53164,0.09216,0.13546],"force_p95":0.13445,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17503,"mean_force":0.08229,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.52712,0.07381,0.13659]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4074.0,"contact_point_centroid":[0.5,0.01935,0.03256],"force_p95":0.07982,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14074,"mean_force":0.05182,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49949,0.03855,0.02975]},{"body_a":"world","body_b":"grasp_target","contact_count":1524.0,"contact_point_centroid":[0.51251,0.03972,-0.00191],"force_p95":0.13468,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12295,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50272,0.01693,0.24609]},{"body_a":"world","body_b":"grasp_target","contact_count":3604.0,"contact_point_centroid":[0.51251,0.03972,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50617,0.0372,0.10703]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4972.0,"contact_point_centroid":[0.5,0.05769,0.03156],"force_p95":0.07234,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08609,"mean_force":0.04475,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49949,0.03855,0.02975]}],"total_contact_groups":11},"final_pose_error":0.08795,"key_states":{"actual_goal_position":[0.62757,0.17252,0.14502],"final_object_position":[0.57961,0.12982,0.01602],"final_tcp_position":[0.56447,0.11188,0.13632],"realised_goal_position":[0.62757,0.17252,0.14502],"realised_object_initial_position":[0.51251,0.03972,0.03]},"peak_contact_force":1.27015,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":382.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.03],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21001,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1524.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.50766,0.03501,0.19222],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.16634,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":901.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3604.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.50747,0.03921,0.03846],"tcp_start":[0.50766,0.03501,0.19222],"tcp_to_object_dist_end":0.01343,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.5124,0.03855,0.02565],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21322,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.14636,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10846.0,"raw_peak_contact_force":0.22487,"subtask_id":"grasp_1","tcp_end":[0.49946,0.03855,0.02972],"tcp_start":[0.50747,0.03921,0.03846],"tcp_to_object_dist_end":0.01357,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":31.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50765,0.03823,0.12644],"object_pos_start":[0.5124,0.03855,0.02565],"object_to_goal_dist_end":0.181,"object_to_goal_dist_start":0.21322,"object_z_max":0.12635,"peak_contact_force":0.11617,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":34425.0,"raw_peak_contact_force":0.64974,"tcp_end":[0.49542,0.03823,0.1414],"tcp_start":[0.49946,0.03855,0.02972],"tcp_to_object_dist_end":0.01932,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.57409,0.11961,0.04726],"object_pos_start":[0.50765,0.03823,0.12644],"object_to_goal_dist_end":0.12336,"object_to_goal_dist_start":0.181,"object_z_max":0.12647,"peak_contact_force":0.0,"phase_name":"transport_arc","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":20773.0,"raw_peak_contact_force":0.2319,"subtask_id":"transport_arc","tcp_end":[0.56447,0.11188,0.13632],"tcp_start":[0.49542,0.03823,0.1414],"tcp_to_object_dist_end":0.08992,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.57961,0.12982,0.01602],"object_pos_start":[0.57409,0.11961,0.04726],"object_to_goal_dist_end":0.14411,"object_to_goal_dist_start":0.12336,"object_z_max":0.04726,"peak_contact_force":0.12268,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":744.0,"raw_peak_contact_force":1.27015,"subtask_id":"release_1","tcp_end":[0.55823,0.11061,0.15884],"tcp_start":[0.56447,0.11188,0.13632],"tcp_to_object_dist_end":0.14568,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.38667,"average_solve_count":150.0,"average_success_count":150.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.14512,"approach_1.speed":0.06843,"descend_1.grasp_z_offset":0.00855,"descend_1.speed":0.06748,"lift_1.lift_height":0.26915,"lift_1.speed":0.05828,"transport_arc.speed":0.09992},"optimized_scores":{"best_composite_score":0.11113,"best_fitness_score":0.58113,"best_task_score":0.20262},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":725.0,"contact_point_centroid":[0.52087,0.14157,-0.00324],"force_p95":0.65336,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.63309,"mean_force":0.18548,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.51231,0.13027,0.17193]},{"body_a":"world","body_b":"grasp_target","contact_count":175.0,"contact_point_centroid":[0.47822,0.04593,-0.00124],"force_p95":0.4532,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.64703,"mean_force":0.10455,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46862,0.04709,0.03]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":20077.0,"contact_point_centroid":[0.46626,0.06601,0.07805],"force_p95":0.07496,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31469,"mean_force":0.05095,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46616,0.04686,0.07628]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":20081.0,"contact_point_centroid":[0.46629,0.02772,0.0801],"force_p95":0.07407,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27799,"mean_force":0.05028,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46616,0.04686,0.07803]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":12708.0,"contact_point_centroid":[0.48997,0.06619,0.14188],"force_p95":0.12724,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25223,"mean_force":0.07059,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.48694,0.08482,0.14225]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.48274,0.04847,-0.00213],"force_p95":0.16063,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24409,"mean_force":0.13297,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47143,0.04738,0.0294]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":12240.0,"contact_point_centroid":[0.49123,0.10515,0.14288],"force_p95":0.12925,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23564,"mean_force":0.0748,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.48795,0.08643,0.14313]},{"body_a":"world","body_b":"grasp_target","contact_count":1612.0,"contact_point_centroid":[0.4827,0.04873,-0.00192],"force_p95":0.13462,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12293,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48984,0.02092,0.24168]},{"body_a":"world","body_b":"grasp_target","contact_count":3488.0,"contact_point_centroid":[0.4827,0.04873,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.47798,0.04561,0.10547]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5018.0,"contact_point_centroid":[0.47011,0.02802,0.0312],"force_p95":0.06943,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11359,"mean_force":0.043,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47029,0.04726,0.02825]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5505.0,"contact_point_centroid":[0.46992,0.06659,0.03057],"force_p95":0.06944,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08094,"mean_force":0.04114,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.4703,0.04726,0.02826]}],"total_contact_groups":11},"final_pose_error":0.13293,"key_states":{"actual_goal_position":[0.58187,0.22885,0.23048],"final_object_position":[0.5208,0.14157,0.01602],"final_tcp_position":[0.51654,0.13126,0.16822],"realised_goal_position":[0.58187,0.22885,0.23048],"realised_object_initial_position":[0.4827,0.04873,0.03]},"peak_contact_force":1.63309,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":404.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.03],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28719,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1612.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.48108,0.04326,0.18315],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.15724,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":872.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3488.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.47799,0.04803,0.03607],"tcp_start":[0.48108,0.04326,0.18315],"tcp_to_object_dist_end":0.01112,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":47.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.4826,0.04742,0.02554],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.29116,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.15426,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12323.0,"raw_peak_contact_force":0.24409,"subtask_id":"grasp_1","tcp_end":[0.47027,0.04726,0.02822],"tcp_start":[0.47799,0.04803,0.03607],"tcp_to_object_dist_end":0.01262,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.47672,0.04704,0.11414],"object_pos_start":[0.4826,0.04742,0.02554],"object_to_goal_dist_end":0.2401,"object_to_goal_dist_start":0.29116,"object_z_max":0.11406,"peak_contact_force":0.07975,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":40333.0,"raw_peak_contact_force":0.64703,"tcp_end":[0.46613,0.04687,0.12491],"tcp_start":[0.47027,0.04726,0.02822],"tcp_to_object_dist_end":0.0151,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.52497,0.14454,0.06233],"object_pos_start":[0.47672,0.04704,0.11414],"object_to_goal_dist_end":0.19652,"object_to_goal_dist_start":0.2401,"object_z_max":0.1416,"peak_contact_force":0.0,"phase_name":"transport_arc","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":24948.0,"raw_peak_contact_force":0.25223,"subtask_id":"transport_arc","tcp_end":[0.51654,0.13126,0.16822],"tcp_start":[0.46613,0.04687,0.12491],"tcp_to_object_dist_end":0.10705,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.5208,0.14157,0.01602],"object_pos_start":[0.52497,0.14454,0.06233],"object_to_goal_dist_end":0.23947,"object_to_goal_dist_start":0.19652,"object_z_max":0.06233,"peak_contact_force":0.12271,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":725.0,"raw_peak_contact_force":1.63309,"subtask_id":"release_1","tcp_end":[0.51114,0.12995,0.19224],"tcp_start":[0.51654,0.13126,0.16822],"tcp_to_object_dist_end":0.17687,"terminated_normally":true,"termination_reason":"step_budget"}],"success":false}]}
```