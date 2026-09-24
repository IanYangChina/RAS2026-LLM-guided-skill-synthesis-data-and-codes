## Search State

- **Seed**: 4
- **Iteration**: 8 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 7 | approach → descend → grasp → lift → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | force_threshold_switch | position_control | position_control | position_control | admittance_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | time_limit | 4 | 0.3576 | 0.37 | ❌ rejected |
| 6 | approach → descend → grasp → lift → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | force_threshold_switch | position_control | position_control | position_control | admittance_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | time_limit | 4 | 0.3576 | 0.37 | ❌ rejected |
| 5 | approach → descend → grasp → lift → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | force_threshold_switch | position_control | position_control | position_control | admittance_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | time_limit | 4 | 0.3576 | 0.37 | ❌ rejected |
| 4 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 8 | 0.0849 | 0.32 | ❌ rejected |
| 3 | approach → descend → grasp → lift → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | force_threshold_switch | position_control | position_control | position_control | admittance_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | time_limit | 4 | 0.3579 | 0.37 | ❌ rejected |

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
- **task_score** (E): 0.367
- **fitness_score**: 0.648  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.290

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1664 |
| descend_1 | 1.00 | 1.00 | 0.0833 |
| grasp_1 | 1.00 | 1.00 | 0.0131 |
| lift_1 | 0.33 | 1.00 | 0.1170 |
| release_1 | 1.00 | 1.00 | 0.1615 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.520, 0.005, 0.137) | (0.526, 0.005, 0.030)→(0.526, 0.005, 0.026) | 0.246→0.249 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.520, 0.005, 0.137)→(0.521, 0.005, 0.054) | (0.526, 0.005, 0.026)→(0.526, 0.005, 0.026) | 0.249→0.249 | 1.00 / 4.000 | 11.588 | 0.123 |
| grasp_1 | grasp | 1.00 / step_budget | (0.521, 0.005, 0.054)→(0.512, 0.005, 0.044) | (0.526, 0.005, 0.026)→(0.526, 0.005, 0.026) | 0.249→0.249 | 1.00 / 46.000 | 0.139 | 0.174 |
| lift_1 | lift | 0.33 / step_budget | (0.512, 0.005, 0.044)→(0.518, 0.005, 0.161) | (0.526, 0.005, 0.026)→(0.524, 0.005, 0.136) | 0.249→0.204 | 1.00 / 38.000 | 0.079 | 0.428 |
| release_1 | release | 1.00 / time_limit | (0.518, 0.005, 0.161)→(0.588, 0.140, 0.191) | (0.524, 0.005, 0.136)→(0.584, 0.149, 0.025) | 0.204→0.163 | 1.00 / 3.667 | 0.171 | 1.406 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.571
- phase_score: 0.330
- phase_breakdown.transport_arc_score: 0.000
- phase_breakdown.release_1_score: 0.583
- phase_breakdown.grasp_1_score: 1.000
- phase_breakdown.descend_1_score: 0.869
- phase_breakdown.approach_1_score: 0.117
- grasp_place_fitness: 0.749

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.749
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.571
- **Median Q (composite search score)**: 0.336
- **K-run variance**: 0.0058
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.222


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.5,"average_solve_count":164.0,"average_success_count":164.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.05105,"descend_1.depth":0.0537,"grasp_1.grip_force":17.23793,"lift_1.speed":0.08597},"optimized_scores":{"best_composite_score":0.33649,"best_fitness_score":0.62649,"best_task_score":0.32379},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":238.0,"contact_point_centroid":[0.61676,0.1415,-0.00608],"force_p95":0.92227,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.59499,"mean_force":0.29189,"phase_index":4.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.62386,0.13224,0.1978]},{"body_a":"world","body_b":"grasp_target","contact_count":168.0,"contact_point_centroid":[0.54094,0.00089,-0.00114],"force_p95":0.26629,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.44979,"mean_force":0.08184,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52818,0.0008,0.04505]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":19862.0,"contact_point_centroid":[0.53184,0.02002,0.11221],"force_p95":0.07367,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31173,"mean_force":0.05131,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.53113,0.00087,0.10942]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":20446.0,"contact_point_centroid":[0.53153,-0.01826,0.10992],"force_p95":0.0742,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28467,"mean_force":0.05014,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.53098,0.00086,0.10752]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":17940.0,"contact_point_centroid":[0.57553,0.08131,0.17855],"force_p95":0.08725,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27589,"mean_force":0.0553,"phase_index":4.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.57722,0.06251,0.17809]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":16500.0,"contact_point_centroid":[0.57596,0.04031,0.17768],"force_p95":0.1079,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26123,"mean_force":0.06046,"phase_index":4.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.57503,0.05939,0.17797]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.54431,0.00116,-0.00203],"force_p95":0.13133,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.15483,"mean_force":0.12547,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53089,0.00086,0.04502]},{"body_a":"world","body_b":"grasp_target","contact_count":2396.0,"contact_point_centroid":[0.54431,0.00113,-0.00194],"force_p95":0.13076,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12283,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51702,0.00047,0.21768]},{"body_a":"world","body_b":"grasp_target","contact_count":1012.0,"contact_point_centroid":[0.54431,0.00113,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.53634,0.00097,0.09485]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4149.0,"contact_point_centroid":[0.5309,0.02013,0.04609],"force_p95":0.07646,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09636,"mean_force":0.05216,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52964,0.00083,0.04354]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5327.0,"contact_point_centroid":[0.53024,-0.0182,0.04617],"force_p95":0.06266,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08976,"mean_force":0.04074,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52964,0.00083,0.04354]}],"total_contact_groups":11},"final_pose_error":0.03411,"key_states":{"actual_goal_position":[0.64762,0.15808,0.1911],"final_object_position":[0.61751,0.14082,0.02555],"final_tcp_position":[0.62686,0.13293,0.18114],"realised_goal_position":[0.64762,0.15808,0.1911],"realised_object_initial_position":[0.54431,0.00113,0.03]},"peak_contact_force":34.51877,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":600.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.03],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.24751,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2396.0,"raw_peak_contact_force":0.13845,"tcp_end":[0.53689,0.00098,0.13641],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.11064,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":253.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":34.51877,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1012.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.53833,0.00101,0.05397],"tcp_start":[0.53689,0.00098,0.13641],"tcp_to_object_dist_end":0.02858,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54422,0.00112,0.02586],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25028,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.13103,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11276.0,"raw_peak_contact_force":0.15483,"tcp_end":[0.52961,0.00083,0.0435],"tcp_start":[0.53833,0.00101,0.05397],"tcp_to_object_dist_end":0.02291,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":38.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.54475,0.00112,0.15691],"object_pos_start":[0.54422,0.00112,0.02586],"object_to_goal_dist_end":0.19076,"object_to_goal_dist_start":0.25028,"object_z_max":0.15675,"peak_contact_force":0.0781,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":40476.0,"raw_peak_contact_force":0.44979,"tcp_end":[0.5373,0.00099,0.18095],"tcp_start":[0.52961,0.00083,0.0435],"tcp_to_object_dist_end":0.02516,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.61751,0.14082,0.02555],"object_pos_start":[0.54475,0.00112,0.15691],"object_to_goal_dist_end":0.16915,"object_to_goal_dist_start":0.19076,"object_z_max":0.15702,"peak_contact_force":0.0897,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":34678.0,"raw_peak_contact_force":1.59499,"tcp_end":[0.6238,0.1322,0.20677],"tcp_start":[0.5373,0.00099,0.18095],"tcp_to_object_dist_end":0.18153,"terminated_normally":true,"termination_reason":"time_limit"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.77931,"average_solve_count":145.0,"average_success_count":145.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.07131,"descend_1.depth":0.08708,"grasp_1.grip_force":19.90772,"lift_1.speed":0.06667},"optimized_scores":{"best_composite_score":0.45945,"best_fitness_score":0.74945,"best_task_score":0.57069},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":368.0,"contact_point_centroid":[0.58247,0.17872,-0.00325],"force_p95":0.55544,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.82366,"mean_force":0.18485,"phase_index":4.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.58879,0.1677,0.11583]},{"body_a":"world","body_b":"grasp_target","contact_count":175.0,"contact_point_centroid":[0.52655,0.02884,-0.0012],"force_p95":0.27317,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.42864,"mean_force":0.0815,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51469,0.02942,0.04554]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":16678.0,"contact_point_centroid":[0.54788,0.10955,0.12789],"force_p95":0.09693,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32162,"mean_force":0.05903,"phase_index":4.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.55054,0.09092,0.12765]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":19296.0,"contact_point_centroid":[0.51672,0.04866,0.09996],"force_p95":0.07469,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27951,"mean_force":0.0522,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51648,0.02948,0.09704]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":21057.0,"contact_point_centroid":[0.51764,0.01039,0.09648],"force_p95":0.07614,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26391,"mean_force":0.04861,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51629,0.02947,0.09468]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":15320.0,"contact_point_centroid":[0.55136,0.0708,0.12695],"force_p95":0.10939,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26013,"mean_force":0.06521,"phase_index":4.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.54992,0.08972,0.12806]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53054,0.03083,-0.00211],"force_p95":0.15292,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.20405,"mean_force":0.1309,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51743,0.02961,0.04537]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5782.0,"contact_point_centroid":[0.51716,0.01038,0.04661],"force_p95":0.06401,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1409,"mean_force":0.0381,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.5162,0.02953,0.04394]},{"body_a":"world","body_b":"grasp_target","contact_count":2212.0,"contact_point_centroid":[0.5305,0.03079,-0.00194],"force_p95":0.13205,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12285,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51076,0.01385,0.21803]},{"body_a":"world","body_b":"grasp_target","contact_count":1024.0,"contact_point_centroid":[0.5305,0.03079,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.52318,0.02906,0.09516]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4698.0,"contact_point_centroid":[0.51635,0.04885,0.04763],"force_p95":0.07523,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07809,"mean_force":0.04683,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.5162,0.02953,0.04395]}],"total_contact_groups":11},"final_pose_error":0.01444,"key_states":{"actual_goal_position":[0.60153,0.17858,0.10809],"final_object_position":[0.58212,0.17975,0.02623],"final_tcp_position":[0.59241,0.16868,0.10286],"realised_goal_position":[0.60153,0.17858,0.10809],"realised_object_initial_position":[0.5305,0.03079,0.03]},"peak_contact_force":0.82366,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":554.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.03],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18162,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2212.0,"raw_peak_contact_force":0.13845,"tcp_end":[0.5241,0.0282,0.13701],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.11121,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":256.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1024.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.52476,0.03009,0.05394],"tcp_start":[0.5241,0.0282,0.13701],"tcp_to_object_dist_end":0.02851,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":47.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53048,0.03026,0.0256],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18399,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.15142,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12280.0,"raw_peak_contact_force":0.20405,"tcp_end":[0.51617,0.02953,0.04391],"tcp_start":[0.52476,0.03009,0.05394],"tcp_to_object_dist_end":0.02325,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":38.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.52789,0.03035,0.12779],"object_pos_start":[0.53048,0.03026,0.0256],"object_to_goal_dist_end":0.16668,"object_to_goal_dist_start":0.18399,"object_z_max":0.12767,"peak_contact_force":0.08056,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":40528.0,"raw_peak_contact_force":0.42864,"tcp_end":[0.52113,0.02973,0.15247],"tcp_start":[0.51617,0.02953,0.04391],"tcp_to_object_dist_end":0.0256,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.58212,0.17975,0.02623],"object_pos_start":[0.52789,0.03035,0.12779],"object_to_goal_dist_end":0.08414,"object_to_goal_dist_start":0.16668,"object_z_max":0.12783,"peak_contact_force":0.13515,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":32366.0,"raw_peak_contact_force":0.82366,"tcp_end":[0.58862,0.16759,0.12911],"tcp_start":[0.52113,0.02973,0.15247],"tcp_to_object_dist_end":0.1038,"terminated_normally":true,"termination_reason":"time_limit"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.77778,"average_solve_count":144.0,"average_success_count":144.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.07113,"descend_1.depth":0.04494,"grasp_1.grip_force":18.04882,"lift_1.speed":0.06436},"optimized_scores":{"best_composite_score":0.27689,"best_fitness_score":0.56689,"best_task_score":0.20694},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":177.0,"contact_point_centroid":[0.54411,0.12967,-0.0077],"force_p95":1.24497,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.7988,"mean_force":0.41298,"phase_index":4.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.55058,0.11968,0.22829]},{"body_a":"world","body_b":"grasp_target","contact_count":170.0,"contact_point_centroid":[0.50056,-0.0152,-0.00113],"force_p95":0.27103,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.4064,"mean_force":0.07349,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48876,-0.01536,0.04697]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":20721.0,"contact_point_centroid":[0.49115,0.00371,0.09661],"force_p95":0.07396,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26547,"mean_force":0.04916,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49003,-0.01541,0.0952]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":19919.0,"contact_point_centroid":[0.49057,-0.03459,0.09836],"force_p95":0.0726,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25778,"mean_force":0.05046,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49009,-0.01542,0.09596]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":17553.0,"contact_point_centroid":[0.51878,0.06695,0.17494],"force_p95":0.09524,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21742,"mean_force":0.05639,"phase_index":4.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.51996,0.04808,0.17504]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":17420.0,"contact_point_centroid":[0.52216,0.02901,0.1749],"force_p95":0.09976,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21359,"mean_force":0.05652,"phase_index":4.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.51984,0.0478,0.17491]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50382,-0.01574,-0.00203],"force_p95":0.13438,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.16289,"mean_force":0.12564,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49136,-0.01538,0.04662]},{"body_a":"world","body_b":"grasp_target","contact_count":2028.0,"contact_point_centroid":[0.50382,-0.01567,-0.00193],"force_p95":0.13256,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12287,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49869,-0.00697,0.21966]},{"body_a":"world","body_b":"grasp_target","contact_count":1056.0,"contact_point_centroid":[0.50382,-0.01567,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49779,-0.01485,0.09632]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5558.0,"contact_point_centroid":[0.49092,0.00386,0.0474],"force_p95":0.06421,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08941,"mean_force":0.03993,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49016,-0.01537,0.04532]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5123.0,"contact_point_centroid":[0.49017,-0.03464,0.04879],"force_p95":0.06791,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08189,"mean_force":0.04272,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49016,-0.01537,0.04533]}],"total_contact_groups":11},"final_pose_error":0.08472,"key_states":{"actual_goal_position":[0.58691,0.18745,0.24812],"final_object_position":[0.5534,0.12722,0.0221],"final_tcp_position":[0.55319,0.12027,0.20904],"realised_goal_position":[0.58691,0.18745,0.24812],"realised_object_initial_position":[0.50382,-0.01567,0.03]},"peak_contact_force":1.7988,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":508.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.03],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.30942,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2028.0,"raw_peak_contact_force":0.13845,"tcp_end":[0.49952,-0.01431,0.13884],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.11291,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":264.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1056.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.49852,-0.01543,0.05448],"tcp_start":[0.49952,-0.01431,0.13884],"tcp_to_object_dist_end":0.02895,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":48.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50374,-0.01566,0.02585],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31237,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.13461,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12481.0,"raw_peak_contact_force":0.16289,"tcp_end":[0.49013,-0.01537,0.04529],"tcp_start":[0.49852,-0.01543,0.05448],"tcp_to_object_dist_end":0.02373,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":38.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5006,-0.01592,0.1242],"object_pos_start":[0.50374,-0.01566,0.02585],"object_to_goal_dist_end":0.2533,"object_to_goal_dist_start":0.31237,"object_z_max":0.12408,"peak_contact_force":0.07886,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":40810.0,"raw_peak_contact_force":0.4064,"tcp_end":[0.49437,-0.0155,0.1499],"tcp_start":[0.49013,-0.01537,0.04529],"tcp_to_object_dist_end":0.02645,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5534,0.12722,0.0221],"object_pos_start":[0.5006,-0.01592,0.1242],"object_to_goal_dist_end":0.2363,"object_to_goal_dist_start":0.2533,"object_z_max":0.17737,"peak_contact_force":0.28734,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":35150.0,"raw_peak_contact_force":1.7988,"tcp_end":[0.55052,0.11965,0.23615],"tcp_start":[0.49437,-0.0155,0.1499],"tcp_to_object_dist_end":0.21421,"terminated_normally":true,"termination_reason":"time_limit"}],"success":true}]}
```