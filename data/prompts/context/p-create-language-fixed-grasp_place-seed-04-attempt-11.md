## Search State

- **Seed**: 4
- **Iteration**: 12 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 11 | approach → descend → grasp → lift → approach → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | time_limit | 3 | 0.3424 | 0.27 | ❌ rejected |
| 10 | approach → descend → grasp → approach → release | linear_cartesian | linear_cartesian | — | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | time_limit | 1 | 0.3400 | 0.34 | ✅ accepted |
| 9 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 6 | 0.1835 | 0.32 | ❌ rejected |
| 8 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 6 | 0.1862 | 0.32 | ❌ rejected |
| 7 | approach → descend → grasp → lift → approach → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | time_limit | 6 | 0.2135 | 0.31 | ❌ rejected |

**Proposal policy**: task_score is 0.27 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.342) — your mutation base

```yaml
skill: grasp_place
dsl_version: 2
skill_type: arm_gripper
subtasks:
- id: approach_1
  anchor: object
- id: descend_1
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.02
- id: grasp_1
  anchor: object
  metric: contact
  offset:
  - 0.0
  - 0.0
  - 0.02
- id: transport_arc
- id: release_1
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
    offset_along_axis:
      distance: 0.05
      axis: world_z
      mode: add_to_offset
      sign: positive
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    approach_height:
      type: scalar
      range:
      - 0.05
      - 0.3
      default: 0.05
      binds_to:
      - path: target.offset_along_axis.distance
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
    entity: grasp_target
    offset:
    - 0.0
    - 0.0
    - 0.02
    tolerance: 0.005
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
- id: transport_arc
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
    tolerance: 0.02
    orientation:
      mode: keep_current
  subtask_id: transport_arc
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
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=world_z, distance=0.05, mode=add_to_offset, sign=positive}, tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_height: status=consumed; consumers=target.offset_along_axis.distance (replace)
- **descend_1** (`descend`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.02], tolerance=0.005
  - orientation: mode=keep_current
  - parameter_bindings: none
- **grasp_1** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings: none
- **transport_arc** (`approach`)
  - target: source=yaml, anchor=task_goal, entity=placement_surface, offset=[0.0, 0.0, 0.0], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings: none
- **release_1** (`release`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings: none

## Design Metrics

- **Composite score**: 0.342
- **task_score** (E): 0.273
- **fitness_score**: 0.612  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.270

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1704 |
| descend_1 | 1.00 | 1.00 | 0.0908 |
| grasp_1 | 1.00 | 1.00 | 0.0123 |
| lift_1 | 1.00 | 1.00 | 0.0951 |
| transport_arc | 1.00 | 1.00 | 0.1956 |
| release_1 | 1.00 | 1.00 | 0.0208 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.519, 0.004, 0.133) | (0.526, 0.005, 0.030)→(0.526, 0.005, 0.026) | 0.246→0.249 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.519, 0.004, 0.133)→(0.521, 0.005, 0.043) | (0.526, 0.005, 0.026)→(0.526, 0.005, 0.026) | 0.249→0.249 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_1 | grasp | 1.00 / step_budget | (0.521, 0.005, 0.043)→(0.513, 0.005, 0.033) | (0.526, 0.005, 0.026)→(0.526, 0.005, 0.026) | 0.249→0.249 | 1.00 / 41.667 | 0.135 | 0.175 |
| lift_1 | lift | 1.00 / step_budget | (0.513, 0.005, 0.033)→(0.509, 0.005, 0.128) | (0.526, 0.005, 0.026)→(0.524, 0.005, 0.113) | 0.249→0.209 | 1.00 / 23.667 | 524.403 | 0.613 |
| transport_arc | approach | 1.00 / step_budget | (0.509, 0.005, 0.128)→(0.601, 0.160, 0.188) | (0.524, 0.005, 0.113)→(0.549, 0.057, 0.016) | 0.209→0.214 | 1.00 / 8.333 | 91005.105 | 1.792 |
| release_1 | release | 1.00 / step_budget | (0.601, 0.160, 0.188)→(0.595, 0.159, 0.208) | (0.549, 0.057, 0.016)→(0.549, 0.057, 0.016) | 0.214→0.214 | 1.00 / 4.000 | 0.123 | 0.123 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: 1.000
- terminal_score: 0.460
- phase_score: 0.676
- phase_breakdown.descend_1_score: 0.839
- phase_breakdown.transport_arc_score: 0.674
- phase_breakdown.grasp_1_score: 1.000
- phase_breakdown.approach_1_score: 0.045
- phase_breakdown.release_1_score: 0.462
- grasp_place_fitness: 0.705

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.705
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.460
- **Median Q (composite search score)**: 0.319
- **K-run variance**: 0.0047
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 10.0
- **Final σ (mean)**: 0.234


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.89922,"average_solve_count":129.0,"average_success_count":129.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.06713,"lift_1.lift_height":0.10591,"transport_arc.arc_height":0.18668},"optimized_scores":{"best_composite_score":0.31906,"best_fitness_score":0.58906,"best_task_score":0.22556},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":1462.0,"contact_point_centroid":[0.57041,0.04287,-0.00266],"force_p95":0.32255,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.74132,"mean_force":0.15484,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.59377,0.09168,0.20569]},{"body_a":"world","body_b":"grasp_target","contact_count":146.0,"contact_point_centroid":[0.54158,0.00076,-0.00112],"force_p95":0.41948,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.64402,"mean_force":0.08713,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52896,0.00085,0.03382]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":9449.0,"contact_point_centroid":[0.52877,-0.01806,0.07513],"force_p95":0.10264,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33461,"mean_force":0.06538,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52625,0.00081,0.07356]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":9595.0,"contact_point_centroid":[0.52869,0.01971,0.07413],"force_p95":0.10259,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31272,"mean_force":0.06457,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52629,0.00081,0.07236]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2442.0,"contact_point_centroid":[0.53826,-0.00587,0.15093],"force_p95":0.15334,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26602,"mean_force":0.09184,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.53244,0.01234,0.15163]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1980.0,"contact_point_centroid":[0.53744,0.02987,0.14989],"force_p95":0.18691,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26369,"mean_force":0.10707,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.5317,0.01129,0.14976]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.5443,0.00101,-0.00203],"force_p95":0.13161,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.15449,"mean_force":0.12529,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53188,0.00091,0.03362]},{"body_a":"world","body_b":"grasp_target","contact_count":1456.0,"contact_point_centroid":[0.54431,0.00113,-0.00191],"force_p95":0.13511,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12296,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51663,0.00046,0.20856]},{"body_a":"world","body_b":"grasp_target","contact_count":3508.0,"contact_point_centroid":[0.54431,0.00113,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.53599,0.00097,0.06981]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.57032,0.04291,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.62997,0.14313,0.19233]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4116.0,"contact_point_centroid":[0.53137,-0.01832,0.03489],"force_p95":0.0761,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11664,"mean_force":0.05176,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53063,0.00089,0.03217]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4878.0,"contact_point_centroid":[0.53135,0.01996,0.03401],"force_p95":0.06811,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09481,"mean_force":0.04474,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53063,0.00089,0.03217]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1316.0,"contact_point_centroid":[0.6002,0.09925,0.20911],"force_p95":0.01208,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01641,"mean_force":0.01061,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.59969,0.09924,0.20693]},{"body_a":"left_finger","body_b":"right_finger","contact_count":225.0,"contact_point_centroid":[0.63295,0.14401,0.19147],"force_p95":0.0109,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01091,"mean_force":0.00991,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.63246,0.144,0.18893]}],"total_contact_groups":14},"final_pose_error":0.01972,"key_states":{"actual_goal_position":[0.64762,0.15808,0.1911],"final_object_position":[0.57032,0.04291,0.01602],"final_tcp_position":[0.6342,0.14374,0.19284],"realised_goal_position":[0.64762,0.15808,0.1911],"realised_object_initial_position":[0.54431,0.00113,0.03]},"peak_contact_force":1573.09317,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":365.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.03],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.24751,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1456.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.53558,0.00094,0.11506],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.08947,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":877.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3508.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.53895,0.00103,0.04192],"tcp_start":[0.53558,0.00094,0.11506],"tcp_to_object_dist_end":0.01678,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54418,0.00075,0.02588],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.2505,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.12979,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10794.0,"raw_peak_contact_force":0.15449,"subtask_id":"grasp_1","tcp_end":[0.5306,0.00088,0.03213],"tcp_start":[0.53895,0.00103,0.04192],"tcp_to_object_dist_end":0.01495,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":603.0,"n_steps_budget":690.0,"object_pos_end":[0.54165,0.00078,0.11127],"object_pos_start":[0.54418,0.00075,0.02588],"object_to_goal_dist_end":0.20578,"object_to_goal_dist_start":0.2505,"object_z_max":0.11116,"peak_contact_force":1573.09317,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":19190.0,"raw_peak_contact_force":0.64402,"tcp_end":[0.52635,0.00082,0.12559],"tcp_start":[0.5306,0.00088,0.03213],"tcp_to_object_dist_end":0.02096,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":671.0,"n_steps_budget":1000.0,"object_pos_end":[0.57032,0.04291,0.01602],"object_pos_start":[0.54165,0.00078,0.11127],"object_to_goal_dist_end":0.22337,"object_to_goal_dist_start":0.20578,"object_z_max":0.15617,"peak_contact_force":0.12263,"phase_name":"transport_arc","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":7200.0,"raw_peak_contact_force":1.74132,"subtask_id":"transport_arc","tcp_end":[0.6342,0.14374,0.19284],"tcp_start":[0.52635,0.00082,0.12559],"tcp_to_object_dist_end":0.21334,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.57032,0.04291,0.01602],"object_pos_start":[0.57032,0.04291,0.01602],"object_to_goal_dist_end":0.22337,"object_to_goal_dist_start":0.22337,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1025.0,"raw_peak_contact_force":0.12263,"subtask_id":"release_1","tcp_end":[0.62851,0.14266,0.21166],"tcp_start":[0.6342,0.14374,0.19284],"tcp_to_object_dist_end":0.22718,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.89744,"average_solve_count":117.0,"average_success_count":117.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.1374,"lift_1.lift_height":0.10469,"transport_arc.arc_height":0.14638},"optimized_scores":{"best_composite_score":0.43542,"best_fitness_score":0.70542,"best_task_score":0.45967},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":875.0,"contact_point_centroid":[0.56399,0.1172,-0.00312],"force_p95":0.6083,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.67616,"mean_force":0.17887,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.57184,0.13353,0.1476]},{"body_a":"world","body_b":"grasp_target","contact_count":143.0,"contact_point_centroid":[0.52745,0.02911,-0.00117],"force_p95":0.43474,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.62941,"mean_force":0.08313,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51557,0.02968,0.03539]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":9270.0,"contact_point_centroid":[0.5155,0.04838,0.07443],"force_p95":0.10265,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31857,"mean_force":0.06409,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.513,0.02952,0.07278]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8773.0,"contact_point_centroid":[0.51539,0.01061,0.07675],"force_p95":0.10453,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31687,"mean_force":0.06683,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51296,0.02952,0.07478]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1776.0,"contact_point_centroid":[0.52665,0.02888,0.14122],"force_p95":0.19577,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31629,"mean_force":0.10513,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.52118,0.04742,0.14073]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2158.0,"contact_point_centroid":[0.52822,0.06806,0.1422],"force_p95":0.14712,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26399,"mean_force":0.0901,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.52247,0.04979,0.14235]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53053,0.03058,-0.00209],"force_p95":0.14891,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.21594,"mean_force":0.12971,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51842,0.02988,0.03502]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4085.0,"contact_point_centroid":[0.51781,0.0106,0.03642],"force_p95":0.07909,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13917,"mean_force":0.05185,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.5172,0.0298,0.03363]},{"body_a":"world","body_b":"grasp_target","contact_count":940.0,"contact_point_centroid":[0.5305,0.03079,-0.00186],"force_p95":0.13709,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12315,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51021,0.01206,0.24361]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.56407,0.11765,-0.00199],"force_p95":0.12264,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12265,"mean_force":0.12263,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.58566,0.16492,0.11943]},{"body_a":"world","body_b":"grasp_target","contact_count":3808.0,"contact_point_centroid":[0.5305,0.03079,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.52282,0.02818,0.09936]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4952.0,"contact_point_centroid":[0.5178,0.04892,0.03545],"force_p95":0.07165,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08299,"mean_force":0.04468,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.5172,0.0298,0.03364]},{"body_a":"left_finger","body_b":"right_finger","contact_count":666.0,"contact_point_centroid":[0.57812,0.14327,0.14502],"force_p95":0.01362,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01596,"mean_force":0.01092,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.57762,0.14325,0.14281]},{"body_a":"left_finger","body_b":"right_finger","contact_count":216.0,"contact_point_centroid":[0.58892,0.166,0.11723],"force_p95":0.01104,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01105,"mean_force":0.0103,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.58862,0.16597,0.11507]}],"total_contact_groups":14},"final_pose_error":0.01972,"key_states":{"actual_goal_position":[0.60153,0.17858,0.10809],"final_object_position":[0.56407,0.11765,0.01602],"final_tcp_position":[0.591,0.16609,0.11914],"realised_goal_position":[0.60153,0.17858,0.10809],"realised_object_initial_position":[0.5305,0.03079,0.03]},"peak_contact_force":273015.07033,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":236.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.03],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18162,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":940.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.52232,0.02522,0.18477],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.15906,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":952.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3808.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.52534,0.03035,0.04294],"tcp_start":[0.52232,0.02522,0.18477],"tcp_to_object_dist_end":0.0177,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.5304,0.02982,0.02569],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18433,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.14356,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10837.0,"raw_peak_contact_force":0.21594,"subtask_id":"grasp_1","tcp_end":[0.51717,0.0298,0.0336],"tcp_start":[0.52534,0.03035,0.04294],"tcp_to_object_dist_end":0.01542,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":574.0,"n_steps_budget":660.0,"object_pos_end":[0.52785,0.02961,0.11014],"object_pos_start":[0.5304,0.02982,0.02569],"object_to_goal_dist_end":0.16621,"object_to_goal_dist_start":0.18433,"object_z_max":0.11003,"peak_contact_force":0.1146,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":18186.0,"raw_peak_contact_force":0.62941,"tcp_end":[0.51301,0.02953,0.12588],"tcp_start":[0.51717,0.0298,0.0336],"tcp_to_object_dist_end":0.02163,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":497.0,"n_steps_budget":1000.0,"object_pos_end":[0.56407,0.11765,0.01602],"object_pos_start":[0.52785,0.02961,0.11014],"object_to_goal_dist_end":0.11659,"object_to_goal_dist_start":0.16621,"object_z_max":0.13499,"peak_contact_force":273015.07033,"phase_name":"transport_arc","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":5475.0,"raw_peak_contact_force":1.67616,"subtask_id":"transport_arc","tcp_end":[0.591,0.16609,0.11914],"tcp_start":[0.51301,0.02953,0.12588],"tcp_to_object_dist_end":0.11707,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.56407,0.11765,0.01602],"object_pos_start":[0.56407,0.11765,0.01602],"object_to_goal_dist_end":0.11659,"object_to_goal_dist_start":0.11659,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1016.0,"raw_peak_contact_force":0.12265,"subtask_id":"release_1","tcp_end":[0.58383,0.16431,0.13935],"tcp_start":[0.591,0.16609,0.11914],"tcp_to_object_dist_end":0.13334,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.78169,"average_solve_count":142.0,"average_success_count":142.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.05114,"lift_1.lift_height":0.11091,"transport_arc.arc_height":0.18798},"optimized_scores":{"best_composite_score":0.27279,"best_fitness_score":0.54279,"best_task_score":0.13425},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":1957.0,"contact_point_centroid":[0.51144,0.01091,-0.00256],"force_p95":0.21672,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.95903,"mean_force":0.14688,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.53624,0.08912,0.26281]},{"body_a":"world","body_b":"grasp_target","contact_count":135.0,"contact_point_centroid":[0.50084,-0.015,-0.00109],"force_p95":0.42102,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.56662,"mean_force":0.07652,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48953,-0.01541,0.03628]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":9690.0,"contact_point_centroid":[0.48917,0.00361,0.08055],"force_p95":0.10555,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32205,"mean_force":0.06634,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48696,-0.01536,0.07848]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":10632.0,"contact_point_centroid":[0.48928,-0.03419,0.07905],"force_p95":0.10011,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29703,"mean_force":0.06146,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48697,-0.01536,0.07761]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2278.0,"contact_point_centroid":[0.49241,0.00789,0.16823],"force_p95":0.17689,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28417,"mean_force":0.10701,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.48663,-0.01063,0.16829]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2714.0,"contact_point_centroid":[0.49266,-0.0283,0.16936],"force_p95":0.14898,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2613,"mean_force":0.09354,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.48688,-0.01008,0.17004]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50381,-0.01556,-0.00203],"force_p95":0.13302,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.15584,"mean_force":0.12539,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49222,-0.01544,0.03581]},{"body_a":"world","body_b":"grasp_target","contact_count":1508.0,"contact_point_centroid":[0.50382,-0.01567,-0.00191],"force_p95":0.13496,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12295,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49928,-0.00673,0.20136]},{"body_a":"world","body_b":"grasp_target","contact_count":2148.0,"contact_point_centroid":[0.50382,-0.01567,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49795,-0.01488,0.06342]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.51137,0.01096,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.57338,0.17018,0.25262]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4116.0,"contact_point_centroid":[0.49145,0.00386,0.03734],"force_p95":0.07664,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11491,"mean_force":0.05216,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49105,-0.01543,0.03456]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5369.0,"contact_point_centroid":[0.4908,-0.03448,0.03723],"force_p95":0.06376,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0833,"mean_force":0.04079,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49105,-0.01543,0.03456]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1870.0,"contact_point_centroid":[0.54012,0.09615,0.26756],"force_p95":0.01149,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01514,"mean_force":0.01063,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.53976,0.09615,0.2653]},{"body_a":"left_finger","body_b":"right_finger","contact_count":223.0,"contact_point_centroid":[0.57565,0.17105,0.25048],"force_p95":0.01092,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01095,"mean_force":0.01001,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.57524,0.17105,0.2483]}],"total_contact_groups":14},"final_pose_error":0.01986,"key_states":{"actual_goal_position":[0.58691,0.18745,0.24812],"final_object_position":[0.51137,0.01096,0.01602],"final_tcp_position":[0.57675,0.1708,0.25185],"realised_goal_position":[0.58691,0.18745,0.24812],"realised_object_initial_position":[0.50382,-0.01567,0.03]},"peak_contact_force":1.95903,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":378.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.03],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.30942,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1508.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.4999,-0.01386,0.10023],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.07434,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":537.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2148.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.49886,-0.01553,0.04292],"tcp_start":[0.4999,-0.01386,0.10023],"tcp_to_object_dist_end":0.01762,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50371,-0.01527,0.02587],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.3121,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.13177,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11285.0,"raw_peak_contact_force":0.15584,"subtask_id":"grasp_1","tcp_end":[0.49102,-0.01543,0.03453],"tcp_start":[0.49886,-0.01553,0.04292],"tcp_to_object_dist_end":0.01536,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":25.0,"n_steps":633.0,"n_steps_budget":720.0,"object_pos_end":[0.50157,-0.01521,0.11718],"object_pos_start":[0.50371,-0.01527,0.02587],"object_to_goal_dist_end":0.25592,"object_to_goal_dist_start":0.3121,"object_z_max":0.11707,"peak_contact_force":0.0,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":20457.0,"raw_peak_contact_force":0.56662,"tcp_end":[0.48702,-0.01535,0.13376],"tcp_start":[0.49102,-0.01543,0.03453],"tcp_to_object_dist_end":0.02206,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":836.0,"n_steps_budget":1000.0,"object_pos_end":[0.51137,0.01096,0.01602],"object_pos_start":[0.50157,-0.01521,0.11718],"object_to_goal_dist_end":0.3012,"object_to_goal_dist_start":0.25592,"object_z_max":0.1852,"peak_contact_force":0.12263,"phase_name":"transport_arc","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":8819.0,"raw_peak_contact_force":1.95903,"subtask_id":"transport_arc","tcp_end":[0.57675,0.1708,0.25185],"tcp_start":[0.48702,-0.01535,0.13376],"tcp_to_object_dist_end":0.2923,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51137,0.01096,0.01602],"object_pos_start":[0.51137,0.01096,0.01602],"object_to_goal_dist_end":0.3012,"object_to_goal_dist_start":0.3012,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1023.0,"raw_peak_contact_force":0.12263,"subtask_id":"release_1","tcp_end":[0.57233,0.16972,0.27255],"tcp_start":[0.57675,0.1708,0.25185],"tcp_to_object_dist_end":0.30779,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```