## Search State

- **Seed**: 1
- **Iteration**: 9 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 8 | approach → contact → push → align | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 3 | 0.2037 | 0.12 | ❌ rejected |
| 7 | rotate → align → push → align | impedance_motion | linear_cartesian | impedance_motion | linear_cartesian | impedance_control | position_control | impedance_control | position_control | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 3 | 0.1659 | 0.40 | ❌ rejected |
| 6 | rotate → align → push → align | impedance_motion | linear_cartesian | impedance_motion | linear_cartesian | impedance_control | position_control | impedance_control | position_control | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 3 | 0.1659 | 0.40 | ❌ rejected |
| 5 | rotate → align → push → align | impedance_motion | linear_cartesian | impedance_motion | linear_cartesian | impedance_control | position_control | impedance_control | position_control | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 3 | 0.1208 | 0.32 | ❌ rejected |
| 4 | rotate → align → push → align | impedance_motion | linear_cartesian | impedance_motion | linear_cartesian | impedance_control | position_control | impedance_control | position_control | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 3 | 0.1680 | 0.40 | ❌ rejected |

**Proposal policy**: task_score is 0.12 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.204) — your mutation base

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

- **Composite score**: 0.204
- **task_score** (E): 0.123
- **fitness_score**: 0.164  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.250
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.210

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.2179 |
| contact_1 | 1.00 | 1.00 | 0.0361 |
| push_1 | 0.00 | 1.00 | 0.0001 |
| final_align | 0.00 | 1.00 | 0.0389 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.481, 0.123, 0.099) | (0.483, 0.080, 0.040)→(0.497, 0.080, 0.034) | 0.161→0.160 | 1.00 / 1.000 | 0.546 | 2.857 |
| contact_1 | contact | 1.00 / force_exceeded | (0.481, 0.123, 0.099)→(0.484, 0.111, 0.065) | (0.497, 0.080, 0.034)→(0.497, 0.079, 0.034) | 0.160→0.160 | 1.00 / 2.000 | 56.925 | 56.925 |
| push_1 | push | 0.00 / guard_failure | (0.484, 0.111, 0.065)→(0.484, 0.111, 0.065) | (0.497, 0.079, 0.034)→(0.497, 0.079, 0.034) | 0.160→0.160 | 1.00 / 2.000 | 61.195 | 101.327 |
| final_align | align | 0.00 / step_budget | (0.484, 0.111, 0.065)→(0.502, 0.089, 0.054) | (0.497, 0.079, 0.034)→(0.498, 0.060, 0.034) | 0.160→0.140 | 1.00 / 3.000 | 338.351 | 613.536 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.366
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.366
- phase_score: 0.214
- phase_breakdown.push_score: 0.012
- phase_breakdown.contact_score: 0.728
- phase_breakdown.approach_score: 0.305

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.274
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.366
- **Median Q (composite search score)**: 0.151
- **K-run variance**: 0.0061
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.3
- **Parameters at upper bound**: final_align.lateral_offset_x
- **Final σ (mean)**: 0.286


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.89,"average_solve_count":100.0,"average_success_count":100.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"contact_1.contact_force_threshold":5.26115,"final_align.lateral_offset_x":-0.00701,"push_1.push_distance":0.04522},"optimized_scores":{"best_composite_score":0.31436,"best_fitness_score":0.27436,"best_task_score":0.36552},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_right_wall","body_b":"link7","contact_count":534.0,"contact_point_centroid":[0.46564,0.11987,0.05892],"force_p95":430.93432,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":784.62578,"mean_force":280.67965,"phase_index":3.0,"phase_name":"final_align","phase_type":"align","tcp_position_centroid":[0.49978,0.08348,0.05246]},{"body_a":"world","body_b":"link7","contact_count":596.0,"contact_point_centroid":[0.49572,0.16668,-2e-05],"force_p95":269.48672,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":605.28537,"mean_force":161.9738,"phase_index":3.0,"phase_name":"final_align","phase_type":"align","tcp_position_centroid":[0.49814,0.10385,0.05301]},{"body_a":"world","body_b":"link7","contact_count":3.0,"contact_point_centroid":[0.49803,0.2044,-0.00017],"force_p95":98.32827,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":100.6414,"mean_force":76.93101,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49681,0.14234,0.05393]},{"body_a":"world","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.498,0.2045,-6e-05],"force_p95":91.59551,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":91.59551,"mean_force":91.59551,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49678,0.14243,0.05415]},{"body_a":"peg","body_b":"channel_base_body","contact_count":925.0,"contact_point_centroid":[0.50378,0.07056,0.00949],"force_p95":2.166,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":42.96989,"mean_force":1.02878,"phase_index":3.0,"phase_name":"final_align","phase_type":"align","tcp_position_centroid":[0.49872,0.09654,0.05282]},{"body_a":"attachment","body_b":"peg","contact_count":140.0,"contact_point_centroid":[0.5,0.1064,0.04862],"force_p95":22.21718,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":42.61262,"mean_force":3.34575,"phase_index":3.0,"phase_name":"final_align","phase_type":"align","tcp_position_centroid":[0.49748,0.10607,0.05315]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":50.0,"contact_point_centroid":[0.47486,0.07517,0.02696],"force_p95":0.46268,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.47095,"mean_force":0.30833,"phase_index":3.0,"phase_name":"final_align","phase_type":"align","tcp_position_centroid":[0.49803,0.09276,0.05297]},{"body_a":"peg","body_b":"channel_base_body","contact_count":639.0,"contact_point_centroid":[0.50092,0.11604,0.00939],"force_p95":0.61237,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.92055,"mean_force":0.55589,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49528,0.1838,0.19662]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":35.0,"contact_point_centroid":[0.52524,0.06853,0.0591],"force_p95":0.7156,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.04696,"mean_force":0.15747,"phase_index":3.0,"phase_name":"final_align","phase_type":"align","tcp_position_centroid":[0.49846,0.09284,0.05283]},{"body_a":"peg","body_b":"channel_base_body","contact_count":220.0,"contact_point_centroid":[0.50103,0.11591,0.00945],"force_p95":0.59281,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.64991,"mean_force":0.53939,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49667,0.14971,0.07619]},{"body_a":"peg","body_b":"channel_base_body","contact_count":3.0,"contact_point_centroid":[0.48375,0.11196,0.00943],"force_p95":0.60655,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.61013,"mean_force":0.57474,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49681,0.14234,0.05393]}],"total_contact_groups":11},"final_pose_error":0.16744,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50565,0.05755,0.03436],"final_tcp_position":[0.50064,0.0868,0.05245],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50095,0.11604,0.04]},"peak_contact_force":784.62578,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":655.0,"n_steps_budget":1000.0,"object_pos_end":[0.50093,0.11602,0.03387],"object_pos_start":[0.50095,0.11604,0.04],"object_to_goal_dist_end":0.19612,"object_to_goal_dist_start":0.19604,"object_z_max":0.04,"peak_contact_force":0.54233,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":639.0,"raw_peak_contact_force":1.92055,"subtask_id":"approach","tcp_end":[0.49822,0.15733,0.09924],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.07737,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":220.0,"n_steps_budget":600.0,"object_pos_end":[0.50092,0.11602,0.0339],"object_pos_start":[0.50093,0.11602,0.03387],"object_to_goal_dist_end":0.19612,"object_to_goal_dist_start":0.19612,"object_z_max":0.03401,"peak_contact_force":91.59551,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":221.0,"raw_peak_contact_force":91.59551,"subtask_id":"contact","tcp_end":[0.4968,0.14239,0.05397],"tcp_start":[0.49822,0.15733,0.09924],"tcp_to_object_dist_end":0.03339,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":3.0,"n_steps_budget":600.0,"object_pos_end":[0.5009,0.11601,0.0339],"object_pos_start":[0.50092,0.11602,0.0339],"object_to_goal_dist_end":0.19611,"object_to_goal_dist_start":0.19612,"object_z_max":0.0339,"peak_contact_force":52.64156,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":6.0,"raw_peak_contact_force":100.6414,"subtask_id":"push","tcp_end":[0.49683,0.14225,0.05387],"tcp_start":[0.49682,0.14229,0.0539],"tcp_to_object_dist_end":0.03323,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50565,0.05755,0.03436],"object_pos_start":[0.5009,0.11601,0.03389],"object_to_goal_dist_end":0.13779,"object_to_goal_dist_start":0.1961,"object_z_max":0.03754,"peak_contact_force":291.55035,"phase_name":"final_align","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":2280.0,"raw_peak_contact_force":784.62578,"tcp_end":[0.50064,0.0868,0.05245],"tcp_start":[0.49683,0.14225,0.05387],"tcp_to_object_dist_end":0.03475,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.88889,"average_solve_count":99.0,"average_success_count":99.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"contact_1.contact_force_threshold":6.87662,"final_align.lateral_offset_x":0.01,"push_1.push_distance":0.07102},"optimized_scores":{"best_composite_score":0.15088,"best_fitness_score":0.11088,"best_task_score":0.0032},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_right_wall","body_b":"link7","contact_count":878.0,"contact_point_centroid":[0.46071,0.1199,0.05735],"force_p95":272.28727,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":370.46768,"mean_force":222.92603,"phase_index":3.0,"phase_name":"final_align","phase_type":"align","tcp_position_centroid":[0.49629,0.08443,0.05862]},{"body_a":"world","body_b":"link7","contact_count":245.0,"contact_point_centroid":[0.49043,0.14949,-7e-05],"force_p95":355.4115,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":358.98826,"mean_force":310.69641,"phase_index":3.0,"phase_name":"final_align","phase_type":"align","tcp_position_centroid":[0.50349,0.08828,0.05351]},{"body_a":"attachment","body_b":"channel_right_wall","contact_count":3.0,"contact_point_centroid":[0.47496,0.12,0.05995],"force_p95":140.08495,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":145.65138,"mean_force":105.00476,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48259,0.09746,0.06925]},{"body_a":"attachment","body_b":"channel_right_wall","contact_count":93.0,"contact_point_centroid":[0.47499,0.12,0.05999],"force_p95":98.7625,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":101.67822,"mean_force":79.05142,"phase_index":3.0,"phase_name":"final_align","phase_type":"align","tcp_position_centroid":[0.48487,0.08913,0.06692]},{"body_a":"attachment","body_b":"channel_right_wall","contact_count":1.0,"contact_point_centroid":[0.47498,0.12,0.05998],"force_p95":46.76223,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":46.76223,"mean_force":46.76223,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.48247,0.09757,0.06943]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.49586,0.06087,0.00947],"force_p95":0.8478,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.52548,"mean_force":0.60343,"phase_index":3.0,"phase_name":"final_align","phase_type":"align","tcp_position_centroid":[0.49498,0.08501,0.05958]},{"body_a":"attachment","body_b":"peg","contact_count":138.0,"contact_point_centroid":[0.49465,0.08063,0.05698],"force_p95":1.39246,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":3.20435,"mean_force":0.59321,"phase_index":3.0,"phase_name":"final_align","phase_type":"align","tcp_position_centroid":[0.48776,0.08038,0.06387]},{"body_a":"peg","body_b":"channel_base_body","contact_count":692.0,"contact_point_centroid":[0.49541,0.06395,0.00938],"force_p95":0.56578,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.44546,"mean_force":0.55784,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48655,0.15961,0.19503]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":28.0,"contact_point_centroid":[0.47133,0.06388,0.03676],"force_p95":0.92436,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.16907,"mean_force":0.37063,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50423,0.21548,0.2931]},{"body_a":"peg","body_b":"channel_base_body","contact_count":168.0,"contact_point_centroid":[0.49443,0.06363,0.0094],"force_p95":0.5501,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55124,"mean_force":0.5454,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.48023,0.10273,0.0833]},{"body_a":"peg","body_b":"channel_base_body","contact_count":3.0,"contact_point_centroid":[0.4997,0.04691,0.0094],"force_p95":0.54583,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54598,"mean_force":0.54356,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48259,0.09746,0.06925]}],"total_contact_groups":11},"final_pose_error":0.17051,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49506,0.06307,0.03393],"final_tcp_position":[0.50639,0.0898,0.05512],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48093,0.06388,0.04]},"peak_contact_force":370.46768,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":719.0,"n_steps_budget":1000.0,"object_pos_end":[0.4949,0.06401,0.03397],"object_pos_start":[0.48093,0.06388,0.04],"object_to_goal_dist_end":0.14422,"object_to_goal_dist_start":0.14514,"object_z_max":0.04,"peak_contact_force":0.54727,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":720.0,"raw_peak_contact_force":2.44546,"subtask_id":"approach","tcp_end":[0.4795,0.10841,0.09859],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.0799,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":168.0,"n_steps_budget":600.0,"object_pos_end":[0.49509,0.06361,0.034],"object_pos_start":[0.4949,0.06401,0.03397],"object_to_goal_dist_end":0.14382,"object_to_goal_dist_start":0.14422,"object_z_max":0.034,"peak_contact_force":46.76223,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":169.0,"raw_peak_contact_force":46.76223,"subtask_id":"contact","tcp_end":[0.48253,0.09752,0.06928],"tcp_start":[0.4795,0.10841,0.09859],"tcp_to_object_dist_end":0.05052,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":3.0,"n_steps_budget":600.0,"object_pos_end":[0.49516,0.06362,0.034],"object_pos_start":[0.49509,0.06361,0.034],"object_to_goal_dist_end":0.14383,"object_to_goal_dist_start":0.14382,"object_z_max":0.034,"peak_contact_force":79.37575,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":6.0,"raw_peak_contact_force":145.65138,"subtask_id":"push","tcp_end":[0.48271,0.09735,0.06921],"tcp_start":[0.48266,0.0974,0.06922],"tcp_to_object_dist_end":0.05033,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49506,0.06307,0.03393],"object_pos_start":[0.49529,0.06369,0.034],"object_to_goal_dist_end":0.14329,"object_to_goal_dist_start":0.1439,"object_z_max":0.03539,"peak_contact_force":358.96807,"phase_name":"final_align","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":2354.0,"raw_peak_contact_force":370.46768,"tcp_end":[0.50639,0.0898,0.05512],"tcp_start":[0.48271,0.09735,0.06921],"tcp_to_object_dist_end":0.03594,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.88776,"average_solve_count":98.0,"average_success_count":98.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"contact_1.contact_force_threshold":6.37394,"final_align.lateral_offset_x":-0.00127,"push_1.push_distance":0.10226},"optimized_scores":{"best_composite_score":0.14595,"best_fitness_score":0.10595,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_right_wall","body_b":"link7","contact_count":843.0,"contact_point_centroid":[0.4548,0.1199,0.05816],"force_p95":440.7512,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":685.51414,"mean_force":277.83541,"phase_index":3.0,"phase_name":"final_align","phase_type":"align","tcp_position_centroid":[0.4902,0.08478,0.063]},{"body_a":"attachment","body_b":"channel_right_wall","contact_count":613.0,"contact_point_centroid":[0.47487,0.11467,0.05996],"force_p95":338.40854,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":591.44458,"mean_force":180.71432,"phase_index":3.0,"phase_name":"final_align","phase_type":"align","tcp_position_centroid":[0.48442,0.08409,0.0682]},{"body_a":"world","body_b":"link7","contact_count":151.0,"contact_point_centroid":[0.48338,0.15097,-9e-05],"force_p95":360.16387,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":364.53444,"mean_force":332.18444,"phase_index":3.0,"phase_name":"final_align","phase_type":"align","tcp_position_centroid":[0.49813,0.08954,0.0528]},{"body_a":"attachment","body_b":"channel_right_wall","contact_count":3.0,"contact_point_centroid":[0.47287,0.12,0.0599],"force_p95":57.33267,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":57.68701,"mean_force":54.46575,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.47294,0.09358,0.07194]},{"body_a":"attachment","body_b":"channel_right_wall","contact_count":1.0,"contact_point_centroid":[0.47282,0.12,0.05997],"force_p95":32.41774,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":32.41774,"mean_force":32.41774,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.47289,0.09365,0.07207]},{"body_a":"peg","body_b":"channel_base_body","contact_count":701.0,"contact_point_centroid":[0.4943,0.05903,0.00936],"force_p95":0.55972,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.20518,"mean_force":0.56705,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48032,0.15706,0.19481]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":35.0,"contact_point_centroid":[0.46807,0.05895,0.03796],"force_p95":1.19991,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.42382,"mean_force":0.50385,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50279,0.22096,0.28775]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.49424,0.05893,0.0094],"force_p95":0.55051,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55392,"mean_force":0.54539,"phase_index":3.0,"phase_name":"final_align","phase_type":"align","tcp_position_centroid":[0.48826,0.08538,0.06415]},{"body_a":"peg","body_b":"channel_base_body","contact_count":181.0,"contact_point_centroid":[0.49397,0.05889,0.00939],"force_p95":0.5503,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55382,"mean_force":0.54599,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.46892,0.09825,0.0842]},{"body_a":"peg","body_b":"channel_base_body","contact_count":3.0,"contact_point_centroid":[0.49002,0.04203,0.00939],"force_p95":0.54762,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54809,"mean_force":0.54475,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.47294,0.09358,0.07194]}],"total_contact_groups":10},"final_pose_error":0.17092,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49426,0.05923,0.03403],"final_tcp_position":[0.49978,0.09038,0.05353],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.46685,0.05894,0.04]},"peak_contact_force":685.51414,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":730.0,"n_steps_budget":1000.0,"object_pos_end":[0.494,0.05889,0.03389],"object_pos_start":[0.46685,0.05894,0.04],"object_to_goal_dist_end":0.13916,"object_to_goal_dist_start":0.14284,"object_z_max":0.04001,"peak_contact_force":0.54807,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":736.0,"raw_peak_contact_force":4.20518,"subtask_id":"approach","tcp_end":[0.46633,0.10368,0.09856],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.08338,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":181.0,"n_steps_budget":600.0,"object_pos_end":[0.49403,0.05881,0.03391],"object_pos_start":[0.494,0.05889,0.03389],"object_to_goal_dist_end":0.13907,"object_to_goal_dist_start":0.13916,"object_z_max":0.03391,"peak_contact_force":32.41774,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":182.0,"raw_peak_contact_force":32.41774,"subtask_id":"contact","tcp_end":[0.47293,0.09362,0.07198],"tcp_start":[0.46633,0.10368,0.09856],"tcp_to_object_dist_end":0.05574,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":3.0,"n_steps_budget":780.0,"object_pos_end":[0.49408,0.05879,0.03391],"object_pos_start":[0.49403,0.05881,0.03391],"object_to_goal_dist_end":0.13905,"object_to_goal_dist_start":0.13907,"object_z_max":0.03391,"peak_contact_force":51.56662,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":6.0,"raw_peak_contact_force":57.68701,"subtask_id":"push","tcp_end":[0.47297,0.0935,0.07188],"tcp_start":[0.47296,0.09353,0.0719],"tcp_to_object_dist_end":0.0556,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49426,0.05923,0.03403],"object_pos_start":[0.4942,0.0588,0.03391],"object_to_goal_dist_end":0.13948,"object_to_goal_dist_start":0.13905,"object_z_max":0.03403,"peak_contact_force":364.53444,"phase_name":"final_align","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":2607.0,"raw_peak_contact_force":685.51414,"tcp_end":[0.49978,0.09038,0.05353],"tcp_start":[0.47297,0.0935,0.07188],"tcp_to_object_dist_end":0.03716,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```