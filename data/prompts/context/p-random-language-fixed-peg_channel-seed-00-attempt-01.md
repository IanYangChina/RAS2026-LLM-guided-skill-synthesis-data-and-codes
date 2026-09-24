## Search State

- **Seed**: 0
- **Iteration**: 2 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 1 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | admittance_control | pose_tolerance | force_exceeded | pose_tolerance | 5 | 0.1787 | 0.00 | ❌ rejected |
| 0 | insert → approach → push → retract → lift → insert | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | linear_cartesian | impedance_motion | impedance_control | force_threshold_switch | impedance_control | position_control | position_control | admittance_control | force_exceeded | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | force_exceeded | 5 | 0.2281 | 0.74 | ✅ accepted |

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
- Frozen realised-scene SHA-256: `cd60c08f71f9d10bc11dd62c79067fee574cade1f8d1192fc945700528a8d454`
- Frozen object start: [0.5109569349857164, 0.061582937101109625, 0.04]
- Frozen task target: [0.5109569349857164, -0.09841706289889038, 0.04]
- Goal object position: (0.5109569349857164, -0.09841706289889038, 0.04)
- Task success criterion: peg must traverse the channel (0.16 m long) along axis (0.0, -1.0, 0.0); score = axial progress × lateral alignment — NOT a fixed TCP endpoint
- Object initial pose: (0.5109569349857164, 0.061582937101109625, 0.04)
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
  frozen_object_start: [0.511, 0.0616, 0.04]
  frozen_task_target: [0.511, -0.0984, 0.04]
  frozen_fixture_position: [0.54, 0, 0.035]
  frozen_object_starts: {'peg': [0.5109569349857164, 0.061582937101109625, 0.04]}
  frozen_targets: {'channel_exit': [0.5109569349857164, -0.09841706289889038, 0.04]}
  frozen_fixtures: {'channel_left_wall': [0.54, 0.0, 0.035], 'channel_right_wall': [0.46, 0.0, 0.035]}
  channel_axis: [0, -1, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 40
  channel_length_m: 0.16
  force_scale_n: 5
  realized_scene_sha256: cd60c08f71f9d10bc11dd62c79067fee574cade1f8d1192fc945700528a8d454

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

## Current Skill (Q=0.179) — your mutation base

```yaml
skill: peg_channel
phases:
- id: insert_1
  type: insert
  generator: linear_cartesian
  control: impedance_control
  termination: force_exceeded
- id: approach_1
  type: approach
  generator: linear_cartesian
  control: force_threshold_switch
  termination: pose_tolerance
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
  parameters:
    retract_height:
      type: scalar
      range:
      - 0.05
      - 0.2
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1
- id: lift_1
  type: lift
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  parameters:
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1
- id: insert_2
  type: insert
  generator: impedance_motion
  control: admittance_control
  termination: force_exceeded

```

## Design Metrics

- **Composite score**: 0.179
- **task_score** (E): 0.005
- **fitness_score**: 0.125  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.333
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.280

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach | 1.00 | 1.00 | 0.2585 |
| contact | 1.00 | 1.00 | 0.0063 |
| push | 0.00 | 1.00 | 0.0001 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.506, 0.090, 0.066) | (0.498, 0.080, 0.040)→(0.500, 0.081, 0.034) | 0.161→0.161 | 1.00 / 1.000 | 0.530 | 2.179 |
| contact | descend | 1.00 / force_exceeded | (0.506, 0.090, 0.066)→(0.504, 0.089, 0.060) | (0.500, 0.081, 0.034)→(0.500, 0.081, 0.034) | 0.161→0.161 | 1.00 / 2.000 | 20.831 | 20.831 |
| push | push | 0.00 / guard_failure | (0.504, 0.087, 0.060)→(0.504, 0.087, 0.060) | (0.500, 0.081, 0.034)→(0.500, 0.080, 0.034) | 0.161→0.160 | 1.00 / 2.000 | 29.488 | 39.343 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.002
- alignment_error: None
- force_efficiency: 0.180
- terminal_score: 0.002
- phase_score: 0.257
- phase_breakdown.push_score: 0.033
- phase_breakdown.approach_score: 0.555
- phase_breakdown.contact_score: 0.630

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.155
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.010
- **Median Q (composite search score)**: 0.186
- **K-run variance**: 0.0008
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.348


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `d6915c31707ac435a9367b840736087e39a7a48adfeb36a4f94b6b3ae57cce94`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.04,0.04]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `19172182883d287409b73cab43749e937e65f1ca1d4501d52b4a913a881aad36`; realized-scene SHA-256: `cd60c08f71f9d10bc11dd62c79067fee574cade1f8d1192fc945700528a8d454`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.51096,0.06158,0.04]},{"name":"goal","value":[0.51096,-0.09842,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.51096,0.06158,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.51096,-0.09842,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.15888,"average_solve_count":107.0,"average_success_count":107.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach.approach_speed":0.0614,"contact.contact_force":9.37621,"contact.contact_speed":0.03706,"push.push_depth":0.15804,"push.push_speed":0.03035},"optimized_scores":{"best_composite_score":0.20832,"best_fitness_score":0.15498,"best_task_score":0.00193},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":7.0,"contact_point_centroid":[0.49085,0.05579,0.00931],"force_p95":38.5351,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":41.02337,"mean_force":24.16275,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.50397,0.08878,0.06055]},{"body_a":"attachment","body_b":"peg","contact_count":7.0,"contact_point_centroid":[0.50918,0.07831,0.05857],"force_p95":38.09466,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":40.6197,"mean_force":23.7074,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.50397,0.08878,0.06055]},{"body_a":"peg","body_b":"channel_base_body","contact_count":26.0,"contact_point_centroid":[0.50496,0.06165,0.00938],"force_p95":0.55075,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":21.02544,"mean_force":1.33436,"phase_index":1.0,"phase_name":"contact","phase_type":"descend","tcp_position_centroid":[0.50471,0.08896,0.06346]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.50979,0.07851,0.05872],"force_p95":20.56344,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":20.56344,"mean_force":20.56344,"phase_index":1.0,"phase_name":"contact","phase_type":"descend","tcp_position_centroid":[0.50424,0.08886,0.06103]},{"body_a":"peg","body_b":"channel_base_body","contact_count":494.0,"contact_point_centroid":[0.50357,0.0616,0.00934],"force_p95":0.58467,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.17216,"mean_force":0.56296,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.50226,0.14327,0.17885]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":19.0,"contact_point_centroid":[0.52623,0.06158,0.03217],"force_p95":0.5921,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.62339,"mean_force":0.34148,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.49973,0.19893,0.2982]}],"total_contact_groups":6},"final_pose_error":0.32729,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50333,0.06123,0.03374],"final_tcp_position":[0.50374,0.0886,0.06024],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.51096,0.06158,0.04]},"peak_contact_force":41.02337,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":517.0,"n_steps_budget":1000.0,"object_pos_end":[0.50377,0.06159,0.03378],"object_pos_start":[0.51096,0.06158,0.04],"object_to_goal_dist_end":0.14178,"object_to_goal_dist_start":0.14201,"object_z_max":0.04,"peak_contact_force":0.54914,"phase_name":"approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":513.0,"raw_peak_contact_force":2.17216,"subtask_id":"approach","tcp_end":[0.50573,0.08968,0.06645],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.04313,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":26.0,"n_steps_budget":600.0,"object_pos_end":[0.50377,0.06156,0.03377],"object_pos_start":[0.50377,0.06159,0.03378],"object_to_goal_dist_end":0.14175,"object_to_goal_dist_start":0.14178,"object_z_max":0.03378,"peak_contact_force":21.02544,"phase_name":"contact","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":27.0,"raw_peak_contact_force":21.02544,"subtask_id":"contact","tcp_end":[0.50422,0.08887,0.06086],"tcp_start":[0.50573,0.08968,0.06645],"tcp_to_object_dist_end":0.03846,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":7.0,"n_steps_budget":1000.0,"object_pos_end":[0.50341,0.06133,0.03373],"object_pos_start":[0.50377,0.06156,0.03377],"object_to_goal_dist_end":0.14151,"object_to_goal_dist_start":0.14175,"object_z_max":0.03377,"peak_contact_force":29.2505,"phase_name":"push","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":14.0,"raw_peak_contact_force":41.02337,"subtask_id":"push","tcp_end":[0.50374,0.0886,0.06024],"tcp_start":[0.50379,0.08864,0.0603],"tcp_to_object_dist_end":0.03803,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `f24211f27d4adabdef509c8ed61621317fdbcaa86fc9ac888f85a717335bb714`; realized-scene SHA-256: `9fd07833843a6ee28e14c5e2ce05f86547005983f45e63c41c77b8dac2024c0a`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50095,0.11604,0.04]},{"name":"goal","value":[0.50095,-0.04396,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.50095,0.11604,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.50095,-0.04396,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.30769,"average_solve_count":78.0,"average_success_count":78.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach.approach_speed":0.11227,"contact.contact_force":11.19229,"contact.contact_speed":0.01233,"push.push_depth":0.18819,"push.push_speed":0.02131},"optimized_scores":{"best_composite_score":0.14169,"best_fitness_score":0.08836,"best_task_score":0.00979},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":19.0,"contact_point_centroid":[0.49213,0.10644,0.00932],"force_p95":36.63801,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":37.80434,"mean_force":25.94371,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.5035,0.0874,0.05982]},{"body_a":"attachment","body_b":"peg","contact_count":19.0,"contact_point_centroid":[0.50721,0.09852,0.05849],"force_p95":36.58606,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":37.61077,"mean_force":25.44138,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.5035,0.0874,0.05982]},{"body_a":"peg","body_b":"channel_base_body","contact_count":30.0,"contact_point_centroid":[0.50038,0.11635,0.00941],"force_p95":0.59285,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":22.85191,"mean_force":1.29035,"phase_index":1.0,"phase_name":"contact","phase_type":"descend","tcp_position_centroid":[0.50454,0.08891,0.06331]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.50821,0.09993,0.05892],"force_p95":22.3834,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":22.3834,"mean_force":22.3834,"phase_index":1.0,"phase_name":"contact","phase_type":"descend","tcp_position_centroid":[0.50404,0.08885,0.06074]},{"body_a":"peg","body_b":"channel_base_body","contact_count":477.0,"contact_point_centroid":[0.50096,0.11597,0.00936],"force_p95":0.62229,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.92055,"mean_force":0.56111,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.5023,0.14379,0.17996]}],"total_contact_groups":5},"final_pose_error":0.35361,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50029,0.11447,0.03497],"final_tcp_position":[0.50325,0.08489,0.05925],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50095,0.11604,0.04]},"peak_contact_force":37.80434,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":493.0,"n_steps_budget":1000.0,"object_pos_end":[0.50093,0.11603,0.03383],"object_pos_start":[0.50095,0.11604,0.04],"object_to_goal_dist_end":0.19613,"object_to_goal_dist_start":0.19604,"object_z_max":0.04,"peak_contact_force":0.49976,"phase_name":"approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":477.0,"raw_peak_contact_force":1.92055,"subtask_id":"approach","tcp_end":[0.50576,0.08967,0.06644],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.04221,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":30.0,"n_steps_budget":1000.0,"object_pos_end":[0.50098,0.11623,0.03386],"object_pos_start":[0.50093,0.11603,0.03383],"object_to_goal_dist_end":0.19632,"object_to_goal_dist_start":0.19613,"object_z_max":0.03386,"peak_contact_force":22.85191,"phase_name":"contact","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":31.0,"raw_peak_contact_force":22.85191,"subtask_id":"contact","tcp_end":[0.50403,0.08885,0.06057],"tcp_start":[0.50576,0.08967,0.06644],"tcp_to_object_dist_end":0.03837,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":19.0,"n_steps_budget":1000.0,"object_pos_end":[0.50027,0.11459,0.03485],"object_pos_start":[0.50098,0.11623,0.03386],"object_to_goal_dist_end":0.19466,"object_to_goal_dist_start":0.19632,"object_z_max":0.03492,"peak_contact_force":37.80434,"phase_name":"push","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":38.0,"raw_peak_contact_force":37.80434,"subtask_id":"push","tcp_end":[0.50325,0.08489,0.05925],"tcp_start":[0.50325,0.08507,0.0593],"tcp_to_object_dist_end":0.03856,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `d098a7862ff18c9bbe982af3446a89a0fa6bcfa8790d7d955f65b2375d67a881`; realized-scene SHA-256: `2a92d231da5879af7af8916eb4c7dff00148227e84220c4d9643d9841dc77ee7`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.48093,0.06388,0.04]},{"name":"goal","value":[0.48093,-0.09612,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.48093,0.06388,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.48093,-0.09612,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.30159,"average_solve_count":63.0,"average_success_count":63.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach.approach_speed":0.13727,"contact.contact_force":16.78836,"contact.contact_speed":0.0197,"push.push_depth":0.12271,"push.push_speed":0.03122},"optimized_scores":{"best_composite_score":0.18605,"best_fitness_score":0.13272,"best_task_score":0.00228},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":9.0,"contact_point_centroid":[0.4908,0.05215,0.00939],"force_p95":37.40482,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":39.20091,"mean_force":25.55741,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.50376,0.08873,0.05959]},{"body_a":"attachment","body_b":"peg","contact_count":9.0,"contact_point_centroid":[0.50658,0.0772,0.05867],"force_p95":37.04363,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":38.84735,"mean_force":25.17551,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.50376,0.08873,0.05959]},{"body_a":"peg","body_b":"channel_base_body","contact_count":33.0,"contact_point_centroid":[0.49207,0.06294,0.0094],"force_p95":0.54942,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":18.61418,"mean_force":1.09318,"phase_index":1.0,"phase_name":"contact","phase_type":"descend","tcp_position_centroid":[0.50457,0.08891,0.06293]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.50691,0.07728,0.05894],"force_p95":18.21766,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":18.21766,"mean_force":18.21766,"phase_index":1.0,"phase_name":"contact","phase_type":"descend","tcp_position_centroid":[0.50405,0.08886,0.0601]},{"body_a":"peg","body_b":"channel_base_body","contact_count":458.0,"contact_point_centroid":[0.49561,0.06387,0.00936],"force_p95":0.59681,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.44546,"mean_force":0.56408,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.50239,0.14245,0.17709]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":28.0,"contact_point_centroid":[0.47133,0.06388,0.03676],"force_p95":0.92436,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.16907,"mean_force":0.37063,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.49977,0.19776,0.29528]}],"total_contact_groups":6},"final_pose_error":0.29172,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49475,0.06331,0.03387],"final_tcp_position":[0.50353,0.08836,0.05925],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48093,0.06388,0.04]},"peak_contact_force":39.20091,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":485.0,"n_steps_budget":1000.0,"object_pos_end":[0.4951,0.06407,0.03394],"object_pos_start":[0.48093,0.06388,0.04],"object_to_goal_dist_end":0.14428,"object_to_goal_dist_start":0.14514,"object_z_max":0.04,"peak_contact_force":0.54204,"phase_name":"approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":486.0,"raw_peak_contact_force":2.44546,"subtask_id":"approach","tcp_end":[0.50581,0.08967,0.06644],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.04274,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":33.0,"n_steps_budget":870.0,"object_pos_end":[0.49524,0.06374,0.03394],"object_pos_start":[0.4951,0.06407,0.03394],"object_to_goal_dist_end":0.14394,"object_to_goal_dist_start":0.14428,"object_z_max":0.03394,"peak_contact_force":18.61418,"phase_name":"contact","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":34.0,"raw_peak_contact_force":18.61418,"subtask_id":"contact","tcp_end":[0.50404,0.08887,0.05994],"tcp_start":[0.50581,0.08967,0.06644],"tcp_to_object_dist_end":0.03722,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":9.0,"n_steps_budget":1000.0,"object_pos_end":[0.49485,0.06346,0.03385],"object_pos_start":[0.49524,0.06374,0.03394],"object_to_goal_dist_end":0.14369,"object_to_goal_dist_start":0.14394,"object_z_max":0.03394,"peak_contact_force":21.4099,"phase_name":"push","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":18.0,"raw_peak_contact_force":39.20091,"subtask_id":"push","tcp_end":[0.50353,0.08836,0.05925],"tcp_start":[0.50356,0.08843,0.05931],"tcp_to_object_dist_end":0.03661,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```