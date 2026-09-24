## Search State

- **Seed**: 1
- **Iteration**: 11 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 10 | align → approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 8 | 0.0830 | 0.47 | ❌ rejected |
| 9 | approach → contact → push → retract | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 9 | -0.1047 | 0.00 | ❌ rejected |
| 8 | align → approach → contact → push → retract | linear_cartesian | arc_cartesian | impedance_motion | linear_cartesian | arc_cartesian | position_control | force_threshold_switch | admittance_control | impedance_control | position_control | pose_tolerance | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 6 | 0.2220 | 0.61 | ❌ rejected |
| 7 | align → approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 7 | -0.1074 | 0.01 | ❌ rejected |
| 6 | align → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 7 | -0.2720 | 0.00 | ❌ rejected |

**Proposal policy**: task_score is 0.47 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.083) — your mutation base

```yaml
skill: peg_channel
phases:
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
- id: approach_1
  type: approach
  generator: arc_cartesian
  control: force_threshold_switch
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
  control: admittance_control
  termination: contact_detected
  parameters:
    speed:
      type: scalar
      range:
      - 0.005
      - 0.05
- id: push_1
  type: push
  generator: linear_cartesian
  control: impedance_control
  termination: pose_tolerance
  parameters:
    push_distance:
      type: scalar
      range:
      - 0.02
      - 0.2
    push_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
- id: retract_1
  type: retract
  generator: arc_cartesian
  control: position_control
  termination: pose_tolerance

```

## Design Metrics

- **Composite score**: 0.083
- **task_score** (E): 0.469
- **fitness_score**: 0.506  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.067
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.490

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| align_1 | 1.00 | 1.00 | 0.2243 |
| approach_1 | 1.00 | 1.00 | 0.0440 |
| contact_1 | 0.67 | 1.00 | 0.0161 |
| push_1 | 0.33 | 1.00 | 0.0634 |
| retract_1 | 1.00 | 1.00 | 0.2984 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| align_1 | align | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.481, 0.133, 0.089) | (0.483, 0.080, 0.040)→(0.497, 0.080, 0.034) | 0.161→0.160 | 1.00 / 1.000 | 0.551 | 2.857 |
| approach_1 | approach | 1.00 / step_budget | (0.481, 0.133, 0.089)→(0.489, 0.123, 0.048) | (0.497, 0.080, 0.034)→(0.497, 0.080, 0.034) | 0.160→0.160 | 1.00 / 1.333 | 130.776 | 327.971 |
| contact_1 | contact | 0.67 / step_budget | (0.489, 0.123, 0.048)→(0.490, 0.110, 0.039) | (0.497, 0.080, 0.034)→(0.498, 0.074, 0.035) | 0.160→0.154 | 1.00 / 2.000 | 44.871 | 45.831 |
| push_1 | push | 0.33 / guard_failure | (0.491, 0.062, 0.041)→(0.491, -0.001, 0.042) | (0.498, 0.074, 0.035)→(0.503, -0.035, 0.035) | 0.154→0.052 | 1.00 / 2.667 | 34.829 | 49.389 |
| retract_1 | retract | 1.00 / step_budget | (0.491, -0.001, 0.042)→(0.497, 0.176, 0.278) | (0.503, -0.035, 0.035)→(0.500, -0.033, 0.034) | 0.052→0.052 | 1.00 / 1.000 | 0.557 | 35.316 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 1.000
- alignment_error: None
- force_efficiency: 0.616
- terminal_score: 0.997
- phase_score: 0.685
- phase_breakdown.push_score: 0.575
- phase_breakdown.approach_score: 0.901
- phase_breakdown.contact_score: 0.800

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.810
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.997
- **Median Q (composite search score)**: 0.079
- **K-run variance**: 0.0368
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.309


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.40467,"average_solve_count":257.0,"average_success_count":257.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.align_speed":0.09191,"approach_1.approach_speed":0.05798,"contact_1.contact_force_threshold":6.08033,"contact_1.contact_speed":0.01616,"push_1.guard_force_threshold":18.30928,"push_1.push_speed":0.09987,"push_1.push_tolerance":0.01572,"retract_1.retract_speed":0.04545},"optimized_scores":{"best_composite_score":0.3199,"best_fitness_score":0.8099,"best_task_score":0.99728},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg","contact_count":776.0,"contact_point_centroid":[0.50057,0.02847,0.04054],"force_p95":10.62251,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":19.19679,"mean_force":2.97102,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49451,0.0396,0.02996]},{"body_a":"peg","body_b":"channel_base_body","contact_count":3.0,"contact_point_centroid":[0.50714,-0.10008,0.05996],"force_p95":17.82218,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":17.9501,"mean_force":16.15634,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49579,-0.05294,0.03417]},{"body_a":"attachment","body_b":"peg","contact_count":8.0,"contact_point_centroid":[0.50238,-0.065,0.05595],"force_p95":11.43121,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":17.0434,"mean_force":2.81878,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.4955,-0.05346,0.03418]},{"body_a":"peg","body_b":"channel_base_body","contact_count":361.0,"contact_point_centroid":[0.50605,-0.10003,0.05544],"force_p95":0.31218,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":16.84595,"mean_force":0.11556,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49472,0.02892,0.15123]},{"body_a":"peg","body_b":"channel_base_body","contact_count":477.0,"contact_point_centroid":[0.50641,-0.00738,0.00993],"force_p95":10.3533,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":13.32749,"mean_force":4.59638,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49459,0.03666,0.03013]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":633.0,"contact_point_centroid":[0.52509,0.00295,0.02512],"force_p95":4.71386,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.31487,"mean_force":1.29163,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49455,0.0299,0.03028]},{"body_a":"peg","body_b":"channel_base_body","contact_count":629.0,"contact_point_centroid":[0.50264,0.10301,0.00973],"force_p95":2.29115,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.45278,"mean_force":1.32922,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49535,0.14486,0.03319]},{"body_a":"attachment","body_b":"peg","contact_count":378.0,"contact_point_centroid":[0.49949,0.12937,0.04457],"force_p95":1.99059,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":2.10431,"mean_force":1.50454,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.4958,0.14125,0.03147]},{"body_a":"peg","body_b":"channel_base_body","contact_count":635.0,"contact_point_centroid":[0.5009,0.11602,0.00938],"force_p95":0.61711,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.92055,"mean_force":0.55649,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.498,0.18298,0.1919]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":5.0,"contact_point_centroid":[0.52504,-0.08249,0.06],"force_p95":1.76054,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.7809,"mean_force":1.32579,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49566,-0.05344,0.03412]},{"body_a":"peg","body_b":"channel_base_body","contact_count":988.0,"contact_point_centroid":[0.50596,-0.08133,0.0094],"force_p95":0.59857,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.85197,"mean_force":0.54492,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49485,0.04182,0.16788]},{"body_a":"peg","body_b":"channel_base_body","contact_count":162.0,"contact_point_centroid":[0.5011,0.11595,0.00942],"force_p95":0.59345,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.61785,"mean_force":0.54225,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49632,0.1624,0.06587]}],"total_contact_groups":12},"final_pose_error":0.04203,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.506,-0.08196,0.03377],"final_tcp_position":[0.49766,0.16461,0.27745],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50095,0.11604,0.04]},"peak_contact_force":19.19679,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":651.0,"n_steps_budget":1000.0,"object_pos_end":[0.50091,0.11604,0.0338],"object_pos_start":[0.50095,0.11604,0.04],"object_to_goal_dist_end":0.19614,"object_to_goal_dist_start":0.19604,"object_z_max":0.04,"peak_contact_force":0.5562,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":635.0,"raw_peak_contact_force":1.92055,"tcp_end":[0.49763,0.16711,0.08908],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.07533,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":162.0,"n_steps_budget":630.0,"object_pos_end":[0.50093,0.11606,0.03391],"object_pos_start":[0.50091,0.11604,0.0338],"object_to_goal_dist_end":0.19616,"object_to_goal_dist_start":0.19614,"object_z_max":0.03393,"peak_contact_force":0.56496,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":162.0,"raw_peak_contact_force":0.61785,"subtask_id":"approach","tcp_end":[0.49658,0.15763,0.0424],"tcp_start":[0.49763,0.16711,0.08908],"tcp_to_object_dist_end":0.04265,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":639.0,"n_steps_budget":930.0,"object_pos_end":[0.50288,0.10723,0.03535],"object_pos_start":[0.50093,0.11606,0.03391],"object_to_goal_dist_end":0.18731,"object_to_goal_dist_start":0.19616,"object_z_max":0.03542,"peak_contact_force":1.56858,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1007.0,"raw_peak_contact_force":2.45278,"subtask_id":"contact","tcp_end":[0.4967,0.13677,0.02969],"tcp_start":[0.49658,0.15763,0.0424],"tcp_to_object_dist_end":0.03071,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50708,-0.08097,0.03608],"object_pos_start":[0.50288,0.10723,0.03535],"object_to_goal_dist_end":0.00815,"object_to_goal_dist_start":0.18731,"object_z_max":0.03647,"peak_contact_force":19.19679,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1889.0,"raw_peak_contact_force":19.19679,"subtask_id":"push","tcp_end":[0.49578,-0.05327,0.03417],"tcp_start":[0.4967,0.13677,0.02969],"tcp_to_object_dist_end":0.02998,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.506,-0.08196,0.03377],"object_pos_start":[0.50708,-0.08097,0.03608],"object_to_goal_dist_end":0.00887,"object_to_goal_dist_start":0.00815,"object_z_max":0.03608,"peak_contact_force":0.57911,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1362.0,"raw_peak_contact_force":17.0434,"tcp_end":[0.49766,0.16461,0.27745],"tcp_start":[0.49578,-0.05327,0.03417],"tcp_to_object_dist_end":0.34676,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.23377,"average_solve_count":308.0,"average_success_count":308.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.align_speed":0.02121,"approach_1.approach_speed":0.10066,"contact_1.contact_force_threshold":8.58987,"contact_1.contact_speed":0.03206,"push_1.guard_force_threshold":19.42761,"push_1.push_speed":0.08136,"push_1.push_tolerance":0.02164,"retract_1.retract_speed":0.06576},"optimized_scores":{"best_composite_score":0.07928,"best_fitness_score":0.56928,"best_task_score":0.4082},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_right_wall","contact_count":121.0,"contact_point_centroid":[0.47498,0.11091,0.05987],"force_p95":446.9296,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":485.84967,"mean_force":398.27107,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48523,0.1107,0.05804]},{"body_a":"attachment","body_b":"peg","contact_count":690.0,"contact_point_centroid":[0.49872,0.00274,0.04249],"force_p95":21.22843,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":50.82429,"mean_force":8.49123,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49093,0.01318,0.03019]},{"body_a":"peg","body_b":"channel_base_body","contact_count":32.0,"contact_point_centroid":[0.50723,-0.10033,0.06029],"force_p95":39.57597,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":45.81669,"mean_force":27.53626,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49463,-0.05446,0.0338]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":697.0,"contact_point_centroid":[0.52517,-0.01689,0.0366],"force_p95":14.51357,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":17.84835,"mean_force":4.89237,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49101,0.00884,0.03028]},{"body_a":"peg","body_b":"channel_base_body","contact_count":31.0,"contact_point_centroid":[0.50681,-0.10037,0.06033],"force_p95":8.16197,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":16.53672,"mean_force":2.95235,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49333,-0.05398,0.03629]},{"body_a":"peg","body_b":"channel_base_body","contact_count":496.0,"contact_point_centroid":[0.50673,-0.021,0.00993],"force_p95":13.57241,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":16.3233,"mean_force":6.6623,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49057,0.02026,0.02985]},{"body_a":"attachment","body_b":"peg","contact_count":30.0,"contact_point_centroid":[0.5,-0.06446,0.05347],"force_p95":6.61683,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":14.0164,"mean_force":2.68131,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49326,-0.05339,0.03747]},{"body_a":"peg","body_b":"link7","contact_count":108.0,"contact_point_centroid":[0.52079,0.04133,0.06272],"force_p95":9.06138,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":9.70436,"mean_force":5.57974,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48831,0.05607,0.02768]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":15.0,"contact_point_centroid":[0.5251,-0.08237,0.05348],"force_p95":4.73798,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.89255,"mean_force":1.91517,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49327,-0.05335,0.03745]},{"body_a":"peg","body_b":"channel_base_body","contact_count":419.0,"contact_point_centroid":[0.49609,0.05431,0.00963],"force_p95":3.20719,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.12358,"mean_force":1.42875,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.48871,0.09472,0.0337]},{"body_a":"attachment","body_b":"peg","contact_count":192.0,"contact_point_centroid":[0.49381,0.07776,0.04572],"force_p95":3.10171,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":3.80011,"mean_force":2.11214,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.48963,0.0896,0.03151]},{"body_a":"peg","body_b":"channel_base_body","contact_count":732.0,"contact_point_centroid":[0.49541,0.06384,0.00938],"force_p95":0.56511,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.44546,"mean_force":0.55718,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.48829,0.15773,0.18987]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":28.0,"contact_point_centroid":[0.47133,0.06388,0.03676],"force_p95":0.92436,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.16907,"mean_force":0.37063,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49937,0.19886,0.29756]},{"body_a":"peg","body_b":"channel_base_body","contact_count":975.0,"contact_point_centroid":[0.50174,-0.07743,0.00944],"force_p95":0.55159,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.63915,"mean_force":0.54124,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49408,0.04168,0.16948]},{"body_a":"peg","body_b":"channel_base_body","contact_count":284.0,"contact_point_centroid":[0.49514,0.06404,0.0094],"force_p95":0.55085,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55289,"mean_force":0.5453,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48377,0.11194,0.06294]}],"total_contact_groups":15},"final_pose_error":0.04317,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50127,-0.07678,0.03409],"final_tcp_position":[0.49747,0.16354,0.27702],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48093,0.06388,0.04]},"peak_contact_force":485.84967,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":759.0,"n_steps_budget":1000.0,"object_pos_end":[0.49519,0.0641,0.03398],"object_pos_start":[0.48093,0.06388,0.04],"object_to_goal_dist_end":0.14431,"object_to_goal_dist_start":0.14514,"object_z_max":0.04,"peak_contact_force":0.54792,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":760.0,"raw_peak_contact_force":2.44546,"tcp_end":[0.47881,0.11818,0.08853],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.07854,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":284.0,"n_steps_budget":600.0,"object_pos_end":[0.495,0.06414,0.03402],"object_pos_start":[0.49519,0.0641,0.03398],"object_to_goal_dist_end":0.14435,"object_to_goal_dist_start":0.14431,"object_z_max":0.03402,"peak_contact_force":0.55166,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":405.0,"raw_peak_contact_force":485.84967,"subtask_id":"approach","tcp_end":[0.48931,0.10662,0.04162],"tcp_start":[0.47881,0.11818,0.08853],"tcp_to_object_dist_end":0.04353,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":431.0,"n_steps_budget":600.0,"object_pos_end":[0.49758,0.05633,0.03543],"object_pos_start":[0.495,0.06414,0.03402],"object_to_goal_dist_end":0.13643,"object_to_goal_dist_start":0.14435,"object_z_max":0.03548,"peak_contact_force":2.12857,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":611.0,"raw_peak_contact_force":4.12358,"subtask_id":"contact","tcp_end":[0.49062,0.08574,0.03019],"tcp_start":[0.48931,0.10662,0.04162],"tcp_to_object_dist_end":0.03067,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":854.0,"n_steps_budget":1000.0,"object_pos_end":[0.50733,-0.08206,0.03623],"object_pos_start":[0.49758,0.05633,0.03543],"object_to_goal_dist_end":0.0085,"object_to_goal_dist_start":0.13643,"object_z_max":0.03727,"peak_contact_force":21.20841,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2023.0,"raw_peak_contact_force":50.82429,"subtask_id":"push","tcp_end":[0.49455,-0.05558,0.03367],"tcp_start":[0.49459,-0.05557,0.03372],"tcp_to_object_dist_end":0.02951,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50127,-0.07678,0.03409],"object_pos_start":[0.50731,-0.08215,0.03618],"object_to_goal_dist_end":0.00685,"object_to_goal_dist_start":0.00853,"object_z_max":0.0373,"peak_contact_force":0.54886,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1051.0,"raw_peak_contact_force":16.53672,"tcp_end":[0.49747,0.16354,0.27702],"tcp_start":[0.49455,-0.05558,0.03367],"tcp_to_object_dist_end":0.34174,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.72414,"average_solve_count":145.0,"average_success_count":145.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.align_speed":0.10494,"approach_1.approach_speed":0.10624,"contact_1.contact_force_threshold":7.79949,"contact_1.contact_speed":0.03613,"push_1.guard_force_threshold":29.11574,"push_1.push_speed":0.03598,"push_1.push_tolerance":0.01572,"retract_1.retract_speed":0.07849},"optimized_scores":{"best_composite_score":-0.15021,"best_fitness_score":0.13979,"best_task_score":0.00054},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_right_wall","contact_count":212.0,"contact_point_centroid":[0.47499,0.1125,0.05992],"force_p95":457.99993,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":497.44464,"mean_force":411.05581,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.47882,0.10607,0.05917]},{"body_a":"attachment","body_b":"channel_right_wall","contact_count":2.0,"contact_point_centroid":[0.475,0.11574,0.05999],"force_p95":126.10403,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":130.91673,"mean_force":82.78971,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.48187,0.10604,0.05859]},{"body_a":"attachment","body_b":"channel_right_wall","contact_count":7.0,"contact_point_centroid":[0.47499,0.11566,0.05995],"force_p95":73.92585,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":78.14503,"mean_force":59.17356,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.4819,0.106,0.05849]},{"body_a":"attachment","body_b":"channel_right_wall","contact_count":6.0,"contact_point_centroid":[0.47499,0.11569,0.05994],"force_p95":65.17645,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":72.36914,"mean_force":40.89359,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48187,0.10601,0.05848]},{"body_a":"peg","body_b":"channel_base_body","contact_count":669.0,"contact_point_centroid":[0.49427,0.059,0.00936],"force_p95":0.56052,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.20518,"mean_force":0.56806,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.48147,0.15501,0.18908]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":35.0,"contact_point_centroid":[0.46807,0.05895,0.03796],"force_p95":1.19991,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.42382,"mean_force":0.50385,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49897,0.19822,0.29591]},{"body_a":"peg","body_b":"channel_base_body","contact_count":782.0,"contact_point_centroid":[0.49406,0.05893,0.0094],"force_p95":0.55055,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55392,"mean_force":0.54535,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.4876,0.16711,0.16398]},{"body_a":"peg","body_b":"channel_base_body","contact_count":337.0,"contact_point_centroid":[0.49427,0.05871,0.00939],"force_p95":0.55007,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55382,"mean_force":0.54592,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.47542,0.10745,0.06463]},{"body_a":"peg","body_b":"channel_base_body","contact_count":7.0,"contact_point_centroid":[0.4852,0.07036,0.00939],"force_p95":0.54786,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54843,"mean_force":0.54549,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.4819,0.106,0.05849]},{"body_a":"peg","body_b":"channel_base_body","contact_count":3.0,"contact_point_centroid":[0.50778,0.06969,0.00939],"force_p95":0.54702,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54706,"mean_force":0.54663,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.48188,0.10605,0.0586]}],"total_contact_groups":10},"final_pose_error":0.01976,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.494,0.05869,0.03403],"final_tcp_position":[0.4971,0.19888,0.28049],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.46685,0.05894,0.04]},"peak_contact_force":497.44464,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":698.0,"n_steps_budget":1000.0,"object_pos_end":[0.49408,0.05882,0.03389],"object_pos_start":[0.46685,0.05894,0.04],"object_to_goal_dist_end":0.13908,"object_to_goal_dist_start":0.14284,"object_z_max":0.04001,"peak_contact_force":0.54867,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":704.0,"raw_peak_contact_force":4.20518,"tcp_end":[0.46562,0.11347,0.08853],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.08235,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":337.0,"n_steps_budget":600.0,"object_pos_end":[0.4943,0.05903,0.03393],"object_pos_start":[0.49408,0.05882,0.03389],"object_to_goal_dist_end":0.13927,"object_to_goal_dist_start":0.13908,"object_z_max":0.03393,"peak_contact_force":391.21208,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":549.0,"raw_peak_contact_force":497.44464,"subtask_id":"approach","tcp_end":[0.48184,0.10605,0.05861],"tcp_start":[0.46562,0.11347,0.08853],"tcp_to_object_dist_end":0.05455,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":3.0,"n_steps_budget":690.0,"object_pos_end":[0.49418,0.05915,0.03393],"object_pos_start":[0.4943,0.05903,0.03393],"object_to_goal_dist_end":0.1394,"object_to_goal_dist_start":0.13927,"object_z_max":0.03393,"peak_contact_force":130.91673,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":5.0,"raw_peak_contact_force":130.91673,"subtask_id":"contact","tcp_end":[0.48191,0.10603,0.05855],"tcp_start":[0.48184,0.10605,0.05861],"tcp_to_object_dist_end":0.05436,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":7.0,"n_steps_budget":1000.0,"object_pos_end":[0.49394,0.05901,0.03393],"object_pos_start":[0.49418,0.05915,0.03393],"object_to_goal_dist_end":0.13927,"object_to_goal_dist_start":0.1394,"object_z_max":0.03393,"peak_contact_force":64.08111,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":14.0,"raw_peak_contact_force":78.14503,"subtask_id":"push","tcp_end":[0.48188,0.10596,0.05843],"tcp_start":[0.48188,0.10596,0.05844],"tcp_to_object_dist_end":0.05431,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":782.0,"n_steps_budget":1000.0,"object_pos_end":[0.494,0.05869,0.03403],"object_pos_start":[0.49394,0.05889,0.03393],"object_to_goal_dist_end":0.13894,"object_to_goal_dist_start":0.13915,"object_z_max":0.03403,"peak_contact_force":0.54342,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":788.0,"raw_peak_contact_force":72.36914,"tcp_end":[0.4971,0.19888,0.28049],"tcp_start":[0.48188,0.10596,0.05843],"tcp_to_object_dist_end":0.28355,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```