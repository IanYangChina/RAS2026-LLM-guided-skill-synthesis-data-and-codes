## Search State

- **Seed**: 0
- **Iteration**: 11 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 10 | approach → approach → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 5 | 0.3974 | 0.73 | ❌ rejected |
| 9 | approach → approach → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 5 | 0.0691 | 0.00 | ❌ rejected |
| 8 | approach → approach → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | position_control | position_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 5 | 0.0966 | 0.00 | ❌ rejected |
| 7 | approach → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | 3 | 0.3217 | 0.00 | ❌ rejected |
| 6 | insert → approach → push → retract → lift → insert | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | linear_cartesian | impedance_motion | impedance_control | force_threshold_switch | impedance_control | position_control | position_control | admittance_control | force_exceeded | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | force_exceeded | 5 | 0.2014 | 0.71 | ❌ rejected |

**Proposal policy**: task_score is 0.73 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.397) — your mutation base

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

- **Composite score**: 0.397
- **task_score** (E): 0.734
- **fitness_score**: 0.707  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.310

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_vertical | 1.00 | 1.00 | 0.1714 |
| approach_horizontal | 1.00 | 1.00 | 0.1054 |
| contact | 1.00 | 1.00 | 0.0224 |
| push | 1.00 | 1.00 | 0.1582 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_vertical | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.495, 0.126, 0.148) | (0.498, 0.080, 0.040)→(0.500, 0.081, 0.034) | 0.161→0.161 | 1.00 / 1.000 | 0.545 | 2.179 |
| approach_horizontal | approach | 1.00 / step_budget | (0.495, 0.126, 0.148)→(0.496, 0.120, 0.043) | (0.500, 0.081, 0.034)→(0.500, 0.080, 0.034) | 0.161→0.161 | 1.00 / 1.000 | 0.542 | 0.583 |
| contact | contact | 1.00 / step_budget | (0.496, 0.120, 0.043)→(0.496, 0.102, 0.030) | (0.500, 0.080, 0.034)→(0.502, 0.072, 0.035) | 0.161→0.152 | 1.00 / 2.000 | 2.514 | 3.815 |
| push | push | 1.00 / step_budget | (0.496, 0.102, 0.030)→(0.495, -0.056, 0.034) | (0.502, 0.072, 0.035)→(0.507, -0.082, 0.036) | 0.152→0.010 | 1.00 / 3.333 | 73.878 | 84.446 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.918
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.918
- phase_score: 0.705
- phase_breakdown.push_score: 0.662
- phase_breakdown.approach_score: 0.804
- phase_breakdown.contact_score: 0.737

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.790
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.949
- **Median Q (composite search score)**: 0.457
- **K-run variance**: 0.0103
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.367


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.70435,"average_solve_count":115.0,"average_success_count":115.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_horizontal.speed":0.08354,"approach_vertical.speed":0.13808,"contact.force_threshold":23.94378,"contact.speed":0.13314,"push.speed":0.09267},"optimized_scores":{"best_composite_score":0.48026,"best_fitness_score":0.79026,"best_task_score":0.9178},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg","contact_count":666.0,"contact_point_centroid":[0.50173,-0.0162,0.04432],"force_p95":89.51997,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":109.64365,"mean_force":16.38246,"phase_index":3.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.49603,-0.005,0.03098]},{"body_a":"peg","body_b":"channel_base_body","contact_count":130.0,"contact_point_centroid":[0.50746,-0.10109,0.05996],"force_p95":98.47717,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":99.72653,"mean_force":65.46918,"phase_index":3.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.49575,-0.05739,0.03392]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":6.0,"contact_point_centroid":[0.53367,0.07732,0.05998],"force_p95":96.4956,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":98.25081,"mean_force":76.57631,"phase_index":3.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.49614,0.07807,0.02569]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":544.0,"contact_point_centroid":[0.52513,-0.03633,0.03362],"force_p95":23.0889,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":49.55581,"mean_force":4.28167,"phase_index":3.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.496,-0.00882,0.03117]},{"body_a":"peg","body_b":"link7","contact_count":12.0,"contact_point_centroid":[0.52325,0.05538,0.06187],"force_p95":13.23016,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":13.35591,"mean_force":3.41337,"phase_index":3.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.49622,0.07875,0.02578]},{"body_a":"peg","body_b":"channel_base_body","contact_count":486.0,"contact_point_centroid":[0.50644,-0.03576,0.00986],"force_p95":9.87799,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":13.29345,"mean_force":3.731,"phase_index":3.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.49602,0.008,0.03019]},{"body_a":"peg","body_b":"channel_base_body","contact_count":392.0,"contact_point_centroid":[0.50467,0.04886,0.0097],"force_p95":3.36264,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.11435,"mean_force":1.76568,"phase_index":2.0,"phase_name":"contact","phase_type":"contact","tcp_position_centroid":[0.49868,0.0907,0.034]},{"body_a":"attachment","body_b":"peg","contact_count":232.0,"contact_point_centroid":[0.50236,0.0752,0.04477],"force_p95":3.21165,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":3.80227,"mean_force":2.25634,"phase_index":2.0,"phase_name":"contact","phase_type":"contact","tcp_position_centroid":[0.49887,0.08715,0.03191]},{"body_a":"peg","body_b":"channel_base_body","contact_count":528.0,"contact_point_centroid":[0.50363,0.06155,0.00934],"force_p95":0.58352,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.17216,"mean_force":0.5619,"phase_index":0.0,"phase_name":"approach_vertical","phase_type":"approach","tcp_position_centroid":[0.50294,0.15249,0.21942]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":19.0,"contact_point_centroid":[0.52623,0.06158,0.03217],"force_p95":0.5921,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.62339,"mean_force":0.34148,"phase_index":0.0,"phase_name":"approach_vertical","phase_type":"approach","tcp_position_centroid":[0.49975,0.1989,0.29852]},{"body_a":"peg","body_b":"channel_base_body","contact_count":329.0,"contact_point_centroid":[0.50376,0.06158,0.00938],"force_p95":0.55119,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55158,"mean_force":0.54667,"phase_index":1.0,"phase_name":"approach_horizontal","phase_type":"approach","tcp_position_centroid":[0.50294,0.10467,0.09489]}],"total_contact_groups":11},"final_pose_error":0.02063,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50785,-0.08527,0.03513],"final_tcp_position":[0.49504,-0.06101,0.03365],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.51096,0.06158,0.04]},"peak_contact_force":109.64365,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":551.0,"n_steps_budget":870.0,"object_pos_end":[0.50374,0.06158,0.03378],"object_pos_start":[0.51096,0.06158,0.04],"object_to_goal_dist_end":0.14177,"object_to_goal_dist_start":0.14201,"object_z_max":0.04,"peak_contact_force":0.54619,"phase_name":"approach_vertical","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":547.0,"raw_peak_contact_force":2.17216,"subtask_id":"approach","tcp_end":[0.50722,0.10804,0.14661],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.12206,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":329.0,"n_steps_budget":870.0,"object_pos_end":[0.50374,0.06158,0.03378],"object_pos_start":[0.50374,0.06158,0.03378],"object_to_goal_dist_end":0.14176,"object_to_goal_dist_start":0.14177,"object_z_max":0.03378,"peak_contact_force":0.54544,"phase_name":"approach_horizontal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":329.0,"raw_peak_contact_force":0.55158,"subtask_id":"approach","tcp_end":[0.50045,0.10163,0.043],"tcp_start":[0.50722,0.10804,0.14661],"tcp_to_object_dist_end":0.04123,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":401.0,"n_steps_budget":600.0,"object_pos_end":[0.50539,0.05342,0.03529],"object_pos_start":[0.50374,0.06158,0.03378],"object_to_goal_dist_end":0.13361,"object_to_goal_dist_start":0.14176,"object_z_max":0.03542,"peak_contact_force":2.48533,"phase_name":"contact","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":624.0,"raw_peak_contact_force":4.11435,"subtask_id":"contact","tcp_end":[0.49953,0.08299,0.02996],"tcp_start":[0.50045,0.10163,0.043],"tcp_to_object_dist_end":0.03061,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":885.0,"n_steps_budget":1000.0,"object_pos_end":[0.50785,-0.08527,0.03513],"object_pos_start":[0.50539,0.05342,0.03529],"object_to_goal_dist_end":0.01063,"object_to_goal_dist_start":0.13361,"object_z_max":0.03785,"peak_contact_force":109.64365,"phase_name":"push","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1844.0,"raw_peak_contact_force":109.64365,"subtask_id":"push","tcp_end":[0.49504,-0.06101,0.03365],"tcp_start":[0.49953,0.08299,0.02996],"tcp_to_object_dist_end":0.02747,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.30345,"average_solve_count":145.0,"average_success_count":145.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_horizontal.speed":0.16664,"approach_vertical.speed":0.05259,"contact.force_threshold":22.79041,"contact.speed":0.09332,"push.speed":0.09991},"optimized_scores":{"best_composite_score":0.45748,"best_fitness_score":0.76748,"best_task_score":0.94909},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":504.0,"contact_point_centroid":[0.50671,0.00725,0.00991],"force_p95":12.44596,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":32.76743,"mean_force":5.58057,"phase_index":3.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.49438,0.05109,0.0297]},{"body_a":"peg","body_b":"link7","contact_count":45.0,"contact_point_centroid":[0.51991,0.10959,0.06214],"force_p95":21.27121,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":30.96496,"mean_force":10.73863,"phase_index":3.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.49322,0.12938,0.02572]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":700.0,"contact_point_centroid":[0.52512,0.01694,0.029],"force_p95":13.56128,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":21.87056,"mean_force":2.32195,"phase_index":3.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.49437,0.04414,0.02989]},{"body_a":"attachment","body_b":"peg","contact_count":766.0,"contact_point_centroid":[0.50053,0.03144,0.04089],"force_p95":16.11848,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":21.57745,"mean_force":4.08939,"phase_index":3.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.49442,0.04255,0.03]},{"body_a":"peg","body_b":"channel_base_body","contact_count":387.0,"contact_point_centroid":[0.50257,0.10205,0.00975],"force_p95":3.26095,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.80528,"mean_force":1.7979,"phase_index":2.0,"phase_name":"contact","phase_type":"contact","tcp_position_centroid":[0.4956,0.14451,0.03391]},{"body_a":"attachment","body_b":"peg","contact_count":248.0,"contact_point_centroid":[0.49959,0.1295,0.04572],"force_p95":3.05137,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":3.48236,"mean_force":2.14672,"phase_index":2.0,"phase_name":"contact","phase_type":"contact","tcp_position_centroid":[0.49585,0.14139,0.03204]},{"body_a":"peg","body_b":"channel_base_body","contact_count":498.0,"contact_point_centroid":[0.5009,0.11597,0.00937],"force_p95":0.62198,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.92055,"mean_force":0.55982,"phase_index":0.0,"phase_name":"approach_vertical","phase_type":"approach","tcp_position_centroid":[0.49814,0.17897,0.22234]},{"body_a":"peg","body_b":"channel_base_body","contact_count":326.0,"contact_point_centroid":[0.50089,0.11618,0.00943],"force_p95":0.60282,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.64352,"mean_force":0.54157,"phase_index":1.0,"phase_name":"approach_horizontal","phase_type":"approach","tcp_position_centroid":[0.4965,0.15685,0.0958]}],"total_contact_groups":8},"final_pose_error":0.03396,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50699,-0.07462,0.03607],"final_tcp_position":[0.4959,-0.04679,0.03416],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50095,0.11604,0.04]},"peak_contact_force":32.76743,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":514.0,"n_steps_budget":1000.0,"object_pos_end":[0.50094,0.1161,0.03386],"object_pos_start":[0.50095,0.11604,0.04],"object_to_goal_dist_end":0.19619,"object_to_goal_dist_start":0.19604,"object_z_max":0.04,"peak_contact_force":0.54552,"phase_name":"approach_vertical","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":498.0,"raw_peak_contact_force":1.92055,"subtask_id":"approach","tcp_end":[0.49795,0.15893,0.14894],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.12283,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":326.0,"n_steps_budget":600.0,"object_pos_end":[0.501,0.11604,0.03399],"object_pos_start":[0.50094,0.1161,0.03386],"object_to_goal_dist_end":0.19614,"object_to_goal_dist_start":0.19619,"object_z_max":0.03401,"peak_contact_force":0.53424,"phase_name":"approach_horizontal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":326.0,"raw_peak_contact_force":0.64352,"subtask_id":"approach","tcp_end":[0.49696,0.15533,0.04278],"tcp_start":[0.49795,0.15893,0.14894],"tcp_to_object_dist_end":0.04046,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":397.0,"n_steps_budget":600.0,"object_pos_end":[0.50301,0.10762,0.03531],"object_pos_start":[0.501,0.11604,0.03399],"object_to_goal_dist_end":0.1877,"object_to_goal_dist_start":0.19614,"object_z_max":0.03541,"peak_contact_force":2.44205,"phase_name":"contact","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":635.0,"raw_peak_contact_force":3.80528,"subtask_id":"contact","tcp_end":[0.49672,0.13709,0.03004],"tcp_start":[0.49696,0.15533,0.04278],"tcp_to_object_dist_end":0.0306,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50699,-0.07462,0.03607],"object_pos_start":[0.50301,0.10762,0.03531],"object_to_goal_dist_end":0.00966,"object_to_goal_dist_start":0.1877,"object_z_max":0.03732,"peak_contact_force":1.06525,"phase_name":"push","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2015.0,"raw_peak_contact_force":32.76743,"subtask_id":"push","tcp_end":[0.4959,-0.04679,0.03416],"tcp_start":[0.49672,0.13709,0.03004],"tcp_to_object_dist_end":0.03001,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.90179,"average_solve_count":224.0,"average_success_count":224.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_horizontal.speed":0.02029,"approach_vertical.speed":0.08518,"contact.force_threshold":34.97647,"contact.speed":0.07877,"push.speed":0.07973},"optimized_scores":{"best_composite_score":0.25446,"best_fitness_score":0.56446,"best_task_score":0.33622},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg","contact_count":776.0,"contact_point_centroid":[0.4987,-0.01111,0.04124],"force_p95":92.53611,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":110.92588,"mean_force":17.42133,"phase_index":3.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.49181,-0.00066,0.031]},{"body_a":"peg","body_b":"channel_base_body","contact_count":150.0,"contact_point_centroid":[0.50737,-0.10109,0.06048],"force_p95":99.34312,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":101.11885,"mean_force":65.47552,"phase_index":3.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.49483,-0.05767,0.03395]},{"body_a":"peg","body_b":"channel_base_body","contact_count":607.0,"contact_point_centroid":[0.50956,-0.03158,0.00988],"force_p95":28.55493,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":39.74185,"mean_force":7.17705,"phase_index":3.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.49143,0.00766,0.03059]},{"body_a":"peg","body_b":"link7","contact_count":89.0,"contact_point_centroid":[0.51071,0.05643,0.06417],"force_p95":29.55746,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":30.44797,"mean_force":17.88169,"phase_index":3.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.48809,0.0734,0.02693]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":631.0,"contact_point_centroid":[0.52517,-0.02728,0.03751],"force_p95":23.65626,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":30.01603,"mean_force":5.35668,"phase_index":3.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.49179,-0.00139,0.03101]},{"body_a":"peg","body_b":"channel_base_body","contact_count":399.0,"contact_point_centroid":[0.49644,0.05158,0.0097],"force_p95":3.09858,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.52611,"mean_force":1.60033,"phase_index":2.0,"phase_name":"contact","phase_type":"contact","tcp_position_centroid":[0.48902,0.09302,0.0339]},{"body_a":"attachment","body_b":"peg","contact_count":227.0,"contact_point_centroid":[0.49352,0.07738,0.04529],"force_p95":2.7943,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":3.22095,"mean_force":2.04478,"phase_index":2.0,"phase_name":"contact","phase_type":"contact","tcp_position_centroid":[0.48954,0.08926,0.03194]},{"body_a":"peg","body_b":"channel_base_body","contact_count":536.0,"contact_point_centroid":[0.49548,0.0638,0.00937],"force_p95":0.58418,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.44546,"mean_force":0.56142,"phase_index":0.0,"phase_name":"approach_vertical","phase_type":"approach","tcp_position_centroid":[0.4887,0.15354,0.21956]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":28.0,"contact_point_centroid":[0.47133,0.06388,0.03676],"force_p95":0.92436,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.16907,"mean_force":0.37063,"phase_index":0.0,"phase_name":"approach_vertical","phase_type":"approach","tcp_position_centroid":[0.49929,0.19837,0.29733]},{"body_a":"peg","body_b":"channel_base_body","contact_count":415.0,"contact_point_centroid":[0.49494,0.06412,0.0094],"force_p95":0.55054,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55289,"mean_force":0.54545,"phase_index":1.0,"phase_name":"approach_horizontal","phase_type":"approach","tcp_position_centroid":[0.48338,0.10699,0.09478]}],"total_contact_groups":10},"final_pose_error":0.02049,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50626,-0.08477,0.03608],"final_tcp_position":[0.49448,-0.06136,0.03355],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48093,0.06388,0.04]},"peak_contact_force":110.92588,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":563.0,"n_steps_budget":1000.0,"object_pos_end":[0.49526,0.064,0.03394],"object_pos_start":[0.48093,0.06388,0.04],"object_to_goal_dist_end":0.14421,"object_to_goal_dist_start":0.14514,"object_z_max":0.04,"peak_contact_force":0.54234,"phase_name":"approach_vertical","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":564.0,"raw_peak_contact_force":2.44546,"subtask_id":"approach","tcp_end":[0.47953,0.11037,0.14738],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.12355,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":415.0,"n_steps_budget":1000.0,"object_pos_end":[0.49488,0.0637,0.03401],"object_pos_start":[0.49526,0.064,0.03394],"object_to_goal_dist_end":0.14392,"object_to_goal_dist_start":0.14421,"object_z_max":0.03401,"peak_contact_force":0.54575,"phase_name":"approach_horizontal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":415.0,"raw_peak_contact_force":0.55289,"subtask_id":"approach","tcp_end":[0.48986,0.10397,0.04212],"tcp_start":[0.47953,0.11037,0.14738],"tcp_to_object_dist_end":0.04138,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":411.0,"n_steps_budget":600.0,"object_pos_end":[0.49757,0.05579,0.03536],"object_pos_start":[0.49488,0.0637,0.03401],"object_to_goal_dist_end":0.13589,"object_to_goal_dist_start":0.14392,"object_z_max":0.03553,"peak_contact_force":2.61449,"phase_name":"contact","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":626.0,"raw_peak_contact_force":3.52611,"subtask_id":"contact","tcp_end":[0.49057,0.08511,0.03024],"tcp_start":[0.48986,0.10397,0.04212],"tcp_to_object_dist_end":0.03057,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":965.0,"n_steps_budget":1000.0,"object_pos_end":[0.50626,-0.08477,0.03608],"object_pos_start":[0.49757,0.05579,0.03536],"object_to_goal_dist_end":0.00879,"object_to_goal_dist_start":0.13589,"object_z_max":0.03798,"peak_contact_force":110.92588,"phase_name":"push","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2253.0,"raw_peak_contact_force":110.92588,"subtask_id":"push","tcp_end":[0.49448,-0.06136,0.03355],"tcp_start":[0.49057,0.08511,0.03024],"tcp_to_object_dist_end":0.02633,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```