## Search State

- **Seed**: 0
- **Iteration**: 10 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 9 | align → approach → contact → push → retract | linear_cartesian | arc_cartesian | linear_cartesian | impedance_motion | arc_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 8 | -0.1451 | 0.10 | ❌ rejected |
| 8 | align → approach → contact → push → retract | linear_cartesian | arc_cartesian | linear_cartesian | impedance_motion | arc_cartesian | position_control | force_threshold_switch | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 7 | 0.2569 | 0.80 | ❌ rejected |
| 7 | align → approach → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 8 | -0.0502 | 0.02 | ❌ rejected |
| 6 | align → approach → contact → push → retract | linear_cartesian | arc_cartesian | linear_cartesian | impedance_motion | arc_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 10 | -0.2656 | 0.00 | ❌ rejected |
| 5 | align → approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 8 | -0.3173 | 0.10 | ❌ rejected |

**Proposal policy**: task_score is 0.10 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=-0.145) — your mutation base

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
- id: contact_1
  type: contact
  generator: linear_cartesian
  control: force_threshold_switch
  termination: contact_detected
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

```

## Design Metrics

- **Composite score**: -0.145
- **task_score** (E): 0.103
- **fitness_score**: 0.212  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.133
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.490

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| align_1 | 1.00 | 1.00 | 0.0162 |
| approach_1 | 1.00 | 1.00 | 0.2379 |
| contact_1 | 1.00 | 1.00 | 0.0358 |
| push_1 | 0.00 | 1.00 | 0.0005 |
| retract_1 | 1.00 | 1.00 | 0.2680 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| align_1 | align | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.497, 0.188, 0.294) | (0.498, 0.080, 0.040)→(0.500, 0.081, 0.033) | 0.161→0.161 | 1.00 / 1.000 | 0.788 | 2.179 |
| approach_1 | approach | 1.00 / step_budget | (0.497, 0.188, 0.294)→(0.497, 0.119, 0.066) | (0.500, 0.081, 0.033)→(0.500, 0.080, 0.034) | 0.161→0.161 | 1.00 / 1.000 | 0.535 | 0.873 |
| contact_1 | contact | 1.00 / force_exceeded | (0.497, 0.119, 0.066)→(0.495, 0.094, 0.041) | (0.500, 0.080, 0.034)→(0.505, 0.066, 0.036) | 0.161→0.146 | 1.00 / 2.667 | 90.748 | 9.452 |
| push_1 | push | 0.00 / guard_failure | (0.487, 0.098, 0.030)→(0.487, 0.099, 0.030) | (0.505, 0.066, 0.036)→(0.504, 0.066, 0.035) | 0.146→0.146 | 1.00 / 2.000 | 332.246 | 563.958 |
| retract_1 | retract | 1.00 / step_budget | (0.487, 0.099, 0.030)→(0.499, 0.231, 0.261) | (0.504, 0.066, 0.035)→(0.504, 0.065, 0.034) | 0.147→0.146 | 1.00 / 1.000 | 0.548 | 337.191 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.102
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.102
- phase_score: 0.292
- phase_breakdown.approach_score: 0.586
- phase_breakdown.push_score: 0.014
- phase_breakdown.contact_score: 0.832

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.228
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.160
- **Median Q (composite search score)**: -0.099
- **K-run variance**: 0.0069
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.241


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.37302,"average_solve_count":126.0,"average_success_count":126.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.alignment_speed":0.09416,"align_1.lateral_offset_x":-0.00202,"approach_1.approach_height":0.12116,"contact_1.contact_force":21.76543,"push_1.push_distance":0.15909,"push_1.push_speed":0.0608,"retract_1.retract_height":0.18022,"retract_1.speed":0.1845},"optimized_scores":{"best_composite_score":-0.26203,"best_fitness_score":0.22797,"best_task_score":0.16031},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":2.0,"contact_point_centroid":[0.555,0.05325,0.05999],"force_p95":660.05284,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":682.96707,"mean_force":453.82483,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48841,0.07855,0.02787]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":23.0,"contact_point_centroid":[0.555,0.0731,0.05998],"force_p95":276.81438,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":304.04904,"mean_force":216.67271,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49239,0.08341,0.02662]},{"body_a":"attachment","body_b":"peg","contact_count":16.0,"contact_point_centroid":[0.5016,0.06159,0.06084],"force_p95":143.00921,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":175.40832,"mean_force":42.96461,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.4903,0.07321,0.02729]},{"body_a":"peg","body_b":"channel_base_body","contact_count":375.0,"contact_point_centroid":[0.50651,0.04695,0.00943],"force_p95":0.72821,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":119.50713,"mean_force":1.78005,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49287,0.19405,0.10348]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":56.0,"contact_point_centroid":[0.52526,0.04699,0.05936],"force_p95":47.60115,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":91.37865,"mean_force":8.51191,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.4912,0.10911,0.03077]},{"body_a":"peg","body_b":"channel_base_body","contact_count":256.0,"contact_point_centroid":[0.50545,0.04621,0.00974],"force_p95":8.00053,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.49168,"mean_force":3.73539,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49861,0.08716,0.05136]},{"body_a":"attachment","body_b":"peg","contact_count":158.0,"contact_point_centroid":[0.50112,0.07134,0.04679],"force_p95":7.93239,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":9.17045,"mean_force":5.35194,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49835,0.08297,0.04707]},{"body_a":"peg","body_b":"channel_base_body","contact_count":34.0,"contact_point_centroid":[0.50172,0.06163,0.00893],"force_p95":1.67745,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.17216,"mean_force":0.79867,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.50178,0.18733,0.29419]},{"body_a":"peg","body_b":"channel_base_body","contact_count":34.0,"contact_point_centroid":[0.50699,0.04722,0.00968],"force_p95":0.79102,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.91374,"mean_force":0.58195,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49153,0.08253,0.03211]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":19.0,"contact_point_centroid":[0.52623,0.06158,0.03217],"force_p95":0.5921,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.62339,"mean_force":0.34148,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49984,0.19836,0.2993]},{"body_a":"peg","body_b":"channel_base_body","contact_count":666.0,"contact_point_centroid":[0.50377,0.0616,0.00937],"force_p95":0.60072,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.60566,"mean_force":0.54594,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.5013,0.19976,0.15219]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":5.0,"contact_point_centroid":[0.52503,0.04989,0.01118],"force_p95":0.35745,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.3587,"mean_force":0.32807,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49872,0.07829,0.04164]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.50193,0.06571,0.04159],"force_p95":0.0,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49871,0.07723,0.04214]}],"total_contact_groups":13},"final_pose_error":0.04935,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50659,0.04798,0.03387],"final_tcp_position":[0.49959,0.22606,0.2581],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.51096,0.06158,0.04]},"peak_contact_force":682.96707,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":57.0,"n_steps_budget":600.0,"object_pos_end":[0.50382,0.06157,0.03324],"object_pos_start":[0.51096,0.06158,0.04],"object_to_goal_dist_end":0.14178,"object_to_goal_dist_start":0.14201,"object_z_max":0.04,"peak_contact_force":0.52199,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":53.0,"raw_peak_contact_force":2.17216,"subtask_id":"approach","tcp_end":[0.50318,0.18037,0.29151],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.28428,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":666.0,"n_steps_budget":1000.0,"object_pos_end":[0.50378,0.06159,0.03376],"object_pos_start":[0.50382,0.06157,0.03324],"object_to_goal_dist_end":0.14178,"object_to_goal_dist_start":0.14178,"object_z_max":0.03377,"peak_contact_force":0.52886,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":666.0,"raw_peak_contact_force":0.60566,"subtask_id":"contact","tcp_end":[0.50053,0.09886,0.06417],"tcp_start":[0.50318,0.18037,0.29151],"tcp_to_object_dist_end":0.04821,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":267.0,"n_steps_budget":600.0,"object_pos_end":[0.5068,0.04868,0.03598],"object_pos_start":[0.50378,0.06159,0.03376],"object_to_goal_dist_end":0.12892,"object_to_goal_dist_start":0.14178,"object_z_max":0.0367,"peak_contact_force":67.62331,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":414.0,"raw_peak_contact_force":9.49168,"subtask_id":"contact","tcp_end":[0.49871,0.07723,0.04214],"tcp_start":[0.50053,0.09886,0.06417],"tcp_to_object_dist_end":0.0303,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":39.0,"n_steps_budget":1000.0,"object_pos_end":[0.50645,0.04883,0.03408],"object_pos_start":[0.5068,0.04868,0.03598],"object_to_goal_dist_end":0.12913,"object_to_goal_dist_start":0.12892,"object_z_max":0.036,"peak_contact_force":1.42841,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":42.0,"raw_peak_contact_force":682.96707,"subtask_id":"push","tcp_end":[0.48874,0.07823,0.02821],"tcp_start":[0.48849,0.07816,0.02803],"tcp_to_object_dist_end":0.03482,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":375.0,"n_steps_budget":1000.0,"object_pos_end":[0.50659,0.04798,0.03387],"object_pos_start":[0.50639,0.04884,0.03408],"object_to_goal_dist_end":0.1283,"object_to_goal_dist_start":0.12913,"object_z_max":0.03533,"peak_contact_force":0.55055,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":470.0,"raw_peak_contact_force":304.04904,"tcp_end":[0.49959,0.22606,0.2581],"tcp_start":[0.48874,0.07823,0.02821],"tcp_to_object_dist_end":0.28642,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.22308,"average_solve_count":130.0,"average_success_count":130.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.alignment_speed":0.18627,"align_1.lateral_offset_x":-0.0019,"approach_1.approach_height":0.11557,"contact_1.contact_force":13.22799,"push_1.push_distance":0.09687,"push_1.push_speed":0.02634,"retract_1.retract_height":0.12313,"retract_1.speed":0.16352},"optimized_scores":{"best_composite_score":-0.07414,"best_fitness_score":0.21586,"best_task_score":0.10154},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":3.0,"contact_point_centroid":[0.53734,0.10965,0.05978],"force_p95":817.5223,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":830.84135,"mean_force":575.30706,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48602,0.13259,0.02712]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":3.0,"contact_point_centroid":[0.555,0.09118,0.05975],"force_p95":332.13871,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":344.51053,"mean_force":236.22382,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48603,0.13175,0.02741]},{"body_a":"peg","body_b":"link7","contact_count":17.0,"contact_point_centroid":[0.51983,0.10337,0.06228],"force_p95":39.77627,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":40.03494,"mean_force":16.04808,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49155,0.12537,0.02746]},{"body_a":"peg","body_b":"channel_base_body","contact_count":366.0,"contact_point_centroid":[0.50523,0.10049,0.00944],"force_p95":1.14414,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":39.00826,"mean_force":1.45584,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.4912,0.23006,0.11383]},{"body_a":"attachment","body_b":"peg","contact_count":11.0,"contact_point_centroid":[0.49787,0.11395,0.03524],"force_p95":30.73742,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":37.62948,"mean_force":7.08687,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49025,0.12455,0.02787]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":46.0,"contact_point_centroid":[0.52533,0.09926,0.05944],"force_p95":31.50887,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":33.67358,"mean_force":5.37413,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48918,0.18504,0.05181]},{"body_a":"peg","body_b":"channel_base_body","contact_count":292.0,"contact_point_centroid":[0.50305,0.09938,0.00975],"force_p95":8.42356,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.09532,"mean_force":3.86805,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49589,0.14029,0.05117]},{"body_a":"attachment","body_b":"peg","contact_count":182.0,"contact_point_centroid":[0.49856,0.12432,0.04669],"force_p95":8.33059,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":8.75683,"mean_force":5.50368,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.4957,0.13594,0.04673]},{"body_a":"peg","body_b":"channel_base_body","contact_count":4.0,"contact_point_centroid":[0.49811,0.11606,0.00947],"force_p95":1.88436,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.92055,"mean_force":1.64822,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49947,0.20106,0.29793]},{"body_a":"peg","body_b":"channel_base_body","contact_count":638.0,"contact_point_centroid":[0.50093,0.11601,0.00937],"force_p95":0.62093,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.32691,"mean_force":0.54972,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49815,0.23959,0.16748]},{"body_a":"peg","body_b":"channel_base_body","contact_count":28.0,"contact_point_centroid":[0.50826,0.09889,0.0097],"force_p95":0.86162,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.93733,"mean_force":0.53581,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49059,0.1337,0.033]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":11.0,"contact_point_centroid":[0.52515,0.09955,0.05977],"force_p95":0.18882,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.21034,"mean_force":0.0762,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49468,0.13199,0.03787]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.50121,0.11676,0.0485],"force_p95":0.0,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49618,0.12816,0.03995]}],"total_contact_groups":13},"final_pose_error":0.04974,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50512,0.09979,0.03424],"final_tcp_position":[0.49929,0.2343,0.26398],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50095,0.11604,0.04]},"peak_contact_force":830.84135,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":20.0,"n_steps_budget":600.0,"object_pos_end":[0.50096,0.11615,0.03303],"object_pos_start":[0.50095,0.11604,0.04],"object_to_goal_dist_end":0.19627,"object_to_goal_dist_start":0.19604,"object_z_max":0.04,"peak_contact_force":1.4131,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":4.0,"raw_peak_contact_force":1.92055,"subtask_id":"approach","tcp_end":[0.49942,0.20161,0.29738],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.27782,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":638.0,"n_steps_budget":1000.0,"object_pos_end":[0.50097,0.11611,0.03388],"object_pos_start":[0.50096,0.11615,0.03303],"object_to_goal_dist_end":0.19621,"object_to_goal_dist_start":0.19627,"object_z_max":0.03405,"peak_contact_force":0.53134,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":638.0,"raw_peak_contact_force":1.32691,"subtask_id":"contact","tcp_end":[0.49773,0.15447,0.06647],"tcp_start":[0.49942,0.20161,0.29738],"tcp_to_object_dist_end":0.05043,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":310.0,"n_steps_budget":600.0,"object_pos_end":[0.50633,0.10018,0.03549],"object_pos_start":[0.50097,0.11611,0.03388],"object_to_goal_dist_end":0.18035,"object_to_goal_dist_start":0.19621,"object_z_max":0.03699,"peak_contact_force":187.54958,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":474.0,"raw_peak_contact_force":9.09532,"subtask_id":"contact","tcp_end":[0.49618,0.12816,0.03995],"tcp_start":[0.49773,0.15447,0.06647],"tcp_to_object_dist_end":0.03009,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":28.0,"n_steps_budget":1000.0,"object_pos_end":[0.50491,0.10151,0.03443],"object_pos_start":[0.50633,0.10018,0.03549],"object_to_goal_dist_end":0.18166,"object_to_goal_dist_start":0.18035,"object_z_max":0.03549,"peak_contact_force":830.84135,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":43.0,"raw_peak_contact_force":830.84135,"subtask_id":"push","tcp_end":[0.48591,0.13215,0.02719],"tcp_start":[0.48591,0.13231,0.02701],"tcp_to_object_dist_end":0.03678,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":366.0,"n_steps_budget":1000.0,"object_pos_end":[0.50512,0.09979,0.03424],"object_pos_start":[0.50498,0.10144,0.03441],"object_to_goal_dist_end":0.17996,"object_to_goal_dist_start":0.18159,"object_z_max":0.03824,"peak_contact_force":0.54605,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":443.0,"raw_peak_contact_force":344.51053,"tcp_end":[0.49929,0.2343,0.26398],"tcp_start":[0.48591,0.13215,0.02719],"tcp_to_object_dist_end":0.26628,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.08088,"average_solve_count":136.0,"average_success_count":136.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.alignment_speed":0.13413,"align_1.lateral_offset_x":-0.00234,"approach_1.approach_height":0.14925,"contact_1.contact_force":14.39557,"push_1.push_distance":0.11277,"push_1.push_speed":0.06264,"retract_1.retract_height":0.13921,"retract_1.speed":0.13978},"optimized_scores":{"best_composite_score":-0.09906,"best_fitness_score":0.19094,"best_task_score":0.04808},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":24.0,"contact_point_centroid":[0.52632,0.08725,0.05997],"force_p95":354.68648,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":363.01286,"mean_force":273.88159,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48991,0.09911,0.02644]},{"body_a":"attachment","body_b":"channel_right_wall","contact_count":2.0,"contact_point_centroid":[0.47488,0.08536,0.0353],"force_p95":180.95982,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":181.79123,"mean_force":173.47711,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48655,0.08547,0.03308]},{"body_a":"attachment","body_b":"channel_right_wall","contact_count":3.0,"contact_point_centroid":[0.47482,0.08399,0.0367],"force_p95":176.70616,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":178.06588,"mean_force":152.05825,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48645,0.08406,0.03455]},{"body_a":"peg","body_b":"channel_base_body","contact_count":314.0,"contact_point_centroid":[0.49745,0.04772,0.00975],"force_p95":8.31224,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.76923,"mean_force":3.71961,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.48989,0.08832,0.05257]},{"body_a":"attachment","body_b":"peg","contact_count":186.0,"contact_point_centroid":[0.49274,0.07175,0.04702],"force_p95":8.50727,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":9.4368,"mean_force":5.53989,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.48979,0.08332,0.04736]},{"body_a":"peg","body_b":"channel_base_body","contact_count":30.0,"contact_point_centroid":[0.49863,0.06347,0.00906],"force_p95":1.93074,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.44546,"mean_force":0.82717,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49146,0.18702,0.29387]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":28.0,"contact_point_centroid":[0.47133,0.06388,0.03676],"force_p95":0.92436,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.16907,"mean_force":0.37063,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49769,0.19689,0.29845]},{"body_a":"peg","body_b":"channel_base_body","contact_count":411.0,"contact_point_centroid":[0.49988,0.04923,0.00945],"force_p95":0.56926,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.70367,"mean_force":0.54578,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49075,0.20913,0.10405]},{"body_a":"peg","body_b":"channel_base_body","contact_count":602.0,"contact_point_centroid":[0.49513,0.06397,0.00939],"force_p95":0.55725,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.68508,"mean_force":0.54567,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.4899,0.19043,0.16012]},{"body_a":"peg","body_b":"channel_base_body","contact_count":13.0,"contact_point_centroid":[0.51135,0.03589,0.00991],"force_p95":0.54421,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55603,"mean_force":0.49946,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48871,0.08028,0.03762]},{"body_a":"attachment","body_b":"peg","contact_count":6.0,"contact_point_centroid":[0.49575,0.06747,0.05913],"force_p95":0.04236,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.05647,"mean_force":0.00941,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48754,0.08084,0.02809]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.49528,0.0642,0.04899],"force_p95":0.0,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49028,0.07565,0.04039]}],"total_contact_groups":12},"final_pose_error":0.04939,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49991,0.0484,0.0342],"final_tcp_position":[0.49881,0.232,0.2624],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48093,0.06388,0.04]},"peak_contact_force":363.01286,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":57.0,"n_steps_budget":600.0,"object_pos_end":[0.49503,0.06379,0.03359],"object_pos_start":[0.48093,0.06388,0.04],"object_to_goal_dist_end":0.14402,"object_to_goal_dist_start":0.14514,"object_z_max":0.04,"peak_contact_force":0.42772,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":58.0,"raw_peak_contact_force":2.44546,"subtask_id":"approach","tcp_end":[0.48796,0.18124,0.29162],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.28359,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":602.0,"n_steps_budget":1000.0,"object_pos_end":[0.49497,0.06368,0.03396],"object_pos_start":[0.49503,0.06379,0.03359],"object_to_goal_dist_end":0.14389,"object_to_goal_dist_start":0.14402,"object_z_max":0.03396,"peak_contact_force":0.54392,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":602.0,"raw_peak_contact_force":0.68508,"subtask_id":"contact","tcp_end":[0.49177,0.10254,0.06852],"tcp_start":[0.48796,0.18124,0.29162],"tcp_to_object_dist_end":0.05211,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":332.0,"n_steps_budget":600.0,"object_pos_end":[0.50047,0.04766,0.03584],"object_pos_start":[0.49497,0.06368,0.03396],"object_to_goal_dist_end":0.12773,"object_to_goal_dist_start":0.14389,"object_z_max":0.03714,"peak_contact_force":17.07033,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":500.0,"raw_peak_contact_force":9.76923,"subtask_id":"contact","tcp_end":[0.49028,0.07565,0.04039],"tcp_start":[0.49177,0.10254,0.06852],"tcp_to_object_dist_end":0.03013,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":13.0,"n_steps_budget":1000.0,"object_pos_end":[0.50087,0.0485,0.03526],"object_pos_start":[0.50047,0.04766,0.03584],"object_to_goal_dist_end":0.12859,"object_to_goal_dist_start":0.12773,"object_z_max":0.03584,"peak_contact_force":164.46876,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":17.0,"raw_peak_contact_force":178.06588,"subtask_id":"push","tcp_end":[0.48642,0.08522,0.03334],"tcp_start":[0.48622,0.08452,0.03394],"tcp_to_object_dist_end":0.03951,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":411.0,"n_steps_budget":1000.0,"object_pos_end":[0.49991,0.0484,0.0342],"object_pos_start":[0.50078,0.04879,0.03511],"object_to_goal_dist_end":0.12854,"object_to_goal_dist_start":0.12888,"object_z_max":0.03511,"peak_contact_force":0.54714,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":443.0,"raw_peak_contact_force":363.01286,"tcp_end":[0.49881,0.232,0.2624],"tcp_start":[0.48642,0.08522,0.03334],"tcp_to_object_dist_end":0.29289,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```