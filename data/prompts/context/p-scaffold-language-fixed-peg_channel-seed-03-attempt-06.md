## Search State

- **Seed**: 3
- **Iteration**: 7 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 6 | approach → descend → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 7 | -0.0508 | 0.22 | ❌ rejected |
| 5 | approach → descend → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 6 | -0.2495 | 0.00 | ❌ rejected |
| 4 | approach → descend → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 6 | 0.0567 | 0.16 | ❌ rejected |
| 3 | align → approach → contact → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 6 | 0.1016 | 0.21 | ❌ rejected |
| 2 | align → approach → contact → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 6 | 0.1392 | 0.28 | ✅ accepted |

**Proposal policy**: task_score is 0.22 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `990d03f436076caee02f5d9d8b3b9b0b3759564b7644084e4eac46818881d834`
- Frozen object start: [0.46685193337148995, 0.058944840527687975, 0.04]
- Frozen task target: [0.46685193337148995, -0.10105515947231203, 0.04]
- Goal object position: (0.46685193337148995, -0.10105515947231203, 0.04)
- Task success criterion: peg must traverse the channel (0.16 m long) along axis (0.0, -1.0, 0.0); score = axial progress × lateral alignment — NOT a fixed TCP endpoint
- Object initial pose: (0.46685193337148995, 0.058944840527687975, 0.04)
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
  frozen_object_start: [0.4669, 0.0589, 0.04]
  frozen_task_target: [0.4669, -0.1011, 0.04]
  frozen_fixture_position: [0.54, 0, 0.035]
  frozen_object_starts: {'peg': [0.46685193337148995, 0.058944840527687975, 0.04]}
  frozen_targets: {'channel_exit': [0.46685193337148995, -0.10105515947231203, 0.04]}
  frozen_fixtures: {'channel_left_wall': [0.54, 0.0, 0.035], 'channel_right_wall': [0.46, 0.0, 0.035]}
  channel_axis: [0, -1, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 40
  channel_length_m: 0.16
  force_scale_n: 5
  realized_scene_sha256: 990d03f436076caee02f5d9d8b3b9b0b3759564b7644084e4eac46818881d834

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

## Current Skill (Q=-0.051) — your mutation base

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
  control: position_control
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
  generator: linear_cartesian
  control: impedance_control
  termination: pose_tolerance
  parameters:
    push_depth:
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

- **Composite score**: -0.051
- **task_score** (E): 0.215
- **fitness_score**: 0.189  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.200
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.440

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_high | 1.00 | 1.00 | 0.1711 |
| descend_to_peg | 1.00 | 1.00 | 0.1152 |
| contact_engage | 1.00 | 1.00 | 0.0082 |
| push_through_channel | 0.00 | 1.00 | 0.0013 |
| lift_up | 1.00 | 1.00 | 0.1598 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_high | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.505, 0.131, 0.147) | (0.509, 0.081, 0.040)→(0.502, 0.081, 0.034) | 0.165→0.162 | 1.00 / 1.000 | 0.546 | 3.954 |
| descend_to_peg | descend | 1.00 / step_budget | (0.505, 0.131, 0.147)→(0.499, 0.103, 0.038) | (0.502, 0.081, 0.034)→(0.504, 0.066, 0.038) | 0.162→0.146 | 1.00 / 1.000 | 0.616 | 204.350 |
| contact_engage | contact | 1.00 / force_exceeded | (0.499, 0.103, 0.038)→(0.504, 0.098, 0.034) | (0.504, 0.066, 0.038)→(0.505, 0.064, 0.039) | 0.146→0.145 | 1.00 / 2.000 | 2633.074 | 114.409 |
| push_through_channel | push | 0.00 / guard_failure | (0.510, 0.091, 0.030)→(0.511, 0.090, 0.029) | (0.505, 0.064, 0.039)→(0.507, 0.058, 0.042) | 0.145→0.138 | 1.00 / 2.667 | 1297.815 | 1588.004 |
| lift_up | retract | 1.00 / step_budget | (0.511, 0.090, 0.029)→(0.501, -0.042, 0.118) | (0.508, 0.055, 0.042)→(0.502, -0.018, 0.028) | 0.136→0.064 | 1.00 / 1.333 | 0.483 | 381.211 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.814
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.259
- phase_score: 0.177
- phase_breakdown.approach_score: 0.117
- phase_breakdown.contact_score: 0.588
- phase_breakdown.push_score: 0.059

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.210
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.259
- **Median Q (composite search score)**: -0.045
- **K-run variance**: 0.0004
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.274


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `cc7283febf3c95cef1fde4c5a16cbcb134186cb6faf3a169717a9aa53375931d`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.04,0.04]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `178d67757a065da6e29d31070e25f6065dc7e42bdbf58dfbff0deec513214033`; realized-scene SHA-256: `990d03f436076caee02f5d9d8b3b9b0b3759564b7644084e4eac46818881d834`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.46685,0.05894,0.04]},{"name":"goal","value":[0.46685,-0.10106,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.46685,0.05894,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.46685,-0.10106,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.41627,"average_solve_count":209.0,"average_success_count":209.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_high.lateral_offset_y":-0.0002,"approach_high.speed":0.10595,"contact_engage.contact_force":9.15808,"descend_to_peg.speed":0.07204,"lift_up.lift_speed":0.01723,"push_through_channel.push_depth":0.16721,"push_through_channel.push_speed":0.02156},"optimized_scores":{"best_composite_score":-0.03045,"best_fitness_score":0.20955,"best_task_score":0.25889},"replay_outcomes":[{"contacts":{"omitted_contact_groups":3,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":3.0,"contact_point_centroid":[0.53581,0.08345,0.05909],"force_p95":1641.18083,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1660.77906,"mean_force":1497.13298,"phase_index":3.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.50481,0.06205,0.02452]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":23.0,"contact_point_centroid":[0.53215,0.08881,0.05859],"force_p95":873.09845,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":910.70419,"mean_force":380.81059,"phase_index":4.0,"phase_name":"lift_up","phase_type":"retract","tcp_position_centroid":[0.50769,0.05878,0.02473]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":14.0,"contact_point_centroid":[0.5253,0.065,0.05995],"force_p95":884.50563,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":907.96157,"mean_force":438.84468,"phase_index":4.0,"phase_name":"lift_up","phase_type":"retract","tcp_position_centroid":[0.50796,0.05859,0.02392]},{"body_a":"attachment","body_b":"channel_right_wall","contact_count":137.0,"contact_point_centroid":[0.47499,0.08038,0.05994],"force_p95":427.33229,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":450.73018,"mean_force":381.28105,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.48531,0.08541,0.05827]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.49866,0.06636,0.05854],"force_p95":71.78036,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":71.78036,"mean_force":71.78036,"phase_index":2.0,"phase_name":"contact_engage","phase_type":"contact","tcp_position_centroid":[0.49145,0.07756,0.0352]},{"body_a":"peg","body_b":"channel_base_body","contact_count":5.0,"contact_point_centroid":[0.50703,0.03275,0.00882],"force_p95":57.41807,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":71.57545,"mean_force":14.86592,"phase_index":2.0,"phase_name":"contact_engage","phase_type":"contact","tcp_position_centroid":[0.48999,0.07915,0.03621]},{"body_a":"peg","body_b":"channel_base_body","contact_count":815.0,"contact_point_centroid":[0.49628,0.05524,0.0095],"force_p95":1.46961,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":44.8861,"mean_force":1.27131,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.47673,0.09239,0.08962]},{"body_a":"attachment","body_b":"peg","contact_count":142.0,"contact_point_centroid":[0.49055,0.07375,0.05931],"force_p95":31.34238,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":44.41458,"mean_force":4.31041,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.48572,0.08482,0.05585]},{"body_a":"peg","body_b":"channel_base_body","contact_count":2.0,"contact_point_centroid":[0.50754,0.03213,0.00924],"force_p95":33.53359,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":33.77953,"mean_force":31.32011,"phase_index":3.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.49338,0.07558,0.03411]},{"body_a":"attachment","body_b":"peg","contact_count":7.0,"contact_point_centroid":[0.50251,0.0614,0.05118],"force_p95":30.5578,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":31.47436,"mean_force":12.34871,"phase_index":3.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.49735,0.07122,0.0317]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":9.0,"contact_point_centroid":[0.52698,0.03728,0.01686],"force_p95":4.7698,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":5.85239,"mean_force":2.34913,"phase_index":3.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.50134,0.06646,0.02825]},{"body_a":"peg","body_b":"link7","contact_count":4.0,"contact_point_centroid":[0.52427,0.04036,0.06669],"force_p95":4.89239,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":5.69202,"mean_force":1.54406,"phase_index":3.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.50433,0.06269,0.02513]},{"body_a":"peg","body_b":"channel_base_body","contact_count":534.0,"contact_point_centroid":[0.49438,0.05905,0.00935],"force_p95":0.56942,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.20518,"mean_force":0.57361,"phase_index":0.0,"phase_name":"approach_high","phase_type":"approach","tcp_position_centroid":[0.48187,0.15073,0.21904]},{"body_a":"peg","body_b":"channel_base_body","contact_count":93.0,"contact_point_centroid":[0.49749,-0.10046,0.02633],"force_p95":1.60958,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.93134,"mean_force":0.50239,"phase_index":4.0,"phase_name":"lift_up","phase_type":"retract","tcp_position_centroid":[0.50248,-0.00594,0.07998]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":35.0,"contact_point_centroid":[0.46807,0.05895,0.03796],"force_p95":1.19991,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.42382,"mean_force":0.50385,"phase_index":0.0,"phase_name":"approach_high","phase_type":"approach","tcp_position_centroid":[0.49882,0.19772,0.2962]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":18.0,"contact_point_centroid":[0.52632,0.00893,0.05053],"force_p95":1.73295,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.57433,"mean_force":0.59664,"phase_index":4.0,"phase_name":"lift_up","phase_type":"retract","tcp_position_centroid":[0.50781,0.05877,0.02417]}],"total_contact_groups":19},"final_pose_error":0.04982,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49477,-0.07135,0.03355],"final_tcp_position":[0.50073,-0.04518,0.11438],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.46685,0.05894,0.04]},"peak_contact_force":1660.77906,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":563.0,"n_steps_budget":1000.0,"object_pos_end":[0.494,0.05892,0.03387],"object_pos_start":[0.46685,0.05894,0.04],"object_to_goal_dist_end":0.13919,"object_to_goal_dist_start":0.14284,"object_z_max":0.04001,"peak_contact_force":0.54736,"phase_name":"approach_high","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":569.0,"raw_peak_contact_force":4.20518,"subtask_id":"approach","tcp_end":[0.46642,0.10538,0.14718],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.12553,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":834.0,"n_steps_budget":1000.0,"object_pos_end":[0.50368,0.04968,0.03311],"object_pos_start":[0.494,0.05892,0.03387],"object_to_goal_dist_end":0.12992,"object_to_goal_dist_start":0.13919,"object_z_max":0.03852,"peak_contact_force":0.87664,"phase_name":"descend_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1094.0,"raw_peak_contact_force":450.73018,"tcp_end":[0.48902,0.08025,0.037],"tcp_start":[0.46642,0.10538,0.14718],"tcp_to_object_dist_end":0.03412,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":5.0,"n_steps_budget":600.0,"object_pos_end":[0.50422,0.04889,0.03381],"object_pos_start":[0.50368,0.04968,0.03311],"object_to_goal_dist_end":0.1291,"object_to_goal_dist_start":0.12992,"object_z_max":0.03312,"peak_contact_force":71.78036,"phase_name":"contact_engage","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":6.0,"raw_peak_contact_force":71.78036,"subtask_id":"contact","tcp_end":[0.49266,0.07631,0.0345],"tcp_start":[0.48902,0.08025,0.037],"tcp_to_object_dist_end":0.02977,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":11.0,"n_steps_budget":1000.0,"object_pos_end":[0.5102,0.03123,0.04213],"object_pos_start":[0.50422,0.04889,0.03381],"object_to_goal_dist_end":0.11172,"object_to_goal_dist_start":0.1291,"object_z_max":0.04236,"peak_contact_force":1464.79674,"phase_name":"push_through_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":25.0,"raw_peak_contact_force":1660.77906,"subtask_id":"push","tcp_end":[0.50648,0.06006,0.02326],"tcp_start":[0.50573,0.06098,0.02367],"tcp_to_object_dist_end":0.03465,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":170.0,"n_steps_budget":1000.0,"object_pos_end":[0.49477,-0.07135,0.03355],"object_pos_start":[0.51037,0.02661,0.04255],"object_to_goal_dist_end":0.01199,"object_to_goal_dist_start":0.10715,"object_z_max":0.04293,"peak_contact_force":0.38816,"phase_name":"lift_up","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":268.0,"raw_peak_contact_force":910.70419,"tcp_end":[0.50073,-0.04518,0.11438],"tcp_start":[0.50648,0.06006,0.02326],"tcp_to_object_dist_end":0.08516,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `1ee374347cb6f80436633ebcb956aaa73ea8a10685d65b21d5c3814cf0c53498`; realized-scene SHA-256: `5d75b33f12bcf5a2f8bdcc4693a93f63ce145f4d32d6acfe75032964e261854c`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.53544,0.08091,0.04]},{"name":"goal","value":[0.53544,-0.07909,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.53544,0.08091,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.53544,-0.07909,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.3369,"average_solve_count":187.0,"average_success_count":187.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_high.lateral_offset_y":0.00644,"approach_high.speed":0.06325,"contact_engage.contact_force":9.97519,"descend_to_peg.speed":0.06256,"lift_up.lift_speed":0.05305,"push_through_channel.push_depth":0.1504,"push_through_channel.push_speed":0.02837},"optimized_scores":{"best_composite_score":-0.07657,"best_fitness_score":0.16343,"best_task_score":0.17038},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_left_wall","contact_count":3.0,"contact_point_centroid":[0.52561,0.09712,0.05991],"force_p95":1439.24484,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1452.67976,"mean_force":1318.26381,"phase_index":3.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.51031,0.09615,0.03403]},{"body_a":"peg","body_b":"channel_base_body","contact_count":5.0,"contact_point_centroid":[0.50292,0.06287,0.00998],"force_p95":93.94233,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":117.30599,"mean_force":23.85124,"phase_index":2.0,"phase_name":"contact_engage","phase_type":"contact","tcp_position_centroid":[0.50519,0.10159,0.03723]},{"body_a":"attachment","body_b":"peg","contact_count":2.0,"contact_point_centroid":[0.50689,0.08763,0.03614],"force_p95":109.87654,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":115.43912,"mean_force":59.81334,"phase_index":2.0,"phase_name":"contact_engage","phase_type":"contact","tcp_position_centroid":[0.50724,0.09943,0.0358]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":7.0,"contact_point_centroid":[0.52602,0.09459,0.05984],"force_p95":94.82861,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":109.22469,"mean_force":24.35178,"phase_index":4.0,"phase_name":"lift_up","phase_type":"retract","tcp_position_centroid":[0.51042,0.09219,0.03186]},{"body_a":"peg","body_b":"channel_base_body","contact_count":539.0,"contact_point_centroid":[0.50595,0.07839,0.00943],"force_p95":28.5303,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":80.01906,"mean_force":3.67214,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.51589,0.1172,0.09082]},{"body_a":"attachment","body_b":"peg","contact_count":33.0,"contact_point_centroid":[0.51232,0.097,0.05745],"force_p95":75.88843,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":79.48026,"mean_force":51.34597,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.5089,0.1081,0.05741]},{"body_a":"peg","body_b":"channel_base_body","contact_count":158.0,"contact_point_centroid":[0.50112,0.00616,0.00881],"force_p95":1.57923,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":10.09092,"mean_force":0.80241,"phase_index":4.0,"phase_name":"lift_up","phase_type":"retract","tcp_position_centroid":[0.50293,0.02793,0.07389]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":30.0,"contact_point_centroid":[0.5257,0.03512,0.04789],"force_p95":8.85075,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.69329,"mean_force":1.26459,"phase_index":4.0,"phase_name":"lift_up","phase_type":"retract","tcp_position_centroid":[0.50373,0.05238,0.05811]},{"body_a":"peg","body_b":"channel_base_body","contact_count":552.0,"contact_point_centroid":[0.50568,0.0809,0.00936],"force_p95":0.55756,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.32595,"mean_force":0.57441,"phase_index":0.0,"phase_name":"approach_high","phase_type":"approach","tcp_position_centroid":[0.51445,0.16449,0.21882]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":36.0,"contact_point_centroid":[0.5324,0.0809,0.02649],"force_p95":1.27622,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.70803,"mean_force":0.52144,"phase_index":0.0,"phase_name":"approach_high","phase_type":"approach","tcp_position_centroid":[0.50007,0.19833,0.29633]},{"body_a":"attachment","body_b":"peg","contact_count":3.0,"contact_point_centroid":[0.50877,0.08503,0.03515],"force_p95":1.55168,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.5544,"mean_force":1.52502,"phase_index":3.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.51031,0.09615,0.03403]},{"body_a":"attachment","body_b":"peg","contact_count":4.0,"contact_point_centroid":[0.50919,0.08123,0.03379],"force_p95":0.43913,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.44968,"mean_force":0.28636,"phase_index":4.0,"phase_name":"lift_up","phase_type":"retract","tcp_position_centroid":[0.5113,0.09251,0.03238]}],"total_contact_groups":12},"final_pose_error":0.04981,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50573,-0.0129,0.02458],"final_tcp_position":[0.50127,-0.04094,0.11912],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.53544,0.08091,0.04]},"peak_contact_force":3916.107,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":581.0,"n_steps_budget":1000.0,"object_pos_end":[0.50599,0.08089,0.03378],"object_pos_start":[0.53544,0.08091,0.04],"object_to_goal_dist_end":0.16112,"object_to_goal_dist_start":0.16476,"object_z_max":0.04001,"peak_contact_force":0.55007,"phase_name":"approach_high","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":588.0,"raw_peak_contact_force":4.32595,"subtask_id":"approach","tcp_end":[0.52972,0.13198,0.14649],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.12601,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":540.0,"n_steps_budget":1000.0,"object_pos_end":[0.50298,0.0631,0.04077],"object_pos_start":[0.50599,0.08089,0.03378],"object_to_goal_dist_end":0.14313,"object_to_goal_dist_start":0.16112,"object_z_max":0.04076,"peak_contact_force":0.48729,"phase_name":"descend_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":572.0,"raw_peak_contact_force":80.01906,"tcp_end":[0.50428,0.10268,0.03808],"tcp_start":[0.52972,0.13198,0.14649],"tcp_to_object_dist_end":0.0397,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":6.0,"n_steps_budget":600.0,"object_pos_end":[0.50404,0.06197,0.04139],"object_pos_start":[0.50298,0.0631,0.04077],"object_to_goal_dist_end":0.14203,"object_to_goal_dist_start":0.14313,"object_z_max":0.04111,"peak_contact_force":3916.107,"phase_name":"contact_engage","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":7.0,"raw_peak_contact_force":117.30599,"subtask_id":"contact","tcp_end":[0.50938,0.09744,0.03466],"tcp_start":[0.50428,0.10268,0.03808],"tcp_to_object_dist_end":0.0365,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.50455,0.06127,0.04161],"object_pos_start":[0.50404,0.06197,0.04139],"object_to_goal_dist_end":0.14135,"object_to_goal_dist_start":0.14203,"object_z_max":0.04178,"peak_contact_force":1183.78116,"phase_name":"push_through_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":6.0,"raw_peak_contact_force":1452.67976,"subtask_id":"push","tcp_end":[0.51147,0.09367,0.03297],"tcp_start":[0.51111,0.09488,0.03343],"tcp_to_object_dist_end":0.03424,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":189.0,"n_steps_budget":1000.0,"object_pos_end":[0.50573,-0.0129,0.02458],"object_pos_start":[0.50538,0.05956,0.04193],"object_to_goal_dist_end":0.06909,"object_to_goal_dist_start":0.13967,"object_z_max":0.04207,"peak_contact_force":0.50106,"phase_name":"lift_up","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":199.0,"raw_peak_contact_force":109.22469,"tcp_end":[0.50127,-0.04094,0.11912],"tcp_start":[0.51147,0.09367,0.03297],"tcp_to_object_dist_end":0.09871,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `e082b57d1be6744ae6d3993c25b90215f3fc56dc7131af62e0630c4f325e4b04`; realized-scene SHA-256: `ca4f9624fc0e37438ffe7fd92236fc537e25f346e4aaef8c3b399c2f4b45089e`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.5244,0.10464,0.04]},{"name":"goal","value":[0.5244,-0.05536,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.5244,0.10464,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.5244,-0.05536,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.22124,"average_solve_count":226.0,"average_success_count":226.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_high.lateral_offset_y":0.00763,"approach_high.speed":0.1107,"contact_engage.contact_force":4.92483,"descend_to_peg.speed":0.0362,"lift_up.lift_speed":0.01777,"push_through_channel.push_depth":0.11966,"push_through_channel.push_speed":0.03432},"optimized_scores":{"best_composite_score":-0.04548,"best_fitness_score":0.19452,"best_task_score":0.21647},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_left_wall","contact_count":3.0,"contact_point_centroid":[0.52647,0.11941,0.05979],"force_p95":1628.98911,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1650.55334,"mean_force":1443.44339,"phase_index":3.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.51202,0.11828,0.03288]},{"body_a":"peg","body_b":"channel_base_body","contact_count":5.0,"contact_point_centroid":[0.50455,0.08626,0.00999],"force_p95":123.43087,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":154.14202,"mean_force":31.23489,"phase_index":2.0,"phase_name":"contact_engage","phase_type":"contact","tcp_position_centroid":[0.50489,0.12467,0.03667]},{"body_a":"attachment","body_b":"peg","contact_count":2.0,"contact_point_centroid":[0.50786,0.11031,0.0355],"force_p95":145.41916,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":152.8552,"mean_force":78.49484,"phase_index":2.0,"phase_name":"contact_engage","phase_type":"contact","tcp_position_centroid":[0.50805,0.12175,0.03473]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":11.0,"contact_point_centroid":[0.52699,0.11863,0.0597],"force_p95":116.21263,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":123.705,"mean_force":34.90926,"phase_index":4.0,"phase_name":"lift_up","phase_type":"retract","tcp_position_centroid":[0.51234,0.11591,0.03097]},{"body_a":"peg","body_b":"channel_base_body","contact_count":587.0,"contact_point_centroid":[0.50624,0.1022,0.00944],"force_p95":35.85298,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":82.3022,"mean_force":4.14857,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.51023,0.14048,0.09116]},{"body_a":"attachment","body_b":"peg","contact_count":39.0,"contact_point_centroid":[0.51131,0.12107,0.0575],"force_p95":80.34003,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":81.78968,"mean_force":54.50026,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.50643,0.1316,0.05753]},{"body_a":"attachment","body_b":"peg","contact_count":20.0,"contact_point_centroid":[0.50693,0.09227,0.03908],"force_p95":19.44948,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":23.39477,"mean_force":3.26764,"phase_index":4.0,"phase_name":"lift_up","phase_type":"retract","tcp_position_centroid":[0.50647,0.10365,0.0378]},{"body_a":"peg","body_b":"channel_base_body","contact_count":179.0,"contact_point_centroid":[0.50451,0.04022,0.00863],"force_p95":3.02579,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":22.79824,"mean_force":1.11755,"phase_index":4.0,"phase_name":"lift_up","phase_type":"retract","tcp_position_centroid":[0.50499,0.03962,0.07445]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":40.0,"contact_point_centroid":[0.52573,0.06459,0.04983],"force_p95":6.95657,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":13.17417,"mean_force":1.2841,"phase_index":4.0,"phase_name":"lift_up","phase_type":"retract","tcp_position_centroid":[0.50654,0.08993,0.04613]},{"body_a":"peg","body_b":"channel_base_body","contact_count":466.0,"contact_point_centroid":[0.50557,0.10472,0.00937],"force_p95":0.57839,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.33087,"mean_force":0.57062,"phase_index":0.0,"phase_name":"approach_high","phase_type":"approach","tcp_position_centroid":[0.50921,0.17653,0.21968]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":32.0,"contact_point_centroid":[0.52975,0.10463,0.03425],"force_p95":1.06006,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.32726,"mean_force":0.42874,"phase_index":0.0,"phase_name":"approach_high","phase_type":"approach","tcp_position_centroid":[0.49998,0.19875,0.2964]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":1.0,"contact_point_centroid":[0.52504,0.06665,0.06],"force_p95":1.96013,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.96013,"mean_force":1.96013,"phase_index":3.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.51316,0.11707,0.03234]},{"body_a":"attachment","body_b":"peg","contact_count":3.0,"contact_point_centroid":[0.51026,0.10746,0.03448],"force_p95":0.78819,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.80136,"mean_force":0.67778,"phase_index":3.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.51202,0.11828,0.03288]}],"total_contact_groups":13},"final_pose_error":0.04957,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50433,0.03107,0.02449],"final_tcp_position":[0.50168,-0.03972,0.12115],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.5244,0.10464,0.04]},"peak_contact_force":3911.3352,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":493.0,"n_steps_budget":960.0,"object_pos_end":[0.506,0.10464,0.03384],"object_pos_start":[0.5244,0.10464,0.04],"object_to_goal_dist_end":0.18484,"object_to_goal_dist_start":0.18624,"object_z_max":0.04,"peak_contact_force":0.53947,"phase_name":"approach_high","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":498.0,"raw_peak_contact_force":3.33087,"subtask_id":"approach","tcp_end":[0.5194,0.15531,0.14796],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.12558,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":588.0,"n_steps_budget":1000.0,"object_pos_end":[0.50432,0.08399,0.04072],"object_pos_start":[0.506,0.10464,0.03384],"object_to_goal_dist_end":0.16405,"object_to_goal_dist_start":0.18484,"object_z_max":0.04078,"peak_contact_force":0.48266,"phase_name":"descend_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":626.0,"raw_peak_contact_force":82.3022,"tcp_end":[0.50343,0.12614,0.03779],"tcp_start":[0.5194,0.15531,0.14796],"tcp_to_object_dist_end":0.04226,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":7.0,"n_steps_budget":600.0,"object_pos_end":[0.50561,0.08229,0.04099],"object_pos_start":[0.50432,0.08399,0.04072],"object_to_goal_dist_end":0.16239,"object_to_goal_dist_start":0.16405,"object_z_max":0.04084,"peak_contact_force":3911.3352,"phase_name":"contact_engage","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":7.0,"raw_peak_contact_force":154.14202,"subtask_id":"contact","tcp_end":[0.51075,0.11956,0.03348],"tcp_start":[0.50343,0.12614,0.03779],"tcp_to_object_dist_end":0.03836,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.50629,0.08158,0.04109],"object_pos_start":[0.50561,0.08229,0.04099],"object_to_goal_dist_end":0.16171,"object_to_goal_dist_start":0.16239,"object_z_max":0.04113,"peak_contact_force":1244.86584,"phase_name":"push_through_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":7.0,"raw_peak_contact_force":1650.55334,"subtask_id":"push","tcp_end":[0.51392,0.11607,0.03205],"tcp_start":[0.51316,0.11707,0.03234],"tcp_to_object_dist_end":0.03646,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":212.0,"n_steps_budget":1000.0,"object_pos_end":[0.50433,0.03107,0.02449],"object_pos_start":[0.50741,0.0801,0.04109],"object_to_goal_dist_end":0.11223,"object_to_goal_dist_start":0.16027,"object_z_max":0.04109,"peak_contact_force":0.55944,"phase_name":"lift_up","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":250.0,"raw_peak_contact_force":123.705,"tcp_end":[0.50168,-0.03972,0.12115],"tcp_start":[0.51392,0.11607,0.03205],"tcp_to_object_dist_end":0.11984,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```