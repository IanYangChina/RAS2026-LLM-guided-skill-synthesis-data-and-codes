## Search State

- **Seed**: 7
- **Iteration**: 7 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 6 | approach → contact → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 7 | -0.0089 | 0.00 | ❌ rejected |
| 5 | approach → contact → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | admittance_control | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 8 | -0.1835 | 0.03 | ❌ rejected |
| 4 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 7 | 0.1032 | 0.33 | ❌ rejected |
| 3 | approach → contact → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | force_exceeded | pose_tolerance | 7 | -0.1366 | 0.02 | ❌ rejected |
| 2 | align → approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | force_threshold_switch | admittance_control | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 6 | 0.3441 | 0.62 | ❌ rejected |

**Proposal policy**: task_score is 0.00 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=-0.009) — your mutation base

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

- **Composite score**: -0.009
- **task_score** (E): 0.000
- **fitness_score**: 0.151  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.250
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.410

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach | 1.00 | 1.00 | 0.2491 |
| contact | 1.00 | 1.00 | 0.0208 |
| push | 0.00 | 1.00 | 0.0007 |
| retract | 1.00 | 1.00 | 0.1010 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.505, 0.143, 0.059) | (0.509, 0.098, 0.040)→(0.502, 0.103, 0.033) | 0.179→0.184 | 1.00 / 1.333 | 146.512 | 194.781 |
| contact | contact | 1.00 / force_exceeded | (0.505, 0.143, 0.059)→(0.515, 0.135, 0.043) | (0.502, 0.103, 0.033)→(0.502, 0.104, 0.033) | 0.184→0.184 | 1.00 / 2.000 | 590.342 | 590.342 |
| push | push | 0.00 / guard_failure | (0.516, 0.134, 0.042)→(0.516, 0.134, 0.041) | (0.502, 0.104, 0.033)→(0.502, 0.104, 0.032) | 0.184→0.184 | 1.00 / 2.000 | 282.199 | 396.818 |
| retract | retract | 1.00 / step_budget | (0.516, 0.134, 0.041)→(0.513, 0.226, 0.082) | (0.502, 0.104, 0.032)→(0.503, 0.111, 0.027) | 0.184→0.192 | 1.00 / 1.000 | 0.552 | 272.300 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.000
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.000
- phase_score: 0.267
- phase_breakdown.push_score: 0.009
- phase_breakdown.contact_score: 0.629
- phase_breakdown.approach_score: 0.677

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.160
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.001
- **Median Q (composite search score)**: -0.011
- **K-run variance**: 0.0000
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.386


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.85345,"average_solve_count":116.0,"average_success_count":116.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach.speed":0.03604,"contact.contact_force":8.73189,"contact.speed":0.02963,"push.max_time":5.40922,"push.push_distance":0.14386,"push.push_speed":0.02212,"retract.speed":0.03615},"optimized_scores":{"best_composite_score":-0.0106,"best_fitness_score":0.1494,"best_task_score":0.0006},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.555,0.11989,0.05969],"force_p95":892.99131,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":892.99131,"mean_force":892.99131,"phase_index":1.0,"phase_name":"contact","phase_type":"contact","tcp_position_centroid":[0.52933,0.13637,0.01694]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":3.0,"contact_point_centroid":[0.55498,0.11943,0.05859],"force_p95":765.83376,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":782.11164,"mean_force":643.35405,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.52942,0.13579,0.01378]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":27.0,"contact_point_centroid":[0.55499,0.11958,0.05907],"force_p95":387.77619,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":459.44112,"mean_force":109.54185,"phase_index":3.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.52911,0.13853,0.01158]},{"body_a":"peg","body_b":"channel_base_body","contact_count":829.0,"contact_point_centroid":[0.50349,0.11191,0.00941],"force_p95":0.60576,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.26049,"mean_force":0.55167,"phase_index":3.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.52593,0.1845,0.03168]},{"body_a":"peg","body_b":"link7","contact_count":5.0,"contact_point_centroid":[0.51355,0.12682,0.0588],"force_p95":2.52434,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":2.58146,"mean_force":1.36153,"phase_index":3.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.52952,0.13569,0.01078]},{"body_a":"peg","body_b":"channel_base_body","contact_count":452.0,"contact_point_centroid":[0.50351,0.11164,0.00937],"force_p95":0.62608,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06328,"mean_force":0.5617,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.5024,0.17668,0.17493]},{"body_a":"peg","body_b":"channel_base_body","contact_count":25.0,"contact_point_centroid":[0.50351,0.11231,0.00939],"force_p95":0.59088,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.59429,"mean_force":0.54485,"phase_index":1.0,"phase_name":"contact","phase_type":"contact","tcp_position_centroid":[0.52018,0.1444,0.04198]},{"body_a":"peg","body_b":"channel_base_body","contact_count":3.0,"contact_point_centroid":[0.5208,0.10914,0.00939],"force_p95":0.58312,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.58609,"mean_force":0.5568,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.52942,0.13579,0.01378]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":16.0,"contact_point_centroid":[0.52601,0.11178,0.02875],"force_p95":0.50724,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54079,"mean_force":0.34334,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.49992,0.19943,0.29856]}],"total_contact_groups":9},"final_pose_error":0.01108,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50373,0.11167,0.03383],"final_tcp_position":[0.5258,0.22907,0.05344],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.51001,0.11178,0.04]},"peak_contact_force":892.99131,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":474.0,"n_steps_budget":1000.0,"object_pos_end":[0.50376,0.11174,0.0338],"object_pos_start":[0.51001,0.11178,0.04],"object_to_goal_dist_end":0.19188,"object_to_goal_dist_start":0.19204,"object_z_max":0.04,"peak_contact_force":0.55408,"phase_name":"approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":468.0,"raw_peak_contact_force":2.06328,"subtask_id":"approach","tcp_end":[0.50592,0.15519,0.05881],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.05018,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":25.0,"n_steps_budget":600.0,"object_pos_end":[0.50375,0.11175,0.0338],"object_pos_start":[0.50376,0.11174,0.0338],"object_to_goal_dist_end":0.19188,"object_to_goal_dist_start":0.19188,"object_z_max":0.0338,"peak_contact_force":892.99131,"phase_name":"contact","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":26.0,"raw_peak_contact_force":892.99131,"subtask_id":"contact","tcp_end":[0.52934,0.13607,0.0151],"tcp_start":[0.50592,0.15519,0.05881],"tcp_to_object_dist_end":0.03996,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.50376,0.11175,0.0338],"object_pos_start":[0.50375,0.11175,0.0338],"object_to_goal_dist_end":0.19189,"object_to_goal_dist_start":0.19188,"object_z_max":0.0338,"peak_contact_force":528.61763,"phase_name":"push","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":6.0,"raw_peak_contact_force":782.11164,"subtask_id":"push","tcp_end":[0.52959,0.13531,0.01177],"tcp_start":[0.5295,0.13551,0.01258],"tcp_to_object_dist_end":0.04132,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":829.0,"n_steps_budget":960.0,"object_pos_end":[0.50373,0.11167,0.03383],"object_pos_start":[0.50374,0.11177,0.0338],"object_to_goal_dist_end":0.19181,"object_to_goal_dist_start":0.19191,"object_z_max":0.03458,"peak_contact_force":0.54143,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":861.0,"raw_peak_contact_force":459.44112,"tcp_end":[0.5258,0.22907,0.05344],"tcp_start":[0.52959,0.13531,0.01177],"tcp_to_object_dist_end":0.12105,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.5,"average_solve_count":112.0,"average_success_count":112.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach.speed":0.03223,"contact.contact_force":8.69258,"contact.speed":0.02384,"push.max_time":4.6187,"push.push_distance":0.17423,"push.push_speed":0.02883,"retract.speed":0.0814},"optimized_scores":{"best_composite_score":-9e-05,"best_fitness_score":0.15991,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.4901,0.14666,0.0552],"force_p95":244.2877,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":244.2877,"mean_force":244.2877,"phase_index":1.0,"phase_name":"contact","phase_type":"contact","tcp_position_centroid":[0.48827,0.15827,0.055]},{"body_a":"peg","body_b":"world","contact_count":6.0,"contact_point_centroid":[0.49589,0.13352,-0.00026],"force_p95":181.47092,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":241.77457,"mean_force":40.71705,"phase_index":1.0,"phase_name":"contact","phase_type":"contact","tcp_position_centroid":[0.48586,0.16033,0.05732]},{"body_a":"peg","body_b":"world","contact_count":513.0,"contact_point_centroid":[0.49678,0.15097,-0.00147],"force_p95":3.50731,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":136.12994,"mean_force":2.74404,"phase_index":3.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.49017,0.20177,0.0703]},{"body_a":"attachment","body_b":"peg","contact_count":30.0,"contact_point_centroid":[0.49483,0.14705,0.05142],"force_p95":96.17035,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":135.99514,"mean_force":43.42837,"phase_index":3.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.49283,0.15727,0.04966]},{"body_a":"attachment","body_b":"peg","contact_count":3.0,"contact_point_centroid":[0.49294,0.14553,0.05446],"force_p95":124.81085,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":125.8977,"mean_force":114.21861,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.49132,0.15623,0.0531]},{"body_a":"peg","body_b":"world","contact_count":3.0,"contact_point_centroid":[0.49644,0.1333,-0.00037],"force_p95":124.80637,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":125.85364,"mean_force":114.51403,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.49132,0.15623,0.0531]},{"body_a":"peg","body_b":"channel_base_body","contact_count":49.0,"contact_point_centroid":[0.4912,0.11993,0.00992],"force_p95":32.95416,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":35.54194,"mean_force":4.63655,"phase_index":3.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.49111,0.16412,0.05135]},{"body_a":"peg","body_b":"channel_base_body","contact_count":449.0,"contact_point_centroid":[0.4961,0.11944,0.00943],"force_p95":0.60526,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.24822,"mean_force":0.54526,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.49138,0.17995,0.17477]},{"body_a":"peg","body_b":"world","contact_count":7.0,"contact_point_centroid":[0.49597,0.13378,-0.00021],"force_p95":1.00831,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.04134,"mean_force":0.7878,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.4845,0.16204,0.06129]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":24.0,"contact_point_centroid":[0.47288,0.11898,0.03087],"force_p95":0.72905,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.86893,"mean_force":0.3628,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.49962,0.19921,0.29688]}],"total_contact_groups":10},"final_pose_error":0.01301,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.4995,0.1583,0.01415],"final_tcp_position":[0.49016,0.24636,0.09249],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48616,0.11898,0.04]},"peak_contact_force":244.2877,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":475.0,"n_steps_budget":1000.0,"object_pos_end":[0.49591,0.1354,0.03017],"object_pos_start":[0.48616,0.11898,0.04],"object_to_goal_dist_end":0.21566,"object_to_goal_dist_start":0.19946,"object_z_max":0.04,"peak_contact_force":0.59819,"phase_name":"approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":480.0,"raw_peak_contact_force":2.24822,"subtask_id":"approach","tcp_end":[0.48436,0.16171,0.05926],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.04089,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":6.0,"n_steps_budget":600.0,"object_pos_end":[0.49616,0.13758,0.02994],"object_pos_start":[0.49591,0.1354,0.03017],"object_to_goal_dist_end":0.21785,"object_to_goal_dist_start":0.21566,"object_z_max":0.03017,"peak_contact_force":244.2877,"phase_name":"contact","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":7.0,"raw_peak_contact_force":244.2877,"subtask_id":"contact","tcp_end":[0.48997,0.15708,0.05397],"tcp_start":[0.48436,0.16171,0.05926],"tcp_to_object_dist_end":0.03156,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.49648,0.13764,0.02975],"object_pos_start":[0.49616,0.13758,0.02994],"object_to_goal_dist_end":0.2179,"object_to_goal_dist_start":0.21785,"object_z_max":0.02994,"peak_contact_force":102.30751,"phase_name":"push","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":6.0,"raw_peak_contact_force":125.8977,"subtask_id":"push","tcp_end":[0.49348,0.15506,0.05157],"tcp_start":[0.49258,0.15547,0.05227],"tcp_to_object_dist_end":0.02808,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":521.0,"n_steps_budget":600.0,"object_pos_end":[0.4995,0.1583,0.01415],"object_pos_start":[0.49696,0.13774,0.02937],"object_to_goal_dist_end":0.2397,"object_to_goal_dist_start":0.21802,"object_z_max":0.03054,"peak_contact_force":0.56844,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":592.0,"raw_peak_contact_force":136.12994,"tcp_end":[0.49016,0.24636,0.09249],"tcp_start":[0.49348,0.15506,0.05157],"tcp_to_object_dist_end":0.11823,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.35849,"average_solve_count":53.0,"average_success_count":53.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach.speed":0.09983,"contact.contact_force":10.84296,"contact.speed":0.02601,"push.max_time":7.351,"push.push_distance":0.13962,"push.push_speed":0.02044,"retract.speed":0.07597},"optimized_scores":{"best_composite_score":-0.01609,"best_fitness_score":0.14391,"best_task_score":3e-05},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_left_wall","contact_count":1.0,"contact_point_centroid":[0.53727,0.11068,0.05925],"force_p95":633.74648,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":633.74648,"mean_force":633.74648,"phase_index":1.0,"phase_name":"contact","phase_type":"contact","tcp_position_centroid":[0.52539,0.11132,0.06011]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":20.0,"contact_point_centroid":[0.53656,0.11081,0.05912],"force_p95":574.85434,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":580.0317,"mean_force":481.60205,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.52469,0.11153,0.05984]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":3.0,"contact_point_centroid":[0.53732,0.11072,0.05938],"force_p95":276.29826,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":282.44433,"mean_force":239.70041,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.52545,0.11133,0.06038]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":13.0,"contact_point_centroid":[0.5374,0.11133,0.05978],"force_p95":181.37543,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":221.3276,"mean_force":113.45654,"phase_index":3.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.52553,0.11197,0.06119]},{"body_a":"peg","body_b":"channel_base_body","contact_count":438.0,"contact_point_centroid":[0.50568,0.06305,0.00935],"force_p95":0.58028,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.88411,"mean_force":0.57744,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.51238,0.15179,0.16828]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":34.0,"contact_point_centroid":[0.53102,0.06295,0.03156],"force_p95":1.1362,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.98455,"mean_force":0.48262,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.50047,0.19738,0.29295]},{"body_a":"peg","body_b":"channel_base_body","contact_count":528.0,"contact_point_centroid":[0.50601,0.06305,0.00938],"force_p95":0.55147,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55501,"mean_force":0.54657,"phase_index":3.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.52232,0.157,0.0791]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1.0,"contact_point_centroid":[0.52264,0.05623,0.00938],"force_p95":0.54807,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54807,"mean_force":0.54807,"phase_index":1.0,"phase_name":"contact","phase_type":"contact","tcp_position_centroid":[0.52539,0.11132,0.06011]},{"body_a":"peg","body_b":"channel_base_body","contact_count":3.0,"contact_point_centroid":[0.5057,0.0473,0.00938],"force_p95":0.54737,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54743,"mean_force":0.54646,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.52545,0.11133,0.06038]}],"total_contact_groups":9},"final_pose_error":0.01296,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50598,0.06293,0.0338],"final_tcp_position":[0.52203,0.20315,0.10135],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.52962,0.06295,0.04]},"peak_contact_force":633.74648,"phases":[{"contact_detected":true,"contact_event_count":2.0,"n_steps":466.0,"n_steps_budget":870.0,"object_pos_end":[0.50603,0.06297,0.0338],"object_pos_start":[0.52962,0.06295,0.04],"object_to_goal_dist_end":0.14323,"object_to_goal_dist_start":0.14598,"object_z_max":0.04001,"peak_contact_force":438.38313,"phase_name":"approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":492.0,"raw_peak_contact_force":580.0317,"subtask_id":"approach","tcp_end":[0.52539,0.11132,0.06011],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.05835,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1.0,"n_steps_budget":600.0,"object_pos_end":[0.50601,0.06295,0.0338],"object_pos_start":[0.50603,0.06297,0.0338],"object_to_goal_dist_end":0.14321,"object_to_goal_dist_start":0.14323,"object_z_max":0.0338,"peak_contact_force":633.74648,"phase_name":"contact","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2.0,"raw_peak_contact_force":633.74648,"subtask_id":"contact","tcp_end":[0.52545,0.11128,0.06023],"tcp_start":[0.52539,0.11132,0.06011],"tcp_to_object_dist_end":0.05841,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.50598,0.06294,0.0338],"object_pos_start":[0.50601,0.06295,0.0338],"object_to_goal_dist_end":0.1432,"object_to_goal_dist_start":0.14321,"object_z_max":0.0338,"peak_contact_force":215.67326,"phase_name":"push","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":6.0,"raw_peak_contact_force":282.44433,"subtask_id":"push","tcp_end":[0.52549,0.11148,0.06065],"tcp_start":[0.52546,0.11139,0.06052],"tcp_to_object_dist_end":0.0588,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":528.0,"n_steps_budget":600.0,"object_pos_end":[0.50598,0.06293,0.0338],"object_pos_start":[0.50593,0.06297,0.0338],"object_to_goal_dist_end":0.14319,"object_to_goal_dist_start":0.14323,"object_z_max":0.03381,"peak_contact_force":0.54514,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":541.0,"raw_peak_contact_force":221.3276,"tcp_end":[0.52203,0.20315,0.10135],"tcp_start":[0.52549,0.11148,0.06065],"tcp_to_object_dist_end":0.15646,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```