## Search State

- **Seed**: 6
- **Iteration**: 14 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 13 | approach → descend → grasp → lift → approach → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | time_limit | pose_tolerance | time_limit | 8 | 0.1813 | 0.44 | ❌ rejected |
| 12 | approach → descend → grasp → lift → approach → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | time_limit | time_limit | pose_tolerance | time_limit | 9 | 0.1035 | 0.39 | ❌ rejected |
| 11 | approach → descend → grasp → lift → approach → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | time_limit | time_limit | pose_tolerance | time_limit | 8 | 0.2068 | 0.50 | ✅ accepted |
| 10 | approach → descend → grasp → lift → approach → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | time_limit | 7 | 0.1478 | 0.28 | ❌ rejected |
| 9 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 11 | -0.0663 | 0.31 | ❌ rejected |

**Proposal policy**: task_score is 0.44 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.181) — your mutation base

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

- **Composite score**: 0.181
- **task_score** (E): 0.444
- **fitness_score**: 0.701  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.520

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_to_object | 1.00 | 1.00 | 0.2650 |
| descend_to_grasp | 1.00 | 1.00 | 0.0043 |
| grasp_object | 1.00 | 1.00 | 0.0115 |
| lift_object | 1.00 | 1.00 | 0.2188 |
| transport_to_goal | 1.00 | 0.67 | 0.2046 |
| release_at_goal | 0.67 | 0.67 | 0.0144 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_to_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.495, 0.023, 0.038) | (0.500, 0.024, 0.030)→(0.500, 0.024, 0.026) | 0.269→0.271 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_to_grasp | descend | 1.00 / step_budget | (0.495, 0.023, 0.038)→(0.494, 0.023, 0.034) | (0.500, 0.024, 0.026)→(0.500, 0.024, 0.026) | 0.271→0.271 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_object | grasp | 1.00 / step_budget | (0.494, 0.023, 0.034)→(0.487, 0.023, 0.026) | (0.500, 0.024, 0.026)→(0.500, 0.023, 0.025) | 0.271→0.273 | 1.00 / 39.667 | 0.169 | 0.266 |
| lift_object | lift | 1.00 / time_limit | (0.487, 0.023, 0.026)→(0.484, 0.022, 0.245) | (0.500, 0.023, 0.025)→(0.498, 0.023, 0.232) | 0.273→0.210 | 1.00 / 32.333 | 0.089 | 0.855 |
| transport_to_goal | approach | 1.00 / step_budget | (0.484, 0.022, 0.245)→(0.590, 0.185, 0.210) | (0.498, 0.023, 0.232)→(0.588, 0.188, 0.171) | 0.210→0.041 | 0.67 / 26.000 | 0.058 | 0.322 |
| release_at_goal | release | 0.67 / step_budget | (0.590, 0.185, 0.210)→(0.587, 0.184, 0.224) | (0.588, 0.188, 0.171)→(0.584, 0.189, 0.077) | 0.041→0.132 | 0.67 / 2.000 | 0.119 | 1.042 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.634
- phase_score: 0.680
- phase_breakdown.transport_arc_score: 0.596
- phase_breakdown.release_1_score: 0.596
- phase_breakdown.approach_1_score: 0.822
- phase_breakdown.grasp_1_score: 1.000
- phase_breakdown.descend_1_score: 0.717
- grasp_place_fitness: 0.796

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.796
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.634
- **Median Q (composite search score)**: 0.184
- **K-run variance**: 0.0061
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.296


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.74561,"average_solve_count":114.0,"average_success_count":114.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_to_object.speed":0.07009,"descend_to_grasp.speed":0.03974,"lift_object.lift_height":0.28026,"lift_object.lift_time":3.69835,"lift_object.speed":0.06421,"release_at_goal.max_time":0.8273,"transport_to_goal.arc_height":0.21086,"transport_to_goal.speed":0.19312},"optimized_scores":{"best_composite_score":0.27576,"best_fitness_score":0.79576,"best_task_score":0.63415},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":250.0,"contact_point_centroid":[0.49987,-0.01452,-0.00144],"force_p95":0.33038,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.76858,"mean_force":0.12503,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.48828,-0.01485,0.02687]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":17433.0,"contact_point_centroid":[0.48765,0.00423,0.11933],"force_p95":0.08544,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.35844,"mean_force":0.05894,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.48664,-0.0148,0.11719]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":10865.0,"contact_point_centroid":[0.5235,0.03815,0.24918],"force_p95":0.1579,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33163,"mean_force":0.08482,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.52021,0.05706,0.24945]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":17920.0,"contact_point_centroid":[0.4876,-0.0338,0.11628],"force_p95":0.08529,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.3309,"mean_force":0.05775,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.48665,-0.0148,0.11426]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":14547.0,"contact_point_centroid":[0.52653,0.08301,0.25062],"force_p95":0.0962,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27982,"mean_force":0.0626,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.52392,0.06461,0.25043]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50383,-0.01544,-0.00207],"force_p95":0.14482,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.21809,"mean_force":0.12863,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.4915,-0.01489,0.02708]},{"body_a":"world","body_b":"grasp_target","contact_count":3100.0,"contact_point_centroid":[0.50382,-0.01567,-0.00195],"force_p95":0.12782,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12278,"phase_index":0.0,"phase_name":"approach_to_object","phase_type":"approach","tcp_position_centroid":[0.49843,-0.00737,0.1678]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4083.0,"contact_point_centroid":[0.49088,0.00433,0.02866],"force_p95":0.07805,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1279,"mean_force":0.05184,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.49035,-0.01488,0.02588]},{"body_a":"world","body_b":"grasp_target","contact_count":88.0,"contact_point_centroid":[0.50382,-0.01567,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.49838,-0.01488,0.0367]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4939.0,"contact_point_centroid":[0.49095,-0.03398,0.02776],"force_p95":0.0704,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08716,"mean_force":0.04474,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.49035,-0.01488,0.02588]}],"total_contact_groups":10},"final_pose_error":0.02587,"key_states":{"actual_goal_position":[0.58691,0.18745,0.24812],"final_object_position":[0.58294,0.17456,0.18114],"final_tcp_position":[0.57382,0.1652,0.24975],"realised_goal_position":[0.58691,0.18745,0.24812],"realised_object_initial_position":[0.50382,-0.01567,0.03]},"peak_contact_force":0.76858,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":776.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.03],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.30942,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_to_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3100.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.49912,-0.01482,0.03858],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.01344,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":22.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":88.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.49829,-0.01496,0.03432],"tcp_start":[0.49912,-0.01482,0.03858],"tcp_to_object_dist_end":0.00999,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50369,-0.01478,0.02575],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31188,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.13985,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10822.0,"raw_peak_contact_force":0.21809,"subtask_id":"grasp_1","tcp_end":[0.49032,-0.01487,0.02585],"tcp_start":[0.49829,-0.01496,0.03432],"tcp_to_object_dist_end":0.01336,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":32.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50081,-0.0148,0.21159],"object_pos_start":[0.50369,-0.01478,0.02575],"object_to_goal_dist_end":0.22283,"object_to_goal_dist_start":0.31188,"object_z_max":0.21136,"peak_contact_force":0.08807,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":35603.0,"raw_peak_contact_force":0.76858,"tcp_end":[0.48724,-0.01478,0.22466],"tcp_start":[0.49032,-0.01487,0.02585],"tcp_to_object_dist_end":0.01883,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.58294,0.17456,0.18114],"object_pos_start":[0.50081,-0.0148,0.21159],"object_to_goal_dist_end":0.06832,"object_to_goal_dist_start":0.22283,"object_z_max":0.23968,"peak_contact_force":0.0,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":25412.0,"raw_peak_contact_force":0.33163,"subtask_id":"transport_arc","tcp_end":[0.57382,0.1652,0.24975],"tcp_start":[0.48724,-0.01478,0.22466],"tcp_to_object_dist_end":0.06985,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":0.0,"n_steps_budget":0.0,"object_pos_end":[0.58294,0.17456,0.18114],"object_pos_start":[0.58294,0.17456,0.18114],"object_to_goal_dist_end":0.06832,"object_to_goal_dist_start":0.06832,"peak_contact_force":0.0,"phase_name":"release_at_goal","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"release_1","tcp_end":[0.57382,0.1652,0.24975],"tcp_start":[0.57382,0.1652,0.24975],"tcp_to_object_dist_end":0.06985,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.90625,"average_solve_count":128.0,"average_success_count":128.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_to_object.speed":0.05133,"descend_to_grasp.speed":0.04931,"lift_object.lift_height":0.22746,"lift_object.lift_time":3.11369,"lift_object.speed":0.07326,"release_at_goal.max_time":0.91486,"transport_to_goal.arc_height":0.09126,"transport_to_goal.speed":0.11694},"optimized_scores":{"best_composite_score":0.18432,"best_fitness_score":0.70432,"best_task_score":0.45268},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":145.0,"contact_point_centroid":[0.60263,0.17367,-0.00823],"force_p95":1.16927,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.43575,"mean_force":0.48519,"phase_index":5.0,"phase_name":"release_at_goal","phase_type":"release","tcp_position_centroid":[0.61527,0.16702,0.1611]},{"body_a":"world","body_b":"grasp_target","contact_count":244.0,"contact_point_centroid":[0.50864,0.03635,-0.00165],"force_p95":0.38457,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.81133,"mean_force":0.12968,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.49656,0.03692,0.02647]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":15792.0,"contact_point_centroid":[0.49631,0.01775,0.12667],"force_p95":0.09064,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.40382,"mean_force":0.06217,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.49494,0.0368,0.12433]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":17433.0,"contact_point_centroid":[0.49607,0.05577,0.12056],"force_p95":0.08584,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.39568,"mean_force":0.0578,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.49494,0.0368,0.11877]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":14099.0,"contact_point_centroid":[0.56817,0.09396,0.22705],"force_p95":0.09871,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33887,"mean_force":0.06743,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.56772,0.11318,0.22603]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":18487.0,"contact_point_centroid":[0.56621,0.12985,0.23001],"force_p95":0.08222,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29696,"mean_force":0.05152,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.56565,0.11105,0.22845]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.51264,0.03919,-0.00224],"force_p95":0.19511,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.28587,"mean_force":0.14142,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.49977,0.03719,0.02636]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1182.0,"contact_point_centroid":[0.6179,0.14914,0.1492],"force_p95":0.08121,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25139,"mean_force":0.04455,"phase_index":5.0,"phase_name":"release_at_goal","phase_type":"release","tcp_position_centroid":[0.61934,0.16837,0.14773]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1386.0,"contact_point_centroid":[0.61845,0.18771,0.14803],"force_p95":0.08287,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23794,"mean_force":0.05012,"phase_index":5.0,"phase_name":"release_at_goal","phase_type":"release","tcp_position_centroid":[0.61914,0.1683,0.14738]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3572.0,"contact_point_centroid":[0.50016,0.01791,0.02837],"force_p95":0.09089,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15999,"mean_force":0.05784,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.49861,0.0371,0.02511]},{"body_a":"world","body_b":"grasp_target","contact_count":3292.0,"contact_point_centroid":[0.51251,0.03972,-0.00195],"force_p95":0.12693,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12277,"phase_index":0.0,"phase_name":"approach_to_object","phase_type":"approach","tcp_position_centroid":[0.50257,0.01868,0.16716]},{"body_a":"world","body_b":"grasp_target","contact_count":88.0,"contact_point_centroid":[0.51251,0.03972,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.50669,0.03751,0.0362]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4898.0,"contact_point_centroid":[0.49962,0.05633,0.02709],"force_p95":0.08112,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09015,"mean_force":0.04673,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.49862,0.0371,0.02512]}],"total_contact_groups":13},"final_pose_error":0.00988,"key_states":{"actual_goal_position":[0.62757,0.17252,0.14502],"final_object_position":[0.61147,0.1736,0.02724],"final_tcp_position":[0.62133,0.16888,0.15178],"realised_goal_position":[0.62757,0.17252,0.14502],"realised_object_initial_position":[0.51251,0.03972,0.03]},"peak_contact_force":1.43575,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":824.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.03],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21001,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_to_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3292.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.50742,0.0374,0.03809],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.0133,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":22.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":88.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.50664,0.03772,0.03384],"tcp_start":[0.50742,0.0374,0.03809],"tcp_to_object_dist_end":0.00999,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":38.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51241,0.03714,0.02522],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21434,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.17771,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10270.0,"raw_peak_contact_force":0.28587,"subtask_id":"grasp_1","tcp_end":[0.49858,0.03709,0.02508],"tcp_start":[0.50664,0.03772,0.03384],"tcp_to_object_dist_end":0.01383,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":32.0,"n_steps":961.0,"n_steps_budget":990.0,"object_pos_end":[0.51005,0.0371,0.22548],"object_pos_start":[0.51241,0.03714,0.02522],"object_to_goal_dist_end":0.19653,"object_to_goal_dist_start":0.21434,"object_z_max":0.22531,"peak_contact_force":0.08629,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":33469.0,"raw_peak_contact_force":0.81133,"tcp_end":[0.4957,0.03688,0.23815],"tcp_start":[0.49858,0.03709,0.02508],"tcp_to_object_dist_end":0.01914,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":927.0,"n_steps_budget":1000.0,"object_pos_end":[0.61305,0.16877,0.12835],"object_pos_start":[0.51005,0.0371,0.22548],"object_to_goal_dist_end":0.02242,"object_to_goal_dist_start":0.19653,"object_z_max":0.23465,"peak_contact_force":0.08391,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":32586.0,"raw_peak_contact_force":0.33887,"subtask_id":"transport_arc","tcp_end":[0.62133,0.16888,0.15178],"tcp_start":[0.4957,0.03688,0.23815],"tcp_to_object_dist_end":0.02484,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.61147,0.1736,0.02724],"object_pos_start":[0.61305,0.16877,0.12835],"object_to_goal_dist_end":0.11889,"object_to_goal_dist_start":0.02242,"object_z_max":0.12835,"peak_contact_force":0.28405,"phase_name":"release_at_goal","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2713.0,"raw_peak_contact_force":1.43575,"subtask_id":"release_1","tcp_end":[0.61518,0.16699,0.17184],"tcp_start":[0.62133,0.16888,0.15178],"tcp_to_object_dist_end":0.1448,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.03546,"average_solve_count":141.0,"average_success_count":141.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_to_object.speed":0.04293,"descend_to_grasp.speed":0.03294,"lift_object.lift_height":0.28758,"lift_object.lift_time":2.89483,"lift_object.speed":0.0788,"release_at_goal.max_time":0.65994,"transport_to_goal.arc_height":0.20795,"transport_to_goal.speed":0.11631},"optimized_scores":{"best_composite_score":0.08392,"best_fitness_score":0.60392,"best_task_score":0.24663},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":187.0,"contact_point_centroid":[0.55692,0.21977,-0.00804],"force_p95":1.09839,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.69036,"mean_force":0.39287,"phase_index":5.0,"phase_name":"release_at_goal","phase_type":"release","tcp_position_centroid":[0.57104,0.21988,0.24277]},{"body_a":"world","body_b":"grasp_target","contact_count":223.0,"contact_point_centroid":[0.47889,0.04503,-0.00166],"force_p95":0.39102,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.98425,"mean_force":0.12469,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.46883,0.04537,0.02833]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":17924.0,"contact_point_centroid":[0.46774,0.02613,0.14263],"force_p95":0.08515,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.41605,"mean_force":0.05731,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.46732,0.04524,0.14018]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":19151.0,"contact_point_centroid":[0.46746,0.06429,0.13837],"force_p95":0.08173,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.40922,"mean_force":0.0547,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.4673,0.04524,0.13641]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":20211.0,"contact_point_centroid":[0.52256,0.15579,0.26742],"force_p95":0.08049,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29642,"mean_force":0.04981,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.52288,0.13689,0.26598]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1177.0,"contact_point_centroid":[0.57222,0.24044,0.22486],"force_p95":0.08442,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29505,"mean_force":0.04793,"phase_index":5.0,"phase_name":"release_at_goal","phase_type":"release","tcp_position_centroid":[0.57392,0.22135,0.225]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.48283,0.04815,-0.0023],"force_p95":0.20906,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.29343,"mean_force":0.14509,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.47177,0.04568,0.02786]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":16694.0,"contact_point_centroid":[0.52541,0.12238,0.2658],"force_p95":0.0953,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28632,"mean_force":0.06138,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.52581,0.1416,0.26462]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1115.0,"contact_point_centroid":[0.57236,0.20211,0.22483],"force_p95":0.09019,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19852,"mean_force":0.04746,"phase_index":5.0,"phase_name":"release_at_goal","phase_type":"release","tcp_position_centroid":[0.57392,0.22135,0.22501]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3554.0,"contact_point_centroid":[0.47174,0.0263,0.03005],"force_p95":0.09422,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16651,"mean_force":0.0584,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.47067,0.04557,0.02674]},{"body_a":"world","body_b":"grasp_target","contact_count":3308.0,"contact_point_centroid":[0.4827,0.04873,-0.00195],"force_p95":0.12693,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12277,"phase_index":0.0,"phase_name":"approach_to_object","phase_type":"approach","tcp_position_centroid":[0.48855,0.02289,0.16768]},{"body_a":"world","body_b":"grasp_target","contact_count":88.0,"contact_point_centroid":[0.4827,0.04873,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.47854,0.04603,0.0369]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5465.0,"contact_point_centroid":[0.47036,0.06485,0.02922],"force_p95":0.07944,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08744,"mean_force":0.04249,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.47068,0.04558,0.02676]}],"total_contact_groups":13},"final_pose_error":0.00993,"key_states":{"actual_goal_position":[0.58187,0.22885,0.23048],"final_object_position":[0.55874,0.21938,0.022],"final_tcp_position":[0.5753,0.22175,0.22828],"realised_goal_position":[0.58187,0.22885,0.23048],"realised_object_initial_position":[0.4827,0.04873,0.03]},"peak_contact_force":1.69036,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":828.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.03],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28719,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_to_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3308.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.47934,0.04589,0.03873],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.01345,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":22.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":88.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.47833,0.04629,0.03457],"tcp_start":[0.47934,0.04589,0.03873],"tcp_to_object_dist_end":0.00991,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.48264,0.04567,0.02504],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.2926,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.18956,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10819.0,"raw_peak_contact_force":0.29343,"subtask_id":"grasp_1","tcp_end":[0.47065,0.04557,0.02672],"tcp_start":[0.47833,0.04629,0.03457],"tcp_to_object_dist_end":0.01211,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":33.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.48178,0.04566,0.25782],"object_pos_start":[0.48264,0.04567,0.02504],"object_to_goal_dist_end":0.21053,"object_to_goal_dist_start":0.2926,"object_z_max":0.25753,"peak_contact_force":0.09304,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":37298.0,"raw_peak_contact_force":0.98425,"tcp_end":[0.46807,0.04532,0.2712],"tcp_start":[0.47065,0.04557,0.02672],"tcp_to_object_dist_end":0.01916,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":993.0,"n_steps_budget":1000.0,"object_pos_end":[0.56681,0.2217,0.20303],"object_pos_start":[0.48178,0.04566,0.25782],"object_to_goal_dist_end":0.03212,"object_to_goal_dist_start":0.21053,"object_z_max":0.25915,"peak_contact_force":0.09149,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":36905.0,"raw_peak_contact_force":0.29642,"subtask_id":"transport_arc","tcp_end":[0.5753,0.22175,0.22828],"tcp_start":[0.46807,0.04532,0.2712],"tcp_to_object_dist_end":0.02664,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.55874,0.21938,0.022],"object_pos_start":[0.56681,0.2217,0.20303],"object_to_goal_dist_end":0.20998,"object_to_goal_dist_start":0.03212,"object_z_max":0.20303,"peak_contact_force":0.07199,"phase_name":"release_at_goal","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2479.0,"raw_peak_contact_force":1.69036,"subtask_id":"release_1","tcp_end":[0.57099,0.21987,0.24995],"tcp_start":[0.5753,0.22175,0.22828],"tcp_to_object_dist_end":0.22828,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```