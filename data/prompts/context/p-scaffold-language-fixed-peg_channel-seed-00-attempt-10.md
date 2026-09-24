## Search State

- **Seed**: 0
- **Iteration**: 11 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 10 | approach → approach → contact → push → retract | linear_cartesian | arc_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | position_control | force_threshold_switch | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 12 | -0.2603 | 0.08 | ❌ rejected |
| 9 | align → approach → contact → push → retract | linear_cartesian | arc_cartesian | linear_cartesian | impedance_motion | arc_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 8 | -0.1451 | 0.10 | ❌ rejected |
| 8 | align → approach → contact → push → retract | linear_cartesian | arc_cartesian | linear_cartesian | impedance_motion | arc_cartesian | position_control | force_threshold_switch | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 7 | 0.2569 | 0.80 | ❌ rejected |
| 7 | align → approach → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 8 | -0.0502 | 0.02 | ❌ rejected |
| 6 | align → approach → contact → push → retract | linear_cartesian | arc_cartesian | linear_cartesian | impedance_motion | arc_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 10 | -0.2656 | 0.00 | ❌ rejected |

**Proposal policy**: task_score is 0.08 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=-0.260) — your mutation base

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

- **Composite score**: -0.260
- **task_score** (E): 0.075
- **fitness_score**: 0.230  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.200
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.690

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| align_1 | 1.00 | 1.00 | 0.2528 |
| approach_1 | 1.00 | 1.00 | 0.0295 |
| contact_1 | 1.00 | 1.00 | 0.0010 |
| push_1 | 0.00 | 1.00 | 0.0001 |
| retract_1 | 1.00 | 1.00 | 0.2507 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| align_1 | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.497, 0.127, 0.060) | (0.498, 0.080, 0.040)→(0.500, 0.081, 0.034) | 0.161→0.161 | 1.00 / 1.667 | 166.691 | 219.573 |
| approach_1 | approach | 1.00 / step_budget | (0.497, 0.127, 0.060)→(0.496, 0.107, 0.040) | (0.500, 0.081, 0.034)→(0.500, 0.077, 0.036) | 0.161→0.157 | 1.00 / 1.333 | 32.921 | 121.187 |
| contact_1 | contact | 1.00 / force_exceeded | (0.496, 0.107, 0.040)→(0.496, 0.106, 0.039) | (0.500, 0.077, 0.036)→(0.500, 0.075, 0.036) | 0.157→0.156 | 1.00 / 2.000 | 44.205 | 19.701 |
| push_1 | push | 0.00 / guard_failure | (0.494, 0.100, 0.037)→(0.494, 0.100, 0.037) | (0.500, 0.075, 0.036)→(0.499, 0.070, 0.036) | 0.156→0.150 | 1.00 / 2.000 | 97.387 | 99.272 |
| retract_1 | retract | 1.00 / step_budget | (0.494, 0.100, 0.037)→(0.499, 0.220, 0.255) | (0.499, 0.069, 0.036)→(0.499, 0.067, 0.034) | 0.149→0.148 | 1.00 / 1.000 | 0.544 | 316.090 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.114
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.114
- phase_score: 0.334
- phase_breakdown.approach_score: 0.763
- phase_breakdown.push_score: 0.015
- phase_breakdown.contact_score: 0.863

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.246
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.114
- **Median Q (composite search score)**: -0.261
- **K-run variance**: 0.0002
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.324


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.24561,"average_solve_count":114.0,"average_success_count":114.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.approach_speed":0.16986,"align_1.lateral_offset_x":0.0087,"approach_1.approach_height":0.06427,"approach_1.approach_speed":0.07091,"contact_1.contact_force":9.61164,"push_1.push_distance":0.18412,"push_1.push_force_limit":42.10601,"push_1.push_speed":0.04703,"push_1.push_tolerance":0.01741,"push_1.retry_offset_x":0.00861,"retract_1.retract_height":0.20223,"retract_1.retract_speed":0.1277},"optimized_scores":{"best_composite_score":-0.26097,"best_fitness_score":0.22903,"best_task_score":0.07615},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_left_wall","contact_count":27.0,"contact_point_centroid":[0.52554,0.11091,0.05978],"force_p95":454.86087,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":473.54653,"mean_force":360.8324,"phase_index":0.0,"phase_name":"align_1","phase_type":"approach","tcp_position_centroid":[0.51406,0.11091,0.06194]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":6.0,"contact_point_centroid":[0.54531,0.08053,0.05995],"force_p95":376.30998,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":379.20995,"mean_force":273.55043,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49996,0.08061,0.03752]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":4.0,"contact_point_centroid":[0.54532,0.08098,0.05997],"force_p95":102.57471,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":102.77935,"mean_force":72.74036,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49998,0.08103,0.03756]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":6.0,"contact_point_centroid":[0.52507,0.10655,0.05997],"force_p95":97.94738,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":98.55374,"mean_force":58.95081,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51104,0.1065,0.05806]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":1.0,"contact_point_centroid":[0.525,0.08804,0.06],"force_p95":28.6338,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":28.6338,"mean_force":28.6338,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50222,0.08784,0.04046]},{"body_a":"peg","body_b":"channel_base_body","contact_count":114.0,"contact_point_centroid":[0.50412,0.0602,0.00941],"force_p95":5.14916,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":20.78397,"mean_force":1.32486,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50726,0.09964,0.05299]},{"body_a":"attachment","body_b":"peg","contact_count":13.0,"contact_point_centroid":[0.50391,0.07781,0.04519],"force_p95":18.47257,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":20.28443,"mean_force":7.15691,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50312,0.08973,0.04336]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":3.0,"contact_point_centroid":[0.52502,0.08823,0.05999],"force_p95":16.7029,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":18.55877,"mean_force":6.18626,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50242,0.08804,0.04075]},{"body_a":"peg","body_b":"channel_base_body","contact_count":37.0,"contact_point_centroid":[0.50288,0.04762,0.00962],"force_p95":10.53845,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":13.85933,"mean_force":2.36909,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50093,0.08488,0.03885]},{"body_a":"attachment","body_b":"peg","contact_count":19.0,"contact_point_centroid":[0.50302,0.07094,0.04302],"force_p95":11.11071,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":12.98899,"mean_force":3.74612,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50026,0.08251,0.03796]},{"body_a":"peg","body_b":"channel_base_body","contact_count":456.0,"contact_point_centroid":[0.50356,0.06161,0.00934],"force_p95":0.60263,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.17216,"mean_force":0.56413,"phase_index":0.0,"phase_name":"align_1","phase_type":"approach","tcp_position_centroid":[0.50715,0.15181,0.17015]},{"body_a":"peg","body_b":"channel_base_body","contact_count":332.0,"contact_point_centroid":[0.50457,0.04835,0.00943],"force_p95":0.61422,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.93454,"mean_force":0.54609,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49888,0.19153,0.11802]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":19.0,"contact_point_centroid":[0.52623,0.06158,0.03217],"force_p95":0.5921,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.62339,"mean_force":0.34148,"phase_index":0.0,"phase_name":"align_1","phase_type":"approach","tcp_position_centroid":[0.49994,0.19882,0.29721]},{"body_a":"peg","body_b":"channel_base_body","contact_count":3.0,"contact_point_centroid":[0.50466,0.07417,0.00984],"force_p95":0.31779,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.31925,"mean_force":0.30415,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50242,0.08804,0.04075]},{"body_a":"attachment","body_b":"peg","contact_count":2.0,"contact_point_centroid":[0.50375,0.06878,0.04552],"force_p95":0.03101,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.03264,"mean_force":0.01632,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49993,0.08068,0.0375]}],"total_contact_groups":15},"final_pose_error":0.04908,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50479,0.04867,0.03395],"final_tcp_position":[0.49986,0.22138,0.25582],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.51096,0.06158,0.04]},"peak_contact_force":473.54653,"phases":[{"contact_detected":true,"contact_event_count":2.0,"n_steps":479.0,"n_steps_budget":1000.0,"object_pos_end":[0.50377,0.0616,0.03378],"object_pos_start":[0.51096,0.06158,0.04],"object_to_goal_dist_end":0.14178,"object_to_goal_dist_start":0.14201,"object_z_max":0.04,"peak_contact_force":316.31414,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":502.0,"raw_peak_contact_force":473.54653,"subtask_id":"approach","tcp_end":[0.51298,0.11026,0.06156],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.05679,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":118.0,"n_steps_budget":600.0,"object_pos_end":[0.50383,0.05738,0.03542],"object_pos_start":[0.50377,0.0616,0.03378],"object_to_goal_dist_end":0.13751,"object_to_goal_dist_start":0.14178,"object_z_max":0.03557,"peak_contact_force":98.55374,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":133.0,"raw_peak_contact_force":98.55374,"subtask_id":"contact","tcp_end":[0.50252,0.08815,0.04091],"tcp_start":[0.51298,0.11026,0.06156],"tcp_to_object_dist_end":0.03128,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":3.0,"n_steps_budget":600.0,"object_pos_end":[0.50382,0.05661,0.03511],"object_pos_start":[0.50383,0.05738,0.03542],"object_to_goal_dist_end":0.13675,"object_to_goal_dist_start":0.13751,"object_z_max":0.03542,"peak_contact_force":18.55877,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":6.0,"raw_peak_contact_force":18.55877,"subtask_id":"contact","tcp_end":[0.50222,0.08784,0.04046],"tcp_start":[0.50252,0.08815,0.04091],"tcp_to_object_dist_end":0.03173,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":40.0,"n_steps_budget":1000.0,"object_pos_end":[0.50353,0.05134,0.03522],"object_pos_start":[0.50382,0.05661,0.03511],"object_to_goal_dist_end":0.13148,"object_to_goal_dist_start":0.13675,"object_z_max":0.03527,"peak_contact_force":101.41513,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":61.0,"raw_peak_contact_force":102.77935,"tcp_end":[0.49994,0.08072,0.03751],"tcp_start":[0.49995,0.08082,0.03752],"tcp_to_object_dist_end":0.02968,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":333.0,"n_steps_budget":1000.0,"object_pos_end":[0.50479,0.04867,0.03395],"object_pos_start":[0.50368,0.05082,0.03529],"object_to_goal_dist_end":0.1289,"object_to_goal_dist_start":0.13095,"object_z_max":0.03529,"peak_contact_force":0.54462,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":340.0,"raw_peak_contact_force":379.20995,"tcp_end":[0.49986,0.22138,0.25582],"tcp_start":[0.49994,0.08072,0.03751],"tcp_to_object_dist_end":0.28121,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.06604,"average_solve_count":106.0,"average_success_count":106.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.approach_speed":0.21184,"align_1.lateral_offset_x":0.00429,"approach_1.approach_height":0.09633,"approach_1.approach_speed":0.09579,"contact_1.contact_force":10.70882,"push_1.push_distance":0.1021,"push_1.push_force_limit":39.51574,"push_1.push_speed":0.04074,"push_1.push_tolerance":0.01574,"push_1.retry_offset_x":0.0044,"retract_1.retract_height":0.0656,"retract_1.retract_speed":0.13499},"optimized_scores":{"best_composite_score":-0.244,"best_fitness_score":0.246,"best_task_score":0.11366},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":4.0,"contact_point_centroid":[0.54235,0.12,0.05996],"force_p95":133.8825,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":134.52604,"mean_force":86.14494,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49475,0.13001,0.03544]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":5.0,"contact_point_centroid":[0.54223,0.12,0.05995],"force_p95":116.68396,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":126.42453,"mean_force":83.23899,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49474,0.12955,0.03544]},{"body_a":"peg","body_b":"channel_base_body","contact_count":85.0,"contact_point_centroid":[0.50134,0.11342,0.00945],"force_p95":11.68012,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":19.70705,"mean_force":1.5807,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.4988,0.15142,0.04995]},{"body_a":"attachment","body_b":"peg","contact_count":11.0,"contact_point_centroid":[0.50054,0.13233,0.04668],"force_p95":17.91198,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":19.32129,"mean_force":8.28918,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.4978,0.14417,0.04185]},{"body_a":"peg","body_b":"channel_base_body","contact_count":50.0,"contact_point_centroid":[0.50549,0.09964,0.00952],"force_p95":9.91395,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":12.95413,"mean_force":1.99127,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49586,0.13799,0.03741]},{"body_a":"attachment","body_b":"peg","contact_count":21.0,"contact_point_centroid":[0.50069,0.12207,0.04318],"force_p95":10.52904,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":12.43609,"mean_force":3.59171,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49515,0.13367,0.0362]},{"body_a":"peg","body_b":"channel_base_body","contact_count":404.0,"contact_point_centroid":[0.50091,0.11598,0.00935],"force_p95":0.61968,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.92055,"mean_force":0.56446,"phase_index":0.0,"phase_name":"align_1","phase_type":"approach","tcp_position_centroid":[0.50027,0.17893,0.17624]},{"body_a":"peg","body_b":"channel_base_body","contact_count":271.0,"contact_point_centroid":[0.50021,0.09782,0.00938],"force_p95":0.70549,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.76341,"mean_force":0.56965,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49575,0.19953,0.13151]},{"body_a":"attachment","body_b":"peg","contact_count":4.0,"contact_point_centroid":[0.50298,0.13096,0.05435],"force_p95":0.43169,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.49055,"mean_force":0.18173,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49755,0.14271,0.03986]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":10.0,"contact_point_centroid":[0.52512,0.10587,0.05875],"force_p95":0.2062,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24666,"mean_force":0.06251,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.4956,0.13738,0.03705]}],"total_contact_groups":10},"final_pose_error":0.04936,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50054,0.09785,0.03392],"final_tcp_position":[0.49899,0.21583,0.25326],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50095,0.11604,0.04]},"peak_contact_force":134.52604,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":420.0,"n_steps_budget":780.0,"object_pos_end":[0.50096,0.11602,0.03397],"object_pos_start":[0.50095,0.11604,0.04],"object_to_goal_dist_end":0.19611,"object_to_goal_dist_start":0.19604,"object_z_max":0.04,"peak_contact_force":0.50712,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":404.0,"raw_peak_contact_force":1.92055,"subtask_id":"approach","tcp_end":[0.50146,0.15912,0.05928],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.04999,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":89.0,"n_steps_budget":600.0,"object_pos_end":[0.50219,0.11289,0.0361],"object_pos_start":[0.50096,0.11602,0.03397],"object_to_goal_dist_end":0.19294,"object_to_goal_dist_start":0.19611,"object_z_max":0.03603,"peak_contact_force":0.07359,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":96.0,"raw_peak_contact_force":19.70705,"subtask_id":"contact","tcp_end":[0.4977,0.14291,0.0401],"tcp_start":[0.50146,0.15912,0.05928],"tcp_to_object_dist_end":0.03062,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":4.0,"n_steps_budget":600.0,"object_pos_end":[0.50258,0.11157,0.03602],"object_pos_start":[0.50219,0.11289,0.0361],"object_to_goal_dist_end":0.19163,"object_to_goal_dist_start":0.19294,"object_z_max":0.03613,"peak_contact_force":14.34143,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":4.0,"raw_peak_contact_force":0.49055,"subtask_id":"contact","tcp_end":[0.49733,0.14244,0.0395],"tcp_start":[0.4977,0.14291,0.0401],"tcp_to_object_dist_end":0.03151,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":66.0,"n_steps_budget":1000.0,"object_pos_end":[0.5016,0.09995,0.03731],"object_pos_start":[0.50258,0.11157,0.03602],"object_to_goal_dist_end":0.17998,"object_to_goal_dist_start":0.19163,"object_z_max":0.03813,"peak_contact_force":130.23573,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":85.0,"raw_peak_contact_force":134.52604,"tcp_end":[0.49474,0.12967,0.03542],"tcp_start":[0.49475,0.12978,0.03542],"tcp_to_object_dist_end":0.03056,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":274.0,"n_steps_budget":1000.0,"object_pos_end":[0.50054,0.09785,0.03392],"object_pos_start":[0.50138,0.09934,0.03674],"object_to_goal_dist_end":0.17796,"object_to_goal_dist_start":0.17938,"object_z_max":0.03674,"peak_contact_force":0.54825,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":276.0,"raw_peak_contact_force":126.42453,"tcp_end":[0.49899,0.21583,0.25326],"tcp_start":[0.49474,0.12967,0.03542],"tcp_to_object_dist_end":0.24906,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.83186,"average_solve_count":113.0,"average_success_count":113.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.approach_speed":0.12473,"align_1.lateral_offset_x":-0.0019,"approach_1.approach_height":0.08962,"approach_1.approach_speed":0.06767,"contact_1.contact_force":7.01868,"push_1.push_distance":0.10081,"push_1.push_force_limit":43.32254,"push_1.push_speed":0.0476,"push_1.push_tolerance":0.01414,"push_1.retry_offset_x":0.00548,"retract_1.retract_height":0.18941,"retract_1.retract_speed":0.17214},"optimized_scores":{"best_composite_score":-0.27605,"best_fitness_score":0.21395,"best_task_score":0.03637},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":7.0,"contact_point_centroid":[0.53323,0.08926,0.05983],"force_p95":442.46277,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":442.63445,"mean_force":331.08247,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48791,0.08868,0.03723]},{"body_a":"attachment","body_b":"channel_right_wall","contact_count":73.0,"contact_point_centroid":[0.47493,0.11544,0.05986],"force_p95":243.36926,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":245.30167,"mean_force":169.09846,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48168,0.1074,0.05652]},{"body_a":"attachment","body_b":"channel_right_wall","contact_count":1.0,"contact_point_centroid":[0.47491,0.12,0.05982],"force_p95":183.25236,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":183.25236,"mean_force":183.25236,"phase_index":0.0,"phase_name":"align_1","phase_type":"approach","tcp_position_centroid":[0.4776,0.11163,0.05842]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":5.0,"contact_point_centroid":[0.5332,0.08934,0.05986],"force_p95":59.39918,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":60.51043,"mean_force":46.31489,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48788,0.08874,0.0373]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.53328,0.08954,0.05997],"force_p95":40.05409,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":40.05409,"mean_force":40.05409,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.48797,0.08894,0.03749]},{"body_a":"peg","body_b":"channel_base_body","contact_count":174.0,"contact_point_centroid":[0.49533,0.06189,0.00939],"force_p95":0.80813,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":16.53606,"mean_force":1.04473,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48417,0.10193,0.05178]},{"body_a":"attachment","body_b":"peg","contact_count":14.0,"contact_point_centroid":[0.49305,0.08016,0.04938],"force_p95":15.62453,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":16.06222,"mean_force":6.4012,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48767,0.09182,0.0414]},{"body_a":"peg","body_b":"channel_base_body","contact_count":455.0,"contact_point_centroid":[0.49554,0.06378,0.00936],"force_p95":0.59683,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.44546,"mean_force":0.5642,"phase_index":0.0,"phase_name":"align_1","phase_type":"approach","tcp_position_centroid":[0.48779,0.1538,0.17291]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":28.0,"contact_point_centroid":[0.47133,0.06388,0.03676],"force_p95":0.92436,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.16907,"mean_force":0.37063,"phase_index":0.0,"phase_name":"align_1","phase_type":"approach","tcp_position_centroid":[0.49926,0.19818,0.2954]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":5.0,"contact_point_centroid":[0.47491,0.05684,0.01065],"force_p95":0.90436,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.91241,"mean_force":0.76998,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48788,0.08874,0.0373]},{"body_a":"peg","body_b":"channel_base_body","contact_count":330.0,"contact_point_centroid":[0.49541,0.05519,0.00946],"force_p95":0.66034,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.85262,"mean_force":0.53697,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49082,0.19896,0.11799]},{"body_a":"attachment","body_b":"peg","contact_count":6.0,"contact_point_centroid":[0.49275,0.07776,0.04512],"force_p95":0.60477,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.74732,"mean_force":0.22936,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.48836,0.08948,0.03817]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":146.0,"contact_point_centroid":[0.47495,0.05529,0.04001],"force_p95":0.41274,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55702,"mean_force":0.15883,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48993,0.17082,0.09281]},{"body_a":"peg","body_b":"channel_base_body","contact_count":4.0,"contact_point_centroid":[0.49945,0.0734,0.00979],"force_p95":0.53128,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.53979,"mean_force":0.46666,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48787,0.08872,0.03727]}],"total_contact_groups":14},"final_pose_error":0.04954,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49304,0.05558,0.03378],"final_tcp_position":[0.49806,0.22408,0.25675],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48093,0.06388,0.04]},"peak_contact_force":442.63445,"phases":[{"contact_detected":true,"contact_event_count":2.0,"n_steps":482.0,"n_steps_budget":1000.0,"object_pos_end":[0.49525,0.06399,0.03394],"object_pos_start":[0.48093,0.06388,0.04],"object_to_goal_dist_end":0.14419,"object_to_goal_dist_start":0.14514,"object_z_max":0.04,"peak_contact_force":183.25236,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":484.0,"raw_peak_contact_force":183.25236,"subtask_id":"approach","tcp_end":[0.47759,0.11148,0.05802],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.0561,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":176.0,"n_steps_budget":600.0,"object_pos_end":[0.49431,0.06069,0.0365],"object_pos_start":[0.49525,0.06399,0.03394],"object_to_goal_dist_end":0.14085,"object_to_goal_dist_start":0.14419,"object_z_max":0.03637,"peak_contact_force":0.1363,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":261.0,"raw_peak_contact_force":245.30167,"subtask_id":"contact","tcp_end":[0.48854,0.08971,0.03846],"tcp_start":[0.47759,0.11148,0.05802],"tcp_to_object_dist_end":0.02966,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":10.0,"n_steps_budget":600.0,"object_pos_end":[0.49324,0.05822,0.03577],"object_pos_start":[0.49431,0.06069,0.0365],"object_to_goal_dist_end":0.13845,"object_to_goal_dist_start":0.14085,"object_z_max":0.03664,"peak_contact_force":99.71353,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":7.0,"raw_peak_contact_force":40.05409,"subtask_id":"contact","tcp_end":[0.48793,0.08886,0.03741],"tcp_start":[0.48854,0.08971,0.03846],"tcp_to_object_dist_end":0.03113,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":5.0,"n_steps_budget":1000.0,"object_pos_end":[0.49316,0.0575,0.03518],"object_pos_start":[0.49324,0.05822,0.03577],"object_to_goal_dist_end":0.13775,"object_to_goal_dist_start":0.13845,"object_z_max":0.03577,"peak_contact_force":60.51043,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":14.0,"raw_peak_contact_force":60.51043,"tcp_end":[0.48784,0.08862,0.03718],"tcp_start":[0.48785,0.08865,0.03721],"tcp_to_object_dist_end":0.03163,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":330.0,"n_steps_budget":1000.0,"object_pos_end":[0.49304,0.05558,0.03378],"object_pos_start":[0.4932,0.05705,0.03491],"object_to_goal_dist_end":0.1359,"object_to_goal_dist_start":0.13731,"object_z_max":0.03526,"peak_contact_force":0.53978,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":483.0,"raw_peak_contact_force":442.63445,"tcp_end":[0.49806,0.22408,0.25675],"tcp_start":[0.48784,0.08862,0.03718],"tcp_to_object_dist_end":0.27953,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```