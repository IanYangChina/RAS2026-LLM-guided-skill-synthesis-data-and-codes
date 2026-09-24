## Search State

- **Seed**: 7
- **Iteration**: 8 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 7 | approach → contact → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 7 | -0.0912 | 0.05 | ❌ rejected |
| 6 | approach → contact → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 7 | -0.0089 | 0.00 | ❌ rejected |
| 5 | approach → contact → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | admittance_control | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 8 | -0.1835 | 0.03 | ❌ rejected |
| 4 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 7 | 0.1032 | 0.33 | ❌ rejected |
| 3 | approach → contact → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | force_exceeded | pose_tolerance | 7 | -0.1366 | 0.02 | ❌ rejected |

**Proposal policy**: task_score is 0.05 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=-0.091) — your mutation base

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

- **Composite score**: -0.091
- **task_score** (E): 0.051
- **fitness_score**: 0.152  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.167
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.410

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach | 1.00 | 1.00 | 0.2070 |
| contact | 1.00 | 1.00 | 0.0726 |
| push | 0.00 | 1.00 | 0.0030 |
| retract | 1.00 | 1.00 | 0.0632 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.505, 0.161, 0.099) | (0.509, 0.098, 0.040)→(0.502, 0.098, 0.034) | 0.179→0.178 | 1.00 / 1.000 | 0.547 | 2.732 |
| contact | contact | 1.00 / force_exceeded | (0.505, 0.161, 0.099)→(0.499, 0.118, 0.041) | (0.502, 0.098, 0.034)→(0.503, 0.088, 0.035) | 0.178→0.169 | 1.00 / 2.000 | 33.183 | 33.983 |
| push | push | 0.00 / guard_failure | (0.499, 0.118, 0.041)→(0.498, 0.120, 0.040) | (0.503, 0.088, 0.035)→(0.503, 0.088, 0.035) | 0.169→0.169 | 1.00 / 1.667 | 251.967 | 323.458 |
| retract | retract | 1.00 / step_budget | (0.498, 0.120, 0.040)→(0.499, 0.175, 0.071) | (0.503, 0.088, 0.035)→(0.503, 0.089, 0.034) | 0.169→0.169 | 1.00 / 1.000 | 0.550 | 220.661 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.103
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.103
- phase_score: 0.221
- phase_breakdown.push_score: 0.016
- phase_breakdown.contact_score: 0.777
- phase_breakdown.approach_score: 0.282

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.174
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.103
- **Median Q (composite search score)**: -0.043
- **K-run variance**: 0.0123
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.348


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.76744,"average_solve_count":86.0,"average_success_count":86.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach.speed":0.07173,"contact.force_threshold":3.85067,"contact.speed":0.02615,"push.max_time":9.95972,"push.push_distance":0.13613,"push.push_speed":0.04578,"retract.speed":0.09962},"optimized_scores":{"best_composite_score":0.01403,"best_fitness_score":0.17403,"best_task_score":0.10293},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.54615,0.11999,0.05989],"force_p95":317.14349,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":317.14349,"mean_force":317.14349,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.49991,0.12598,0.03507]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":7.0,"contact_point_centroid":[0.54607,0.11999,0.05987],"force_p95":250.97054,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":317.10364,"mean_force":91.86957,"phase_index":3.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.49991,0.12576,0.03501]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.54616,0.12,0.05994],"force_p95":55.24733,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":55.24733,"mean_force":55.24733,"phase_index":1.0,"phase_name":"contact","phase_type":"contact","tcp_position_centroid":[0.49991,0.12605,0.03516]},{"body_a":"peg","body_b":"channel_base_body","contact_count":504.0,"contact_point_centroid":[0.50416,0.10354,0.00958],"force_p95":8.99927,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":10.83169,"mean_force":2.32461,"phase_index":1.0,"phase_name":"contact","phase_type":"contact","tcp_position_centroid":[0.50137,0.14916,0.06454]},{"body_a":"attachment","body_b":"peg","contact_count":144.0,"contact_point_centroid":[0.5026,0.12173,0.04643],"force_p95":9.50963,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":10.52139,"mean_force":6.4233,"phase_index":1.0,"phase_name":"contact","phase_type":"contact","tcp_position_centroid":[0.50032,0.13359,0.04458]},{"body_a":"peg","body_b":"channel_base_body","contact_count":349.0,"contact_point_centroid":[0.50355,0.11176,0.00935],"force_p95":0.63578,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06328,"mean_force":0.56661,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.50254,0.18619,0.19487]},{"body_a":"peg","body_b":"channel_base_body","contact_count":207.0,"contact_point_centroid":[0.50546,0.09519,0.00943],"force_p95":0.5985,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.65605,"mean_force":0.55048,"phase_index":3.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.49961,0.15371,0.05166]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1.0,"contact_point_centroid":[0.52325,0.09895,0.00991],"force_p95":0.55802,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55802,"mean_force":0.55802,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.49991,0.12598,0.03507]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":16.0,"contact_point_centroid":[0.52601,0.11178,0.02875],"force_p95":0.50724,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54079,"mean_force":0.34334,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.49991,0.19949,0.29805]}],"total_contact_groups":9},"final_pose_error":0.01989,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50561,0.09531,0.03391],"final_tcp_position":[0.50121,0.18248,0.07086],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.51001,0.11178,0.04]},"peak_contact_force":317.14349,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":371.0,"n_steps_budget":960.0,"object_pos_end":[0.50372,0.11172,0.034],"object_pos_start":[0.51001,0.11178,0.04],"object_to_goal_dist_end":0.19186,"object_to_goal_dist_start":0.19204,"object_z_max":0.04,"peak_contact_force":0.53635,"phase_name":"approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":365.0,"raw_peak_contact_force":2.06328,"subtask_id":"approach","tcp_end":[0.50595,0.17388,0.09921],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.09011,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":523.0,"n_steps_budget":990.0,"object_pos_end":[0.5057,0.09595,0.03497],"object_pos_start":[0.50372,0.11172,0.034],"object_to_goal_dist_end":0.17612,"object_to_goal_dist_start":0.19186,"object_z_max":0.03627,"peak_contact_force":55.24733,"phase_name":"contact","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":649.0,"raw_peak_contact_force":55.24733,"subtask_id":"contact","tcp_end":[0.49991,0.12598,0.03507],"tcp_start":[0.50595,0.17388,0.09921],"tcp_to_object_dist_end":0.03058,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.5057,0.09581,0.0349],"object_pos_start":[0.5057,0.09595,0.03497],"object_to_goal_dist_end":0.17598,"object_to_goal_dist_start":0.17612,"object_z_max":0.03497,"peak_contact_force":317.14349,"phase_name":"push","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2.0,"raw_peak_contact_force":317.14349,"subtask_id":"push","tcp_end":[0.49992,0.12595,0.03499],"tcp_start":[0.49991,0.12598,0.03507],"tcp_to_object_dist_end":0.03069,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":207.0,"n_steps_budget":600.0,"object_pos_end":[0.50561,0.09531,0.03391],"object_pos_start":[0.5057,0.09581,0.0349],"object_to_goal_dist_end":0.1755,"object_to_goal_dist_start":0.17598,"object_z_max":0.0349,"peak_contact_force":0.54447,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":214.0,"raw_peak_contact_force":317.10364,"tcp_end":[0.50121,0.18248,0.07086],"tcp_start":[0.49992,0.12595,0.03499],"tcp_to_object_dist_end":0.09478,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.10738,"average_solve_count":149.0,"average_success_count":149.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach.speed":0.05019,"contact.force_threshold":11.24512,"contact.speed":0.01268,"push.max_time":8.62357,"push.push_distance":0.10932,"push.push_speed":0.0283,"retract.speed":0.02158},"optimized_scores":{"best_composite_score":-0.24422,"best_fitness_score":0.16578,"best_task_score":0.05},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.53806,0.12,0.05982],"force_p95":438.75871,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":438.75871,"mean_force":438.75871,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.48672,0.14161,0.03554]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":19.0,"contact_point_centroid":[0.53764,0.11999,0.05929],"force_p95":303.1705,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":344.17156,"mean_force":125.08021,"phase_index":3.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.48502,0.14422,0.03484]},{"body_a":"peg","body_b":"channel_base_body","contact_count":999.0,"contact_point_centroid":[0.49803,0.10833,0.00969],"force_p95":3.76449,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":5.18795,"mean_force":1.53542,"phase_index":1.0,"phase_name":"contact","phase_type":"contact","tcp_position_centroid":[0.48703,0.15209,0.05976]},{"body_a":"attachment","body_b":"peg","contact_count":421.0,"contact_point_centroid":[0.49408,0.1297,0.05123],"force_p95":3.83308,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":4.86725,"mean_force":2.54641,"phase_index":1.0,"phase_name":"contact","phase_type":"contact","tcp_position_centroid":[0.48918,0.14138,0.04578]},{"body_a":"peg","body_b":"channel_base_body","contact_count":355.0,"contact_point_centroid":[0.49635,0.11906,0.00941],"force_p95":0.62248,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.24822,"mean_force":0.56211,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.49155,0.18937,0.19439]},{"body_a":"peg","body_b":"channel_base_body","contact_count":216.0,"contact_point_centroid":[0.49781,0.10807,0.00945],"force_p95":0.67207,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.90107,"mean_force":0.54758,"phase_index":3.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.48812,0.16804,0.05176]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":24.0,"contact_point_centroid":[0.47288,0.11898,0.03087],"force_p95":0.72905,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.86893,"mean_force":0.3628,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.4995,0.19935,0.29638]},{"body_a":"peg","body_b":"channel_base_body","contact_count":8.0,"contact_point_centroid":[0.50084,0.09014,0.00997],"force_p95":0.45042,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.45332,"mean_force":0.43242,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.48886,0.13824,0.03736]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.49569,0.12409,0.046],"force_p95":0.0,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.49036,0.13585,0.03856]}],"total_contact_groups":9},"final_pose_error":0.01999,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49783,0.10781,0.03383],"final_tcp_position":[0.49237,0.19423,0.07121],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48616,0.11898,0.04]},"peak_contact_force":438.75871,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":380.0,"n_steps_budget":1000.0,"object_pos_end":[0.49607,0.11906,0.03381],"object_pos_start":[0.48616,0.11898,0.04],"object_to_goal_dist_end":0.1992,"object_to_goal_dist_start":0.19946,"object_z_max":0.04,"peak_contact_force":0.5576,"phase_name":"approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":379.0,"raw_peak_contact_force":2.24822,"subtask_id":"approach","tcp_end":[0.48477,0.18022,0.09941],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.0904,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49802,0.10674,0.03577],"object_pos_start":[0.49607,0.11906,0.03381],"object_to_goal_dist_end":0.1868,"object_to_goal_dist_start":0.1992,"object_z_max":0.03622,"peak_contact_force":2.78963,"phase_name":"contact","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1420.0,"raw_peak_contact_force":5.18795,"subtask_id":"contact","tcp_end":[0.49036,0.13585,0.03856],"tcp_start":[0.48477,0.18022,0.09941],"tcp_to_object_dist_end":0.03023,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":8.0,"n_steps_budget":1000.0,"object_pos_end":[0.49793,0.10707,0.03549],"object_pos_start":[0.49802,0.10674,0.03577],"object_to_goal_dist_end":0.18714,"object_to_goal_dist_start":0.1868,"object_z_max":0.03577,"peak_contact_force":438.75871,"phase_name":"push","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":10.0,"raw_peak_contact_force":438.75871,"subtask_id":"push","tcp_end":[0.48613,0.14234,0.035],"tcp_start":[0.49036,0.13585,0.03856],"tcp_to_object_dist_end":0.03719,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":216.0,"n_steps_budget":1000.0,"object_pos_end":[0.49783,0.10781,0.03383],"object_pos_start":[0.49793,0.10707,0.03549],"object_to_goal_dist_end":0.18793,"object_to_goal_dist_start":0.18714,"object_z_max":0.03549,"peak_contact_force":0.56573,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":235.0,"raw_peak_contact_force":344.17156,"tcp_end":[0.49237,0.19423,0.07121],"tcp_start":[0.48613,0.14234,0.035],"tcp_to_object_dist_end":0.09432,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.67606,"average_solve_count":213.0,"average_success_count":213.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach.speed":0.02319,"contact.force_threshold":8.15263,"contact.speed":0.00597,"push.max_time":4.10117,"push.push_distance":0.1929,"push.push_speed":0.03767,"retract.speed":0.08289},"optimized_scores":{"best_composite_score":-0.04336,"best_fitness_score":0.11664,"best_task_score":0.00045},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_left_wall","contact_count":1.0,"contact_point_centroid":[0.52501,0.09218,0.06],"force_p95":214.47194,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":214.47194,"mean_force":214.47194,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.50795,0.09213,0.05072]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":1.0,"contact_point_centroid":[0.525,0.09227,0.06],"force_p95":41.51282,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":41.51282,"mean_force":41.51282,"phase_index":1.0,"phase_name":"contact","phase_type":"contact","tcp_position_centroid":[0.50798,0.09222,0.05082]},{"body_a":"peg","body_b":"channel_base_body","contact_count":382.0,"contact_point_centroid":[0.50585,0.06281,0.00938],"force_p95":0.55254,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.54593,"mean_force":0.5686,"phase_index":1.0,"phase_name":"contact","phase_type":"contact","tcp_position_centroid":[0.51429,0.11096,0.07206]},{"body_a":"attachment","body_b":"peg","contact_count":4.0,"contact_point_centroid":[0.50741,0.08089,0.05186],"force_p95":6.1788,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":7.05909,"mean_force":2.2123,"phase_index":1.0,"phase_name":"contact","phase_type":"contact","tcp_position_centroid":[0.50817,0.09283,0.0515]},{"body_a":"peg","body_b":"channel_base_body","contact_count":412.0,"contact_point_centroid":[0.5057,0.06293,0.00935],"force_p95":0.58095,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.88411,"mean_force":0.5794,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.51142,0.16353,0.19354]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":34.0,"contact_point_centroid":[0.53102,0.06295,0.03156],"force_p95":1.1362,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.98455,"mean_force":0.48262,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.50008,0.19827,0.29524]},{"body_a":"peg","body_b":"channel_base_body","contact_count":174.0,"contact_point_centroid":[0.50573,0.06274,0.00942],"force_p95":0.60472,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.70886,"mean_force":0.54168,"phase_index":3.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.50417,0.11888,0.05975]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1.0,"contact_point_centroid":[0.49604,0.04798,0.00932],"force_p95":0.49441,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.49441,"mean_force":0.49441,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.50795,0.09213,0.05072]},{"body_a":"attachment","body_b":"peg","contact_count":6.0,"contact_point_centroid":[0.50663,0.08021,0.05042],"force_p95":0.38728,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.44482,"mean_force":0.12456,"phase_index":3.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.50727,0.09211,0.05012]}],"total_contact_groups":9},"final_pose_error":0.01973,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50608,0.06276,0.03395],"final_tcp_position":[0.50261,0.14717,0.07203],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.52962,0.06295,0.04]},"peak_contact_force":214.47194,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":440.0,"n_steps_budget":1000.0,"object_pos_end":[0.50594,0.06297,0.03381],"object_pos_start":[0.52962,0.06295,0.04],"object_to_goal_dist_end":0.14323,"object_to_goal_dist_start":0.14598,"object_z_max":0.04001,"peak_contact_force":0.54788,"phase_name":"approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":446.0,"raw_peak_contact_force":3.88411,"subtask_id":"approach","tcp_end":[0.5234,0.13009,0.0973],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.09403,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":382.0,"n_steps_budget":1000.0,"object_pos_end":[0.50568,0.0625,0.03404],"object_pos_start":[0.50594,0.06297,0.03381],"object_to_goal_dist_end":0.14274,"object_to_goal_dist_start":0.14323,"object_z_max":0.03399,"peak_contact_force":41.51282,"phase_name":"contact","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":387.0,"raw_peak_contact_force":41.51282,"subtask_id":"contact","tcp_end":[0.50795,0.09213,0.05072],"tcp_start":[0.5234,0.13009,0.0973],"tcp_to_object_dist_end":0.03408,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.50565,0.0625,0.03409],"object_pos_start":[0.50568,0.0625,0.03404],"object_to_goal_dist_end":0.14273,"object_to_goal_dist_start":0.14274,"object_z_max":0.03404,"peak_contact_force":0.0,"phase_name":"push","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2.0,"raw_peak_contact_force":214.47194,"subtask_id":"push","tcp_end":[0.50778,0.09226,0.05057],"tcp_start":[0.50795,0.09213,0.05072],"tcp_to_object_dist_end":0.03409,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":174.0,"n_steps_budget":600.0,"object_pos_end":[0.50608,0.06276,0.03395],"object_pos_start":[0.50565,0.0625,0.03409],"object_to_goal_dist_end":0.14302,"object_to_goal_dist_start":0.14273,"object_z_max":0.03438,"peak_contact_force":0.54118,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":180.0,"raw_peak_contact_force":0.70886,"tcp_end":[0.50261,0.14717,0.07203],"tcp_start":[0.50778,0.09226,0.05057],"tcp_to_object_dist_end":0.09267,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```