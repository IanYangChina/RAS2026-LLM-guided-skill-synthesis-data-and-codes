## Search State

- **Seed**: 6
- **Iteration**: 1 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 0 | approach → descend → grasp → lift → release | linear_cartesian | linear_cartesian | — | linear_cartesian | — | force_threshold_switch | admittance_control | position_control | position_control | position_control | pose_tolerance | contact_detected | time_limit | pose_tolerance | time_limit | 3 | 0.3184 | 0.17 | ✅ accepted |

**Proposal policy**: task_score is 0.17 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
| `object` | offset from object initial position (0.5038164351471943, -0.015672913018666156, 0.03) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.5869067239795378, 0.18744967655878825, 0.24811674852797) | final destination targets |
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

## Current Skill (Q=0.318) — your mutation base

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
    approach_height:
      type: scalar
      range:
      - 0.05
      - 0.3
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1
- id: descend_1
  type: descend
  generator: linear_cartesian
  control: admittance_control
  termination: contact_detected
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
- id: release_1
  type: release
  control: position_control
  termination: time_limit
  end_effector_action: open

```

## Design Metrics

- **Composite score**: 0.318
- **task_score** (E): 0.166
- **fitness_score**: 0.558  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.240

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.2031 |
| descend_1 | 1.00 | 1.00 | 0.0594 |
| grasp_1 | 1.00 | 1.00 | 0.0120 |
| lift_1 | 1.00 | 1.00 | 0.1616 |
| release_1 | 1.00 | 1.00 | 0.0255 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.496, 0.022, 0.102) | (0.500, 0.024, 0.030)→(0.500, 0.024, 0.026) | 0.269→0.271 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.496, 0.022, 0.102)→(0.494, 0.024, 0.042) | (0.500, 0.024, 0.026)→(0.500, 0.024, 0.026) | 0.271→0.271 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_1 | grasp | 1.00 / step_budget | (0.494, 0.024, 0.042)→(0.486, 0.023, 0.034) | (0.500, 0.024, 0.026)→(0.500, 0.024, 0.026) | 0.271→0.272 | 1.00 / 42.333 | 0.145 | 0.184 |
| lift_1 | lift | 1.00 / step_budget | (0.486, 0.023, 0.034)→(0.494, 0.024, 0.195) | (0.500, 0.024, 0.026)→(0.504, 0.024, 0.179) | 0.272→0.205 | 1.00 / 37.000 | 0.082 | 0.596 |
| release_1 | release | 1.00 / step_budget | (0.494, 0.024, 0.195)→(0.489, 0.023, 0.220) | (0.504, 0.024, 0.179)→(0.498, 0.022, 0.021) | 0.205→0.276 | 1.00 / 2.000 | 0.139 | 1.566 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.239
- phase_score: 0.258
- phase_breakdown.transport_arc_score: 0.000
- phase_breakdown.approach_1_score: 0.464
- phase_breakdown.release_1_score: 0.019
- phase_breakdown.grasp_1_score: 1.000
- phase_breakdown.descend_1_score: 0.816
- grasp_place_fitness: 0.596

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.596
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.239
- **Median Q (composite search score)**: 0.303
- **K-run variance**: 0.0007
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 10.0
- **Final σ (mean)**: 0.414


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.11299,"average_solve_count":177.0,"average_success_count":177.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.05922,"approach_1.speed":0.03654,"grasp_1.grip_force":17.64328},"optimized_scores":{"best_composite_score":0.29683,"best_fitness_score":0.53683,"best_task_score":0.12139},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":110.0,"contact_point_centroid":[0.49503,-0.01445,-0.01144],"force_p95":1.43348,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.57386,"mean_force":0.67648,"phase_index":4.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.49341,-0.0157,0.21156]},{"body_a":"world","body_b":"grasp_target","contact_count":132.0,"contact_point_centroid":[0.50057,-0.0154,-0.00109],"force_p95":0.41283,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.60835,"mean_force":0.08295,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48899,-0.01551,0.03444]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":20509.0,"contact_point_centroid":[0.49324,0.00341,0.11232],"force_p95":0.07404,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32047,"mean_force":0.05005,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49195,-0.01562,0.11049]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":18169.0,"contact_point_centroid":[0.49246,-0.03479,0.11342],"force_p95":0.07931,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.3161,"mean_force":0.05529,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49196,-0.01562,0.11075]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.5038,-0.01578,-0.00202],"force_p95":0.13103,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.14429,"mean_force":0.12482,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49153,-0.01553,0.03405]},{"body_a":"world","body_b":"grasp_target","contact_count":3112.0,"contact_point_centroid":[0.50382,-0.01567,-0.00195],"force_p95":0.1276,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12278,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.4983,-0.00728,0.18334]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1163.0,"contact_point_centroid":[0.49773,-0.03486,0.19519],"force_p95":0.07383,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12779,"mean_force":0.04554,"phase_index":4.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.49704,-0.01575,0.19307]},{"body_a":"world","body_b":"grasp_target","contact_count":2384.0,"contact_point_centroid":[0.50382,-0.01567,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49748,-0.0153,0.04868]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1122.0,"contact_point_centroid":[0.4987,0.00339,0.19504],"force_p95":0.07756,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1129,"mean_force":0.04693,"phase_index":4.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.49696,-0.01575,0.19294]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4142.0,"contact_point_centroid":[0.48965,-0.03476,0.03526],"force_p95":0.07916,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09371,"mean_force":0.05174,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49029,-0.01552,0.03273]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5098.0,"contact_point_centroid":[0.49135,0.00354,0.03443],"force_p95":0.0684,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08951,"mean_force":0.04296,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49028,-0.01552,0.03273]}],"total_contact_groups":11},"final_pose_error":0.03133,"key_states":{"actual_goal_position":[0.58691,0.18745,0.24812],"final_object_position":[0.50294,-0.01664,0.0215],"final_tcp_position":[0.49832,-0.01577,0.19504],"realised_goal_position":[0.58691,0.18745,0.24812],"realised_object_initial_position":[0.50382,-0.01567,0.03]},"peak_contact_force":1.57386,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":779.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.03],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.30942,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3112.0,"raw_peak_contact_force":0.13845,"tcp_end":[0.49896,-0.01472,0.06783],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.04211,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":596.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.12262,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2384.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.49854,-0.01559,0.04153],"tcp_start":[0.49896,-0.01472,0.06783],"tcp_to_object_dist_end":0.01639,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":42.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50368,-0.01586,0.0259],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31248,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.13129,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11040.0,"raw_peak_contact_force":0.14429,"tcp_end":[0.49025,-0.01552,0.03269],"tcp_start":[0.49854,-0.01559,0.04153],"tcp_to_object_dist_end":0.01505,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50795,-0.01612,0.18043],"object_pos_start":[0.50368,-0.01586,0.0259],"object_to_goal_dist_end":0.2286,"object_to_goal_dist_start":0.31248,"object_z_max":0.18024,"peak_contact_force":0.08296,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":38810.0,"raw_peak_contact_force":0.60835,"tcp_end":[0.49832,-0.01577,0.19504],"tcp_start":[0.49025,-0.01552,0.03269],"tcp_to_object_dist_end":0.0175,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50294,-0.01664,0.0215],"object_pos_start":[0.50795,-0.01612,0.18043],"object_to_goal_dist_end":0.31632,"object_to_goal_dist_start":0.2286,"object_z_max":0.18057,"peak_contact_force":0.14458,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2395.0,"raw_peak_contact_force":1.57386,"tcp_end":[0.49333,-0.0157,0.21996],"tcp_start":[0.49832,-0.01577,0.19504],"tcp_to_object_dist_end":0.19869,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.11299,"average_solve_count":177.0,"average_success_count":177.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.06001,"approach_1.speed":0.03387,"grasp_1.grip_force":29.33847},"optimized_scores":{"best_composite_score":0.35571,"best_fitness_score":0.59571,"best_task_score":0.23945},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":110.0,"contact_point_centroid":[0.50207,0.03927,-0.01138],"force_p95":1.45139,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.52051,"mean_force":0.65624,"phase_index":4.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.50214,0.03829,0.21083]},{"body_a":"world","body_b":"grasp_target","contact_count":141.0,"contact_point_centroid":[0.50946,0.03779,-0.00119],"force_p95":0.40469,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.62822,"mean_force":0.08474,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49751,0.03839,0.03409]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":17000.0,"contact_point_centroid":[0.50102,0.05763,0.11498],"force_p95":0.08364,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.3374,"mean_force":0.05875,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.50077,0.03843,0.11222]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":20622.0,"contact_point_centroid":[0.50263,0.01951,0.11234],"force_p95":0.07861,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31323,"mean_force":0.04991,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.50066,0.03843,0.11074]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.51256,0.0397,-0.0021],"force_p95":0.15268,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.20383,"mean_force":0.13043,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.50012,0.03862,0.03362]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5037.0,"contact_point_centroid":[0.5005,0.01951,0.03372],"force_p95":0.07319,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17149,"mean_force":0.04306,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49887,0.03852,0.03226]},{"body_a":"world","body_b":"grasp_target","contact_count":3204.0,"contact_point_centroid":[0.51251,0.03972,-0.00195],"force_p95":0.12703,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12278,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50235,0.01836,0.18317]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1059.0,"contact_point_centroid":[0.50585,0.05786,0.19527],"force_p95":0.07924,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12997,"mean_force":0.04925,"phase_index":4.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.50574,0.03862,0.19246]},{"body_a":"world","body_b":"grasp_target","contact_count":2584.0,"contact_point_centroid":[0.51251,0.03972,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50587,0.0384,0.0488]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1226.0,"contact_point_centroid":[0.50825,0.01968,0.19399],"force_p95":0.0753,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11709,"mean_force":0.04366,"phase_index":4.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.50577,0.03862,0.19249]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4201.0,"contact_point_centroid":[0.49906,0.05781,0.03494],"force_p95":0.08509,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09098,"mean_force":0.05188,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49888,0.03852,0.03226]}],"total_contact_groups":11},"final_pose_error":0.03153,"key_states":{"actual_goal_position":[0.62757,0.17252,0.14502],"final_object_position":[0.51771,0.03858,0.01868],"final_tcp_position":[0.50708,0.03871,0.19457],"realised_goal_position":[0.62757,0.17252,0.14502],"realised_object_initial_position":[0.51251,0.03972,0.03]},"peak_contact_force":1.52051,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":802.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.03],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21001,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3204.0,"raw_peak_contact_force":0.13845,"tcp_end":[0.50714,0.03713,0.0679],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.04231,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":646.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2584.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.50718,0.03919,0.04135],"tcp_start":[0.50714,0.03713,0.0679],"tcp_to_object_dist_end":0.01624,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":42.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51247,0.03908,0.02564],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21286,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.15116,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11038.0,"raw_peak_contact_force":0.20383,"tcp_end":[0.49884,0.03851,0.03222],"tcp_start":[0.50718,0.03919,0.04135],"tcp_to_object_dist_end":0.01515,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51675,0.03953,0.17982],"object_pos_start":[0.51247,0.03908,0.02564],"object_to_goal_dist_end":0.17657,"object_to_goal_dist_start":0.21286,"object_z_max":0.17963,"peak_contact_force":0.08109,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":37763.0,"raw_peak_contact_force":0.62822,"tcp_end":[0.50708,0.03871,0.19457],"tcp_start":[0.49884,0.03851,0.03222],"tcp_to_object_dist_end":0.01766,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51771,0.03858,0.01868],"object_pos_start":[0.51675,0.03953,0.17982],"object_to_goal_dist_end":0.21441,"object_to_goal_dist_start":0.17657,"object_z_max":0.17996,"peak_contact_force":0.07858,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2395.0,"raw_peak_contact_force":1.52051,"tcp_end":[0.50206,0.03829,0.21923],"tcp_start":[0.50708,0.03871,0.19457],"tcp_to_object_dist_end":0.20116,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.46218,"average_solve_count":119.0,"average_success_count":119.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.16109,"approach_1.speed":0.05432,"grasp_1.grip_force":18.5577},"optimized_scores":{"best_composite_score":0.30252,"best_fitness_score":0.54252,"best_task_score":0.1379},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":171.0,"contact_point_centroid":[0.46485,0.04699,-0.00856],"force_p95":1.39555,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.60357,"mean_force":0.4359,"phase_index":4.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.47265,0.04708,0.21278]},{"body_a":"world","body_b":"grasp_target","contact_count":138.0,"contact_point_centroid":[0.47985,0.0466,-0.00119],"force_p95":0.34764,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55161,"mean_force":0.07854,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46833,0.04716,0.03791]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":17000.0,"contact_point_centroid":[0.47121,0.06644,0.11752],"force_p95":0.08494,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32299,"mean_force":0.0586,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.47141,0.04723,0.1148]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":20910.0,"contact_point_centroid":[0.4734,0.02833,0.11521],"force_p95":0.07844,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29463,"mean_force":0.04912,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.47133,0.04723,0.11367]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.48276,0.0487,-0.00211],"force_p95":0.15488,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.20467,"mean_force":0.13112,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47081,0.04743,0.03727]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5261.0,"contact_point_centroid":[0.47114,0.02829,0.0373],"force_p95":0.07374,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17737,"mean_force":0.04135,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46961,0.04731,0.03604]},{"body_a":"world","body_b":"grasp_target","contact_count":1832.0,"contact_point_centroid":[0.4827,0.04873,-0.00192],"force_p95":0.13357,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12289,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48957,0.02115,0.23484]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1056.0,"contact_point_centroid":[0.47578,0.0667,0.19644],"force_p95":0.07992,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13212,"mean_force":0.04937,"phase_index":4.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.47613,0.04747,0.19362]},{"body_a":"world","body_b":"grasp_target","contact_count":2836.0,"contact_point_centroid":[0.4827,0.04873,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.4777,0.0459,0.10116]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1226.0,"contact_point_centroid":[0.47883,0.02857,0.1951],"force_p95":0.07607,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11903,"mean_force":0.04362,"phase_index":4.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.47615,0.04747,0.19365]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4203.0,"contact_point_centroid":[0.46943,0.06663,0.03847],"force_p95":0.08825,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09451,"mean_force":0.05204,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46961,0.04731,0.03604]}],"total_contact_groups":11},"final_pose_error":0.03051,"key_states":{"actual_goal_position":[0.58187,0.22885,0.23048],"final_object_position":[0.47356,0.04551,0.02319],"final_tcp_position":[0.47744,0.04758,0.19555],"realised_goal_position":[0.58187,0.22885,0.23048],"realised_object_initial_position":[0.4827,0.04873,0.03]},"peak_contact_force":1.60357,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":459.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.03],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28719,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1832.0,"raw_peak_contact_force":0.13845,"tcp_end":[0.48073,0.04366,0.16937],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.14346,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":709.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2836.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.47766,0.0481,0.04433],"tcp_start":[0.48073,0.04366,0.16937],"tcp_to_object_dist_end":0.019,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.4827,0.04803,0.0256],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.2907,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.15303,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11264.0,"raw_peak_contact_force":0.20467,"tcp_end":[0.46958,0.04731,0.03601],"tcp_start":[0.47766,0.0481,0.04433],"tcp_to_object_dist_end":0.01676,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.48615,0.04849,0.17798],"object_pos_start":[0.4827,0.04803,0.0256],"object_to_goal_dist_end":0.21084,"object_to_goal_dist_start":0.2907,"object_z_max":0.17779,"peak_contact_force":0.08144,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":38048.0,"raw_peak_contact_force":0.55161,"tcp_end":[0.47744,0.04758,0.19555],"tcp_start":[0.46958,0.04731,0.03601],"tcp_to_object_dist_end":0.01963,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.47356,0.04551,0.02319],"object_pos_start":[0.48615,0.04849,0.17798],"object_to_goal_dist_end":0.29718,"object_to_goal_dist_start":0.21084,"object_z_max":0.17811,"peak_contact_force":0.19479,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2453.0,"raw_peak_contact_force":1.60357,"tcp_end":[0.47257,0.04708,0.221],"tcp_start":[0.47744,0.04758,0.19555],"tcp_to_object_dist_end":0.19782,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```