## Search State

- **Seed**: 4
- **Iteration**: 3 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 2 | approach → descend → grasp → lift → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | force_threshold_switch | position_control | position_control | position_control | admittance_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | time_limit | 4 | 0.3576 | 0.37 | ❌ rejected |
| 1 | approach → descend → grasp → lift → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | force_threshold_switch | position_control | position_control | position_control | admittance_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | time_limit | 4 | 0.3580 | 0.37 | ✅ accepted |
| 0 | approach → descend → grasp → lift → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | force_threshold_switch | position_control | position_control | position_control | admittance_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | time_limit | 4 | 0.3576 | 0.37 | ✅ accepted |

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
| lift_1 | 0.33 | 1.00 | 0.1164 |
| release_1 | 1.00 | 1.00 | 0.1617 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.520, 0.005, 0.137) | (0.526, 0.005, 0.030)→(0.526, 0.005, 0.026) | 0.246→0.249 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.520, 0.005, 0.137)→(0.521, 0.005, 0.054) | (0.526, 0.005, 0.026)→(0.526, 0.005, 0.026) | 0.249→0.249 | 1.00 / 4.000 | 11.589 | 0.123 |
| grasp_1 | grasp | 1.00 / step_budget | (0.521, 0.005, 0.054)→(0.512, 0.005, 0.044) | (0.526, 0.005, 0.026)→(0.526, 0.005, 0.026) | 0.249→0.249 | 1.00 / 46.000 | 0.139 | 0.174 |
| lift_1 | lift | 0.33 / step_budget | (0.512, 0.005, 0.044)→(0.518, 0.005, 0.160) | (0.526, 0.005, 0.026)→(0.524, 0.005, 0.136) | 0.249→0.204 | 1.00 / 38.000 | 0.079 | 0.428 |
| release_1 | release | 1.00 / time_limit | (0.518, 0.005, 0.160)→(0.588, 0.140, 0.190) | (0.524, 0.005, 0.136)→(0.585, 0.150, 0.025) | 0.204→0.163 | 1.00 / 3.667 | 0.182 | 1.416 |

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
- **Final σ (mean)**: 0.243


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.73154,"average_solve_count":149.0,"average_success_count":149.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.06493,"descend_1.depth":0.04894,"grasp_1.grip_force":25.9894,"lift_1.speed":0.08583},"optimized_scores":{"best_composite_score":0.3365,"best_fitness_score":0.6265,"best_task_score":0.32381},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":239.0,"contact_point_centroid":[0.61662,0.14156,-0.00602],"force_p95":0.91444,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.595,"mean_force":0.29075,"phase_index":4.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.62386,0.13224,0.19777]},{"body_a":"world","body_b":"grasp_target","contact_count":168.0,"contact_point_centroid":[0.54094,0.00089,-0.00114],"force_p95":0.26628,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.44976,"mean_force":0.08184,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52818,0.0008,0.04505]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":19817.0,"contact_point_centroid":[0.53184,0.02003,0.11224],"force_p95":0.07367,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31172,"mean_force":0.0514,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.53113,0.00087,0.10943]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":20481.0,"contact_point_centroid":[0.53153,-0.01826,0.10992],"force_p95":0.07416,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28466,"mean_force":0.05009,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.53098,0.00086,0.10752]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":17936.0,"contact_point_centroid":[0.57552,0.0813,0.17854],"force_p95":0.08727,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27572,"mean_force":0.05531,"phase_index":4.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.57722,0.06251,0.17809]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":16499.0,"contact_point_centroid":[0.57596,0.04031,0.17768],"force_p95":0.1079,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26125,"mean_force":0.06046,"phase_index":4.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.57503,0.05938,0.17797]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.54431,0.00116,-0.00203],"force_p95":0.13134,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.15484,"mean_force":0.12547,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53089,0.00086,0.04502]},{"body_a":"world","body_b":"grasp_target","contact_count":2320.0,"contact_point_centroid":[0.54431,0.00113,-0.00194],"force_p95":0.13105,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12284,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51705,0.00047,0.21764]},{"body_a":"world","body_b":"grasp_target","contact_count":1012.0,"contact_point_centroid":[0.54431,0.00113,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.53634,0.00097,0.09486]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4149.0,"contact_point_centroid":[0.5309,0.02013,0.0461],"force_p95":0.07646,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09636,"mean_force":0.05216,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52964,0.00083,0.04354]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5327.0,"contact_point_centroid":[0.53024,-0.0182,0.04617],"force_p95":0.06266,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08976,"mean_force":0.04074,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52964,0.00083,0.04354]}],"total_contact_groups":11},"final_pose_error":0.03411,"key_states":{"actual_goal_position":[0.64762,0.15808,0.1911],"final_object_position":[0.61765,0.14073,0.02555],"final_tcp_position":[0.62686,0.13293,0.18114],"realised_goal_position":[0.64762,0.15808,0.1911],"realised_object_initial_position":[0.54431,0.00113,0.03]},"peak_contact_force":34.52171,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":581.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.03],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.24751,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2320.0,"raw_peak_contact_force":0.13845,"tcp_end":[0.53688,0.00098,0.13641],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.11064,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":253.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":34.52171,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1012.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.53832,0.00101,0.05397],"tcp_start":[0.53688,0.00098,0.13641],"tcp_to_object_dist_end":0.02858,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54422,0.00112,0.02586],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25028,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.13103,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11276.0,"raw_peak_contact_force":0.15484,"tcp_end":[0.52961,0.00083,0.0435],"tcp_start":[0.53832,0.00101,0.05397],"tcp_to_object_dist_end":0.02291,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":38.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.54474,0.00112,0.15691],"object_pos_start":[0.54422,0.00112,0.02586],"object_to_goal_dist_end":0.19076,"object_to_goal_dist_start":0.25028,"object_z_max":0.15675,"peak_contact_force":0.07809,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":40466.0,"raw_peak_contact_force":0.44976,"tcp_end":[0.5373,0.00099,0.18095],"tcp_start":[0.52961,0.00083,0.0435],"tcp_to_object_dist_end":0.02517,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.61765,0.14073,0.02555],"object_pos_start":[0.54474,0.00112,0.15691],"object_to_goal_dist_end":0.16914,"object_to_goal_dist_start":0.19076,"object_z_max":0.15701,"peak_contact_force":0.08893,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":34674.0,"raw_peak_contact_force":1.595,"tcp_end":[0.6238,0.1322,0.20677],"tcp_start":[0.5373,0.00099,0.18095],"tcp_to_object_dist_end":0.18152,"terminated_normally":true,"termination_reason":"time_limit"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.67123,"average_solve_count":146.0,"average_success_count":146.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.07018,"descend_1.depth":0.05259,"grasp_1.grip_force":15.33565,"lift_1.speed":0.06725},"optimized_scores":{"best_composite_score":0.45945,"best_fitness_score":0.74945,"best_task_score":0.57068},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":368.0,"contact_point_centroid":[0.58247,0.17873,-0.00325],"force_p95":0.55547,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.82363,"mean_force":0.18485,"phase_index":4.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.58879,0.1677,0.11583]},{"body_a":"world","body_b":"grasp_target","contact_count":175.0,"contact_point_centroid":[0.52655,0.02884,-0.0012],"force_p95":0.27322,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.42873,"mean_force":0.0815,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51469,0.02942,0.04554]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":16689.0,"contact_point_centroid":[0.54789,0.10958,0.12788],"force_p95":0.09686,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32178,"mean_force":0.05899,"phase_index":4.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.55055,0.09094,0.12764]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":19296.0,"contact_point_centroid":[0.51671,0.04866,0.09996],"force_p95":0.07469,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2795,"mean_force":0.0522,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51648,0.02948,0.09704]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":21059.0,"contact_point_centroid":[0.51764,0.01039,0.09648],"force_p95":0.07614,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26393,"mean_force":0.0486,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51629,0.02947,0.09468]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":15311.0,"contact_point_centroid":[0.55134,0.07077,0.12696],"force_p95":0.10944,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26007,"mean_force":0.06525,"phase_index":4.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.5499,0.08969,0.12807]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53054,0.03083,-0.00211],"force_p95":0.15291,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.20403,"mean_force":0.13089,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51743,0.02961,0.04536]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5782.0,"contact_point_centroid":[0.51716,0.01038,0.04661],"force_p95":0.06401,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14094,"mean_force":0.0381,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.5162,0.02953,0.04394]},{"body_a":"world","body_b":"grasp_target","contact_count":2240.0,"contact_point_centroid":[0.5305,0.03079,-0.00194],"force_p95":0.13156,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12284,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51075,0.01384,0.21805]},{"body_a":"world","body_b":"grasp_target","contact_count":1024.0,"contact_point_centroid":[0.5305,0.03079,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.52319,0.02906,0.09514]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4698.0,"contact_point_centroid":[0.51635,0.04885,0.04763],"force_p95":0.07523,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07808,"mean_force":0.04683,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.5162,0.02953,0.04394]}],"total_contact_groups":11},"final_pose_error":0.01444,"key_states":{"actual_goal_position":[0.60153,0.17858,0.10809],"final_object_position":[0.58211,0.17976,0.02623],"final_tcp_position":[0.59241,0.16868,0.10286],"realised_goal_position":[0.60153,0.17858,0.10809],"realised_object_initial_position":[0.5305,0.03079,0.03]},"peak_contact_force":0.82363,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":561.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.03],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18162,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2240.0,"raw_peak_contact_force":0.13845,"tcp_end":[0.52411,0.0282,0.13698],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.11117,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":256.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1024.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.52476,0.03009,0.05393],"tcp_start":[0.52411,0.0282,0.13698],"tcp_to_object_dist_end":0.02851,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":47.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53048,0.03026,0.0256],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18399,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.15142,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12280.0,"raw_peak_contact_force":0.20403,"tcp_end":[0.51617,0.02953,0.0439],"tcp_start":[0.52476,0.03009,0.05393],"tcp_to_object_dist_end":0.02325,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":38.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.52789,0.03035,0.12779],"object_pos_start":[0.53048,0.03026,0.0256],"object_to_goal_dist_end":0.16668,"object_to_goal_dist_start":0.18399,"object_z_max":0.12767,"peak_contact_force":0.08056,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":40530.0,"raw_peak_contact_force":0.42873,"tcp_end":[0.52113,0.02973,0.15246],"tcp_start":[0.51617,0.02953,0.0439],"tcp_to_object_dist_end":0.02559,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.58211,0.17976,0.02623],"object_pos_start":[0.52789,0.03035,0.12779],"object_to_goal_dist_end":0.08414,"object_to_goal_dist_start":0.16668,"object_z_max":0.12783,"peak_contact_force":0.13516,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":32368.0,"raw_peak_contact_force":0.82363,"tcp_end":[0.58862,0.16759,0.12911],"tcp_start":[0.52113,0.02973,0.15246],"tcp_to_object_dist_end":0.1038,"terminated_normally":true,"termination_reason":"time_limit"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.77622,"average_solve_count":143.0,"average_success_count":143.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.07178,"descend_1.depth":0.05075,"grasp_1.grip_force":16.43865,"lift_1.speed":0.06306},"optimized_scores":{"best_composite_score":0.27697,"best_fitness_score":0.56697,"best_task_score":0.2071},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":175.0,"contact_point_centroid":[0.54413,0.13161,-0.00784],"force_p95":1.27293,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.82971,"mean_force":0.42008,"phase_index":4.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.55052,0.11968,0.22759]},{"body_a":"world","body_b":"grasp_target","contact_count":174.0,"contact_point_centroid":[0.50039,-0.01522,-0.00113],"force_p95":0.26257,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.40423,"mean_force":0.07348,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48873,-0.01536,0.04697]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":20723.0,"contact_point_centroid":[0.49107,0.00371,0.09566],"force_p95":0.07392,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26385,"mean_force":0.04913,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48995,-0.01541,0.09425]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":19917.0,"contact_point_centroid":[0.49049,-0.03459,0.09739],"force_p95":0.07258,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25641,"mean_force":0.05044,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49001,-0.01541,0.09499]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":17550.0,"contact_point_centroid":[0.51866,0.06694,0.17364],"force_p95":0.09526,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21688,"mean_force":0.05641,"phase_index":4.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.51984,0.04807,0.17374]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":17415.0,"contact_point_centroid":[0.52203,0.02899,0.17358],"force_p95":0.09976,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1921,"mean_force":0.05647,"phase_index":4.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.5197,0.04777,0.1736]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50382,-0.01574,-0.00203],"force_p95":0.13438,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.16289,"mean_force":0.12564,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49136,-0.01538,0.04662]},{"body_a":"world","body_b":"grasp_target","contact_count":2024.0,"contact_point_centroid":[0.50382,-0.01567,-0.00193],"force_p95":0.13256,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12287,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49869,-0.00697,0.21967]},{"body_a":"world","body_b":"grasp_target","contact_count":1056.0,"contact_point_centroid":[0.50382,-0.01567,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49779,-0.01485,0.09632]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5558.0,"contact_point_centroid":[0.49092,0.00386,0.0474],"force_p95":0.06421,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08941,"mean_force":0.03993,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49016,-0.01537,0.04532]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5123.0,"contact_point_centroid":[0.49017,-0.03464,0.04879],"force_p95":0.06791,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08189,"mean_force":0.04272,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49016,-0.01537,0.04533]}],"total_contact_groups":11},"final_pose_error":0.08503,"key_states":{"actual_goal_position":[0.58691,0.18745,0.24812],"final_object_position":[0.5546,0.12804,0.02182],"final_tcp_position":[0.55313,0.12027,0.20842],"realised_goal_position":[0.58691,0.18745,0.24812],"realised_object_initial_position":[0.50382,-0.01567,0.03]},"peak_contact_force":1.82971,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":507.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.03],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.30942,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2024.0,"raw_peak_contact_force":0.13845,"tcp_end":[0.49952,-0.01431,0.13884],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.11291,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":264.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1056.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.49852,-0.01543,0.05448],"tcp_start":[0.49952,-0.01431,0.13884],"tcp_to_object_dist_end":0.02895,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":48.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50374,-0.01566,0.02585],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31237,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.13461,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12481.0,"raw_peak_contact_force":0.16289,"tcp_end":[0.49013,-0.01537,0.04529],"tcp_start":[0.49852,-0.01543,0.05448],"tcp_to_object_dist_end":0.02373,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":38.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50042,-0.01591,0.1223],"object_pos_start":[0.50374,-0.01566,0.02585],"object_to_goal_dist_end":0.2543,"object_to_goal_dist_start":0.31237,"object_z_max":0.12217,"peak_contact_force":0.07879,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":40814.0,"raw_peak_contact_force":0.40423,"tcp_end":[0.49421,-0.0155,0.14801],"tcp_start":[0.49013,-0.01537,0.04529],"tcp_to_object_dist_end":0.02645,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5546,0.12804,0.02182],"object_pos_start":[0.50042,-0.01591,0.1223],"object_to_goal_dist_end":0.23619,"object_to_goal_dist_start":0.2543,"object_z_max":0.17675,"peak_contact_force":0.32262,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":35140.0,"raw_peak_contact_force":1.82971,"tcp_end":[0.55045,0.11965,0.23553],"tcp_start":[0.49421,-0.0155,0.14801],"tcp_to_object_dist_end":0.21392,"terminated_normally":true,"termination_reason":"time_limit"}],"success":true}]}
```