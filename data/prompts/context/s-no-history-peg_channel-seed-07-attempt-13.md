## Search State

- **Seed**: 7
- **Iteration**: 14 / 15

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

## Current Skill (Q=-0.311) — your mutation base

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

- **Composite score**: -0.311
- **task_score** (E): 0.000
- **fitness_score**: 0.099  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
  → CMA-ES cannot optimise this structure (shaped reward also near zero)
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.410

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_behind | 1.00 | 1.00 | 0.1740 |
| descend_to_height | 1.00 | 1.00 | 0.0668 |
| move_to_contact | 1.00 | 1.00 | 0.0326 |
| push_through_channel | 0.67 | 1.00 | 0.0484 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_behind | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.505, 0.197, 0.129) | (0.509, 0.098, 0.040)→(0.502, 0.098, 0.034) | 0.179→0.179 | 1.00 / 1.000 | 0.527 | 2.732 |
| descend_to_height | descend | 1.00 / step_budget | (0.505, 0.197, 0.129)→(0.499, 0.197, 0.063) | (0.502, 0.098, 0.034)→(0.502, 0.112, 0.027) | 0.179→0.192 | 1.00 / 1.000 | 0.519 | 1.362 |
| move_to_contact | align | 1.00 / step_budget | (0.499, 0.197, 0.063)→(0.501, 0.171, 0.048) | (0.502, 0.112, 0.027)→(0.502, 0.112, 0.027) | 0.192→0.192 | 1.00 / 1.333 | 52.521 | 54.102 |
| push_through_channel | push | 0.67 / step_budget | (0.501, 0.171, 0.048)→(0.503, 0.219, 0.042) | (0.502, 0.112, 0.027)→(0.521, 0.112, 0.027) | 0.192→0.194 | 1.00 / 1.000 | 0.346 | 14.115 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.000
- alignment_error: None
- force_efficiency: 0.941
- terminal_score: 0.000
- phase_score: 0.211
- phase_breakdown.push_to_goal_score: 0.000
- phase_breakdown.reach_behind_peg_score: 0.704

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.127
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.000
- **Median Q (composite search score)**: -0.316
- **K-run variance**: 0.0004
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Parameters at lower bound**: push_through_channel.push_distance
- **Final σ (mean)**: 0.465


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.83871,"average_solve_count":186.0,"average_success_count":186.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_behind.speed":0.04571,"descend_to_height.speed":0.04112,"move_to_contact.lateral_offset_x":0.00325,"move_to_contact.speed":0.02513,"push_through_channel.push_distance":0.1,"push_through_channel.push_speed":0.03499,"push_through_channel.retry_offset_x":-0.00276},"optimized_scores":{"best_composite_score":-0.33406,"best_fitness_score":0.07594,"best_task_score":0.0002},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":552.0,"contact_point_centroid":[0.50352,0.11171,0.00936],"force_p95":0.61179,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06328,"mean_force":0.55927,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.50224,0.20434,0.21145]},{"body_a":"peg","body_b":"channel_base_body","contact_count":289.0,"contact_point_centroid":[0.50365,0.11165,0.00941],"force_p95":0.60606,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.63364,"mean_force":0.54386,"phase_index":3.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.49949,0.18781,0.04732]},{"body_a":"peg","body_b":"channel_base_body","contact_count":216.0,"contact_point_centroid":[0.50384,0.11166,0.00941],"force_p95":0.58145,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.62884,"mean_force":0.54404,"phase_index":2.0,"phase_name":"move_to_contact","phase_type":"align","tcp_position_centroid":[0.49998,0.18969,0.05492]},{"body_a":"peg","body_b":"channel_base_body","contact_count":216.0,"contact_point_centroid":[0.50378,0.11173,0.00938],"force_p95":0.60041,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.60276,"mean_force":0.54621,"phase_index":1.0,"phase_name":"descend_to_height","phase_type":"descend","tcp_position_centroid":[0.50255,0.20936,0.09613]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":16.0,"contact_point_centroid":[0.52601,0.11178,0.02875],"force_p95":0.50724,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54079,"mean_force":0.34334,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.49975,0.19966,0.2991]}],"total_contact_groups":5},"final_pose_error":0.00999,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50371,0.11174,0.03387],"final_tcp_position":[0.49955,0.20496,0.04783],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.51001,0.11178,0.04]},"peak_contact_force":2.06328,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":574.0,"n_steps_budget":1000.0,"object_pos_end":[0.50375,0.11175,0.03378],"object_pos_start":[0.51001,0.11178,0.04],"object_to_goal_dist_end":0.19189,"object_to_goal_dist_start":0.19204,"object_z_max":0.04,"peak_contact_force":0.49815,"phase_name":"approach_behind","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":568.0,"raw_peak_contact_force":2.06328,"subtask_id":"reach_behind_peg","tcp_end":[0.50608,0.20958,0.12874],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.13636,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":216.0,"n_steps_budget":1000.0,"object_pos_end":[0.50373,0.11175,0.03384],"object_pos_start":[0.50375,0.11175,0.03378],"object_to_goal_dist_end":0.19188,"object_to_goal_dist_start":0.19189,"object_z_max":0.03385,"peak_contact_force":0.52067,"phase_name":"descend_to_height","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":216.0,"raw_peak_contact_force":0.60276,"subtask_id":"reach_behind_peg","tcp_end":[0.50059,0.20991,0.06298],"tcp_start":[0.50608,0.20958,0.12874],"tcp_to_object_dist_end":0.10244,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":216.0,"n_steps_budget":1000.0,"object_pos_end":[0.50372,0.11175,0.03385],"object_pos_start":[0.50373,0.11175,0.03384],"object_to_goal_dist_end":0.19188,"object_to_goal_dist_start":0.19188,"object_z_max":0.0339,"peak_contact_force":0.53736,"phase_name":"move_to_contact","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":216.0,"raw_peak_contact_force":0.62884,"subtask_id":"reach_behind_peg","tcp_end":[0.50187,0.16952,0.05018],"tcp_start":[0.50059,0.20991,0.06298],"tcp_to_object_dist_end":0.06006,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":289.0,"n_steps_budget":780.0,"object_pos_end":[0.50371,0.11174,0.03387],"object_pos_start":[0.50372,0.11175,0.03385],"object_to_goal_dist_end":0.19188,"object_to_goal_dist_start":0.19188,"object_z_max":0.034,"peak_contact_force":0.53923,"phase_name":"push_through_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":289.0,"raw_peak_contact_force":0.63364,"subtask_id":"push_to_goal","tcp_end":[0.49955,0.20496,0.04783],"tcp_start":[0.50187,0.16952,0.05018],"tcp_to_object_dist_end":0.09434,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.05028,"average_solve_count":179.0,"average_success_count":179.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_behind.speed":0.0613,"descend_to_height.speed":0.03375,"move_to_contact.lateral_offset_x":-0.01208,"move_to_contact.speed":0.03447,"push_through_channel.push_distance":0.16767,"push_through_channel.push_speed":0.04718,"push_through_channel.retry_offset_x":-0.00098},"optimized_scores":{"best_composite_score":-0.28321,"best_fitness_score":0.12679,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"world","contact_count":129.0,"contact_point_centroid":[0.49614,0.15269,-0.00145],"force_p95":1.27201,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.92727,"mean_force":0.64195,"phase_index":1.0,"phase_name":"descend_to_height","phase_type":"descend","tcp_position_centroid":[0.48775,0.21722,0.08035]},{"body_a":"peg","body_b":"channel_base_body","contact_count":529.0,"contact_point_centroid":[0.49625,0.11925,0.00943],"force_p95":0.62021,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.24822,"mean_force":0.55442,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.49116,0.20771,0.21109]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":24.0,"contact_point_centroid":[0.47288,0.11898,0.03087],"force_p95":0.72905,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.86893,"mean_force":0.3628,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.49948,0.19974,0.29783]},{"body_a":"peg","body_b":"world","contact_count":64.0,"contact_point_centroid":[0.49689,0.15995,-0.00198],"force_p95":0.72599,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.72605,"mean_force":0.60555,"phase_index":2.0,"phase_name":"move_to_contact","phase_type":"align","tcp_position_centroid":[0.48743,0.21572,0.05332]},{"body_a":"peg","body_b":"world","contact_count":984.0,"contact_point_centroid":[0.51846,0.15998,-0.00199],"force_p95":0.72586,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.72594,"mean_force":0.60602,"phase_index":3.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.48747,0.27023,0.03307]},{"body_a":"peg","body_b":"channel_base_body","contact_count":110.0,"contact_point_centroid":[0.49695,0.11991,0.00953],"force_p95":0.55689,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.56328,"mean_force":0.48785,"phase_index":1.0,"phase_name":"descend_to_height","phase_type":"descend","tcp_position_centroid":[0.48413,0.21606,0.11395]}],"total_contact_groups":6},"final_pose_error":0.00998,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.55269,0.16007,0.01408],"final_tcp_position":[0.493,0.32102,0.02807],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48616,0.11898,0.04]},"peak_contact_force":2.92727,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":554.0,"n_steps_budget":1000.0,"object_pos_end":[0.49605,0.12034,0.03397],"object_pos_start":[0.48616,0.11898,0.04],"object_to_goal_dist_end":0.20047,"object_to_goal_dist_start":0.19946,"object_z_max":0.04,"peak_contact_force":0.54092,"phase_name":"approach_behind","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":553.0,"raw_peak_contact_force":2.24822,"subtask_id":"reach_behind_peg","tcp_end":[0.4842,0.21615,0.12915],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.13557,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":242.0,"n_steps_budget":1000.0,"object_pos_end":[0.49658,0.16,0.01409],"object_pos_start":[0.49605,0.12034,0.03397],"object_to_goal_dist_end":0.24141,"object_to_goal_dist_start":0.20047,"object_z_max":0.03397,"peak_contact_force":0.49655,"phase_name":"descend_to_height","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":239.0,"raw_peak_contact_force":2.92727,"subtask_id":"reach_behind_peg","tcp_end":[0.49036,0.21813,0.06189],"tcp_start":[0.4842,0.21615,0.12915],"tcp_to_object_dist_end":0.07552,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":64.0,"n_steps_budget":600.0,"object_pos_end":[0.49739,0.15999,0.01409],"object_pos_start":[0.49658,0.16,0.01409],"object_to_goal_dist_end":0.2414,"object_to_goal_dist_start":0.24141,"object_z_max":0.01411,"peak_contact_force":0.49909,"phase_name":"move_to_contact","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":64.0,"raw_peak_contact_force":0.72605,"subtask_id":"reach_behind_peg","tcp_end":[0.48457,0.21285,0.0436],"tcp_start":[0.49036,0.21813,0.06189],"tcp_to_object_dist_end":0.06189,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":984.0,"n_steps_budget":1000.0,"object_pos_end":[0.55269,0.16007,0.01408],"object_pos_start":[0.49739,0.15999,0.01409],"object_to_goal_dist_end":0.24715,"object_to_goal_dist_start":0.2414,"object_z_max":0.01409,"peak_contact_force":0.49853,"phase_name":"push_through_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":984.0,"raw_peak_contact_force":0.72594,"subtask_id":"push_to_goal","tcp_end":[0.493,0.32102,0.02807],"tcp_start":[0.48457,0.21285,0.0436],"tcp_to_object_dist_end":0.17223,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.30337,"average_solve_count":267.0,"average_success_count":267.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_behind.speed":0.04204,"descend_to_height.speed":0.01628,"move_to_contact.lateral_offset_x":0.01997,"move_to_contact.speed":0.01401,"push_through_channel.push_distance":0.15296,"push_through_channel.push_speed":0.02681,"push_through_channel.retry_offset_x":-0.0013},"optimized_scores":{"best_composite_score":-0.31649,"best_fitness_score":0.09351,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_left_wall","contact_count":511.0,"contact_point_centroid":[0.52502,0.11996,0.05999],"force_p95":157.11373,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":160.95154,"mean_force":122.47763,"phase_index":2.0,"phase_name":"move_to_contact","phase_type":"align","tcp_position_centroid":[0.51541,0.13049,0.05121]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":3.0,"contact_point_centroid":[0.52501,0.11997,0.06],"force_p95":40.96973,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":40.98435,"mean_force":40.12458,"phase_index":3.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.51594,0.13095,0.0504]},{"body_a":"peg","body_b":"channel_base_body","contact_count":575.0,"contact_point_centroid":[0.5057,0.06297,0.00936],"force_p95":0.56449,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.88411,"mean_force":0.57008,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.51147,0.18152,0.21012]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":34.0,"contact_point_centroid":[0.53102,0.06295,0.03156],"force_p95":1.1362,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.98455,"mean_force":0.48262,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.49988,0.19905,0.29662]},{"body_a":"peg","body_b":"channel_base_body","contact_count":735.0,"contact_point_centroid":[0.50603,0.06294,0.00938],"force_p95":0.55225,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55532,"mean_force":0.54656,"phase_index":2.0,"phase_name":"move_to_contact","phase_type":"align","tcp_position_centroid":[0.51348,0.13519,0.05274]},{"body_a":"peg","body_b":"channel_base_body","contact_count":220.0,"contact_point_centroid":[0.50599,0.06298,0.00938],"force_p95":0.55232,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55501,"mean_force":0.54659,"phase_index":1.0,"phase_name":"descend_to_height","phase_type":"descend","tcp_position_centroid":[0.51482,0.16321,0.09682]},{"body_a":"peg","body_b":"channel_base_body","contact_count":3.0,"contact_point_centroid":[0.49298,0.0728,0.00938],"force_p95":0.55073,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55101,"mean_force":0.54807,"phase_index":3.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.51594,0.13095,0.0504]}],"total_contact_groups":7},"final_pose_error":0.08559,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50599,0.06306,0.03382],"final_tcp_position":[0.51589,0.13101,0.05034],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.52962,0.06295,0.04]},"peak_contact_force":160.95154,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":603.0,"n_steps_budget":1000.0,"object_pos_end":[0.50599,0.06304,0.03381],"object_pos_start":[0.52962,0.06295,0.04],"object_to_goal_dist_end":0.1433,"object_to_goal_dist_start":0.14598,"object_z_max":0.04001,"peak_contact_force":0.54149,"phase_name":"approach_behind","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":609.0,"raw_peak_contact_force":3.88411,"subtask_id":"reach_behind_peg","tcp_end":[0.52413,0.16473,0.12799],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.13979,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":220.0,"n_steps_budget":1000.0,"object_pos_end":[0.50599,0.06304,0.03381],"object_pos_start":[0.50599,0.06304,0.03381],"object_to_goal_dist_end":0.1433,"object_to_goal_dist_start":0.1433,"object_z_max":0.03381,"peak_contact_force":0.54104,"phase_name":"descend_to_height","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":220.0,"raw_peak_contact_force":0.55501,"subtask_id":"reach_behind_peg","tcp_end":[0.50603,0.16225,0.06377],"tcp_start":[0.52413,0.16473,0.12799],"tcp_to_object_dist_end":0.10364,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":735.0,"n_steps_budget":1000.0,"object_pos_end":[0.50591,0.06299,0.03382],"object_pos_start":[0.50599,0.06304,0.03381],"object_to_goal_dist_end":0.14325,"object_to_goal_dist_start":0.1433,"object_z_max":0.03382,"peak_contact_force":156.52598,"phase_name":"move_to_contact","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":1246.0,"raw_peak_contact_force":160.95154,"subtask_id":"reach_behind_peg","tcp_end":[0.51596,0.13094,0.05042],"tcp_start":[0.50603,0.16225,0.06377],"tcp_to_object_dist_end":0.07066,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.50592,0.06303,0.03382],"object_pos_start":[0.50591,0.06299,0.03382],"object_to_goal_dist_end":0.14328,"object_to_goal_dist_start":0.14325,"object_z_max":0.03382,"peak_contact_force":0.0,"phase_name":"push_through_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":6.0,"raw_peak_contact_force":40.98435,"subtask_id":"push_to_goal","tcp_end":[0.51589,0.13101,0.05034],"tcp_start":[0.51592,0.13098,0.05037],"tcp_to_object_dist_end":0.07067,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":true}]}
```