## Search State

- **Seed**: 7
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

## Current Skill (Q=-0.131) — your mutation base

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

- **Composite score**: -0.131
- **task_score** (E): 0.262
- **fitness_score**: 0.209  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.340

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| descend_1 | 1.00 | 1.00 | 0.2543 |
| insert_1 | 0.00 | 1.00 | 0.1328 |
| grasp_1 | 1.00 | 1.00 | 0.0011 |
| approach_1 | 1.00 | 1.00 | 0.0251 |
| align_1 | 1.00 | 1.00 | 0.0243 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| descend_1 | descend | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.504, 0.142, 0.054) | (0.509, 0.098, 0.040)→(0.502, 0.098, 0.034) | 0.179→0.178 | 1.00 / 1.333 | 106.254 | 119.349 |
| insert_1 | insert | 0.00 / step_budget | (0.504, 0.142, 0.054)→(0.503, 0.010, 0.047) | (0.502, 0.098, 0.034)→(0.503, 0.006, 0.038) | 0.178→0.086 | 1.00 / 2.000 | 97.425 | 174.984 |
| grasp_1 | grasp | 1.00 / step_budget | (0.503, 0.010, 0.047)→(0.502, 0.009, 0.047) | (0.503, 0.006, 0.038)→(0.502, 0.005, 0.038) | 0.086→0.086 | 1.00 / 3.333 | 70.549 | 95.544 |
| approach_1 | approach | 1.00 / step_budget | (0.502, 0.009, 0.047)→(0.507, 0.034, 0.046) | (0.502, 0.005, 0.038)→(0.503, 0.028, 0.038) | 0.086→0.108 | 1.00 / 2.667 | 125.947 | 180.752 |
| align_1 | align | 1.00 / step_budget | (0.507, 0.034, 0.046)→(0.509, 0.058, 0.046) | (0.503, 0.028, 0.038)→(0.504, 0.049, 0.030) | 0.108→0.130 | 1.00 / 2.667 | 126.154 | 185.361 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 1.000
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.786
- phase_score: 0.224
- phase_breakdown.approach_score: 0.026
- phase_breakdown.push_score: 0.364
- phase_breakdown.contact_score: 0.000

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.448
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.786
- **Median Q (composite search score)**: -0.238
- **K-run variance**: 0.0289
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.7
- **Final σ (mean)**: 0.460


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.16418,"average_solve_count":134.0,"average_success_count":134.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":0.0032,"align_1.lateral_offset_y":0.0026,"approach_1.speed":0.06389,"insert_1.insertion_depth":0.09015,"insert_1.insertion_force":4.63452},"optimized_scores":{"best_composite_score":0.10835,"best_fitness_score":0.44835,"best_task_score":0.78558},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":432.0,"contact_point_centroid":[0.54191,-0.03567,0.05997],"force_p95":87.01714,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":94.29373,"mean_force":76.9009,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49729,-0.0296,0.03691]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":20.0,"contact_point_centroid":[0.5421,-0.03569,0.05998],"force_p95":80.23945,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":80.33021,"mean_force":53.89444,"phase_index":4.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.4975,-0.02963,0.03692]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":20.0,"contact_point_centroid":[0.54209,-0.03569,0.05998],"force_p95":79.17415,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":79.19046,"mean_force":53.50078,"phase_index":3.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49749,-0.02963,0.03691]},{"body_a":"peg","body_b":"channel_base_body","contact_count":985.0,"contact_point_centroid":[0.50385,0.02322,0.00977],"force_p95":38.31166,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":42.59357,"mean_force":24.039,"phase_index":1.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.50056,0.05697,0.04175]},{"body_a":"attachment","body_b":"peg","contact_count":945.0,"contact_point_centroid":[0.50407,0.0421,0.0402],"force_p95":38.07037,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":42.37809,"mean_force":24.63395,"phase_index":1.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.5004,0.05298,0.04153]},{"body_a":"peg","body_b":"channel_base_body","contact_count":450.0,"contact_point_centroid":[0.50038,-0.06642,0.00997],"force_p95":3.10107,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":12.53111,"mean_force":1.12185,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49732,-0.02961,0.03694]},{"body_a":"attachment","body_b":"peg","contact_count":450.0,"contact_point_centroid":[0.50148,-0.04065,0.03494],"force_p95":2.7758,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":11.73358,"mean_force":0.64837,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49732,-0.02961,0.03694]},{"body_a":"peg","body_b":"channel_base_body","contact_count":8.0,"contact_point_centroid":[0.50039,-0.10005,0.04487],"force_p95":4.46998,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.4746,"mean_force":4.26737,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49813,-0.02982,0.03791]},{"body_a":"peg","body_b":"channel_base_body","contact_count":756.0,"contact_point_centroid":[0.50359,0.11169,0.00938],"force_p95":0.60779,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06328,"mean_force":0.55452,"phase_index":0.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50201,0.17585,0.17071]},{"body_a":"peg","body_b":"channel_base_body","contact_count":20.0,"contact_point_centroid":[0.50058,-0.0666,0.00998],"force_p95":0.67318,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.75382,"mean_force":0.58635,"phase_index":4.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.4975,-0.02963,0.03692]},{"body_a":"peg","body_b":"channel_base_body","contact_count":20.0,"contact_point_centroid":[0.50058,-0.06661,0.00998],"force_p95":0.63288,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.73707,"mean_force":0.55221,"phase_index":3.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49749,-0.02963,0.03691]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":16.0,"contact_point_centroid":[0.52601,0.11178,0.02875],"force_p95":0.50724,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54079,"mean_force":0.34334,"phase_index":0.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49976,0.19944,0.29874]},{"body_a":"attachment","body_b":"peg","contact_count":20.0,"contact_point_centroid":[0.50164,-0.04072,0.03491],"force_p95":0.2692,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31923,"mean_force":0.17972,"phase_index":4.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.4975,-0.02963,0.03692]},{"body_a":"attachment","body_b":"peg","contact_count":10.0,"contact_point_centroid":[0.50162,-0.04071,0.0349],"force_p95":0.23267,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28684,"mean_force":0.15347,"phase_index":3.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49749,-0.02963,0.03691]},{"body_a":"peg","body_b":"channel_base_body","contact_count":20.0,"contact_point_centroid":[0.49946,-0.10002,0.04724],"force_p95":0.24661,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.25019,"mean_force":0.2058,"phase_index":4.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.4975,-0.02963,0.03692]},{"body_a":"peg","body_b":"channel_base_body","contact_count":13.0,"contact_point_centroid":[0.49946,-0.10002,0.04724],"force_p95":0.24065,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24482,"mean_force":0.1642,"phase_index":3.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49749,-0.02963,0.03691]}],"total_contact_groups":16},"final_pose_error":0.00455,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50018,-0.06996,0.04059],"final_tcp_position":[0.49751,-0.02964,0.03692],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.51001,0.11178,0.04]},"peak_contact_force":94.29373,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":778.0,"n_steps_budget":1000.0,"object_pos_end":[0.50367,0.11173,0.03382],"object_pos_start":[0.51001,0.11178,0.04],"object_to_goal_dist_end":0.19187,"object_to_goal_dist_start":0.19204,"object_z_max":0.04,"peak_contact_force":0.57116,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":772.0,"raw_peak_contact_force":2.06328,"tcp_end":[0.50559,0.15326,0.04883],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.0442,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50108,-0.06948,0.04008],"object_pos_start":[0.50367,0.11173,0.03382],"object_to_goal_dist_end":0.01058,"object_to_goal_dist_start":0.19187,"object_z_max":0.04039,"peak_contact_force":18.30294,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":1930.0,"raw_peak_contact_force":42.59357,"tcp_end":[0.49833,-0.0295,0.03815],"tcp_start":[0.50559,0.15326,0.04883],"tcp_to_object_dist_end":0.04012,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50017,-0.06992,0.04059],"object_pos_start":[0.50108,-0.06948,0.04008],"object_to_goal_dist_end":0.0101,"object_to_goal_dist_start":0.01058,"object_z_max":0.0406,"peak_contact_force":72.00629,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":1340.0,"raw_peak_contact_force":94.29373,"tcp_end":[0.49748,-0.02963,0.03691],"tcp_start":[0.49833,-0.0295,0.03815],"tcp_to_object_dist_end":0.04055,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":20.0,"n_steps_budget":600.0,"object_pos_end":[0.50018,-0.06997,0.04059],"object_pos_start":[0.50017,-0.06992,0.04059],"object_to_goal_dist_end":0.01005,"object_to_goal_dist_start":0.0101,"object_z_max":0.04059,"peak_contact_force":19.17963,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":63.0,"raw_peak_contact_force":79.19046,"tcp_end":[0.49749,-0.02963,0.03692],"tcp_start":[0.49748,-0.02963,0.03691],"tcp_to_object_dist_end":0.0406,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":20.0,"n_steps_budget":600.0,"object_pos_end":[0.50018,-0.06996,0.04059],"object_pos_start":[0.50018,-0.06997,0.04059],"object_to_goal_dist_end":0.01006,"object_to_goal_dist_start":0.01005,"object_z_max":0.04059,"peak_contact_force":19.06441,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":80.0,"raw_peak_contact_force":80.33021,"tcp_end":[0.49751,-0.02964,0.03692],"tcp_start":[0.49749,-0.02963,0.03692],"tcp_to_object_dist_end":0.04057,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.68243,"average_solve_count":148.0,"average_success_count":148.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":0.00284,"align_1.lateral_offset_y":0.00501,"approach_1.speed":0.04379,"insert_1.insertion_depth":0.10903,"insert_1.insertion_force":18.67364},"optimized_scores":{"best_composite_score":-0.23757,"best_fitness_score":0.10243,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":6,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_right_wall","contact_count":325.0,"contact_point_centroid":[0.47495,0.09844,0.04772],"force_p95":196.19954,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":201.74714,"mean_force":124.00354,"phase_index":1.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.48389,0.10312,0.04321]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":297.0,"contact_point_centroid":[0.54398,0.07865,0.05999],"force_p95":122.48255,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":135.47057,"mean_force":77.71705,"phase_index":4.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49919,0.07876,0.03652]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":662.0,"contact_point_centroid":[0.5388,0.01167,0.05999],"force_p95":100.33735,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":113.97798,"mean_force":75.21858,"phase_index":3.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49366,0.01516,0.03748]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":112.0,"contact_point_centroid":[0.53213,0.01003,0.06],"force_p95":101.46686,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":112.56894,"mean_force":78.53636,"phase_index":1.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.48658,0.0136,0.03833]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":666.0,"contact_point_centroid":[0.52617,0.04166,0.02651],"force_p95":85.5006,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":99.62789,"mean_force":51.55571,"phase_index":1.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.48616,0.04787,0.04056]},{"body_a":"attachment","body_b":"peg","contact_count":859.0,"contact_point_centroid":[0.49455,0.0644,0.03832],"force_p95":89.45027,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":98.70763,"mean_force":44.90774,"phase_index":1.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.48523,0.06655,0.04134]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":449.0,"contact_point_centroid":[0.53539,-0.01622,0.05998],"force_p95":78.45774,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":80.57819,"mean_force":72.97699,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49022,-0.01125,0.03778]},{"body_a":"peg","body_b":"channel_base_body","contact_count":883.0,"contact_point_centroid":[0.5059,0.06863,0.00926],"force_p95":56.68019,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":70.32332,"mean_force":21.54338,"phase_index":1.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.4846,0.08135,0.04215]},{"body_a":"attachment","body_b":"peg","contact_count":884.0,"contact_point_centroid":[0.50022,0.02711,0.03439],"force_p95":36.04403,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":42.45306,"mean_force":13.91623,"phase_index":3.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49392,0.01776,0.03745]},{"body_a":"attachment","body_b":"peg","contact_count":217.0,"contact_point_centroid":[0.50416,0.08495,0.03417],"force_p95":27.66593,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":37.53956,"mean_force":7.20286,"phase_index":4.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49895,0.07477,0.03663]},{"body_a":"peg","body_b":"channel_base_body","contact_count":870.0,"contact_point_centroid":[0.50305,0.04959,0.00992],"force_p95":27.27678,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":31.23671,"mean_force":8.67135,"phase_index":3.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49387,0.01723,0.03746]},{"body_a":"peg","body_b":"channel_base_body","contact_count":250.0,"contact_point_centroid":[0.50549,0.10845,0.00988],"force_p95":22.73548,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":31.10675,"mean_force":3.54089,"phase_index":4.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49909,0.07374,0.03661]},{"body_a":"peg","body_b":"world","contact_count":164.0,"contact_point_centroid":[0.50622,0.14674,-0.00187],"force_p95":26.51817,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":29.20971,"mean_force":4.39242,"phase_index":4.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.50014,0.11026,0.03606]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":810.0,"contact_point_centroid":[0.52508,0.03853,0.02578],"force_p95":15.71851,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":18.89336,"mean_force":8.74646,"phase_index":3.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49369,0.01527,0.03748]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":97.0,"contact_point_centroid":[0.52504,0.09375,0.023],"force_p95":11.13195,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":14.42073,"mean_force":3.10626,"phase_index":4.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49886,0.06943,0.03667]},{"body_a":"attachment","body_b":"peg","contact_count":443.0,"contact_point_centroid":[0.49705,-0.00204,0.03431],"force_p95":0.78088,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":3.44985,"mean_force":0.43537,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49022,-0.01125,0.03778]}],"total_contact_groups":22},"final_pose_error":0.00986,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.5045,0.1542,0.0147],"final_tcp_position":[0.50064,0.12334,0.03638],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48616,0.11898,0.04]},"peak_contact_force":201.74714,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":764.0,"n_steps_budget":1000.0,"object_pos_end":[0.49601,0.11947,0.03385],"object_pos_start":[0.48616,0.11898,0.04],"object_to_goal_dist_end":0.1996,"object_to_goal_dist_start":0.19946,"object_z_max":0.04,"peak_contact_force":0.52313,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":763.0,"raw_peak_contact_force":2.24822,"tcp_end":[0.48315,0.16005,0.04931],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.0453,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.02363,0.04076],"object_pos_start":[0.49601,0.11947,0.03385],"object_to_goal_dist_end":0.10364,"object_to_goal_dist_start":0.1996,"object_z_max":0.04096,"peak_contact_force":0.228,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":2845.0,"raw_peak_contact_force":201.74714,"tcp_end":[0.48994,-0.01019,0.03787],"tcp_start":[0.48315,0.16005,0.04931],"tcp_to_object_dist_end":0.03575,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50001,0.02326,0.04048],"object_pos_start":[0.50118,0.02363,0.04076],"object_to_goal_dist_end":0.10326,"object_to_goal_dist_start":0.10364,"object_z_max":0.04076,"peak_contact_force":69.55588,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":1969.0,"raw_peak_contact_force":80.57819,"tcp_end":[0.49038,-0.01128,0.03777],"tcp_start":[0.48994,-0.01019,0.03787],"tcp_to_object_dist_end":0.03596,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":884.0,"n_steps_budget":1000.0,"object_pos_end":[0.50395,0.09161,0.04063],"object_pos_start":[0.50001,0.02326,0.04048],"object_to_goal_dist_end":0.17165,"object_to_goal_dist_start":0.10326,"object_z_max":0.04082,"peak_contact_force":11.59035,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3228.0,"raw_peak_contact_force":113.97798,"tcp_end":[0.49713,0.05443,0.03702],"tcp_start":[0.49038,-0.01128,0.03777],"tcp_to_object_dist_end":0.03797,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":503.0,"n_steps_budget":600.0,"object_pos_end":[0.5045,0.1542,0.0147],"object_pos_start":[0.50395,0.09161,0.04063],"object_to_goal_dist_end":0.23561,"object_to_goal_dist_start":0.17165,"object_z_max":0.0411,"peak_contact_force":24.85652,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":1025.0,"raw_peak_contact_force":135.47057,"tcp_end":[0.50064,0.12334,0.03638],"tcp_start":[0.49713,0.05443,0.03702],"tcp_to_object_dist_end":0.03792,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.40385,"average_solve_count":156.0,"average_success_count":156.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":-0.00976,"align_1.lateral_offset_y":0.00526,"approach_1.speed":0.02387,"insert_1.insertion_depth":0.03977,"insert_1.insertion_force":8.37312},"optimized_scores":{"best_composite_score":-0.2649,"best_fitness_score":0.0751,"best_task_score":0.00016},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_left_wall","contact_count":114.0,"contact_point_centroid":[0.53488,0.11266,0.05979],"force_p95":345.12221,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":353.73417,"mean_force":317.18085,"phase_index":0.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.52374,0.11275,0.06404]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":999.0,"contact_point_centroid":[0.53314,0.0707,0.05993],"force_p95":346.9773,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":349.08868,"mean_force":322.72712,"phase_index":3.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.52229,0.07182,0.06485]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":455.0,"contact_point_centroid":[0.53721,0.07658,0.05992],"force_p95":335.78423,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":340.2814,"mean_force":313.37149,"phase_index":4.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.5263,0.07767,0.06473]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":971.0,"contact_point_centroid":[0.53179,0.07947,0.05996],"force_p95":269.18931,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":280.61255,"mean_force":220.14643,"phase_index":1.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.52086,0.0799,0.06481]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":450.0,"contact_point_centroid":[0.53025,0.06773,0.05998],"force_p95":78.15631,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":111.75961,"mean_force":73.29178,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51942,0.06891,0.06497]},{"body_a":"peg","body_b":"channel_base_body","contact_count":876.0,"contact_point_centroid":[0.5058,0.06299,0.00937],"force_p95":0.55584,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.88411,"mean_force":0.56201,"phase_index":0.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.51235,0.14948,0.1623]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":34.0,"contact_point_centroid":[0.53102,0.06295,0.03156],"force_p95":1.1362,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.98455,"mean_force":0.48262,"phase_index":0.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49981,0.19843,0.29603]},{"body_a":"peg","body_b":"channel_base_body","contact_count":455.0,"contact_point_centroid":[0.50613,0.0631,0.00939],"force_p95":0.55121,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55544,"mean_force":0.54622,"phase_index":4.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.5263,0.07767,0.06473]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.50599,0.06301,0.00938],"force_p95":0.55192,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55532,"mean_force":0.5465,"phase_index":1.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.5209,0.08037,0.06481]},{"body_a":"peg","body_b":"channel_base_body","contact_count":999.0,"contact_point_centroid":[0.50592,0.06299,0.00939],"force_p95":0.55082,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55491,"mean_force":0.54625,"phase_index":3.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.52229,0.07182,0.06485]},{"body_a":"peg","body_b":"channel_base_body","contact_count":450.0,"contact_point_centroid":[0.50609,0.06282,0.00939],"force_p95":0.55092,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55442,"mean_force":0.54631,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51942,0.06891,0.06497]}],"total_contact_groups":11},"final_pose_error":0.04442,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50606,0.06288,0.03388],"final_tcp_position":[0.52749,0.07945,0.06468],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.52962,0.06295,0.04]},"peak_contact_force":353.73417,"phases":[{"contact_detected":true,"contact_event_count":2.0,"n_steps":904.0,"n_steps_budget":1000.0,"object_pos_end":[0.50601,0.06303,0.03381],"object_pos_start":[0.52962,0.06295,0.04],"object_to_goal_dist_end":0.14329,"object_to_goal_dist_start":0.14598,"object_z_max":0.04001,"peak_contact_force":317.66646,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1024.0,"raw_peak_contact_force":353.73417,"tcp_end":[0.52444,0.11271,0.06453],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.06125,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50606,0.06302,0.03385],"object_pos_start":[0.50601,0.06303,0.03381],"object_to_goal_dist_end":0.14328,"object_to_goal_dist_start":0.14329,"object_z_max":0.03385,"peak_contact_force":273.74442,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":1971.0,"raw_peak_contact_force":280.61255,"tcp_end":[0.51934,0.0685,0.06491],"tcp_start":[0.52444,0.11271,0.06453],"tcp_to_object_dist_end":0.03423,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50587,0.06295,0.03386],"object_pos_start":[0.50606,0.06302,0.03385],"object_to_goal_dist_end":0.1432,"object_to_goal_dist_start":0.14328,"object_z_max":0.03386,"peak_contact_force":70.08427,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":900.0,"raw_peak_contact_force":111.75961,"tcp_end":[0.51952,0.06893,0.06498],"tcp_start":[0.51934,0.0685,0.06491],"tcp_to_object_dist_end":0.0345,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":999.0,"n_steps_budget":1000.0,"object_pos_end":[0.50593,0.06309,0.03388],"object_pos_start":[0.50587,0.06295,0.03386],"object_to_goal_dist_end":0.14335,"object_to_goal_dist_start":0.1432,"object_z_max":0.03388,"peak_contact_force":347.07062,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1998.0,"raw_peak_contact_force":349.08868,"tcp_end":[0.52503,0.07646,0.06479],"tcp_start":[0.51952,0.06893,0.06498],"tcp_to_object_dist_end":0.03872,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":455.0,"n_steps_budget":600.0,"object_pos_end":[0.50606,0.06288,0.03388],"object_pos_start":[0.50593,0.06309,0.03388],"object_to_goal_dist_end":0.14314,"object_to_goal_dist_start":0.14335,"object_z_max":0.03388,"peak_contact_force":334.54154,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":910.0,"raw_peak_contact_force":340.2814,"tcp_end":[0.52749,0.07945,0.06468],"tcp_start":[0.52503,0.07646,0.06479],"tcp_to_object_dist_end":0.04102,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```