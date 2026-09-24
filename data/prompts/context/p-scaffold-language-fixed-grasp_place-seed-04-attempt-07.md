## Search State

- **Seed**: 4
- **Iteration**: 8 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 7 | approach → descend → grasp → lift → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | 6 | 0.5857 | 1.00 | ❌ rejected |
| 6 | approach → descend → grasp → lift → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | 6 | 0.5857 | 1.00 | ✅ accepted |
| 5 | approach → descend → grasp → lift → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | time_limit | 7 | 0.1881 | 0.37 | ❌ rejected |
| 4 | approach → descend → grasp → lift → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | 6 | 0.5857 | 1.00 | ✅ accepted |
| 3 | approach → descend → grasp → lift → descend → release | linear_cartesian | linear_cartesian | — | arc_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | time_limit | 7 | 0.1941 | 0.38 | ✅ accepted |

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

## Current Skill (Q=0.586) — your mutation base

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

- **Composite score**: 0.586
- **task_score** (E): 1.000
- **fitness_score**: 0.976  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.390

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1664 |
| descend_1 | 1.00 | 1.00 | 0.0952 |
| grasp_1 | 1.00 | 1.00 | 0.0128 |
| lift_1 | 1.00 | 1.00 | 0.0028 |
| place_1 | 1.00 | 1.00 | 0.1111 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.520, 0.005, 0.137) | (0.526, 0.005, 0.030)→(0.526, 0.005, 0.026) | 0.246→0.249 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.520, 0.005, 0.137)→(0.521, 0.005, 0.042) | (0.526, 0.005, 0.026)→(0.526, 0.005, 0.026) | 0.249→0.249 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_1 | grasp | 1.00 / step_budget | (0.521, 0.005, 0.042)→(0.512, 0.005, 0.033) | (0.526, 0.005, 0.026)→(0.526, 0.005, 0.026) | 0.249→0.249 | 1.00 / 42.667 | 0.136 | 0.163 |
| lift_1 | lift | 1.00 / step_budget | (0.604, 0.164, 0.306)→(0.605, 0.165, 0.308) | (0.526, 0.005, 0.026)→(0.619, 0.168, 0.297) | 0.249→0.115 | 1.00 / 36.000 | 0.108 | 0.476 |
| place_1 | descend | 1.00 / step_budget | (0.605, 0.165, 0.308)→(0.608, 0.172, 0.197) | (0.620, 0.170, 0.299)→(0.620, 0.176, 0.182) | 0.117→0.008 | 1.00 / 31.667 | 55983.941 | 0.190 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.521
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 1.000
- phase_score: 0.283
- phase_breakdown.release_1_score: 0.000
- phase_breakdown.descend_1_score: 0.825
- phase_breakdown.transport_arc_score: 0.081
- phase_breakdown.grasp_1_score: 1.000
- phase_breakdown.approach_1_score: 0.118
- grasp_place_fitness: 0.976

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.976
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 1.000
- **Median Q (composite search score)**: 0.586
- **K-run variance**: 0.0000
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.293


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.72727,"average_solve_count":209.0,"average_success_count":209.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.07445,"descend_1.speed":0.08939,"grasp_1.grasp_timeout":1.58455,"lift_1.speed":0.09638,"place_1.place_z_offset":0.00081,"place_1.speed":0.06375},"optimized_scores":{"best_composite_score":0.58586,"best_fitness_score":0.97586,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":76.0,"contact_point_centroid":[0.54344,0.00228,-0.00141],"force_p95":0.41521,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.46102,"mean_force":0.24879,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.53003,0.00175,0.03319]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":14827.0,"contact_point_centroid":[0.58604,0.05665,0.17421],"force_p95":0.0803,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25217,"mean_force":0.05365,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.5832,0.07548,0.17259]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":13203.0,"contact_point_centroid":[0.58209,0.09487,0.17651],"force_p95":0.0835,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22771,"mean_force":0.05763,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.58351,0.07587,0.17337]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5084.0,"contact_point_centroid":[0.64656,0.13457,0.26228],"force_p95":0.09031,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1917,"mean_force":0.06394,"phase_index":4.0,"phase_name":"place_1","phase_type":"descend","tcp_position_centroid":[0.64058,0.15262,0.26169]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4893.0,"contact_point_centroid":[0.63836,0.17143,0.26335],"force_p95":0.09221,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18865,"mean_force":0.06485,"phase_index":4.0,"phase_name":"place_1","phase_type":"descend","tcp_position_centroid":[0.64061,0.15267,0.2607]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.5443,0.00115,-0.00203],"force_p95":0.1312,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.15262,"mean_force":0.1253,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53155,0.00088,0.03352]},{"body_a":"world","body_b":"grasp_target","contact_count":2252.0,"contact_point_centroid":[0.54431,0.00113,-0.00194],"force_p95":0.13153,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12284,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51705,0.00047,0.21778]},{"body_a":"world","body_b":"grasp_target","contact_count":3908.0,"contact_point_centroid":[0.54431,0.00113,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.53651,0.00098,0.07907]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4149.0,"contact_point_centroid":[0.53131,0.02015,0.03442],"force_p95":0.07656,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09651,"mean_force":0.05218,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53026,0.00085,0.03201]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5327.0,"contact_point_centroid":[0.53065,-0.01819,0.0345],"force_p95":0.06263,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08696,"mean_force":0.04072,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53026,0.00085,0.03201]}],"total_contact_groups":10},"final_pose_error":0.00994,"key_states":{"actual_goal_position":[0.64762,0.15808,0.1911],"final_object_position":[0.65516,0.15957,0.18539],"final_tcp_position":[0.64313,0.15608,0.20056],"realised_goal_position":[0.64762,0.15808,0.1911],"realised_object_initial_position":[0.54431,0.00113,0.03]},"peak_contact_force":0.46102,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":564.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.03],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.24751,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2252.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.53689,0.00098,0.13648],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.11071,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":977.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3908.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.53886,0.00102,0.04209],"tcp_start":[0.53689,0.00098,0.13648],"tcp_to_object_dist_end":0.01697,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54418,0.00111,0.02587],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25029,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.13092,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11276.0,"raw_peak_contact_force":0.15262,"subtask_id":"grasp_1","tcp_end":[0.53023,0.00085,0.03198],"tcp_start":[0.53886,0.00102,0.04209],"tcp_to_object_dist_end":0.01523,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":34.0,"n_steps":739.0,"n_steps_budget":1000.0,"object_pos_end":[0.65428,0.15227,0.30605],"object_pos_start":[0.54418,0.00111,0.02587],"object_to_goal_dist_end":0.11528,"object_to_goal_dist_start":0.25029,"object_z_max":0.30728,"peak_contact_force":0.11354,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":28106.0,"raw_peak_contact_force":0.46102,"subtask_id":"transport_arc","tcp_end":[0.63981,0.15006,0.31628],"tcp_start":[0.63902,0.14844,0.31444],"tcp_to_object_dist_end":0.01786,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":30.0,"n_steps":316.0,"n_steps_budget":1000.0,"object_pos_end":[0.65516,0.15957,0.18539],"object_pos_start":[0.65499,0.15386,0.30752],"object_to_goal_dist_end":0.00957,"object_to_goal_dist_start":0.11672,"object_z_max":0.30768,"peak_contact_force":0.09168,"phase_name":"place_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":9977.0,"raw_peak_contact_force":0.1917,"tcp_end":[0.64313,0.15608,0.20056],"tcp_start":[0.63981,0.15006,0.31628],"tcp_to_object_dist_end":0.01967,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.77564,"average_solve_count":156.0,"average_success_count":156.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.08783,"descend_1.speed":0.08636,"grasp_1.grasp_timeout":1.31763,"lift_1.speed":0.12877,"place_1.place_z_offset":0.00913,"place_1.speed":0.09471},"optimized_scores":{"best_composite_score":0.58561,"best_fitness_score":0.97561,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":77.0,"contact_point_centroid":[0.52954,0.0313,-0.00143],"force_p95":0.41407,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.50579,"mean_force":0.28226,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51655,0.03106,0.03398]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":11141.0,"contact_point_centroid":[0.5571,0.08119,0.13483],"force_p95":0.08556,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27389,"mean_force":0.05306,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.55374,0.09996,0.13355]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":9477.0,"contact_point_centroid":[0.55172,0.11852,0.13643],"force_p95":0.08535,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23432,"mean_force":0.05846,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.55353,0.09956,0.13298]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53053,0.0308,-0.00208],"force_p95":0.14768,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.19336,"mean_force":0.12919,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51796,0.02991,0.03403]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4727.0,"contact_point_centroid":[0.59085,0.19046,0.18539],"force_p95":0.10888,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17421,"mean_force":0.06836,"phase_index":4.0,"phase_name":"place_1","phase_type":"descend","tcp_position_centroid":[0.59341,0.17161,0.18256]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5835.0,"contact_point_centroid":[0.59943,0.15392,0.18193],"force_p95":0.09099,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15784,"mean_force":0.05608,"phase_index":4.0,"phase_name":"place_1","phase_type":"descend","tcp_position_centroid":[0.59342,0.17165,0.18169]},{"body_a":"world","body_b":"grasp_target","contact_count":2168.0,"contact_point_centroid":[0.5305,0.03079,-0.00193],"force_p95":0.13205,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12285,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51075,0.0138,0.2183]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5287.0,"contact_point_centroid":[0.51771,0.01079,0.03444],"force_p95":0.06899,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13844,"mean_force":0.0411,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51669,0.02983,0.03259]},{"body_a":"world","body_b":"grasp_target","contact_count":3864.0,"contact_point_centroid":[0.5305,0.03079,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.52327,0.02941,0.07841]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4191.0,"contact_point_centroid":[0.51709,0.04913,0.03536],"force_p95":0.08293,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08566,"mean_force":0.05187,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51669,0.02983,0.0326]}],"total_contact_groups":10},"final_pose_error":0.00975,"key_states":{"actual_goal_position":[0.60153,0.17858,0.10809],"final_object_position":[0.60885,0.18024,0.11028],"final_tcp_position":[0.59618,0.17601,0.12495],"realised_goal_position":[0.60153,0.17858,0.10809],"realised_object_initial_position":[0.5305,0.03079,0.03]},"peak_contact_force":167951.73011,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":543.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.03],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18162,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2168.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.52414,0.02817,0.13721],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.1114,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":966.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3864.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.52516,0.03038,0.04226],"tcp_start":[0.52414,0.02817,0.13721],"tcp_to_object_dist_end":0.0171,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53043,0.03033,0.02569],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18391,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.14665,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11278.0,"raw_peak_contact_force":0.19336,"subtask_id":"grasp_1","tcp_end":[0.51666,0.02982,0.03256],"tcp_start":[0.52516,0.03038,0.04226],"tcp_to_object_dist_end":0.0154,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":539.0,"n_steps_budget":1000.0,"object_pos_end":[0.60711,0.1703,0.22408],"object_pos_start":[0.53043,0.03033,0.02569],"object_to_goal_dist_end":0.11642,"object_to_goal_dist_start":0.18391,"object_z_max":0.22539,"peak_contact_force":0.10952,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":20695.0,"raw_peak_contact_force":0.50579,"subtask_id":"transport_arc","tcp_end":[0.59289,0.1683,0.23469],"tcp_start":[0.59231,0.16629,0.23282],"tcp_to_object_dist_end":0.01786,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":33.0,"n_steps":308.0,"n_steps_budget":1000.0,"object_pos_end":[0.60885,0.18024,0.11028],"object_pos_start":[0.60774,0.1724,0.22561],"object_to_goal_dist_end":0.00782,"object_to_goal_dist_start":0.11785,"object_z_max":0.22577,"peak_contact_force":167951.73011,"phase_name":"place_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":10562.0,"raw_peak_contact_force":0.17421,"tcp_end":[0.59618,0.17601,0.12495],"tcp_start":[0.59289,0.1683,0.23469],"tcp_to_object_dist_end":0.01985,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.67323,"average_solve_count":254.0,"average_success_count":254.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.08039,"descend_1.speed":0.063,"grasp_1.grasp_timeout":1.11261,"lift_1.speed":0.01951,"place_1.place_z_offset":0.00915,"place_1.speed":0.06242},"optimized_scores":{"best_composite_score":0.58569,"best_fitness_score":0.97569,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":72.0,"contact_point_centroid":[0.50157,-0.01493,-0.00143],"force_p95":0.43336,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.46144,"mean_force":0.26031,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48989,-0.01473,0.03456]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":15722.0,"contact_point_centroid":[0.53819,0.0651,0.20876],"force_p95":0.08021,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26147,"mean_force":0.05638,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.53522,0.08395,0.20675]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":16484.0,"contact_point_centroid":[0.53145,0.09908,0.2028],"force_p95":0.07803,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24106,"mean_force":0.05333,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.53341,0.08024,0.20014]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5275.0,"contact_point_centroid":[0.57793,0.19974,0.32474],"force_p95":0.08834,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20412,"mean_force":0.05963,"phase_index":4.0,"phase_name":"place_1","phase_type":"descend","tcp_position_centroid":[0.58174,0.18126,0.32237]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5215.0,"contact_point_centroid":[0.58836,0.16347,0.32201],"force_p95":0.09003,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17434,"mean_force":0.06139,"phase_index":4.0,"phase_name":"place_1","phase_type":"descend","tcp_position_centroid":[0.58177,0.18136,0.3209]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.5038,-0.01578,-0.00202],"force_p95":0.13085,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.14422,"mean_force":0.12483,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49164,-0.01554,0.03488]},{"body_a":"world","body_b":"grasp_target","contact_count":2008.0,"contact_point_centroid":[0.50382,-0.01567,-0.00193],"force_p95":0.13256,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12287,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49869,-0.00698,0.2196]},{"body_a":"world","body_b":"grasp_target","contact_count":3824.0,"contact_point_centroid":[0.50382,-0.01567,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49766,-0.01512,0.07638]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4141.0,"contact_point_centroid":[0.48973,-0.03478,0.03606],"force_p95":0.07918,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09654,"mean_force":0.05173,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.4904,-0.01553,0.03356]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5099.0,"contact_point_centroid":[0.49143,0.00352,0.03526],"force_p95":0.06839,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08896,"mean_force":0.04296,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.4904,-0.01553,0.03356]}],"total_contact_groups":10},"final_pose_error":0.00997,"key_states":{"actual_goal_position":[0.58691,0.18745,0.24812],"final_object_position":[0.59463,0.1893,0.24975],"final_tcp_position":[0.58347,0.18524,0.26636],"realised_goal_position":[0.58691,0.18745,0.24812],"realised_object_initial_position":[0.50382,-0.01567,0.03]},"peak_contact_force":0.46144,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":503.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.03],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.30942,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2008.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.49951,-0.01433,0.13866],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.11273,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":956.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3824.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.49866,-0.0156,0.04239],"tcp_start":[0.49951,-0.01433,0.13866],"tcp_to_object_dist_end":0.01717,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":42.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50368,-0.01588,0.0259],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31249,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.13111,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11040.0,"raw_peak_contact_force":0.14422,"subtask_id":"grasp_1","tcp_end":[0.49037,-0.01553,0.03353],"tcp_start":[0.49866,-0.0156,0.04239],"tcp_to_object_dist_end":0.01535,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":844.0,"n_steps_budget":1000.0,"object_pos_end":[0.59582,0.18084,0.36146],"object_pos_start":[0.50368,-0.01588,0.0259],"object_to_goal_dist_end":0.11388,"object_to_goal_dist_start":0.31249,"object_z_max":0.36305,"peak_contact_force":0.10022,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":32278.0,"raw_peak_contact_force":0.46144,"subtask_id":"transport_arc","tcp_end":[0.58123,0.17814,0.37341],"tcp_start":[0.58066,0.17625,0.37117],"tcp_to_object_dist_end":0.01905,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":32.0,"n_steps":308.0,"n_steps_budget":1000.0,"object_pos_end":[0.59463,0.1893,0.24975],"object_pos_start":[0.59634,0.18265,0.36332],"object_to_goal_dist_end":0.0081,"object_to_goal_dist_start":0.11569,"object_z_max":0.36351,"peak_contact_force":0.0,"phase_name":"place_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":10490.0,"raw_peak_contact_force":0.20412,"tcp_end":[0.58347,0.18524,0.26636],"tcp_start":[0.58123,0.17814,0.37341],"tcp_to_object_dist_end":0.02042,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```