## Search State

- **Seed**: 7
- **Iteration**: 6 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 5 | approach → contact → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | admittance_control | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 8 | -0.1835 | 0.03 | ❌ rejected |
| 4 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 7 | 0.1032 | 0.33 | ❌ rejected |
| 3 | approach → contact → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | force_exceeded | pose_tolerance | 7 | -0.1366 | 0.02 | ❌ rejected |
| 2 | align → approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | force_threshold_switch | admittance_control | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 6 | 0.3441 | 0.62 | ❌ rejected |
| 1 | align → approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | force_threshold_switch | admittance_control | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 6 | 0.3446 | 0.63 | ✅ accepted |

**Proposal policy**: task_score is 0.03 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `d0d8b50673ee8d816e4de306a6620129fbd254b61025859fc8d57d0983f18415`
- Frozen object start: [0.5100076373283734, 0.11177710407756605, 0.04]
- Frozen task target: [0.5100076373283734, -0.04822289592243395, 0.04]
- Goal object position: (0.5100076373283734, -0.04822289592243395, 0.04)
- Task success criterion: peg must traverse the channel (0.16 m long) along axis (0.0, -1.0, 0.0); score = axial progress × lateral alignment — NOT a fixed TCP endpoint
- Object initial pose: (0.5100076373283734, 0.11177710407756605, 0.04)
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
  frozen_object_start: [0.51, 0.1118, 0.04]
  frozen_task_target: [0.51, -0.0482, 0.04]
  frozen_fixture_position: [0.54, 0, 0.035]
  frozen_object_starts: {'peg': [0.5100076373283734, 0.11177710407756605, 0.04]}
  frozen_targets: {'channel_exit': [0.5100076373283734, -0.04822289592243395, 0.04]}
  frozen_fixtures: {'channel_left_wall': [0.54, 0.0, 0.035], 'channel_right_wall': [0.46, 0.0, 0.035]}
  channel_axis: [0, -1, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 40
  channel_length_m: 0.16
  force_scale_n: 5
  realized_scene_sha256: d0d8b50673ee8d816e4de306a6620129fbd254b61025859fc8d57d0983f18415

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

## Current Skill (Q=-0.183) — your mutation base

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
  control: admittance_control
  termination: force_exceeded
  parameters:
    contact_force:
      type: scalar
      range:
      - 1.0
      - 20.0
    speed:
      type: scalar
      range:
      - 0.005
      - 0.05
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

- **Composite score**: -0.183
- **task_score** (E): 0.029
- **fitness_score**: 0.165  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.111
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.460

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach | 1.00 | 1.00 | 0.2352 |
| contact | 0.33 | 1.00 | 0.0342 |
| push | 0.00 | 1.00 | 0.0012 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.505, 0.130, 0.078) | (0.509, 0.098, 0.040)→(0.502, 0.098, 0.034) | 0.179→0.178 | 1.00 / 1.000 | 0.519 | 2.732 |
| contact | contact | 0.33 / step_budget | (0.505, 0.130, 0.078)→(0.502, 0.120, 0.046) | (0.502, 0.098, 0.034)→(0.502, 0.093, 0.034) | 0.178→0.173 | 1.00 / 1.667 | 28.803 | 34.253 |
| push | push | 0.00 / guard_failure | (0.502, 0.120, 0.046)→(0.502, 0.121, 0.045) | (0.502, 0.093, 0.034)→(0.503, 0.093, 0.034) | 0.173→0.173 | 1.00 / 2.000 | 43.918 | 43.918 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.000
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.000
- phase_score: 0.227
- phase_breakdown.push_score: 0.034
- phase_breakdown.contact_score: 0.582
- phase_breakdown.approach_score: 0.453

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.184
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.049
- **Median Q (composite search score)**: -0.276
- **K-run variance**: 0.0187
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.310


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `474e87cb3f7f98c9c8d99c8760356b7c026b70b97898f68d5a6c39ba94bca956`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.04,0.04]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `a79e5fd8fc80d9ecadd30a274b12d8d7e7d0841df5ca68ae512c46dc86b114e6`; realized-scene SHA-256: `d0d8b50673ee8d816e4de306a6620129fbd254b61025859fc8d57d0983f18415`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.51001,0.11178,0.04]},{"name":"goal","value":[0.51001,-0.04822,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.51001,0.11178,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.51001,-0.04822,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.76159,"average_solve_count":151.0,"average_success_count":151.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach.lateral_offset":-0.00446,"approach.speed":0.05031,"contact.contact_force":11.39172,"contact.speed":0.02234,"push.min_push_force":3.41713,"push.push_distance":0.05634,"push.push_speed":0.0479,"retract.speed":0.07489},"optimized_scores":{"best_composite_score":-0.28389,"best_fitness_score":0.17611,"best_task_score":0.0494},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.54825,0.12,0.05999],"force_p95":78.53562,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":78.53562,"mean_force":78.53562,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.49919,0.13674,0.03458]},{"body_a":"peg","body_b":"channel_base_body","contact_count":258.0,"contact_point_centroid":[0.50425,0.1015,0.00961],"force_p95":9.50412,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":11.11588,"mean_force":2.80859,"phase_index":1.0,"phase_name":"contact","phase_type":"contact","tcp_position_centroid":[0.50173,0.14163,0.05643]},{"body_a":"attachment","body_b":"peg","contact_count":81.0,"contact_point_centroid":[0.5031,0.12543,0.04829],"force_p95":9.68513,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":10.88201,"mean_force":7.47091,"phase_index":1.0,"phase_name":"contact","phase_type":"contact","tcp_position_centroid":[0.50057,0.13734,0.04474]},{"body_a":"peg","body_b":"channel_base_body","contact_count":731.0,"contact_point_centroid":[0.50362,0.11164,0.00938],"force_p95":0.6049,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06328,"mean_force":0.55486,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.50206,0.17395,0.18595]},{"body_a":"peg","body_b":"channel_base_body","contact_count":17.0,"contact_point_centroid":[0.50281,0.10069,0.00986],"force_p95":0.60679,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.63364,"mean_force":0.50002,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.49962,0.13482,0.03533]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":16.0,"contact_point_centroid":[0.52601,0.11178,0.02875],"force_p95":0.50724,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54079,"mean_force":0.34334,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.49972,0.19944,0.29906]}],"total_contact_groups":6},"final_pose_error":0.05345,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50502,0.10387,0.03445],"final_tcp_position":[0.49916,0.13707,0.03452],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.51001,0.11178,0.04]},"peak_contact_force":78.53562,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":753.0,"n_steps_budget":1000.0,"object_pos_end":[0.50373,0.11175,0.03385],"object_pos_start":[0.51001,0.11178,0.04],"object_to_goal_dist_end":0.19188,"object_to_goal_dist_start":0.19204,"object_z_max":0.04,"peak_contact_force":0.50916,"phase_name":"approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":747.0,"raw_peak_contact_force":2.06328,"subtask_id":"approach","tcp_end":[0.50577,0.14945,0.07859],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.05854,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":262.0,"n_steps_budget":1000.0,"object_pos_end":[0.50481,0.10415,0.03494],"object_pos_start":[0.50373,0.11175,0.03385],"object_to_goal_dist_end":0.18429,"object_to_goal_dist_start":0.19188,"object_z_max":0.03586,"peak_contact_force":0.46311,"phase_name":"contact","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":339.0,"raw_peak_contact_force":11.11588,"subtask_id":"contact","tcp_end":[0.5001,0.13414,0.0362],"tcp_start":[0.50577,0.14945,0.07859],"tcp_to_object_dist_end":0.03038,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":17.0,"n_steps_budget":750.0,"object_pos_end":[0.50502,0.10387,0.03445],"object_pos_start":[0.50481,0.10415,0.03494],"object_to_goal_dist_end":0.18402,"object_to_goal_dist_start":0.18429,"object_z_max":0.03495,"peak_contact_force":78.53562,"phase_name":"push","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":18.0,"raw_peak_contact_force":78.53562,"subtask_id":"push","tcp_end":[0.49916,0.13707,0.03452],"tcp_start":[0.5001,0.13414,0.0362],"tcp_to_object_dist_end":0.03371,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `3ca2e925d364d2c0fe81fb71ee31d40f947a20e349a0720e1c44a2dd2bc628da`; realized-scene SHA-256: `c5fb87552d009c7e1ef813cadc54d289d6d9c896c1dd51a37fa468bf6305165e`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.48616,0.11898,0.04]},{"name":"goal","value":[0.48616,-0.04102,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.48616,0.11898,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.48616,-0.04102,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.73077,"average_solve_count":104.0,"average_success_count":104.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach.lateral_offset":-0.00943,"approach.speed":0.11841,"contact.contact_force":9.35862,"contact.speed":0.01334,"push.min_push_force":2.66691,"push.push_distance":0.12438,"push.push_speed":0.04281,"retract.speed":0.06637},"optimized_scores":{"best_composite_score":-0.27629,"best_fitness_score":0.18371,"best_task_score":0.03815},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.49856,0.10114,0.00987],"force_p95":2.20477,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.11608,"mean_force":1.33639,"phase_index":1.0,"phase_name":"contact","phase_type":"contact","tcp_position_centroid":[0.48644,0.144,0.05021]},{"body_a":"attachment","body_b":"peg","contact_count":689.0,"contact_point_centroid":[0.49446,0.13136,0.05826],"force_p95":2.07519,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":6.77718,"mean_force":1.32714,"phase_index":1.0,"phase_name":"contact","phase_type":"contact","tcp_position_centroid":[0.48723,0.14301,0.04646]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1.0,"contact_point_centroid":[0.48632,0.09632,0.00973],"force_p95":3.29401,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.29401,"mean_force":3.29401,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.4895,0.14066,0.03793]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.4962,0.12887,0.05159],"force_p95":3.09867,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":3.09867,"mean_force":3.09867,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.4895,0.14066,0.03793]},{"body_a":"peg","body_b":"channel_base_body","contact_count":642.0,"contact_point_centroid":[0.49623,0.11912,0.00941],"force_p95":0.60384,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.24822,"mean_force":0.55322,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.49078,0.17487,0.1855]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":24.0,"contact_point_centroid":[0.47288,0.11898,0.03087],"force_p95":0.72905,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.86893,"mean_force":0.3628,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.49947,0.19917,0.2976]}],"total_contact_groups":6},"final_pose_error":0.12439,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49677,0.1109,0.03449],"final_tcp_position":[0.48948,0.14065,0.03789],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48616,0.11898,0.04]},"peak_contact_force":7.11608,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":667.0,"n_steps_budget":1000.0,"object_pos_end":[0.49608,0.11924,0.03397],"object_pos_start":[0.48616,0.11898,0.04],"object_to_goal_dist_end":0.19937,"object_to_goal_dist_start":0.19946,"object_z_max":0.04,"peak_contact_force":0.50653,"phase_name":"approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":666.0,"raw_peak_contact_force":2.24822,"subtask_id":"approach","tcp_end":[0.48347,0.15158,0.07918],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.05701,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49675,0.11092,0.03449],"object_pos_start":[0.49608,0.11924,0.03397],"object_to_goal_dist_end":0.19103,"object_to_goal_dist_start":0.19937,"object_z_max":0.03565,"peak_contact_force":1.41795,"phase_name":"contact","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1689.0,"raw_peak_contact_force":7.11608,"subtask_id":"contact","tcp_end":[0.4895,0.14066,0.03793],"tcp_start":[0.48347,0.15158,0.07918],"tcp_to_object_dist_end":0.0308,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.49677,0.1109,0.03449],"object_pos_start":[0.49675,0.11092,0.03449],"object_to_goal_dist_end":0.19101,"object_to_goal_dist_start":0.19103,"object_z_max":0.03449,"peak_contact_force":3.29401,"phase_name":"push","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2.0,"raw_peak_contact_force":3.29401,"subtask_id":"push","tcp_end":[0.48948,0.14065,0.03789],"tcp_start":[0.4895,0.14066,0.03793],"tcp_to_object_dist_end":0.03082,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `f85f1938a541e3d507519c8f918b8ca98f1f9baf6ab2f6f3ba2c32478e079e47`; realized-scene SHA-256: `a0d7ea14565b0a67e86de15fa43f3773b761884db645527685cd53e0fd95aeb9`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.52962,0.06295,0.04]},{"name":"goal","value":[0.52962,-0.09705,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.52962,0.06295,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.52962,-0.09705,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.54217,"average_solve_count":83.0,"average_success_count":83.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach.lateral_offset":-0.01999,"approach.speed":0.08275,"contact.contact_force":11.85561,"contact.speed":0.02317,"push.min_push_force":2.22336,"push.push_distance":0.11177,"push.push_speed":0.01762,"retract.speed":0.07765},"optimized_scores":{"best_composite_score":0.00975,"best_fitness_score":0.13641,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_left_wall","contact_count":1.0,"contact_point_centroid":[0.52906,0.08659,0.05991],"force_p95":84.52745,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":84.52745,"mean_force":84.52745,"phase_index":1.0,"phase_name":"contact","phase_type":"contact","tcp_position_centroid":[0.51791,0.08663,0.06426]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":1.0,"contact_point_centroid":[0.52898,0.08657,0.05982],"force_p95":49.9233,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":49.9233,"mean_force":49.9233,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.51784,0.08661,0.06409]},{"body_a":"peg","body_b":"channel_base_body","contact_count":790.0,"contact_point_centroid":[0.50585,0.06299,0.00937],"force_p95":0.55634,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.88411,"mean_force":0.56368,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.51163,0.1422,0.18316]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":34.0,"contact_point_centroid":[0.53102,0.06295,0.03156],"force_p95":1.1362,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.98455,"mean_force":0.48262,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.49978,0.19821,0.29642]},{"body_a":"peg","body_b":"channel_base_body","contact_count":63.0,"contact_point_centroid":[0.50551,0.0624,0.00938],"force_p95":0.5507,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.5515,"mean_force":0.54666,"phase_index":1.0,"phase_name":"contact","phase_type":"contact","tcp_position_centroid":[0.52109,0.08729,0.07043]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1.0,"contact_point_centroid":[0.48941,0.06997,0.00938],"force_p95":0.5476,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.5476,"mean_force":0.5476,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.51784,0.08661,0.06409]}],"total_contact_groups":6},"final_pose_error":0.11179,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50595,0.06303,0.0338],"final_tcp_position":[0.51778,0.08659,0.06396],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.52962,0.06295,0.04]},"peak_contact_force":84.52745,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":818.0,"n_steps_budget":1000.0,"object_pos_end":[0.50598,0.06294,0.03381],"object_pos_start":[0.52962,0.06295,0.04],"object_to_goal_dist_end":0.1432,"object_to_goal_dist_start":0.14598,"object_z_max":0.04001,"peak_contact_force":0.54163,"phase_name":"approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":824.0,"raw_peak_contact_force":3.88411,"subtask_id":"approach","tcp_end":[0.52432,0.08827,0.07637],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.05282,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":63.0,"n_steps_budget":1000.0,"object_pos_end":[0.50593,0.06301,0.0338],"object_pos_start":[0.50598,0.06294,0.03381],"object_to_goal_dist_end":0.14326,"object_to_goal_dist_start":0.1432,"object_z_max":0.03381,"peak_contact_force":84.52745,"phase_name":"contact","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":64.0,"raw_peak_contact_force":84.52745,"subtask_id":"contact","tcp_end":[0.51784,0.08661,0.06409],"tcp_start":[0.52432,0.08827,0.07637],"tcp_to_object_dist_end":0.0402,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.50595,0.06303,0.0338],"object_pos_start":[0.50593,0.06301,0.0338],"object_to_goal_dist_end":0.14329,"object_to_goal_dist_start":0.14326,"object_z_max":0.0338,"peak_contact_force":49.9233,"phase_name":"push","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2.0,"raw_peak_contact_force":49.9233,"subtask_id":"push","tcp_end":[0.51778,0.08659,0.06396],"tcp_start":[0.51784,0.08661,0.06409],"tcp_to_object_dist_end":0.04005,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```