## Search State

- **Seed**: 0
- **Iteration**: 1 / 15

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
- Frozen realised-scene SHA-256: `f07a678caf5b8ea43212ad5a337315ad102b1ae725b01cf669f7af9bd0eea2ea`
- Frozen object start: [0.5136961687321454, -0.02302132862361297, 0.03]
- Frozen task target: [0.5540973523936195, 0.15165276355285293, 0.22199053588004086]
- Goal object position: (0.5540973523936195, 0.15165276355285293, 0.22199053588004086)
- place_goal_position (task success criterion — final object 3D position must be close to the realised airborne target here): (0.5540973523936195, 0.15165276355285293, 0.22199053588004086)
- Grasp/lift components are optimiser fitness diagnostics only; canonical task_score is final object-to-realised-target proximity.
- Object initial pose: (0.5136961687321454, -0.02302132862361297, 0.03)
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
  frozen_object_start: [0.5137, -0.023, 0.03]
  frozen_task_target: [0.5541, 0.1517, 0.222]
  frozen_object_starts: {'grasp_target': [0.5136961687321454, -0.02302132862361297, 0.03]}
  frozen_targets: {'place_target': [0.5540973523936195, 0.15165276355285293, 0.22199053588004086]}
  goal_tolerance_m: 0.02
  force_limit_n: 20
  force_scale_n: 5
  realized_scene_sha256: f07a678caf5b8ea43212ad5a337315ad102b1ae725b01cf669f7af9bd0eea2ea

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
| `object` | offset from object initial position (0.5136961687321454, -0.02302132862361297, 0.03) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.5540973523936195, 0.15165276355285293, 0.22199053588004086) | final destination targets |
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

## Current Skill (Q=-0.171) — your mutation base

```yaml
skill: grasp_place
phases:
- id: insert_1
  type: insert
  generator: linear_cartesian
  control: impedance_control
  termination: pose_tolerance
  parameters:
    insertion_force:
      type: scalar
      range:
      - 1.0
      - 20.0
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
- id: push_1
  type: push
  generator: impedance_motion
  control: position_control
  termination: time_limit
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
- id: retract_1
  type: retract
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  parameters:
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1
- id: lift_1
  type: lift
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
- id: insert_2
  type: insert
  generator: impedance_motion
  control: impedance_control
  termination: force_exceeded
  parameters:
    insertion_depth:
      type: scalar
      range:
      - 0.01
      - 0.15
    insertion_force:
      type: scalar
      range:
      - 1.0
      - 20.0
- id: push_2
  type: push
  generator: linear_cartesian
  control: impedance_control
  termination: time_limit
  parameters:
    push_distance:
      type: scalar
      range:
      - 0.02
      - 0.2

```

## Design Metrics

- **Composite score**: -0.171
- **task_score** (E): 0.180
- **fitness_score**: 0.179  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.200
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.550

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| insert_1 | 0.00 | 1.00 | 0.2373 |
| approach_1 | 1.00 | 1.00 | 0.1833 |
| push_1 | 1.00 | 1.00 | 0.0590 |
| retract_1 | 0.00 | 1.00 | 0.0581 |
| lift_1 | 1.00 | 1.00 | 0.1559 |
| insert_2 | 1.00 | 1.00 | 0.0001 |
| push_2 | 1.00 | 1.00 | 0.1640 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| insert_1 | insert | 0.00 / step_budget | (0.500, -0.000, 0.301)→(0.574, 0.155, 0.137) | (0.497, 0.001, 0.030)→(0.497, 0.001, 0.026) | 0.263→0.265 | 1.00 / 4.000 | 0.123 | 0.138 |
| approach_1 | approach | 1.00 / step_budget | (0.574, 0.155, 0.137)→(0.497, 0.010, 0.059) | (0.497, 0.001, 0.026)→(0.493, -0.007, 0.022) | 0.265→0.274 | 1.00 / 6.333 | 0.434 | 0.440 |
| push_1 | push | 1.00 / time_limit | (0.497, 0.010, 0.059)→(0.522, 0.063, 0.065) | (0.493, -0.007, 0.022)→(0.500, 0.013, 0.026) | 0.274→0.256 | 1.00 / 4.667 | 27.310 | 0.461 |
| retract_1 | retract | 0.00 / step_budget | (0.522, 0.063, 0.065)→(0.537, 0.104, 0.098) | (0.500, 0.013, 0.026)→(0.497, 0.008, 0.026) | 0.256→0.260 | 1.00 / 4.000 | 0.123 | 0.323 |
| lift_1 | lift | 1.00 / step_budget | (0.537, 0.104, 0.098)→(0.495, 0.012, 0.215) | (0.497, 0.008, 0.026)→(0.497, 0.008, 0.026) | 0.260→0.260 | 1.00 / 4.000 | 0.123 | 0.123 |
| insert_2 | insert | 1.00 / force_exceeded | (0.495, 0.012, 0.215)→(0.495, 0.012, 0.215) | (0.497, 0.008, 0.026)→(0.497, 0.008, 0.026) | 0.260→0.260 | 1.00 / 4.000 | 287.519 | 0.123 |
| push_2 | push | 1.00 / time_limit | (0.495, 0.012, 0.215)→(0.561, 0.134, 0.131) | (0.497, 0.008, 0.026)→(0.497, 0.008, 0.026) | 0.260→0.260 | 1.00 / 4.000 | 27.129 | 0.123 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 0.000
- transport_retention: None
- grasp_place_fitness: 0.181

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.181
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.218
- **Median Q (composite search score)**: -0.171
- **K-run variance**: 0.0000
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.408


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `096c354712624ed6bd8f9b9cbbbc2b7d35a94d9c1517cfb8353e2e383be5aaf0`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.05,0.05],"goal_z_delta":0.15,"object_xy_delta":[0.05,0.05]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `3798aa6551d21849355469c7d63897f628ac7de9267c18bb4301fe6cfaae0164`; realized-scene SHA-256: `f07a678caf5b8ea43212ad5a337315ad102b1ae725b01cf669f7af9bd0eea2ea`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.5137,-0.02302,0.03]},{"name":"goal","value":[0.5541,0.15165,0.22199]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.5137,-0.02302,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.5541,0.15165,0.22199]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.58848,"average_solve_count":243.0,"average_success_count":243.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.05109,"insert_1.insertion_force":13.21662,"insert_2.insertion_depth":0.04982,"insert_2.insertion_force":11.52737,"push_1.push_distance":0.17742,"push_1.push_speed":0.0135,"push_2.push_distance":0.15291,"retract_1.speed":0.02615},"optimized_scores":{"best_composite_score":-0.16867,"best_fitness_score":0.18133,"best_task_score":0.1745},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":3547.0,"contact_point_centroid":[0.5088,-0.0167,-0.00521],"force_p95":0.61584,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.68884,"mean_force":0.3247,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51971,0.0164,0.05135]},{"body_a":"world","body_b":"grasp_target","contact_count":2793.0,"contact_point_centroid":[0.51328,-0.0234,-0.00229],"force_p95":0.39181,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.61723,"mean_force":0.14632,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.54178,0.07207,0.09125]},{"body_a":"world","body_b":"grasp_target","contact_count":3885.0,"contact_point_centroid":[0.5062,-0.0147,-0.00207],"force_p95":0.13671,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.48329,"mean_force":0.12733,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.53155,0.06544,0.08216]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":9390.0,"contact_point_centroid":[0.51913,-0.02662,0.04581],"force_p95":0.16862,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24013,"mean_force":0.0715,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51951,0.01596,0.05123]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":720.0,"contact_point_centroid":[0.52143,-0.04109,0.04989],"force_p95":0.14987,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17163,"mean_force":0.08125,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.517,0.00082,0.05678]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":47.0,"contact_point_centroid":[0.52466,0.00104,0.05297],"force_p95":0.14238,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15343,"mean_force":0.07062,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.53121,0.04747,0.0581]},{"body_a":"world","body_b":"grasp_target","contact_count":3996.0,"contact_point_centroid":[0.5137,-0.02302,-0.00196],"force_p95":0.12459,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12275,"phase_index":0.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.53682,0.07971,0.21414]},{"body_a":"world","body_b":"grasp_target","contact_count":3612.0,"contact_point_centroid":[0.50587,-0.01523,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":4.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51696,0.03348,0.15847]},{"body_a":"world","body_b":"grasp_target","contact_count":4.0,"contact_point_centroid":[0.50587,-0.01523,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":5.0,"phase_name":"insert_2","phase_type":"insert","tcp_position_centroid":[0.50375,-0.01127,0.21523]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.50587,-0.01523,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"push_2","phase_type":"push","tcp_position_centroid":[0.5302,0.05421,0.17334]}],"total_contact_groups":10},"final_pose_error":0.09478,"key_states":{"actual_goal_position":[0.5541,0.15165,0.22199],"final_object_position":[0.50587,-0.01523,0.02602],"final_tcp_position":[0.56055,0.12145,0.13545],"realised_goal_position":[0.5541,0.15165,0.22199],"realised_object_initial_position":[0.5137,-0.02302,0.03]},"peak_contact_force":271.79469,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5137,-0.02302,0.02602],"object_pos_start":[0.5137,-0.02302,0.03],"object_to_goal_dist_end":0.26561,"object_to_goal_dist_start":0.26269,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":3996.0,"raw_peak_contact_force":0.13845,"tcp_end":[0.57391,0.15482,0.13706],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.21814,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":6.0,"n_steps":715.0,"n_steps_budget":1000.0,"object_pos_end":[0.50774,-0.03738,0.01952],"object_pos_start":[0.5137,-0.02302,0.02602],"object_to_goal_dist_end":0.28085,"object_to_goal_dist_start":0.26561,"object_z_max":0.02602,"peak_contact_force":0.59946,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3513.0,"raw_peak_contact_force":0.61723,"tcp_end":[0.51211,-0.01337,0.04998],"tcp_start":[0.57391,0.15482,0.13706],"tcp_to_object_dist_end":0.03903,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51634,-0.00483,0.02452],"object_pos_start":[0.50774,-0.03738,0.01952],"object_to_goal_dist_end":0.25477,"object_to_goal_dist_start":0.28085,"object_z_max":0.02452,"peak_contact_force":0.48184,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":12937.0,"raw_peak_contact_force":0.68884,"tcp_end":[0.53205,0.04665,0.05796],"tcp_start":[0.51211,-0.01337,0.04998],"tcp_to_object_dist_end":0.06336,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50587,-0.01523,0.02602],"object_pos_start":[0.51634,-0.00483,0.02452],"object_to_goal_dist_end":0.26188,"object_to_goal_dist_start":0.25477,"object_z_max":0.02617,"peak_contact_force":0.12263,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3932.0,"raw_peak_contact_force":0.48329,"tcp_end":[0.53473,0.08033,0.10525],"tcp_start":[0.53205,0.04665,0.05796],"tcp_to_object_dist_end":0.12744,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":903.0,"n_steps_budget":990.0,"object_pos_end":[0.50587,-0.01523,0.02602],"object_pos_start":[0.50587,-0.01523,0.02602],"object_to_goal_dist_end":0.26188,"object_to_goal_dist_start":0.26188,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":3612.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.50375,-0.01127,0.21523],"tcp_start":[0.53473,0.08033,0.10525],"tcp_to_object_dist_end":0.18927,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.50587,-0.01523,0.02602],"object_pos_start":[0.50587,-0.01523,0.02602],"object_to_goal_dist_end":0.26188,"object_to_goal_dist_start":0.26188,"object_z_max":0.02602,"peak_contact_force":271.79469,"phase_name":"insert_2","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":4.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.50379,-0.01133,0.21528],"tcp_start":[0.50375,-0.01127,0.21523],"tcp_to_object_dist_end":0.18932,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50587,-0.01523,0.02602],"object_pos_start":[0.50587,-0.01523,0.02602],"object_to_goal_dist_end":0.26188,"object_to_goal_dist_start":0.26188,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"push_2","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.56055,0.12145,0.13545],"tcp_start":[0.50379,-0.01133,0.21528],"tcp_to_object_dist_end":0.18343,"terminated_normally":true,"termination_reason":"time_limit"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `ed2df336ade3d991e9495251c8398520a59dd014a70bd2d7bb71dc7aefccaa8a`; realized-scene SHA-256: `a2ed2c4162d37489f2d2d0fa0373774d72c951d58f2469e0ba2d602ff46b6cfb`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50118,0.04505,0.03]},{"name":"goal","value":[0.56442,0.24486,0.14677]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.50118,0.04505,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.56442,0.24486,0.14677]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.51883,"average_solve_count":239.0,"average_success_count":239.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.0505,"insert_1.insertion_force":4.22848,"insert_2.insertion_depth":0.04694,"insert_2.insertion_force":13.06458,"push_1.push_distance":0.05537,"push_1.push_speed":0.01313,"push_2.push_distance":0.19166,"retract_1.speed":0.01723},"optimized_scores":{"best_composite_score":-0.17129,"best_fitness_score":0.17871,"best_task_score":0.21805},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":1779.0,"contact_point_centroid":[0.5011,0.04505,-0.00215],"force_p95":0.30415,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.58005,"mean_force":0.14026,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.53792,0.10589,0.0932]},{"body_a":"world","body_b":"grasp_target","contact_count":3202.0,"contact_point_centroid":[0.49997,0.05396,-0.003],"force_p95":0.39136,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.57009,"mean_force":0.19161,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51053,0.07192,0.05306]},{"body_a":"world","body_b":"grasp_target","contact_count":3127.0,"contact_point_centroid":[0.50571,0.06354,-0.00255],"force_p95":0.34251,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.36367,"mean_force":0.15841,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.52984,0.12779,0.07336]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":862.0,"contact_point_centroid":[0.52425,0.0649,0.05443],"force_p95":0.05745,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22476,"mean_force":0.02975,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.52475,0.10494,0.06139]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3540.0,"contact_point_centroid":[0.51588,0.03249,0.04652],"force_p95":0.15397,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18468,"mean_force":0.06417,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51103,0.07231,0.05344]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":374.0,"contact_point_centroid":[0.51471,0.02107,0.051],"force_p95":0.1385,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1492,"mean_force":0.08724,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50816,0.06203,0.05852]},{"body_a":"world","body_b":"grasp_target","contact_count":3996.0,"contact_point_centroid":[0.50118,0.04505,-0.00196],"force_p95":0.12459,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12275,"phase_index":0.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.53682,0.07971,0.21414]},{"body_a":"world","body_b":"grasp_target","contact_count":3852.0,"contact_point_centroid":[0.50815,0.05928,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":4.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51809,0.1037,0.14779]},{"body_a":"world","body_b":"grasp_target","contact_count":4.0,"contact_point_centroid":[0.50815,0.05928,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":5.0,"phase_name":"insert_2","phase_type":"insert","tcp_position_centroid":[0.5059,0.06229,0.21463]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.50815,0.05928,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"push_2","phase_type":"push","tcp_position_centroid":[0.53971,0.11622,0.16288]}],"total_contact_groups":10},"final_pose_error":0.03919,"key_states":{"actual_goal_position":[0.56442,0.24486,0.14677],"final_object_position":[0.50815,0.05928,0.02602],"final_tcp_position":[0.57734,0.17179,0.11505],"realised_goal_position":[0.56442,0.24486,0.14677],"realised_object_initial_position":[0.50118,0.04505,0.03]},"peak_contact_force":307.29137,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.03],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.23992,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":3996.0,"raw_peak_contact_force":0.13845,"tcp_end":[0.57391,0.15482,0.13706],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.17225,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":446.0,"n_steps_budget":1000.0,"object_pos_end":[0.49624,0.03791,0.02085],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.25166,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"peak_contact_force":0.58005,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2153.0,"raw_peak_contact_force":0.58005,"tcp_end":[0.50316,0.05455,0.05272],"tcp_start":[0.57391,0.15482,0.13706],"tcp_to_object_dist_end":0.03661,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5067,0.0631,0.0269],"object_pos_start":[0.49624,0.03791,0.02085],"object_to_goal_dist_end":0.22525,"object_to_goal_dist_start":0.25166,"object_z_max":0.02692,"peak_contact_force":0.3069,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":6742.0,"raw_peak_contact_force":0.57009,"tcp_end":[0.5257,0.09493,0.05993],"tcp_start":[0.50316,0.05455,0.05272],"tcp_to_object_dist_end":0.04965,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50815,0.05928,0.02602],"object_pos_start":[0.5067,0.0631,0.0269],"object_to_goal_dist_end":0.22845,"object_to_goal_dist_start":0.22525,"object_z_max":0.02773,"peak_contact_force":0.12263,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3989.0,"raw_peak_contact_force":0.36367,"tcp_end":[0.53492,0.14748,0.08447],"tcp_start":[0.5257,0.09493,0.05993],"tcp_to_object_dist_end":0.10915,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":963.0,"n_steps_budget":1000.0,"object_pos_end":[0.50815,0.05928,0.02602],"object_pos_start":[0.50815,0.05928,0.02602],"object_to_goal_dist_end":0.22845,"object_to_goal_dist_start":0.22845,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":3852.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.5059,0.06229,0.21463],"tcp_start":[0.53492,0.14748,0.08447],"tcp_to_object_dist_end":0.18865,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.50815,0.05928,0.02602],"object_pos_start":[0.50815,0.05928,0.02602],"object_to_goal_dist_end":0.22845,"object_to_goal_dist_start":0.22845,"object_z_max":0.02602,"peak_contact_force":307.29137,"phase_name":"insert_2","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":4.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.50595,0.06225,0.21469],"tcp_start":[0.5059,0.06229,0.21463],"tcp_to_object_dist_end":0.18871,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50815,0.05928,0.02602],"object_pos_start":[0.50815,0.05928,0.02602],"object_to_goal_dist_end":0.22845,"object_to_goal_dist_start":0.22845,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"push_2","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.57734,0.17179,0.11505],"tcp_start":[0.50595,0.06225,0.21469],"tcp_to_object_dist_end":0.15929,"terminated_normally":true,"termination_reason":"time_limit"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `291bc6f2bd023fc25503740a7343328e565e43fc71fa3c9c5d2fdbe2d4351fd2`; realized-scene SHA-256: `67b45068113fe0ef6f199d4981822d51bd0bd66bb4f388f7402a08094b41852a`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.47616,-0.02015,0.03]},{"name":"goal","value":[0.63142,0.15919,0.19002]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.47616,-0.02015,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.63142,0.15919,0.19002]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.6,"average_solve_count":245.0,"average_success_count":245.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.0762,"insert_1.insertion_force":14.43491,"insert_2.insertion_depth":0.0921,"insert_2.insertion_force":15.02338,"push_1.push_distance":0.06424,"push_1.push_speed":0.02661,"push_2.push_distance":0.07592,"retract_1.speed":0.01404},"optimized_scores":{"best_composite_score":-0.17444,"best_fitness_score":0.17556,"best_task_score":0.14623},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":3996.0,"contact_point_centroid":[0.47616,-0.02015,-0.00196],"force_p95":0.12459,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12275,"phase_index":0.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.53682,0.07971,0.21414]},{"body_a":"world","body_b":"grasp_target","contact_count":2876.0,"contact_point_centroid":[0.47616,-0.02015,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.52391,0.07218,0.10273]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.47616,-0.02015,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49019,0.01932,0.07286]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.47616,-0.02015,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.52462,0.06755,0.0901]},{"body_a":"world","body_b":"grasp_target","contact_count":3972.0,"contact_point_centroid":[0.47616,-0.02015,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":4.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.50626,0.03244,0.15903]},{"body_a":"world","body_b":"grasp_target","contact_count":4.0,"contact_point_centroid":[0.47616,-0.02015,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"insert_2","phase_type":"insert","tcp_position_centroid":[0.47541,-0.01621,0.21616]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.47616,-0.02015,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"push_2","phase_type":"push","tcp_position_centroid":[0.50815,0.04628,0.17683]}],"total_contact_groups":7},"final_pose_error":0.11316,"key_states":{"actual_goal_position":[0.63142,0.15919,0.19002],"final_object_position":[0.47616,-0.02015,0.02602],"final_tcp_position":[0.54479,0.11024,0.14124],"realised_goal_position":[0.63142,0.15919,0.19002],"realised_object_initial_position":[0.47616,-0.02015,0.03]},"peak_contact_force":283.47135,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.03],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28614,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":3996.0,"raw_peak_contact_force":0.13845,"tcp_end":[0.57391,0.15482,0.13706],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.22913,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":719.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2876.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.47706,-0.01055,0.07434],"tcp_start":[0.57391,0.15482,0.13706],"tcp_to_object_dist_end":0.04927,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":81.14225,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.5072,0.04868,0.07587],"tcp_start":[0.47706,-0.01055,0.07434],"tcp_to_object_dist_end":0.09048,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.54225,0.08322,0.10575],"tcp_start":[0.5072,0.04868,0.07587],"tcp_to_object_dist_end":0.14632,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":993.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":3972.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.47541,-0.01621,0.21616],"tcp_start":[0.54225,0.08322,0.10575],"tcp_to_object_dist_end":0.19019,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":283.47135,"phase_name":"insert_2","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":4.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.47544,-0.01627,0.21621],"tcp_start":[0.47541,-0.01621,0.21616],"tcp_to_object_dist_end":0.19023,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":81.14225,"phase_name":"push_2","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.54479,0.11024,0.14124],"tcp_start":[0.47544,-0.01627,0.21621],"tcp_to_object_dist_end":0.18705,"terminated_normally":true,"termination_reason":"time_limit"}],"success":false}]}
```