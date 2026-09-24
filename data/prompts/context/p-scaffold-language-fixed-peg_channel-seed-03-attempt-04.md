## Search State

- **Seed**: 3
- **Iteration**: 5 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 4 | approach → descend → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 6 | 0.0567 | 0.16 | ❌ rejected |
| 3 | align → approach → contact → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 6 | 0.1016 | 0.21 | ❌ rejected |
| 2 | align → approach → contact → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 6 | 0.1392 | 0.28 | ✅ accepted |
| 1 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 7 | -0.1455 | 0.00 | ❌ rejected |
| 0 | align → approach → contact → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 6 | 0.0963 | 0.18 | ✅ accepted |

**Proposal policy**: task_score is 0.16 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
- task_score stagnant: change coupled targets, parameters, terminations, phase types, controls, subtasks, or ordering when evidence shows they need to change together.
A HOLD wastes an iteration when task_score is below 0.9.

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
- Frozen realised-scene SHA-256: `990d03f436076caee02f5d9d8b3b9b0b3759564b7644084e4eac46818881d834`
- Frozen object start: [0.46685193337148995, 0.058944840527687975, 0.04]
- Frozen task target: [0.46685193337148995, -0.10105515947231203, 0.04]
- Goal object position: (0.46685193337148995, -0.10105515947231203, 0.04)
- Task success criterion: peg must traverse the channel (0.16 m long) along axis (0.0, -1.0, 0.0); score = axial progress × lateral alignment — NOT a fixed TCP endpoint
- Object initial pose: (0.46685193337148995, 0.058944840527687975, 0.04)
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
  frozen_object_start: [0.4669, 0.0589, 0.04]
  frozen_task_target: [0.4669, -0.1011, 0.04]
  frozen_fixture_position: [0.54, 0, 0.035]
  frozen_object_starts: {'peg': [0.46685193337148995, 0.058944840527687975, 0.04]}
  frozen_targets: {'channel_exit': [0.46685193337148995, -0.10105515947231203, 0.04]}
  frozen_fixtures: {'channel_left_wall': [0.54, 0.0, 0.035], 'channel_right_wall': [0.46, 0.0, 0.035]}
  channel_axis: [0, -1, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 40
  channel_length_m: 0.16
  force_scale_n: 5
  realized_scene_sha256: 990d03f436076caee02f5d9d8b3b9b0b3759564b7644084e4eac46818881d834

## Subtask Layer

**Mode**: fixed (subtask targets are defined by the task configuration)

Available subtask IDs for phase binding:
| Subtask ID | Anchor | Target offset (m) | Metric | CMA-ES offset param |
|---|---|---|---|---|
| approach | object | (0.00, 0.04, 0.00) | distance | — |
| contact | object | (0.00, 0.02, 0.00) | distance | — |
| push | world | (0.50, -0.08, 0.04) | distance | push_depth |

Annotate phases with `subtask_id: <id>` to bind them to a subtask target.
- A phase bound to a subtask receives a navigation waypoint computed from that subtask's anchor and offset.
- Only the **last phase** bound to a given subtask is used for subtask scoring.
- Phases without `subtask_id` are not scored against subtasks but still execute normally.

## Current Skill (Q=0.057) — your mutation base

```yaml
skill: peg_channel
phases:
- id: align_1
  type: align
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  parameters:
    lateral_offset_y:
      type: scalar
      range:
      - -0.01
      - 0.01
- id: approach_1
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  parameters:
    approach_height:
      type: scalar
      range:
      - 0.05
      - 0.3
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1
- id: contact_1
  type: contact
  generator: impedance_motion
  control: force_threshold_switch
  termination: force_exceeded
  parameters:
    contact_force:
      type: scalar
      range:
      - 1.0
      - 20.0
- id: push_1
  type: push
  generator: linear_cartesian
  control: impedance_control
  termination: pose_tolerance
  parameters:
    push_depth:
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

```

## Design Metrics

- **Composite score**: 0.057
- **task_score** (E): 0.162
- **fitness_score**: 0.247  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.200
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.390

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_high | 1.00 | 1.00 | 0.2555 |
| descend_to_contact | 1.00 | 1.00 | 0.0160 |
| contact_prepush | 1.00 | 1.00 | 0.0054 |
| push_channel | 0.33 | 1.00 | 0.0801 |
| retract_up | 0.00 | 1.00 | 0.1033 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_high | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.508, 0.128, 0.057) | (0.509, 0.081, 0.040)→(0.502, 0.081, 0.034) | 0.165→0.162 | 1.00 / 1.667 | 215.282 | 241.530 |
| descend_to_contact | descend | 1.00 / step_budget | (0.508, 0.128, 0.057)→(0.507, 0.126, 0.044) | (0.502, 0.081, 0.034)→(0.502, 0.082, 0.034) | 0.162→0.162 | 1.00 / 1.333 | 41.925 | 196.333 |
| contact_prepush | contact | 1.00 / force_exceeded | (0.507, 0.126, 0.044)→(0.504, 0.123, 0.041) | (0.502, 0.082, 0.034)→(0.502, 0.082, 0.034) | 0.162→0.162 | 1.00 / 2.000 | 28.114 | 28.114 |
| push_channel | push | 0.33 / step_budget | (0.504, 0.123, 0.041)→(0.497, 0.044, 0.038) | (0.502, 0.082, 0.034)→(0.505, 0.013, 0.039) | 0.162→0.093 | 1.00 / 2.667 | 43.477 | 170.553 |
| retract_up | retract | 0.00 / step_budget | (0.497, 0.044, 0.038)→(0.495, 0.026, 0.140) | (0.505, 0.013, 0.039)→(0.503, -0.006, 0.027) | 0.093→0.076 | 1.00 / 1.000 | 0.582 | 59.187 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.499
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.258
- phase_score: 0.334
- phase_breakdown.approach_score: 0.821
- phase_breakdown.contact_score: 0.640
- phase_breakdown.push_score: 0.070

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.304
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.258
- **Median Q (composite search score)**: 0.048
- **K-run variance**: 0.0019
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.453


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `cc7283febf3c95cef1fde4c5a16cbcb134186cb6faf3a169717a9aa53375931d`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.04,0.04]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `178d67757a065da6e29d31070e25f6065dc7e42bdbf58dfbff0deec513214033`; realized-scene SHA-256: `990d03f436076caee02f5d9d8b3b9b0b3759564b7644084e4eac46818881d834`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.46685,0.05894,0.04]},{"name":"goal","value":[0.46685,-0.10106,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.46685,0.05894,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.46685,-0.10106,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.4012,"average_solve_count":167.0,"average_success_count":167.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_high.speed":0.09056,"contact_prepush.contact_force":8.7449,"descend_to_contact.speed":0.09905,"push_channel.push_depth":0.11663,"push_channel.speed":0.04964,"retract_up.speed":0.06463},"optimized_scores":{"best_composite_score":0.04831,"best_fitness_score":0.23831,"best_task_score":0.11708},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_right_wall","contact_count":112.0,"contact_point_centroid":[0.47493,0.11847,0.05986],"force_p95":350.68504,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":365.85558,"mean_force":320.44394,"phase_index":0.0,"phase_name":"approach_high","phase_type":"approach","tcp_position_centroid":[0.47015,0.10813,0.06248]},{"body_a":"attachment","body_b":"channel_right_wall","contact_count":118.0,"contact_point_centroid":[0.47498,0.11477,0.05976],"force_p95":306.402,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":327.74246,"mean_force":240.26581,"phase_index":1.0,"phase_name":"descend_to_contact","phase_type":"descend","tcp_position_centroid":[0.48124,0.10659,0.05674]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":831.0,"contact_point_centroid":[0.53471,0.06108,0.05999],"force_p95":93.75058,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":98.12376,"mean_force":85.45569,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.4892,0.0619,0.03799]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":2.0,"contact_point_centroid":[0.53789,0.01768,0.05999],"force_p95":55.49924,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":56.31425,"mean_force":48.16415,"phase_index":4.0,"phase_name":"retract_up","phase_type":"retract","tcp_position_centroid":[0.4925,0.02086,0.03794]},{"body_a":"attachment","body_b":"peg","contact_count":671.0,"contact_point_centroid":[0.49764,0.03947,0.03937],"force_p95":38.25251,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":47.84104,"mean_force":11.28161,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49027,0.04934,0.03802]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.53142,0.101,0.05998],"force_p95":35.75301,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":35.75301,"mean_force":35.75301,"phase_index":2.0,"phase_name":"contact_prepush","phase_type":"contact","tcp_position_centroid":[0.48593,0.09972,0.0379]},{"body_a":"peg","body_b":"channel_base_body","contact_count":927.0,"contact_point_centroid":[0.50316,0.0238,0.00979],"force_p95":26.43765,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":33.15331,"mean_force":5.51302,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.48929,0.0608,0.038]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":421.0,"contact_point_centroid":[0.52522,0.01889,0.02143],"force_p95":22.57335,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":27.76151,"mean_force":10.65489,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49116,0.03848,0.03801]},{"body_a":"attachment","body_b":"peg","contact_count":14.0,"contact_point_centroid":[0.49898,0.01183,0.03502],"force_p95":5.8038,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":11.80517,"mean_force":1.38588,"phase_index":4.0,"phase_name":"retract_up","phase_type":"retract","tcp_position_centroid":[0.49213,0.0207,0.03838]},{"body_a":"peg","body_b":"channel_base_body","contact_count":988.0,"contact_point_centroid":[0.50564,-0.03494,0.00829],"force_p95":0.73395,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.32124,"mean_force":0.64762,"phase_index":4.0,"phase_name":"retract_up","phase_type":"retract","tcp_position_centroid":[0.49069,0.01605,0.09208]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":24.0,"contact_point_centroid":[0.52511,-0.00387,0.02177],"force_p95":8.64877,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.89267,"mean_force":2.17032,"phase_index":4.0,"phase_name":"retract_up","phase_type":"retract","tcp_position_centroid":[0.4918,0.018,0.07034]},{"body_a":"peg","body_b":"channel_base_body","contact_count":868.0,"contact_point_centroid":[0.49424,0.05891,0.00937],"force_p95":0.55479,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.20518,"mean_force":0.56299,"phase_index":0.0,"phase_name":"approach_high","phase_type":"approach","tcp_position_centroid":[0.48056,0.14694,0.16157]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":35.0,"contact_point_centroid":[0.46807,0.05895,0.03796],"force_p95":1.19991,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.42382,"mean_force":0.50385,"phase_index":0.0,"phase_name":"approach_high","phase_type":"approach","tcp_position_centroid":[0.49901,0.19835,0.29604]},{"body_a":"peg","body_b":"channel_base_body","contact_count":21.0,"contact_point_centroid":[0.4944,0.05955,0.0094],"force_p95":0.54961,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.5514,"mean_force":0.54548,"phase_index":2.0,"phase_name":"contact_prepush","phase_type":"contact","tcp_position_centroid":[0.48635,0.10069,0.03893]},{"body_a":"peg","body_b":"channel_base_body","contact_count":181.0,"contact_point_centroid":[0.4946,0.05905,0.00939],"force_p95":0.54999,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55091,"mean_force":0.54589,"phase_index":1.0,"phase_name":"descend_to_contact","phase_type":"descend","tcp_position_centroid":[0.48244,0.10581,0.05412]}],"total_contact_groups":15},"final_pose_error":0.15539,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50465,-0.03759,0.0241],"final_tcp_position":[0.49244,0.01184,0.14525],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.46685,0.05894,0.04]},"peak_contact_force":365.85558,"phases":[{"contact_detected":true,"contact_event_count":2.0,"n_steps":897.0,"n_steps_budget":1000.0,"object_pos_end":[0.49427,0.05887,0.03391],"object_pos_start":[0.46685,0.05894,0.04],"object_to_goal_dist_end":0.13912,"object_to_goal_dist_start":0.14284,"object_z_max":0.04001,"peak_contact_force":332.14499,"phase_name":"approach_high","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1015.0,"raw_peak_contact_force":365.85558,"tcp_end":[0.4742,0.10665,0.06043],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.05821,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":181.0,"n_steps_budget":600.0,"object_pos_end":[0.49419,0.05915,0.03394],"object_pos_start":[0.49427,0.05887,0.03391],"object_to_goal_dist_end":0.1394,"object_to_goal_dist_start":0.13912,"object_z_max":0.03394,"peak_contact_force":0.54782,"phase_name":"descend_to_contact","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":299.0,"raw_peak_contact_force":327.74246,"tcp_end":[0.48698,0.10156,0.04018],"tcp_start":[0.4742,0.10665,0.06043],"tcp_to_object_dist_end":0.04347,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":21.0,"n_steps_budget":600.0,"object_pos_end":[0.49414,0.05916,0.03394],"object_pos_start":[0.49419,0.05915,0.03394],"object_to_goal_dist_end":0.13942,"object_to_goal_dist_start":0.1394,"object_z_max":0.03394,"peak_contact_force":35.75301,"phase_name":"contact_prepush","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":22.0,"raw_peak_contact_force":35.75301,"subtask_id":"contact","tcp_end":[0.48591,0.09964,0.03782],"tcp_start":[0.48698,0.10156,0.04018],"tcp_to_object_dist_end":0.04149,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50742,-0.01008,0.04062],"object_pos_start":[0.49414,0.05916,0.03394],"object_to_goal_dist_end":0.07031,"object_to_goal_dist_start":0.13942,"object_z_max":0.04071,"peak_contact_force":0.0,"phase_name":"push_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2850.0,"raw_peak_contact_force":98.12376,"subtask_id":"push","tcp_end":[0.49251,0.02093,0.03795],"tcp_start":[0.48591,0.09964,0.03782],"tcp_to_object_dist_end":0.03451,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50465,-0.03759,0.0241],"object_pos_start":[0.50742,-0.01008,0.04062],"object_to_goal_dist_end":0.04553,"object_to_goal_dist_start":0.07031,"object_z_max":0.04082,"peak_contact_force":0.63682,"phase_name":"retract_up","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1028.0,"raw_peak_contact_force":56.31425,"tcp_end":[0.49244,0.01184,0.14525],"tcp_start":[0.49251,0.02093,0.03795],"tcp_to_object_dist_end":0.13141,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `1ee374347cb6f80436633ebcb956aaa73ea8a10685d65b21d5c3814cf0c53498`; realized-scene SHA-256: `5d75b33f12bcf5a2f8bdcc4693a93f63ce145f4d32d6acfe75032964e261854c`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.53544,0.08091,0.04]},{"name":"goal","value":[0.53544,-0.07909,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.53544,0.08091,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.53544,-0.07909,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.27419,"average_solve_count":186.0,"average_success_count":186.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_high.speed":0.06364,"contact_prepush.contact_force":11.91148,"descend_to_contact.speed":0.04382,"push_channel.push_depth":0.08929,"push_channel.speed":0.04887,"retract_up.speed":0.06328},"optimized_scores":{"best_composite_score":0.00818,"best_fitness_score":0.19818,"best_task_score":0.11242},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_left_wall","contact_count":151.0,"contact_point_centroid":[0.53613,0.11994,0.05984],"force_p95":338.03867,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":355.40423,"mean_force":316.67934,"phase_index":0.0,"phase_name":"approach_high","phase_type":"approach","tcp_position_centroid":[0.52883,0.12895,0.06256]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":445.0,"contact_point_centroid":[0.53486,0.11996,0.05995],"force_p95":219.88723,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":260.68077,"mean_force":196.67224,"phase_index":1.0,"phase_name":"descend_to_contact","phase_type":"descend","tcp_position_centroid":[0.52953,0.13035,0.062]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":932.0,"contact_point_centroid":[0.52503,0.10271,0.05998],"force_p95":188.98507,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":235.10331,"mean_force":145.6264,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50863,0.10767,0.04651]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":3.0,"contact_point_centroid":[0.52501,0.05897,0.06],"force_p95":64.58693,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":71.76326,"mean_force":23.92109,"phase_index":4.0,"phase_name":"retract_up","phase_type":"retract","tcp_position_centroid":[0.50079,0.05878,0.03972]},{"body_a":"attachment","body_b":"peg","contact_count":436.0,"contact_point_centroid":[0.50366,0.06826,0.04099],"force_p95":30.36496,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":47.12251,"mean_force":9.66948,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50204,0.0799,0.04159]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.50372,0.06405,0.00962],"force_p95":13.6882,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":46.59529,"mean_force":4.68233,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50833,0.10674,0.04634]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":1.0,"contact_point_centroid":[0.525,0.11997,0.06],"force_p95":29.43141,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":29.43141,"mean_force":29.43141,"phase_index":2.0,"phase_name":"contact_prepush","phase_type":"contact","tcp_position_centroid":[0.52091,0.13193,0.05238]},{"body_a":"peg","body_b":"channel_base_body","contact_count":991.0,"contact_point_centroid":[0.49923,0.00017,0.00837],"force_p95":0.72836,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.22334,"mean_force":0.65468,"phase_index":4.0,"phase_name":"retract_up","phase_type":"retract","tcp_position_centroid":[0.49709,0.04577,0.09121]},{"body_a":"attachment","body_b":"peg","contact_count":13.0,"contact_point_centroid":[0.5024,0.0468,0.03912],"force_p95":5.36607,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":6.77294,"mean_force":1.4675,"phase_index":4.0,"phase_name":"retract_up","phase_type":"retract","tcp_position_centroid":[0.50039,0.05844,0.03998]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":40.0,"contact_point_centroid":[0.47485,-0.00192,0.04662],"force_p95":5.89015,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":6.1783,"mean_force":1.07729,"phase_index":4.0,"phase_name":"retract_up","phase_type":"retract","tcp_position_centroid":[0.49829,0.05177,0.06621]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":9.0,"contact_point_centroid":[0.52505,0.01748,0.0246],"force_p95":5.91238,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":6.08789,"mean_force":1.58297,"phase_index":4.0,"phase_name":"retract_up","phase_type":"retract","tcp_position_centroid":[0.49676,0.05162,0.06482]},{"body_a":"peg","body_b":"channel_base_body","contact_count":947.0,"contact_point_centroid":[0.5058,0.08087,0.00937],"force_p95":0.55077,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.32595,"mean_force":0.56288,"phase_index":0.0,"phase_name":"approach_high","phase_type":"approach","tcp_position_centroid":[0.5158,0.15752,0.15828]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":36.0,"contact_point_centroid":[0.5324,0.0809,0.02649],"force_p95":1.27622,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.70803,"mean_force":0.52144,"phase_index":0.0,"phase_name":"approach_high","phase_type":"approach","tcp_position_centroid":[0.49983,0.19867,0.29612]},{"body_a":"peg","body_b":"channel_base_body","contact_count":455.0,"contact_point_centroid":[0.50601,0.08085,0.00938],"force_p95":0.55006,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55006,"mean_force":0.54677,"phase_index":1.0,"phase_name":"descend_to_contact","phase_type":"descend","tcp_position_centroid":[0.52944,0.13039,0.0619]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1.0,"contact_point_centroid":[0.49001,0.08914,0.00938],"force_p95":0.54527,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54527,"mean_force":0.54527,"phase_index":2.0,"phase_name":"contact_prepush","phase_type":"contact","tcp_position_centroid":[0.52091,0.13193,0.05238]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":2.0,"contact_point_centroid":[0.52501,0.07213,0.06],"force_p95":0.33806,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.34136,"mean_force":0.30841,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50419,0.10661,0.04516]}],"total_contact_groups":16},"final_pose_error":0.16114,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49925,-0.00466,0.0241],"final_tcp_position":[0.49715,0.03421,0.14256],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.53544,0.08091,0.04]},"peak_contact_force":355.40423,"phases":[{"contact_detected":true,"contact_event_count":2.0,"n_steps":976.0,"n_steps_budget":1000.0,"object_pos_end":[0.50597,0.0809,0.03378],"object_pos_start":[0.53544,0.08091,0.04],"object_to_goal_dist_end":0.16113,"object_to_goal_dist_start":0.16476,"object_z_max":0.04001,"peak_contact_force":313.15772,"phase_name":"approach_high","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1134.0,"raw_peak_contact_force":355.40423,"tcp_end":[0.52961,0.12943,0.06268],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.06123,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":455.0,"n_steps_budget":600.0,"object_pos_end":[0.50595,0.08088,0.03378],"object_pos_start":[0.50597,0.0809,0.03378],"object_to_goal_dist_end":0.16111,"object_to_goal_dist_start":0.16113,"object_z_max":0.03378,"peak_contact_force":124.67524,"phase_name":"descend_to_contact","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":900.0,"raw_peak_contact_force":260.68077,"tcp_end":[0.52091,0.13193,0.05238],"tcp_start":[0.52961,0.12943,0.06268],"tcp_to_object_dist_end":0.05635,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1.0,"n_steps_budget":600.0,"object_pos_end":[0.50597,0.08089,0.03378],"object_pos_start":[0.50595,0.08088,0.03378],"object_to_goal_dist_end":0.16113,"object_to_goal_dist_start":0.16111,"object_z_max":0.03378,"peak_contact_force":29.43141,"phase_name":"contact_prepush","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2.0,"raw_peak_contact_force":29.43141,"subtask_id":"contact","tcp_end":[0.52064,0.13192,0.05204],"tcp_start":[0.52091,0.13193,0.05238],"tcp_to_object_dist_end":0.05615,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49972,0.02548,0.04059],"object_pos_start":[0.50597,0.08089,0.03378],"object_to_goal_dist_end":0.10548,"object_to_goal_dist_start":0.16113,"object_z_max":0.04059,"peak_contact_force":118.98336,"phase_name":"push_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2370.0,"raw_peak_contact_force":235.10331,"subtask_id":"push","tcp_end":[0.5008,0.05887,0.03973],"tcp_start":[0.52064,0.13192,0.05204],"tcp_to_object_dist_end":0.03342,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49925,-0.00466,0.0241],"object_pos_start":[0.49972,0.02548,0.04059],"object_to_goal_dist_end":0.077,"object_to_goal_dist_start":0.10548,"object_z_max":0.04081,"peak_contact_force":0.56204,"phase_name":"retract_up","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1056.0,"raw_peak_contact_force":71.76326,"tcp_end":[0.49715,0.03421,0.14256],"tcp_start":[0.5008,0.05887,0.03973],"tcp_to_object_dist_end":0.12469,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `e082b57d1be6744ae6d3993c25b90215f3fc56dc7131af62e0630c4f325e4b04`; realized-scene SHA-256: `ca4f9624fc0e37438ffe7fd92236fc537e25f346e4aaef8c3b399c2f4b45089e`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.5244,0.10464,0.04]},{"name":"goal","value":[0.5244,-0.05536,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.5244,0.10464,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.5244,-0.05536,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.03941,"average_solve_count":203.0,"average_success_count":203.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_high.speed":0.0667,"contact_prepush.contact_force":10.99196,"descend_to_contact.speed":0.02884,"push_channel.push_depth":0.06434,"push_channel.speed":0.0481,"retract_up.speed":0.01741},"optimized_scores":{"best_composite_score":0.11369,"best_fitness_score":0.30369,"best_task_score":0.25764},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":800.0,"contact_point_centroid":[0.54718,0.09993,0.05998],"force_p95":109.77668,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":178.43117,"mean_force":73.08696,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50175,0.10306,0.03571]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":334.0,"contact_point_centroid":[0.52502,0.11294,0.05999],"force_p95":112.13147,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":138.28863,"mean_force":69.47603,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50183,0.11551,0.03554]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":3.0,"contact_point_centroid":[0.5434,0.05109,0.05999],"force_p95":49.03976,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":49.48251,"mean_force":41.89787,"phase_index":4.0,"phase_name":"retract_up","phase_type":"retract","tcp_position_centroid":[0.49841,0.05262,0.03694]},{"body_a":"peg","body_b":"channel_base_body","contact_count":868.0,"contact_point_centroid":[0.50404,0.0629,0.00977],"force_p95":12.90832,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":27.79267,"mean_force":2.05597,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50175,0.10315,0.03571]},{"body_a":"attachment","body_b":"peg","contact_count":516.0,"contact_point_centroid":[0.50446,0.0861,0.04114],"force_p95":15.34973,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":27.6854,"mean_force":2.77605,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.5014,0.09788,0.03589]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.555,0.12,0.06],"force_p95":19.15727,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":19.15727,"mean_force":19.15727,"phase_index":2.0,"phase_name":"contact_prepush","phase_type":"contact","tcp_position_centroid":[0.50687,0.13693,0.03382]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":232.0,"contact_point_centroid":[0.52515,0.05191,0.03453],"force_p95":2.17423,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.74197,"mean_force":0.45874,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.5003,0.08176,0.03644]},{"body_a":"peg","body_b":"channel_base_body","contact_count":990.0,"contact_point_centroid":[0.50647,0.01904,0.00958],"force_p95":0.59156,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.13251,"mean_force":0.51759,"phase_index":4.0,"phase_name":"retract_up","phase_type":"retract","tcp_position_centroid":[0.49516,0.04204,0.08403]},{"body_a":"attachment","body_b":"peg","contact_count":207.0,"contact_point_centroid":[0.50236,0.03708,0.05968],"force_p95":2.0075,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":3.65183,"mean_force":0.57669,"phase_index":4.0,"phase_name":"retract_up","phase_type":"retract","tcp_position_centroid":[0.4951,0.04848,0.05219]},{"body_a":"peg","body_b":"channel_base_body","contact_count":813.0,"contact_point_centroid":[0.50568,0.10462,0.00938],"force_p95":0.57574,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.33087,"mean_force":0.56024,"phase_index":0.0,"phase_name":"approach_high","phase_type":"approach","tcp_position_centroid":[0.50893,0.17219,0.16942]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":100.0,"contact_point_centroid":[0.52502,0.02021,0.05266],"force_p95":2.35142,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.48812,"mean_force":0.98165,"phase_index":4.0,"phase_name":"retract_up","phase_type":"retract","tcp_position_centroid":[0.4952,0.04823,0.05354]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":32.0,"contact_point_centroid":[0.52975,0.10463,0.03425],"force_p95":1.06006,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.32726,"mean_force":0.42874,"phase_index":0.0,"phase_name":"approach_high","phase_type":"approach","tcp_position_centroid":[0.49974,0.19901,0.29658]},{"body_a":"peg","body_b":"channel_base_body","contact_count":34.0,"contact_point_centroid":[0.50798,0.10495,0.00939],"force_p95":0.57572,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.57579,"mean_force":0.54629,"phase_index":1.0,"phase_name":"descend_to_contact","phase_type":"descend","tcp_position_centroid":[0.5165,0.14574,0.04483]},{"body_a":"peg","body_b":"channel_base_body","contact_count":80.0,"contact_point_centroid":[0.5056,0.10432,0.00939],"force_p95":0.5757,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.57577,"mean_force":0.54645,"phase_index":2.0,"phase_name":"contact_prepush","phase_type":"contact","tcp_position_centroid":[0.50933,0.14115,0.03661]}],"total_contact_groups":14},"final_pose_error":0.17206,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50617,0.02476,0.03386],"final_tcp_position":[0.49564,0.03263,0.13112],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.5244,0.10464,0.04]},"peak_contact_force":178.43117,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":840.0,"n_steps_budget":1000.0,"object_pos_end":[0.50589,0.10472,0.03384],"object_pos_start":[0.5244,0.10464,0.04],"object_to_goal_dist_end":0.18491,"object_to_goal_dist_start":0.18624,"object_z_max":0.04,"peak_contact_force":0.54261,"phase_name":"approach_high","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":845.0,"raw_peak_contact_force":3.33087,"tcp_end":[0.51916,0.14646,0.04816],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.04608,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":34.0,"n_steps_budget":600.0,"object_pos_end":[0.50587,0.10457,0.03384],"object_pos_start":[0.50589,0.10472,0.03384],"object_to_goal_dist_end":0.18476,"object_to_goal_dist_start":0.18491,"object_z_max":0.03384,"peak_contact_force":0.55166,"phase_name":"descend_to_contact","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":34.0,"raw_peak_contact_force":0.57579,"tcp_end":[0.51292,0.14517,0.04075],"tcp_start":[0.51916,0.14646,0.04816],"tcp_to_object_dist_end":0.04178,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":80.0,"n_steps_budget":600.0,"object_pos_end":[0.50582,0.10463,0.03384],"object_pos_start":[0.50587,0.10457,0.03384],"object_to_goal_dist_end":0.18482,"object_to_goal_dist_start":0.18476,"object_z_max":0.03384,"peak_contact_force":19.15727,"phase_name":"contact_prepush","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":81.0,"raw_peak_contact_force":19.15727,"subtask_id":"contact","tcp_end":[0.50683,0.13685,0.03378],"tcp_start":[0.51292,0.14517,0.04075],"tcp_to_object_dist_end":0.03224,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5066,0.02377,0.03618],"object_pos_start":[0.50582,0.10463,0.03384],"object_to_goal_dist_end":0.10405,"object_to_goal_dist_start":0.18482,"object_z_max":0.03642,"peak_contact_force":11.44903,"phase_name":"push_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2750.0,"raw_peak_contact_force":178.43117,"subtask_id":"push","tcp_end":[0.49843,0.05278,0.03697],"tcp_start":[0.50683,0.13685,0.03378],"tcp_to_object_dist_end":0.03015,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50617,0.02476,0.03386],"object_pos_start":[0.5066,0.02377,0.03618],"object_to_goal_dist_end":0.10513,"object_to_goal_dist_start":0.10405,"object_z_max":0.03695,"peak_contact_force":0.54775,"phase_name":"retract_up","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1300.0,"raw_peak_contact_force":49.48251,"tcp_end":[0.49564,0.03263,0.13112],"tcp_start":[0.49843,0.05278,0.03697],"tcp_to_object_dist_end":0.09814,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```