## Search State

- **Seed**: 6
- **Iteration**: 4 / 15

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
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.480

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| align_1 | 0.00 | 1.00 | 0.2373 |
| lift_1 | 1.00 | 1.00 | 0.1407 |
| push_1 | 0.00 | 1.00 | 0.1255 |
| approach_1 | 1.00 | 1.00 | 0.1243 |
| approach_2 | 1.00 | 1.00 | 0.0026 |
| descend_1 | 1.00 | 1.00 | 0.0673 |
| grasp_1 | 1.00 | 1.00 | 0.0124 |
| rotate_1 | 0.67 | 1.00 | 0.1620 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| align_1 | align | 0.00 / step_budget | (0.500, -0.000, 0.301)→(0.574, 0.155, 0.137) | (0.500, 0.024, 0.030)→(0.500, 0.024, 0.026) | 0.269→0.271 | 1.00 / 4.000 | 0.123 | 0.138 |
| lift_1 | lift | 1.00 / step_budget | (0.574, 0.155, 0.137)→(0.505, 0.041, 0.160) | (0.500, 0.024, 0.026)→(0.500, 0.024, 0.026) | 0.271→0.271 | 1.00 / 4.000 | 0.123 | 0.123 |
| push_1 | push | 0.00 / step_budget | (0.505, 0.041, 0.160)→(0.559, 0.141, 0.113) | (0.500, 0.024, 0.026)→(0.500, 0.024, 0.026) | 0.271→0.271 | 1.00 / 4.000 | 0.123 | 0.123 |
| approach_1 | approach | 1.00 / step_budget | (0.559, 0.141, 0.113)→(0.501, 0.033, 0.123) | (0.500, 0.024, 0.026)→(0.500, 0.024, 0.026) | 0.271→0.271 | 1.00 / 4.000 | 0.123 | 0.123 |
| approach_2 | approach | 1.00 / step_budget | (0.501, 0.033, 0.123)→(0.499, 0.032, 0.121) | (0.500, 0.024, 0.026)→(0.500, 0.024, 0.026) | 0.271→0.271 | 1.00 / 4.000 | 0.123 | 0.123 |
| descend_1 | descend | 1.00 / step_budget | (0.499, 0.032, 0.121)→(0.495, 0.025, 0.054) | (0.500, 0.024, 0.026)→(0.500, 0.024, 0.026) | 0.271→0.271 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_1 | grasp | 1.00 / step_budget | (0.495, 0.025, 0.054)→(0.487, 0.025, 0.045) | (0.500, 0.024, 0.026)→(0.500, 0.025, 0.026) | 0.271→0.271 | 1.00 / 46.333 | 0.139 | 0.162 |
| rotate_1 | rotate | 0.67 / step_budget | (0.487, 0.025, 0.045)→(0.570, 0.158, 0.081) | (0.500, 0.025, 0.026)→(0.540, 0.125, 0.016) | 0.271→0.216 | 1.00 / 8.667 | 91001.189 | 0.680 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 0.000
- transport_retention: None
- terminal_score: 0.362
- phase_score: 0.245
- phase_breakdown.release_1_score: 0.000
- phase_breakdown.descend_1_score: 0.875
- phase_breakdown.grasp_1_score: 1.000
- phase_breakdown.approach_1_score: 0.158
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
- **Final σ (mean)**: 0.299


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.54167,"average_solve_count":264.0,"average_success_count":264.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_y":-0.00531,"approach_2.speed":0.0437,"lift_1.lift_height":0.21478,"push_1.push_distance":0.06789,"push_1.push_speed":0.05694,"rotate_1.yaw_angle":0.38256},"optimized_scores":{"best_composite_score":-0.1814,"best_fitness_score":0.2986,"best_task_score":0.17023},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":2622.0,"contact_point_centroid":[0.52121,0.03989,-0.003],"force_p95":0.53273,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.65518,"mean_force":0.25147,"phase_index":7.0,"phase_name":"rotate_1","phase_type":"rotate","tcp_position_centroid":[0.52567,0.06284,0.05925]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5327.0,"contact_point_centroid":[0.5041,0.03836,0.04814],"force_p95":0.1977,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.51849,"mean_force":0.10496,"phase_index":7.0,"phase_name":"rotate_1","phase_type":"rotate","tcp_position_centroid":[0.50394,0.02,0.04909]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8204.0,"contact_point_centroid":[0.50596,0.00313,0.04932],"force_p95":0.18533,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26359,"mean_force":0.10055,"phase_index":7.0,"phase_name":"rotate_1","phase_type":"rotate","tcp_position_centroid":[0.50473,0.02174,0.0494]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50386,-0.01568,-0.00213],"force_p95":0.15797,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.21226,"mean_force":0.13199,"phase_index":6.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49166,-0.01422,0.04642]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5065.0,"contact_point_centroid":[0.49191,0.00498,0.0467],"force_p95":0.0691,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14904,"mean_force":0.04341,"phase_index":6.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49046,-0.01421,0.04512]},{"body_a":"world","body_b":"grasp_target","contact_count":3996.0,"contact_point_centroid":[0.50382,-0.01567,-0.00196],"force_p95":0.12459,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12275,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.53682,0.07971,0.21414]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.50382,-0.01567,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.5422,0.08598,0.17234]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.50382,-0.01567,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.54362,0.08768,0.16384]},{"body_a":"world","body_b":"grasp_target","contact_count":3332.0,"contact_point_centroid":[0.50382,-0.01567,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":3.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.53845,0.07688,0.13118]},{"body_a":"world","body_b":"grasp_target","contact_count":80.0,"contact_point_centroid":[0.50382,-0.01567,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":4.0,"phase_name":"approach_2","phase_type":"approach","tcp_position_centroid":[0.50298,-0.00677,0.12316]},{"body_a":"world","body_b":"grasp_target","contact_count":872.0,"contact_point_centroid":[0.50382,-0.01567,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":5.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.4995,-0.01084,0.08863]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5212.0,"contact_point_centroid":[0.4903,-0.03347,0.04855],"force_p95":0.06607,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07237,"mean_force":0.04242,"phase_index":6.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49046,-0.01421,0.04512]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1079.0,"contact_point_centroid":[0.55089,0.11185,0.07328],"force_p95":0.0127,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01639,"mean_force":0.01074,"phase_index":7.0,"phase_name":"rotate_1","phase_type":"rotate","tcp_position_centroid":[0.55061,0.11194,0.07094]}],"total_contact_groups":13},"final_pose_error":0.08424,"key_states":{"actual_goal_position":[0.58691,0.18745,0.24812],"final_object_position":[0.53044,0.07134,0.01602],"final_tcp_position":[0.56001,0.13007,0.07536],"realised_goal_position":[0.58691,0.18745,0.24812],"realised_object_initial_position":[0.50382,-0.01567,0.03]},"peak_contact_force":273003.31934,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.03],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.30942,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":3996.0,"raw_peak_contact_force":0.13845,"tcp_end":[0.57391,0.15482,0.13706],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.2152,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.51515,0.0201,0.2129],"tcp_start":[0.57391,0.15482,0.13706],"tcp_to_object_dist_end":0.19062,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.57187,0.14842,0.12442],"tcp_start":[0.51515,0.0201,0.2129],"tcp_to_object_dist_end":0.20308,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":833.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3332.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.50371,-0.00599,0.12393],"tcp_start":[0.57187,0.14842,0.12442],"tcp_to_object_dist_end":0.09839,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":20.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"approach_2","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":80.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.50223,-0.00766,0.12251],"tcp_start":[0.50371,-0.00599,0.12393],"tcp_to_object_dist_end":0.09684,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":218.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":872.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.49883,-0.01421,0.05428],"tcp_start":[0.50223,-0.00766,0.12251],"tcp_to_object_dist_end":0.02874,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":46.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.5038,-0.01492,0.02554],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31208,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.15612,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12077.0,"raw_peak_contact_force":0.21226,"tcp_end":[0.49043,-0.01421,0.04508],"tcp_start":[0.49883,-0.01421,0.05428],"tcp_to_object_dist_end":0.02369,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53044,0.07134,0.01602],"object_pos_start":[0.5038,-0.01492,0.02554],"object_to_goal_dist_end":0.26559,"object_to_goal_dist_start":0.31208,"object_z_max":0.02932,"peak_contact_force":273003.31934,"phase_name":"rotate_1","phase_peak_obstacle_force":0.0,"phase_type":"rotate","raw_contact_event_count":17232.0,"raw_peak_contact_force":0.65518,"tcp_end":[0.56001,0.13007,0.07536],"tcp_start":[0.49043,-0.01421,0.04508],"tcp_to_object_dist_end":0.08857,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.5307,"average_solve_count":228.0,"average_success_count":228.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_y":0.00101,"approach_2.speed":0.05566,"lift_1.lift_height":0.12472,"push_1.push_distance":0.13054,"push_1.push_speed":0.05209,"rotate_1.yaw_angle":0.96608},"optimized_scores":{"best_composite_score":-0.0846,"best_fitness_score":0.3954,"best_task_score":0.36227},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":2297.0,"contact_point_centroid":[0.5357,0.10184,-0.00257],"force_p95":0.5026,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.70595,"mean_force":0.2473,"phase_index":7.0,"phase_name":"rotate_1","phase_type":"rotate","tcp_position_centroid":[0.53948,0.11001,0.06325]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6990.0,"contact_point_centroid":[0.51797,0.09698,0.05232],"force_p95":0.18219,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.49759,"mean_force":0.09866,"phase_index":7.0,"phase_name":"rotate_1","phase_type":"rotate","tcp_position_centroid":[0.51921,0.07787,0.0528]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":10515.0,"contact_point_centroid":[0.52376,0.06228,0.0531],"force_p95":0.17097,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29999,"mean_force":0.09243,"phase_index":7.0,"phase_name":"rotate_1","phase_type":"rotate","tcp_position_centroid":[0.52127,0.08125,0.05382]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.51249,0.03988,-0.00202],"force_p95":0.12966,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.14047,"mean_force":0.12508,"phase_index":6.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.5004,0.04004,0.04626]},{"body_a":"world","body_b":"grasp_target","contact_count":3996.0,"contact_point_centroid":[0.51251,0.03972,-0.00196],"force_p95":0.12459,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12275,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.53682,0.07971,0.21414]},{"body_a":"world","body_b":"grasp_target","contact_count":2364.0,"contact_point_centroid":[0.51251,0.03972,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.54135,0.10032,0.13742]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.51251,0.03972,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.53846,0.09865,0.12267]},{"body_a":"world","body_b":"grasp_target","contact_count":2196.0,"contact_point_centroid":[0.51251,0.03972,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":3.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.53808,0.09882,0.1184]},{"body_a":"world","body_b":"grasp_target","contact_count":80.0,"contact_point_centroid":[0.51251,0.03972,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":4.0,"phase_name":"approach_2","phase_type":"approach","tcp_position_centroid":[0.51235,0.04799,0.12126]},{"body_a":"world","body_b":"grasp_target","contact_count":836.0,"contact_point_centroid":[0.51251,0.03972,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50857,0.04392,0.08788]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5596.0,"contact_point_centroid":[0.50065,0.02071,0.04703],"force_p95":0.07417,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10199,"mean_force":0.04014,"phase_index":6.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49919,0.03994,0.04491]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4846.0,"contact_point_centroid":[0.49846,0.05918,0.04841],"force_p95":0.07826,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10195,"mean_force":0.04472,"phase_index":6.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49919,0.03994,0.04491]},{"body_a":"left_finger","body_b":"right_finger","contact_count":721.0,"contact_point_centroid":[0.57301,0.16292,0.08272],"force_p95":0.01315,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01654,"mean_force":0.0109,"phase_index":7.0,"phase_name":"rotate_1","phase_type":"rotate","tcp_position_centroid":[0.57281,0.16307,0.08034]}],"total_contact_groups":13},"final_pose_error":0.03623,"key_states":{"actual_goal_position":[0.62757,0.17252,0.14502],"final_object_position":[0.55111,0.14592,0.01602],"final_tcp_position":[0.58002,0.17434,0.08403],"realised_goal_position":[0.62757,0.17252,0.14502],"realised_object_initial_position":[0.51251,0.03972,0.03]},"peak_contact_force":0.70595,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.03],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21001,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":3996.0,"raw_peak_contact_force":0.13845,"tcp_end":[0.57391,0.15482,0.13706],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.17132,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":591.0,"n_steps_budget":840.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":2364.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.51262,0.04697,0.14388],"tcp_start":[0.57391,0.15482,0.13706],"tcp_to_object_dist_end":0.11808,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.56304,0.14205,0.10922],"tcp_start":[0.51262,0.04697,0.14388],"tcp_to_object_dist_end":0.14123,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":549.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2196.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.51303,0.04876,0.12191],"tcp_start":[0.56304,0.14205,0.10922],"tcp_to_object_dist_end":0.09632,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":20.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"approach_2","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":80.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.51149,0.04711,0.12076],"tcp_start":[0.51303,0.04876,0.12191],"tcp_to_object_dist_end":0.09503,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":209.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":836.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.50761,0.04071,0.0544],"tcp_start":[0.51149,0.04711,0.12076],"tcp_to_object_dist_end":0.02882,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":47.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51238,0.04019,0.02589],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21207,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.13028,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12242.0,"raw_peak_contact_force":0.14047,"tcp_end":[0.49916,0.03994,0.04488],"tcp_start":[0.50761,0.04071,0.0544],"tcp_to_object_dist_end":0.02314,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.55111,0.14592,0.01602],"object_pos_start":[0.51238,0.04019,0.02589],"object_to_goal_dist_end":0.1523,"object_to_goal_dist_start":0.21207,"object_z_max":0.03878,"peak_contact_force":0.12263,"phase_name":"rotate_1","phase_peak_obstacle_force":0.0,"phase_type":"rotate","raw_contact_event_count":20523.0,"raw_peak_contact_force":0.70595,"tcp_end":[0.58002,0.17434,0.08403],"tcp_start":[0.49916,0.03994,0.04488],"tcp_to_object_dist_end":0.07918,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.50209,"average_solve_count":239.0,"average_success_count":239.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_y":0.00634,"approach_2.speed":0.05534,"lift_1.lift_height":0.10204,"push_1.push_distance":0.13041,"push_1.push_speed":0.03703,"rotate_1.yaw_angle":0.79724},"optimized_scores":{"best_composite_score":-0.15859,"best_fitness_score":0.32141,"best_task_score":0.21593},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":1952.0,"contact_point_centroid":[0.51165,0.10123,-0.00269],"force_p95":0.48339,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.67823,"mean_force":0.26139,"phase_index":7.0,"phase_name":"rotate_1","phase_type":"rotate","tcp_position_centroid":[0.51565,0.10585,0.06116]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8128.0,"contact_point_centroid":[0.49664,0.10501,0.05381],"force_p95":0.18176,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.52294,"mean_force":0.09609,"phase_index":7.0,"phase_name":"rotate_1","phase_type":"rotate","tcp_position_centroid":[0.49854,0.08603,0.05448]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":11455.0,"contact_point_centroid":[0.50442,0.07107,0.05458],"force_p95":0.16548,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31974,"mean_force":0.09072,"phase_index":7.0,"phase_name":"rotate_1","phase_type":"rotate","tcp_position_centroid":[0.50171,0.08981,0.05566]},{"body_a":"world","body_b":"grasp_target","contact_count":3996.0,"contact_point_centroid":[0.4827,0.04873,-0.00196],"force_p95":0.12459,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12275,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.53682,0.07971,0.21414]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.48268,0.04886,-0.00202],"force_p95":0.13106,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13184,"mean_force":0.12491,"phase_index":6.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47126,0.0488,0.04728]},{"body_a":"world","body_b":"grasp_target","contact_count":2012.0,"contact_point_centroid":[0.4827,0.04873,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.5289,0.1062,0.12724]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.4827,0.04873,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51569,0.09849,0.11062]},{"body_a":"world","body_b":"grasp_target","contact_count":1876.0,"contact_point_centroid":[0.4827,0.04873,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":3.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51479,0.09825,0.11507]},{"body_a":"world","body_b":"grasp_target","contact_count":80.0,"contact_point_centroid":[0.4827,0.04873,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":4.0,"phase_name":"approach_2","phase_type":"approach","tcp_position_centroid":[0.48445,0.05663,0.12112]},{"body_a":"world","body_b":"grasp_target","contact_count":852.0,"contact_point_centroid":[0.4827,0.04873,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.4799,0.05265,0.08802]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5159.0,"contact_point_centroid":[0.47188,0.02948,0.04694],"force_p95":0.08046,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10761,"mean_force":0.04352,"phase_index":6.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47009,0.04868,0.04606]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4848.0,"contact_point_centroid":[0.46903,0.06788,0.04919],"force_p95":0.08068,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09812,"mean_force":0.04478,"phase_index":6.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47009,0.04868,0.04605]},{"body_a":"left_finger","body_b":"right_finger","contact_count":450.0,"contact_point_centroid":[0.56509,0.16315,0.08265],"force_p95":0.01377,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01521,"mean_force":0.0109,"phase_index":7.0,"phase_name":"rotate_1","phase_type":"rotate","tcp_position_centroid":[0.56488,0.16331,0.08015]}],"total_contact_groups":13},"final_pose_error":0.04606,"key_states":{"actual_goal_position":[0.58187,0.22885,0.23048],"final_object_position":[0.53861,0.15814,0.01603],"final_tcp_position":[0.57032,0.16958,0.08224],"realised_goal_position":[0.58187,0.22885,0.23048],"realised_object_initial_position":[0.4827,0.04873,0.03]},"peak_contact_force":0.67823,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.03],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28719,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":3996.0,"raw_peak_contact_force":0.13845,"tcp_end":[0.57391,0.15482,0.13706],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.17863,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":503.0,"n_steps_budget":900.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":2012.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.48606,0.05681,0.12328],"tcp_start":[0.57391,0.15482,0.13706],"tcp_to_object_dist_end":0.09766,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.54337,0.13345,0.10399],"tcp_start":[0.48606,0.05681,0.12328],"tcp_to_object_dist_end":0.13015,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":469.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1876.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.4852,0.05735,0.12168],"tcp_start":[0.54337,0.13345,0.10399],"tcp_to_object_dist_end":0.09608,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":20.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"approach_2","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":80.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.4834,0.05577,0.12074],"tcp_start":[0.4852,0.05735,0.12168],"tcp_to_object_dist_end":0.09498,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":213.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":852.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.47825,0.04956,0.05466],"tcp_start":[0.4834,0.05577,0.12074],"tcp_to_object_dist_end":0.029,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":46.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.48259,0.04904,0.02589],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.28991,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.13184,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11807.0,"raw_peak_contact_force":0.13184,"tcp_end":[0.47006,0.04867,0.04602],"tcp_start":[0.47825,0.04956,0.05466],"tcp_to_object_dist_end":0.02371,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53861,0.15814,0.01603],"object_pos_start":[0.48259,0.04904,0.02589],"object_to_goal_dist_end":0.22992,"object_to_goal_dist_start":0.28991,"object_z_max":0.04009,"peak_contact_force":0.12379,"phase_name":"rotate_1","phase_peak_obstacle_force":0.0,"phase_type":"rotate","raw_contact_event_count":21985.0,"raw_peak_contact_force":0.67823,"tcp_end":[0.57032,0.16958,0.08224],"tcp_start":[0.47006,0.04867,0.04602],"tcp_to_object_dist_end":0.07431,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```