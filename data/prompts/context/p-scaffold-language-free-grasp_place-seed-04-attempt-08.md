## Search State

- **Seed**: 4
- **Iteration**: 9 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 8 | approach → descend → grasp → lift → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | force_threshold_switch | position_control | position_control | position_control | admittance_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | time_limit | 4 | 0.3580 | 0.37 | ❌ rejected |
| 7 | approach → descend → grasp → lift → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | force_threshold_switch | position_control | position_control | position_control | admittance_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | time_limit | 4 | 0.3576 | 0.37 | ❌ rejected |
| 6 | approach → descend → grasp → lift → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | force_threshold_switch | position_control | position_control | position_control | admittance_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | time_limit | 4 | 0.3576 | 0.37 | ❌ rejected |
| 5 | approach → descend → grasp → lift → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | force_threshold_switch | position_control | position_control | position_control | admittance_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | time_limit | 4 | 0.3576 | 0.37 | ❌ rejected |
| 4 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 8 | 0.0849 | 0.32 | ❌ rejected |

**Proposal policy**: task_score is 0.37 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

**Mode**: free (you define subtask targets; use `subtasks:` block in your YAML)

Define subtasks in a `subtasks:` block **before** `phases:`. Each subtask specifies an intermediate optimisation target.

**Required fields** — always include both, never omit:
- `anchor` (**required**): fixture | goal | object | world
- `target_entity` (**required**): hinge | object | tcp

Subtask anchors are separate from phase `target.anchor` vocabulary: subtasks use `world | object | goal | fixture`, while phase targets use `world | task_goal | task_object | fixture | body | site | current_tcp`.

Optional fields:
- `metric`: contact | distance | goal_progress | hinge_angle (default: distance)
- `offset`: [x, y, z] in metres relative to anchor (default: [0, 0, 0])
- `param_offset_key`: CMA-ES parameter added to offset at runtime (optional)
- `weight`: scoring weight [0.1, 1.0] (default: 1.0)

**Anchor resolution for this task** — choose anchor so the resolved position is meaningful:
| Anchor | Resolves to | Best used for |
|--------|-------------|---------------|
| `world` | absolute world-frame coordinate | fixed reference points not tied to objects |
| `object` | offset from object initial position (0.5443056105572368, 0.0011327552814361583, 0.03) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.6476243705707704, 0.15808360238956023, 0.19110337479925443) | final destination targets |
| `fixture` | offset from fixture pose (if defined, else world) | targets near fixture |

Annotate each phase with `subtask_id: <id>` to bind it to a subtask.
Only the **last phase** bound to a given subtask contributes to subtask scoring.

Example (two subtasks — one near object start, one at goal):
```yaml
subtasks:
  - id: reach_pre_contact
    anchor: object         # resolved to object initial position (see table above)
    target_entity: tcp     # score TCP distance to this target
    metric: distance
    offset: [0.0, 0.0, 0.10]  # 10 cm above object start position
    weight: 0.3
  - id: reach_goal
    anchor: goal           # resolved to task goal position (see table above)
    target_entity: tcp
    metric: distance
    offset: [0.0, 0.0, 0.0]
    weight: 0.7
phases:
  - id: approach_1
    type: approach
    subtask_id: reach_pre_contact
    ...
  - id: push_1
    type: push
    subtask_id: reach_goal
    ...
```

## Current Skill (Q=0.358) — your mutation base

```yaml
skill: grasp_place
skill_type: arm_gripper
phases:
- id: approach_1
  type: approach
  generator: linear_cartesian
  control: force_threshold_switch
  termination: pose_tolerance
  parameters:
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1
- id: descend_1
  type: descend
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  parameters:
    depth:
      type: scalar
      range:
      - 0.01
      - 0.1
- id: grasp_1
  type: grasp
  control: position_control
  termination: time_limit
  end_effector_action: force_grasp
  parameters:
    grip_force:
      type: scalar
      range:
      - 5.0
      - 30.0
- id: lift_1
  type: lift
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  parameters:
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1
- id: release_1
  type: release
  generator: linear_cartesian
  control: admittance_control
  termination: time_limit
  end_effector_action: open

```

## Design Metrics

- **Composite score**: 0.358
- **task_score** (E): 0.368
- **fitness_score**: 0.648  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.290

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1663 |
| descend_1 | 1.00 | 1.00 | 0.0833 |
| grasp_1 | 1.00 | 1.00 | 0.0131 |
| lift_1 | 0.33 | 1.00 | 0.1192 |
| release_1 | 1.00 | 1.00 | 0.1606 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.520, 0.005, 0.137) | (0.526, 0.005, 0.030)→(0.526, 0.005, 0.026) | 0.246→0.249 | 1.00 / 4.000 | 8.570 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.520, 0.005, 0.137)→(0.521, 0.005, 0.054) | (0.526, 0.005, 0.026)→(0.526, 0.005, 0.026) | 0.249→0.249 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_1 | grasp | 1.00 / step_budget | (0.521, 0.005, 0.054)→(0.512, 0.005, 0.044) | (0.526, 0.005, 0.026)→(0.526, 0.005, 0.026) | 0.249→0.249 | 1.00 / 46.000 | 0.139 | 0.174 |
| lift_1 | lift | 0.33 / step_budget | (0.512, 0.005, 0.044)→(0.518, 0.005, 0.163) | (0.526, 0.005, 0.026)→(0.525, 0.005, 0.139) | 0.249→0.204 | 1.00 / 38.000 | 0.078 | 0.431 |
| release_1 | release | 1.00 / time_limit | (0.518, 0.005, 0.163)→(0.587, 0.139, 0.191) | (0.525, 0.005, 0.139)→(0.583, 0.150, 0.025) | 0.204→0.163 | 1.00 / 3.000 | 0.214 | 1.405 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.573
- phase_score: 0.323
- phase_breakdown.transport_arc_score: 0.000
- phase_breakdown.release_1_score: 0.535
- phase_breakdown.grasp_1_score: 1.000
- phase_breakdown.descend_1_score: 0.868
- phase_breakdown.approach_1_score: 0.117
- grasp_place_fitness: 0.750

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.750
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.573
- **Median Q (composite search score)**: 0.336
- **K-run variance**: 0.0058
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.329


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.46328,"average_solve_count":177.0,"average_success_count":177.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.04306,"descend_1.depth":0.04944,"grasp_1.grip_force":10.3086,"lift_1.speed":0.0836},"optimized_scores":{"best_composite_score":0.33649,"best_fitness_score":0.62649,"best_task_score":0.32379},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":239.0,"contact_point_centroid":[0.61638,0.14162,-0.006],"force_p95":0.92558,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.57937,"mean_force":0.29081,"phase_index":4.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.6238,0.13224,0.19727]},{"body_a":"world","body_b":"grasp_target","contact_count":174.0,"contact_point_centroid":[0.5408,0.0009,-0.00114],"force_p95":0.2628,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.44663,"mean_force":0.08116,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52814,0.0008,0.04506]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":19836.0,"contact_point_centroid":[0.53171,0.02002,0.1106],"force_p95":0.07365,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30832,"mean_force":0.05133,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.53098,0.00086,0.10782]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":20453.0,"contact_point_centroid":[0.5314,-0.01826,0.10835],"force_p95":0.0741,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28171,"mean_force":0.0501,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.53084,0.00086,0.10595]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":18014.0,"contact_point_centroid":[0.57547,0.08149,0.17662],"force_p95":0.08709,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27539,"mean_force":0.05506,"phase_index":4.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.57716,0.06269,0.17613]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":16604.0,"contact_point_centroid":[0.57596,0.04055,0.17568],"force_p95":0.10767,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25965,"mean_force":0.06009,"phase_index":4.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.575,0.05963,0.17595]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.54431,0.00116,-0.00203],"force_p95":0.13134,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.15484,"mean_force":0.12547,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53089,0.00086,0.04503]},{"body_a":"world","body_b":"grasp_target","contact_count":2404.0,"contact_point_centroid":[0.54431,0.00113,-0.00194],"force_p95":0.13067,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12283,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51702,0.00047,0.21764]},{"body_a":"world","body_b":"grasp_target","contact_count":1012.0,"contact_point_centroid":[0.54431,0.00113,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.53634,0.00097,0.09487]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4149.0,"contact_point_centroid":[0.5309,0.02013,0.0461],"force_p95":0.07646,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09636,"mean_force":0.05216,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52964,0.00083,0.04354]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5327.0,"contact_point_centroid":[0.53024,-0.0182,0.04617],"force_p95":0.06266,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08976,"mean_force":0.04074,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52964,0.00083,0.04354]}],"total_contact_groups":11},"final_pose_error":0.03429,"key_states":{"actual_goal_position":[0.64762,0.15808,0.1911],"final_object_position":[0.61739,0.14086,0.02557],"final_tcp_position":[0.62681,0.13293,0.18064],"realised_goal_position":[0.64762,0.15808,0.1911],"realised_object_initial_position":[0.54431,0.00113,0.03]},"peak_contact_force":25.46423,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":602.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.03],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.24751,"object_z_max":0.03,"peak_contact_force":25.46423,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2404.0,"raw_peak_contact_force":0.13845,"tcp_end":[0.53689,0.00098,0.13643],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.11066,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":253.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1012.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.53833,0.00101,0.05397],"tcp_start":[0.53689,0.00098,0.13643],"tcp_to_object_dist_end":0.02858,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54422,0.00112,0.02586],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25028,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.13103,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11276.0,"raw_peak_contact_force":0.15484,"tcp_end":[0.52961,0.00083,0.04351],"tcp_start":[0.53833,0.00101,0.05397],"tcp_to_object_dist_end":0.02291,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":38.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.54439,0.00112,0.15363],"object_pos_start":[0.54422,0.00112,0.02586],"object_to_goal_dist_end":0.19157,"object_to_goal_dist_start":0.25028,"object_z_max":0.15347,"peak_contact_force":0.07801,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":40463.0,"raw_peak_contact_force":0.44663,"tcp_end":[0.537,0.00098,0.17769],"tcp_start":[0.52961,0.00083,0.04351],"tcp_to_object_dist_end":0.02517,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.61739,0.14086,0.02557],"object_pos_start":[0.54439,0.00112,0.15363],"object_to_goal_dist_end":0.16915,"object_to_goal_dist_start":0.19157,"object_z_max":0.15372,"peak_contact_force":0.09012,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":34857.0,"raw_peak_contact_force":1.57937,"tcp_end":[0.62374,0.1322,0.20627],"tcp_start":[0.537,0.00098,0.17769],"tcp_to_object_dist_end":0.18101,"terminated_normally":true,"termination_reason":"time_limit"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.90071,"average_solve_count":141.0,"average_success_count":141.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.07622,"descend_1.depth":0.06811,"grasp_1.grip_force":29.31223,"lift_1.speed":0.07379},"optimized_scores":{"best_composite_score":0.46045,"best_fitness_score":0.75045,"best_task_score":0.57298},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":192.0,"contact_point_centroid":[0.5837,0.17422,-0.00572],"force_p95":0.76926,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.83807,"mean_force":0.34977,"phase_index":4.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.58682,0.16387,0.11749]},{"body_a":"world","body_b":"grasp_target","contact_count":188.0,"contact_point_centroid":[0.5265,0.02886,-0.00125],"force_p95":0.25599,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.44102,"mean_force":0.08197,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51462,0.02941,0.04568]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":16622.0,"contact_point_centroid":[0.54785,0.10836,0.13409],"force_p95":0.09944,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.40641,"mean_force":0.06003,"phase_index":4.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.55045,0.08972,0.134]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":19270.0,"contact_point_centroid":[0.51718,0.04868,0.10442],"force_p95":0.07491,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29161,"mean_force":0.05235,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51688,0.0295,0.10162]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":20916.0,"contact_point_centroid":[0.51806,0.01041,0.10074],"force_p95":0.0766,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27413,"mean_force":0.04899,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51667,0.02949,0.09903]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":15090.0,"contact_point_centroid":[0.55056,0.06828,0.1339],"force_p95":0.11049,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26752,"mean_force":0.06616,"phase_index":4.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.54914,0.08721,0.135]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53055,0.03083,-0.00211],"force_p95":0.15297,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.20407,"mean_force":0.13092,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51743,0.0296,0.04548]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5782.0,"contact_point_centroid":[0.51719,0.01037,0.04671],"force_p95":0.06397,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14049,"mean_force":0.0381,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51619,0.02952,0.04406]},{"body_a":"world","body_b":"grasp_target","contact_count":2196.0,"contact_point_centroid":[0.5305,0.03079,-0.00194],"force_p95":0.13205,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12285,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51073,0.01382,0.21821]},{"body_a":"world","body_b":"grasp_target","contact_count":1024.0,"contact_point_centroid":[0.5305,0.03079,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.52317,0.02904,0.09527]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4699.0,"contact_point_centroid":[0.51639,0.04885,0.04772],"force_p95":0.0753,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07814,"mean_force":0.04682,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.5162,0.02952,0.04407]}],"total_contact_groups":11},"final_pose_error":0.01797,"key_states":{"actual_goal_position":[0.60153,0.17858,0.10809],"final_object_position":[0.57765,0.18051,0.02806],"final_tcp_position":[0.59041,0.16482,0.10494],"realised_goal_position":[0.60153,0.17858,0.10809],"realised_object_initial_position":[0.5305,0.03079,0.03]},"peak_contact_force":0.83807,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":550.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.03],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18162,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2196.0,"raw_peak_contact_force":0.13845,"tcp_end":[0.52408,0.02817,0.13717],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.11137,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":256.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1024.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.52475,0.03008,0.05406],"tcp_start":[0.52408,0.02817,0.13717],"tcp_to_object_dist_end":0.02864,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":47.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53048,0.03026,0.0256],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18399,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.15145,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12281.0,"raw_peak_contact_force":0.20407,"tcp_end":[0.51616,0.02952,0.04403],"tcp_start":[0.52475,0.03008,0.05406],"tcp_to_object_dist_end":0.02335,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":38.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.52889,0.03039,0.13769],"object_pos_start":[0.53048,0.03026,0.0256],"object_to_goal_dist_end":0.16767,"object_to_goal_dist_start":0.18399,"object_z_max":0.13758,"peak_contact_force":0.07754,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":40374.0,"raw_peak_contact_force":0.44102,"tcp_end":[0.52203,0.02977,0.16255],"tcp_start":[0.51616,0.02952,0.04403],"tcp_to_object_dist_end":0.02579,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.57765,0.18051,0.02806],"object_pos_start":[0.52889,0.03039,0.13769],"object_to_goal_dist_end":0.08354,"object_to_goal_dist_start":0.16767,"object_z_max":0.13773,"peak_contact_force":0.25321,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":31904.0,"raw_peak_contact_force":0.83807,"tcp_end":[0.58664,0.16376,0.13124],"tcp_start":[0.52203,0.02977,0.16255],"tcp_to_object_dist_end":0.10492,"terminated_normally":true,"termination_reason":"time_limit"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.37427,"average_solve_count":171.0,"average_success_count":171.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.04527,"descend_1.depth":0.09403,"grasp_1.grip_force":24.55863,"lift_1.speed":0.06379},"optimized_scores":{"best_composite_score":0.27693,"best_fitness_score":0.56693,"best_task_score":0.20703},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":176.0,"contact_point_centroid":[0.54416,0.13059,-0.00772],"force_p95":1.25156,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.79875,"mean_force":0.41527,"phase_index":4.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.55058,0.11968,0.22827]},{"body_a":"world","body_b":"grasp_target","contact_count":170.0,"contact_point_centroid":[0.50056,-0.0152,-0.00113],"force_p95":0.27098,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.40634,"mean_force":0.07348,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48875,-0.01536,0.04697]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":20722.0,"contact_point_centroid":[0.49115,0.00371,0.09661],"force_p95":0.07398,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26545,"mean_force":0.04916,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49002,-0.01541,0.0952]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":19914.0,"contact_point_centroid":[0.49057,-0.03459,0.09836],"force_p95":0.0726,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25778,"mean_force":0.05047,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49009,-0.01541,0.09596]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":17548.0,"contact_point_centroid":[0.51877,0.06694,0.17493],"force_p95":0.09524,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21742,"mean_force":0.05641,"phase_index":4.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.51996,0.04807,0.17503]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":17415.0,"contact_point_centroid":[0.52215,0.029,0.17489],"force_p95":0.09977,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21356,"mean_force":0.05651,"phase_index":4.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.51983,0.04778,0.1749]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50382,-0.01574,-0.00203],"force_p95":0.13438,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.1629,"mean_force":0.12564,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49136,-0.01538,0.04663]},{"body_a":"world","body_b":"grasp_target","contact_count":2144.0,"contact_point_centroid":[0.50382,-0.01567,-0.00193],"force_p95":0.13219,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12285,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49864,-0.00697,0.21968]},{"body_a":"world","body_b":"grasp_target","contact_count":1056.0,"contact_point_centroid":[0.50382,-0.01567,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49779,-0.01485,0.09634]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5562.0,"contact_point_centroid":[0.49091,0.00386,0.04741],"force_p95":0.0642,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0894,"mean_force":0.0399,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49016,-0.01537,0.04533]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5123.0,"contact_point_centroid":[0.49016,-0.03464,0.0488],"force_p95":0.06791,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0819,"mean_force":0.04272,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49016,-0.01537,0.04533]}],"total_contact_groups":11},"final_pose_error":0.08472,"key_states":{"actual_goal_position":[0.58691,0.18745,0.24812],"final_object_position":[0.55345,0.12775,0.02201],"final_tcp_position":[0.55319,0.12027,0.20904],"realised_goal_position":[0.58691,0.18745,0.24812],"realised_object_initial_position":[0.50382,-0.01567,0.03]},"peak_contact_force":1.79875,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":537.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.03],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.30942,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2144.0,"raw_peak_contact_force":0.13845,"tcp_end":[0.4995,-0.01431,0.13887],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.11294,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":264.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1056.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.49852,-0.01543,0.05449],"tcp_start":[0.4995,-0.01431,0.13887],"tcp_to_object_dist_end":0.02896,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":48.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50374,-0.01566,0.02585],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31237,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.13461,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12485.0,"raw_peak_contact_force":0.1629,"tcp_end":[0.49013,-0.01537,0.0453],"tcp_start":[0.49852,-0.01543,0.05449],"tcp_to_object_dist_end":0.02373,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":38.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5006,-0.01592,0.1242],"object_pos_start":[0.50374,-0.01566,0.02585],"object_to_goal_dist_end":0.2533,"object_to_goal_dist_start":0.31237,"object_z_max":0.12407,"peak_contact_force":0.07886,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":40806.0,"raw_peak_contact_force":0.40634,"tcp_end":[0.49437,-0.0155,0.14991],"tcp_start":[0.49013,-0.01537,0.0453],"tcp_to_object_dist_end":0.02646,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.55345,0.12775,0.02201],"object_pos_start":[0.5006,-0.01592,0.1242],"object_to_goal_dist_end":0.23623,"object_to_goal_dist_start":0.2533,"object_z_max":0.17737,"peak_contact_force":0.29929,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":35139.0,"raw_peak_contact_force":1.79875,"tcp_end":[0.55052,0.11965,0.23615],"tcp_start":[0.49437,-0.0155,0.14991],"tcp_to_object_dist_end":0.21431,"terminated_normally":true,"termination_reason":"time_limit"}],"success":true}]}
```