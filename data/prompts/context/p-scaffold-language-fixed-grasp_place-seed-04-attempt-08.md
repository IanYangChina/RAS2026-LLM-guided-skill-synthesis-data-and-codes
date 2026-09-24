## Search State

- **Seed**: 4
- **Iteration**: 9 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 8 | approach → descend → grasp → lift → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | 6 | 0.5678 | 1.00 | ❌ rejected |
| 7 | approach → descend → grasp → lift → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | 6 | 0.5857 | 1.00 | ❌ rejected |
| 6 | approach → descend → grasp → lift → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | 6 | 0.5857 | 1.00 | ✅ accepted |
| 5 | approach → descend → grasp → lift → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | time_limit | 7 | 0.1881 | 0.37 | ❌ rejected |
| 4 | approach → descend → grasp → lift → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | 6 | 0.5857 | 1.00 | ✅ accepted |

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
| descend_1 | 1.00 | 1.00 | 0.0987 |
| grasp_1 | 1.00 | 1.00 | 0.0133 |
| lift_1 | 1.00 | 1.00 | 0.0046 |
| place_1 | 1.00 | 1.00 | 0.0832 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.518, 0.004, 0.158) | (0.526, 0.005, 0.030)→(0.526, 0.005, 0.026) | 0.246→0.249 | 1.00 / 4.000 | 27.129 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.518, 0.004, 0.158)→(0.520, 0.005, 0.059) | (0.526, 0.005, 0.026)→(0.526, 0.005, 0.026) | 0.249→0.249 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_1 | grasp | 1.00 / step_budget | (0.520, 0.005, 0.059)→(0.512, 0.005, 0.049) | (0.526, 0.005, 0.026)→(0.526, 0.005, 0.026) | 0.249→0.249 | 1.00 / 40.333 | 0.147 | 0.184 |
| lift_1 | lift | 1.00 / step_budget | (0.601, 0.158, 0.298)→(0.602, 0.161, 0.302) | (0.526, 0.005, 0.026)→(0.616, 0.162, 0.270) | 0.249→0.089 | 1.00 / 21.667 | 0.189 | 0.378 |
| place_1 | descend | 1.00 / step_budget | (0.602, 0.161, 0.302)→(0.607, 0.170, 0.219) | (0.617, 0.165, 0.274)→(0.616, 0.173, 0.187) | 0.092→0.009 | 1.00 / 18.333 | 0.128 | 0.336 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.706
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 1.000
- phase_score: 0.284
- phase_breakdown.release_1_score: 0.000
- phase_breakdown.descend_1_score: 0.799
- phase_breakdown.transport_arc_score: 0.091
- phase_breakdown.grasp_1_score: 1.000
- phase_breakdown.approach_1_score: 0.077
- grasp_place_fitness: 0.958

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.958
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 1.000
- **Median Q (composite search score)**: 0.568
- **K-run variance**: 0.0000
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.367


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.32721,"average_solve_count":272.0,"average_success_count":272.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.01018,"descend_1.speed":0.08357,"grasp_1.grasp_timeout":1.91895,"lift_1.speed":0.09608,"place_1.place_z_offset":0.00055,"place_1.speed":0.08798},"optimized_scores":{"best_composite_score":0.56845,"best_fitness_score":0.95845,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"right_finger","body_b":"grasp_target","contact_count":7808.0,"contact_point_centroid":[0.57773,0.08722,0.16827],"force_p95":0.13047,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.35779,"mean_force":0.06866,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.5775,0.06816,0.16786]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1057.0,"contact_point_centroid":[0.64067,0.16876,0.27018],"force_p95":0.17264,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.34682,"mean_force":0.11325,"phase_index":4.0,"phase_name":"place_1","phase_type":"descend","tcp_position_centroid":[0.63944,0.14974,0.27041]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1249.0,"contact_point_centroid":[0.64819,0.13318,0.26924],"force_p95":0.17561,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.34174,"mean_force":0.10607,"phase_index":4.0,"phase_name":"place_1","phase_type":"descend","tcp_position_centroid":[0.63945,0.14976,0.26999]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8646.0,"contact_point_centroid":[0.58215,0.05067,0.16952],"force_p95":0.11106,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33872,"mean_force":0.06461,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.57816,0.06903,0.16945]},{"body_a":"world","body_b":"grasp_target","contact_count":71.0,"contact_point_centroid":[0.54386,0.00186,-0.00149],"force_p95":0.27643,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.29198,"mean_force":0.20117,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.5288,0.00171,0.04953]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.54431,0.00112,-0.00204],"force_p95":0.13395,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.16147,"mean_force":0.12574,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53018,0.00084,0.0499]},{"body_a":"world","body_b":"grasp_target","contact_count":908.0,"contact_point_centroid":[0.54431,0.00113,-0.00186],"force_p95":0.13709,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12317,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51467,0.0004,0.23314]},{"body_a":"world","body_b":"grasp_target","contact_count":912.0,"contact_point_centroid":[0.54431,0.00113,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.53392,0.0009,0.10745]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4600.0,"contact_point_centroid":[0.52982,-0.01834,0.04913],"force_p95":0.07008,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10282,"mean_force":0.04702,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52894,0.00081,0.04844]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4640.0,"contact_point_centroid":[0.53047,0.01998,0.04957],"force_p95":0.07061,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08618,"mean_force":0.04677,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52895,0.00081,0.04844]}],"total_contact_groups":10},"final_pose_error":0.02924,"key_states":{"actual_goal_position":[0.64762,0.15808,0.1911],"final_object_position":[0.65298,0.15675,0.18904],"final_tcp_position":[0.64238,0.15389,0.2201],"realised_goal_position":[0.64762,0.15808,0.1911],"realised_object_initial_position":[0.54431,0.00113,0.03]},"peak_contact_force":0.35779,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":228.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.03],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.24751,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":908.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.53283,0.00086,0.15741],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.13189,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":228.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.12262,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":912.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.5377,0.00099,0.0591],"tcp_start":[0.53283,0.00086,0.15741],"tcp_to_object_dist_end":0.03373,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":42.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54423,0.00093,0.02584],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.2504,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.13376,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11040.0,"raw_peak_contact_force":0.16147,"subtask_id":"grasp_1","tcp_end":[0.52891,0.00081,0.0484],"tcp_start":[0.5377,0.00099,0.0591],"tcp_to_object_dist_end":0.02726,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":26.0,"n_steps":495.0,"n_steps_budget":1000.0,"object_pos_end":[0.6516,0.14712,0.28021],"object_pos_start":[0.54423,0.00093,0.02584],"object_to_goal_dist_end":0.08986,"object_to_goal_dist_start":0.2504,"object_z_max":0.28314,"peak_contact_force":0.18626,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":16525.0,"raw_peak_contact_force":0.35779,"subtask_id":"transport_arc","tcp_end":[0.63707,0.14616,0.30968],"tcp_start":[0.63568,0.14364,0.3064],"tcp_to_object_dist_end":0.03287,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":19.0,"n_steps":123.0,"n_steps_budget":1000.0,"object_pos_end":[0.65298,0.15675,0.18904],"object_pos_start":[0.65351,0.14986,0.28347],"object_to_goal_dist_end":0.00589,"object_to_goal_dist_start":0.09292,"object_z_max":0.28377,"peak_contact_force":0.13046,"phase_name":"place_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2306.0,"raw_peak_contact_force":0.34682,"tcp_end":[0.64238,0.15389,0.2201],"tcp_start":[0.63707,0.14616,0.30968],"tcp_to_object_dist_end":0.03295,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.59296,"average_solve_count":199.0,"average_success_count":199.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.09861,"descend_1.speed":0.07253,"grasp_1.grasp_timeout":1.76193,"lift_1.speed":0.0884,"place_1.place_z_offset":0.02005,"place_1.speed":0.04483},"optimized_scores":{"best_composite_score":0.5677,"best_fitness_score":0.9577,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"right_finger","body_b":"grasp_target","contact_count":5704.0,"contact_point_centroid":[0.54746,0.10872,0.12923],"force_p95":0.13177,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.362,"mean_force":0.06978,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.54819,0.08963,0.1288]},{"body_a":"world","body_b":"grasp_target","contact_count":78.0,"contact_point_centroid":[0.53062,0.0307,-0.0016],"force_p95":0.29048,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.30585,"mean_force":0.22383,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51576,0.03018,0.0503]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6824.0,"contact_point_centroid":[0.55557,0.07807,0.13736],"force_p95":0.11868,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30106,"mean_force":0.0627,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.55207,0.09634,0.13798]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":808.0,"contact_point_centroid":[0.593,0.18655,0.19717],"force_p95":0.16483,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29693,"mean_force":0.12427,"phase_index":4.0,"phase_name":"place_1","phase_type":"descend","tcp_position_centroid":[0.59229,0.16747,0.19794]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1122.0,"contact_point_centroid":[0.60085,0.15119,0.19532],"force_p95":0.16638,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27928,"mean_force":0.09909,"phase_index":4.0,"phase_name":"place_1","phase_type":"descend","tcp_position_centroid":[0.59231,0.16752,0.19748]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53058,0.03074,-0.00215],"force_p95":0.16439,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.21727,"mean_force":0.13364,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51703,0.02898,0.05045]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4337.0,"contact_point_centroid":[0.51681,0.00979,0.04883],"force_p95":0.08304,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16485,"mean_force":0.04956,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51582,0.0289,0.04904]},{"body_a":"world","body_b":"grasp_target","contact_count":832.0,"contact_point_centroid":[0.5305,0.03079,-0.00184],"force_p95":0.13728,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12321,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51019,0.01172,0.23098]},{"body_a":"world","body_b":"grasp_target","contact_count":920.0,"contact_point_centroid":[0.5305,0.03079,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.52191,0.02695,0.10766]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4752.0,"contact_point_centroid":[0.51649,0.0481,0.05018],"force_p95":0.07367,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07926,"mean_force":0.04614,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51583,0.0289,0.04905]}],"total_contact_groups":10},"final_pose_error":0.02986,"key_states":{"actual_goal_position":[0.60153,0.17858,0.10809],"final_object_position":[0.60569,0.17632,0.12471],"final_tcp_position":[0.59512,0.17257,0.15668],"realised_goal_position":[0.60153,0.17858,0.10809],"realised_object_initial_position":[0.5305,0.03079,0.03]},"peak_contact_force":0.362,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":209.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.03],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18162,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":832.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.52193,0.02461,0.1575],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.1319,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":230.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":920.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.52446,0.02944,0.05929],"tcp_start":[0.52193,0.02461,0.1575],"tcp_to_object_dist_end":0.03384,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53055,0.02972,0.02546],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18446,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.16208,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10889.0,"raw_peak_contact_force":0.21727,"subtask_id":"grasp_1","tcp_end":[0.51579,0.0289,0.04901],"tcp_start":[0.52446,0.02944,0.05929],"tcp_to_object_dist_end":0.0278,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":20.0,"n_steps":369.0,"n_steps_budget":1000.0,"object_pos_end":[0.60379,0.16422,0.19825],"object_pos_start":[0.53055,0.02972,0.02546],"object_to_goal_dist_end":0.09133,"object_to_goal_dist_start":0.18446,"object_z_max":0.20098,"peak_contact_force":0.19272,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":12606.0,"raw_peak_contact_force":0.362,"subtask_id":"transport_arc","tcp_end":[0.59024,0.16325,0.22864],"tcp_start":[0.58912,0.1601,0.2255],"tcp_to_object_dist_end":0.03328,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":17.0,"n_steps":109.0,"n_steps_budget":1000.0,"object_pos_end":[0.60569,0.17632,0.12471],"object_pos_start":[0.60552,0.16757,0.20129],"object_to_goal_dist_end":0.01728,"object_to_goal_dist_start":0.09393,"object_z_max":0.2016,"peak_contact_force":0.1393,"phase_name":"place_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1930.0,"raw_peak_contact_force":0.29693,"tcp_end":[0.59512,0.17257,0.15668],"tcp_start":[0.59024,0.16325,0.22864],"tcp_to_object_dist_end":0.03388,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.45972,"average_solve_count":211.0,"average_success_count":211.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.11362,"descend_1.speed":0.06122,"grasp_1.grasp_timeout":0.98716,"lift_1.speed":0.13035,"place_1.place_z_offset":0.00303,"place_1.speed":0.04247},"optimized_scores":{"best_composite_score":0.56719,"best_fitness_score":0.95719,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":65.0,"contact_point_centroid":[0.50208,-0.01357,-0.00155],"force_p95":0.39938,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.41538,"mean_force":0.25153,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.4898,-0.01395,0.05155]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":7026.0,"contact_point_centroid":[0.52863,0.08841,0.1889],"force_p95":0.14153,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.37406,"mean_force":0.08308,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52873,0.06967,0.19062]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1054.0,"contact_point_centroid":[0.58193,0.19732,0.32433],"force_p95":0.14075,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.36343,"mean_force":0.11258,"phase_index":4.0,"phase_name":"place_1","phase_type":"descend","tcp_position_centroid":[0.58116,0.17815,0.32538]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8039.0,"contact_point_centroid":[0.53411,0.05412,0.1938],"force_p95":0.1389,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29828,"mean_force":0.07687,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52996,0.07224,0.19493]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1165.0,"contact_point_centroid":[0.59149,0.16244,0.32264],"force_p95":0.13434,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29772,"mean_force":0.10338,"phase_index":4.0,"phase_name":"place_1","phase_type":"descend","tcp_position_centroid":[0.58117,0.17816,0.32529]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50386,-0.01567,-0.00207],"force_p95":0.14388,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.1733,"mean_force":0.12846,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.4915,-0.01506,0.05166]},{"body_a":"world","body_b":"grasp_target","contact_count":788.0,"contact_point_centroid":[0.50382,-0.01567,-0.00184],"force_p95":0.13748,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12325,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49991,-0.00593,0.23187]},{"body_a":"world","body_b":"grasp_target","contact_count":960.0,"contact_point_centroid":[0.50382,-0.01567,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49834,-0.01378,0.1088]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4127.0,"contact_point_centroid":[0.49191,0.00393,0.04969],"force_p95":0.08155,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11844,"mean_force":0.0537,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49031,-0.01505,0.05037]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4190.0,"contact_point_centroid":[0.49167,-0.0341,0.05046],"force_p95":0.08372,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08439,"mean_force":0.05311,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49032,-0.01505,0.05037]}],"total_contact_groups":10},"final_pose_error":0.0297,"key_states":{"actual_goal_position":[0.58691,0.18745,0.24812],"final_object_position":[0.58965,0.18582,0.2461],"final_tcp_position":[0.58313,0.18268,0.28022],"realised_goal_position":[0.58691,0.18745,0.24812],"realised_object_initial_position":[0.50382,-0.01567,0.03]},"peak_contact_force":81.14226,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":198.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.03],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.30942,"object_z_max":0.03,"peak_contact_force":81.14226,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":788.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.5005,-0.01248,0.1591],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.13316,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":240.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":960.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.49877,-0.0151,0.05977],"tcp_start":[0.5005,-0.01248,0.1591],"tcp_to_object_dist_end":0.03413,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":38.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.5038,-0.01538,0.02561],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31233,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.14554,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10117.0,"raw_peak_contact_force":0.1733,"subtask_id":"grasp_1","tcp_end":[0.49028,-0.01505,0.05034],"tcp_start":[0.49877,-0.0151,0.05977],"tcp_to_object_dist_end":0.02817,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":19.0,"n_steps":556.0,"n_steps_budget":1000.0,"object_pos_end":[0.59139,0.17465,0.33235],"object_pos_start":[0.5038,-0.01538,0.02561],"object_to_goal_dist_end":0.08532,"object_to_goal_dist_start":0.31233,"object_z_max":0.33574,"peak_contact_force":0.18835,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":15130.0,"raw_peak_contact_force":0.41538,"subtask_id":"transport_arc","tcp_end":[0.57948,0.1738,0.36649],"tcp_start":[0.57856,0.17093,0.36279],"tcp_to_object_dist_end":0.03617,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":19.0,"n_steps":128.0,"n_steps_budget":1000.0,"object_pos_end":[0.58965,0.18582,0.2461],"object_pos_start":[0.59308,0.17792,0.33611],"object_to_goal_dist_end":0.00378,"object_to_goal_dist_start":0.08873,"object_z_max":0.33646,"peak_contact_force":0.11435,"phase_name":"place_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2219.0,"raw_peak_contact_force":0.36343,"tcp_end":[0.58313,0.18268,0.28022],"tcp_start":[0.57948,0.1738,0.36649],"tcp_to_object_dist_end":0.03488,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```