## Search State

- **Seed**: 0
- **Iteration**: 15 / 15

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

## Current Skill (Q=0.309) — your mutation base

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

- **Composite score**: 0.309
- **task_score** (E): 0.004
- **fitness_score**: 0.256  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.333
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.280

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1766 |
| descend_1 | 1.00 | 1.00 | 0.1052 |
| push_1 | 0.00 | 1.00 | 0.0001 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.495, 0.088, 0.165) | (0.498, 0.080, 0.040)→(0.500, 0.081, 0.034) | 0.161→0.161 | 1.00 / 1.000 | 0.557 | 2.179 |
| descend_1 | descend | 1.00 / force_exceeded | (0.495, 0.088, 0.165)→(0.496, 0.081, 0.060) | (0.500, 0.081, 0.034)→(0.500, 0.081, 0.034) | 0.161→0.161 | 1.00 / 2.000 | 30.937 | 30.937 |
| push_1 | push | 0.00 / guard_failure | (0.495, 0.079, 0.060)→(0.495, 0.079, 0.060) | (0.500, 0.081, 0.034)→(0.499, 0.080, 0.034) | 0.161→0.160 | 1.00 / 2.000 | 21.444 | 43.144 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.005
- alignment_error: None
- force_efficiency: 0.073
- terminal_score: 0.005
- phase_score: 0.443
- phase_breakdown.traverse_channel_score: 0.003
- phase_breakdown.contact_peg_score: 0.924
- phase_breakdown.reach_peg_top_score: 0.822

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.268
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.005
- **Median Q (composite search score)**: 0.306
- **K-run variance**: 0.0001
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.366


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.67089,"average_solve_count":79.0,"average_success_count":79.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.09816,"descend_1.contact_force_threshold":23.05998,"descend_1.descend_speed":0.0996,"push_1.push_distance":0.10492,"push_1.push_speed":0.03371},"optimized_scores":{"best_composite_score":0.3003,"best_fitness_score":0.24696,"best_task_score":0.00353},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":13.0,"contact_point_centroid":[0.49131,0.05243,0.00932],"force_p95":41.72301,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":46.81696,"mean_force":27.90977,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50013,0.06159,0.05973]},{"body_a":"attachment","body_b":"peg","contact_count":13.0,"contact_point_centroid":[0.51199,0.06151,0.05843],"force_p95":41.23831,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":46.33682,"mean_force":27.42459,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50013,0.06159,0.05973]},{"body_a":"peg","body_b":"channel_base_body","contact_count":498.0,"contact_point_centroid":[0.5038,0.06166,0.00938],"force_p95":0.55549,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":31.22145,"mean_force":0.60823,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50273,0.06577,0.11114]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.51237,0.06141,0.05875],"force_p95":30.75157,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":30.75157,"mean_force":30.75157,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50051,0.06199,0.06048]},{"body_a":"peg","body_b":"channel_base_body","contact_count":619.0,"contact_point_centroid":[0.50363,0.06157,0.00935],"force_p95":0.59275,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.17216,"mean_force":0.55936,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50296,0.13267,0.22796]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":19.0,"contact_point_centroid":[0.52623,0.06158,0.03217],"force_p95":0.5921,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.62339,"mean_force":0.34148,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49974,0.19864,0.29869]}],"total_contact_groups":6},"final_pose_error":0.10364,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50324,0.06094,0.03397],"final_tcp_position":[0.49996,0.0607,0.05943],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.51096,0.06158,0.04]},"peak_contact_force":46.81696,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":642.0,"n_steps_budget":1000.0,"object_pos_end":[0.50374,0.0616,0.03378],"object_pos_start":[0.51096,0.06158,0.04],"object_to_goal_dist_end":0.14178,"object_to_goal_dist_start":0.14201,"object_z_max":0.04,"peak_contact_force":0.54352,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":638.0,"raw_peak_contact_force":2.17216,"subtask_id":"reach_peg_top","tcp_end":[0.50729,0.06985,0.16387],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.1304,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":498.0,"n_steps_budget":720.0,"object_pos_end":[0.50378,0.06155,0.03379],"object_pos_start":[0.50374,0.0616,0.03378],"object_to_goal_dist_end":0.14173,"object_to_goal_dist_start":0.14178,"object_z_max":0.03379,"peak_contact_force":31.22145,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":499.0,"raw_peak_contact_force":31.22145,"subtask_id":"contact_peg","tcp_end":[0.50051,0.06198,0.06027],"tcp_start":[0.50729,0.06985,0.16387],"tcp_to_object_dist_end":0.02669,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":13.0,"n_steps_budget":1000.0,"object_pos_end":[0.50321,0.06112,0.03392],"object_pos_start":[0.50378,0.06155,0.03379],"object_to_goal_dist_end":0.14128,"object_to_goal_dist_start":0.14173,"object_z_max":0.03395,"peak_contact_force":36.75749,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":26.0,"raw_peak_contact_force":46.81696,"subtask_id":"traverse_channel","tcp_end":[0.49996,0.0607,0.05943],"tcp_start":[0.49995,0.06081,0.05945],"tcp_to_object_dist_end":0.02572,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.75714,"average_solve_count":70.0,"average_success_count":70.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.1129,"descend_1.contact_force_threshold":18.96548,"descend_1.descend_speed":0.07458,"push_1.push_distance":0.12526,"push_1.push_speed":0.07697},"optimized_scores":{"best_composite_score":0.32129,"best_fitness_score":0.26796,"best_task_score":0.00482},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":551.0,"contact_point_centroid":[0.50088,0.11593,0.00942],"force_p95":0.60906,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":46.33285,"mean_force":0.62584,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49631,0.11887,0.11235]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.50882,0.11516,0.05888],"force_p95":45.61071,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":45.61071,"mean_force":45.61071,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49697,0.11591,0.06057]},{"body_a":"peg","body_b":"channel_base_body","contact_count":12.0,"contact_point_centroid":[0.49193,0.1122,0.00932],"force_p95":40.52638,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":42.69143,"mean_force":22.68722,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49672,0.11522,0.05999]},{"body_a":"attachment","body_b":"peg","contact_count":12.0,"contact_point_centroid":[0.50855,0.11514,0.05859],"force_p95":39.96449,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":42.1625,"mean_force":22.205,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49672,0.11522,0.05999]},{"body_a":"peg","body_b":"channel_base_body","contact_count":460.0,"contact_point_centroid":[0.50094,0.11597,0.00938],"force_p95":0.61632,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.92055,"mean_force":0.56004,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49824,0.16042,0.23084]}],"total_contact_groups":5},"final_pose_error":0.12324,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50046,0.11527,0.03393],"final_tcp_position":[0.49653,0.11389,0.05968],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50095,0.11604,0.04]},"peak_contact_force":46.33285,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":476.0,"n_steps_budget":900.0,"object_pos_end":[0.50096,0.11611,0.03389],"object_pos_start":[0.50095,0.11604,0.04],"object_to_goal_dist_end":0.19621,"object_to_goal_dist_start":0.19604,"object_z_max":0.04,"peak_contact_force":0.58102,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":460.0,"raw_peak_contact_force":1.92055,"subtask_id":"reach_peg_top","tcp_end":[0.49806,0.1224,0.1669],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.1332,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":551.0,"n_steps_budget":960.0,"object_pos_end":[0.50101,0.11616,0.03397],"object_pos_start":[0.50096,0.11611,0.03389],"object_to_goal_dist_end":0.19626,"object_to_goal_dist_start":0.19621,"object_z_max":0.03399,"peak_contact_force":46.33285,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":552.0,"raw_peak_contact_force":46.33285,"subtask_id":"contact_peg","tcp_end":[0.49704,0.11591,0.06042],"tcp_start":[0.49806,0.1224,0.1669],"tcp_to_object_dist_end":0.02675,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":12.0,"n_steps_budget":1000.0,"object_pos_end":[0.5004,0.11548,0.0339],"object_pos_start":[0.50101,0.11616,0.03397],"object_to_goal_dist_end":0.19557,"object_to_goal_dist_start":0.19626,"object_z_max":0.03397,"peak_contact_force":6.83405,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":24.0,"raw_peak_contact_force":42.69143,"subtask_id":"traverse_channel","tcp_end":[0.49653,0.11389,0.05968],"tcp_start":[0.49651,0.11402,0.05972],"tcp_to_object_dist_end":0.02612,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.43981,"average_solve_count":216.0,"average_success_count":216.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.04235,"descend_1.contact_force_threshold":10.07165,"descend_1.descend_speed":0.01067,"push_1.push_distance":0.17508,"push_1.push_speed":0.09152},"optimized_scores":{"best_composite_score":0.30615,"best_fitness_score":0.25282,"best_task_score":0.00324},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":12.0,"contact_point_centroid":[0.48098,0.06305,0.00937],"force_p95":37.70143,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":39.9223,"mean_force":25.26396,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48942,0.06346,0.06027]},{"body_a":"attachment","body_b":"peg","contact_count":12.0,"contact_point_centroid":[0.50124,0.06334,0.05889],"force_p95":37.19235,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":39.43176,"mean_force":24.7644,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48942,0.06346,0.06027]},{"body_a":"peg","body_b":"channel_base_body","contact_count":782.0,"contact_point_centroid":[0.49519,0.06382,0.0094],"force_p95":0.55075,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":15.25729,"mean_force":0.56405,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.48324,0.06803,0.11055]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.5014,0.06269,0.05903],"force_p95":14.73691,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":14.73691,"mean_force":14.73691,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.48963,0.06419,0.06073]},{"body_a":"peg","body_b":"channel_base_body","contact_count":651.0,"contact_point_centroid":[0.49536,0.06398,0.00937],"force_p95":0.56718,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.44546,"mean_force":0.55863,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48851,0.13392,0.22831]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":28.0,"contact_point_centroid":[0.47133,0.06388,0.03676],"force_p95":0.92436,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.16907,"mean_force":0.37063,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49924,0.19819,0.29789]}],"total_contact_groups":6},"final_pose_error":0.17304,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49431,0.06309,0.03425],"final_tcp_position":[0.48929,0.06214,0.06],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48093,0.06388,0.04]},"peak_contact_force":39.9223,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":678.0,"n_steps_budget":1000.0,"object_pos_end":[0.49487,0.06381,0.03396],"object_pos_start":[0.48093,0.06388,0.04],"object_to_goal_dist_end":0.14403,"object_to_goal_dist_start":0.14514,"object_z_max":0.04,"peak_contact_force":0.54597,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":679.0,"raw_peak_contact_force":2.44546,"subtask_id":"reach_peg_top","tcp_end":[0.47934,0.07231,0.16468],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.13191,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":782.0,"n_steps_budget":1000.0,"object_pos_end":[0.49498,0.06415,0.03403],"object_pos_start":[0.49487,0.06381,0.03396],"object_to_goal_dist_end":0.14436,"object_to_goal_dist_start":0.14403,"object_z_max":0.03403,"peak_contact_force":15.25729,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":783.0,"raw_peak_contact_force":15.25729,"subtask_id":"contact_peg","tcp_end":[0.48965,0.06418,0.06062],"tcp_start":[0.47934,0.07231,0.16468],"tcp_to_object_dist_end":0.02711,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":12.0,"n_steps_budget":1000.0,"object_pos_end":[0.4943,0.0633,0.03423],"object_pos_start":[0.49498,0.06415,0.03403],"object_to_goal_dist_end":0.14353,"object_to_goal_dist_start":0.14436,"object_z_max":0.03425,"peak_contact_force":20.74159,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":24.0,"raw_peak_contact_force":39.9223,"subtask_id":"traverse_channel","tcp_end":[0.48929,0.06214,0.06],"tcp_start":[0.48929,0.06227,0.06003],"tcp_to_object_dist_end":0.02628,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```