## Search State

- **Seed**: 1
- **Iteration**: 3 / 15

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

## Current Skill (Q=0.085) — your mutation base

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

- **Composite score**: 0.085
- **task_score** (E): 0.000
- **fitness_score**: 0.082  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
  → CMA-ES cannot optimise this structure (shaped reward also near zero)
- **Termination Fidelity** (C): 0.333
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.330

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_above | 1.00 | 1.00 | 0.2263 |
| descend_contact | 1.00 | 1.00 | 0.0468 |
| push_through | 0.00 | 1.00 | 0.0009 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_above | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.481, 0.086, 0.107) | (0.483, 0.080, 0.040)→(0.497, 0.080, 0.034) | 0.161→0.160 | 1.00 / 1.000 | 0.539 | 2.857 |
| descend_contact | descend | 1.00 / force_exceeded | (0.481, 0.086, 0.107)→(0.486, 0.082, 0.061) | (0.497, 0.080, 0.034)→(0.497, 0.080, 0.034) | 0.160→0.160 | 1.00 / 2.000 | 21.934 | 21.934 |
| push_through | push | 0.00 / guard_failure | (0.486, 0.082, 0.061)→(0.486, 0.082, 0.061) | (0.497, 0.080, 0.034)→(0.496, 0.080, 0.034) | 0.160→0.160 | 1.00 / 2.000 | 37.957 | 37.957 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.001
- alignment_error: None
- force_efficiency: 0.256
- terminal_score: 0.001
- phase_score: 0.138
- phase_breakdown.push_through_score: 0.000
- phase_breakdown.reach_above_score: 0.459

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.083
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.001
- **Median Q (composite search score)**: 0.086
- **K-run variance**: 0.0000
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.233


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.98039,"average_solve_count":51.0,"average_success_count":51.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above.approach_speed":0.13185,"descend_contact.contact_force_threshold":4.79291,"push_through.guard_force_limit":35.94039,"push_through.lateral_offset_x":-0.00243,"push_through.push_distance":0.12653,"push_through.push_max_time":2.99375},"optimized_scores":{"best_composite_score":0.08573,"best_fitness_score":0.08239,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":12.0,"contact_point_centroid":[0.49371,0.1169,0.00944],"force_p95":34.86554,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":35.94121,"mean_force":22.49046,"phase_index":2.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.49575,0.11757,0.0608]},{"body_a":"attachment","body_b":"peg","contact_count":12.0,"contact_point_centroid":[0.50748,0.11715,0.05865],"force_p95":34.42818,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":35.48701,"mean_force":22.02172,"phase_index":2.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.49575,0.11757,0.0608]},{"body_a":"peg","body_b":"channel_base_body","contact_count":241.0,"contact_point_centroid":[0.50078,0.11603,0.00942],"force_p95":0.60206,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":15.1394,"mean_force":0.60322,"phase_index":1.0,"phase_name":"descend_contact","phase_type":"descend","tcp_position_centroid":[0.49586,0.11873,0.08403]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.50776,0.11735,0.05898],"force_p95":14.68529,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":14.68529,"mean_force":14.68529,"phase_index":1.0,"phase_name":"descend_contact","phase_type":"descend","tcp_position_centroid":[0.49601,0.11726,0.06142]},{"body_a":"peg","body_b":"channel_base_body","contact_count":608.0,"contact_point_centroid":[0.50095,0.11601,0.00938],"force_p95":0.61186,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.92055,"mean_force":0.55656,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.49814,0.15943,0.20097]}],"total_contact_groups":5},"final_pose_error":0.12546,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50067,0.11665,0.03395],"final_tcp_position":[0.49554,0.11834,0.06043],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50095,0.11604,0.04]},"peak_contact_force":35.94121,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":624.0,"n_steps_budget":1000.0,"object_pos_end":[0.50098,0.11599,0.034],"object_pos_start":[0.50095,0.11604,0.04],"object_to_goal_dist_end":0.19609,"object_to_goal_dist_start":0.19604,"object_z_max":0.04,"peak_contact_force":0.53425,"phase_name":"approach_above","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":608.0,"raw_peak_contact_force":1.92055,"subtask_id":"reach_above","tcp_end":[0.49773,0.12065,0.1081],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.07432,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":241.0,"n_steps_budget":600.0,"object_pos_end":[0.50093,0.116,0.03397],"object_pos_start":[0.50098,0.11599,0.034],"object_to_goal_dist_end":0.19609,"object_to_goal_dist_start":0.19609,"object_z_max":0.034,"peak_contact_force":15.1394,"phase_name":"descend_contact","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":242.0,"raw_peak_contact_force":15.1394,"subtask_id":"reach_above","tcp_end":[0.49602,0.11725,0.06126],"tcp_start":[0.49773,0.12065,0.1081],"tcp_to_object_dist_end":0.02776,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":12.0,"n_steps_budget":810.0,"object_pos_end":[0.50067,0.11665,0.03395],"object_pos_start":[0.50093,0.116,0.03397],"object_to_goal_dist_end":0.19674,"object_to_goal_dist_start":0.19609,"object_z_max":0.03397,"peak_contact_force":35.94121,"phase_name":"push_through","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":24.0,"raw_peak_contact_force":35.94121,"subtask_id":"push_through","tcp_end":[0.49554,0.11834,0.06043],"tcp_start":[0.49602,0.11725,0.06126],"tcp_to_object_dist_end":0.02703,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.5641,"average_solve_count":39.0,"average_success_count":39.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above.approach_speed":0.21723,"descend_contact.contact_force_threshold":7.93802,"push_through.guard_force_limit":31.86808,"push_through.lateral_offset_x":0.00996,"push_through.push_distance":0.1326,"push_through.push_max_time":3.71569},"optimized_scores":{"best_composite_score":0.08629,"best_fitness_score":0.08296,"best_task_score":0.00064},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":1.0,"contact_point_centroid":[0.47924,0.05537,0.0094],"force_p95":37.19903,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":37.19903,"mean_force":37.19903,"phase_index":2.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.48454,0.0664,0.06132]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.49628,0.06673,0.05895],"force_p95":36.53095,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":36.53095,"mean_force":36.53095,"phase_index":2.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.48454,0.0664,0.06132]},{"body_a":"peg","body_b":"channel_base_body","contact_count":290.0,"contact_point_centroid":[0.49522,0.06409,0.0094],"force_p95":0.55048,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":18.07558,"mean_force":0.60586,"phase_index":1.0,"phase_name":"descend_contact","phase_type":"descend","tcp_position_centroid":[0.48065,0.06842,0.08252]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.49623,0.06653,0.05902],"force_p95":17.6137,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":17.6137,"mean_force":17.6137,"phase_index":1.0,"phase_name":"descend_contact","phase_type":"descend","tcp_position_centroid":[0.48448,0.06641,0.06146]},{"body_a":"peg","body_b":"channel_base_body","contact_count":613.0,"contact_point_centroid":[0.49528,0.06388,0.00937],"force_p95":0.56981,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.44546,"mean_force":0.55944,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.48834,0.13258,0.19772]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":28.0,"contact_point_centroid":[0.47133,0.06388,0.03676],"force_p95":0.92436,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.16907,"mean_force":0.37063,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.49939,0.1981,0.29662]}],"total_contact_groups":6},"final_pose_error":0.13299,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49479,0.06372,0.03403],"final_tcp_position":[0.48451,0.06638,0.06123],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48093,0.06388,0.04]},"peak_contact_force":37.19903,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":640.0,"n_steps_budget":720.0,"object_pos_end":[0.49513,0.06365,0.03396],"object_pos_start":[0.48093,0.06388,0.04],"object_to_goal_dist_end":0.14386,"object_to_goal_dist_start":0.14514,"object_z_max":0.04,"peak_contact_force":0.54116,"phase_name":"approach_above","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":641.0,"raw_peak_contact_force":2.44546,"subtask_id":"reach_above","tcp_end":[0.4789,0.07084,0.10664],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.07481,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":290.0,"n_steps_budget":600.0,"object_pos_end":[0.49485,0.06375,0.03399],"object_pos_start":[0.49513,0.06365,0.03396],"object_to_goal_dist_end":0.14397,"object_to_goal_dist_start":0.14386,"object_z_max":0.034,"peak_contact_force":18.07558,"phase_name":"descend_contact","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":291.0,"raw_peak_contact_force":18.07558,"subtask_id":"reach_above","tcp_end":[0.48454,0.0664,0.06132],"tcp_start":[0.4789,0.07084,0.10664],"tcp_to_object_dist_end":0.02933,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1.0,"n_steps_budget":840.0,"object_pos_end":[0.49479,0.06372,0.03403],"object_pos_start":[0.49485,0.06375,0.03399],"object_to_goal_dist_end":0.14394,"object_to_goal_dist_start":0.14397,"object_z_max":0.03399,"peak_contact_force":37.19903,"phase_name":"push_through","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2.0,"raw_peak_contact_force":37.19903,"subtask_id":"push_through","tcp_end":[0.48451,0.06638,0.06123],"tcp_start":[0.48454,0.0664,0.06132],"tcp_to_object_dist_end":0.0292,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.62,"average_solve_count":50.0,"average_success_count":50.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above.approach_speed":0.15851,"descend_contact.contact_force_threshold":9.5534,"push_through.guard_force_limit":38.54555,"push_through.lateral_offset_x":0.00524,"push_through.push_distance":0.16831,"push_through.push_max_time":3.25469},"optimized_scores":{"best_composite_score":0.08342,"best_fitness_score":0.08009,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":11.0,"contact_point_centroid":[0.4874,0.07297,0.00933],"force_p95":39.54896,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":40.72977,"mean_force":25.47481,"phase_index":2.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.47805,0.06203,0.06089]},{"body_a":"attachment","body_b":"peg","contact_count":11.0,"contact_point_centroid":[0.48978,0.0614,0.05865],"force_p95":39.06379,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":40.26098,"mean_force":24.96642,"phase_index":2.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.47805,0.06203,0.06089]},{"body_a":"peg","body_b":"channel_base_body","contact_count":324.0,"contact_point_centroid":[0.49406,0.05874,0.00939],"force_p95":0.55013,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":32.58847,"mean_force":0.64483,"phase_index":1.0,"phase_name":"descend_contact","phase_type":"descend","tcp_position_centroid":[0.4708,0.06378,0.08266]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.48991,0.06165,0.05895],"force_p95":32.17857,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":32.17857,"mean_force":32.17857,"phase_index":1.0,"phase_name":"descend_contact","phase_type":"descend","tcp_position_centroid":[0.47816,0.06178,0.06139]},{"body_a":"peg","body_b":"channel_base_body","contact_count":663.0,"contact_point_centroid":[0.4944,0.05899,0.00936],"force_p95":0.56071,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.20518,"mean_force":0.56827,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.48146,0.13021,0.19787]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":35.0,"contact_point_centroid":[0.46807,0.05895,0.03796],"force_p95":1.19991,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.42382,"mean_force":0.50385,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.499,0.1976,0.29583]}],"total_contact_groups":6},"final_pose_error":0.16747,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49387,0.05972,0.03406],"final_tcp_position":[0.47793,0.0627,0.06061],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.46685,0.05894,0.04]},"peak_contact_force":40.72977,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":692.0,"n_steps_budget":990.0,"object_pos_end":[0.49405,0.05908,0.03389],"object_pos_start":[0.46685,0.05894,0.04],"object_to_goal_dist_end":0.13934,"object_to_goal_dist_start":0.14284,"object_z_max":0.04001,"peak_contact_force":0.54201,"phase_name":"approach_above","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":698.0,"raw_peak_contact_force":4.20518,"subtask_id":"reach_above","tcp_end":[0.46566,0.06612,0.10671],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.07848,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":324.0,"n_steps_budget":600.0,"object_pos_end":[0.49431,0.05906,0.03393],"object_pos_start":[0.49405,0.05908,0.03389],"object_to_goal_dist_end":0.13931,"object_to_goal_dist_start":0.13934,"object_z_max":0.03393,"peak_contact_force":32.58847,"phase_name":"descend_contact","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":325.0,"raw_peak_contact_force":32.58847,"subtask_id":"reach_above","tcp_end":[0.47824,0.06177,0.06125],"tcp_start":[0.46566,0.06612,0.10671],"tcp_to_object_dist_end":0.03181,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":11.0,"n_steps_budget":1000.0,"object_pos_end":[0.49387,0.05972,0.03406],"object_pos_start":[0.49431,0.05906,0.03393],"object_to_goal_dist_end":0.13998,"object_to_goal_dist_start":0.13931,"object_z_max":0.03403,"peak_contact_force":40.72977,"phase_name":"push_through","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":22.0,"raw_peak_contact_force":40.72977,"subtask_id":"push_through","tcp_end":[0.47793,0.0627,0.06061],"tcp_start":[0.47824,0.06177,0.06125],"tcp_to_object_dist_end":0.03111,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```