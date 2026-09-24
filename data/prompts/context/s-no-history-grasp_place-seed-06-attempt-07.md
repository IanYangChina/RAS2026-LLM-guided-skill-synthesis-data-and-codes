## Search State

- **Seed**: 6
- **Iteration**: 8 / 15

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

## Current Skill (Q=-0.142) — your mutation base

```yaml
skill: grasp_place
skill_type: arm_gripper
phases:
- id: align_1
  type: align
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  parameters:
    lateral_offset_y:
      type: scalar
      range:
      - -0.01
      - 0.01
- id: lift_1
  type: lift
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  parameters:
    lift_height:
      type: scalar
      range:
      - 0.05
      - 0.3
- id: push_1
  type: push
  generator: impedance_motion
  control: impedance_control
  termination: pose_tolerance
  parameters:
    push_distance:
      type: scalar
      range:
      - 0.02
      - 0.2
    push_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
- id: approach_1
  type: approach
  generator: arc_cartesian
  control: force_threshold_switch
  termination: pose_tolerance
- id: approach_2
  type: approach
  generator: arc_cartesian
  control: position_control
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
  control: admittance_control
  termination: pose_tolerance
- id: grasp_1
  type: grasp
  control: position_control
  termination: time_limit
  end_effector_action: force_grasp
- id: rotate_1
  type: rotate
  generator: impedance_motion
  control: impedance_control
  termination: pose_tolerance
  parameters:
    yaw_angle:
      type: angle
      range:
      - 0.1
      - 1.57

```

## Design Metrics

- **Composite score**: -0.142
- **task_score** (E): 0.249
- **fitness_score**: 0.338  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.480

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| align_1 | 0.00 | 1.00 | 0.2373 |
| lift_1 | 0.67 | 1.00 | 0.1504 |
| push_1 | 0.33 | 1.00 | 0.1557 |
| approach_1 | 1.00 | 1.00 | 0.1444 |
| approach_2 | 1.00 | 1.00 | 0.0027 |
| descend_1 | 1.00 | 1.00 | 0.0677 |
| grasp_1 | 1.00 | 1.00 | 0.0124 |
| rotate_1 | 0.67 | 1.00 | 0.1619 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| align_1 | align | 0.00 / step_budget | (0.500, -0.000, 0.301)→(0.574, 0.155, 0.137) | (0.500, 0.024, 0.030)→(0.500, 0.024, 0.026) | 0.269→0.271 | 1.00 / 4.000 | 0.123 | 0.138 |
| lift_1 | lift | 0.67 / step_budget | (0.574, 0.155, 0.137)→(0.505, 0.043, 0.186) | (0.500, 0.024, 0.026)→(0.500, 0.024, 0.026) | 0.271→0.271 | 1.00 / 4.000 | 0.123 | 0.123 |
| push_1 | push | 0.33 / step_budget | (0.505, 0.043, 0.186)→(0.571, 0.158, 0.113) | (0.500, 0.024, 0.026)→(0.500, 0.024, 0.026) | 0.271→0.271 | 1.00 / 4.000 | 30.114 | 0.123 |
| approach_1 | approach | 1.00 / step_budget | (0.571, 0.158, 0.113)→(0.501, 0.033, 0.123) | (0.500, 0.024, 0.026)→(0.500, 0.024, 0.026) | 0.271→0.271 | 1.00 / 4.000 | 0.123 | 0.123 |
| approach_2 | approach | 1.00 / step_budget | (0.501, 0.033, 0.123)→(0.499, 0.032, 0.122) | (0.500, 0.024, 0.026)→(0.500, 0.024, 0.026) | 0.271→0.271 | 1.00 / 4.000 | 0.123 | 0.123 |
| descend_1 | descend | 1.00 / step_budget | (0.499, 0.032, 0.122)→(0.495, 0.025, 0.054) | (0.500, 0.024, 0.026)→(0.500, 0.024, 0.026) | 0.271→0.271 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_1 | grasp | 1.00 / step_budget | (0.495, 0.025, 0.054)→(0.487, 0.025, 0.045) | (0.500, 0.024, 0.026)→(0.500, 0.025, 0.026) | 0.271→0.271 | 1.00 / 46.333 | 0.139 | 0.163 |
| rotate_1 | rotate | 0.67 / step_budget | (0.487, 0.025, 0.045)→(0.570, 0.158, 0.081) | (0.500, 0.025, 0.026)→(0.540, 0.125, 0.016) | 0.271→0.216 | 1.00 / 8.667 | 94250.783 | 0.679 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 0.000
- transport_retention: None
- terminal_score: 0.362
- phase_score: 0.245
- phase_breakdown.release_1_score: 0.000
- phase_breakdown.descend_1_score: 0.876
- phase_breakdown.grasp_1_score: 1.000
- phase_breakdown.approach_1_score: 0.153
- phase_breakdown.transport_arc_score: 0.000
- grasp_place_fitness: 0.395

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.395
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.362
- **Median Q (composite search score)**: -0.159
- **K-run variance**: 0.0017
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.325


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.48322,"average_solve_count":298.0,"average_success_count":298.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_y":0.00453,"approach_2.speed":0.07702,"lift_1.lift_height":0.2349,"push_1.push_distance":0.14392,"push_1.push_speed":0.03135,"rotate_1.yaw_angle":0.92149},"optimized_scores":{"best_composite_score":-0.1814,"best_fitness_score":0.2986,"best_task_score":0.17023},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":2622.0,"contact_point_centroid":[0.52123,0.03988,-0.003],"force_p95":0.53274,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.65517,"mean_force":0.25148,"phase_index":7.0,"phase_name":"rotate_1","phase_type":"rotate","tcp_position_centroid":[0.52567,0.06284,0.05925]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5327.0,"contact_point_centroid":[0.5041,0.03836,0.04814],"force_p95":0.19772,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.5185,"mean_force":0.10495,"phase_index":7.0,"phase_name":"rotate_1","phase_type":"rotate","tcp_position_centroid":[0.50394,0.02,0.04909]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8204.0,"contact_point_centroid":[0.50596,0.00313,0.04932],"force_p95":0.18532,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26358,"mean_force":0.10054,"phase_index":7.0,"phase_name":"rotate_1","phase_type":"rotate","tcp_position_centroid":[0.50472,0.02173,0.0494]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50386,-0.01568,-0.00213],"force_p95":0.15796,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.21225,"mean_force":0.13198,"phase_index":6.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49166,-0.01422,0.04642]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5065.0,"contact_point_centroid":[0.49191,0.00497,0.0467],"force_p95":0.06909,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14907,"mean_force":0.04341,"phase_index":6.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49046,-0.01421,0.04511]},{"body_a":"world","body_b":"grasp_target","contact_count":3996.0,"contact_point_centroid":[0.50382,-0.01567,-0.00196],"force_p95":0.12459,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12275,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.53682,0.07971,0.21414]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.50382,-0.01567,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.5436,0.08925,0.17798]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.50382,-0.01567,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.54642,0.09379,0.16915]},{"body_a":"world","body_b":"grasp_target","contact_count":3504.0,"contact_point_centroid":[0.50382,-0.01567,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":3.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.54026,0.0808,0.13131]},{"body_a":"world","body_b":"grasp_target","contact_count":80.0,"contact_point_centroid":[0.50382,-0.01567,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":4.0,"phase_name":"approach_2","phase_type":"approach","tcp_position_centroid":[0.50299,-0.00677,0.12316]},{"body_a":"world","body_b":"grasp_target","contact_count":872.0,"contact_point_centroid":[0.50382,-0.01567,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":5.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49951,-0.01084,0.08863]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5212.0,"contact_point_centroid":[0.4903,-0.03347,0.04855],"force_p95":0.06608,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07237,"mean_force":0.04242,"phase_index":6.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49047,-0.01422,0.04512]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1096.0,"contact_point_centroid":[0.55091,0.11187,0.07314],"force_p95":0.0118,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01644,"mean_force":0.01059,"phase_index":7.0,"phase_name":"rotate_1","phase_type":"rotate","tcp_position_centroid":[0.55062,0.11195,0.07094]}],"total_contact_groups":13},"final_pose_error":0.08424,"key_states":{"actual_goal_position":[0.58691,0.18745,0.24812],"final_object_position":[0.53049,0.07133,0.01602],"final_tcp_position":[0.56001,0.13006,0.07536],"realised_goal_position":[0.58691,0.18745,0.24812],"realised_object_initial_position":[0.50382,-0.01567,0.03]},"peak_contact_force":273003.31887,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.03],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.30942,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":3996.0,"raw_peak_contact_force":0.13845,"tcp_end":[0.57391,0.15482,0.13706],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.2152,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.51785,0.02634,0.22416],"tcp_start":[0.57391,0.15482,0.13706],"tcp_to_object_dist_end":0.20303,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":9.07851,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.57499,0.15514,0.12391],"tcp_start":[0.51785,0.02634,0.22416],"tcp_to_object_dist_end":0.20934,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":876.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3504.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.50373,-0.00599,0.12393],"tcp_start":[0.57499,0.15514,0.12391],"tcp_to_object_dist_end":0.09838,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":20.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"approach_2","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":80.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.50224,-0.00766,0.12251],"tcp_start":[0.50373,-0.00599,0.12393],"tcp_to_object_dist_end":0.09683,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":218.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":872.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.49883,-0.01421,0.05428],"tcp_start":[0.50224,-0.00766,0.12251],"tcp_to_object_dist_end":0.02874,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":46.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.5038,-0.01492,0.02554],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31208,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.15612,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12077.0,"raw_peak_contact_force":0.21225,"tcp_end":[0.49043,-0.01421,0.04508],"tcp_start":[0.49883,-0.01421,0.05428],"tcp_to_object_dist_end":0.02368,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53049,0.07133,0.01602],"object_pos_start":[0.5038,-0.01492,0.02554],"object_to_goal_dist_end":0.26559,"object_to_goal_dist_start":0.31208,"object_z_max":0.02932,"peak_contact_force":273003.31887,"phase_name":"rotate_1","phase_peak_obstacle_force":0.0,"phase_type":"rotate","raw_contact_event_count":17249.0,"raw_peak_contact_force":0.65517,"tcp_end":[0.56001,0.13006,0.07536],"tcp_start":[0.49043,-0.01421,0.04508],"tcp_to_object_dist_end":0.08856,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.47653,"average_solve_count":277.0,"average_success_count":277.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_y":0.00998,"approach_2.speed":0.03479,"lift_1.lift_height":0.20558,"push_1.push_distance":0.02754,"push_1.push_speed":0.04178,"rotate_1.yaw_angle":0.54858},"optimized_scores":{"best_composite_score":-0.08479,"best_fitness_score":0.39521,"best_task_score":0.36188},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":2305.0,"contact_point_centroid":[0.53569,0.10189,-0.00257],"force_p95":0.50456,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.70432,"mean_force":0.24669,"phase_index":7.0,"phase_name":"rotate_1","phase_type":"rotate","tcp_position_centroid":[0.53961,0.11018,0.06331]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6968.0,"contact_point_centroid":[0.51794,0.09693,0.05231],"force_p95":0.1821,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.49842,"mean_force":0.09865,"phase_index":7.0,"phase_name":"rotate_1","phase_type":"rotate","tcp_position_centroid":[0.51921,0.07783,0.05279]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":10465.0,"contact_point_centroid":[0.5237,0.06214,0.05307],"force_p95":0.1711,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30023,"mean_force":0.09248,"phase_index":7.0,"phase_name":"rotate_1","phase_type":"rotate","tcp_position_centroid":[0.52121,0.08112,0.05379]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.5125,0.03988,-0.00203],"force_p95":0.13033,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.14617,"mean_force":0.12524,"phase_index":6.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.50046,0.04009,0.04628]},{"body_a":"world","body_b":"grasp_target","contact_count":3996.0,"contact_point_centroid":[0.51251,0.03972,-0.00196],"force_p95":0.12459,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12275,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.53682,0.07971,0.21414]},{"body_a":"world","body_b":"grasp_target","contact_count":3732.0,"contact_point_centroid":[0.51251,0.03972,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.54038,0.09804,0.17696]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.51251,0.03972,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.54423,0.10719,0.16561]},{"body_a":"world","body_b":"grasp_target","contact_count":2532.0,"contact_point_centroid":[0.51251,0.03972,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":3.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.54541,0.11115,0.12574]},{"body_a":"world","body_b":"grasp_target","contact_count":80.0,"contact_point_centroid":[0.51251,0.03972,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":4.0,"phase_name":"approach_2","phase_type":"approach","tcp_position_centroid":[0.51272,0.0484,0.12251]},{"body_a":"world","body_b":"grasp_target","contact_count":848.0,"contact_point_centroid":[0.51251,0.03972,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50877,0.04412,0.08843]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4845.0,"contact_point_centroid":[0.49851,0.05923,0.04841],"force_p95":0.07839,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10309,"mean_force":0.04474,"phase_index":6.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49925,0.03998,0.04494]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5596.0,"contact_point_centroid":[0.5007,0.02075,0.04705],"force_p95":0.07426,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10237,"mean_force":0.04015,"phase_index":6.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49925,0.03998,0.04494]},{"body_a":"left_finger","body_b":"right_finger","contact_count":738.0,"contact_point_centroid":[0.57287,0.16264,0.08267],"force_p95":0.01318,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01647,"mean_force":0.01082,"phase_index":7.0,"phase_name":"rotate_1","phase_type":"rotate","tcp_position_centroid":[0.57263,0.16279,0.08024]}],"total_contact_groups":13},"final_pose_error":0.03622,"key_states":{"actual_goal_position":[0.62757,0.17252,0.14502],"final_object_position":[0.55091,0.14555,0.01602],"final_tcp_position":[0.58003,0.17435,0.08404],"realised_goal_position":[0.62757,0.17252,0.14502],"realised_object_initial_position":[0.51251,0.03972,0.03]},"peak_contact_force":81.14225,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.03],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21001,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":3996.0,"raw_peak_contact_force":0.13845,"tcp_end":[0.57391,0.15482,0.13706],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.17132,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":933.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":3732.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.51173,0.04401,0.22185],"tcp_start":[0.57391,0.15482,0.13706],"tcp_to_object_dist_end":0.19588,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":81.14225,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.57606,0.16424,0.11958],"tcp_start":[0.51173,0.04401,0.22185],"tcp_to_object_dist_end":0.16822,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":633.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2532.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.51346,0.04922,0.12327],"tcp_start":[0.57606,0.16424,0.11958],"tcp_to_object_dist_end":0.09772,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":20.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"approach_2","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":80.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.51183,0.04746,0.12189],"tcp_start":[0.51346,0.04922,0.12327],"tcp_to_object_dist_end":0.09618,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":212.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":848.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.50767,0.04075,0.05443],"tcp_start":[0.51183,0.04746,0.12189],"tcp_to_object_dist_end":0.02884,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":47.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51238,0.04022,0.02588],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21206,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.13013,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12241.0,"raw_peak_contact_force":0.14617,"tcp_end":[0.49922,0.03998,0.0449],"tcp_start":[0.50767,0.04075,0.05443],"tcp_to_object_dist_end":0.02313,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.55091,0.14555,0.01602],"object_pos_start":[0.51238,0.04022,0.02588],"object_to_goal_dist_end":0.15247,"object_to_goal_dist_start":0.21206,"object_z_max":0.03867,"peak_contact_force":0.12263,"phase_name":"rotate_1","phase_peak_obstacle_force":0.0,"phase_type":"rotate","raw_contact_event_count":20476.0,"raw_peak_contact_force":0.70432,"tcp_end":[0.58003,0.17435,0.08404],"tcp_start":[0.49922,0.03998,0.0449],"tcp_to_object_dist_end":0.0794,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.72197,"average_solve_count":223.0,"average_success_count":223.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_y":0.0061,"approach_2.speed":0.0558,"lift_1.lift_height":0.08955,"push_1.push_distance":0.02967,"push_1.push_speed":0.07326,"rotate_1.yaw_angle":1.19971},"optimized_scores":{"best_composite_score":-0.15866,"best_fitness_score":0.32134,"best_task_score":0.21579},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":1959.0,"contact_point_centroid":[0.51165,0.10133,-0.00269],"force_p95":0.48347,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.67823,"mean_force":0.26092,"phase_index":7.0,"phase_name":"rotate_1","phase_type":"rotate","tcp_position_centroid":[0.51578,0.10598,0.06121]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8105.0,"contact_point_centroid":[0.49655,0.10489,0.0538],"force_p95":0.18192,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.52348,"mean_force":0.0962,"phase_index":7.0,"phase_name":"rotate_1","phase_type":"rotate","tcp_position_centroid":[0.49845,0.08591,0.05445]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":11436.0,"contact_point_centroid":[0.50435,0.07096,0.05456],"force_p95":0.16543,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31979,"mean_force":0.09074,"phase_index":7.0,"phase_name":"rotate_1","phase_type":"rotate","tcp_position_centroid":[0.50164,0.0897,0.05564]},{"body_a":"world","body_b":"grasp_target","contact_count":3996.0,"contact_point_centroid":[0.4827,0.04873,-0.00196],"force_p95":0.12459,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12275,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.53682,0.07971,0.21414]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.48268,0.04886,-0.00202],"force_p95":0.13124,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13202,"mean_force":0.12493,"phase_index":6.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47127,0.04878,0.04728]},{"body_a":"world","body_b":"grasp_target","contact_count":1908.0,"contact_point_centroid":[0.4827,0.04873,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52921,0.10659,0.12169]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.4827,0.04873,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52281,0.10749,0.10171]},{"body_a":"world","body_b":"grasp_target","contact_count":2516.0,"contact_point_centroid":[0.4827,0.04873,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":3.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.52466,0.11076,0.11237]},{"body_a":"world","body_b":"grasp_target","contact_count":80.0,"contact_point_centroid":[0.4827,0.04873,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":4.0,"phase_name":"approach_2","phase_type":"approach","tcp_position_centroid":[0.4845,0.05651,0.12116]},{"body_a":"world","body_b":"grasp_target","contact_count":852.0,"contact_point_centroid":[0.4827,0.04873,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":5.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.47993,0.05259,0.08803]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5155.0,"contact_point_centroid":[0.47189,0.02947,0.04694],"force_p95":0.08043,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11448,"mean_force":0.04355,"phase_index":6.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.4701,0.04866,0.04606]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4850.0,"contact_point_centroid":[0.46904,0.06786,0.0492],"force_p95":0.08064,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09719,"mean_force":0.04477,"phase_index":6.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.4701,0.04866,0.04606]},{"body_a":"left_finger","body_b":"right_finger","contact_count":455.0,"contact_point_centroid":[0.56503,0.16311,0.08274],"force_p95":0.01463,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01654,"mean_force":0.01092,"phase_index":7.0,"phase_name":"rotate_1","phase_type":"rotate","tcp_position_centroid":[0.56486,0.16329,0.08014]}],"total_contact_groups":13},"final_pose_error":0.04606,"key_states":{"actual_goal_position":[0.58187,0.22885,0.23048],"final_object_position":[0.53842,0.15795,0.01603],"final_tcp_position":[0.57032,0.16958,0.08224],"realised_goal_position":[0.58187,0.22885,0.23048],"realised_object_initial_position":[0.4827,0.04873,0.03]},"peak_contact_force":9748.90869,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.03],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28719,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":3996.0,"raw_peak_contact_force":0.13845,"tcp_end":[0.57391,0.15482,0.13706],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.17863,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":477.0,"n_steps_budget":900.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":1908.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.48636,0.05725,0.1119],"tcp_start":[0.57391,0.15482,0.13706],"tcp_to_object_dist_end":0.08638,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.56048,0.15497,0.09656],"tcp_start":[0.48636,0.05725,0.1119],"tcp_to_object_dist_end":0.14938,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":629.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2516.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.48526,0.05722,0.12172],"tcp_start":[0.56048,0.15497,0.09656],"tcp_to_object_dist_end":0.09611,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":20.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"approach_2","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":80.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.48345,0.05566,0.12077],"tcp_start":[0.48526,0.05722,0.12172],"tcp_to_object_dist_end":0.095,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":213.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":852.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.47826,0.04954,0.05467],"tcp_start":[0.48345,0.05566,0.12077],"tcp_to_object_dist_end":0.029,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":46.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.48259,0.04903,0.02589],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.28992,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.132,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11805.0,"raw_peak_contact_force":0.13202,"tcp_end":[0.47007,0.04866,0.04603],"tcp_start":[0.47826,0.04954,0.05467],"tcp_to_object_dist_end":0.02371,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53842,0.15795,0.01603],"object_pos_start":[0.48259,0.04903,0.02589],"object_to_goal_dist_end":0.23002,"object_to_goal_dist_start":0.28992,"object_z_max":0.04005,"peak_contact_force":9748.90869,"phase_name":"rotate_1","phase_peak_obstacle_force":0.0,"phase_type":"rotate","raw_contact_event_count":21955.0,"raw_peak_contact_force":0.67823,"tcp_end":[0.57032,0.16958,0.08224],"tcp_start":[0.47007,0.04866,0.04603],"tcp_to_object_dist_end":0.07442,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```