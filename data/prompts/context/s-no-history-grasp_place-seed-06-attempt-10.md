## Search State

- **Seed**: 6
- **Iteration**: 11 / 15

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

## Current Skill (Q=-0.001) — your mutation base

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

- **Composite score**: -0.001
- **task_score** (E): 0.205
- **fitness_score**: 0.579  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.580

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_object | 1.00 | 1.00 | 0.1258 |
| descend_grasp | 1.00 | 1.00 | 0.1454 |
| grasp | 1.00 | 1.00 | 0.0121 |
| lift | 1.00 | 1.00 | 0.0987 |
| transport_to_goal | 0.00 | 1.00 | 0.0842 |
| descend_place | 0.33 | 1.00 | 0.0912 |
| release | 1.00 | 1.00 | 0.0228 |
| retract | 1.00 | 1.00 | 0.0878 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.497, 0.030, 0.182) | (0.500, 0.024, 0.030)→(0.500, 0.024, 0.026) | 0.269→0.271 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_grasp | descend | 1.00 / step_budget | (0.497, 0.030, 0.182)→(0.495, 0.025, 0.037) | (0.500, 0.024, 0.026)→(0.500, 0.024, 0.026) | 0.271→0.271 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp | grasp | 1.00 / step_budget | (0.495, 0.025, 0.037)→(0.487, 0.024, 0.028) | (0.500, 0.024, 0.026)→(0.500, 0.024, 0.026) | 0.271→0.272 | 1.00 / 43.000 | 0.141 | 0.207 |
| lift | lift | 1.00 / step_budget | (0.487, 0.024, 0.028)→(0.483, 0.024, 0.127) | (0.500, 0.024, 0.026)→(0.499, 0.024, 0.115) | 0.272→0.224 | 1.00 / 25.000 | 0.107 | 0.663 |
| transport_to_goal | approach | 0.00 / step_budget | (0.483, 0.024, 0.127)→(0.513, 0.073, 0.188) | (0.499, 0.024, 0.115)→(0.516, 0.071, 0.014) | 0.224→0.247 | 1.00 / 7.000 | 3249.310 | 1.546 |
| descend_place | descend | 0.33 / step_budget | (0.513, 0.073, 0.188)→(0.562, 0.145, 0.189) | (0.516, 0.071, 0.014)→(0.516, 0.070, 0.016) | 0.247→0.246 | 1.00 / 8.000 | 3249.663 | 0.126 |
| release | release | 1.00 / step_budget | (0.562, 0.145, 0.189)→(0.557, 0.144, 0.212) | (0.516, 0.070, 0.016)→(0.516, 0.070, 0.016) | 0.246→0.246 | 1.00 / 4.000 | 0.123 | 0.123 |
| retract | retract | 1.00 / step_budget | (0.557, 0.144, 0.212)→(0.555, 0.143, 0.299) | (0.516, 0.070, 0.016)→(0.516, 0.070, 0.016) | 0.246→0.246 | 1.00 / 4.000 | 0.123 | 0.123 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.301
- phase_score: 0.460
- phase_breakdown.reach_object_score: 0.821
- phase_breakdown.lift_object_score: 0.133
- phase_breakdown.transport_to_goal_score: 0.027
- phase_breakdown.place_object_score: 0.361
- phase_breakdown.grasp_object_score: 0.757
- grasp_place_fitness: 0.626

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.626
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.301
- **Median Q (composite search score)**: -0.019
- **K-run variance**: 0.0011
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.251


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.27984,"average_solve_count":243.0,"average_success_count":243.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_speed":0.07676,"approach_object.arc_height":0.0557,"descend_grasp.descent_speed":0.03446,"descend_grasp.descent_tolerance":0.01603,"descend_place.place_speed":0.05197,"lift.lift_distance":0.10707,"retract.retract_speed":0.07242,"transport_to_goal.transport_speed":0.05424},"optimized_scores":{"best_composite_score":-0.0302,"best_fitness_score":0.5498,"best_task_score":0.14572},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":303.0,"contact_point_centroid":[0.52183,0.02786,-0.00523],"force_p95":0.96896,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.65367,"mean_force":0.26731,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.50717,0.03417,0.18698]},{"body_a":"world","body_b":"grasp_target","contact_count":139.0,"contact_point_centroid":[0.501,-0.01363,-0.00117],"force_p95":0.41357,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.59262,"mean_force":0.08163,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.4891,-0.01444,0.03374]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":9053.0,"contact_point_centroid":[0.48901,0.00455,0.0762],"force_p95":0.10671,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33018,"mean_force":0.06765,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.48654,-0.01439,0.07418]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":9886.0,"contact_point_centroid":[0.48908,-0.03319,0.07456],"force_p95":0.10128,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30892,"mean_force":0.06315,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.48657,-0.01439,0.07311]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8830.0,"contact_point_centroid":[0.49821,0.02568,0.15007],"force_p95":0.13852,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28888,"mean_force":0.08749,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.49369,0.00731,0.15135]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50385,-0.01542,-0.00211],"force_p95":0.15466,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.22401,"mean_force":0.13115,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.4918,-0.01447,0.03312]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":9115.0,"contact_point_centroid":[0.49834,-0.01098,0.1501],"force_p95":0.12561,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19713,"mean_force":0.08498,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.49376,0.00735,0.15147]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4077.0,"contact_point_centroid":[0.4912,0.00475,0.03467],"force_p95":0.07984,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14274,"mean_force":0.05184,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.49065,-0.01446,0.03191]},{"body_a":"world","body_b":"grasp_target","contact_count":2380.0,"contact_point_centroid":[0.50382,-0.01567,-0.00194],"force_p95":0.13103,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12283,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.49909,0.02554,0.23319]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.52232,0.02798,-0.00198],"force_p95":0.12296,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12636,"mean_force":0.1226,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.52659,0.07748,0.19962]},{"body_a":"world","body_b":"grasp_target","contact_count":1312.0,"contact_point_centroid":[0.50382,-0.01567,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.49837,-0.01096,0.10932]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.52232,0.02798,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.54112,0.11148,0.21495]},{"body_a":"world","body_b":"grasp_target","contact_count":3024.0,"contact_point_centroid":[0.52232,0.02798,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":7.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.53724,0.11059,0.279]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4979.0,"contact_point_centroid":[0.49123,-0.03359,0.03376],"force_p95":0.07189,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08388,"mean_force":0.04465,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.49065,-0.01446,0.03192]},{"body_a":"left_finger","body_b":"right_finger","contact_count":63.0,"contact_point_centroid":[0.50809,0.03558,0.19136],"force_p95":0.01611,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01625,"mean_force":0.01303,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.5079,0.03558,0.18886]},{"body_a":"left_finger","body_b":"right_finger","contact_count":4253.0,"contact_point_centroid":[0.52701,0.07762,0.20194],"force_p95":0.01101,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01279,"mean_force":0.0105,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.52666,0.07762,0.19967]}],"total_contact_groups":17},"final_pose_error":0.01176,"key_states":{"actual_goal_position":[0.58691,0.18745,0.24812],"final_object_position":[0.52232,0.02798,0.01602],"final_tcp_position":[0.53758,0.11063,0.32381],"realised_goal_position":[0.58691,0.18745,0.24812],"realised_object_initial_position":[0.50382,-0.01567,0.03]},"peak_contact_force":9747.69645,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":596.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.03],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.30942,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2380.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.50004,-0.00758,0.17565],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.14989,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":328.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1312.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_object","tcp_end":[0.49896,-0.01452,0.04087],"tcp_start":[0.50004,-0.00758,0.17565],"tcp_to_object_dist_end":0.01567,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50372,-0.01449,0.02563],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31177,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.14814,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10856.0,"raw_peak_contact_force":0.22401,"subtask_id":"grasp_object","tcp_end":[0.49062,-0.01445,0.03188],"tcp_start":[0.49896,-0.01452,0.04087],"tcp_to_object_dist_end":0.01452,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":603.0,"n_steps_budget":690.0,"object_pos_end":[0.50194,-0.01433,0.11252],"object_pos_start":[0.50372,-0.01449,0.02563],"object_to_goal_dist_end":0.25753,"object_to_goal_dist_start":0.31177,"object_z_max":0.11241,"peak_contact_force":0.11282,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":19078.0,"raw_peak_contact_force":0.59262,"subtask_id":"lift_object","tcp_end":[0.48658,-0.01438,0.12724],"tcp_start":[0.49062,-0.01445,0.03188],"tcp_to_object_dist_end":0.02128,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.52233,0.02802,0.0166],"object_pos_start":[0.50194,-0.01433,0.11252],"object_to_goal_dist_end":0.28843,"object_to_goal_dist_start":0.25753,"object_z_max":0.15342,"peak_contact_force":9747.69645,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":18311.0,"raw_peak_contact_force":1.65367,"subtask_id":"transport_to_goal","tcp_end":[0.50804,0.03585,0.18922],"tcp_start":[0.48658,-0.01438,0.12724],"tcp_to_object_dist_end":0.1734,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.52232,0.02798,0.01602],"object_pos_start":[0.52233,0.02802,0.0166],"object_to_goal_dist_end":0.28891,"object_to_goal_dist_start":0.28843,"object_z_max":0.0166,"peak_contact_force":0.12263,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":8253.0,"raw_peak_contact_force":0.12636,"subtask_id":"place_object","tcp_end":[0.54468,0.11218,0.21238],"tcp_start":[0.50804,0.03585,0.18922],"tcp_to_object_dist_end":0.21482,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.52232,0.02798,0.01602],"object_pos_start":[0.52232,0.02798,0.01602],"object_to_goal_dist_end":0.28891,"object_to_goal_dist_start":0.28891,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1024.0,"raw_peak_contact_force":0.12263,"subtask_id":"place_object","tcp_end":[0.53979,0.11116,0.23534],"tcp_start":[0.54468,0.11218,0.21238],"tcp_to_object_dist_end":0.23521,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":756.0,"n_steps_budget":870.0,"object_pos_end":[0.52232,0.02798,0.01602],"object_pos_start":[0.52232,0.02798,0.01602],"object_to_goal_dist_end":0.28891,"object_to_goal_dist_start":0.28891,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3024.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.53758,0.11063,0.32381],"tcp_start":[0.53979,0.11116,0.23534],"tcp_to_object_dist_end":0.31906,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.5314,"average_solve_count":207.0,"average_success_count":207.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_speed":0.06597,"approach_object.arc_height":0.07849,"descend_grasp.descent_speed":0.06196,"descend_grasp.descent_tolerance":0.01836,"descend_place.place_speed":0.0704,"lift.lift_distance":0.10882,"retract.retract_speed":0.0817,"transport_to_goal.transport_speed":0.04589},"optimized_scores":{"best_composite_score":0.04632,"best_fitness_score":0.62632,"best_task_score":0.30147},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":151.0,"contact_point_centroid":[0.5437,0.08021,-0.0078],"force_p95":1.27444,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.55269,"mean_force":0.46489,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.5304,0.07823,0.17289]},{"body_a":"world","body_b":"grasp_target","contact_count":132.0,"contact_point_centroid":[0.50931,0.03991,-0.0011],"force_p95":0.44014,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.56832,"mean_force":0.07811,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.49766,0.0397,0.03552]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":9093.0,"contact_point_centroid":[0.49755,0.05845,0.07876],"force_p95":0.10489,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33763,"mean_force":0.06756,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.49504,0.03949,0.07683]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":9675.0,"contact_point_centroid":[0.49769,0.02072,0.07697],"force_p95":0.10189,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29658,"mean_force":0.06397,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.49507,0.03949,0.07547]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8698.0,"contact_point_centroid":[0.51393,0.03849,0.14638],"force_p95":0.1484,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25573,"mean_force":0.09126,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.5091,0.05688,0.14723]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":9282.0,"contact_point_centroid":[0.51484,0.07603,0.1471],"force_p95":0.12791,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1614,"mean_force":0.08582,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.50991,0.05771,0.1482]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.5125,0.03981,-0.00202],"force_p95":0.13,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.1479,"mean_force":0.12482,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.50034,0.03993,0.03507]},{"body_a":"world","body_b":"grasp_target","contact_count":2388.0,"contact_point_centroid":[0.51251,0.03972,-0.00194],"force_p95":0.13091,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12283,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.50149,0.04752,0.25496]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.54409,0.07902,-0.00201],"force_p95":0.12307,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12922,"mean_force":0.12129,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.56752,0.11715,0.15483]},{"body_a":"world","body_b":"grasp_target","contact_count":1176.0,"contact_point_centroid":[0.51251,0.03972,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.50687,0.04437,0.1137]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.54409,0.07903,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.59248,0.1447,0.14596]},{"body_a":"world","body_b":"grasp_target","contact_count":2772.0,"contact_point_centroid":[0.54409,0.07903,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":7.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.5875,0.14332,0.20677]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4129.0,"contact_point_centroid":[0.49976,0.05905,0.0365],"force_p95":0.07567,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09527,"mean_force":0.05174,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.49918,0.03984,0.03382]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4866.0,"contact_point_centroid":[0.49983,0.02078,0.03573],"force_p95":0.06779,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08859,"mean_force":0.04468,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.49918,0.03984,0.03382]},{"body_a":"left_finger","body_b":"right_finger","contact_count":4149.0,"contact_point_centroid":[0.5687,0.11796,0.15673],"force_p95":0.01102,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01639,"mean_force":0.01054,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.56826,0.11794,0.15444]},{"body_a":"left_finger","body_b":"right_finger","contact_count":222.0,"contact_point_centroid":[0.59602,0.14556,0.14411],"force_p95":0.01101,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0126,"mean_force":0.01006,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.59545,0.14553,0.142]}],"total_contact_groups":16},"final_pose_error":0.01362,"key_states":{"actual_goal_position":[0.62757,0.17252,0.14502],"final_object_position":[0.54409,0.07903,0.01602],"final_tcp_position":[0.58781,0.14336,0.25246],"realised_goal_position":[0.62757,0.17252,0.14502],"realised_object_initial_position":[0.51251,0.03972,0.03]},"peak_contact_force":1.55269,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":598.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.03],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21001,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2388.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.50805,0.04823,0.18219],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.15647,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":294.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1176.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_object","tcp_end":[0.50766,0.04059,0.04332],"tcp_start":[0.50805,0.04823,0.18219],"tcp_to_object_dist_end":0.01799,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51239,0.03999,0.0259],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21219,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.12884,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10795.0,"raw_peak_contact_force":0.1479,"subtask_id":"grasp_object","tcp_end":[0.49915,0.03983,0.03379],"tcp_start":[0.50766,0.04059,0.04332],"tcp_to_object_dist_end":0.01542,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":25.0,"n_steps":603.0,"n_steps_budget":690.0,"object_pos_end":[0.50985,0.03953,0.11442],"object_pos_start":[0.51239,0.03999,0.0259],"object_to_goal_dist_end":0.18022,"object_to_goal_dist_start":0.21219,"object_z_max":0.11431,"peak_contact_force":0.09997,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":18900.0,"raw_peak_contact_force":0.56832,"subtask_id":"lift_object","tcp_end":[0.49511,0.03951,0.1306],"tcp_start":[0.49915,0.03983,0.03379],"tcp_to_object_dist_end":0.02189,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.54457,0.08198,0.00998],"object_pos_start":[0.50985,0.03953,0.11442],"object_to_goal_dist_end":0.18255,"object_to_goal_dist_start":0.18022,"object_z_max":0.14142,"peak_contact_force":0.11181,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":18131.0,"raw_peak_contact_force":1.55269,"subtask_id":"transport_to_goal","tcp_end":[0.53104,0.07887,0.17367],"tcp_start":[0.49511,0.03951,0.1306],"tcp_to_object_dist_end":0.16428,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.54409,0.07903,0.01602],"object_pos_start":[0.54457,0.08198,0.00998],"object_to_goal_dist_end":0.17987,"object_to_goal_dist_start":0.18255,"object_z_max":0.01667,"peak_contact_force":0.12263,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":8149.0,"raw_peak_contact_force":0.12922,"subtask_id":"place_object","tcp_end":[0.59695,0.14585,0.1448],"tcp_start":[0.53104,0.07887,0.17367],"tcp_to_object_dist_end":0.15441,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54409,0.07903,0.01602],"object_pos_start":[0.54409,0.07903,0.01602],"object_to_goal_dist_end":0.17987,"object_to_goal_dist_start":0.17987,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1022.0,"raw_peak_contact_force":0.12263,"subtask_id":"place_object","tcp_end":[0.59073,0.1442,0.16573],"tcp_start":[0.59695,0.14585,0.1448],"tcp_to_object_dist_end":0.16981,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":693.0,"n_steps_budget":780.0,"object_pos_end":[0.54409,0.07903,0.01602],"object_pos_start":[0.54409,0.07903,0.01602],"object_to_goal_dist_end":0.17987,"object_to_goal_dist_start":0.17987,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2772.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.58781,0.14336,0.25246],"tcp_start":[0.59073,0.1442,0.16573],"tcp_to_object_dist_end":0.2489,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.17949,"average_solve_count":273.0,"average_success_count":273.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_speed":0.02295,"approach_object.arc_height":0.02203,"descend_grasp.descent_speed":0.07901,"descend_grasp.descent_tolerance":0.00503,"descend_place.place_speed":0.06,"lift.lift_distance":0.11502,"retract.retract_speed":0.07348,"transport_to_goal.transport_speed":0.08614},"optimized_scores":{"best_composite_score":-0.01852,"best_fitness_score":0.56148,"best_task_score":0.16681},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":2399.0,"contact_point_centroid":[0.48129,0.10147,-0.00233],"force_p95":0.15691,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.43214,"mean_force":0.14432,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.48929,0.08868,0.17762]},{"body_a":"world","body_b":"grasp_target","contact_count":137.0,"contact_point_centroid":[0.47981,0.04654,-0.00115],"force_p95":0.65613,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.82769,"mean_force":0.10309,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.46866,0.04737,0.02161]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":10685.0,"contact_point_centroid":[0.46863,0.06606,0.06658],"force_p95":0.10529,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31018,"mean_force":0.06527,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.46616,0.04713,0.06497]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":10559.0,"contact_point_centroid":[0.46842,0.02826,0.06906],"force_p95":0.10693,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29707,"mean_force":0.06556,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.46614,0.04713,0.0674]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3204.0,"contact_point_centroid":[0.47314,0.03884,0.13147],"force_p95":0.1635,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25799,"mean_force":0.09794,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.46953,0.05708,0.13412]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3328.0,"contact_point_centroid":[0.47345,0.07648,0.13273],"force_p95":0.16297,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25298,"mean_force":0.10363,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.47018,0.05827,0.13564]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.48272,0.04841,-0.0021],"force_p95":0.15298,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24972,"mean_force":0.13127,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.4713,0.04764,0.02089]},{"body_a":"world","body_b":"grasp_target","contact_count":1832.0,"contact_point_centroid":[0.4827,0.04873,-0.00192],"force_p95":0.13357,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12289,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.49092,0.03325,0.25149]},{"body_a":"world","body_b":"grasp_target","contact_count":3576.0,"contact_point_centroid":[0.4827,0.04873,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.47818,0.04921,0.10412]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.48122,0.1022,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.52362,0.14483,0.20391]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.48122,0.1022,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.54221,0.17697,0.21336]},{"body_a":"world","body_b":"grasp_target","contact_count":3024.0,"contact_point_centroid":[0.48122,0.1022,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":7.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.53844,0.1756,0.27694]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5007.0,"contact_point_centroid":[0.47001,0.0283,0.02284],"force_p95":0.06934,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10208,"mean_force":0.04295,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.47015,0.04753,0.01975]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5476.0,"contact_point_centroid":[0.46982,0.06684,0.02219],"force_p95":0.06798,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08961,"mean_force":0.04137,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.47016,0.04753,0.01975]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2316.0,"contact_point_centroid":[0.49045,0.09,0.18169],"force_p95":0.0113,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01767,"mean_force":0.01076,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.49014,0.08999,0.17946]},{"body_a":"left_finger","body_b":"right_finger","contact_count":4296.0,"contact_point_centroid":[0.5242,0.14503,0.20622],"force_p95":0.01098,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01283,"mean_force":0.01039,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.52374,0.145,0.20394]}],"total_contact_groups":17},"final_pose_error":0.01206,"key_states":{"actual_goal_position":[0.58187,0.22885,0.23048],"final_object_position":[0.48122,0.1022,0.01602],"final_tcp_position":[0.53879,0.17567,0.32174],"realised_goal_position":[0.58187,0.22885,0.23048],"realised_object_initial_position":[0.4827,0.04873,0.03]},"peak_contact_force":9748.74331,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":459.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.03],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28719,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1832.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.48143,0.05045,0.18955],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.16354,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":894.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3576.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_object","tcp_end":[0.47795,0.04832,0.02756],"tcp_start":[0.48143,0.05045,0.18955],"tcp_to_object_dist_end":0.00501,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":47.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.48255,0.04753,0.02565],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.29104,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.14719,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12283.0,"raw_peak_contact_force":0.24972,"subtask_id":"grasp_object","tcp_end":[0.47013,0.04752,0.01972],"tcp_start":[0.47795,0.04832,0.02756],"tcp_to_object_dist_end":0.01377,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":27.0,"n_steps":663.0,"n_steps_budget":750.0,"object_pos_end":[0.48637,0.04721,0.1166],"object_pos_start":[0.48255,0.04753,0.02565],"object_to_goal_dist_end":0.2347,"object_to_goal_dist_start":0.29104,"object_z_max":0.1165,"peak_contact_force":0.10826,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":21381.0,"raw_peak_contact_force":0.82769,"subtask_id":"lift_object","tcp_end":[0.46617,0.04715,0.1235],"tcp_start":[0.47013,0.04752,0.01972],"tcp_to_object_dist_end":0.02134,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.48122,0.1022,0.01602],"object_pos_start":[0.48637,0.04721,0.1166],"object_to_goal_dist_end":0.26864,"object_to_goal_dist_start":0.2347,"object_z_max":0.12412,"peak_contact_force":0.12263,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":11247.0,"raw_peak_contact_force":1.43214,"subtask_id":"transport_to_goal","tcp_end":[0.49967,0.1046,0.19995],"tcp_start":[0.46617,0.04715,0.1235],"tcp_to_object_dist_end":0.18487,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.48122,0.1022,0.01602],"object_pos_start":[0.48122,0.1022,0.01602],"object_to_goal_dist_end":0.26864,"object_to_goal_dist_start":0.26864,"object_z_max":0.01602,"peak_contact_force":9748.74331,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":8296.0,"raw_peak_contact_force":0.12263,"subtask_id":"place_object","tcp_end":[0.54568,0.1781,0.21118],"tcp_start":[0.49967,0.1046,0.19995],"tcp_to_object_dist_end":0.2191,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.48122,0.1022,0.01602],"object_pos_start":[0.48122,0.1022,0.01602],"object_to_goal_dist_end":0.26864,"object_to_goal_dist_start":0.26864,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1022.0,"raw_peak_contact_force":0.12263,"subtask_id":"place_object","tcp_end":[0.5409,0.17647,0.23358],"tcp_start":[0.54568,0.1781,0.21118],"tcp_to_object_dist_end":0.23751,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":756.0,"n_steps_budget":870.0,"object_pos_end":[0.48122,0.1022,0.01602],"object_pos_start":[0.48122,0.1022,0.01602],"object_to_goal_dist_end":0.26864,"object_to_goal_dist_start":0.26864,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3024.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.53879,0.17567,0.32174],"tcp_start":[0.5409,0.17647,0.23358],"tcp_to_object_dist_end":0.31965,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```