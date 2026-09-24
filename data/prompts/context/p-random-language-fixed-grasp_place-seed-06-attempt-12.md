## Search State

- **Seed**: 6
- **Iteration**: 13 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 12 | approach → descend → grasp → lift → approach → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | time_limit | time_limit | pose_tolerance | time_limit | 9 | 0.1035 | 0.39 | ❌ rejected |
| 11 | approach → descend → grasp → lift → approach → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | time_limit | time_limit | pose_tolerance | time_limit | 8 | 0.2068 | 0.50 | ✅ accepted |
| 10 | approach → descend → grasp → lift → approach → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | time_limit | 7 | 0.1478 | 0.28 | ❌ rejected |
| 9 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 11 | -0.0663 | 0.31 | ❌ rejected |
| 8 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | force_threshold_switch | position_control | position_control | position_control | position_control | position_control | pose_tolerance | force_exceeded | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 10 | -0.3272 | 0.17 | ❌ rejected |

**Proposal policy**: task_score is 0.39 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.103) — your mutation base

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
  termination: time_limit
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
    lift_time:
      type: scalar
      range:
      - 1.0
      - 5.0
      default: 2.0
      binds_to:
      - path: duration.max_time
        mode: add
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
  generator: linear_cartesian
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.0
    orientation:
      mode: keep_current
  parameters:
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
    on_failure: abort
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
    - lift_time: status=consumed; consumers=duration.max_time (add)
    - speed: status=consumed; consumers=generator.speed (add)
- **transport_to_goal** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings:
    - speed: status=consumed; consumers=generator.speed (add)
- **release_at_goal** (`release`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0]
  - parameter_bindings:
    - max_time: status=consumed; consumers=duration.max_time (add)
  - guards:
    - id=object_still_grasped, when=before_phase, predicate=bilateral_grasp, on_failure=abort, threshold=0.5

## Design Metrics

- **Composite score**: 0.103
- **task_score** (E): 0.393
- **fitness_score**: 0.673  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.570

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_to_object | 1.00 | 1.00 | 0.2651 |
| descend_to_grasp | 1.00 | 1.00 | 0.0047 |
| grasp_object | 1.00 | 1.00 | 0.0124 |
| lift_object | 1.00 | 1.00 | 0.1477 |
| transport_to_goal | 1.00 | 0.33 | 0.1957 |
| release_at_goal | 0.00 | 0.33 | 0.0000 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_to_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.495, 0.023, 0.038) | (0.500, 0.024, 0.030)→(0.500, 0.024, 0.026) | 0.269→0.271 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_to_grasp | descend | 1.00 / step_budget | (0.495, 0.023, 0.038)→(0.494, 0.023, 0.034) | (0.500, 0.024, 0.026)→(0.500, 0.024, 0.026) | 0.271→0.271 | 1.00 / 4.000 | 27.129 | 0.123 |
| grasp_object | grasp | 1.00 / step_budget | (0.494, 0.023, 0.034)→(0.485, 0.023, 0.025) | (0.500, 0.024, 0.026)→(0.500, 0.023, 0.025) | 0.271→0.273 | 1.00 / 42.000 | 0.176 | 0.251 |
| lift_object | lift | 1.00 / time_limit | (0.485, 0.023, 0.025)→(0.482, 0.022, 0.172) | (0.500, 0.023, 0.025)→(0.494, 0.023, 0.162) | 0.273→0.213 | 1.00 / 32.667 | 0.091 | 0.745 |
| transport_to_goal | approach | 1.00 / step_budget | (0.482, 0.022, 0.172)→(0.584, 0.177, 0.213) | (0.494, 0.023, 0.162)→(0.599, 0.190, 0.065) | 0.213→0.144 | 0.33 / 0.333 | 0.474 | 0.694 |
| release_at_goal | release | 0.00 / guard_failure | (0.584, 0.177, 0.213)→(0.584, 0.177, 0.213) | (0.599, 0.190, 0.065)→(0.599, 0.190, 0.065) | 0.144→0.144 | 0.33 / 0.333 | 0.474 | 0.000 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.451
- phase_score: 0.701
- phase_breakdown.transport_arc_score: 0.628
- phase_breakdown.release_1_score: 0.628
- phase_breakdown.approach_1_score: 0.820
- phase_breakdown.grasp_1_score: 1.000
- phase_breakdown.descend_1_score: 0.698
- grasp_place_fitness: 0.701

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.701
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.451
- **Median Q (composite search score)**: 0.131
- **K-run variance**: 0.0016
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.271


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.0,"average_solve_count":107.0,"average_success_count":107.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_to_object.speed":0.08271,"descend_to_grasp.speed":0.07722,"grasp_object.max_time":0.52772,"lift_object.lift_height":0.16755,"lift_object.lift_time":4.32868,"lift_object.speed":0.05179,"release_at_goal.max_time":0.74415,"transport_to_goal.speed":0.23503,"transport_to_goal.z_raise":0.01157},"optimized_scores":{"best_composite_score":0.04779,"best_fitness_score":0.61779,"best_task_score":0.28167},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":308.0,"contact_point_centroid":[0.49957,-0.01516,-0.0015],"force_p95":0.31967,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.71182,"mean_force":0.12829,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.4867,-0.01494,0.02557]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":17223.0,"contact_point_centroid":[0.4859,-0.03408,0.10058],"force_p95":0.08193,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31151,"mean_force":0.05878,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.48505,-0.01492,0.09823]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":19994.0,"contact_point_centroid":[0.48673,0.00405,0.09578],"force_p95":0.07743,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30459,"mean_force":0.05206,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.48504,-0.01492,0.09404]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":10159.0,"contact_point_centroid":[0.52192,0.03776,0.20285],"force_p95":0.14505,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28486,"mean_force":0.08613,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.51859,0.05673,0.2028]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":13615.0,"contact_point_centroid":[0.52543,0.08129,0.20473],"force_p95":0.09525,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20811,"mean_force":0.06461,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.5217,0.06299,0.20511]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50383,-0.01566,-0.00205],"force_p95":0.14106,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.18414,"mean_force":0.12716,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.49048,-0.01497,0.02615]},{"body_a":"grasp_target","body_b":"hand","contact_count":47.0,"contact_point_centroid":[0.51421,-0.03504,0.05925],"force_p95":0.01122,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1557,"mean_force":0.0102,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.48566,-0.01493,0.02649]},{"body_a":"world","body_b":"grasp_target","contact_count":2916.0,"contact_point_centroid":[0.50382,-0.01567,-0.00195],"force_p95":0.12867,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12279,"phase_index":0.0,"phase_name":"approach_to_object","phase_type":"approach","tcp_position_centroid":[0.49837,-0.00736,0.16848]},{"body_a":"world","body_b":"grasp_target","contact_count":92.0,"contact_point_centroid":[0.50382,-0.01567,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.49793,-0.01491,0.03649]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5293.0,"contact_point_centroid":[0.49023,0.00408,0.02695],"force_p95":0.06397,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10194,"mean_force":0.04106,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.48923,-0.01496,0.02485]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4185.0,"contact_point_centroid":[0.48898,-0.03425,0.02764],"force_p95":0.07753,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08865,"mean_force":0.05192,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.48923,-0.01496,0.02485]}],"total_contact_groups":11},"final_pose_error":0.03144,"key_states":{"actual_goal_position":[0.58691,0.18745,0.24812],"final_object_position":[0.5903,0.1745,0.05854],"final_tcp_position":[0.57312,0.16438,0.24338],"realised_goal_position":[0.58691,0.18745,0.24812],"realised_object_initial_position":[0.50382,-0.01567,0.03]},"peak_contact_force":81.14225,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":730.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.03],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.30942,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_to_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2916.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.49878,-0.01483,0.03858],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.01356,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":23.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":81.14225,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":92.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.49783,-0.015,0.0339],"tcp_start":[0.49878,-0.01483,0.03858],"tcp_to_object_dist_end":0.00991,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50367,-0.01533,0.0258],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31221,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.14044,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11278.0,"raw_peak_contact_force":0.18414,"subtask_id":"grasp_1","tcp_end":[0.4892,-0.01496,0.02482],"tcp_start":[0.49783,-0.015,0.0339],"tcp_to_object_dist_end":0.01451,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":34.0,"n_steps":991.0,"n_steps_budget":1000.0,"object_pos_end":[0.49825,-0.01526,0.17025],"object_pos_start":[0.50367,-0.01533,0.0258],"object_to_goal_dist_end":0.23455,"object_to_goal_dist_start":0.31221,"object_z_max":0.17013,"peak_contact_force":0.0905,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":37572.0,"raw_peak_contact_force":0.71182,"tcp_end":[0.48558,-0.01491,0.18016],"tcp_start":[0.4892,-0.01496,0.02482],"tcp_to_object_dist_end":0.01609,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5903,0.1745,0.05854],"object_pos_start":[0.49825,-0.01526,0.17025],"object_to_goal_dist_end":0.19005,"object_to_goal_dist_start":0.23455,"object_z_max":0.21048,"peak_contact_force":0.0,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":23774.0,"raw_peak_contact_force":0.28486,"subtask_id":"transport_arc","tcp_end":[0.57312,0.16438,0.24338],"tcp_start":[0.48558,-0.01491,0.18016],"tcp_to_object_dist_end":0.18591,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":0.0,"n_steps_budget":0.0,"object_pos_end":[0.5903,0.1745,0.05854],"object_pos_start":[0.5903,0.1745,0.05854],"object_to_goal_dist_end":0.19005,"object_to_goal_dist_start":0.19005,"peak_contact_force":0.0,"phase_name":"release_at_goal","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"release_1","tcp_end":[0.57312,0.16438,0.24338],"tcp_start":[0.57312,0.16438,0.24338],"tcp_to_object_dist_end":0.18591,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.72727,"average_solve_count":121.0,"average_success_count":121.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_to_object.speed":0.05299,"descend_to_grasp.speed":0.04191,"grasp_object.max_time":0.81905,"lift_object.lift_height":0.16371,"lift_object.lift_time":2.63374,"lift_object.speed":0.06011,"release_at_goal.max_time":0.75405,"transport_to_goal.speed":0.16191,"transport_to_goal.z_raise":0.01994},"optimized_scores":{"best_composite_score":0.13134,"best_fitness_score":0.70134,"best_task_score":0.45094},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":4.0,"contact_point_centroid":[0.60421,0.17394,-0.00217],"force_p95":1.42828,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.42859,"mean_force":1.39244,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.61208,0.15979,0.15724]},{"body_a":"world","body_b":"grasp_target","contact_count":297.0,"contact_point_centroid":[0.50874,0.03685,-0.00173],"force_p95":0.41685,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.7711,"mean_force":0.13356,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.49492,0.03686,0.02505]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":10808.0,"contact_point_centroid":[0.49639,0.05587,0.09007],"force_p95":0.11107,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.39947,"mean_force":0.07814,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.49332,0.03674,0.08759]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":14507.0,"contact_point_centroid":[0.49685,0.01827,0.08686],"force_p95":0.10213,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30937,"mean_force":0.06072,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.49331,0.03674,0.08596]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":10691.0,"contact_point_centroid":[0.5467,0.06945,0.16378],"force_p95":0.14894,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28712,"mean_force":0.08277,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.54104,0.08764,0.16467]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":10866.0,"contact_point_centroid":[0.54838,0.11005,0.16406],"force_p95":0.1288,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28315,"mean_force":0.08014,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.54462,0.0913,0.16426]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.51271,0.03949,-0.00226],"force_p95":0.1953,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.27974,"mean_force":0.14198,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.49876,0.03717,0.02533]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5176.0,"contact_point_centroid":[0.49911,0.01827,0.02591],"force_p95":0.06591,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21069,"mean_force":0.04089,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.49751,0.03707,0.02399]},{"body_a":"grasp_target","body_b":"hand","contact_count":45.0,"contact_point_centroid":[0.52097,0.05604,0.05943],"force_p95":0.0168,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1565,"mean_force":0.01287,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.4939,0.03678,0.02594]},{"body_a":"world","body_b":"grasp_target","contact_count":3276.0,"contact_point_centroid":[0.51251,0.03972,-0.00195],"force_p95":0.12696,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12277,"phase_index":0.0,"phase_name":"approach_to_object","phase_type":"approach","tcp_position_centroid":[0.50236,0.01856,0.16778]},{"body_a":"world","body_b":"grasp_target","contact_count":92.0,"contact_point_centroid":[0.51251,0.03972,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.5062,0.03748,0.03584]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3960.0,"contact_point_centroid":[0.49887,0.05657,0.02678],"force_p95":0.09475,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10702,"mean_force":0.05904,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.49752,0.03707,0.024]}],"total_contact_groups":12},"final_pose_error":0.02124,"key_states":{"actual_goal_position":[0.62757,0.17252,0.14502],"final_object_position":[0.625,0.1731,0.02559],"final_tcp_position":[0.61227,0.16,0.15721],"realised_goal_position":[0.62757,0.17252,0.14502],"realised_object_initial_position":[0.51251,0.03972,0.03]},"peak_contact_force":1.42859,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":820.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.03],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21001,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_to_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3276.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.50699,0.03736,0.03787],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.01328,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":23.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":92.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.50616,0.03771,0.03331],"tcp_start":[0.50699,0.03736,0.03787],"tcp_to_object_dist_end":0.00987,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":42.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51264,0.03776,0.02513],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21388,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.18724,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10936.0,"raw_peak_contact_force":0.27974,"subtask_id":"grasp_1","tcp_end":[0.49748,0.03707,0.02396],"tcp_start":[0.50616,0.03771,0.03331],"tcp_to_object_dist_end":0.01522,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":27.0,"n_steps":841.0,"n_steps_budget":870.0,"object_pos_end":[0.50878,0.0378,0.16079],"object_pos_start":[0.51264,0.03776,0.02513],"object_to_goal_dist_end":0.1803,"object_to_goal_dist_start":0.21388,"object_z_max":0.16066,"peak_contact_force":0.10112,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":25657.0,"raw_peak_contact_force":0.7711,"tcp_end":[0.49386,0.03678,0.17439],"tcp_start":[0.49748,0.03707,0.02396],"tcp_to_object_dist_end":0.02021,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.625,0.1731,0.02559],"object_pos_start":[0.50878,0.0378,0.16079],"object_to_goal_dist_end":0.11946,"object_to_goal_dist_start":0.1803,"object_z_max":0.16087,"peak_contact_force":1.42121,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":21561.0,"raw_peak_contact_force":1.42859,"subtask_id":"transport_arc","tcp_end":[0.61227,0.16,0.15721],"tcp_start":[0.49386,0.03678,0.17439],"tcp_to_object_dist_end":0.13288,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":0.0,"n_steps_budget":0.0,"object_pos_end":[0.625,0.1731,0.02559],"object_pos_start":[0.625,0.1731,0.02559],"object_to_goal_dist_end":0.11946,"object_to_goal_dist_start":0.11946,"peak_contact_force":1.42121,"phase_name":"release_at_goal","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"release_1","tcp_end":[0.61227,0.16,0.15721],"tcp_start":[0.61227,0.16,0.15721],"tcp_to_object_dist_end":0.13288,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.71552,"average_solve_count":116.0,"average_success_count":116.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_to_object.speed":0.06964,"descend_to_grasp.speed":0.06181,"grasp_object.max_time":0.53822,"lift_object.lift_height":0.18545,"lift_object.lift_time":3.46286,"lift_object.speed":0.0435,"release_at_goal.max_time":0.53879,"transport_to_goal.speed":0.16027,"transport_to_goal.z_raise":0.02709},"optimized_scores":{"best_composite_score":0.13129,"best_fitness_score":0.70129,"best_task_score":0.44578},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":256.0,"contact_point_centroid":[0.47823,0.04425,-0.00153],"force_p95":0.40692,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.75116,"mean_force":0.12443,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.46703,0.04528,0.02751]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":13435.0,"contact_point_centroid":[0.5088,0.09153,0.19083],"force_p95":0.11574,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.36811,"mean_force":0.06751,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.50376,0.10981,0.19082]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":16900.0,"contact_point_centroid":[0.46499,0.0643,0.09412],"force_p95":0.08424,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.35481,"mean_force":0.0594,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.4651,0.0451,0.0915]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":12103.0,"contact_point_centroid":[0.5083,0.13246,0.19344],"force_p95":0.10887,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33575,"mean_force":0.07443,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.50605,0.11341,0.1926]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":20931.0,"contact_point_centroid":[0.46716,0.0262,0.09201],"force_p95":0.07868,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30374,"mean_force":0.04909,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.4651,0.0451,0.0905]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.48291,0.04842,-0.00232],"force_p95":0.20954,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.28866,"mean_force":0.14594,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.47051,0.04562,0.02684]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4919.0,"contact_point_centroid":[0.47127,0.02659,0.02693],"force_p95":0.0784,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21038,"mean_force":0.04328,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.46929,0.0455,0.02562]},{"body_a":"world","body_b":"grasp_target","contact_count":3128.0,"contact_point_centroid":[0.4827,0.04873,-0.00195],"force_p95":0.12742,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12278,"phase_index":0.0,"phase_name":"approach_to_object","phase_type":"approach","tcp_position_centroid":[0.48838,0.02272,0.16838]},{"body_a":"world","body_b":"grasp_target","contact_count":92.0,"contact_point_centroid":[0.4827,0.04873,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.4779,0.04596,0.03664]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4137.0,"contact_point_centroid":[0.46965,0.06501,0.02812],"force_p95":0.09514,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09882,"mean_force":0.05479,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.4693,0.04551,0.02564]},{"body_a":"grasp_target","body_b":"hand","contact_count":44.0,"contact_point_centroid":[0.49451,0.0646,0.06109],"force_p95":0.01629,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08763,"mean_force":0.00814,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.4659,0.04518,0.02918]}],"total_contact_groups":11},"final_pose_error":0.0319,"key_states":{"actual_goal_position":[0.58187,0.22885,0.23048],"final_object_position":[0.58037,0.22165,0.10952],"final_tcp_position":[0.56652,0.20764,0.23937],"realised_goal_position":[0.58187,0.22885,0.23048],"realised_object_initial_position":[0.4827,0.04873,0.03]},"peak_contact_force":0.75116,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":783.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.03],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28719,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_to_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3128.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.47879,0.0458,0.03862],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.01351,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":23.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":92.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.47769,0.04625,0.0341],"tcp_start":[0.47879,0.0458,0.03862],"tcp_to_object_dist_end":0.00983,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.48279,0.04624,0.02493],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.29226,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.19991,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10856.0,"raw_peak_contact_force":0.28866,"subtask_id":"grasp_1","tcp_end":[0.46927,0.0455,0.0256],"tcp_start":[0.47769,0.04625,0.0341],"tcp_to_object_dist_end":0.01356,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.4763,0.04613,0.1542],"object_pos_start":[0.48279,0.04624,0.02493],"object_to_goal_dist_end":0.22439,"object_to_goal_dist_start":0.29226,"object_z_max":0.15403,"peak_contact_force":0.08196,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":38131.0,"raw_peak_contact_force":0.75116,"tcp_end":[0.46544,0.04513,0.16264],"tcp_start":[0.46927,0.0455,0.0256],"tcp_to_object_dist_end":0.0138,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.58037,0.22165,0.10952],"object_pos_start":[0.4763,0.04613,0.1542],"object_to_goal_dist_end":0.12119,"object_to_goal_dist_start":0.22439,"object_z_max":0.20574,"peak_contact_force":0.0,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":25538.0,"raw_peak_contact_force":0.36811,"subtask_id":"transport_arc","tcp_end":[0.56652,0.20764,0.23937],"tcp_start":[0.46544,0.04513,0.16264],"tcp_to_object_dist_end":0.13134,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":0.0,"n_steps_budget":0.0,"object_pos_end":[0.58037,0.22165,0.10952],"object_pos_start":[0.58037,0.22165,0.10952],"object_to_goal_dist_end":0.12119,"object_to_goal_dist_start":0.12119,"peak_contact_force":0.0,"phase_name":"release_at_goal","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"release_1","tcp_end":[0.56652,0.20764,0.23937],"tcp_start":[0.56652,0.20764,0.23937],"tcp_to_object_dist_end":0.13134,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":true}]}
```