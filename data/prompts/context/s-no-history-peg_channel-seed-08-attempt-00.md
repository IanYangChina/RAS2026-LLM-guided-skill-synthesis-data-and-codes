## Search State

- **Seed**: 8
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

- Task name: peg_channel
- Frozen realised-scene SHA-256: `c5fb87552d009c7e1ef813cadc54d289d6d9c896c1dd51a37fa468bf6305165e`
- Frozen object start: [0.48615778212844485, 0.11898214746703403, 0.04]
- Frozen task target: [0.48615778212844485, -0.04101785253296597, 0.04]
- Goal object position: (0.48615778212844485, -0.04101785253296597, 0.04)
- Task success criterion: peg must traverse the channel (0.16 m long) along axis (0.0, -1.0, 0.0); score = axial progress × lateral alignment — NOT a fixed TCP endpoint
- Object initial pose: (0.48615778212844485, 0.11898214746703403, 0.04)
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
  frozen_object_start: [0.4862, 0.119, 0.04]
  frozen_task_target: [0.4862, -0.041, 0.04]
  frozen_fixture_position: [0.54, 0, 0.035]
  frozen_object_starts: {'peg': [0.48615778212844485, 0.11898214746703403, 0.04]}
  frozen_targets: {'channel_exit': [0.48615778212844485, -0.04101785253296597, 0.04]}
  frozen_fixtures: {'channel_left_wall': [0.54, 0.0, 0.035], 'channel_right_wall': [0.46, 0.0, 0.035]}
  channel_axis: [0, -1, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 40
  channel_length_m: 0.16
  force_scale_n: 5
  realized_scene_sha256: c5fb87552d009c7e1ef813cadc54d289d6d9c896c1dd51a37fa468bf6305165e

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
| `object` | offset from object initial position (0.48615778212844485, 0.11898214746703403, 0.04) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.48615778212844485, -0.04101785253296597, 0.04) | final destination targets |
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

## Current Skill (Q=0.263) — your mutation base

```yaml
skill: peg_channel
phases:
- id: pull_1
  type: pull
  generator: arc_cartesian
  control: impedance_control
  termination: time_limit
  parameters:
    pull_angle:
      type: angle
      range:
      - 0.1
      - 1.2
- id: insert_1
  type: insert
  generator: impedance_motion
  control: impedance_control
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
- id: descend_1
  type: descend
  generator: linear_cartesian
  control: position_control
  termination: contact_detected
  parameters:
    depth:
      type: scalar
      range:
      - 0.01
      - 0.1
- id: contact_1
  type: contact
  generator: linear_cartesian
  control: impedance_control
  termination: force_exceeded
  parameters:
    speed:
      type: scalar
      range:
      - 0.005
      - 0.05

```

## Design Metrics

- **Composite score**: 0.263
- **task_score** (E): 0.000
- **fitness_score**: 0.240  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.333
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.310

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| pull_1 | 1.00 | 1.00 | 0.1691 |
| insert_1 | 0.00 | 1.00 | 0.3135 |
| descend_1 | 1.00 | 1.00 | 0.1521 |
| contact_1 | 1.00 | 1.00 | 0.0043 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| pull_1 | pull | 1.00 / time_limit | (0.500, 0.200, 0.300)→(0.499, 0.051, 0.380) | (0.517, 0.080, 0.040)→(0.503, 0.080, 0.034) | 0.162→0.160 | 1.00 / 1.000 | 0.565 | 3.526 |
| insert_1 | insert | 0.00 / step_budget | (0.499, 0.051, 0.380)→(0.496, -0.060, 0.087) | (0.503, 0.080, 0.034)→(0.503, 0.080, 0.034) | 0.160→0.160 | 1.00 / 1.000 | 0.544 | 0.584 |
| descend_1 | descend | 1.00 / step_budget | (0.496, -0.060, 0.087)→(0.498, 0.084, 0.039) | (0.503, 0.080, 0.034)→(0.503, 0.115, 0.034) | 0.160→0.196 | 1.00 / 2.667 | 158.104 | 248.237 |
| contact_1 | contact | 1.00 / force_exceeded | (0.498, 0.084, 0.039)→(0.497, 0.088, 0.037) | (0.503, 0.115, 0.034)→(0.504, 0.126, 0.028) | 0.196→0.206 | 1.00 / 3.000 | 1330.849 | 34.014 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.000
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.000
- phase_score: 0.423
- phase_breakdown.contact_score: 0.559
- phase_breakdown.approach_score: 0.482
- phase_breakdown.push_score: 0.358

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.254
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.000
- **Median Q (composite search score)**: 0.264
- **K-run variance**: 0.0001
- **Stagnated**: yes
  → Parameter optimiser converged to local optimum; structural change likely needed
- **Stop reason**: tolfun
- **Mean generations**: 4.3
- **Final σ (mean)**: 0.303


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `a8ce855c7f52ba2d198de8387bdd2f3b869655c206850d620daaec6ac6f298cd`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.04,0.04]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `79b30dd7102e96fb2fa0880d3932c959e04a6f943c7e87b878f77a0e54f87a94`; realized-scene SHA-256: `c5fb87552d009c7e1ef813cadc54d289d6d9c896c1dd51a37fa468bf6305165e`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.48616,0.11898,0.04]},{"name":"goal","value":[0.48616,-0.04102,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.48616,0.11898,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.48616,-0.04102,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.86897,"average_solve_count":145.0,"average_success_count":145.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"contact_1.speed":0.04994,"descend_1.depth":0.04909,"insert_1.insertion_depth":0.07295,"insert_1.insertion_force":6.88888,"pull_1.pull_angle":1.07714},"optimized_scores":{"best_composite_score":0.24869,"best_fitness_score":0.22536,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"world","contact_count":106.0,"contact_point_centroid":[0.49719,0.15284,-0.00149],"force_p95":1.4236,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.9927,"mean_force":0.66675,"phase_index":3.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.48974,0.10208,0.03934]},{"body_a":"peg","body_b":"channel_base_body","contact_count":975.0,"contact_point_centroid":[0.49614,0.11916,0.00943],"force_p95":0.61356,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.24822,"mean_force":0.5483,"phase_index":0.0,"phase_name":"pull_1","phase_type":"pull","tcp_position_centroid":[0.49843,0.13207,0.3481]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.49598,0.11923,0.00945],"force_p95":0.60434,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.66317,"mean_force":0.54215,"phase_index":2.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49244,0.01756,0.06358]},{"body_a":"attachment","body_b":"peg","contact_count":6.0,"contact_point_centroid":[0.49522,0.10212,0.05075],"force_p95":1.51602,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.6403,"mean_force":0.82939,"phase_index":2.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49208,0.0902,0.0456]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":24.0,"contact_point_centroid":[0.47288,0.11898,0.03087],"force_p95":0.72905,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.86893,"mean_force":0.3628,"phase_index":0.0,"phase_name":"pull_1","phase_type":"pull","tcp_position_centroid":[0.49943,0.19904,0.29999]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.49603,0.11916,0.00943],"force_p95":0.5951,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.64787,"mean_force":0.54147,"phase_index":1.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.49691,-0.00437,0.23233]},{"body_a":"peg","body_b":"channel_base_body","contact_count":14.0,"contact_point_centroid":[0.50104,0.11984,0.00973],"force_p95":0.44786,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.47385,"mean_force":0.25855,"phase_index":3.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49177,0.09702,0.0435]}],"total_contact_groups":7},"final_pose_error":0.04377,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.4979,0.16003,0.01392],"final_tcp_position":[0.48909,0.10649,0.0371],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48616,0.11898,0.04]},"peak_contact_force":3893.49745,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49599,0.11946,0.03385],"object_pos_start":[0.48616,0.11898,0.04],"object_to_goal_dist_end":0.19959,"object_to_goal_dist_start":0.19946,"object_z_max":0.04,"peak_contact_force":0.59887,"phase_name":"pull_1","phase_peak_obstacle_force":0.0,"phase_type":"pull","raw_contact_event_count":999.0,"raw_peak_contact_force":2.24822,"tcp_end":[0.49865,0.0507,0.38034],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.35326,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49606,0.11913,0.03399],"object_pos_start":[0.49599,0.11946,0.03385],"object_to_goal_dist_end":0.19925,"object_to_goal_dist_start":0.19959,"object_z_max":0.03405,"peak_contact_force":0.54271,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":1000.0,"raw_peak_contact_force":0.64787,"tcp_end":[0.49625,-0.05978,0.087],"tcp_start":[0.49865,0.0507,0.38034],"tcp_to_object_dist_end":0.1866,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49602,0.12943,0.0323],"object_pos_start":[0.49606,0.11913,0.03399],"object_to_goal_dist_end":0.20961,"object_to_goal_dist_start":0.19925,"object_z_max":0.03425,"peak_contact_force":0.42702,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1006.0,"raw_peak_contact_force":1.66317,"tcp_end":[0.49212,0.09634,0.04408],"tcp_start":[0.49625,-0.05978,0.087],"tcp_to_object_dist_end":0.03535,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":125.0,"n_steps_budget":690.0,"object_pos_end":[0.4979,0.16003,0.01392],"object_pos_start":[0.49602,0.12943,0.0323],"object_to_goal_dist_end":0.24145,"object_to_goal_dist_start":0.20961,"object_z_max":0.0323,"peak_contact_force":3893.49745,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":120.0,"raw_peak_contact_force":2.9927,"tcp_end":[0.48909,0.10649,0.0371],"tcp_start":[0.49212,0.09634,0.04408],"tcp_to_object_dist_end":0.05901,"terminated_normally":true,"termination_reason":"force_exceeded"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `0a7722137b05abd45e72adac5a0a8f18d70c24ddc36cf4c70c52ed7e5618005d`; realized-scene SHA-256: `a0d7ea14565b0a67e86de15fa43f3773b761884db645527685cd53e0fd95aeb9`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.52962,0.06295,0.04]},{"name":"goal","value":[0.52962,-0.09705,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.52962,0.06295,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.52962,-0.09705,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.91304,"average_solve_count":138.0,"average_success_count":138.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"contact_1.speed":0.02582,"descend_1.depth":0.05707,"insert_1.insertion_depth":0.07123,"insert_1.insertion_force":7.49553,"pull_1.pull_angle":0.68684},"optimized_scores":{"best_composite_score":0.27724,"best_fitness_score":0.2539,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":85.0,"contact_point_centroid":[0.54572,0.08036,0.05995],"force_p95":325.02143,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":369.84552,"mean_force":188.92433,"phase_index":2.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50096,0.0806,0.03637]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":77.0,"contact_point_centroid":[0.52506,0.0806,0.05997],"force_p95":239.82688,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":251.13486,"mean_force":168.06839,"phase_index":2.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50098,0.08066,0.03637]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.5457,0.08065,0.05996],"force_p95":34.88881,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":34.88881,"mean_force":34.88881,"phase_index":3.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50071,0.08084,0.03681]},{"body_a":"attachment","body_b":"peg","contact_count":260.0,"contact_point_centroid":[0.50302,0.06838,0.04362],"force_p95":21.24176,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":34.6006,"mean_force":10.0054,"phase_index":2.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49951,0.05704,0.04368]},{"body_a":"peg","body_b":"channel_base_body","contact_count":930.0,"contact_point_centroid":[0.50629,0.07532,0.00952],"force_p95":12.63377,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":29.39502,"mean_force":2.91329,"phase_index":2.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49684,0.01125,0.05909]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":1.0,"contact_point_centroid":[0.525,0.08082,0.06],"force_p95":25.0779,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":25.0779,"mean_force":25.0779,"phase_index":3.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50071,0.08084,0.03681]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":232.0,"contact_point_centroid":[0.52511,0.0822,0.03286],"force_p95":9.53843,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":17.23576,"mean_force":4.31063,"phase_index":2.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49941,0.05524,0.04427]},{"body_a":"peg","body_b":"channel_base_body","contact_count":972.0,"contact_point_centroid":[0.50586,0.06296,0.00937],"force_p95":0.55508,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.88411,"mean_force":0.56049,"phase_index":0.0,"phase_name":"pull_1","phase_type":"pull","tcp_position_centroid":[0.49843,0.13187,0.34825]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":34.0,"contact_point_centroid":[0.53102,0.06295,0.03156],"force_p95":1.1362,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.98455,"mean_force":0.48262,"phase_index":0.0,"phase_name":"pull_1","phase_type":"pull","tcp_position_centroid":[0.4993,0.19877,0.29989]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.50595,0.06304,0.00939],"force_p95":0.55181,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55532,"mean_force":0.54648,"phase_index":1.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.49691,-0.00437,0.23233]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1.0,"contact_point_centroid":[0.52153,0.12,0.00941],"force_p95":0.50535,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.50535,"mean_force":0.50535,"phase_index":3.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50071,0.08084,0.03681]}],"total_contact_groups":11},"final_pose_error":0.05047,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50633,0.11089,0.03385],"final_tcp_position":[0.50078,0.08087,0.03684],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.52962,0.06295,0.04]},"peak_contact_force":369.84552,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50593,0.06297,0.0338],"object_pos_start":[0.52962,0.06295,0.04],"object_to_goal_dist_end":0.14323,"object_to_goal_dist_start":0.14598,"object_z_max":0.04001,"peak_contact_force":0.54709,"phase_name":"pull_1","phase_peak_obstacle_force":0.0,"phase_type":"pull","raw_contact_event_count":1006.0,"raw_peak_contact_force":3.88411,"tcp_end":[0.49865,0.0507,0.38034],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.34683,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50607,0.06302,0.03384],"object_pos_start":[0.50593,0.06297,0.0338],"object_to_goal_dist_end":0.14328,"object_to_goal_dist_start":0.14323,"object_z_max":0.03385,"peak_contact_force":0.54545,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":1000.0,"raw_peak_contact_force":0.55532,"tcp_end":[0.49625,-0.05978,0.087],"tcp_start":[0.49865,0.0507,0.38034],"tcp_to_object_dist_end":0.13417,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50634,0.11094,0.03385],"object_pos_start":[0.50607,0.06302,0.03384],"object_to_goal_dist_end":0.19115,"object_to_goal_dist_start":0.14328,"object_z_max":0.03839,"peak_contact_force":150.35086,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1584.0,"raw_peak_contact_force":369.84552,"tcp_end":[0.50071,0.08084,0.03681],"tcp_start":[0.49625,-0.05978,0.087],"tcp_to_object_dist_end":0.03076,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.50633,0.11089,0.03385],"object_pos_start":[0.50634,0.11094,0.03385],"object_to_goal_dist_end":0.1911,"object_to_goal_dist_start":0.19115,"object_z_max":0.03385,"peak_contact_force":34.88881,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":3.0,"raw_peak_contact_force":34.88881,"tcp_end":[0.50078,0.08087,0.03684],"tcp_start":[0.50071,0.08084,0.03681],"tcp_to_object_dist_end":0.03067,"terminated_normally":true,"termination_reason":"force_exceeded"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `bf9c239495ea25cc1b534d0795871edaef0fee72244885088104a44eb548c1a2`; realized-scene SHA-256: `11c1f773d01ee1d435c5ecc0d1531095d6f84a2c0ab26c3ff2560d4c62fcd41a`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.53648,0.05661,0.04]},{"name":"goal","value":[0.53648,-0.10339,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.53648,0.05661,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.53648,-0.10339,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.91241,"average_solve_count":137.0,"average_success_count":137.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"contact_1.speed":0.03175,"descend_1.depth":0.05205,"insert_1.insertion_depth":0.09134,"insert_1.insertion_force":6.65716,"pull_1.pull_angle":0.91486},"optimized_scores":{"best_composite_score":0.26411,"best_fitness_score":0.24078,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":101.0,"contact_point_centroid":[0.54575,0.07427,0.05993],"force_p95":333.42718,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":373.20215,"mean_force":208.50226,"phase_index":2.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50091,0.0748,0.0365]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":95.0,"contact_point_centroid":[0.52506,0.07478,0.05997],"force_p95":298.78177,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":325.2003,"mean_force":180.896,"phase_index":2.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50092,0.07484,0.0365]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":1.0,"contact_point_centroid":[0.52519,0.07615,0.05991],"force_p95":64.1597,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":64.1597,"mean_force":64.1597,"phase_index":3.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50106,0.07617,0.03678]},{"body_a":"attachment","body_b":"peg","contact_count":309.0,"contact_point_centroid":[0.50361,0.06571,0.04398],"force_p95":26.49174,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":45.7529,"mean_force":12.25361,"phase_index":2.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49972,0.05443,0.04302]},{"body_a":"peg","body_b":"channel_base_body","contact_count":933.0,"contact_point_centroid":[0.50664,0.07087,0.00954],"force_p95":17.3461,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":34.06682,"mean_force":3.81199,"phase_index":2.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49699,0.01009,0.0585]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":275.0,"contact_point_centroid":[0.52526,0.0786,0.0355],"force_p95":14.14822,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":25.53383,"mean_force":6.58451,"phase_index":2.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49956,0.05158,0.04389]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.54611,0.07574,0.05987],"force_p95":10.01317,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":10.01317,"mean_force":10.01317,"phase_index":3.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50106,0.07617,0.03678]},{"body_a":"peg","body_b":"channel_base_body","contact_count":971.0,"contact_point_centroid":[0.506,0.05661,0.00937],"force_p95":0.59948,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.44541,"mean_force":0.56302,"phase_index":0.0,"phase_name":"pull_1","phase_type":"pull","tcp_position_centroid":[0.49843,0.1318,0.3483]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":37.0,"contact_point_centroid":[0.53251,0.05661,0.02607],"force_p95":1.30561,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.83578,"mean_force":0.52649,"phase_index":0.0,"phase_name":"pull_1","phase_type":"pull","tcp_position_centroid":[0.49926,0.19868,0.29987]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1.0,"contact_point_centroid":[0.51634,0.11999,0.00978],"force_p95":1.83135,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.83135,"mean_force":1.83135,"phase_index":3.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50106,0.07617,0.03678]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.50564,0.088,0.04437],"force_p95":1.50367,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.50367,"mean_force":1.50367,"phase_index":3.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50106,0.07617,0.03678]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.50612,0.05664,0.00938],"force_p95":0.55015,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55021,"mean_force":0.54674,"phase_index":1.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.49691,-0.00437,0.23233]}],"total_contact_groups":12},"final_pose_error":0.04974,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50677,0.1056,0.03504],"final_tcp_position":[0.50106,0.07619,0.03678],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.53648,0.05661,0.04]},"peak_contact_force":373.20215,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50611,0.0566,0.03378],"object_pos_start":[0.53648,0.05661,0.04],"object_to_goal_dist_end":0.13688,"object_to_goal_dist_start":0.1414,"object_z_max":0.04001,"peak_contact_force":0.54967,"phase_name":"pull_1","phase_peak_obstacle_force":0.0,"phase_type":"pull","raw_contact_event_count":1008.0,"raw_peak_contact_force":4.44541,"tcp_end":[0.49865,0.0507,0.38034],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.3467,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50615,0.05661,0.03378],"object_pos_start":[0.50611,0.0566,0.03378],"object_to_goal_dist_end":0.13688,"object_to_goal_dist_start":0.13688,"object_z_max":0.03378,"peak_contact_force":0.545,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":1000.0,"raw_peak_contact_force":0.55021,"tcp_end":[0.49625,-0.05978,0.087],"tcp_start":[0.49865,0.0507,0.38034],"tcp_to_object_dist_end":0.12836,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":992.0,"n_steps_budget":1000.0,"object_pos_end":[0.50677,0.10557,0.03501],"object_pos_start":[0.50615,0.05661,0.03378],"object_to_goal_dist_end":0.18576,"object_to_goal_dist_start":0.13688,"object_z_max":0.03902,"peak_contact_force":323.53354,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1713.0,"raw_peak_contact_force":373.20215,"tcp_end":[0.50106,0.07617,0.03678],"tcp_start":[0.49625,-0.05978,0.087],"tcp_to_object_dist_end":0.03,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1.0,"n_steps_budget":990.0,"object_pos_end":[0.50677,0.1056,0.03504],"object_pos_start":[0.50677,0.10557,0.03501],"object_to_goal_dist_end":0.18579,"object_to_goal_dist_start":0.18576,"object_z_max":0.03501,"peak_contact_force":64.1597,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":4.0,"raw_peak_contact_force":64.1597,"tcp_end":[0.50106,0.07619,0.03678],"tcp_start":[0.50106,0.07617,0.03678],"tcp_to_object_dist_end":0.03001,"terminated_normally":true,"termination_reason":"force_exceeded"}],"success":true}]}
```