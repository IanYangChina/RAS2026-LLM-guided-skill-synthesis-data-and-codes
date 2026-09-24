## Search State

- **Seed**: 1
- **Iteration**: 7 / 15

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
- Frozen realised-scene SHA-256: `9fd07833843a6ee28e14c5e2ce05f86547005983f45e63c41c77b8dac2024c0a`
- Frozen object start: [0.5009457299760205, 0.11603709570607482, 0.04]
- Frozen task target: [0.5009457299760205, -0.04396290429392519, 0.04]
- Goal object position: (0.5009457299760205, -0.04396290429392519, 0.04)
- Task success criterion: peg must traverse the channel (0.16 m long) along axis (0.0, -1.0, 0.0); score = axial progress × lateral alignment — NOT a fixed TCP endpoint
- Object initial pose: (0.5009457299760205, 0.11603709570607482, 0.04)
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
  frozen_object_start: [0.5009, 0.116, 0.04]
  frozen_task_target: [0.5009, -0.044, 0.04]
  frozen_fixture_position: [0.54, 0, 0.035]
  frozen_object_starts: {'peg': [0.5009457299760205, 0.11603709570607482, 0.04]}
  frozen_targets: {'channel_exit': [0.5009457299760205, -0.04396290429392519, 0.04]}
  frozen_fixtures: {'channel_left_wall': [0.54, 0.0, 0.035], 'channel_right_wall': [0.46, 0.0, 0.035]}
  channel_axis: [0, -1, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 40
  channel_length_m: 0.16
  force_scale_n: 5
  realized_scene_sha256: 9fd07833843a6ee28e14c5e2ce05f86547005983f45e63c41c77b8dac2024c0a

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
| `object` | offset from object initial position (0.5009457299760205, 0.11603709570607482, 0.04) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.5009457299760205, -0.04396290429392519, 0.04) | final destination targets |
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

## Current Skill (Q=0.038) — your mutation base

```yaml
skill: peg_channel
phases:
- id: rotate_1
  type: rotate
  generator: impedance_motion
  control: impedance_control
  termination: time_limit
- id: align_1
  type: align
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  parameters:
    lateral_offset_x:
      type: scalar
      range:
      - -0.01
      - 0.01
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
- id: align_2
  type: align
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  parameters:
    lateral_offset_x:
      type: scalar
      range:
      - -0.01
      - 0.01

```

## Design Metrics

- **Composite score**: 0.038
- **task_score** (E): 0.080
- **fitness_score**: 0.098  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
  → CMA-ES cannot optimise this structure (shaped reward also near zero)
- **Termination Fidelity** (C): 0.250
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.310

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach | 1.00 | 1.00 | 0.1650 |
| descend | 1.00 | 1.00 | 0.1058 |
| push | 0.00 | 1.00 | 0.0001 |
| retract | 1.00 | 1.00 | 0.1222 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.483, 0.112, 0.164) | (0.483, 0.080, 0.040)→(0.497, 0.080, 0.034) | 0.161→0.160 | 1.00 / 1.000 | 0.562 | 2.857 |
| descend | descend | 1.00 / force_exceeded | (0.483, 0.112, 0.164)→(0.490, 0.095, 0.060) | (0.497, 0.080, 0.034)→(0.497, 0.080, 0.034) | 0.160→0.160 | 1.00 / 2.000 | 19.876 | 19.876 |
| push | push | 0.00 / guard_failure | (0.493, 0.064, 0.057)→(0.493, 0.064, 0.057) | (0.497, 0.080, 0.034)→(0.498, 0.062, 0.033) | 0.160→0.142 | 1.00 / 2.000 | 32.903 | 89.822 |
| retract | retract | 1.00 / step_budget | (0.493, 0.064, 0.057)→(0.490, 0.152, 0.141) | (0.498, 0.062, 0.033)→(0.498, 0.062, 0.034) | 0.142→0.142 | 1.00 / 1.000 | 0.545 | 49.064 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.159
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.159
- phase_score: 0.087
- phase_breakdown.push_sub_score: 0.038
- phase_breakdown.approach_sub_score: 0.202

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.116
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.159
- **Median Q (composite search score)**: 0.036
- **K-run variance**: 0.0002
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.491


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `a904e23429ae963dd2788b3e8d0575d9ce341e1daddfe013fbb1224c3e0c850e`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.04,0.04]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `6bee39a4c127c6d39ee1365e3969a50bb09484f7e2580b1a3dc4d8c4ae20213b`; realized-scene SHA-256: `9fd07833843a6ee28e14c5e2ce05f86547005983f45e63c41c77b8dac2024c0a`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50095,0.11604,0.04]},{"name":"goal","value":[0.50095,-0.04396,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.50095,0.11604,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.50095,-0.04396,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.5625,"average_solve_count":128.0,"average_success_count":128.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach.approach_z_offset":0.11004,"descend.behind_offset":0.01944,"push.behind_offset":0.00891,"push.force_guard_threshold":49.54985,"push.push_speed":0.02405},"optimized_scores":{"best_composite_score":0.0558,"best_fitness_score":0.1158,"best_task_score":0.1585},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":153.0,"contact_point_centroid":[0.50846,0.09264,0.00914],"force_p95":87.62161,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":89.90887,"mean_force":69.20222,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.4972,0.11572,0.05793]},{"body_a":"attachment","body_b":"peg","contact_count":153.0,"contact_point_centroid":[0.50897,0.11476,0.0573],"force_p95":87.15977,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":89.44126,"mean_force":68.75941,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.4972,0.11572,0.05793]},{"body_a":"peg","body_b":"channel_base_body","contact_count":364.0,"contact_point_centroid":[0.50084,0.09309,0.00944],"force_p95":4.40372,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":57.02519,"mean_force":1.41743,"phase_index":3.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.49616,0.13709,0.09795]},{"body_a":"attachment","body_b":"peg","contact_count":39.0,"contact_point_centroid":[0.50825,0.0912,0.05932],"force_p95":27.58894,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":56.64015,"mean_force":8.23583,"phase_index":3.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.49798,0.09616,0.05997]},{"body_a":"peg","body_b":"channel_base_body","contact_count":518.0,"contact_point_centroid":[0.50087,0.11603,0.00942],"force_p95":0.60681,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":30.35611,"mean_force":0.60058,"phase_index":1.0,"phase_name":"descend","phase_type":"descend","tcp_position_centroid":[0.49642,0.1404,0.11223]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.50793,0.13274,0.05879],"force_p95":29.86495,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":29.86495,"mean_force":29.86495,"phase_index":1.0,"phase_name":"descend","phase_type":"descend","tcp_position_centroid":[0.49673,0.13674,0.06044]},{"body_a":"peg","body_b":"channel_base_body","contact_count":258.0,"contact_point_centroid":[0.50107,0.11608,0.00932],"force_p95":0.74997,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.92055,"mean_force":0.57679,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.49876,0.17161,0.23093]}],"total_contact_groups":7},"final_pose_error":0.0197,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50112,0.09068,0.03393],"final_tcp_position":[0.496,0.18107,0.14112],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50095,0.11604,0.04]},"peak_contact_force":89.90887,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":274.0,"n_steps_budget":1000.0,"object_pos_end":[0.50091,0.11608,0.03387],"object_pos_start":[0.50095,0.11604,0.04],"object_to_goal_dist_end":0.19618,"object_to_goal_dist_start":0.19604,"object_z_max":0.04,"peak_contact_force":0.59635,"phase_name":"approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":258.0,"raw_peak_contact_force":1.92055,"subtask_id":"approach_sub","tcp_end":[0.49849,0.14479,0.16739],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.13659,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":518.0,"n_steps_budget":840.0,"object_pos_end":[0.50097,0.11608,0.03384],"object_pos_start":[0.50091,0.11608,0.03387],"object_to_goal_dist_end":0.19618,"object_to_goal_dist_start":0.19618,"object_z_max":0.03397,"peak_contact_force":30.35611,"phase_name":"descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":519.0,"raw_peak_contact_force":30.35611,"subtask_id":"approach_sub","tcp_end":[0.49675,0.13673,0.06023],"tcp_start":[0.49849,0.14479,0.16739],"tcp_to_object_dist_end":0.03378,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":153.0,"n_steps_budget":1000.0,"object_pos_end":[0.50137,0.09125,0.03335],"object_pos_start":[0.50097,0.11608,0.03384],"object_to_goal_dist_end":0.17138,"object_to_goal_dist_start":0.19618,"object_z_max":0.03386,"peak_contact_force":29.68346,"phase_name":"push","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":306.0,"raw_peak_contact_force":89.90887,"subtask_id":"push_sub","tcp_end":[0.4989,0.09261,0.05682],"tcp_start":[0.49884,0.09274,0.05683],"tcp_to_object_dist_end":0.02364,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":364.0,"n_steps_budget":900.0,"object_pos_end":[0.50112,0.09068,0.03393],"object_pos_start":[0.50145,0.09104,0.03335],"object_to_goal_dist_end":0.17079,"object_to_goal_dist_start":0.17118,"object_z_max":0.03736,"peak_contact_force":0.54804,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":403.0,"raw_peak_contact_force":57.02519,"tcp_end":[0.496,0.18107,0.14112],"tcp_start":[0.4989,0.09261,0.05682],"tcp_to_object_dist_end":0.14031,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `8416ac3bebb4dbec2abbf751596843a33db171fd8d70765023f3b940d846bd0c`; realized-scene SHA-256: `2a92d231da5879af7af8916eb4c7dff00148227e84220c4d9643d9841dc77ee7`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.48093,0.06388,0.04]},{"name":"goal","value":[0.48093,-0.09612,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.48093,0.06388,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.48093,-0.09612,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.43284,"average_solve_count":134.0,"average_success_count":134.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach.approach_z_offset":0.08003,"descend.behind_offset":0.005,"push.behind_offset":0.01078,"push.force_guard_threshold":49.33227,"push.push_speed":0.01456},"optimized_scores":{"best_composite_score":0.03631,"best_fitness_score":0.09631,"best_task_score":0.05754},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":101.0,"contact_point_centroid":[0.50206,0.04236,0.00933],"force_p95":86.97633,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":89.89844,"mean_force":68.06042,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.48825,0.06484,0.05846]},{"body_a":"attachment","body_b":"peg","contact_count":101.0,"contact_point_centroid":[0.50011,0.06446,0.05774],"force_p95":86.5141,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":89.43071,"mean_force":67.62534,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.48825,0.06484,0.05846]},{"body_a":"peg","body_b":"channel_base_body","contact_count":354.0,"contact_point_centroid":[0.49587,0.05067,0.00942],"force_p95":6.13426,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":46.53312,"mean_force":1.44944,"phase_index":3.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.48792,0.09449,0.09804]},{"body_a":"attachment","body_b":"peg","contact_count":37.0,"contact_point_centroid":[0.50013,0.0486,0.0594],"force_p95":33.32614,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":46.03916,"mean_force":8.72543,"phase_index":3.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.48976,0.05351,0.06004]},{"body_a":"peg","body_b":"channel_base_body","contact_count":439.0,"contact_point_centroid":[0.49509,0.06395,0.0094],"force_p95":0.55036,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":15.02755,"mean_force":0.57863,"phase_index":1.0,"phase_name":"descend","phase_type":"descend","tcp_position_centroid":[0.48257,0.08602,0.09615]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.49889,0.07681,0.05913],"force_p95":14.56062,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":14.56062,"mean_force":14.56062,"phase_index":1.0,"phase_name":"descend","phase_type":"descend","tcp_position_centroid":[0.48701,0.07664,0.06087]},{"body_a":"peg","body_b":"channel_base_body","contact_count":350.0,"contact_point_centroid":[0.49544,0.06389,0.00936],"force_p95":0.62673,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.44546,"mean_force":0.56973,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.48929,0.1454,0.21212]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":28.0,"contact_point_centroid":[0.47133,0.06388,0.03676],"force_p95":0.92436,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.16907,"mean_force":0.37063,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.49929,0.19746,0.29598]}],"total_contact_groups":8},"final_pose_error":0.0198,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49652,0.04824,0.0338],"final_tcp_position":[0.48775,0.13843,0.14124],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48093,0.06388,0.04]},"peak_contact_force":89.89844,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":377.0,"n_steps_budget":1000.0,"object_pos_end":[0.49513,0.0637,0.03392],"object_pos_start":[0.48093,0.06388,0.04],"object_to_goal_dist_end":0.14391,"object_to_goal_dist_start":0.14514,"object_z_max":0.04,"peak_contact_force":0.5429,"phase_name":"approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":378.0,"raw_peak_contact_force":2.44546,"subtask_id":"approach_sub","tcp_end":[0.48054,0.0961,0.13533],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.10745,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":439.0,"n_steps_budget":690.0,"object_pos_end":[0.49498,0.06363,0.03399],"object_pos_start":[0.49513,0.0637,0.03392],"object_to_goal_dist_end":0.14384,"object_to_goal_dist_start":0.14391,"object_z_max":0.03399,"peak_contact_force":15.02755,"phase_name":"descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":440.0,"raw_peak_contact_force":15.02755,"subtask_id":"approach_sub","tcp_end":[0.48704,0.0766,0.06071],"tcp_start":[0.48054,0.0961,0.13533],"tcp_to_object_dist_end":0.03075,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":101.0,"n_steps_budget":1000.0,"object_pos_end":[0.49679,0.04889,0.03337],"object_pos_start":[0.49498,0.06363,0.03399],"object_to_goal_dist_end":0.1291,"object_to_goal_dist_start":0.14384,"object_z_max":0.03412,"peak_contact_force":35.43057,"phase_name":"push","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":202.0,"raw_peak_contact_force":89.89844,"subtask_id":"push_sub","tcp_end":[0.49062,0.05012,0.05697],"tcp_start":[0.49061,0.05025,0.05699],"tcp_to_object_dist_end":0.02443,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":355.0,"n_steps_budget":900.0,"object_pos_end":[0.49652,0.04824,0.0338],"object_pos_start":[0.49678,0.04867,0.03332],"object_to_goal_dist_end":0.12844,"object_to_goal_dist_start":0.12888,"object_z_max":0.03738,"peak_contact_force":0.54827,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":391.0,"raw_peak_contact_force":46.53312,"tcp_end":[0.48775,0.13843,0.14124],"tcp_start":[0.49062,0.05012,0.05697],"tcp_to_object_dist_end":0.14056,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `0188121de1b8142d5ff7a7406b62c43adf6da5520b986a997e46ef53b7d11bf9`; realized-scene SHA-256: `990d03f436076caee02f5d9d8b3b9b0b3759564b7644084e4eac46818881d834`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.46685,0.05894,0.04]},{"name":"goal","value":[0.46685,-0.10106,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.46685,0.05894,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.46685,-0.10106,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.62698,"average_solve_count":126.0,"average_success_count":126.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach.approach_z_offset":0.13807,"descend.behind_offset":0.00585,"push.behind_offset":0.01368,"push.force_guard_threshold":49.37794,"push.push_speed":0.03056},"optimized_scores":{"best_composite_score":0.02249,"best_fitness_score":0.08249,"best_task_score":0.02409},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":83.0,"contact_point_centroid":[0.50033,0.03928,0.00933],"force_p95":87.65392,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":89.65728,"mean_force":69.25249,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.48678,0.06061,0.05858]},{"body_a":"attachment","body_b":"peg","contact_count":83.0,"contact_point_centroid":[0.49865,0.06064,0.05786],"force_p95":87.18905,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":89.19372,"mean_force":68.81729,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.48678,0.06061,0.05858]},{"body_a":"peg","body_b":"channel_base_body","contact_count":354.0,"contact_point_centroid":[0.49452,0.04826,0.00945],"force_p95":5.51491,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":43.63482,"mean_force":1.33,"phase_index":3.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.48627,0.09273,0.0982]},{"body_a":"attachment","body_b":"peg","contact_count":35.0,"contact_point_centroid":[0.4987,0.04706,0.05925],"force_p95":28.16766,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":43.13243,"mean_force":8.03406,"phase_index":3.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.4881,0.05154,0.05996]},{"body_a":"peg","body_b":"channel_base_body","contact_count":759.0,"contact_point_centroid":[0.49406,0.05902,0.00939],"force_p95":0.5503,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":14.24571,"mean_force":0.56411,"phase_index":1.0,"phase_name":"descend","phase_type":"descend","tcp_position_centroid":[0.47627,0.082,0.12276]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.49733,0.06974,0.05895],"force_p95":13.73512,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":13.73512,"mean_force":13.73512,"phase_index":1.0,"phase_name":"descend","phase_type":"descend","tcp_position_centroid":[0.48547,0.07031,0.06067]},{"body_a":"peg","body_b":"channel_base_body","contact_count":277.0,"contact_point_centroid":[0.49477,0.059,0.00932],"force_p95":0.64986,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.20518,"mean_force":0.599,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.48311,0.14359,0.23962]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":35.0,"contact_point_centroid":[0.46807,0.05895,0.03796],"force_p95":1.19991,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.42382,"mean_force":0.50385,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.49842,0.19569,0.29512]}],"total_contact_groups":8},"final_pose_error":0.01969,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49557,0.04633,0.03404],"final_tcp_position":[0.4861,0.13677,0.14151],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.46685,0.05894,0.04]},"peak_contact_force":89.65728,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":306.0,"n_steps_budget":1000.0,"object_pos_end":[0.49409,0.05905,0.03384],"object_pos_start":[0.46685,0.05894,0.04],"object_to_goal_dist_end":0.13931,"object_to_goal_dist_start":0.14284,"object_z_max":0.04001,"peak_contact_force":0.54751,"phase_name":"approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":312.0,"raw_peak_contact_force":4.20518,"subtask_id":"approach_sub","tcp_end":[0.46918,0.09446,0.18978],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.16183,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":759.0,"n_steps_budget":1000.0,"object_pos_end":[0.49393,0.0589,0.03393],"object_pos_start":[0.49409,0.05905,0.03384],"object_to_goal_dist_end":0.13917,"object_to_goal_dist_start":0.13931,"object_z_max":0.03393,"peak_contact_force":14.24571,"phase_name":"descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":760.0,"raw_peak_contact_force":14.24571,"subtask_id":"approach_sub","tcp_end":[0.48549,0.07028,0.06053],"tcp_start":[0.46918,0.09446,0.18978],"tcp_to_object_dist_end":0.03013,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":83.0,"n_steps_budget":1000.0,"object_pos_end":[0.4956,0.04675,0.0335],"object_pos_start":[0.49393,0.0589,0.03393],"object_to_goal_dist_end":0.12699,"object_to_goal_dist_start":0.13917,"object_z_max":0.0341,"peak_contact_force":33.59589,"phase_name":"push","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":166.0,"raw_peak_contact_force":89.65728,"subtask_id":"push_sub","tcp_end":[0.48897,0.04839,0.05715],"tcp_start":[0.48896,0.04853,0.05718],"tcp_to_object_dist_end":0.02462,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":354.0,"n_steps_budget":900.0,"object_pos_end":[0.49557,0.04633,0.03404],"object_pos_start":[0.49558,0.04652,0.03345],"object_to_goal_dist_end":0.12655,"object_to_goal_dist_start":0.12677,"object_z_max":0.03717,"peak_contact_force":0.53949,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":389.0,"raw_peak_contact_force":43.63482,"tcp_end":[0.4861,0.13677,0.14151],"tcp_start":[0.48897,0.04839,0.05715],"tcp_to_object_dist_end":0.14079,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```