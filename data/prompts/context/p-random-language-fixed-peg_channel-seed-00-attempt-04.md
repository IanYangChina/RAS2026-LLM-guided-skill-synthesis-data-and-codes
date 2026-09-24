## Search State

- **Seed**: 0
- **Iteration**: 5 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 4 | insert → approach → push → retract → lift → insert | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | linear_cartesian | impedance_motion | impedance_control | force_threshold_switch | impedance_control | position_control | position_control | admittance_control | force_exceeded | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | force_exceeded | 5 | 0.2014 | 0.77 | ✅ accepted |
| 3 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | 6 | 0.0857 | 0.14 | ❌ rejected |
| 2 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | 5 | 0.5607 | 0.71 | ❌ rejected |
| 1 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | admittance_control | pose_tolerance | force_exceeded | pose_tolerance | 5 | 0.1787 | 0.00 | ❌ rejected |
| 0 | insert → approach → push → retract → lift → insert | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | linear_cartesian | impedance_motion | impedance_control | force_threshold_switch | impedance_control | position_control | position_control | admittance_control | force_exceeded | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | force_exceeded | 5 | 0.2281 | 0.74 | ✅ accepted |

**Proposal policy**: task_score is 0.77 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.201) — your mutation base

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

- **Composite score**: 0.201
- **task_score** (E): 0.770
- **fitness_score**: 0.571  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.370

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| insert_1 | 0.00 | 1.00 | 0.1730 |
| approach_1 | 1.00 | 1.00 | 0.1465 |
| push_1 | 0.00 | 1.00 | 0.1543 |
| retract_1 | 0.00 | 1.00 | 0.1196 |
| lift_1 | 0.00 | 1.00 | 0.1646 |
| insert_2 | 0.00 | 1.00 | 0.1662 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| insert_1 | insert | 0.00 / step_budget | (0.500, 0.200, 0.300)→(0.497, 0.075, 0.180) | (0.498, 0.080, 0.040)→(0.500, 0.080, 0.034) | 0.161→0.161 | 1.00 / 1.000 | 0.575 | 2.179 |
| approach_1 | approach | 1.00 / step_budget | (0.497, 0.075, 0.180)→(0.497, 0.119, 0.043) | (0.500, 0.080, 0.034)→(0.500, 0.084, 0.033) | 0.161→0.165 | 1.00 / 1.667 | 34.686 | 43.877 |
| push_1 | push | 0.00 / step_budget | (0.497, 0.119, 0.043)→(0.494, -0.035, 0.038) | (0.500, 0.084, 0.033)→(0.508, -0.061, 0.036) | 0.165→0.026 | 1.00 / 3.333 | 0.946 | 154.487 |
| retract_1 | retract | 0.00 / step_budget | (0.494, -0.035, 0.038)→(0.493, 0.007, 0.149) | (0.508, -0.061, 0.036)→(0.505, -0.058, 0.031) | 0.026→0.028 | 1.00 / 1.000 | 0.599 | 115.386 |
| lift_1 | lift | 0.00 / step_budget | (0.493, 0.007, 0.149)→(0.400, -0.048, 0.272) | (0.505, -0.058, 0.031)→(0.502, -0.058, 0.031) | 0.028→0.028 | 1.00 / 1.000 | 0.582 | 3.531 |
| insert_2 | insert | 0.00 / step_budget | (0.400, -0.048, 0.272)→(0.461, -0.068, 0.119) | (0.502, -0.058, 0.031)→(0.502, -0.058, 0.031) | 0.028→0.028 | 1.00 / 1.000 | 0.542 | 3.551 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.861
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.856
- phase_score: 0.537
- phase_breakdown.push_score: 0.634
- phase_breakdown.approach_score: 0.783
- phase_breakdown.contact_score: 0.000

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.664
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.856
- **Median Q (composite search score)**: 0.159
- **K-run variance**: 0.0043
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.354


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.61172,"average_solve_count":273.0,"average_success_count":273.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"lift_1.speed":0.0313,"push_1.push_distance":0.1924,"push_1.push_speed":0.08077,"retract_1.retract_height":0.13292,"retract_1.speed":0.0997},"optimized_scores":{"best_composite_score":0.2944,"best_fitness_score":0.6644,"best_task_score":0.85596},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":2.0,"contact_point_centroid":[0.5425,-0.05379,0.06],"force_p95":92.24726,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":93.9193,"mean_force":77.19885,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49785,-0.05753,0.03665]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":335.0,"contact_point_centroid":[0.54142,-0.01263,0.06],"force_p95":61.00979,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":92.08053,"mean_force":45.7807,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.4966,-0.01117,0.03699]},{"body_a":"attachment","body_b":"peg","contact_count":734.0,"contact_point_centroid":[0.50248,-0.00658,0.04266],"force_p95":54.12679,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":86.37679,"mean_force":10.65188,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49641,0.00479,0.03708]},{"body_a":"peg","body_b":"channel_base_body","contact_count":108.0,"contact_point_centroid":[0.50637,-0.10092,0.05832],"force_p95":69.99592,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":83.0796,"mean_force":42.84499,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49734,-0.05468,0.03672]},{"body_a":"attachment","body_b":"peg","contact_count":73.0,"contact_point_centroid":[0.50401,-0.06399,0.05483],"force_p95":15.87083,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":63.36509,"mean_force":5.9897,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49585,-0.05243,0.04128]},{"body_a":"peg","body_b":"channel_base_body","contact_count":52.0,"contact_point_centroid":[0.50585,-0.10082,0.05964],"force_p95":15.85916,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":63.3164,"mean_force":8.20173,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49635,-0.05423,0.03916]},{"body_a":"peg","body_b":"channel_base_body","contact_count":596.0,"contact_point_centroid":[0.50628,-0.02622,0.00983],"force_p95":14.82494,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":20.78898,"mean_force":5.72105,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49644,0.01575,0.03732]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":350.0,"contact_point_centroid":[0.52507,-0.00994,0.02236],"force_p95":6.43303,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.52862,"mean_force":1.70035,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49622,0.01643,0.03712]},{"body_a":"peg","body_b":"channel_base_body","contact_count":977.0,"contact_point_centroid":[0.50366,0.06159,0.00935],"force_p95":0.6416,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.17216,"mean_force":0.55484,"phase_index":0.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.49748,0.13519,0.23593]},{"body_a":"peg","body_b":"channel_base_body","contact_count":944.0,"contact_point_centroid":[0.50574,-0.07683,0.00942],"force_p95":0.55247,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.03395,"mean_force":0.54358,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.4951,-0.0184,0.11386]},{"body_a":"peg","body_b":"channel_base_body","contact_count":454.0,"contact_point_centroid":[0.50368,0.06157,0.00936],"force_p95":0.64141,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.64379,"mean_force":0.54631,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49703,0.08639,0.11069]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":19.0,"contact_point_centroid":[0.52623,0.06158,0.03217],"force_p95":0.5921,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.62339,"mean_force":0.34148,"phase_index":0.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.49956,0.19884,0.29897]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.5056,-0.07609,0.00941],"force_p95":0.55052,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55509,"mean_force":0.54509,"phase_index":5.0,"phase_name":"insert_2","phase_type":"insert","tcp_position_centroid":[0.42215,-0.06131,0.21829]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.50544,-0.07602,0.0094],"force_p95":0.55068,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55398,"mean_force":0.54535,"phase_index":4.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44395,-0.0255,0.24059]}],"total_contact_groups":14},"final_pose_error":0.11222,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50584,-0.07616,0.03403],"final_tcp_position":[0.45314,-0.06898,0.14137],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.51096,0.06158,0.04]},"peak_contact_force":93.9193,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50384,0.06159,0.03376],"object_pos_start":[0.51096,0.06158,0.04],"object_to_goal_dist_end":0.14178,"object_to_goal_dist_start":0.14201,"object_z_max":0.04,"peak_contact_force":0.59321,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":996.0,"raw_peak_contact_force":2.17216,"tcp_end":[0.49696,0.07528,0.18003],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.14707,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":454.0,"n_steps_budget":930.0,"object_pos_end":[0.5038,0.06158,0.03376],"object_pos_start":[0.50384,0.06159,0.03376],"object_to_goal_dist_end":0.14177,"object_to_goal_dist_start":0.14178,"object_z_max":0.03377,"peak_contact_force":0.47825,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":454.0,"raw_peak_contact_force":0.64379,"tcp_end":[0.49926,0.09848,0.04185],"tcp_start":[0.49696,0.07528,0.18003],"tcp_to_object_dist_end":0.03805,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.506,-0.0853,0.03565],"object_pos_start":[0.5038,0.06158,0.03376],"object_to_goal_dist_end":0.00911,"object_to_goal_dist_start":0.14177,"object_z_max":0.03811,"peak_contact_force":1.41421,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2123.0,"raw_peak_contact_force":92.08053,"tcp_end":[0.49786,-0.05753,0.03665],"tcp_start":[0.49926,0.09848,0.04185],"tcp_to_object_dist_end":0.02896,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50556,-0.07582,0.03395],"object_pos_start":[0.506,-0.0853,0.03565],"object_to_goal_dist_end":0.00922,"object_to_goal_dist_start":0.00911,"object_z_max":0.03787,"peak_contact_force":0.54365,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1071.0,"raw_peak_contact_force":93.9193,"tcp_end":[0.49624,0.00271,0.18959],"tcp_start":[0.49786,-0.05753,0.03665],"tcp_to_object_dist_end":0.17458,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50559,-0.07632,0.03402],"object_pos_start":[0.50556,-0.07582,0.03395],"object_to_goal_dist_end":0.00897,"object_to_goal_dist_start":0.00922,"object_z_max":0.03402,"peak_contact_force":0.551,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":1000.0,"raw_peak_contact_force":0.55398,"tcp_end":[0.39363,-0.05402,0.29651],"tcp_start":[0.49624,0.00271,0.18959],"tcp_to_object_dist_end":0.28624,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50584,-0.07616,0.03403],"object_pos_start":[0.50559,-0.07632,0.03402],"object_to_goal_dist_end":0.00919,"object_to_goal_dist_start":0.00897,"object_z_max":0.03404,"peak_contact_force":0.54505,"phase_name":"insert_2","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":1000.0,"raw_peak_contact_force":0.55509,"tcp_end":[0.45314,-0.06898,0.14137],"tcp_start":[0.39363,-0.05402,0.29651],"tcp_to_object_dist_end":0.11979,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.72727,"average_solve_count":242.0,"average_success_count":242.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"lift_1.speed":0.09487,"push_1.push_distance":0.19895,"push_1.push_speed":0.0741,"retract_1.retract_height":0.09988,"retract_1.speed":0.03422},"optimized_scores":{"best_composite_score":0.15118,"best_fitness_score":0.52118,"best_task_score":0.85542},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":789.0,"contact_point_centroid":[0.50279,0.06504,0.00854],"force_p95":185.2354,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":188.81633,"mean_force":71.95564,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50065,0.09801,0.04348]},{"body_a":"attachment","body_b":"peg","contact_count":795.0,"contact_point_centroid":[0.50469,0.08714,0.04514],"force_p95":184.68131,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":188.37665,"mean_force":75.19096,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50068,0.09692,0.04348]},{"body_a":"attachment","body_b":"peg","contact_count":109.0,"contact_point_centroid":[0.50657,0.13982,0.05102],"force_p95":119.53343,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":130.43451,"mean_force":83.80714,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49846,0.14657,0.05326]},{"body_a":"peg","body_b":"channel_base_body","contact_count":563.0,"contact_point_centroid":[0.50214,0.1166,0.00925],"force_p95":94.17839,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":117.99062,"mean_force":15.43742,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49609,0.11288,0.10781]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":207.0,"contact_point_centroid":[0.47398,0.06841,0.03548],"force_p95":63.23214,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":71.63633,"mean_force":18.61749,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50093,0.09504,0.0425]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":77.0,"contact_point_centroid":[0.5415,0.02099,0.06],"force_p95":51.69964,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":54.37643,"mean_force":39.67722,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.4965,0.02414,0.03716]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":3.0,"contact_point_centroid":[0.5417,-0.00153,0.05999],"force_p95":48.55122,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":48.8495,"mean_force":43.89272,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.4968,0.0028,0.03712]},{"body_a":"peg","body_b":"world","contact_count":133.0,"contact_point_centroid":[0.50195,0.12555,-0.00016],"force_p95":19.84041,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":48.74864,"mean_force":13.35402,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50037,0.15458,0.045]},{"body_a":"peg","body_b":"world","contact_count":28.0,"contact_point_centroid":[0.50222,0.12719,-0.0003],"force_p95":37.33342,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":39.90411,"mean_force":28.00895,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49992,0.15488,0.04587]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":149.0,"contact_point_centroid":[0.52516,-0.0023,0.02444],"force_p95":7.72745,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":10.76179,"mean_force":3.06887,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49649,0.02464,0.03718]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.50611,-0.02431,0.00942],"force_p95":0.62094,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.69741,"mean_force":0.54261,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49387,0.01737,0.08279]},{"body_a":"attachment","body_b":"peg","contact_count":47.0,"contact_point_centroid":[0.50359,-0.00725,0.05335],"force_p95":0.47921,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":3.05217,"mean_force":0.3104,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49507,0.00455,0.04011]},{"body_a":"peg","body_b":"channel_base_body","contact_count":984.0,"contact_point_centroid":[0.50098,0.11602,0.0094],"force_p95":0.60736,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.92055,"mean_force":0.55146,"phase_index":0.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.49749,0.13563,0.23636]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.50621,-0.02298,0.00938],"force_p95":0.55474,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.62302,"mean_force":0.54661,"phase_index":4.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44701,-0.0069,0.19453]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.50626,-0.02305,0.00938],"force_p95":0.55278,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.5543,"mean_force":0.54662,"phase_index":5.0,"phase_name":"insert_2","phase_type":"insert","tcp_position_centroid":[0.43149,-0.05272,0.18704]}],"total_contact_groups":15},"final_pose_error":0.08188,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50626,-0.02297,0.03381],"final_tcp_position":[0.46336,-0.066,0.11187],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50095,0.11604,0.04]},"peak_contact_force":188.81633,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50092,0.11601,0.03383],"object_pos_start":[0.50095,0.11604,0.04],"object_to_goal_dist_end":0.19611,"object_to_goal_dist_start":0.19604,"object_z_max":0.04,"peak_contact_force":0.58045,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":984.0,"raw_peak_contact_force":1.92055,"tcp_end":[0.49696,0.07528,0.18003],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.15182,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":563.0,"n_steps_budget":1000.0,"object_pos_end":[0.50228,0.12805,0.02979],"object_pos_start":[0.50092,0.11601,0.03383],"object_to_goal_dist_end":0.20832,"object_to_goal_dist_start":0.19611,"object_z_max":0.0342,"peak_contact_force":103.03901,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":700.0,"raw_peak_contact_force":130.43451,"tcp_end":[0.50029,0.1577,0.04359],"tcp_start":[0.49696,0.07528,0.18003],"tcp_to_object_dist_end":0.03276,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50655,-0.02555,0.03632],"object_pos_start":[0.50228,0.12805,0.02979],"object_to_goal_dist_end":0.05496,"object_to_goal_dist_start":0.20832,"object_z_max":0.03779,"peak_contact_force":1.42449,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2150.0,"raw_peak_contact_force":188.81633,"tcp_end":[0.49683,0.00303,0.03715],"tcp_start":[0.50029,0.1577,0.04359],"tcp_to_object_dist_end":0.03019,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50626,-0.02297,0.03377],"object_pos_start":[0.50655,-0.02555,0.03632],"object_to_goal_dist_end":0.05771,"object_to_goal_dist_start":0.05496,"object_z_max":0.03633,"peak_contact_force":0.61101,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1050.0,"raw_peak_contact_force":48.8495,"tcp_end":[0.4946,0.0261,0.13004],"tcp_start":[0.49683,0.00303,0.03715],"tcp_to_object_dist_end":0.10869,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50621,-0.02306,0.03381],"object_pos_start":[0.50626,-0.02297,0.03377],"object_to_goal_dist_end":0.05761,"object_to_goal_dist_start":0.05771,"object_z_max":0.03381,"peak_contact_force":0.54444,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":1000.0,"raw_peak_contact_force":0.62302,"tcp_end":[0.40231,-0.03988,0.26358],"tcp_start":[0.4946,0.0261,0.13004],"tcp_to_object_dist_end":0.25274,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50626,-0.02297,0.03381],"object_pos_start":[0.50621,-0.02306,0.03381],"object_to_goal_dist_end":0.05771,"object_to_goal_dist_start":0.05761,"object_z_max":0.03381,"peak_contact_force":0.54793,"phase_name":"insert_2","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":1000.0,"raw_peak_contact_force":0.5543,"tcp_end":[0.46336,-0.066,0.11187],"tcp_start":[0.40231,-0.03988,0.26358],"tcp_to_object_dist_end":0.09892,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.6625,"average_solve_count":240.0,"average_success_count":240.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"lift_1.speed":0.06974,"push_1.push_distance":0.18715,"push_1.push_speed":0.09903,"retract_1.retract_height":0.07001,"retract_1.speed":0.04636},"optimized_scores":{"best_composite_score":0.15876,"best_fitness_score":0.52876,"best_task_score":0.59735},"replay_outcomes":[{"contacts":{"omitted_contact_groups":4,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_right_wall","contact_count":128.0,"contact_point_centroid":[0.47498,-0.04496,0.05155],"force_p95":176.2092,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":203.39066,"mean_force":84.1535,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48548,-0.04488,0.04578]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":360.0,"contact_point_centroid":[0.53539,-0.01576,0.05999],"force_p95":163.9907,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":182.56544,"mean_force":95.86431,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49014,-0.0118,0.03802]},{"body_a":"attachment","body_b":"peg","contact_count":917.0,"contact_point_centroid":[0.49787,0.0058,0.03596],"force_p95":128.26117,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":156.72512,"mean_force":72.21034,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48988,0.0121,0.03798]},{"body_a":"peg","body_b":"channel_base_body","contact_count":960.0,"contact_point_centroid":[0.50839,-0.00965,0.00956],"force_p95":83.474,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":112.51252,"mean_force":41.2653,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48986,0.01585,0.03809]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":824.0,"contact_point_centroid":[0.52617,-0.00977,0.02717],"force_p95":94.443,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":100.98606,"mean_force":58.21713,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49003,0.00472,0.03795]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":153.0,"contact_point_centroid":[0.52616,-0.05392,0.02932],"force_p95":66.2128,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":89.87543,"mean_force":34.67406,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48581,-0.0458,0.04539]},{"body_a":"attachment","body_b":"peg","contact_count":122.0,"contact_point_centroid":[0.49582,-0.05013,0.03831],"force_p95":65.48254,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":86.55873,"mean_force":39.94446,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48582,-0.04768,0.04252]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":3.0,"contact_point_centroid":[0.53391,-0.04765,0.05999],"force_p95":75.45329,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":75.50275,"mean_force":72.10286,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48808,-0.05148,0.03903]},{"body_a":"peg","body_b":"channel_base_body","contact_count":81.0,"contact_point_centroid":[0.51076,-0.10063,0.032],"force_p95":66.29828,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":73.8427,"mean_force":38.50252,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48881,-0.04719,0.0387]},{"body_a":"peg","body_b":"channel_base_body","contact_count":963.0,"contact_point_centroid":[0.5029,-0.07038,0.00847],"force_p95":10.65386,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":42.28755,"mean_force":2.10502,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48676,-0.02587,0.08271]},{"body_a":"peg","body_b":"channel_base_body","contact_count":158.0,"contact_point_centroid":[0.51204,-0.10017,0.02593],"force_p95":18.61509,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":32.37633,"mean_force":4.10015,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48592,-0.03992,0.05489]},{"body_a":"peg","body_b":"link7","contact_count":360.0,"contact_point_centroid":[0.52011,0.00749,0.06784],"force_p95":22.66926,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":27.75939,"mean_force":10.89108,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48965,0.03247,0.03789]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":17.0,"contact_point_centroid":[0.47488,-0.09875,0.02464],"force_p95":10.14526,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":10.5609,"mean_force":2.93593,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48544,-0.03637,0.05877]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.49405,-0.07457,0.00805],"force_p95":0.7104,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.54314,"mean_force":0.62293,"phase_index":5.0,"phase_name":"insert_2","phase_type":"insert","tcp_position_centroid":[0.43396,-0.06022,0.17907]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.49699,-0.07423,0.00807],"force_p95":0.64684,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.41575,"mean_force":0.62298,"phase_index":4.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44505,-0.02905,0.18975]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":7.0,"contact_point_centroid":[0.475,-0.0994,0.02432],"force_p95":9.0179,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.11632,"mean_force":2.83113,"phase_index":5.0,"phase_name":"insert_2","phase_type":"insert","tcp_position_centroid":[0.42631,-0.05785,0.19632]}],"total_contact_groups":20},"final_pose_error":0.07228,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49337,-0.07476,0.02413],"final_tcp_position":[0.46651,-0.07038,0.10333],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48093,0.06388,0.04]},"peak_contact_force":203.39066,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49482,0.06382,0.03401],"object_pos_start":[0.48093,0.06388,0.04],"object_to_goal_dist_end":0.14404,"object_to_goal_dist_start":0.14514,"object_z_max":0.04,"peak_contact_force":0.55002,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":1001.0,"raw_peak_contact_force":2.44546,"tcp_end":[0.49696,0.07528,0.18003],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.14649,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":447.0,"n_steps_budget":930.0,"object_pos_end":[0.49519,0.06359,0.03403],"object_pos_start":[0.49482,0.06382,0.03401],"object_to_goal_dist_end":0.14379,"object_to_goal_dist_start":0.14404,"object_z_max":0.03403,"peak_contact_force":0.54085,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":447.0,"raw_peak_contact_force":0.55403,"tcp_end":[0.4911,0.10042,0.04259],"tcp_start":[0.49696,0.07528,0.18003],"tcp_to_object_dist_end":0.03803,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5111,-0.07125,0.03644],"object_pos_start":[0.49519,0.06359,0.03403],"object_to_goal_dist_end":0.01457,"object_to_goal_dist_start":0.14379,"object_z_max":0.04003,"peak_contact_force":0.0,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3502.0,"raw_peak_contact_force":182.56544,"tcp_end":[0.4881,-0.05138,0.03903],"tcp_start":[0.4911,0.10042,0.04259],"tcp_to_object_dist_end":0.0305,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50198,-0.07432,0.02415],"object_pos_start":[0.5111,-0.07125,0.03644],"object_to_goal_dist_end":0.01695,"object_to_goal_dist_start":0.01457,"object_z_max":0.03707,"peak_contact_force":0.64358,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1544.0,"raw_peak_contact_force":203.39066,"tcp_end":[0.48893,-0.00768,0.1276],"tcp_start":[0.4881,-0.05138,0.03903],"tcp_to_object_dist_end":0.12374,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49424,-0.07451,0.02413],"object_pos_start":[0.50198,-0.07432,0.02415],"object_to_goal_dist_end":0.01775,"object_to_goal_dist_start":0.01695,"object_z_max":0.02435,"peak_contact_force":0.65119,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":1006.0,"raw_peak_contact_force":9.41575,"tcp_end":[0.40412,-0.05046,0.2562],"tcp_start":[0.48893,-0.00768,0.1276],"tcp_to_object_dist_end":0.25011,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49337,-0.07476,0.02413],"object_pos_start":[0.49424,-0.07451,0.02413],"object_to_goal_dist_end":0.01798,"object_to_goal_dist_start":0.01775,"object_z_max":0.02443,"peak_contact_force":0.53262,"phase_name":"insert_2","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":1007.0,"raw_peak_contact_force":9.54314,"tcp_end":[0.46651,-0.07038,0.10333],"tcp_start":[0.40412,-0.05046,0.2562],"tcp_to_object_dist_end":0.08375,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
```