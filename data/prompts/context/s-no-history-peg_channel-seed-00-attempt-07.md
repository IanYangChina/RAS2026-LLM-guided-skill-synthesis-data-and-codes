## Search State

- **Seed**: 0
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

## Current Skill (Q=0.495) — your mutation base

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

- **Composite score**: 0.495
- **task_score** (E): 0.005
- **fitness_score**: 0.108  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.667
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.280

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.2235 |
| descend_1 | 1.00 | 1.00 | 0.0430 |
| push_1 | 1.00 | 1.00 | 0.0023 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.495, 0.092, 0.106) | (0.498, 0.080, 0.040)→(0.500, 0.081, 0.034) | 0.161→0.161 | 1.00 / 1.000 | 0.520 | 2.179 |
| descend_1 | align | 1.00 / force_exceeded | (0.495, 0.092, 0.106)→(0.494, 0.085, 0.064) | (0.500, 0.081, 0.034)→(0.500, 0.080, 0.034) | 0.161→0.161 | 1.00 / 2.000 | 25.864 | 25.864 |
| push_1 | push | 1.00 / force_exceeded | (0.494, 0.085, 0.064)→(0.493, 0.083, 0.062) | (0.500, 0.080, 0.034)→(0.500, 0.080, 0.034) | 0.161→0.160 | 1.00 / 2.000 | 41.087 | 41.087 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.011
- alignment_error: None
- force_efficiency: 0.136
- terminal_score: 0.007
- phase_score: 0.184
- phase_breakdown.reach_peg_score: 0.588
- phase_breakdown.traverse_channel_score: 0.011

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.113
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.007
- **Median Q (composite search score)**: 0.494
- **K-run variance**: 0.0000
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Parameters at upper bound**: push_1.push_force
- **Final σ (mean)**: 0.422


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.04412,"average_solve_count":136.0,"average_success_count":136.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.03624,"descend_1.descend_force":5.65851,"push_1.push_distance":0.20617,"push_1.push_force":39.25359,"push_1.push_speed":0.07429},"optimized_scores":{"best_composite_score":0.49058,"best_fitness_score":0.10391,"best_task_score":0.00285},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":13.0,"contact_point_centroid":[0.49476,0.05252,0.00927],"force_p95":39.4522,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":40.03386,"mean_force":29.85476,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50104,0.06674,0.06294]},{"body_a":"attachment","body_b":"peg","contact_count":13.0,"contact_point_centroid":[0.51197,0.06691,0.05837],"force_p95":39.01896,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":39.60323,"mean_force":29.40652,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50104,0.06674,0.06294]},{"body_a":"peg","body_b":"channel_base_body","contact_count":198.0,"contact_point_centroid":[0.50411,0.06157,0.00936],"force_p95":0.64162,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":26.47122,"mean_force":0.67782,"phase_index":1.0,"phase_name":"descend_1","phase_type":"align","tcp_position_centroid":[0.5031,0.07048,0.08343]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.51229,0.06722,0.05871],"force_p95":26.00125,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":26.00125,"mean_force":26.00125,"phase_index":1.0,"phase_name":"descend_1","phase_type":"align","tcp_position_centroid":[0.50135,0.0672,0.0636]},{"body_a":"peg","body_b":"channel_base_body","contact_count":458.0,"contact_point_centroid":[0.50352,0.0616,0.00933],"force_p95":0.64089,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.17216,"mean_force":0.56402,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50278,0.13537,0.19845]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":19.0,"contact_point_centroid":[0.52623,0.06158,0.03217],"force_p95":0.5921,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.62339,"mean_force":0.34148,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49968,0.19891,0.29859]}],"total_contact_groups":6},"final_pose_error":0.21269,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50327,0.06106,0.03367],"final_tcp_position":[0.50087,0.06613,0.06254],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.51096,0.06158,0.04]},"peak_contact_force":40.03386,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":481.0,"n_steps_budget":1000.0,"object_pos_end":[0.50374,0.06158,0.03376],"object_pos_start":[0.51096,0.06158,0.04],"object_to_goal_dist_end":0.14177,"object_to_goal_dist_start":0.14201,"object_z_max":0.04,"peak_contact_force":0.49427,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":477.0,"raw_peak_contact_force":2.17216,"subtask_id":"reach_peg","tcp_end":[0.50679,0.0742,0.10488],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.07229,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":198.0,"n_steps_budget":600.0,"object_pos_end":[0.5038,0.06159,0.03377],"object_pos_start":[0.50374,0.06158,0.03376],"object_to_goal_dist_end":0.14177,"object_to_goal_dist_start":0.14177,"object_z_max":0.03377,"peak_contact_force":26.47122,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":199.0,"raw_peak_contact_force":26.47122,"subtask_id":"reach_peg","tcp_end":[0.50134,0.06717,0.06344],"tcp_start":[0.50679,0.0742,0.10488],"tcp_to_object_dist_end":0.0303,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":13.0,"n_steps_budget":1000.0,"object_pos_end":[0.50327,0.06106,0.03367],"object_pos_start":[0.5038,0.06159,0.03377],"object_to_goal_dist_end":0.14124,"object_to_goal_dist_start":0.14177,"object_z_max":0.03377,"peak_contact_force":40.03386,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":26.0,"raw_peak_contact_force":40.03386,"subtask_id":"traverse_channel","tcp_end":[0.50087,0.06613,0.06254],"tcp_start":[0.50134,0.06717,0.06344],"tcp_to_object_dist_end":0.02941,"terminated_normally":true,"termination_reason":"force_exceeded"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.46154,"average_solve_count":91.0,"average_success_count":91.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.06209,"descend_1.descend_force":9.94927,"push_1.push_distance":0.24159,"push_1.push_force":39.9089,"push_1.push_speed":0.0627},"optimized_scores":{"best_composite_score":0.49413,"best_fitness_score":0.10747,"best_task_score":0.00382},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":17.0,"contact_point_centroid":[0.49527,0.10391,0.00931],"force_p95":39.38709,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":40.01466,"mean_force":30.66048,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49532,0.11857,0.06288]},{"body_a":"attachment","body_b":"peg","contact_count":17.0,"contact_point_centroid":[0.50627,0.11898,0.05838],"force_p95":38.95362,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":39.58186,"mean_force":30.20245,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49532,0.11857,0.06288]},{"body_a":"peg","body_b":"channel_base_body","contact_count":221.0,"contact_point_centroid":[0.50074,0.11611,0.00942],"force_p95":0.59607,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":20.81535,"mean_force":0.63532,"phase_index":1.0,"phase_name":"descend_1","phase_type":"align","tcp_position_centroid":[0.49565,0.12141,0.08454]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.50661,0.11926,0.05885],"force_p95":20.4323,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":20.4323,"mean_force":20.4323,"phase_index":1.0,"phase_name":"descend_1","phase_type":"align","tcp_position_centroid":[0.49565,0.11911,0.0637]},{"body_a":"peg","body_b":"channel_base_body","contact_count":392.0,"contact_point_centroid":[0.50101,0.11602,0.00936],"force_p95":0.62625,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.92055,"mean_force":0.56436,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49829,0.16154,0.20141]}],"total_contact_groups":5},"final_pose_error":0.24523,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50049,0.11543,0.03372],"final_tcp_position":[0.49508,0.11798,0.06245],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50095,0.11604,0.04]},"peak_contact_force":40.01466,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":408.0,"n_steps_budget":1000.0,"object_pos_end":[0.50096,0.1161,0.03392],"object_pos_start":[0.50095,0.11604,0.04],"object_to_goal_dist_end":0.1962,"object_to_goal_dist_start":0.19604,"object_z_max":0.04,"peak_contact_force":0.519,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":392.0,"raw_peak_contact_force":1.92055,"subtask_id":"reach_peg","tcp_end":[0.49785,0.12439,0.10784],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.07445,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":221.0,"n_steps_budget":600.0,"object_pos_end":[0.50095,0.11608,0.03387],"object_pos_start":[0.50096,0.1161,0.03392],"object_to_goal_dist_end":0.19618,"object_to_goal_dist_start":0.1962,"object_z_max":0.03398,"peak_contact_force":20.81535,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":222.0,"raw_peak_contact_force":20.81535,"subtask_id":"reach_peg","tcp_end":[0.49569,0.1191,0.06352],"tcp_start":[0.49785,0.12439,0.10784],"tcp_to_object_dist_end":0.03027,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":17.0,"n_steps_budget":1000.0,"object_pos_end":[0.50049,0.11543,0.03372],"object_pos_start":[0.50095,0.11608,0.03387],"object_to_goal_dist_end":0.19553,"object_to_goal_dist_start":0.19618,"object_z_max":0.03387,"peak_contact_force":40.01466,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":34.0,"raw_peak_contact_force":40.01466,"subtask_id":"traverse_channel","tcp_end":[0.49508,0.11798,0.06245],"tcp_start":[0.49569,0.1191,0.06352],"tcp_to_object_dist_end":0.02934,"terminated_normally":true,"termination_reason":"force_exceeded"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.44444,"average_solve_count":99.0,"average_success_count":99.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.06337,"descend_1.descend_force":9.59659,"push_1.push_distance":0.22737,"push_1.push_force":40.0,"push_1.push_speed":0.05566},"optimized_scores":{"best_composite_score":0.49994,"best_fitness_score":0.11328,"best_task_score":0.00722},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":42.0,"contact_point_centroid":[0.49098,0.05511,0.0093],"force_p95":39.80677,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":43.21219,"mean_force":33.13111,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48322,0.068,0.06309]},{"body_a":"attachment","body_b":"peg","contact_count":42.0,"contact_point_centroid":[0.49395,0.06829,0.05819],"force_p95":39.38425,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":42.70024,"mean_force":32.66643,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48322,0.068,0.06309]},{"body_a":"peg","body_b":"channel_base_body","contact_count":267.0,"contact_point_centroid":[0.49477,0.06385,0.0094],"force_p95":0.55066,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":30.30432,"mean_force":0.65706,"phase_index":1.0,"phase_name":"descend_1","phase_type":"align","tcp_position_centroid":[0.48067,0.07251,0.08273]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.49448,0.06991,0.059],"force_p95":29.8841,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":29.8841,"mean_force":29.8841,"phase_index":1.0,"phase_name":"descend_1","phase_type":"align","tcp_position_centroid":[0.48373,0.0695,0.0643]},{"body_a":"peg","body_b":"channel_base_body","contact_count":436.0,"contact_point_centroid":[0.49559,0.0638,0.00936],"force_p95":0.59867,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.44546,"mean_force":0.56501,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48886,0.13564,0.19742]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":28.0,"contact_point_centroid":[0.47133,0.06388,0.03676],"force_p95":0.92436,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.16907,"mean_force":0.37063,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49923,0.19774,0.29645]}],"total_contact_groups":6},"final_pose_error":0.23194,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.4948,0.06208,0.03324],"final_tcp_position":[0.48293,0.06622,0.0623],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48093,0.06388,0.04]},"peak_contact_force":43.21219,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":463.0,"n_steps_budget":1000.0,"object_pos_end":[0.49521,0.06403,0.03394],"object_pos_start":[0.48093,0.06388,0.04],"object_to_goal_dist_end":0.14424,"object_to_goal_dist_start":0.14514,"object_z_max":0.04,"peak_contact_force":0.54725,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":464.0,"raw_peak_contact_force":2.44546,"subtask_id":"reach_peg","tcp_end":[0.47973,0.07635,0.10544],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.07418,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":267.0,"n_steps_budget":600.0,"object_pos_end":[0.4953,0.06372,0.03397],"object_pos_start":[0.49521,0.06403,0.03394],"object_to_goal_dist_end":0.14392,"object_to_goal_dist_start":0.14424,"object_z_max":0.03398,"peak_contact_force":30.30432,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":268.0,"raw_peak_contact_force":30.30432,"subtask_id":"reach_peg","tcp_end":[0.48379,0.06949,0.06417],"tcp_start":[0.47973,0.07635,0.10544],"tcp_to_object_dist_end":0.03283,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":42.0,"n_steps_budget":1000.0,"object_pos_end":[0.4948,0.06208,0.03324],"object_pos_start":[0.4953,0.06372,0.03397],"object_to_goal_dist_end":0.14234,"object_to_goal_dist_start":0.14392,"object_z_max":0.03397,"peak_contact_force":43.21219,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":84.0,"raw_peak_contact_force":43.21219,"subtask_id":"traverse_channel","tcp_end":[0.48293,0.06622,0.0623],"tcp_start":[0.48379,0.06949,0.06417],"tcp_to_object_dist_end":0.03167,"terminated_normally":true,"termination_reason":"force_exceeded"}],"success":false}]}
```