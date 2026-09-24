## Search State

- **Seed**: 4
- **Iteration**: 10 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 9 | approach → descend → grasp → lift → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | 6 | 0.5678 | 1.00 | ❌ rejected |
| 8 | approach → descend → grasp → lift → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | 6 | 0.5678 | 1.00 | ❌ rejected |
| 7 | approach → descend → grasp → lift → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | 6 | 0.5857 | 1.00 | ❌ rejected |
| 6 | approach → descend → grasp → lift → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | 6 | 0.5857 | 1.00 | ✅ accepted |
| 5 | approach → descend → grasp → lift → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | time_limit | 7 | 0.1881 | 0.37 | ❌ rejected |

**Proposal policy**: task_score is near-perfect (1.00). Preserve useful working parts and make only evidence-backed refinements. A HOLD is acceptable if you genuinely cannot find a better structure.

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
- Frozen realised-scene SHA-256: `1959b3932a54fd3d3850620783d44a63a35b8fa059f78d939fdbdef5fbfc64e8`
- Frozen object start: [0.5443056105572368, 0.0011327552814361583, 0.03]
- Frozen task target: [0.6476243705707704, 0.15808360238956023, 0.19110337479925443]
- Goal object position: (0.6476243705707704, 0.15808360238956023, 0.19110337479925443)
- place_goal_position (task success criterion — final object 3D position must be close to the realised airborne target here): (0.6476243705707704, 0.15808360238956023, 0.19110337479925443)
- Grasp/lift components are optimiser fitness diagnostics only; canonical task_score is final object-to-realised-target proximity.
- Object initial pose: (0.5443056105572368, 0.0011327552814361583, 0.03)
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
  frozen_object_start: [0.5443, 0.0011, 0.03]
  frozen_task_target: [0.6476, 0.1581, 0.1911]
  frozen_object_starts: {'grasp_target': [0.5443056105572368, 0.0011327552814361583, 0.03]}
  frozen_targets: {'place_target': [0.6476243705707704, 0.15808360238956023, 0.19110337479925443]}
  goal_tolerance_m: 0.02
  force_limit_n: 20
  force_scale_n: 5
  realized_scene_sha256: 1959b3932a54fd3d3850620783d44a63a35b8fa059f78d939fdbdef5fbfc64e8

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

## Current Skill (Q=0.568) — your mutation base

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
    offset_along_axis:
      distance: 0.1
      axis: world_z
      mode: add_to_offset
      sign: positive
    tolerance: 0.01
  parameters:
    speed:
      type: scalar
      range:
      - 0.01
      - 0.15
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: approach_1
- id: descend_1
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
    - 0.02
    tolerance: 0.005
  parameters:
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
  parameters:
    grasp_timeout:
      type: scalar
      range:
      - 0.5
      - 2.0
      default: 1.0
      binds_to:
      - path: duration.max_time
        mode: replace
  guards:
  - id: grasp_check
    when: after_phase
    predicate: bilateral_grasp
    threshold: 0.5
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: offset_target
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
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.15
      axis: world_z
      mode: add_to_offset
      sign: positive
    tolerance: 0.03
  parameters:
    speed:
      type: scalar
      range:
      - 0.01
      - 0.15
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: lift_check
    when: after_phase
    predicate: object_lifted
    threshold: 0.5
    on_failure: retry
  retries:
    max_attempts: 1
    strategy: offset_target
    offset:
    - 0.0
    - 0.0
    - 0.0
  subtask_id: transport_arc
- id: place_1
  type: descend
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.03
    tolerance: 0.01
  parameters:
    place_z_offset:
      type: scalar
      range:
      - 0.0
      - 0.06
      default: 0.03
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

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=world_z, distance=0.1, mode=add_to_offset, sign=positive}, tolerance=0.01
  - parameter_bindings:
    - speed: status=consumed; consumers=generator.speed (replace)
- **descend_1** (`descend`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.02], tolerance=0.005
  - parameter_bindings:
    - speed: status=consumed; consumers=generator.speed (replace)
- **grasp_1** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings:
    - grasp_timeout: status=consumed; consumers=duration.max_time (replace)
  - guards:
    - id=grasp_check, when=after_phase, predicate=bilateral_grasp, on_failure=retry, threshold=0.5
  - retries: max_attempts=2, strategy=offset_target, offset=[0.0, 0.0, 0.0]
- **lift_1** (`lift`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=world_z, distance=0.15, mode=add_to_offset, sign=positive}, tolerance=0.03
  - parameter_bindings:
    - speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=lift_check, when=after_phase, predicate=object_lifted, on_failure=retry, threshold=0.5
  - retries: max_attempts=1, strategy=offset_target, offset=[0.0, 0.0, 0.0]
- **place_1** (`descend`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.03], tolerance=0.01
  - parameter_bindings:
    - place_z_offset: status=consumed; consumers=target.offset.z (replace)
    - speed: status=consumed; consumers=generator.speed (replace)

## Design Metrics

- **Composite score**: 0.568
- **task_score** (E): 1.000
- **fitness_score**: 0.958  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.390

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1455 |
| descend_1 | 1.00 | 1.00 | 0.0988 |
| grasp_1 | 1.00 | 1.00 | 0.0133 |
| lift_1 | 1.00 | 1.00 | 0.0090 |
| place_1 | 1.00 | 1.00 | 0.0824 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.518, 0.004, 0.158) | (0.526, 0.005, 0.030)→(0.526, 0.005, 0.026) | 0.246→0.249 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.518, 0.004, 0.158)→(0.520, 0.005, 0.059) | (0.526, 0.005, 0.026)→(0.526, 0.005, 0.026) | 0.249→0.249 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_1 | grasp | 1.00 / step_budget | (0.520, 0.005, 0.059)→(0.512, 0.005, 0.049) | (0.526, 0.005, 0.026)→(0.526, 0.005, 0.026) | 0.249→0.249 | 1.00 / 40.333 | 0.147 | 0.184 |
| lift_1 | lift | 1.00 / step_budget | (0.601, 0.158, 0.298)→(0.603, 0.162, 0.306) | (0.526, 0.005, 0.026)→(0.616, 0.162, 0.270) | 0.249→0.089 | 1.00 / 21.667 | 0.146 | 0.366 |
| place_1 | descend | 1.00 / step_budget | (0.603, 0.162, 0.306)→(0.607, 0.170, 0.224) | (0.618, 0.166, 0.278)→(0.619, 0.173, 0.192) | 0.096→0.012 | 1.00 / 18.000 | 0.130 | 0.297 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.302
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 1.000
- phase_score: 0.280
- phase_breakdown.release_1_score: 0.000
- phase_breakdown.descend_1_score: 0.799
- phase_breakdown.transport_arc_score: 0.084
- phase_breakdown.grasp_1_score: 1.000
- phase_breakdown.approach_1_score: 0.078
- grasp_place_fitness: 0.959

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.959
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 1.000
- **Median Q (composite search score)**: 0.568
- **K-run variance**: 0.0000
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.317


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `104d9d5641b6f93313b49acc931f841aa27a6ce63eca9eff4a16c33838e2c9c3`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.05,0.05],"goal_z_delta":0.15,"object_xy_delta":[0.05,0.05]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `9de75aa839370ff688dada9a37e29517e2f368ed4f09f6a013379103594581cf`; realized-scene SHA-256: `1959b3932a54fd3d3850620783d44a63a35b8fa059f78d939fdbdef5fbfc64e8`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.54431,0.00113,0.03]},{"name":"goal","value":[0.64762,0.15808,0.1911]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.54431,0.00113,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.64762,0.15808,0.1911]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.44033,"average_solve_count":243.0,"average_success_count":243.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.14931,"descend_1.speed":0.08965,"grasp_1.grasp_timeout":1.85789,"lift_1.speed":0.0626,"place_1.place_z_offset":0.002,"place_1.speed":0.0436},"optimized_scores":{"best_composite_score":0.56851,"best_fitness_score":0.95851,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"right_finger","body_b":"grasp_target","contact_count":8262.0,"contact_point_centroid":[0.57843,0.08832,0.17052],"force_p95":0.12845,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.3618,"mean_force":0.06763,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.5784,0.06926,0.16996]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":9139.0,"contact_point_centroid":[0.58277,0.05152,0.17131],"force_p95":0.10701,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.34201,"mean_force":0.06349,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.57891,0.06994,0.17121]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1040.0,"contact_point_centroid":[0.64114,0.16947,0.28052],"force_p95":0.14159,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30894,"mean_force":0.09637,"phase_index":4.0,"phase_name":"place_1","phase_type":"descend","tcp_position_centroid":[0.64018,0.15033,0.28018]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1173.0,"contact_point_centroid":[0.64903,0.13358,0.28231],"force_p95":0.14736,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28622,"mean_force":0.08992,"phase_index":4.0,"phase_name":"place_1","phase_type":"descend","tcp_position_centroid":[0.64008,0.15019,0.28227]},{"body_a":"world","body_b":"grasp_target","contact_count":78.0,"contact_point_centroid":[0.54363,0.00154,-0.00153],"force_p95":0.25663,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.26858,"mean_force":0.19,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52888,0.00159,0.04942]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.54431,0.00112,-0.00204],"force_p95":0.13396,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.16146,"mean_force":0.12575,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53032,0.00084,0.04996]},{"body_a":"world","body_b":"grasp_target","contact_count":812.0,"contact_point_centroid":[0.54431,0.00113,-0.00184],"force_p95":0.13728,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12323,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51584,0.00042,0.23058]},{"body_a":"world","body_b":"grasp_target","contact_count":900.0,"contact_point_centroid":[0.54431,0.00113,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.53418,0.0009,0.10734]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4600.0,"contact_point_centroid":[0.52992,-0.01834,0.04918],"force_p95":0.07007,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10283,"mean_force":0.04702,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52909,0.00082,0.04849]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4640.0,"contact_point_centroid":[0.53056,0.01998,0.04962],"force_p95":0.07061,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08616,"mean_force":0.04677,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52909,0.00082,0.04849]}],"total_contact_groups":10},"final_pose_error":0.0391,"key_states":{"actual_goal_position":[0.64762,0.15808,0.1911],"final_object_position":[0.65645,0.15716,0.20188],"final_tcp_position":[0.64281,0.15374,0.23166],"realised_goal_position":[0.64762,0.15808,0.1911],"realised_object_initial_position":[0.54431,0.00113,0.03]},"peak_contact_force":0.3618,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":204.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.03],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.24751,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":812.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.53324,0.00086,0.15722],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.13167,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":225.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":900.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.53786,0.00099,0.05916],"tcp_start":[0.53324,0.00086,0.15722],"tcp_to_object_dist_end":0.03376,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":42.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54423,0.00093,0.02584],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.2504,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.13377,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11040.0,"raw_peak_contact_force":0.16146,"subtask_id":"grasp_1","tcp_end":[0.52906,0.00081,0.04845],"tcp_start":[0.53786,0.00099,0.05916],"tcp_to_object_dist_end":0.02722,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":26.0,"n_steps":515.0,"n_steps_budget":1000.0,"object_pos_end":[0.65173,0.14721,0.28046],"object_pos_start":[0.54423,0.00093,0.02584],"object_to_goal_dist_end":0.09011,"object_to_goal_dist_start":0.2504,"object_z_max":0.288,"peak_contact_force":0.13853,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":17479.0,"raw_peak_contact_force":0.3618,"subtask_id":"transport_arc","tcp_end":[0.63807,0.14738,0.31436],"tcp_start":[0.63559,0.14355,0.30626],"tcp_to_object_dist_end":0.03655,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":19.0,"n_steps":101.0,"n_steps_budget":1000.0,"object_pos_end":[0.65645,0.15716,0.20188],"object_pos_start":[0.65427,0.15113,0.28853],"object_to_goal_dist_end":0.01396,"object_to_goal_dist_start":0.0979,"object_z_max":0.2893,"peak_contact_force":0.13004,"phase_name":"place_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2213.0,"raw_peak_contact_force":0.30894,"tcp_end":[0.64281,0.15374,0.23166],"tcp_start":[0.63807,0.14738,0.31436],"tcp_to_object_dist_end":0.03293,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `349f925163f8e9284ad51ad55d38356f2e3c8deb4dc54e8ff12260e5f6d4b0f8`; realized-scene SHA-256: `e32d7866764afb23ec7c7faebb4bcca0aa39fbf2f1ab61f3c9c527b297153af9`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.5305,0.03079,0.03]},{"name":"goal","value":[0.60153,0.17858,0.10809]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.5305,0.03079,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.60153,0.17858,0.10809]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.10623,"average_solve_count":273.0,"average_success_count":273.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.07975,"descend_1.speed":0.08878,"grasp_1.grasp_timeout":1.39806,"lift_1.speed":0.09201,"place_1.place_z_offset":0.00168,"place_1.speed":0.0136},"optimized_scores":{"best_composite_score":0.56769,"best_fitness_score":0.95769,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"right_finger","body_b":"grasp_target","contact_count":5627.0,"contact_point_centroid":[0.54747,0.10862,0.12903],"force_p95":0.13561,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.36251,"mean_force":0.07119,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.54811,0.08951,0.12865]},{"body_a":"world","body_b":"grasp_target","contact_count":78.0,"contact_point_centroid":[0.53062,0.03071,-0.00158],"force_p95":0.29995,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.31485,"mean_force":0.22678,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51575,0.03022,0.05034]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6833.0,"contact_point_centroid":[0.5558,0.07843,0.13778],"force_p95":0.12444,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30407,"mean_force":0.0638,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.55224,0.09667,0.13844]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":929.0,"contact_point_centroid":[0.59299,0.18677,0.20021],"force_p95":0.14705,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25707,"mean_force":0.11972,"phase_index":4.0,"phase_name":"place_1","phase_type":"descend","tcp_position_centroid":[0.59232,0.16773,0.20117]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1304.0,"contact_point_centroid":[0.60063,0.15132,0.199],"force_p95":0.14355,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22301,"mean_force":0.09267,"phase_index":4.0,"phase_name":"place_1","phase_type":"descend","tcp_position_centroid":[0.59233,0.16773,0.20132]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53058,0.03074,-0.00215],"force_p95":0.16458,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.21739,"mean_force":0.1337,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51701,0.02898,0.05044]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4338.0,"contact_point_centroid":[0.51679,0.00979,0.04882],"force_p95":0.08304,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16491,"mean_force":0.04955,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.5158,0.0289,0.04904]},{"body_a":"world","body_b":"grasp_target","contact_count":844.0,"contact_point_centroid":[0.5305,0.03079,-0.00185],"force_p95":0.13728,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12321,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51002,0.01166,0.23135]},{"body_a":"world","body_b":"grasp_target","contact_count":912.0,"contact_point_centroid":[0.5305,0.03079,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.52183,0.02693,0.10781]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4753.0,"contact_point_centroid":[0.51648,0.0481,0.05017],"force_p95":0.07364,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07927,"mean_force":0.04614,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.5158,0.0289,0.04904]}],"total_contact_groups":10},"final_pose_error":0.03974,"key_states":{"actual_goal_position":[0.60153,0.17858,0.10809],"final_object_position":[0.60608,0.17662,0.11653],"final_tcp_position":[0.59551,0.17276,0.14862],"realised_goal_position":[0.60153,0.17858,0.10809],"realised_object_initial_position":[0.5305,0.03079,0.03]},"peak_contact_force":0.36251,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":212.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.03],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18162,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":844.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.52178,0.02456,0.15773],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.13215,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":228.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":912.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.52444,0.02943,0.05928],"tcp_start":[0.52178,0.02456,0.15773],"tcp_to_object_dist_end":0.03383,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53055,0.02971,0.02546],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18446,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.16224,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10891.0,"raw_peak_contact_force":0.21739,"subtask_id":"grasp_1","tcp_end":[0.51577,0.0289,0.049],"tcp_start":[0.52444,0.02943,0.05928],"tcp_to_object_dist_end":0.02781,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":20.0,"n_steps":373.0,"n_steps_budget":1000.0,"object_pos_end":[0.60371,0.1642,0.19814],"object_pos_start":[0.53055,0.02971,0.02546],"object_to_goal_dist_end":0.09122,"object_to_goal_dist_start":0.18446,"object_z_max":0.20433,"peak_contact_force":0.15548,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":12538.0,"raw_peak_contact_force":0.36251,"subtask_id":"transport_arc","tcp_end":[0.59093,0.16444,0.23241],"tcp_start":[0.58916,0.16016,0.22557],"tcp_to_object_dist_end":0.03658,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":17.0,"n_steps":123.0,"n_steps_budget":1000.0,"object_pos_end":[0.60608,0.17662,0.11653],"object_pos_start":[0.60546,0.16851,0.20483],"object_to_goal_dist_end":0.00979,"object_to_goal_dist_start":0.09734,"object_z_max":0.20561,"peak_contact_force":0.14298,"phase_name":"place_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2233.0,"raw_peak_contact_force":0.25707,"tcp_end":[0.59551,0.17276,0.14862],"tcp_start":[0.59093,0.16444,0.23241],"tcp_to_object_dist_end":0.03401,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `a1798e4fdcacfe8740623adfe3f78d2bc74e0d14c8233e64f02c40cf2a534ecc`; realized-scene SHA-256: `584133b5261cffac0dd4282704ff39e97bf4d452e60b02507679bbdea5a4de22`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50382,-0.01567,0.03]},{"name":"goal","value":[0.58691,0.18745,0.24812]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.50382,-0.01567,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.58691,0.18745,0.24812]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.76168,"average_solve_count":214.0,"average_success_count":214.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.12499,"descend_1.speed":0.06738,"grasp_1.grasp_timeout":0.87308,"lift_1.speed":0.08288,"place_1.place_z_offset":0.00421,"place_1.speed":0.08824},"optimized_scores":{"best_composite_score":0.56722,"best_fitness_score":0.95722,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"right_finger","body_b":"grasp_target","contact_count":7478.0,"contact_point_centroid":[0.52837,0.08811,0.18861],"force_p95":0.13742,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.37427,"mean_force":0.0803,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52858,0.06935,0.19016]},{"body_a":"world","body_b":"grasp_target","contact_count":68.0,"contact_point_centroid":[0.50245,-0.01401,-0.0016],"force_p95":0.3141,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.36563,"mean_force":0.22868,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48987,-0.01417,0.05141]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":740.0,"contact_point_centroid":[0.58297,0.19805,0.3336],"force_p95":0.16957,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32564,"mean_force":0.11942,"phase_index":4.0,"phase_name":"place_1","phase_type":"descend","tcp_position_centroid":[0.5821,0.17894,0.33442]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8457.0,"contact_point_centroid":[0.534,0.0542,0.19411],"force_p95":0.1346,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29837,"mean_force":0.07499,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.53001,0.07235,0.19518]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":792.0,"contact_point_centroid":[0.59214,0.16312,0.33328],"force_p95":0.1596,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23583,"mean_force":0.11288,"phase_index":4.0,"phase_name":"place_1","phase_type":"descend","tcp_position_centroid":[0.58204,0.17882,0.33588]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50386,-0.01567,-0.00207],"force_p95":0.14395,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.17332,"mean_force":0.12847,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49151,-0.01506,0.05164]},{"body_a":"world","body_b":"grasp_target","contact_count":780.0,"contact_point_centroid":[0.50382,-0.01567,-0.00183],"force_p95":0.13759,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12325,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49996,-0.00593,0.23179]},{"body_a":"world","body_b":"grasp_target","contact_count":952.0,"contact_point_centroid":[0.50382,-0.01567,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49834,-0.01377,0.10882]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4128.0,"contact_point_centroid":[0.49192,0.00394,0.04967],"force_p95":0.08154,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11847,"mean_force":0.05374,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49033,-0.01505,0.05035]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4192.0,"contact_point_centroid":[0.49168,-0.0341,0.05045],"force_p95":0.08372,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0844,"mean_force":0.05312,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49033,-0.01505,0.05035]}],"total_contact_groups":10},"final_pose_error":0.03988,"key_states":{"actual_goal_position":[0.58691,0.18745,0.24812],"final_object_position":[0.59315,0.18637,0.25869],"final_tcp_position":[0.58378,0.18252,0.29178],"realised_goal_position":[0.58691,0.18745,0.24812],"realised_object_initial_position":[0.50382,-0.01567,0.03]},"peak_contact_force":0.37427,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":196.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.03],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.30942,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":780.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.50046,-0.01247,0.15924],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.1333,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":238.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":952.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.49878,-0.0151,0.05975],"tcp_start":[0.50046,-0.01247,0.15924],"tcp_to_object_dist_end":0.03411,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":38.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.5038,-0.01538,0.02561],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31234,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.14565,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10120.0,"raw_peak_contact_force":0.17332,"subtask_id":"grasp_1","tcp_end":[0.4903,-0.01505,0.05032],"tcp_start":[0.49878,-0.0151,0.05975],"tcp_to_object_dist_end":0.02815,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":19.0,"n_steps":575.0,"n_steps_budget":1000.0,"object_pos_end":[0.59149,0.17473,0.33255],"object_pos_start":[0.5038,-0.01538,0.02561],"object_to_goal_dist_end":0.0855,"object_to_goal_dist_start":0.31234,"object_z_max":0.34022,"peak_contact_force":0.14501,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":16003.0,"raw_peak_contact_force":0.37427,"subtask_id":"transport_arc","tcp_end":[0.58022,0.17511,0.37101],"tcp_start":[0.57853,0.17094,0.36282],"tcp_to_object_dist_end":0.04009,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":18.0,"n_steps":92.0,"n_steps_budget":1000.0,"object_pos_end":[0.59315,0.18637,0.25869],"object_pos_start":[0.59325,0.17915,0.34077],"object_to_goal_dist_end":0.01233,"object_to_goal_dist_start":0.09324,"object_z_max":0.34151,"peak_contact_force":0.11669,"phase_name":"place_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1532.0,"raw_peak_contact_force":0.32564,"tcp_end":[0.58378,0.18252,0.29178],"tcp_start":[0.58022,0.17511,0.37101],"tcp_to_object_dist_end":0.03461,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```