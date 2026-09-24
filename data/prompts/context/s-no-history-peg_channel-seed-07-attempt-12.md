## Search State

- **Seed**: 7
- **Iteration**: 13 / 15

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
- Frozen realised-scene SHA-256: `d0d8b50673ee8d816e4de306a6620129fbd254b61025859fc8d57d0983f18415`
- Frozen object start: [0.5100076373283734, 0.11177710407756605, 0.04]
- Frozen task target: [0.5100076373283734, -0.04822289592243395, 0.04]
- Goal object position: (0.5100076373283734, -0.04822289592243395, 0.04)
- Task success criterion: peg must traverse the channel (0.16 m long) along axis (0.0, -1.0, 0.0); score = axial progress × lateral alignment — NOT a fixed TCP endpoint
- Object initial pose: (0.5100076373283734, 0.11177710407756605, 0.04)
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
  frozen_object_start: [0.51, 0.1118, 0.04]
  frozen_task_target: [0.51, -0.0482, 0.04]
  frozen_fixture_position: [0.54, 0, 0.035]
  frozen_object_starts: {'peg': [0.5100076373283734, 0.11177710407756605, 0.04]}
  frozen_targets: {'channel_exit': [0.5100076373283734, -0.04822289592243395, 0.04]}
  frozen_fixtures: {'channel_left_wall': [0.54, 0.0, 0.035], 'channel_right_wall': [0.46, 0.0, 0.035]}
  channel_axis: [0, -1, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 40
  channel_length_m: 0.16
  force_scale_n: 5
  realized_scene_sha256: d0d8b50673ee8d816e4de306a6620129fbd254b61025859fc8d57d0983f18415

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
| `object` | offset from object initial position (0.5100076373283734, 0.11177710407756605, 0.04) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.5100076373283734, -0.04822289592243395, 0.04) | final destination targets |
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

## Current Skill (Q=-0.245) — your mutation base

```yaml
skill: peg_channel
skill_type: arm_gripper
phases:
- id: descend_1
  type: descend
  generator: linear_cartesian
  control: admittance_control
  termination: pose_tolerance
- id: insert_1
  type: insert
  generator: impedance_motion
  control: admittance_control
  termination: pose_tolerance
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
- id: grasp_1
  type: grasp
  control: position_control
  termination: time_limit
  end_effector_action: force_grasp
- id: approach_1
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  parameters:
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1
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
    lateral_offset_y:
      type: scalar
      range:
      - -0.01
      - 0.01

```

## Design Metrics

- **Composite score**: -0.245
- **task_score** (E): 0.005
- **fitness_score**: 0.065  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
  → CMA-ES cannot optimise this structure (shaped reward also near zero)
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.310

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_behind | 1.00 | 1.00 | 0.1785 |
| descend_to_height | 1.00 | 1.00 | 0.0471 |
| move_to_contact | 1.00 | 1.00 | 0.0230 |
| push_through_channel | 0.00 | 1.00 | 0.0002 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_behind | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.505, 0.160, 0.129) | (0.509, 0.098, 0.040)→(0.502, 0.098, 0.034) | 0.179→0.178 | 1.00 / 1.000 | 0.547 | 2.732 |
| descend_to_height | descend | 1.00 / step_budget | (0.505, 0.160, 0.129)→(0.500, 0.157, 0.083) | (0.502, 0.098, 0.034)→(0.502, 0.098, 0.034) | 0.178→0.178 | 1.00 / 1.000 | 0.555 | 0.598 |
| move_to_contact | align | 1.00 / step_budget | (0.500, 0.157, 0.083)→(0.501, 0.139, 0.070) | (0.502, 0.098, 0.034)→(0.502, 0.098, 0.034) | 0.178→0.178 | 1.00 / 1.000 | 0.537 | 0.610 |
| push_through_channel | push | 0.00 / guard_failure | (0.498, 0.099, 0.060)→(0.498, 0.099, 0.060) | (0.502, 0.098, 0.034)→(0.502, 0.097, 0.034) | 0.178→0.177 | 1.00 / 2.000 | 14.247 | 48.785 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.006
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.005
- phase_score: 0.109
- phase_breakdown.push_to_goal_score: 0.007
- phase_breakdown.reach_behind_peg_score: 0.348

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.067
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.008
- **Median Q (composite search score)**: -0.244
- **K-run variance**: 0.0000
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.377


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `474e87cb3f7f98c9c8d99c8760356b7c026b70b97898f68d5a6c39ba94bca956`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.04,0.04]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `a79e5fd8fc80d9ecadd30a274b12d8d7e7d0841df5ca68ae512c46dc86b114e6`; realized-scene SHA-256: `d0d8b50673ee8d816e4de306a6620129fbd254b61025859fc8d57d0983f18415`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.51001,0.11178,0.04]},{"name":"goal","value":[0.51001,-0.04822,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.51001,0.11178,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.51001,-0.04822,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.21374,"average_solve_count":131.0,"average_success_count":131.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_behind.speed":0.07054,"descend_to_height.speed":0.04817,"move_to_contact.lateral_offset_x":0.00817,"push_through_channel.push_speed":0.03728,"push_through_channel.retry_offset_x":-0.00798},"optimized_scores":{"best_composite_score":-0.24374,"best_fitness_score":0.06626,"best_task_score":0.00751},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":105.0,"contact_point_centroid":[0.5043,0.10996,0.00939],"force_p95":31.94352,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":48.15279,"mean_force":3.67718,"phase_index":3.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.50462,0.13391,0.06443]},{"body_a":"attachment","body_b":"peg","contact_count":11.0,"contact_point_centroid":[0.51493,0.11556,0.05886],"force_p95":45.07885,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":47.6413,"mean_force":29.94963,"phase_index":3.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.50318,0.11439,0.06064]},{"body_a":"peg","body_b":"channel_base_body","contact_count":521.0,"contact_point_centroid":[0.50356,0.11167,0.00937],"force_p95":0.61239,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06328,"mean_force":0.55998,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.50233,0.18583,0.21136]},{"body_a":"peg","body_b":"channel_base_body","contact_count":441.0,"contact_point_centroid":[0.50361,0.11167,0.00942],"force_p95":0.58537,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.63024,"mean_force":0.54292,"phase_index":2.0,"phase_name":"move_to_contact","phase_type":"align","tcp_position_centroid":[0.50324,0.1603,0.0739]},{"body_a":"peg","body_b":"channel_base_body","contact_count":152.0,"contact_point_centroid":[0.50374,0.11169,0.0094],"force_p95":0.5924,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.61047,"mean_force":0.54443,"phase_index":1.0,"phase_name":"descend_to_height","phase_type":"descend","tcp_position_centroid":[0.50307,0.17174,0.10647]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":16.0,"contact_point_centroid":[0.52601,0.11178,0.02875],"force_p95":0.50724,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54079,"mean_force":0.34334,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.49984,0.1995,0.29896]}],"total_contact_groups":6},"final_pose_error":0.19347,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50392,0.11051,0.03443],"final_tcp_position":[0.50329,0.11235,0.0605],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.51001,0.11178,0.04]},"peak_contact_force":48.15279,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":543.0,"n_steps_budget":1000.0,"object_pos_end":[0.50371,0.11177,0.0338],"object_pos_start":[0.51001,0.11178,0.04],"object_to_goal_dist_end":0.19191,"object_to_goal_dist_start":0.19204,"object_z_max":0.04,"peak_contact_force":0.54043,"phase_name":"approach_behind","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":537.0,"raw_peak_contact_force":2.06328,"subtask_id":"reach_behind_peg","tcp_end":[0.5061,0.17293,0.12903],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.1132,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":152.0,"n_steps_budget":720.0,"object_pos_end":[0.50372,0.11178,0.03396],"object_pos_start":[0.50371,0.11177,0.0338],"object_to_goal_dist_end":0.19191,"object_to_goal_dist_start":0.19191,"object_z_max":0.03394,"peak_contact_force":0.58116,"phase_name":"descend_to_height","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":152.0,"raw_peak_contact_force":0.61047,"subtask_id":"reach_behind_peg","tcp_end":[0.5011,0.17099,0.08323],"tcp_start":[0.5061,0.17293,0.12903],"tcp_to_object_dist_end":0.07708,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":441.0,"n_steps_budget":600.0,"object_pos_end":[0.50369,0.11171,0.03382],"object_pos_start":[0.50372,0.11178,0.03396],"object_to_goal_dist_end":0.19185,"object_to_goal_dist_start":0.19191,"object_z_max":0.034,"peak_contact_force":0.49292,"phase_name":"move_to_contact","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":441.0,"raw_peak_contact_force":0.63024,"subtask_id":"reach_behind_peg","tcp_end":[0.5072,0.15242,0.06961],"tcp_start":[0.5011,0.17099,0.08323],"tcp_to_object_dist_end":0.05431,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":105.0,"n_steps_budget":1000.0,"object_pos_end":[0.50379,0.11072,0.03431],"object_pos_start":[0.50369,0.11171,0.03382],"object_to_goal_dist_end":0.19085,"object_to_goal_dist_start":0.19185,"object_z_max":0.03439,"peak_contact_force":17.47052,"phase_name":"push_through_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":116.0,"raw_peak_contact_force":48.15279,"subtask_id":"push_to_goal","tcp_end":[0.50329,0.11235,0.0605],"tcp_start":[0.50327,0.11255,0.06053],"tcp_to_object_dist_end":0.02624,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `3ca2e925d364d2c0fe81fb71ee31d40f947a20e349a0720e1c44a2dd2bc628da`; realized-scene SHA-256: `c5fb87552d009c7e1ef813cadc54d289d6d9c896c1dd51a37fa468bf6305165e`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.48616,0.11898,0.04]},{"name":"goal","value":[0.48616,-0.04102,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.48616,0.11898,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.48616,-0.04102,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.17164,"average_solve_count":134.0,"average_success_count":134.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_behind.speed":0.07537,"descend_to_height.speed":0.04264,"move_to_contact.lateral_offset_x":-0.00891,"push_through_channel.push_speed":0.03632,"push_through_channel.retry_offset_x":0.00184},"optimized_scores":{"best_composite_score":-0.24257,"best_fitness_score":0.06743,"best_task_score":0.00456},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":123.0,"contact_point_centroid":[0.49625,0.11857,0.00945],"force_p95":14.8967,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":55.1887,"mean_force":2.76868,"phase_index":3.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.48352,0.1389,0.06477]},{"body_a":"attachment","body_b":"peg","contact_count":12.0,"contact_point_centroid":[0.4959,0.11644,0.05887],"force_p95":45.52477,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":54.82683,"mean_force":22.85849,"phase_index":3.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.48415,0.11608,0.06067]},{"body_a":"peg","body_b":"channel_base_body","contact_count":502.0,"contact_point_centroid":[0.49625,0.11923,0.00941],"force_p95":0.61722,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.24822,"mean_force":0.55625,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.49128,0.18912,0.21102]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":24.0,"contact_point_centroid":[0.47288,0.11898,0.03087],"force_p95":0.72905,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.86893,"mean_force":0.3628,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.49953,0.19938,0.29774]},{"body_a":"peg","body_b":"channel_base_body","contact_count":181.0,"contact_point_centroid":[0.49635,0.11941,0.00943],"force_p95":0.60177,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.64518,"mean_force":0.54159,"phase_index":2.0,"phase_name":"move_to_contact","phase_type":"align","tcp_position_centroid":[0.4862,0.16899,0.07453]},{"body_a":"peg","body_b":"channel_base_body","contact_count":177.0,"contact_point_centroid":[0.49594,0.11895,0.00942],"force_p95":0.59999,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.62983,"mean_force":0.54274,"phase_index":1.0,"phase_name":"descend_to_height","phase_type":"descend","tcp_position_centroid":[0.48635,0.17861,0.10554]}],"total_contact_groups":6},"final_pose_error":0.19552,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49629,0.11804,0.03431],"final_tcp_position":[0.4844,0.11382,0.06045],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48616,0.11898,0.04]},"peak_contact_force":55.1887,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":527.0,"n_steps_budget":1000.0,"object_pos_end":[0.49607,0.11913,0.03385],"object_pos_start":[0.48616,0.11898,0.04],"object_to_goal_dist_end":0.19926,"object_to_goal_dist_start":0.19946,"object_z_max":0.04,"peak_contact_force":0.5547,"phase_name":"approach_behind","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":526.0,"raw_peak_contact_force":2.24822,"subtask_id":"reach_behind_peg","tcp_end":[0.48441,0.1796,0.12962],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.11387,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":177.0,"n_steps_budget":840.0,"object_pos_end":[0.49607,0.11899,0.03382],"object_pos_start":[0.49607,0.11913,0.03385],"object_to_goal_dist_end":0.19912,"object_to_goal_dist_start":0.19926,"object_z_max":0.03392,"peak_contact_force":0.53597,"phase_name":"descend_to_height","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":177.0,"raw_peak_contact_force":0.62983,"subtask_id":"reach_behind_peg","tcp_end":[0.49019,0.17811,0.0816],"tcp_start":[0.48441,0.1796,0.12962],"tcp_to_object_dist_end":0.07624,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":181.0,"n_steps_budget":600.0,"object_pos_end":[0.496,0.11962,0.03392],"object_pos_start":[0.49607,0.11899,0.03382],"object_to_goal_dist_end":0.19975,"object_to_goal_dist_start":0.19912,"object_z_max":0.034,"peak_contact_force":0.56943,"phase_name":"move_to_contact","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":181.0,"raw_peak_contact_force":0.64518,"subtask_id":"reach_behind_peg","tcp_end":[0.48419,0.16116,0.07043],"tcp_start":[0.49019,0.17811,0.0816],"tcp_to_object_dist_end":0.05656,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":123.0,"n_steps_budget":1000.0,"object_pos_end":[0.49619,0.11826,0.03422],"object_pos_start":[0.496,0.11962,0.03392],"object_to_goal_dist_end":0.19838,"object_to_goal_dist_start":0.19975,"object_z_max":0.03428,"peak_contact_force":17.16701,"phase_name":"push_through_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":135.0,"raw_peak_contact_force":55.1887,"subtask_id":"push_to_goal","tcp_end":[0.4844,0.11382,0.06045],"tcp_start":[0.48434,0.11402,0.06048],"tcp_to_object_dist_end":0.0291,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `f85f1938a541e3d507519c8f918b8ca98f1f9baf6ab2f6f3ba2c32478e079e47`; realized-scene SHA-256: `a0d7ea14565b0a67e86de15fa43f3773b761884db645527685cd53e0fd95aeb9`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.52962,0.06295,0.04]},{"name":"goal","value":[0.52962,-0.09705,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.52962,0.06295,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.52962,-0.09705,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.23022,"average_solve_count":139.0,"average_success_count":139.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_behind.speed":0.07081,"descend_to_height.speed":0.04707,"move_to_contact.lateral_offset_x":0.00998,"push_through_channel.push_speed":0.02487,"push_through_channel.retry_offset_x":-0.00209},"optimized_scores":{"best_composite_score":-0.24964,"best_fitness_score":0.06036,"best_task_score":0.00176},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":91.0,"contact_point_centroid":[0.50702,0.06164,0.00939],"force_p95":30.41306,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":43.0144,"mean_force":3.2338,"phase_index":3.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.50871,0.08939,0.06469]},{"body_a":"attachment","body_b":"peg","contact_count":8.0,"contact_point_centroid":[0.51855,0.07294,0.05879],"force_p95":41.30233,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":42.57291,"mean_force":30.65911,"phase_index":3.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.50673,0.07259,0.06061]},{"body_a":"peg","body_b":"channel_base_body","contact_count":591.0,"contact_point_centroid":[0.5058,0.06297,0.00936],"force_p95":0.56361,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.88411,"mean_force":0.56946,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.51166,0.16222,0.20897]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":34.0,"contact_point_centroid":[0.53102,0.06295,0.03156],"force_p95":1.1362,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.98455,"mean_force":0.48262,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.49997,0.19842,0.29642]},{"body_a":"peg","body_b":"channel_base_body","contact_count":440.0,"contact_point_centroid":[0.50599,0.06299,0.00938],"force_p95":0.55236,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55532,"mean_force":0.54657,"phase_index":2.0,"phase_name":"move_to_contact","phase_type":"align","tcp_position_centroid":[0.50854,0.11237,0.07403]},{"body_a":"peg","body_b":"channel_base_body","contact_count":145.0,"contact_point_centroid":[0.50561,0.06313,0.00938],"force_p95":0.55236,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55501,"mean_force":0.54655,"phase_index":1.0,"phase_name":"descend_to_height","phase_type":"descend","tcp_position_centroid":[0.51608,0.12525,0.10574]}],"total_contact_groups":6},"final_pose_error":0.15268,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50612,0.06224,0.03414],"final_tcp_position":[0.5067,0.07116,0.0604],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.52962,0.06295,0.04]},"peak_contact_force":43.0144,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":619.0,"n_steps_budget":1000.0,"object_pos_end":[0.50595,0.06295,0.0338],"object_pos_start":[0.52962,0.06295,0.04],"object_to_goal_dist_end":0.1432,"object_to_goal_dist_start":0.14598,"object_z_max":0.04001,"peak_contact_force":0.5468,"phase_name":"approach_behind","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":625.0,"raw_peak_contact_force":3.88411,"subtask_id":"reach_behind_peg","tcp_end":[0.52438,0.12739,0.12694],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.11475,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":145.0,"n_steps_budget":750.0,"object_pos_end":[0.50601,0.06302,0.03381],"object_pos_start":[0.50595,0.06295,0.0338],"object_to_goal_dist_end":0.14328,"object_to_goal_dist_start":0.1432,"object_z_max":0.03381,"peak_contact_force":0.54859,"phase_name":"descend_to_height","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":145.0,"raw_peak_contact_force":0.55501,"subtask_id":"reach_behind_peg","tcp_end":[0.50774,0.12335,0.08345],"tcp_start":[0.52438,0.12739,0.12694],"tcp_to_object_dist_end":0.07814,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":440.0,"n_steps_budget":600.0,"object_pos_end":[0.50602,0.06302,0.03381],"object_pos_start":[0.50601,0.06302,0.03381],"object_to_goal_dist_end":0.14328,"object_to_goal_dist_start":0.14328,"object_z_max":0.03381,"peak_contact_force":0.54894,"phase_name":"move_to_contact","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":440.0,"raw_peak_contact_force":0.55532,"subtask_id":"reach_behind_peg","tcp_end":[0.51149,0.1041,0.06962],"tcp_start":[0.50774,0.12335,0.08345],"tcp_to_object_dist_end":0.05478,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":91.0,"n_steps_budget":1000.0,"object_pos_end":[0.50604,0.06241,0.03405],"object_pos_start":[0.50602,0.06302,0.03381],"object_to_goal_dist_end":0.14266,"object_to_goal_dist_start":0.14328,"object_z_max":0.0341,"peak_contact_force":8.10252,"phase_name":"push_through_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":99.0,"raw_peak_contact_force":43.0144,"subtask_id":"push_to_goal","tcp_end":[0.5067,0.07116,0.0604],"tcp_start":[0.50671,0.07136,0.06046],"tcp_to_object_dist_end":0.02777,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```