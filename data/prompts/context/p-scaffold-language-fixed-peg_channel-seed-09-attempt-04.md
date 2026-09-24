## Search State

- **Seed**: 9
- **Iteration**: 5 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 4 | align → approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | force_threshold_switch | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 6 | 0.0983 | 0.12 | ❌ rejected |
| 3 | align → approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | force_threshold_switch | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 6 | 0.1006 | 0.12 | ❌ rejected |
| 2 | approach → contact → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 6 | 0.1183 | 0.00 | ❌ rejected |
| 1 | align → approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 7 | -0.0403 | 0.00 | ❌ rejected |
| 0 | align → approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | force_threshold_switch | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 6 | 0.0986 | 0.13 | ✅ accepted |

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
- Frozen realised-scene SHA-256: `a0d7ea14565b0a67e86de15fa43f3773b761884db645527685cd53e0fd95aeb9`
- Frozen object start: [0.5296199363176067, 0.06294537672700443, 0.04]
- Frozen task target: [0.5296199363176067, -0.09705462327299558, 0.04]
- Goal object position: (0.5296199363176067, -0.09705462327299558, 0.04)
- Task success criterion: peg must traverse the channel (0.16 m long) along axis (0.0, -1.0, 0.0); score = axial progress × lateral alignment — NOT a fixed TCP endpoint
- Object initial pose: (0.5296199363176067, 0.06294537672700443, 0.04)
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
  frozen_object_start: [0.5296, 0.0629, 0.04]
  frozen_task_target: [0.5296, -0.0971, 0.04]
  frozen_fixture_position: [0.54, 0, 0.035]
  frozen_object_starts: {'peg': [0.5296199363176067, 0.06294537672700443, 0.04]}
  frozen_targets: {'channel_exit': [0.5296199363176067, -0.09705462327299558, 0.04]}
  frozen_fixtures: {'channel_left_wall': [0.54, 0.0, 0.035], 'channel_right_wall': [0.46, 0.0, 0.035]}
  channel_axis: [0, -1, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 40
  channel_length_m: 0.16
  force_scale_n: 5
  realized_scene_sha256: a0d7ea14565b0a67e86de15fa43f3773b761884db645527685cd53e0fd95aeb9

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

## Current Skill (Q=0.098) — your mutation base

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
  generator: impedance_motion
  control: impedance_control
  termination: time_limit
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

- **Composite score**: 0.098
- **task_score** (E): 0.117
- **fitness_score**: 0.238  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.250
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.390

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| align_1 | 1.00 | 1.00 | 0.2533 |
| approach_1 | 1.00 | 1.00 | 0.0088 |
| contact_1 | 1.00 | 1.00 | 0.0007 |
| push_1 | 1.00 | 1.00 | 0.0876 |
| retract_1 | 0.00 | 1.00 | 0.0952 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| align_1 | align | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.510, 0.116, 0.063) | (0.512, 0.067, 0.040)→(0.502, 0.067, 0.034) | 0.150→0.147 | 1.00 / 2.000 | 331.482 | 360.279 |
| approach_1 | approach | 1.00 / step_budget | (0.510, 0.116, 0.063)→(0.514, 0.114, 0.056) | (0.502, 0.067, 0.034)→(0.502, 0.067, 0.034) | 0.147→0.147 | 1.00 / 1.667 | 152.847 | 275.275 |
| contact_1 | contact | 1.00 / force_exceeded | (0.514, 0.114, 0.056)→(0.514, 0.113, 0.056) | (0.502, 0.067, 0.034)→(0.502, 0.067, 0.034) | 0.147→0.147 | 1.00 / 2.000 | 55.000 | 55.000 |
| push_1 | push | 1.00 / time_limit | (0.514, 0.113, 0.056)→(0.513, 0.026, 0.056) | (0.502, 0.067, 0.034)→(0.508, 0.022, 0.034) | 0.147→0.103 | 1.00 / 2.667 | 229.930 | 244.195 |
| retract_1 | retract | 0.00 / step_budget | (0.513, 0.026, 0.056)→(0.504, 0.015, 0.149) | (0.508, 0.022, 0.034)→(0.502, 0.018, 0.031) | 0.103→0.101 | 1.00 / 1.000 | 0.572 | 104.388 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.913
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.351
- phase_score: 0.459
- phase_breakdown.approach_score: 0.724
- phase_breakdown.contact_score: 0.590
- phase_breakdown.push_score: 0.328

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.416
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.351
- **Median Q (composite search score)**: 0.011
- **K-run variance**: 0.0158
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.402


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `bf8103833c1e96f48e87b3ce39b3b3bf17e268470bd7b5c037546fb78b5150b8`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.04,0.04]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `98954a34ee744fa939070f7dadee8a411de43cdcfeddcf3b4bfc5c3a4c536020`; realized-scene SHA-256: `a0d7ea14565b0a67e86de15fa43f3773b761884db645527685cd53e0fd95aeb9`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.52962,0.06295,0.04]},{"name":"goal","value":[0.52962,-0.09705,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.52962,0.06295,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.52962,-0.09705,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.5,"average_solve_count":160.0,"average_success_count":160.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":0.00689,"approach_1.speed":0.05225,"contact_1.contact_force":8.03165,"push_1.push_distance":0.19394,"push_1.push_speed":0.09999,"retract_1.speed":0.04794},"optimized_scores":{"best_composite_score":0.00821,"best_fitness_score":0.14821,"best_task_score":0.0002},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_left_wall","contact_count":114.0,"contact_point_centroid":[0.53488,0.11266,0.05979],"force_p95":345.12221,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":353.73417,"mean_force":317.18085,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.52374,0.11275,0.06404]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":960.0,"contact_point_centroid":[0.53404,0.07238,0.05996],"force_p95":276.91475,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":286.50505,"mean_force":206.99929,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52306,0.07273,0.06475]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":426.0,"contact_point_centroid":[0.53649,0.11267,0.05993],"force_p95":266.86038,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":269.63949,"mean_force":246.60197,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.52542,0.11271,0.0645]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":5.0,"contact_point_centroid":[0.53294,0.05468,0.05996],"force_p95":98.67203,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":108.39083,"mean_force":67.37323,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.52205,0.05572,0.06485]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":1.0,"contact_point_centroid":[0.53694,0.11245,0.05993],"force_p95":74.02593,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":74.02593,"mean_force":74.02593,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.52585,0.1125,0.06447]},{"body_a":"peg","body_b":"channel_base_body","contact_count":876.0,"contact_point_centroid":[0.5058,0.06299,0.00937],"force_p95":0.55584,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.88411,"mean_force":0.56201,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.51235,0.14948,0.1623]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":34.0,"contact_point_centroid":[0.53102,0.06295,0.03156],"force_p95":1.1362,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.98455,"mean_force":0.48262,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49981,0.19843,0.29603]},{"body_a":"peg","body_b":"channel_base_body","contact_count":426.0,"contact_point_centroid":[0.50609,0.06292,0.00938],"force_p95":0.55274,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55532,"mean_force":0.54656,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.52542,0.11271,0.0645]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.50596,0.06304,0.00939],"force_p95":0.55121,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55493,"mean_force":0.5464,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.5231,0.07344,0.06475]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.50605,0.06293,0.00939],"force_p95":0.55082,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55491,"mean_force":0.54625,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.51392,0.04345,0.11031]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1.0,"contact_point_centroid":[0.48833,0.05973,0.00938],"force_p95":0.54874,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54874,"mean_force":0.54874,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.52585,0.1125,0.06447]}],"total_contact_groups":11},"final_pose_error":0.14715,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50592,0.06286,0.03388],"final_tcp_position":[0.50974,0.03246,0.1568],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.52962,0.06295,0.04]},"peak_contact_force":353.73417,"phases":[{"contact_detected":true,"contact_event_count":2.0,"n_steps":904.0,"n_steps_budget":1000.0,"object_pos_end":[0.50601,0.06303,0.03381],"object_pos_start":[0.52962,0.06295,0.04],"object_to_goal_dist_end":0.14329,"object_to_goal_dist_start":0.14598,"object_z_max":0.04001,"peak_contact_force":317.66646,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":1024.0,"raw_peak_contact_force":353.73417,"tcp_end":[0.52444,0.11271,0.06453],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.06125,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":426.0,"n_steps_budget":600.0,"object_pos_end":[0.50593,0.06298,0.03381],"object_pos_start":[0.50601,0.06303,0.03381],"object_to_goal_dist_end":0.14323,"object_to_goal_dist_start":0.14329,"object_z_max":0.03381,"peak_contact_force":240.12447,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":852.0,"raw_peak_contact_force":269.63949,"tcp_end":[0.52585,0.1125,0.06447],"tcp_start":[0.52444,0.11271,0.06453],"tcp_to_object_dist_end":0.06156,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1.0,"n_steps_budget":600.0,"object_pos_end":[0.50594,0.063,0.03381],"object_pos_start":[0.50593,0.06298,0.03381],"object_to_goal_dist_end":0.14326,"object_to_goal_dist_start":0.14323,"object_z_max":0.03381,"peak_contact_force":74.02593,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2.0,"raw_peak_contact_force":74.02593,"tcp_end":[0.52586,0.1125,0.06447],"tcp_start":[0.52585,0.1125,0.06447],"tcp_to_object_dist_end":0.06153,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50608,0.06303,0.03386],"object_pos_start":[0.50594,0.063,0.03381],"object_to_goal_dist_end":0.14329,"object_to_goal_dist_start":0.14326,"object_z_max":0.03386,"peak_contact_force":281.8369,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1960.0,"raw_peak_contact_force":286.50505,"tcp_end":[0.52206,0.05566,0.06482],"tcp_start":[0.52586,0.1125,0.06447],"tcp_to_object_dist_end":0.03561,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50592,0.06286,0.03388],"object_pos_start":[0.50608,0.06303,0.03386],"object_to_goal_dist_end":0.14312,"object_to_goal_dist_start":0.14329,"object_z_max":0.03388,"peak_contact_force":0.5414,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1005.0,"raw_peak_contact_force":108.39083,"tcp_end":[0.50974,0.03246,0.1568],"tcp_start":[0.52206,0.05566,0.06482],"tcp_to_object_dist_end":0.12669,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `cae0d95026bac46aa2e5d95cffd531753a79751757c4f25fa56c1ec6e19c2175`; realized-scene SHA-256: `11c1f773d01ee1d435c5ecc0d1531095d6f84a2c0ab26c3ff2560d4c62fcd41a`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.53648,0.05661,0.04]},{"name":"goal","value":[0.53648,-0.10339,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.53648,0.05661,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.53648,-0.10339,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.53247,"average_solve_count":154.0,"average_success_count":154.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":-0.00879,"approach_1.speed":0.06685,"contact_1.contact_force":16.59988,"push_1.push_distance":0.19729,"push_1.push_speed":0.09841,"retract_1.speed":0.05555},"optimized_scores":{"best_composite_score":0.01079,"best_fitness_score":0.15079,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_left_wall","contact_count":115.0,"contact_point_centroid":[0.54111,0.10688,0.05978],"force_p95":348.37484,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":360.87221,"mean_force":319.04148,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.52992,0.10705,0.06389]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":957.0,"contact_point_centroid":[0.53799,0.0652,0.05996],"force_p95":274.08496,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":281.9118,"mean_force":205.75867,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52695,0.06561,0.06458]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":455.0,"contact_point_centroid":[0.54216,0.10676,0.05994],"force_p95":225.76828,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":227.24613,"mean_force":204.86906,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.53105,0.10687,0.0644]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":4.0,"contact_point_centroid":[0.53638,0.04632,0.05995],"force_p95":101.2544,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":107.89961,"mean_force":70.99165,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.52543,0.04741,0.0647]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":1.0,"contact_point_centroid":[0.54194,0.10637,0.05994],"force_p95":74.37477,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":74.37477,"mean_force":74.37477,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.53079,0.10651,0.06431]},{"body_a":"peg","body_b":"channel_base_body","contact_count":893.0,"contact_point_centroid":[0.50599,0.05663,0.00937],"force_p95":0.59924,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.44541,"mean_force":0.56446,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.51585,0.14624,0.1622]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":37.0,"contact_point_centroid":[0.53251,0.05661,0.02607],"force_p95":1.30561,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.83578,"mean_force":0.52649,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.4999,0.19822,0.29562]},{"body_a":"peg","body_b":"channel_base_body","contact_count":455.0,"contact_point_centroid":[0.5061,0.05663,0.00938],"force_p95":0.55015,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55018,"mean_force":0.54674,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.53105,0.10687,0.0644]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.5061,0.05661,0.00938],"force_p95":0.55015,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55015,"mean_force":0.54674,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.527,0.06639,0.06458]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.50615,0.05659,0.00938],"force_p95":0.55015,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55015,"mean_force":0.54674,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.51652,0.03689,0.11054]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1.0,"contact_point_centroid":[0.52227,0.0487,0.00938],"force_p95":0.54501,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54501,"mean_force":0.54501,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.53079,0.10651,0.06431]}],"total_contact_groups":11},"final_pose_error":0.14559,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50611,0.05662,0.03378],"final_tcp_position":[0.51164,0.02745,0.1575],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.53648,0.05661,0.04]},"peak_contact_force":360.87221,"phases":[{"contact_detected":true,"contact_event_count":2.0,"n_steps":922.0,"n_steps_budget":1000.0,"object_pos_end":[0.50613,0.05659,0.03378],"object_pos_start":[0.53648,0.05661,0.04],"object_to_goal_dist_end":0.13687,"object_to_goal_dist_start":0.1414,"object_z_max":0.04001,"peak_contact_force":318.37129,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":1045.0,"raw_peak_contact_force":360.87221,"tcp_end":[0.53064,0.107,0.06441],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.06388,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":455.0,"n_steps_budget":600.0,"object_pos_end":[0.50615,0.0566,0.03378],"object_pos_start":[0.50613,0.05659,0.03378],"object_to_goal_dist_end":0.13688,"object_to_goal_dist_start":0.13687,"object_z_max":0.03378,"peak_contact_force":217.88766,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":910.0,"raw_peak_contact_force":227.24613,"tcp_end":[0.53079,0.10651,0.06431],"tcp_start":[0.53064,0.107,0.06441],"tcp_to_object_dist_end":0.06349,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1.0,"n_steps_budget":600.0,"object_pos_end":[0.50613,0.05659,0.03378],"object_pos_start":[0.50615,0.0566,0.03378],"object_to_goal_dist_end":0.13687,"object_to_goal_dist_start":0.13688,"object_z_max":0.03378,"peak_contact_force":74.37477,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2.0,"raw_peak_contact_force":74.37477,"tcp_end":[0.5308,0.10651,0.06431],"tcp_start":[0.53079,0.10651,0.06431],"tcp_to_object_dist_end":0.0635,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50615,0.05662,0.03378],"object_pos_start":[0.50613,0.05659,0.03378],"object_to_goal_dist_end":0.1369,"object_to_goal_dist_start":0.13687,"object_z_max":0.03378,"peak_contact_force":278.04188,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1957.0,"raw_peak_contact_force":281.9118,"tcp_end":[0.52543,0.04736,0.06468],"tcp_start":[0.5308,0.10651,0.06431],"tcp_to_object_dist_end":0.03758,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50611,0.05662,0.03378],"object_pos_start":[0.50615,0.05662,0.03378],"object_to_goal_dist_end":0.1369,"object_to_goal_dist_start":0.1369,"object_z_max":0.03378,"peak_contact_force":0.54553,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1004.0,"raw_peak_contact_force":107.89961,"tcp_end":[0.51164,0.02745,0.1575],"tcp_start":[0.52543,0.04736,0.06468],"tcp_to_object_dist_end":0.12723,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `fd7ada9a67242f1adcdb6e23860d1223cdc8a17daf859e94e1687ff0564d9575`; realized-scene SHA-256: `8df62a5afc1e0110114ab6e06b493b5783d0c746729f7f7f1f2cb046babeda91`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.47029,0.07994,0.04]},{"name":"goal","value":[0.47029,-0.08006,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.47029,0.07994,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.47029,-0.08006,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.45783,"average_solve_count":166.0,"average_success_count":166.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":0.00098,"approach_1.speed":0.04292,"contact_1.contact_force":15.5859,"push_1.push_distance":0.1703,"push_1.push_speed":0.09992,"retract_1.speed":0.03946},"optimized_scores":{"best_composite_score":0.276,"best_fitness_score":0.416,"best_task_score":0.35099},"replay_outcomes":[{"contacts":{"omitted_contact_groups":2,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_right_wall","contact_count":85.0,"contact_point_centroid":[0.47491,0.12,0.05983],"force_p95":349.23456,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":366.23021,"mean_force":312.61988,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.47173,0.12708,0.06106]},{"body_a":"attachment","body_b":"channel_right_wall","contact_count":147.0,"contact_point_centroid":[0.47498,0.12,0.05955],"force_p95":303.40425,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":328.93871,"mean_force":245.5479,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.4805,0.12727,0.05648]},{"body_a":"attachment","body_b":"peg","contact_count":738.0,"contact_point_centroid":[0.49853,0.02705,0.03668],"force_p95":146.29141,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":164.169,"mean_force":74.77202,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49059,0.03356,0.03861]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":701.0,"contact_point_centroid":[0.53507,0.0545,0.05999],"force_p95":126.5696,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":148.95685,"mean_force":103.99311,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48933,0.05587,0.03849]},{"body_a":"peg","body_b":"channel_base_body","contact_count":956.0,"contact_point_centroid":[0.50545,0.02199,0.00951],"force_p95":106.17613,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":129.52008,"mean_force":36.57478,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48963,0.05037,0.03852]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":684.0,"contact_point_centroid":[0.52607,0.01411,0.02499],"force_p95":96.10648,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":101.16122,"mean_force":55.81117,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49087,0.02861,0.03862]},{"body_a":"attachment","body_b":"channel_right_wall","contact_count":51.0,"contact_point_centroid":[0.47498,0.11939,0.04343],"force_p95":98.23827,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":100.13825,"mean_force":33.14137,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48564,0.11965,0.03798]},{"body_a":"attachment","body_b":"peg","contact_count":84.0,"contact_point_centroid":[0.49806,-0.02813,0.03769],"force_p95":67.60074,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":96.87216,"mean_force":29.79346,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.4892,-0.0239,0.04222]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":121.0,"contact_point_centroid":[0.52582,-0.03791,0.02907],"force_p95":57.89378,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":80.47038,"mean_force":20.54537,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48885,-0.02369,0.04384]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":2.0,"contact_point_centroid":[0.53744,-0.03074,0.06],"force_p95":70.55009,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":70.69146,"mean_force":69.27777,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49185,-0.0249,0.03891]},{"body_a":"peg","body_b":"channel_base_body","contact_count":987.0,"contact_point_centroid":[0.49977,-0.06223,0.00833],"force_p95":9.4688,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":61.83068,"mean_force":2.28281,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48977,-0.0199,0.08533]},{"body_a":"attachment","body_b":"channel_right_wall","contact_count":1.0,"contact_point_centroid":[0.47499,0.12,0.04366],"force_p95":16.59924,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":16.59924,"mean_force":16.59924,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.48557,0.1215,0.03824]},{"body_a":"peg","body_b":"link7","contact_count":15.0,"contact_point_centroid":[0.5195,0.03457,0.06865],"force_p95":9.9834,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":10.08171,"mean_force":6.17899,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48947,0.05973,0.03863]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":4.0,"contact_point_centroid":[0.475,-0.0904,0.02419],"force_p95":7.34275,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.56283,"mean_force":2.4266,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49079,-0.01721,0.11403]},{"body_a":"peg","body_b":"channel_base_body","contact_count":811.0,"contact_point_centroid":[0.49401,0.07994,0.00937],"force_p95":0.5999,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.77147,"mean_force":0.56234,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.4824,0.15853,0.16395]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":35.0,"contact_point_centroid":[0.46907,0.07994,0.03235],"force_p95":1.18295,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.95027,"mean_force":0.45938,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49904,0.19852,0.29579]}],"total_contact_groups":18},"final_pose_error":0.16844,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49439,-0.06606,0.02412],"final_tcp_position":[0.49155,-0.01546,0.13248],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.47029,0.07994,0.04]},"peak_contact_force":366.23021,"phases":[{"contact_detected":true,"contact_event_count":2.0,"n_steps":839.0,"n_steps_budget":1000.0,"object_pos_end":[0.49385,0.07997,0.03377],"object_pos_start":[0.47029,0.07994,0.04],"object_to_goal_dist_end":0.16021,"object_to_goal_dist_start":0.16268,"object_z_max":0.04001,"peak_contact_force":358.40792,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":931.0,"raw_peak_contact_force":366.23021,"tcp_end":[0.47364,0.12685,0.06028],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.05752,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":209.0,"n_steps_budget":600.0,"object_pos_end":[0.49383,0.07995,0.03377],"object_pos_start":[0.49385,0.07997,0.03377],"object_to_goal_dist_end":0.16019,"object_to_goal_dist_start":0.16021,"object_z_max":0.03378,"peak_contact_force":0.52777,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":356.0,"raw_peak_contact_force":328.93871,"tcp_end":[0.48625,0.12247,0.03963],"tcp_start":[0.47364,0.12685,0.06028],"tcp_to_object_dist_end":0.04359,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":12.0,"n_steps_budget":600.0,"object_pos_end":[0.4938,0.07994,0.03377],"object_pos_start":[0.49383,0.07995,0.03377],"object_to_goal_dist_end":0.16018,"object_to_goal_dist_start":0.16019,"object_z_max":0.03377,"peak_contact_force":16.59924,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":13.0,"raw_peak_contact_force":16.59924,"tcp_end":[0.48554,0.1214,0.03815],"tcp_start":[0.48625,0.12247,0.03963],"tcp_to_object_dist_end":0.0425,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51069,-0.05231,0.03516],"object_pos_start":[0.4938,0.07994,0.03377],"object_to_goal_dist_end":0.03008,"object_to_goal_dist_start":0.16018,"object_z_max":0.04045,"peak_contact_force":129.91046,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3145.0,"raw_peak_contact_force":164.169,"tcp_end":[0.49185,-0.02483,0.03891],"tcp_start":[0.48554,0.1214,0.03815],"tcp_to_object_dist_end":0.03353,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49439,-0.06606,0.02412],"object_pos_start":[0.51069,-0.05231,0.03516],"object_to_goal_dist_end":0.02186,"object_to_goal_dist_start":0.03008,"object_z_max":0.0383,"peak_contact_force":0.62987,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1198.0,"raw_peak_contact_force":96.87216,"tcp_end":[0.49155,-0.01546,0.13248],"tcp_start":[0.49185,-0.02483,0.03891],"tcp_to_object_dist_end":0.11963,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```