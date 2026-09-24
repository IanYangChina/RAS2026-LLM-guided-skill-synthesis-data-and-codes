## Search State

- **Seed**: 7
- **Iteration**: 4 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 3 | approach → contact → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | force_exceeded | pose_tolerance | 7 | -0.1366 | 0.02 | ❌ rejected |
| 2 | align → approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | force_threshold_switch | admittance_control | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 6 | 0.3441 | 0.62 | ❌ rejected |
| 1 | align → approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | force_threshold_switch | admittance_control | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 6 | 0.3446 | 0.63 | ✅ accepted |
| 0 | align → approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | force_threshold_switch | admittance_control | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 6 | 0.3475 | 0.62 | ✅ accepted |

**Proposal policy**: task_score is 0.02 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=-0.137) — your mutation base

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
  control: force_threshold_switch
  termination: pose_tolerance
  parameters:
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1
- id: contact_1
  type: contact
  generator: linear_cartesian
  control: admittance_control
  termination: force_exceeded
  parameters:
    contact_force:
      type: scalar
      range:
      - 1.0
      - 20.0
    speed:
      type: scalar
      range:
      - 0.005
      - 0.05
- id: push_1
  type: push
  generator: impedance_motion
  control: impedance_control
  termination: time_limit
  parameters:
    push_distance:
      type: scalar
      range:
      - 0.02
      - 0.2
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

- **Composite score**: -0.137
- **task_score** (E): 0.022
- **fitness_score**: 0.162  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.111
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.410

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach | 1.00 | 1.00 | 0.2388 |
| contact | 1.00 | 1.00 | 0.0331 |
| push | 0.00 | 1.00 | 0.0002 |
| retract | 1.00 | 1.00 | 0.2238 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.505, 0.150, 0.069) | (0.509, 0.098, 0.040)→(0.502, 0.098, 0.034) | 0.179→0.178 | 1.00 / 1.000 | 0.520 | 2.732 |
| contact | contact | 1.00 / step_budget | (0.505, 0.150, 0.069)→(0.504, 0.130, 0.043) | (0.502, 0.098, 0.034)→(0.503, 0.094, 0.035) | 0.178→0.174 | 1.00 / 2.000 | 20.542 | 22.277 |
| push | push | 0.00 / guard_failure | (0.504, 0.130, 0.043)→(0.504, 0.130, 0.043) | (0.503, 0.094, 0.035)→(0.503, 0.094, 0.035) | 0.174→0.174 | 1.00 / 1.333 | 189.033 | 189.328 |
| retract | retract | 1.00 / step_budget | (0.496, 0.139, 0.033)→(0.499, 0.190, 0.251) | (0.501, 0.109, 0.035)→(0.501, 0.109, 0.034) | 0.189→0.189 | 1.00 / 1.000 | 0.536 | 0.878 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.000
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.000
- phase_score: 0.212
- phase_breakdown.push_score: 0.020
- phase_breakdown.contact_score: 0.466
- phase_breakdown.approach_score: 0.537

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.181
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.038
- **Median Q (composite search score)**: -0.229
- **K-run variance**: 0.0176
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Parameters at lower bound**: approach.lateral_offset_y
- **Final σ (mean)**: 0.370


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.25185,"average_solve_count":135.0,"average_success_count":135.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach.lateral_offset_y":-0.00992,"approach.speed":0.18847,"contact.contact_force":19.62583,"contact.speed":0.01239,"push.push_distance":0.19731,"push.push_force_threshold":25.35997,"retract.speed":0.19276},"optimized_scores":{"best_composite_score":-0.23134,"best_fitness_score":0.17866,"best_task_score":0.03836},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":312.0,"contact_point_centroid":[0.50406,0.10622,0.00953],"force_p95":7.52652,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":10.94375,"mean_force":1.98442,"phase_index":1.0,"phase_name":"contact","phase_type":"contact","tcp_position_centroid":[0.50177,0.14872,0.04952]},{"body_a":"attachment","body_b":"peg","contact_count":68.0,"contact_point_centroid":[0.50307,0.12616,0.04775],"force_p95":9.40565,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":10.69067,"mean_force":6.82166,"phase_index":1.0,"phase_name":"contact","phase_type":"contact","tcp_position_centroid":[0.50047,0.13814,0.037]},{"body_a":"peg","body_b":"channel_base_body","contact_count":610.0,"contact_point_centroid":[0.50363,0.11165,0.00939],"force_p95":0.61029,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06328,"mean_force":0.55606,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.50232,0.18062,0.17992]},{"body_a":"attachment","body_b":"peg","contact_count":3.0,"contact_point_centroid":[0.5037,0.1232,0.05539],"force_p95":0.93577,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.96639,"mean_force":0.75177,"phase_index":3.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.49963,0.13527,0.03308]},{"body_a":"peg","body_b":"channel_base_body","contact_count":244.0,"contact_point_centroid":[0.50422,0.105,0.00948],"force_p95":0.63539,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.90797,"mean_force":0.5448,"phase_index":3.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.49872,0.16095,0.13616]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":16.0,"contact_point_centroid":[0.52601,0.11178,0.02875],"force_p95":0.50724,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54079,"mean_force":0.34334,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.49989,0.19942,0.29835]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1.0,"contact_point_centroid":[0.50506,0.08804,0.00998],"force_p95":0.49767,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.49767,"mean_force":0.49767,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.50028,0.13529,0.03366]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.50337,0.12329,0.04761],"force_p95":0.0,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.50028,0.13529,0.03366]}],"total_contact_groups":8},"final_pose_error":0.04993,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50483,0.10559,0.03392],"final_tcp_position":[0.50043,0.18907,0.25128],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.51001,0.11178,0.04]},"peak_contact_force":10.94375,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":632.0,"n_steps_budget":810.0,"object_pos_end":[0.50374,0.11174,0.03381],"object_pos_start":[0.51001,0.11178,0.04],"object_to_goal_dist_end":0.19188,"object_to_goal_dist_start":0.19204,"object_z_max":0.04,"peak_contact_force":0.51749,"phase_name":"approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":626.0,"raw_peak_contact_force":2.06328,"subtask_id":"approach","tcp_end":[0.50596,0.16293,0.06881],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.06205,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":315.0,"n_steps_budget":1000.0,"object_pos_end":[0.50489,0.10558,0.03526],"object_pos_start":[0.50374,0.11174,0.03381],"object_to_goal_dist_end":0.18571,"object_to_goal_dist_start":0.19188,"object_z_max":0.03533,"peak_contact_force":6.56074,"phase_name":"contact","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":380.0,"raw_peak_contact_force":10.94375,"subtask_id":"contact","tcp_end":[0.50028,0.13529,0.03366],"tcp_start":[0.50596,0.16293,0.06881],"tcp_to_object_dist_end":0.0301,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.50489,0.10554,0.03525],"object_pos_start":[0.50489,0.10558,0.03526],"object_to_goal_dist_end":0.18567,"object_to_goal_dist_start":0.18571,"object_z_max":0.03526,"peak_contact_force":0.02551,"phase_name":"push","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2.0,"raw_peak_contact_force":0.49767,"subtask_id":"push","tcp_end":[0.50038,0.13555,0.03349],"tcp_start":[0.50028,0.13529,0.03366],"tcp_to_object_dist_end":0.0304,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":244.0,"n_steps_budget":900.0,"object_pos_end":[0.50483,0.10559,0.03392],"object_pos_start":[0.50489,0.10554,0.03525],"object_to_goal_dist_end":0.18575,"object_to_goal_dist_start":0.18567,"object_z_max":0.03548,"peak_contact_force":0.54228,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":247.0,"raw_peak_contact_force":0.96639,"tcp_end":[0.50043,0.18907,0.25128],"tcp_start":[0.50038,0.13555,0.03349],"tcp_to_object_dist_end":0.23288,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.30366,"average_solve_count":191.0,"average_success_count":191.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach.lateral_offset_y":-0.01,"approach.speed":0.06768,"contact.contact_force":8.34868,"contact.speed":0.01989,"push.push_distance":0.09789,"push.push_force_threshold":40.75533,"retract.speed":0.08029},"optimized_scores":{"best_composite_score":-0.22922,"best_fitness_score":0.18078,"best_task_score":0.02892},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.49771,0.11224,0.00962],"force_p95":2.72288,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.16116,"mean_force":1.06943,"phase_index":1.0,"phase_name":"contact","phase_type":"contact","tcp_position_centroid":[0.48659,0.15245,0.04607]},{"body_a":"attachment","body_b":"peg","contact_count":305.0,"contact_point_centroid":[0.49371,0.13308,0.05191],"force_p95":2.72568,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":2.8108,"mean_force":1.92018,"phase_index":1.0,"phase_name":"contact","phase_type":"contact","tcp_position_centroid":[0.48947,0.14493,0.03708]},{"body_a":"peg","body_b":"channel_base_body","contact_count":712.0,"contact_point_centroid":[0.49614,0.11905,0.00943],"force_p95":0.60231,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.24822,"mean_force":0.55149,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.4908,0.18404,0.1804]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":24.0,"contact_point_centroid":[0.47288,0.11898,0.03087],"force_p95":0.72905,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.86893,"mean_force":0.3628,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.49956,0.19935,0.29772]},{"body_a":"peg","body_b":"channel_base_body","contact_count":256.0,"contact_point_centroid":[0.49681,0.11196,0.0095],"force_p95":0.62205,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.78965,"mean_force":0.53896,"phase_index":3.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.49337,0.16479,0.13688]},{"body_a":"attachment","body_b":"peg","contact_count":5.0,"contact_point_centroid":[0.49548,0.12979,0.05896],"force_p95":0.48321,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.52476,"mean_force":0.34293,"phase_index":3.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.4904,0.1418,0.03297]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1.0,"contact_point_centroid":[0.502,0.09553,0.00999],"force_p95":0.43956,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.43956,"mean_force":0.43956,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.49082,0.14163,0.03317]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.49487,0.12973,0.04885],"force_p95":0.0,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.49082,0.14163,0.03317]}],"total_contact_groups":8},"final_pose_error":0.04995,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49718,0.11273,0.03386],"final_tcp_position":[0.49827,0.18995,0.25111],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48616,0.11898,0.04]},"peak_contact_force":3.16116,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":737.0,"n_steps_budget":1000.0,"object_pos_end":[0.49605,0.11901,0.03387],"object_pos_start":[0.48616,0.11898,0.04],"object_to_goal_dist_end":0.19914,"object_to_goal_dist_start":0.19946,"object_z_max":0.04,"peak_contact_force":0.49484,"phase_name":"approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":736.0,"raw_peak_contact_force":2.24822,"subtask_id":"approach","tcp_end":[0.48357,0.16964,0.06936],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.06308,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49734,0.11226,0.03541],"object_pos_start":[0.49605,0.11901,0.03387],"object_to_goal_dist_end":0.19233,"object_to_goal_dist_start":0.19914,"object_z_max":0.03551,"peak_contact_force":2.33784,"phase_name":"contact","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1305.0,"raw_peak_contact_force":3.16116,"subtask_id":"contact","tcp_end":[0.49082,0.14163,0.03317],"tcp_start":[0.48357,0.16964,0.06936],"tcp_to_object_dist_end":0.03017,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1.0,"n_steps_budget":810.0,"object_pos_end":[0.49734,0.11225,0.0354],"object_pos_start":[0.49734,0.11226,0.03541],"object_to_goal_dist_end":0.19232,"object_to_goal_dist_start":0.19233,"object_z_max":0.03541,"peak_contact_force":0.0254,"phase_name":"push","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2.0,"raw_peak_contact_force":0.43956,"subtask_id":"push","tcp_end":[0.49093,0.14195,0.03307],"tcp_start":[0.49082,0.14163,0.03317],"tcp_to_object_dist_end":0.03048,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":256.0,"n_steps_budget":1000.0,"object_pos_end":[0.49718,0.11273,0.03386],"object_pos_start":[0.49734,0.11225,0.0354],"object_to_goal_dist_end":0.19285,"object_to_goal_dist_start":0.19232,"object_z_max":0.0354,"peak_contact_force":0.52932,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":261.0,"raw_peak_contact_force":0.78965,"tcp_end":[0.49827,0.18995,0.25111],"tcp_start":[0.49093,0.14195,0.03307],"tcp_to_object_dist_end":0.23057,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.85,"average_solve_count":60.0,"average_success_count":60.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach.lateral_offset_y":-0.00995,"approach.speed":0.10616,"contact.contact_force":18.49435,"contact.speed":0.03223,"push.push_distance":0.10133,"push.push_force_threshold":20.41487,"retract.speed":0.02734},"optimized_scores":{"best_composite_score":0.05082,"best_fitness_score":0.12749,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_left_wall","contact_count":1.0,"contact_point_centroid":[0.53255,0.1127,0.05991],"force_p95":567.04789,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":567.04789,"mean_force":567.04789,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.52068,0.11323,0.06152]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":1.0,"contact_point_centroid":[0.53263,0.11279,0.05998],"force_p95":52.72597,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":52.72597,"mean_force":52.72597,"phase_index":1.0,"phase_name":"contact","phase_type":"contact","tcp_position_centroid":[0.52076,0.11333,0.06165]},{"body_a":"peg","body_b":"channel_base_body","contact_count":747.0,"contact_point_centroid":[0.50579,0.06302,0.00936],"force_p95":0.55672,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.88411,"mean_force":0.56468,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.51171,0.15679,0.17851]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":34.0,"contact_point_centroid":[0.53102,0.06295,0.03156],"force_p95":1.1362,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.98455,"mean_force":0.48262,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.49989,0.19846,0.29607]},{"body_a":"peg","body_b":"channel_base_body","contact_count":36.0,"contact_point_centroid":[0.5064,0.06151,0.00938],"force_p95":0.55242,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55396,"mean_force":0.54655,"phase_index":1.0,"phase_name":"contact","phase_type":"contact","tcp_position_centroid":[0.52253,0.11511,0.06446]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1.0,"contact_point_centroid":[0.48861,0.06766,0.00939],"force_p95":0.54415,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54415,"mean_force":0.54415,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.52068,0.11323,0.06152]}],"total_contact_groups":6},"final_pose_error":0.15474,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50595,0.06302,0.03381],"final_tcp_position":[0.52068,0.1132,0.06148],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.52962,0.06295,0.04]},"peak_contact_force":567.04789,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":775.0,"n_steps_budget":1000.0,"object_pos_end":[0.50603,0.063,0.0338],"object_pos_start":[0.52962,0.06295,0.04],"object_to_goal_dist_end":0.14326,"object_to_goal_dist_start":0.14598,"object_z_max":0.04001,"peak_contact_force":0.54779,"phase_name":"approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":781.0,"raw_peak_contact_force":3.88411,"subtask_id":"approach","tcp_end":[0.52437,0.11674,0.0674],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.06598,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":36.0,"n_steps_budget":990.0,"object_pos_end":[0.50594,0.063,0.03381],"object_pos_start":[0.50603,0.063,0.0338],"object_to_goal_dist_end":0.14326,"object_to_goal_dist_start":0.14326,"object_z_max":0.03381,"peak_contact_force":52.72597,"phase_name":"contact","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":37.0,"raw_peak_contact_force":52.72597,"subtask_id":"contact","tcp_end":[0.52068,0.11323,0.06152],"tcp_start":[0.52437,0.11674,0.0674],"tcp_to_object_dist_end":0.05924,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1.0,"n_steps_budget":960.0,"object_pos_end":[0.50595,0.06302,0.03381],"object_pos_start":[0.50594,0.063,0.03381],"object_to_goal_dist_end":0.14328,"object_to_goal_dist_start":0.14326,"object_z_max":0.03381,"peak_contact_force":567.04789,"phase_name":"push","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2.0,"raw_peak_contact_force":567.04789,"subtask_id":"push","tcp_end":[0.52068,0.1132,0.06148],"tcp_start":[0.52068,0.11323,0.06152],"tcp_to_object_dist_end":0.05916,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```