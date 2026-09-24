## Search State

- **Seed**: 1
- **Iteration**: 4 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 3 | approach → descend → grasp → lift → approach → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | time_limit | 6 | 0.1654 | 0.23 | ❌ rejected |
| 2 | approach → descend → grasp → approach → release | linear_cartesian | linear_cartesian | — | arc_cartesian | — | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | time_limit | 0 | 0.2458 | 0.25 | ❌ rejected |
| 1 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 6 | 0.1204 | 0.19 | ✅ accepted |
| 0 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 6 | 0.2458 | 0.25 | ✅ accepted |

**Proposal policy**: task_score is 0.23 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `a2ed2c4162d37489f2d2d0fa0373774d72c951d58f2469e0ba2d602ff46b6cfb`
- Frozen object start: [0.5011821624700257, 0.045046369632593536, 0.03]
- Frozen task target: [0.5644159612719634, 0.2448649447137244, 0.1467747178015728]
- Goal object position: (0.5644159612719634, 0.2448649447137244, 0.1467747178015728)
- place_goal_position (task success criterion — final object 3D position must be close to the realised airborne target here): (0.5644159612719634, 0.2448649447137244, 0.1467747178015728)
- Grasp/lift components are optimiser fitness diagnostics only; canonical task_score is final object-to-realised-target proximity.
- Object initial pose: (0.5011821624700257, 0.045046369632593536, 0.03)
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
  frozen_object_start: [0.5012, 0.045, 0.03]
  frozen_task_target: [0.5644, 0.2449, 0.1468]
  frozen_object_starts: {'grasp_target': [0.5011821624700257, 0.045046369632593536, 0.03]}
  frozen_targets: {'place_target': [0.5644159612719634, 0.2448649447137244, 0.1467747178015728]}
  goal_tolerance_m: 0.02
  force_limit_n: 20
  force_scale_n: 5
  realized_scene_sha256: a2ed2c4162d37489f2d2d0fa0373774d72c951d58f2469e0ba2d602ff46b6cfb

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

## Current Skill (Q=0.165) — your mutation base

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
    entity: grasp_target
    offset:
    - 0.0
    - 0.0
    - 0.08
    orientation:
      mode: keep_current
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
    orientation:
      mode: keep_current
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
- id: transport_1
  type: approach
  generator: arc_cartesian
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
  subtask_id: release_1

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.08]
  - orientation: mode=keep_current
  - parameter_bindings: none
- **descend_1** (`descend`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.02]
  - orientation: mode=keep_current
  - parameter_bindings: none
- **grasp_1** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings: none
- **transport_1** (`approach`)
  - target: source=yaml, anchor=task_goal, entity=placement_surface, offset=[0.0, 0.0, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings: none
- **release_1** (`release`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings: none

## Design Metrics

- **Composite score**: 0.165
- **task_score** (E): 0.227
- **fitness_score**: 0.585  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.420

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1679 |
| descend_1 | 1.00 | 1.00 | 0.0913 |
| grasp_1 | 1.00 | 1.00 | 0.0111 |
| lift_1 | 1.00 | 1.00 | 0.1472 |
| transport_arc | 1.00 | 1.00 | 0.2298 |
| release_1 | 1.00 | 1.00 | 0.0209 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.477, -0.000, 0.138) | (0.479, -0.000, 0.030)→(0.479, -0.000, 0.026) | 0.276→0.278 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.477, -0.000, 0.138)→(0.474, -0.001, 0.047) | (0.479, -0.000, 0.026)→(0.479, -0.000, 0.026) | 0.278→0.278 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_1 | grasp | 1.00 / step_budget | (0.474, -0.001, 0.047)→(0.466, -0.001, 0.039) | (0.479, -0.000, 0.026)→(0.479, -0.001, 0.026) | 0.278→0.278 | 1.00 / 45.333 | 0.143 | 0.198 |
| lift_1 | lift | 1.00 / step_budget | (0.466, -0.001, 0.039)→(0.474, -0.001, 0.186) | (0.479, -0.001, 0.026)→(0.486, -0.001, 0.162) | 0.278→0.244 | 1.00 / 19.000 | 0.138 | 0.477 |
| transport_arc | approach | 1.00 / step_budget | (0.474, -0.001, 0.186)→(0.595, 0.189, 0.164) | (0.486, -0.001, 0.162)→(0.513, 0.054, 0.016) | 0.244→0.226 | 1.00 / 8.333 | 94253.375 | 1.809 |
| release_1 | release | 1.00 / step_budget | (0.595, 0.189, 0.164)→(0.589, 0.187, 0.184) | (0.513, 0.054, 0.016)→(0.513, 0.054, 0.016) | 0.226→0.226 | 1.00 / 4.000 | 0.123 | 0.123 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: 1.000
- terminal_score: 0.266
- phase_score: 0.727
- phase_breakdown.release_1_score: 0.487
- phase_breakdown.grasp_1_score: 1.000
- phase_breakdown.descend_1_score: 0.893
- phase_breakdown.transport_arc_score: 0.745
- phase_breakdown.approach_1_score: 0.094
- grasp_place_fitness: 0.604

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.604
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.266
- **Median Q (composite search score)**: 0.177
- **K-run variance**: 0.0005
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.460


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `8110053be9072e64e15984c6424e4a66fe19af4b6c37a60139a43e94cc34ad53`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.05,0.05],"goal_z_delta":0.15,"object_xy_delta":[0.05,0.05]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `46ef03f7b16015a0d14bf26d80c05d326b92c02b0bf759391930f5ab902d1933`; realized-scene SHA-256: `a2ed2c4162d37489f2d2d0fa0373774d72c951d58f2469e0ba2d602ff46b6cfb`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50118,0.04505,0.03]},{"name":"goal","value":[0.56442,0.24486,0.14677]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.50118,0.04505,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.56442,0.24486,0.14677]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.91111,"average_solve_count":135.0,"average_success_count":135.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.11006,"descend_1.grasp_z_offset":0.01263,"grasp_1.grasp_time":2.97892,"lift_1.lift_height":0.16682,"release_1.release_time":1.00105,"transport_arc.arc_height":0.09043},"optimized_scores":{"best_composite_score":0.1844,"best_fitness_score":0.6044,"best_task_score":0.26627},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":2924.0,"contact_point_centroid":[0.51222,0.10496,-0.00236],"force_p95":0.13173,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.83488,"mean_force":0.14024,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.53167,0.15487,0.22748]},{"body_a":"world","body_b":"grasp_target","contact_count":143.0,"contact_point_centroid":[0.49927,0.04244,-0.00122],"force_p95":0.30472,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.48321,"mean_force":0.06079,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48705,0.04326,0.0405]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":13020.0,"contact_point_centroid":[0.49276,0.06197,0.09979],"force_p95":0.10585,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.3003,"mean_force":0.0679,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48971,0.04313,0.09816]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":12435.0,"contact_point_centroid":[0.49302,0.02429,0.10249],"force_p95":0.10742,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29612,"mean_force":0.07019,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.4899,0.04313,0.10058]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1136.0,"contact_point_centroid":[0.50282,0.06855,0.18821],"force_p95":0.1707,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28391,"mean_force":0.11359,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.49724,0.0506,0.19238]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1029.0,"contact_point_centroid":[0.50267,0.03135,0.18705],"force_p95":0.17541,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26039,"mean_force":0.1153,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.49701,0.04955,0.19074]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50123,0.04481,-0.00214],"force_p95":0.16272,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.22727,"mean_force":0.13322,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.48947,0.04351,0.03984]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4074.0,"contact_point_centroid":[0.48878,0.02415,0.04143],"force_p95":0.08251,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1545,"mean_force":0.05205,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.48833,0.0434,0.03861]},{"body_a":"world","body_b":"grasp_target","contact_count":1940.0,"contact_point_centroid":[0.50118,0.04505,-0.00193],"force_p95":0.13308,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12288,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49774,0.02,0.22391]},{"body_a":"world","body_b":"grasp_target","contact_count":1272.0,"contact_point_centroid":[0.50118,0.04505,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49559,0.04242,0.09728]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.51222,0.10495,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.55523,0.23742,0.16011]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5351.0,"contact_point_centroid":[0.4883,0.06254,0.04101],"force_p95":0.07112,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07978,"mean_force":0.04182,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.48833,0.0434,0.03862]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2935.0,"contact_point_centroid":[0.53392,0.16003,0.23014],"force_p95":0.01111,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01621,"mean_force":0.0105,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.53342,0.16001,0.22785]},{"body_a":"left_finger","body_b":"right_finger","contact_count":220.0,"contact_point_centroid":[0.5581,0.23867,0.15786],"force_p95":0.01102,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01103,"mean_force":0.01015,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.55772,0.23864,0.15564]}],"total_contact_groups":14},"final_pose_error":0.01474,"key_states":{"actual_goal_position":[0.56442,0.24486,0.14677],"final_object_position":[0.51222,0.10495,0.01602],"final_tcp_position":[0.55964,0.23927,0.15955],"realised_goal_position":[0.56442,0.24486,0.14677],"realised_object_initial_position":[0.50118,0.04505,0.03]},"peak_contact_force":1.83488,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":486.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.03],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.23992,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1940.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.49739,0.04095,0.14811],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.12222,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":318.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1272.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.4963,0.04412,0.04725],"tcp_start":[0.49739,0.04095,0.14811],"tcp_to_object_dist_end":0.02181,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50113,0.04362,0.02552],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.24333,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"peak_contact_force":0.15624,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11225.0,"raw_peak_contact_force":0.22727,"subtask_id":"grasp_1","tcp_end":[0.4883,0.0434,0.03858],"tcp_start":[0.4963,0.04412,0.04725],"tcp_to_object_dist_end":0.01832,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":17.0,"n_steps":874.0,"n_steps_budget":960.0,"object_pos_end":[0.50936,0.04321,0.15707],"object_pos_start":[0.50113,0.04362,0.02552],"object_to_goal_dist_end":0.20929,"object_to_goal_dist_start":0.24333,"object_z_max":0.15697,"peak_contact_force":0.16913,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":25598.0,"raw_peak_contact_force":0.48321,"tcp_end":[0.49694,0.04328,0.18014],"tcp_start":[0.4883,0.0434,0.03858],"tcp_to_object_dist_end":0.0262,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":956.0,"n_steps_budget":1000.0,"object_pos_end":[0.51222,0.10495,0.01602],"object_pos_start":[0.50936,0.04321,0.15707],"object_to_goal_dist_end":0.19849,"object_to_goal_dist_start":0.20929,"object_z_max":0.17642,"peak_contact_force":0.12263,"phase_name":"transport_arc","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":8024.0,"raw_peak_contact_force":1.83488,"subtask_id":"transport_arc","tcp_end":[0.55964,0.23927,0.15955],"tcp_start":[0.49694,0.04328,0.18014],"tcp_to_object_dist_end":0.20221,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51222,0.10495,0.01602],"object_pos_start":[0.51222,0.10495,0.01602],"object_to_goal_dist_end":0.19849,"object_to_goal_dist_start":0.19849,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1020.0,"raw_peak_contact_force":0.12263,"subtask_id":"release_1","tcp_end":[0.55372,0.23668,0.1801],"tcp_start":[0.55964,0.23927,0.15955],"tcp_to_object_dist_end":0.21447,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `1efc3ad2e58ea1c47cd56203c4986b53dab7b80d759e458b85d233ccc9cc04bd`; realized-scene SHA-256: `67b45068113fe0ef6f199d4981822d51bd0bd66bb4f388f7402a08094b41852a`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.47616,-0.02015,0.03]},{"name":"goal","value":[0.63142,0.15919,0.19002]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.47616,-0.02015,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.63142,0.15919,0.19002]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.91837,"average_solve_count":147.0,"average_success_count":147.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.08242,"descend_1.grasp_z_offset":0.01079,"grasp_1.grasp_time":2.0964,"lift_1.lift_height":0.19725,"release_1.release_time":1.96251,"transport_arc.arc_height":0.05164},"optimized_scores":{"best_composite_score":0.13492,"best_fitness_score":0.55492,"best_task_score":0.16345},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":3248.0,"contact_point_centroid":[0.49932,-0.00231,-0.00232],"force_p95":0.12541,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.89368,"mean_force":0.13693,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.54997,0.07127,0.2272]},{"body_a":"world","body_b":"grasp_target","contact_count":130.0,"contact_point_centroid":[0.47405,-0.01925,-0.00109],"force_p95":0.33688,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.48893,"mean_force":0.05495,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46271,-0.01958,0.03954]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":13856.0,"contact_point_centroid":[0.46781,-0.0007,0.10706],"force_p95":0.11466,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28332,"mean_force":0.07159,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46479,-0.01954,0.10543]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":14595.0,"contact_point_centroid":[0.46784,-0.03832,0.10613],"force_p95":0.10959,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27773,"mean_force":0.06879,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46476,-0.01954,0.10488]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":275.0,"contact_point_centroid":[0.47873,0.00127,0.19538],"force_p95":0.20156,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21781,"mean_force":0.14706,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.47283,-0.0168,0.20015]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":422.0,"contact_point_centroid":[0.47909,-0.03317,0.19608],"force_p95":0.1569,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19511,"mean_force":0.09971,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.47352,-0.01574,0.20093]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.47616,-0.02006,-0.00204],"force_p95":0.13629,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.17682,"mean_force":0.12632,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46503,-0.01964,0.03885]},{"body_a":"world","body_b":"grasp_target","contact_count":2144.0,"contact_point_centroid":[0.47616,-0.02015,-0.00193],"force_p95":0.13219,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12285,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48636,-0.00907,0.21087]},{"body_a":"world","body_b":"grasp_target","contact_count":996.0,"contact_point_centroid":[0.47616,-0.02015,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.4718,-0.0191,0.08351]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.4993,-0.00231,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.61598,0.14864,0.19241]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5075.0,"contact_point_centroid":[0.46366,-0.00036,0.04048],"force_p95":0.06583,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09728,"mean_force":0.04292,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46393,-0.01961,0.03775]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5393.0,"contact_point_centroid":[0.46353,-0.03886,0.03998],"force_p95":0.06488,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08464,"mean_force":0.04115,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46393,-0.01961,0.03776]},{"body_a":"left_finger","body_b":"right_finger","contact_count":3255.0,"contact_point_centroid":[0.55459,0.07599,0.23017],"force_p95":0.01103,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01617,"mean_force":0.01047,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.55423,0.07599,0.22788]},{"body_a":"left_finger","body_b":"right_finger","contact_count":223.0,"contact_point_centroid":[0.61874,0.14947,0.19122],"force_p95":0.01091,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01092,"mean_force":0.01001,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.61843,0.14946,0.18872]}],"total_contact_groups":14},"final_pose_error":0.01499,"key_states":{"actual_goal_position":[0.63142,0.15919,0.19002],"final_object_position":[0.4993,-0.00231,0.01602],"final_tcp_position":[0.62025,0.14952,0.19256],"realised_goal_position":[0.63142,0.15919,0.19002],"realised_object_initial_position":[0.47616,-0.02015,0.03]},"peak_contact_force":273011.11325,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":537.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.03],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28614,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2144.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.4742,-0.01851,0.12183],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.09584,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":249.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":996.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.47163,-0.01979,0.04553],"tcp_start":[0.4742,-0.01851,0.12183],"tcp_to_object_dist_end":0.02003,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":47.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.47606,-0.0197,0.02583],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28826,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.13461,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12268.0,"raw_peak_contact_force":0.17682,"subtask_id":"grasp_1","tcp_end":[0.4639,-0.01961,0.03772],"tcp_start":[0.47163,-0.01979,0.04553],"tcp_to_object_dist_end":0.01701,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":16.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.48059,-0.01963,0.17344],"object_pos_start":[0.47606,-0.0197,0.02583],"object_to_goal_dist_end":0.23453,"object_to_goal_dist_start":0.28826,"object_z_max":0.17326,"peak_contact_force":0.14098,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":28581.0,"raw_peak_contact_force":0.48893,"tcp_end":[0.4712,-0.01958,0.19802],"tcp_start":[0.4639,-0.01961,0.03772],"tcp_to_object_dist_end":0.02632,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":948.0,"n_steps_budget":1000.0,"object_pos_end":[0.4993,-0.00231,0.01602],"object_pos_start":[0.48059,-0.01963,0.17344],"object_to_goal_dist_end":0.27169,"object_to_goal_dist_start":0.23453,"object_z_max":0.17649,"peak_contact_force":273011.11325,"phase_name":"transport_arc","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":7200.0,"raw_peak_contact_force":1.89368,"subtask_id":"transport_arc","tcp_end":[0.62025,0.14952,0.19256],"tcp_start":[0.4712,-0.01958,0.19802],"tcp_to_object_dist_end":0.2624,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.4993,-0.00231,0.01602],"object_pos_start":[0.4993,-0.00231,0.01602],"object_to_goal_dist_end":0.27169,"object_to_goal_dist_start":0.27169,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1023.0,"raw_peak_contact_force":0.12263,"subtask_id":"release_1","tcp_end":[0.61454,0.14818,0.21191],"tcp_start":[0.62025,0.14952,0.19256],"tcp_to_object_dist_end":0.27258,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `37495cb43897015e78e007c86af160d11c8460c1ce7249e5c03dce38206c0daf`; realized-scene SHA-256: `5ce27bcdb8582e1d517b17df0f9c2ad7b05701113a75707627744a889253e6a7`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.45856,-0.02632,0.03]},{"name":"goal","value":[0.63013,0.20822,0.11412]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.45856,-0.02632,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.63013,0.20822,0.11412]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.91781,"average_solve_count":146.0,"average_success_count":146.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.10458,"descend_1.grasp_z_offset":0.01263,"grasp_1.grasp_time":2.10756,"lift_1.lift_height":0.16486,"release_1.release_time":1.72194,"transport_arc.arc_height":0.05183},"optimized_scores":{"best_composite_score":0.177,"best_fitness_score":0.597,"best_task_score":0.25221},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":2388.0,"contact_point_centroid":[0.52609,0.05901,-0.00241],"force_p95":0.14816,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.69825,"mean_force":0.14272,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.55834,0.11656,0.17919]},{"body_a":"world","body_b":"grasp_target","contact_count":128.0,"contact_point_centroid":[0.45651,-0.02505,-0.00111],"force_p95":0.34466,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.45837,"mean_force":0.04746,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44584,-0.02554,0.04217]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":12973.0,"contact_point_centroid":[0.45071,-0.00658,0.103],"force_p95":0.10513,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27151,"mean_force":0.06725,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44816,-0.02549,0.10094]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":13795.0,"contact_point_centroid":[0.45062,-0.04435,0.10133],"force_p95":0.10115,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2644,"mean_force":0.06412,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44806,-0.02549,0.09972]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2713.0,"contact_point_centroid":[0.47881,-0.01528,0.18416],"force_p95":0.15057,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23899,"mean_force":0.10573,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.47319,0.00282,0.18757]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2710.0,"contact_point_centroid":[0.48069,0.02355,0.18487],"force_p95":0.14056,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20795,"mean_force":0.10428,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.47508,0.00544,0.18827]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.45857,-0.02622,-0.00206],"force_p95":0.1409,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.19087,"mean_force":0.12748,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44803,-0.02563,0.04137]},{"body_a":"world","body_b":"grasp_target","contact_count":1904.0,"contact_point_centroid":[0.45856,-0.02632,-0.00193],"force_p95":0.13347,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12288,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.47885,-0.01166,0.22222]},{"body_a":"world","body_b":"grasp_target","contact_count":1260.0,"contact_point_centroid":[0.45856,-0.02632,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.45534,-0.02482,0.09551]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.52614,0.05903,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.60036,0.17775,0.14052]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4840.0,"contact_point_centroid":[0.44693,-0.00634,0.04259],"force_p95":0.06839,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10363,"mean_force":0.04487,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44697,-0.02559,0.04035]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5406.0,"contact_point_centroid":[0.44642,-0.04481,0.042],"force_p95":0.06537,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07858,"mean_force":0.04109,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44697,-0.02559,0.04035]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2295.0,"contact_point_centroid":[0.56314,0.12254,0.17961],"force_p95":0.01103,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01625,"mean_force":0.01058,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.56284,0.12254,0.17729]},{"body_a":"left_finger","body_b":"right_finger","contact_count":220.0,"contact_point_centroid":[0.60352,0.17883,0.13888],"force_p95":0.01098,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01099,"mean_force":0.01011,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.60322,0.17882,0.13664]}],"total_contact_groups":14},"final_pose_error":0.04647,"key_states":{"actual_goal_position":[0.63013,0.20822,0.11412],"final_object_position":[0.52614,0.05903,0.01602],"final_tcp_position":[0.60524,0.17896,0.14028],"realised_goal_position":[0.63013,0.20822,0.11412],"realised_object_initial_position":[0.45856,-0.02632,0.03]},"peak_contact_force":9748.88887,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":477.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.03],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30252,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1904.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.45857,-0.02392,0.14402],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.11802,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":315.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1260.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.45444,-0.02585,0.04759],"tcp_start":[0.45857,-0.02392,0.14402],"tcp_to_object_dist_end":0.02197,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":46.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.45848,-0.02572,0.02577],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30331,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.1383,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12046.0,"raw_peak_contact_force":0.19087,"subtask_id":"grasp_1","tcp_end":[0.44694,-0.02558,0.04032],"tcp_start":[0.45444,-0.02585,0.04759],"tcp_to_object_dist_end":0.01857,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":24.0,"n_steps":873.0,"n_steps_budget":960.0,"object_pos_end":[0.46703,-0.02557,0.1559],"object_pos_start":[0.45848,-0.02572,0.02577],"object_to_goal_dist_end":0.2881,"object_to_goal_dist_start":0.30331,"object_z_max":0.15579,"peak_contact_force":0.10403,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":26896.0,"raw_peak_contact_force":0.45837,"tcp_end":[0.45446,-0.02556,0.17938],"tcp_start":[0.44694,-0.02558,0.04032],"tcp_to_object_dist_end":0.02663,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.52614,0.05903,0.01602],"object_pos_start":[0.46703,-0.02557,0.1559],"object_to_goal_dist_end":0.20662,"object_to_goal_dist_start":0.2881,"object_z_max":0.16719,"peak_contact_force":9748.88887,"phase_name":"transport_arc","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":10106.0,"raw_peak_contact_force":1.69825,"subtask_id":"transport_arc","tcp_end":[0.60524,0.17896,0.14028],"tcp_start":[0.45446,-0.02556,0.17938],"tcp_to_object_dist_end":0.18995,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.52614,0.05903,0.01602],"object_pos_start":[0.52614,0.05903,0.01602],"object_to_goal_dist_end":0.20662,"object_to_goal_dist_start":0.20662,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1020.0,"raw_peak_contact_force":0.12263,"subtask_id":"release_1","tcp_end":[0.59863,0.17713,0.16016],"tcp_start":[0.60524,0.17896,0.14028],"tcp_to_object_dist_end":0.19995,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```