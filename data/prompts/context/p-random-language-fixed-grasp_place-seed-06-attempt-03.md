## Search State

- **Seed**: 6
- **Iteration**: 4 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 3 | approach → descend → grasp → lift → approach → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | time_limit | 8 | 0.2021 | 0.49 | ✅ accepted |
| 2 | approach → descend → grasp → lift → approach → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | time_limit | 8 | -0.1415 | 0.25 | ✅ accepted |
| 1 | align → lift → push → approach → approach → descend → grasp → rotate | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | arc_cartesian | linear_cartesian | — | impedance_motion | position_control | position_control | impedance_control | force_threshold_switch | position_control | admittance_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 6 | -0.1417 | 0.25 | ❌ rejected |
| 0 | align → lift → push → approach → approach → descend → grasp → rotate | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | arc_cartesian | linear_cartesian | — | impedance_motion | position_control | position_control | impedance_control | force_threshold_switch | position_control | admittance_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 6 | -0.1416 | 0.25 | ❌ rejected |

**Proposal policy**: task_score is 0.49 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.202) — your mutation base

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

- **Composite score**: 0.202
- **task_score** (E): 0.490
- **fitness_score**: 0.722  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.520

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_to_object | 1.00 | 1.00 | 0.2652 |
| descend_to_grasp | 1.00 | 1.00 | 0.0047 |
| grasp_object | 1.00 | 1.00 | 0.0124 |
| lift_object | 1.00 | 1.00 | 0.1514 |
| transport_to_goal | 1.00 | 0.67 | 0.1914 |
| release_at_goal | 1.00 | 0.67 | 0.0108 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_to_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.495, 0.023, 0.038) | (0.500, 0.024, 0.030)→(0.500, 0.024, 0.026) | 0.269→0.271 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_to_grasp | descend | 1.00 / step_budget | (0.495, 0.023, 0.038)→(0.494, 0.023, 0.034) | (0.500, 0.024, 0.026)→(0.500, 0.024, 0.026) | 0.271→0.271 | 1.00 / 4.000 | 27.129 | 0.123 |
| grasp_object | grasp | 1.00 / step_budget | (0.494, 0.023, 0.034)→(0.485, 0.023, 0.025) | (0.500, 0.024, 0.026)→(0.500, 0.023, 0.025) | 0.271→0.273 | 1.00 / 42.000 | 0.176 | 0.251 |
| lift_object | lift | 1.00 / step_budget | (0.485, 0.023, 0.025)→(0.482, 0.022, 0.176) | (0.500, 0.023, 0.025)→(0.496, 0.023, 0.163) | 0.273→0.211 | 1.00 / 26.000 | 0.106 | 0.781 |
| transport_to_goal | approach | 1.00 / step_budget | (0.482, 0.022, 0.176)→(0.583, 0.175, 0.212) | (0.496, 0.023, 0.163)→(0.587, 0.175, 0.173) | 0.211→0.045 | 0.67 / 25.667 | 0.023 | 0.379 |
| release_at_goal | release | 1.00 / step_budget | (0.583, 0.175, 0.212)→(0.579, 0.175, 0.216) | (0.587, 0.175, 0.173)→(0.589, 0.174, 0.091) | 0.045→0.124 | 0.67 / 13.333 | 0.080 | 0.531 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.778
- phase_score: 0.629
- phase_breakdown.transport_arc_score: 0.526
- phase_breakdown.release_1_score: 0.512
- phase_breakdown.approach_1_score: 0.821
- phase_breakdown.grasp_1_score: 1.000
- phase_breakdown.descend_1_score: 0.713
- grasp_place_fitness: 0.867

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.867
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.778
- **Median Q (composite search score)**: 0.182
- **K-run variance**: 0.0124
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.266


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.87719,"average_solve_count":114.0,"average_success_count":114.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_to_object.speed":0.07151,"descend_to_grasp.speed":0.05652,"grasp_object.max_time":0.57204,"lift_object.lift_height":0.22086,"lift_object.speed":0.05752,"release_at_goal.max_time":0.83027,"transport_to_goal.arc_height":0.1783,"transport_to_goal.speed":0.17431},"optimized_scores":{"best_composite_score":0.07698,"best_fitness_score":0.59698,"best_task_score":0.24004},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":151.0,"contact_point_centroid":[0.50005,-0.01476,-0.00125],"force_p95":0.48387,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.73659,"mean_force":0.11269,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.48756,-0.01495,0.02627]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":10265.0,"contact_point_centroid":[0.52477,0.03898,0.24028],"force_p95":0.13583,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.48509,"mean_force":0.08965,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.51897,0.05665,0.24235]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":9647.0,"contact_point_centroid":[0.5203,0.07339,0.24119],"force_p95":0.15173,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.36152,"mean_force":0.0929,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.51802,0.0548,0.24255]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":14214.0,"contact_point_centroid":[0.48802,-0.03387,0.11186],"force_p95":0.10634,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.3223,"mean_force":0.07088,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.48521,-0.01492,0.11008]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":15996.0,"contact_point_centroid":[0.48874,0.00373,0.10601],"force_p95":0.10148,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31404,"mean_force":0.06441,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.4852,-0.01492,0.10491]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50383,-0.01566,-0.00205],"force_p95":0.14101,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.1841,"mean_force":0.12715,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.49049,-0.01497,0.02607]},{"body_a":"world","body_b":"grasp_target","contact_count":3024.0,"contact_point_centroid":[0.50382,-0.01567,-0.00195],"force_p95":0.12817,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12279,"phase_index":0.0,"phase_name":"approach_to_object","phase_type":"approach","tcp_position_centroid":[0.49833,-0.00736,0.16842]},{"body_a":"world","body_b":"grasp_target","contact_count":92.0,"contact_point_centroid":[0.50382,-0.01567,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.49794,-0.01491,0.0364]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5293.0,"contact_point_centroid":[0.49024,0.00408,0.02688],"force_p95":0.06399,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10187,"mean_force":0.04106,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.48924,-0.01496,0.02478]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4185.0,"contact_point_centroid":[0.48899,-0.03426,0.02757],"force_p95":0.07754,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08855,"mean_force":0.05192,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.48924,-0.01496,0.02478]}],"total_contact_groups":10},"final_pose_error":0.02875,"key_states":{"actual_goal_position":[0.58691,0.18745,0.24812],"final_object_position":[0.59465,0.16004,0.03598],"final_tcp_position":[0.57237,0.16281,0.25097],"realised_goal_position":[0.58691,0.18745,0.24812],"realised_object_initial_position":[0.50382,-0.01567,0.03]},"peak_contact_force":81.14225,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":757.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.03],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.30942,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_to_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3024.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.49879,-0.01484,0.03849],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.01347,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":23.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":81.14225,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":92.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.49784,-0.01501,0.03382],"tcp_start":[0.49879,-0.01484,0.03849],"tcp_to_object_dist_end":0.00985,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50367,-0.01534,0.0258],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31221,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.14039,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11278.0,"raw_peak_contact_force":0.1841,"subtask_id":"grasp_1","tcp_end":[0.48921,-0.01496,0.02475],"tcp_start":[0.49784,-0.01501,0.03382],"tcp_to_object_dist_end":0.0145,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":27.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49902,-0.01529,0.19296],"object_pos_start":[0.50367,-0.01534,0.0258],"object_to_goal_dist_end":0.22775,"object_to_goal_dist_start":0.31221,"object_z_max":0.19278,"peak_contact_force":0.10632,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":30361.0,"raw_peak_contact_force":0.73659,"tcp_end":[0.48581,-0.01492,0.20795],"tcp_start":[0.48921,-0.01496,0.02475],"tcp_to_object_dist_end":0.01998,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.58344,0.15783,0.17869],"object_pos_start":[0.49902,-0.01529,0.19296],"object_to_goal_dist_end":0.07556,"object_to_goal_dist_start":0.22775,"object_z_max":0.23762,"peak_contact_force":0.0,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":19912.0,"raw_peak_contact_force":0.48509,"subtask_id":"transport_arc","tcp_end":[0.57237,0.16281,0.25097],"tcp_start":[0.48581,-0.01492,0.20795],"tcp_to_object_dist_end":0.0733,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.59465,0.16004,0.03598],"object_pos_start":[0.58344,0.15783,0.17869],"object_to_goal_dist_end":0.21404,"object_to_goal_dist_start":0.07556,"object_z_max":0.17869,"peak_contact_force":0.0,"phase_name":"release_at_goal","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"release_1","tcp_end":[0.5703,0.16256,0.24611],"tcp_start":[0.57237,0.16281,0.25097],"tcp_to_object_dist_end":0.21156,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.71795,"average_solve_count":117.0,"average_success_count":117.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_to_object.speed":0.05493,"descend_to_grasp.speed":0.04835,"grasp_object.max_time":0.49052,"lift_object.lift_height":0.14824,"lift_object.speed":0.05744,"release_at_goal.max_time":0.63457,"transport_to_goal.arc_height":0.13081,"transport_to_goal.speed":0.1772},"optimized_scores":{"best_composite_score":0.18226,"best_fitness_score":0.70226,"best_task_score":0.4528},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":150.0,"contact_point_centroid":[0.60279,0.15774,-0.00818],"force_p95":1.1112,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.1702,"mean_force":0.46964,"phase_index":5.0,"phase_name":"release_at_goal","phase_type":"release","tcp_position_centroid":[0.60664,0.15893,0.1592]},{"body_a":"world","body_b":"grasp_target","contact_count":175.0,"contact_point_centroid":[0.50876,0.03591,-0.00147],"force_p95":0.45973,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.76651,"mean_force":0.11605,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.4956,0.03691,0.02584]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":9637.0,"contact_point_centroid":[0.49626,0.05591,0.08573],"force_p95":0.11132,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.3969,"mean_force":0.07705,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.49333,0.03674,0.08317]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":13643.0,"contact_point_centroid":[0.49646,0.01826,0.08397],"force_p95":0.09742,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30787,"mean_force":0.05766,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.49331,0.03674,0.08313]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":17401.0,"contact_point_centroid":[0.56274,0.08629,0.17087],"force_p95":0.09305,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30291,"mean_force":0.05956,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.55756,0.10447,0.17089]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.51271,0.03949,-0.00226],"force_p95":0.19523,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.27982,"mean_force":0.14201,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.49876,0.03717,0.02531]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":14256.0,"contact_point_centroid":[0.55486,0.12091,0.17312],"force_p95":0.09798,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27961,"mean_force":0.07009,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.55504,0.10191,0.17066]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1274.0,"contact_point_centroid":[0.60812,0.17905,0.15004],"force_p95":0.06893,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25662,"mean_force":0.04168,"phase_index":5.0,"phase_name":"release_at_goal","phase_type":"release","tcp_position_centroid":[0.61091,0.16018,0.14624]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1349.0,"contact_point_centroid":[0.61597,0.1415,0.14689],"force_p95":0.06687,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24087,"mean_force":0.04012,"phase_index":5.0,"phase_name":"release_at_goal","phase_type":"release","tcp_position_centroid":[0.61089,0.16017,0.14621]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5176.0,"contact_point_centroid":[0.49911,0.01827,0.0259],"force_p95":0.06586,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20981,"mean_force":0.04089,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.4975,0.03707,0.02397]},{"body_a":"world","body_b":"grasp_target","contact_count":3264.0,"contact_point_centroid":[0.51251,0.03972,-0.00195],"force_p95":0.12702,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12278,"phase_index":0.0,"phase_name":"approach_to_object","phase_type":"approach","tcp_position_centroid":[0.50237,0.01856,0.16781]},{"body_a":"world","body_b":"grasp_target","contact_count":92.0,"contact_point_centroid":[0.51251,0.03972,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.50619,0.03748,0.03582]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3963.0,"contact_point_centroid":[0.49886,0.05657,0.02677],"force_p95":0.09471,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10698,"mean_force":0.05899,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.49751,0.03707,0.02399]}],"total_contact_groups":13},"final_pose_error":0.01967,"key_states":{"actual_goal_position":[0.62757,0.17252,0.14502],"final_object_position":[0.60706,0.15847,0.02881],"final_tcp_position":[0.61276,0.16047,0.14978],"realised_goal_position":[0.62757,0.17252,0.14502],"realised_object_initial_position":[0.51251,0.03972,0.03]},"peak_contact_force":1.1702,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":817.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.03],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21001,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_to_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3264.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.50698,0.03736,0.03785],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.01327,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":23.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":92.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.50615,0.03771,0.03329],"tcp_start":[0.50698,0.03736,0.03785],"tcp_to_object_dist_end":0.00987,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":42.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51264,0.03776,0.02513],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21388,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.18716,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10939.0,"raw_peak_contact_force":0.27982,"subtask_id":"grasp_1","tcp_end":[0.49747,0.03707,0.02394],"tcp_start":[0.50615,0.03771,0.03329],"tcp_to_object_dist_end":0.01524,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":26.0,"n_steps":744.0,"n_steps_budget":810.0,"object_pos_end":[0.50898,0.03776,0.14708],"object_pos_start":[0.51264,0.03776,0.02513],"object_to_goal_dist_end":0.17952,"object_to_goal_dist_start":0.21388,"object_z_max":0.14695,"peak_contact_force":0.10536,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":23455.0,"raw_peak_contact_force":0.76651,"tcp_end":[0.49371,0.03677,0.15912],"tcp_start":[0.49747,0.03707,0.02394],"tcp_to_object_dist_end":0.01947,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.61148,0.16162,0.12811],"object_pos_start":[0.50898,0.03776,0.14708],"object_to_goal_dist_end":0.02576,"object_to_goal_dist_start":0.17952,"object_z_max":0.16455,"peak_contact_force":0.06986,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":31657.0,"raw_peak_contact_force":0.30291,"subtask_id":"transport_arc","tcp_end":[0.61276,0.16047,0.14978],"tcp_start":[0.49371,0.03677,0.15912],"tcp_to_object_dist_end":0.02174,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.60706,0.15847,0.02881],"object_pos_start":[0.61148,0.16162,0.12811],"object_to_goal_dist_end":0.11884,"object_to_goal_dist_start":0.02576,"object_z_max":0.12811,"peak_contact_force":0.16341,"phase_name":"release_at_goal","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2773.0,"raw_peak_contact_force":1.1702,"subtask_id":"release_1","tcp_end":[0.60654,0.1589,0.17028],"tcp_start":[0.61276,0.16047,0.14978],"tcp_to_object_dist_end":0.14147,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.69725,"average_solve_count":109.0,"average_success_count":109.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_to_object.speed":0.0675,"descend_to_grasp.speed":0.06041,"grasp_object.max_time":0.37357,"lift_object.lift_height":0.14794,"lift_object.speed":0.05556,"release_at_goal.max_time":0.59713,"transport_to_goal.arc_height":0.13281,"transport_to_goal.speed":0.12357},"optimized_scores":{"best_composite_score":0.3472,"best_fitness_score":0.8672,"best_task_score":0.77757},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":162.0,"contact_point_centroid":[0.47916,0.04381,-0.00151],"force_p95":0.44913,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.84061,"mean_force":0.11169,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.46753,0.04533,0.02766]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":846.0,"contact_point_centroid":[0.55992,0.22206,0.23612],"force_p95":0.08106,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.42293,"mean_force":0.06088,"phase_index":5.0,"phase_name":"release_at_goal","phase_type":"release","tcp_position_centroid":[0.5621,0.20293,0.23227]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":15463.0,"contact_point_centroid":[0.5171,0.10161,0.22008],"force_p95":0.09651,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.34821,"mean_force":0.06538,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.50983,0.11907,0.22026]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":10405.0,"contact_point_centroid":[0.46737,0.06433,0.08775],"force_p95":0.10909,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.34153,"mean_force":0.07399,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.46521,0.04512,0.08532]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":12374.0,"contact_point_centroid":[0.50845,0.1352,0.22112],"force_p95":0.11079,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32812,"mean_force":0.08021,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.50792,0.11607,0.2193]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":14294.0,"contact_point_centroid":[0.46848,0.0266,0.08699],"force_p95":0.0974,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29494,"mean_force":0.05578,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.4652,0.04512,0.08611]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.48291,0.04842,-0.00232],"force_p95":0.20935,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.28858,"mean_force":0.14589,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.47051,0.04563,0.0268]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1050.0,"contact_point_centroid":[0.56961,0.1854,0.23249],"force_p95":0.07624,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25539,"mean_force":0.04947,"phase_index":5.0,"phase_name":"release_at_goal","phase_type":"release","tcp_position_centroid":[0.56211,0.20293,0.23229]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4919.0,"contact_point_centroid":[0.47127,0.0266,0.02689],"force_p95":0.07836,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21051,"mean_force":0.04328,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.4693,0.04551,0.02558]},{"body_a":"world","body_b":"grasp_target","contact_count":3136.0,"contact_point_centroid":[0.4827,0.04873,-0.00195],"force_p95":0.12742,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12278,"phase_index":0.0,"phase_name":"approach_to_object","phase_type":"approach","tcp_position_centroid":[0.48838,0.02272,0.16838]},{"body_a":"world","body_b":"grasp_target","contact_count":92.0,"contact_point_centroid":[0.4827,0.04873,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.4779,0.04596,0.03661]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4136.0,"contact_point_centroid":[0.46965,0.06502,0.02807],"force_p95":0.09512,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09879,"mean_force":0.0548,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.46931,0.04551,0.0256]}],"total_contact_groups":12},"final_pose_error":0.03209,"key_states":{"actual_goal_position":[0.58187,0.22885,0.23048],"final_object_position":[0.5648,0.20487,0.20688],"final_tcp_position":[0.56346,0.20301,0.23526],"realised_goal_position":[0.58187,0.22885,0.23048],"realised_object_initial_position":[0.4827,0.04873,0.03]},"peak_contact_force":0.84061,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":785.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.03],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28719,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_to_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3136.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.47879,0.04581,0.03858],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.01348,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":23.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":92.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.47769,0.04626,0.03407],"tcp_start":[0.47879,0.04581,0.03858],"tcp_to_object_dist_end":0.00979,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.48278,0.04624,0.02494],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.29226,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.19974,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10855.0,"raw_peak_contact_force":0.28858,"subtask_id":"grasp_1","tcp_end":[0.46927,0.04551,0.02556],"tcp_start":[0.47769,0.04626,0.03407],"tcp_to_object_dist_end":0.01355,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":25.0,"n_steps":766.0,"n_steps_budget":840.0,"object_pos_end":[0.4798,0.04635,0.14753],"object_pos_start":[0.48278,0.04624,0.02494],"object_to_goal_dist_end":0.22496,"object_to_goal_dist_start":0.29226,"object_z_max":0.14741,"peak_contact_force":0.10781,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":24861.0,"raw_peak_contact_force":0.84061,"tcp_end":[0.46558,0.04516,0.16114],"tcp_start":[0.46927,0.04551,0.02556],"tcp_to_object_dist_end":0.01972,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":34.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.56717,0.20553,0.21201],"object_pos_start":[0.4798,0.04635,0.14753],"object_to_goal_dist_end":0.03319,"object_to_goal_dist_start":0.22496,"object_z_max":0.22287,"peak_contact_force":0.0,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":27837.0,"raw_peak_contact_force":0.34821,"subtask_id":"transport_arc","tcp_end":[0.56346,0.20301,0.23526],"tcp_start":[0.46558,0.04516,0.16114],"tcp_to_object_dist_end":0.02369,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":38.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.5648,0.20487,0.20688],"object_pos_start":[0.56717,0.20553,0.21201],"object_to_goal_dist_end":0.03774,"object_to_goal_dist_start":0.03319,"object_z_max":0.21201,"peak_contact_force":0.07751,"phase_name":"release_at_goal","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1896.0,"raw_peak_contact_force":0.42293,"subtask_id":"release_1","tcp_end":[0.56124,0.20249,0.23023],"tcp_start":[0.56346,0.20301,0.23526],"tcp_to_object_dist_end":0.02374,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```