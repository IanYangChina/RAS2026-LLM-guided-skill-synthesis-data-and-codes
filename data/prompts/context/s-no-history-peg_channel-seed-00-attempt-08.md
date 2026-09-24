## Search State

- **Seed**: 0
- **Iteration**: 9 / 15

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

- Task name: peg_channel
- Frozen realised-scene SHA-256: `cd60c08f71f9d10bc11dd62c79067fee574cade1f8d1192fc945700528a8d454`
- Frozen object start: [0.5109569349857164, 0.061582937101109625, 0.04]
- Frozen task target: [0.5109569349857164, -0.09841706289889038, 0.04]
- Goal object position: (0.5109569349857164, -0.09841706289889038, 0.04)
- Task success criterion: peg must traverse the channel (0.16 m long) along axis (0.0, -1.0, 0.0); score = axial progress × lateral alignment — NOT a fixed TCP endpoint
- Object initial pose: (0.5109569349857164, 0.061582937101109625, 0.04)
- Goal tolerance: 0.02 m
- Expressivity sigma: 1.0 m
- Expressivity threshold: 0.5
- Force limit: 40.0 N
- Peg body: `peg`
- Channel axis: `(0.0, -1.0, 0.0)` — use `impedance_control` to absorb lateral wall forces
- Robot initial TCP position: (0.5, 0.2, 0.3)
- Phase navigation guidance: the task `phase_target_map` may provide internal predefined TCP waypoint aliases / semantic phase ids. These names are not DSL phase types and are intentionally not enumerated here to avoid confusing ids with types. Phase `id` may be semantic, but phase `type` must be exactly one of the DSL enum values listed in the prompt.
- Primary evaluation target: **insertion depth × lateral alignment (axial progress penalised by wall deviation)**

## Scene Entities

robot:
  model: panda_pusher
  tcp_site: attachment_site
  gripper: null
  tcp_initial_world: [0.5, 0.2, 0.3]
objects:
  - name: peg
    role: manipulated_object
    dynamics: free
    geometry: cylinder
    radius_m: 0.018
    half_length_m: 0.025
  - name: channel_structure
    role: fixture
    dynamics: static
    geometry: two_parallel_walls
    inner_gap_m: 0.05
    wall_thickness_m: 0.03
    wall_height_m: 0.05
task_landmarks:
  frozen_object_start: [0.511, 0.0616, 0.04]
  frozen_task_target: [0.511, -0.0984, 0.04]
  frozen_fixture_position: [0.54, 0, 0.035]
  frozen_object_starts: {'peg': [0.5109569349857164, 0.061582937101109625, 0.04]}
  frozen_targets: {'channel_exit': [0.5109569349857164, -0.09841706289889038, 0.04]}
  frozen_fixtures: {'channel_left_wall': [0.54, 0.0, 0.035], 'channel_right_wall': [0.46, 0.0, 0.035]}
  channel_axis: [0, -1, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 40
  channel_length_m: 0.16
  force_scale_n: 5
  realized_scene_sha256: cd60c08f71f9d10bc11dd62c79067fee574cade1f8d1192fc945700528a8d454

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
| `object` | offset from object initial position (0.5109569349857164, 0.061582937101109625, 0.04) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.5109569349857164, -0.09841706289889038, 0.04) | final destination targets |
| `fixture` | offset from fixture pose (0.54, 0.0, 0.035) | approach/contact targets near fixture |

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

## Current Skill (Q=0.249) — your mutation base

```yaml
skill: peg_channel
phases:
- id: insert_1
  type: insert
  generator: linear_cartesian
  control: impedance_control
  termination: force_exceeded
- id: approach_1
  type: approach
  generator: linear_cartesian
  control: force_threshold_switch
  termination: pose_tolerance
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
- id: retract_1
  type: retract
  generator: arc_cartesian
  control: position_control
  termination: pose_tolerance
  parameters:
    retract_height:
      type: scalar
      range:
      - 0.05
      - 0.2
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
  parameters:
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1
- id: insert_2
  type: insert
  generator: impedance_motion
  control: admittance_control
  termination: force_exceeded

```

## Design Metrics

- **Composite score**: 0.249
- **task_score** (E): 0.289
- **fitness_score**: 0.529  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.280

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1773 |
| push_engage | 0.00 | 1.00 | 0.0892 |
| push_channel | 0.67 | 1.00 | 0.1865 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.495, 0.162, 0.129) | (0.498, 0.080, 0.040)→(0.500, 0.081, 0.034) | 0.161→0.161 | 1.00 / 1.000 | 0.538 | 2.179 |
| push_engage | push | 0.00 / step_budget | (0.495, 0.162, 0.129)→(0.496, 0.103, 0.063) | (0.500, 0.081, 0.034)→(0.500, 0.081, 0.034) | 0.161→0.161 | 1.00 / 1.000 | 0.530 | 0.587 |
| push_channel | push | 0.67 / step_budget | (0.496, 0.103, 0.063)→(0.500, -0.083, 0.051) | (0.500, 0.081, 0.034)→(0.498, 0.024, 0.024) | 0.161→0.106 | 1.00 / 1.333 | 74.043 | 197.190 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.314
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.314
- phase_score: 0.700
- phase_breakdown.reach_peg_score: 0.468
- phase_breakdown.traverse_channel_score: 0.800

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.546
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.314
- **Median Q (composite search score)**: 0.247
- **K-run variance**: 0.0002
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.289


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `d6915c31707ac435a9367b840736087e39a7a48adfeb36a4f94b6b3ae57cce94`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.04,0.04]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `19172182883d287409b73cab43749e937e65f1ca1d4501d52b4a913a881aad36`; realized-scene SHA-256: `cd60c08f71f9d10bc11dd62c79067fee574cade1f8d1192fc945700528a8d454`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.51096,0.06158,0.04]},{"name":"goal","value":[0.51096,-0.09842,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.51096,0.06158,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.51096,-0.09842,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.25366,"average_solve_count":205.0,"average_success_count":205.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.07297,"push_channel.push_distance":0.19002,"push_channel.push_speed":0.03226,"push_engage.engage_force":17.11078,"push_engage.engage_speed":0.06211},"optimized_scores":{"best_composite_score":0.24721,"best_fitness_score":0.52721,"best_task_score":0.28896},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg","contact_count":83.0,"contact_point_centroid":[0.50767,0.04858,0.06089],"force_p95":111.81094,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":114.26295,"mean_force":77.78713,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50227,0.03948,0.06091]},{"body_a":"peg","body_b":"channel_base_body","contact_count":181.0,"contact_point_centroid":[0.50599,0.03165,0.00896],"force_p95":108.72271,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":111.70121,"mean_force":35.80303,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.5019,0.01492,0.05875]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":14.0,"contact_point_centroid":[0.52501,0.03999,0.05972],"force_p95":23.95014,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":24.30826,"mean_force":20.56054,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50299,0.03751,0.06141]},{"body_a":"peg","body_b":"channel_base_body","contact_count":547.0,"contact_point_centroid":[0.50358,0.06156,0.00935],"force_p95":0.58347,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.17216,"mean_force":0.56134,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50278,0.17158,0.21061]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":19.0,"contact_point_centroid":[0.52623,0.06158,0.03217],"force_p95":0.5921,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.62339,"mean_force":0.34148,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49981,0.19926,0.29857]},{"body_a":"peg","body_b":"channel_base_body","contact_count":599.0,"contact_point_centroid":[0.50379,0.06157,0.00938],"force_p95":0.55529,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55715,"mean_force":0.54661,"phase_index":1.0,"phase_name":"push_engage","phase_type":"push","tcp_position_centroid":[0.50221,0.11404,0.09295]}],"total_contact_groups":6},"final_pose_error":0.04907,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.5026,0.0069,0.02377],"final_tcp_position":[0.50214,-0.07941,0.05194],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.51096,0.06158,0.04]},"peak_contact_force":114.26295,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":570.0,"n_steps_budget":1000.0,"object_pos_end":[0.50375,0.06161,0.03379],"object_pos_start":[0.51096,0.06158,0.04],"object_to_goal_dist_end":0.1418,"object_to_goal_dist_start":0.14201,"object_z_max":0.04,"peak_contact_force":0.53829,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":566.0,"raw_peak_contact_force":2.17216,"subtask_id":"reach_peg","tcp_end":[0.50698,0.14502,0.12829],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.12608,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":599.0,"n_steps_budget":930.0,"object_pos_end":[0.50373,0.0616,0.03379],"object_pos_start":[0.50375,0.06161,0.03379],"object_to_goal_dist_end":0.14178,"object_to_goal_dist_start":0.1418,"object_z_max":0.03379,"peak_contact_force":0.54168,"phase_name":"push_engage","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":599.0,"raw_peak_contact_force":0.55715,"subtask_id":"reach_peg","tcp_end":[0.50023,0.08507,0.06318],"tcp_start":[0.50698,0.14502,0.12829],"tcp_to_object_dist_end":0.03777,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":192.0,"n_steps_budget":1000.0,"object_pos_end":[0.5026,0.0069,0.02377],"object_pos_start":[0.50373,0.0616,0.03379],"object_to_goal_dist_end":0.08844,"object_to_goal_dist_start":0.14178,"object_z_max":0.03968,"peak_contact_force":0.64115,"phase_name":"push_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":278.0,"raw_peak_contact_force":114.26295,"subtask_id":"traverse_channel","tcp_end":[0.50214,-0.07941,0.05194],"tcp_start":[0.50023,0.08507,0.06318],"tcp_to_object_dist_end":0.09079,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `f24211f27d4adabdef509c8ed61621317fdbcaa86fc9ac888f85a717335bb714`; realized-scene SHA-256: `9fd07833843a6ee28e14c5e2ce05f86547005983f45e63c41c77b8dac2024c0a`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50095,0.11604,0.04]},{"name":"goal","value":[0.50095,-0.04396,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.50095,0.11604,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.50095,-0.04396,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.77419,"average_solve_count":279.0,"average_success_count":279.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.07136,"push_channel.push_distance":0.24643,"push_channel.push_speed":0.01951,"push_engage.engage_force":10.89476,"push_engage.engage_speed":0.01677},"optimized_scores":{"best_composite_score":0.26585,"best_fitness_score":0.54585,"best_task_score":0.31407},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":230.0,"contact_point_centroid":[0.50184,0.08279,0.00867],"force_p95":102.76284,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":106.0933,"mean_force":21.69122,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49836,0.03729,0.05754]},{"body_a":"attachment","body_b":"peg","contact_count":71.0,"contact_point_centroid":[0.50308,0.10119,0.06145],"force_p95":105.18162,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":105.65129,"mean_force":68.42529,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49864,0.09161,0.06124]},{"body_a":"peg","body_b":"channel_base_body","contact_count":517.0,"contact_point_centroid":[0.5009,0.11604,0.00938],"force_p95":0.61633,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.92055,"mean_force":0.5588,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49818,0.1971,0.21251]},{"body_a":"peg","body_b":"channel_base_body","contact_count":661.0,"contact_point_centroid":[0.50097,0.11599,0.00942],"force_p95":0.60629,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.64903,"mean_force":0.54306,"phase_index":1.0,"phase_name":"push_engage","phase_type":"push","tcp_position_centroid":[0.49604,0.16627,0.09366]}],"total_contact_groups":4},"final_pose_error":0.04932,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49802,0.06579,0.02419],"final_tcp_position":[0.499,-0.08107,0.05106],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50095,0.11604,0.04]},"peak_contact_force":106.0933,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":533.0,"n_steps_budget":1000.0,"object_pos_end":[0.50089,0.11608,0.03386],"object_pos_start":[0.50095,0.11604,0.04],"object_to_goal_dist_end":0.19618,"object_to_goal_dist_start":0.19604,"object_z_max":0.04,"peak_contact_force":0.52758,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":517.0,"raw_peak_contact_force":1.92055,"subtask_id":"reach_peg","tcp_end":[0.49781,0.19514,0.12917],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.12387,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":661.0,"n_steps_budget":1000.0,"object_pos_end":[0.50095,0.11616,0.03386],"object_pos_start":[0.50089,0.11608,0.03386],"object_to_goal_dist_end":0.19626,"object_to_goal_dist_start":0.19618,"object_z_max":0.03396,"peak_contact_force":0.50517,"phase_name":"push_engage","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":661.0,"raw_peak_contact_force":0.64903,"subtask_id":"reach_peg","tcp_end":[0.49701,0.13917,0.06346],"tcp_start":[0.49781,0.19514,0.12917],"tcp_to_object_dist_end":0.03769,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":240.0,"n_steps_budget":1000.0,"object_pos_end":[0.49802,0.06579,0.02419],"object_pos_start":[0.50095,0.11616,0.03386],"object_to_goal_dist_end":0.14665,"object_to_goal_dist_start":0.19626,"object_z_max":0.03951,"peak_contact_force":0.60354,"phase_name":"push_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":301.0,"raw_peak_contact_force":106.0933,"subtask_id":"traverse_channel","tcp_end":[0.499,-0.08107,0.05106],"tcp_start":[0.49701,0.13917,0.06346],"tcp_to_object_dist_end":0.1493,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `d098a7862ff18c9bbe982af3446a89a0fa6bcfa8790d7d955f65b2375d67a881`; realized-scene SHA-256: `2a92d231da5879af7af8916eb4c7dff00148227e84220c4d9643d9841dc77ee7`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.48093,0.06388,0.04]},{"name":"goal","value":[0.48093,-0.09612,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.48093,0.06388,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.48093,-0.09612,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.97255,"average_solve_count":255.0,"average_success_count":255.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.03685,"push_channel.push_distance":0.21435,"push_channel.push_speed":0.04541,"push_engage.engage_force":11.18883,"push_engage.engage_speed":0.04106},"optimized_scores":{"best_composite_score":0.23369,"best_fitness_score":0.51369,"best_task_score":0.26251},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_base_body","contact_count":121.0,"contact_point_centroid":[0.49952,-0.10043,0.06499],"force_p95":304.76395,"geom_a":"pusher_tip","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":371.21386,"mean_force":225.04681,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49707,-0.08841,0.05009]},{"body_a":"peg","body_b":"channel_base_body","contact_count":317.0,"contact_point_centroid":[0.49671,0.01422,0.0086],"force_p95":115.07131,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":117.09987,"mean_force":30.60721,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49493,-0.02885,0.05535]},{"body_a":"attachment","body_b":"peg","contact_count":114.0,"contact_point_centroid":[0.49961,0.04929,0.06111],"force_p95":115.63134,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":116.6663,"mean_force":83.34256,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49364,0.04189,0.06101]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":9.0,"contact_point_centroid":[0.47495,0.0239,0.02392],"force_p95":9.4075,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.57198,"mean_force":3.31418,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.4933,-0.08911,0.05224]},{"body_a":"peg","body_b":"channel_base_body","contact_count":564.0,"contact_point_centroid":[0.49545,0.06399,0.00937],"force_p95":0.58068,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.44546,"mean_force":0.56063,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48867,0.17267,0.21088]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":28.0,"contact_point_centroid":[0.47133,0.06388,0.03676],"force_p95":0.92436,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.16907,"mean_force":0.37063,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49932,0.19898,0.29753]},{"body_a":"peg","body_b":"channel_base_body","contact_count":945.0,"contact_point_centroid":[0.49513,0.06386,0.0094],"force_p95":0.55076,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55403,"mean_force":0.54526,"phase_index":1.0,"phase_name":"push_engage","phase_type":"push","tcp_position_centroid":[0.48439,0.11276,0.09004]}],"total_contact_groups":7},"final_pose_error":0.06276,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49427,0.00014,0.02415],"final_tcp_position":[0.50004,-0.08793,0.04908],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48093,0.06388,0.04]},"peak_contact_force":371.21386,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":591.0,"n_steps_budget":1000.0,"object_pos_end":[0.49489,0.06393,0.03395],"object_pos_start":[0.48093,0.06388,0.04],"object_to_goal_dist_end":0.14414,"object_to_goal_dist_start":0.14514,"object_z_max":0.04,"peak_contact_force":0.54736,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":592.0,"raw_peak_contact_force":2.44546,"subtask_id":"reach_peg","tcp_end":[0.47944,0.14731,0.12925],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.12757,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":945.0,"n_steps_budget":1000.0,"object_pos_end":[0.49488,0.06408,0.03403],"object_pos_start":[0.49489,0.06393,0.03395],"object_to_goal_dist_end":0.14429,"object_to_goal_dist_start":0.14414,"object_z_max":0.03403,"peak_contact_force":0.54338,"phase_name":"push_engage","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":945.0,"raw_peak_contact_force":0.55403,"subtask_id":"reach_peg","tcp_end":[0.49067,0.08544,0.06157],"tcp_start":[0.47944,0.14731,0.12925],"tcp_to_object_dist_end":0.0351,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":326.0,"n_steps_budget":1000.0,"object_pos_end":[0.49427,0.00014,0.02415],"object_pos_start":[0.49488,0.06408,0.03403],"object_to_goal_dist_end":0.08189,"object_to_goal_dist_start":0.14429,"object_z_max":0.03927,"peak_contact_force":220.88473,"phase_name":"push_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":561.0,"raw_peak_contact_force":371.21386,"subtask_id":"traverse_channel","tcp_end":[0.50004,-0.08793,0.04908],"tcp_start":[0.49067,0.08544,0.06157],"tcp_to_object_dist_end":0.09171,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
```