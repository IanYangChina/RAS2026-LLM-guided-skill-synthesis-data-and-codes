## Search State

- **Seed**: 0
- **Iteration**: 1 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 0 | insert → approach → push → retract → lift → insert | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | linear_cartesian | impedance_motion | impedance_control | force_threshold_switch | impedance_control | position_control | position_control | admittance_control | force_exceeded | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | force_exceeded | 5 | 0.2281 | 0.74 | ✅ accepted |

**Proposal policy**: task_score is 0.74 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.228) — your mutation base

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

- **Composite score**: 0.228
- **task_score** (E): 0.743
- **fitness_score**: 0.561  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.037
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.370

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| insert_1 | 0.00 | 1.00 | 0.1730 |
| approach_1 | 1.00 | 1.00 | 0.1465 |
| push_1 | 0.67 | 1.00 | 0.1483 |
| retract_1 | 0.00 | 1.00 | 0.1030 |
| lift_1 | 0.00 | 1.00 | 0.1560 |
| insert_2 | 0.00 | 1.00 | 0.1656 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| insert_1 | insert | 0.00 / step_budget | (0.500, 0.200, 0.300)→(0.497, 0.075, 0.180) | (0.498, 0.080, 0.040)→(0.500, 0.080, 0.034) | 0.161→0.161 | 1.00 / 1.000 | 0.575 | 2.179 |
| approach_1 | approach | 1.00 / step_budget | (0.497, 0.075, 0.180)→(0.497, 0.119, 0.043) | (0.500, 0.080, 0.034)→(0.500, 0.084, 0.033) | 0.161→0.165 | 1.00 / 1.667 | 34.686 | 43.877 |
| push_1 | push | 0.67 / step_budget | (0.497, 0.119, 0.043)→(0.494, -0.029, 0.038) | (0.500, 0.084, 0.033)→(0.508, -0.055, 0.033) | 0.165→0.034 | 1.00 / 3.000 | 63.815 | 172.412 |
| retract_1 | retract | 0.00 / step_budget | (0.494, -0.029, 0.038)→(0.493, 0.006, 0.133) | (0.508, -0.055, 0.033)→(0.504, -0.051, 0.031) | 0.034→0.034 | 1.00 / 1.000 | 0.545 | 105.498 |
| lift_1 | lift | 0.00 / step_budget | (0.493, 0.006, 0.133)→(0.409, -0.043, 0.254) | (0.504, -0.051, 0.031)→(0.503, -0.051, 0.031) | 0.034→0.034 | 1.00 / 1.000 | 0.593 | 0.652 |
| insert_2 | insert | 0.00 / step_budget | (0.409, -0.043, 0.254)→(0.468, -0.068, 0.101) | (0.503, -0.051, 0.031)→(0.503, -0.051, 0.031) | 0.034→0.034 | 1.00 / 1.000 | 0.562 | 0.596 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.875
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.875
- phase_score: 0.528
- phase_breakdown.push_score: 0.619
- phase_breakdown.approach_score: 0.783
- phase_breakdown.contact_score: 0.000

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.667
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.875
- **Median Q (composite search score)**: 0.257
- **K-run variance**: 0.0050
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.322


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.53036,"average_solve_count":247.0,"average_success_count":247.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"lift_1.speed":0.05648,"push_1.push_distance":0.13644,"push_1.push_speed":0.0807,"retract_1.retract_height":0.12314,"retract_1.speed":0.05441},"optimized_scores":{"best_composite_score":0.29657,"best_fitness_score":0.66657,"best_task_score":0.87453},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":368.0,"contact_point_centroid":[0.54167,-0.00884,0.06],"force_p95":65.51386,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":103.96968,"mean_force":48.77819,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49686,-0.00678,0.03699]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":3.0,"contact_point_centroid":[0.5428,-0.05253,0.05999],"force_p95":79.04688,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":80.58733,"mean_force":68.39805,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49817,-0.05635,0.03661]},{"body_a":"attachment","body_b":"peg","contact_count":712.0,"contact_point_centroid":[0.50269,-0.00535,0.04284],"force_p95":34.10239,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":67.75163,"mean_force":8.30287,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49669,0.00607,0.03706]},{"body_a":"peg","body_b":"channel_base_body","contact_count":76.0,"contact_point_centroid":[0.50629,-0.10073,0.0575],"force_p95":61.37318,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":67.34638,"mean_force":34.62552,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49777,-0.05422,0.03667]},{"body_a":"attachment","body_b":"peg","contact_count":71.0,"contact_point_centroid":[0.50466,-0.06432,0.05504],"force_p95":13.30217,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":48.64854,"mean_force":5.13918,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49625,-0.0526,0.03948]},{"body_a":"peg","body_b":"channel_base_body","contact_count":51.0,"contact_point_centroid":[0.50539,-0.10069,0.06074],"force_p95":18.57581,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":48.63057,"mean_force":6.96741,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49675,-0.05388,0.0382]},{"body_a":"peg","body_b":"channel_base_body","contact_count":596.0,"contact_point_centroid":[0.50615,-0.02388,0.00984],"force_p95":14.87462,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":21.10417,"mean_force":5.64725,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49667,0.01828,0.0373]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":395.0,"contact_point_centroid":[0.52508,-0.00347,0.02174],"force_p95":7.04278,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.46444,"mean_force":1.72196,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49639,0.02298,0.03708]},{"body_a":"peg","body_b":"channel_base_body","contact_count":977.0,"contact_point_centroid":[0.50366,0.06159,0.00935],"force_p95":0.6416,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.17216,"mean_force":0.55484,"phase_index":0.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.49748,0.13519,0.23593]},{"body_a":"peg","body_b":"channel_base_body","contact_count":946.0,"contact_point_centroid":[0.50633,-0.07892,0.0094],"force_p95":0.55761,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.96333,"mean_force":0.54633,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49481,-0.02815,0.08309]},{"body_a":"peg","body_b":"channel_base_body","contact_count":454.0,"contact_point_centroid":[0.50368,0.06157,0.00936],"force_p95":0.64141,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.64379,"mean_force":0.54631,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49703,0.08639,0.11069]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":19.0,"contact_point_centroid":[0.52623,0.06158,0.03217],"force_p95":0.5921,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.62339,"mean_force":0.34148,"phase_index":0.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.49956,0.19884,0.29897]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.5064,-0.07831,0.00938],"force_p95":0.55309,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55347,"mean_force":0.54675,"phase_index":4.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.45315,-0.02901,0.18367]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.5064,-0.07831,0.00938],"force_p95":0.55306,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55308,"mean_force":0.54674,"phase_index":5.0,"phase_name":"insert_2","phase_type":"insert","tcp_position_centroid":[0.44218,-0.05934,0.1669]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":1.0,"contact_point_centroid":[0.525,-0.07928,0.01286],"force_p95":0.10557,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.10557,"mean_force":0.10557,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.496,-0.05232,0.03925]}],"total_contact_groups":15},"final_pose_error":0.05763,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50636,-0.07834,0.03378],"final_tcp_position":[0.47338,-0.07108,0.09033],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.51096,0.06158,0.04]},"peak_contact_force":103.96968,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50384,0.06159,0.03376],"object_pos_start":[0.51096,0.06158,0.04],"object_to_goal_dist_end":0.14178,"object_to_goal_dist_start":0.14201,"object_z_max":0.04,"peak_contact_force":0.59321,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":996.0,"raw_peak_contact_force":2.17216,"tcp_end":[0.49696,0.07528,0.18003],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.14707,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":454.0,"n_steps_budget":930.0,"object_pos_end":[0.5038,0.06158,0.03376],"object_pos_start":[0.50384,0.06159,0.03376],"object_to_goal_dist_end":0.14177,"object_to_goal_dist_start":0.14178,"object_z_max":0.03377,"peak_contact_force":0.47825,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":454.0,"raw_peak_contact_force":0.64379,"tcp_end":[0.49926,0.09848,0.04185],"tcp_start":[0.49696,0.07528,0.18003],"tcp_to_object_dist_end":0.03805,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50558,-0.0848,0.03577],"object_pos_start":[0.5038,0.06158,0.03376],"object_to_goal_dist_end":0.00849,"object_to_goal_dist_start":0.14177,"object_z_max":0.03804,"peak_contact_force":53.61422,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2147.0,"raw_peak_contact_force":103.96968,"tcp_end":[0.49817,-0.05632,0.03662],"tcp_start":[0.49926,0.09848,0.04185],"tcp_to_object_dist_end":0.02943,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5064,-0.07836,0.03378],"object_pos_start":[0.50558,-0.0848,0.03577],"object_to_goal_dist_end":0.00907,"object_to_goal_dist_start":0.00849,"object_z_max":0.03721,"peak_contact_force":0.54616,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1072.0,"raw_peak_contact_force":80.58733,"tcp_end":[0.49539,-0.0101,0.12696],"tcp_start":[0.49817,-0.05632,0.03662],"tcp_to_object_dist_end":0.11603,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50638,-0.07836,0.03378],"object_pos_start":[0.5064,-0.07836,0.03378],"object_to_goal_dist_end":0.00906,"object_to_goal_dist_start":0.00907,"object_z_max":0.03378,"peak_contact_force":0.55306,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":1000.0,"raw_peak_contact_force":0.55347,"tcp_end":[0.41377,-0.04803,0.24493],"tcp_start":[0.49539,-0.0101,0.12696],"tcp_to_object_dist_end":0.23255,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50636,-0.07834,0.03378],"object_pos_start":[0.50638,-0.07836,0.03378],"object_to_goal_dist_end":0.00905,"object_to_goal_dist_start":0.00906,"object_z_max":0.03378,"peak_contact_force":0.5416,"phase_name":"insert_2","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":1000.0,"raw_peak_contact_force":0.55308,"tcp_end":[0.47338,-0.07108,0.09033],"tcp_start":[0.41377,-0.04803,0.24493],"tcp_to_object_dist_end":0.06587,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.65041,"average_solve_count":246.0,"average_success_count":246.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"lift_1.speed":0.06424,"push_1.push_distance":0.13792,"push_1.push_speed":0.06754,"retract_1.retract_height":0.09356,"retract_1.speed":0.06363},"optimized_scores":{"best_composite_score":0.25672,"best_fitness_score":0.51561,"best_task_score":0.84044},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":841.0,"contact_point_centroid":[0.5025,0.0745,0.00821],"force_p95":185.01377,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":188.33696,"mean_force":81.39607,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50163,0.1058,0.04428]},{"body_a":"attachment","body_b":"peg","contact_count":831.0,"contact_point_centroid":[0.50588,0.09596,0.04592],"force_p95":184.53305,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":187.87454,"mean_force":87.65409,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50171,0.10554,0.04437]},{"body_a":"attachment","body_b":"peg","contact_count":109.0,"contact_point_centroid":[0.50657,0.13982,0.05102],"force_p95":119.53343,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":130.43451,"mean_force":83.80714,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49846,0.14657,0.05326]},{"body_a":"peg","body_b":"channel_base_body","contact_count":563.0,"contact_point_centroid":[0.50214,0.1166,0.00925],"force_p95":94.17839,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":117.99062,"mean_force":15.43742,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49609,0.11288,0.10781]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":212.0,"contact_point_centroid":[0.47346,0.0759,0.03731],"force_p95":70.79063,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":75.95209,"mean_force":31.17369,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50367,0.09925,0.04471]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":107.0,"contact_point_centroid":[0.54179,0.03834,0.06],"force_p95":53.61132,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":58.48974,"mean_force":42.70272,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49677,0.04058,0.03708]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":2.0,"contact_point_centroid":[0.54214,0.01805,0.06],"force_p95":55.03165,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":55.85909,"mean_force":47.58462,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49717,0.02135,0.0371]},{"body_a":"peg","body_b":"world","contact_count":145.0,"contact_point_centroid":[0.50194,0.12548,-0.00015],"force_p95":19.32639,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":48.74864,"mean_force":12.60526,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.5003,0.15493,0.04491]},{"body_a":"peg","body_b":"world","contact_count":28.0,"contact_point_centroid":[0.50222,0.12719,-0.0003],"force_p95":37.33342,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":39.90411,"mean_force":28.00895,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49992,0.15488,0.04587]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":112.0,"contact_point_centroid":[0.52504,0.01491,0.02185],"force_p95":6.12187,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":6.75804,"mean_force":1.89796,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49675,0.0415,0.03709]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.50615,-0.00658,0.00943],"force_p95":0.55426,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":5.07028,"mean_force":0.54591,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.4943,0.03288,0.09026]},{"body_a":"attachment","body_b":"peg","contact_count":33.0,"contact_point_centroid":[0.50421,0.01103,0.05578],"force_p95":0.64515,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":4.58976,"mean_force":0.39062,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49536,0.02284,0.04068]},{"body_a":"peg","body_b":"channel_base_body","contact_count":984.0,"contact_point_centroid":[0.50098,0.11602,0.0094],"force_p95":0.60736,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.92055,"mean_force":0.55146,"phase_index":0.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.49749,0.13563,0.23636]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.5062,-0.00556,0.00938],"force_p95":0.55216,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55217,"mean_force":0.54673,"phase_index":4.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44977,0.0029,0.20105]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.5062,-0.00555,0.00938],"force_p95":0.55216,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55216,"mean_force":0.54673,"phase_index":5.0,"phase_name":"insert_2","phase_type":"insert","tcp_position_centroid":[0.43485,-0.04727,0.1859]}],"total_contact_groups":15},"final_pose_error":0.08104,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50622,-0.00557,0.03379],"final_tcp_position":[0.46509,-0.06326,0.11119],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50095,0.11604,0.04]},"peak_contact_force":188.33696,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50092,0.11601,0.03383],"object_pos_start":[0.50095,0.11604,0.04],"object_to_goal_dist_end":0.19611,"object_to_goal_dist_start":0.19604,"object_z_max":0.04,"peak_contact_force":0.58045,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":984.0,"raw_peak_contact_force":1.92055,"tcp_end":[0.49696,0.07528,0.18003],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.15182,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":563.0,"n_steps_budget":1000.0,"object_pos_end":[0.50228,0.12805,0.02979],"object_pos_start":[0.50092,0.11601,0.03383],"object_to_goal_dist_end":0.20832,"object_to_goal_dist_start":0.19611,"object_z_max":0.0342,"peak_contact_force":103.03901,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":700.0,"raw_peak_contact_force":130.43451,"tcp_end":[0.50029,0.1577,0.04359],"tcp_start":[0.49696,0.07528,0.18003],"tcp_to_object_dist_end":0.03276,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50624,-0.00704,0.03627],"object_pos_start":[0.50228,0.12805,0.02979],"object_to_goal_dist_end":0.07332,"object_to_goal_dist_start":0.20832,"object_z_max":0.03749,"peak_contact_force":14.39493,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2248.0,"raw_peak_contact_force":188.33696,"tcp_end":[0.49718,0.0215,0.03713],"tcp_start":[0.50029,0.1577,0.04359],"tcp_to_object_dist_end":0.02996,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50624,-0.00558,0.03379],"object_pos_start":[0.50624,-0.00704,0.03627],"object_to_goal_dist_end":0.07494,"object_to_goal_dist_start":0.07332,"object_z_max":0.03657,"peak_contact_force":0.5436,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1035.0,"raw_peak_contact_force":55.85909,"tcp_end":[0.49509,0.03765,0.14432],"tcp_start":[0.49718,0.0215,0.03713],"tcp_to_object_dist_end":0.11921,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50623,-0.00557,0.03379],"object_pos_start":[0.50624,-0.00558,0.03379],"object_to_goal_dist_end":0.07495,"object_to_goal_dist_start":0.07494,"object_z_max":0.03379,"peak_contact_force":0.54361,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":1000.0,"raw_peak_contact_force":0.55217,"tcp_end":[0.40723,-0.03171,0.26215],"tcp_start":[0.49509,0.03765,0.14432],"tcp_to_object_dist_end":0.25027,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50622,-0.00557,0.03379],"object_pos_start":[0.50623,-0.00557,0.03379],"object_to_goal_dist_end":0.07495,"object_to_goal_dist_start":0.07495,"object_z_max":0.03379,"peak_contact_force":0.54361,"phase_name":"insert_2","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":1000.0,"raw_peak_contact_force":0.55216,"tcp_end":[0.46509,-0.06326,0.11119],"tcp_start":[0.40723,-0.03171,0.26215],"tcp_to_object_dist_end":0.10493,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.6214,"average_solve_count":243.0,"average_success_count":243.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"lift_1.speed":0.06692,"push_1.push_distance":0.18387,"push_1.push_speed":0.09747,"retract_1.retract_height":0.12932,"retract_1.speed":0.03952},"optimized_scores":{"best_composite_score":0.13109,"best_fitness_score":0.50109,"best_task_score":0.51446},"replay_outcomes":[{"contacts":{"omitted_contact_groups":2,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":369.0,"contact_point_centroid":[0.53503,-0.01462,0.05999],"force_p95":175.07409,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":224.92841,"mean_force":101.64321,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48972,-0.01034,0.03814]},{"body_a":"attachment","body_b":"channel_right_wall","contact_count":137.0,"contact_point_centroid":[0.47498,-0.04698,0.05206],"force_p95":172.29612,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":180.04647,"mean_force":86.67657,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48548,-0.0469,0.0463]},{"body_a":"attachment","body_b":"peg","contact_count":919.0,"contact_point_centroid":[0.49762,0.00774,0.03568],"force_p95":124.82061,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":142.52948,"mean_force":72.88424,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48958,0.0136,0.03805]},{"body_a":"peg","body_b":"channel_base_body","contact_count":968.0,"contact_point_centroid":[0.50838,-0.00636,0.00953],"force_p95":88.39149,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":109.48218,"mean_force":41.53659,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48957,0.01771,0.03816]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":843.0,"contact_point_centroid":[0.52618,-0.00565,0.02712],"force_p95":96.27426,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":102.95814,"mean_force":59.68727,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48967,0.00784,0.03803]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":5.0,"contact_point_centroid":[0.53353,-0.0496,0.05997],"force_p95":73.92078,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":78.28867,"mean_force":57.69024,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.4877,-0.05335,0.039]},{"body_a":"attachment","body_b":"peg","contact_count":129.0,"contact_point_centroid":[0.49563,-0.05043,0.03766],"force_p95":65.07149,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":69.64775,"mean_force":38.80164,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48576,-0.0499,0.04297]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":135.0,"contact_point_centroid":[0.52607,-0.05528,0.02716],"force_p95":64.92906,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":67.88911,"mean_force":37.36809,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48575,-0.0497,0.04319]},{"body_a":"peg","body_b":"channel_base_body","contact_count":980.0,"contact_point_centroid":[0.49981,-0.06758,0.00825],"force_p95":25.15695,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":46.79708,"mean_force":2.99479,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48654,-0.02756,0.08222]},{"body_a":"peg","body_b":"link7","contact_count":369.0,"contact_point_centroid":[0.51997,0.01098,0.06787],"force_p95":23.04521,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":29.44862,"mean_force":11.33212,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48949,0.03594,0.03789]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":16.0,"contact_point_centroid":[0.47486,-0.09249,0.02461],"force_p95":8.63109,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.20852,"mean_force":2.19747,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48551,-0.04024,0.05464]},{"body_a":"peg","body_b":"channel_base_body","contact_count":973.0,"contact_point_centroid":[0.49527,0.06395,0.00938],"force_p95":0.55699,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.44546,"mean_force":0.55424,"phase_index":0.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.49748,0.13493,0.23568]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":28.0,"contact_point_centroid":[0.47133,0.06388,0.03676],"force_p95":0.92436,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.16907,"mean_force":0.37063,"phase_index":0.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.49942,0.19831,0.29814]},{"body_a":"peg","body_b":"channel_base_body","contact_count":9.0,"contact_point_centroid":[0.49974,-0.10009,0.01263],"force_p95":0.8838,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.09383,"mean_force":0.32118,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48748,-0.05356,0.03922]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.49627,-0.06963,0.00805],"force_p95":0.68341,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.85108,"mean_force":0.60599,"phase_index":4.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44553,-0.02939,0.18876]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.49664,-0.0697,0.00804],"force_p95":0.68341,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.68341,"mean_force":0.60589,"phase_index":5.0,"phase_name":"insert_2","phase_type":"insert","tcp_position_centroid":[0.43468,-0.06005,0.17776]}],"total_contact_groups":18},"final_pose_error":0.07159,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49559,-0.06958,0.02413],"final_tcp_position":[0.46686,-0.07031,0.10271],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48093,0.06388,0.04]},"peak_contact_force":224.92841,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49482,0.06382,0.03401],"object_pos_start":[0.48093,0.06388,0.04],"object_to_goal_dist_end":0.14404,"object_to_goal_dist_start":0.14514,"object_z_max":0.04,"peak_contact_force":0.55002,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":1001.0,"raw_peak_contact_force":2.44546,"tcp_end":[0.49696,0.07528,0.18003],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.14649,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":447.0,"n_steps_budget":930.0,"object_pos_end":[0.49519,0.06359,0.03403],"object_pos_start":[0.49482,0.06382,0.03401],"object_to_goal_dist_end":0.14379,"object_to_goal_dist_start":0.14404,"object_z_max":0.03403,"peak_contact_force":0.54085,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":447.0,"raw_peak_contact_force":0.55403,"tcp_end":[0.4911,0.10042,0.04259],"tcp_start":[0.49696,0.07528,0.18003],"tcp_to_object_dist_end":0.03803,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51094,-0.07444,0.02547],"object_pos_start":[0.49519,0.06359,0.03403],"object_to_goal_dist_end":0.01902,"object_to_goal_dist_start":0.14379,"object_z_max":0.03995,"peak_contact_force":123.43713,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3468.0,"raw_peak_contact_force":224.92841,"tcp_end":[0.48776,-0.05306,0.03898],"tcp_start":[0.4911,0.10042,0.04259],"tcp_to_object_dist_end":0.03431,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49856,-0.06988,0.02414],"object_pos_start":[0.51094,-0.07444,0.02547],"object_to_goal_dist_end":0.01887,"object_to_goal_dist_start":0.01902,"object_z_max":0.03117,"peak_contact_force":0.54626,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1411.0,"raw_peak_contact_force":180.04647,"tcp_end":[0.48871,-0.00863,0.12766],"tcp_start":[0.48776,-0.05306,0.03898],"tcp_to_object_dist_end":0.12069,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49684,-0.06975,0.02413],"object_pos_start":[0.49856,-0.06988,0.02414],"object_to_goal_dist_end":0.01916,"object_to_goal_dist_start":0.01887,"object_z_max":0.0242,"peak_contact_force":0.68341,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":1001.0,"raw_peak_contact_force":0.85108,"tcp_end":[0.40524,-0.05021,0.25423],"tcp_start":[0.48871,-0.00863,0.12766],"tcp_to_object_dist_end":0.24843,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49559,-0.06958,0.02413],"object_pos_start":[0.49684,-0.06975,0.02413],"object_to_goal_dist_end":0.01949,"object_to_goal_dist_start":0.01916,"object_z_max":0.02413,"peak_contact_force":0.60163,"phase_name":"insert_2","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":1000.0,"raw_peak_contact_force":0.68341,"tcp_end":[0.46686,-0.07031,0.10271],"tcp_start":[0.40524,-0.05021,0.25423],"tcp_to_object_dist_end":0.08367,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
```