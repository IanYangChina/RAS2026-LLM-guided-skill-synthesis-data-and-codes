## Search State

- **Seed**: 7
- **Iteration**: 15 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 14 | approach → contact → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 7 | -0.1045 | 0.00 | ❌ rejected |
| 13 | approach → contact → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 6 | -0.0622 | 0.03 | ❌ rejected |
| 12 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 5 | 0.0636 | 0.12 | ❌ rejected |
| 11 | approach → contact → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 5 | 0.3569 | 0.52 | ❌ rejected |
| 10 | approach → contact → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 5 | -0.0909 | 0.00 | ❌ rejected |

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

## Current Skill (Q=-0.105) — your mutation base

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

- **Composite score**: -0.105
- **task_score** (E): 0.000
- **fitness_score**: 0.111  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.194
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.410

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1893 |
| contact_1 | 0.67 | 1.00 | 0.0773 |
| push_1 | 0.00 | 1.00 | 0.0024 |
| retract_1 | 1.00 | 1.00 | 0.0578 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.505, 0.128, 0.128) | (0.509, 0.098, 0.040)→(0.502, 0.098, 0.034) | 0.179→0.178 | 1.00 / 1.000 | 0.559 | 2.732 |
| contact_1 | contact | 0.67 / force_exceeded | (0.505, 0.128, 0.128)→(0.500, 0.119, 0.052) | (0.502, 0.098, 0.034)→(0.505, 0.111, 0.027) | 0.178→0.192 | 1.00 / 1.667 | 21.483 | 22.288 |
| push_1 | push | 0.00 / guard_failure | (0.500, 0.119, 0.052)→(0.502, 0.120, 0.051) | (0.505, 0.111, 0.027)→(0.505, 0.112, 0.027) | 0.192→0.192 | 1.00 / 2.000 | 71.574 | 60.054 |
| retract_1 | retract | 1.00 / step_budget | (0.509, 0.085, 0.060)→(0.503, 0.067, 0.115) | (0.506, 0.063, 0.034)→(0.506, 0.063, 0.034) | 0.143→0.143 | 1.00 / 1.000 | 0.548 | 23.091 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.000
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.000
- phase_score: 0.171
- phase_breakdown.push_score: 0.014
- phase_breakdown.contact_score: 0.644
- phase_breakdown.approach_score: 0.167

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.129
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.001
- **Median Q (composite search score)**: -0.058
- **K-run variance**: 0.0168
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.408


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.85795,"average_solve_count":176.0,"average_success_count":176.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_offset_y":0.02053,"approach_1.speed":0.01986,"contact_1.contact_force":14.76184,"contact_1.speed":0.0273,"push_1.push_distance":0.11096,"push_1.speed":0.03242,"retract_1.speed":0.05281},"optimized_scores":{"best_composite_score":0.02573,"best_fitness_score":0.10239,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":1.0,"contact_point_centroid":[0.51952,0.12,0.00937],"force_p95":59.82788,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":59.82788,"mean_force":59.82788,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50085,0.13234,0.05997]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.51185,0.12785,0.05853],"force_p95":58.03244,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":58.03244,"mean_force":58.03244,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50085,0.13234,0.05997]},{"body_a":"peg","body_b":"channel_base_body","contact_count":386.0,"contact_point_centroid":[0.50363,0.11162,0.00941],"force_p95":0.61091,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":32.70145,"mean_force":0.64984,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50232,0.13405,0.09319]},{"body_a":"attachment","body_b":"peg","contact_count":2.0,"contact_point_centroid":[0.51181,0.12778,0.05867],"force_p95":30.9328,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":32.10232,"mean_force":20.40712,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50083,0.13234,0.06021]},{"body_a":"peg","body_b":"channel_base_body","contact_count":601.0,"contact_point_centroid":[0.5036,0.11169,0.00938],"force_p95":0.61524,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06328,"mean_force":0.55683,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50226,0.16733,0.21087]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":16.0,"contact_point_centroid":[0.52601,0.11178,0.02875],"force_p95":0.50724,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54079,"mean_force":0.34334,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49971,0.19938,0.29923]}],"total_contact_groups":6},"final_pose_error":0.13449,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50383,0.11194,0.03386],"final_tcp_position":[0.50097,0.13271,0.05977],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.51001,0.11178,0.04]},"peak_contact_force":59.82788,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":623.0,"n_steps_budget":1000.0,"object_pos_end":[0.50371,0.11176,0.03392],"object_pos_start":[0.51001,0.11178,0.04],"object_to_goal_dist_end":0.19189,"object_to_goal_dist_start":0.19204,"object_z_max":0.04,"peak_contact_force":0.50918,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":617.0,"raw_peak_contact_force":2.06328,"subtask_id":"approach","tcp_end":[0.50617,0.13638,0.12802],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.0973,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":386.0,"n_steps_budget":1000.0,"object_pos_end":[0.50375,0.11175,0.03377],"object_pos_start":[0.50371,0.11176,0.03392],"object_to_goal_dist_end":0.19189,"object_to_goal_dist_start":0.19189,"object_z_max":0.03397,"peak_contact_force":32.70145,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":388.0,"raw_peak_contact_force":32.70145,"subtask_id":"contact","tcp_end":[0.50085,0.13234,0.05997],"tcp_start":[0.50617,0.13638,0.12802],"tcp_to_object_dist_end":0.03345,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.50383,0.11194,0.03386],"object_pos_start":[0.50375,0.11175,0.03377],"object_to_goal_dist_end":0.19208,"object_to_goal_dist_start":0.19189,"object_z_max":0.03377,"peak_contact_force":59.82788,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2.0,"raw_peak_contact_force":59.82788,"subtask_id":"push","tcp_end":[0.50097,0.13271,0.05977],"tcp_start":[0.50085,0.13234,0.05997],"tcp_to_object_dist_end":0.03333,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.85065,"average_solve_count":154.0,"average_success_count":154.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_offset_y":0.03536,"approach_1.speed":0.06263,"contact_1.contact_force":11.32665,"contact_1.speed":0.02317,"push_1.push_distance":0.12435,"push_1.speed":0.06479,"retract_1.speed":0.05601},"optimized_scores":{"best_composite_score":-0.28102,"best_fitness_score":0.12898,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg","contact_count":2.0,"contact_point_centroid":[0.50558,0.14292,0.03168],"force_p95":114.93033,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":120.33371,"mean_force":66.29987,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49382,0.14297,0.03333]},{"body_a":"peg","body_b":"world","contact_count":7.0,"contact_point_centroid":[0.50508,0.15605,-0.00201],"force_p95":86.76571,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":119.29847,"mean_force":19.02704,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49237,0.14134,0.03457]},{"body_a":"peg","body_b":"world","contact_count":401.0,"contact_point_centroid":[0.50018,0.15766,-0.00181],"force_p95":0.80684,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.01697,"mean_force":0.61916,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.48825,0.14453,0.06253]},{"body_a":"peg","body_b":"channel_base_body","contact_count":535.0,"contact_point_centroid":[0.49631,0.11916,0.00943],"force_p95":0.61751,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.24822,"mean_force":0.5541,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49118,0.17759,0.21092]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":24.0,"contact_point_centroid":[0.47288,0.11898,0.03087],"force_p95":0.72905,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.86893,"mean_force":0.3628,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49949,0.19916,0.29785]},{"body_a":"peg","body_b":"channel_base_body","contact_count":251.0,"contact_point_centroid":[0.49626,0.11969,0.00942],"force_p95":0.61702,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.62289,"mean_force":0.52018,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.48357,0.15308,0.10894]}],"total_contact_groups":6},"final_pose_error":0.11051,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50571,0.15974,0.01367],"final_tcp_position":[0.49557,0.1438,0.03224],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48616,0.11898,0.04]},"peak_contact_force":120.33371,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":560.0,"n_steps_budget":1000.0,"object_pos_end":[0.49597,0.11942,0.03388],"object_pos_start":[0.48616,0.11898,0.04],"object_to_goal_dist_end":0.19956,"object_to_goal_dist_start":0.19946,"object_z_max":0.04,"peak_contact_force":0.61501,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":559.0,"raw_peak_contact_force":2.24822,"subtask_id":"approach","tcp_end":[0.48421,0.15693,0.12927],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.10318,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":655.0,"n_steps_budget":1000.0,"object_pos_end":[0.50526,0.15956,0.01413],"object_pos_start":[0.49597,0.11942,0.03388],"object_to_goal_dist_end":0.24101,"object_to_goal_dist_start":0.19956,"object_z_max":0.03388,"peak_contact_force":0.60182,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":652.0,"raw_peak_contact_force":3.01697,"subtask_id":"contact","tcp_end":[0.49133,0.13957,0.03567],"tcp_start":[0.48421,0.15693,0.12927],"tcp_to_object_dist_end":0.03252,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":7.0,"n_steps_budget":1000.0,"object_pos_end":[0.50571,0.15974,0.01367],"object_pos_start":[0.50526,0.15956,0.01413],"object_to_goal_dist_end":0.24125,"object_to_goal_dist_start":0.24101,"object_z_max":0.01413,"peak_contact_force":120.33371,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":9.0,"raw_peak_contact_force":120.33371,"subtask_id":"push","tcp_end":[0.49557,0.1438,0.03224],"tcp_start":[0.49133,0.13957,0.03567],"tcp_to_object_dist_end":0.02649,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":55.0,"average_failure_rate":0.20446,"average_mean_iterations":43.24535,"average_solve_count":269.0,"average_success_count":214.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_offset_y":0.0214,"approach_1.speed":0.03093,"contact_1.contact_force":13.14228,"contact_1.speed":0.03258,"push_1.push_distance":0.13843,"push_1.speed":0.06125,"retract_1.speed":0.03311},"optimized_scores":{"best_composite_score":-0.05829,"best_fitness_score":0.10171,"best_task_score":0.0009},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":327.0,"contact_point_centroid":[0.5059,0.06309,0.00938],"force_p95":0.55236,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":31.1466,"mean_force":0.64015,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.51573,0.08768,0.09253]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.51742,0.07699,0.05869],"force_p95":30.62665,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":30.62665,"mean_force":30.62665,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50854,0.08494,0.05997]},{"body_a":"peg","body_b":"channel_base_body","contact_count":196.0,"contact_point_centroid":[0.50291,0.06197,0.00946],"force_p95":8.12604,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":23.09119,"mean_force":1.42373,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50495,0.07593,0.08527]},{"body_a":"attachment","body_b":"peg","contact_count":23.0,"contact_point_centroid":[0.51593,0.07598,0.0595],"force_p95":21.67984,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":22.55496,"mean_force":7.61646,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50748,0.08438,0.06039]},{"body_a":"peg","body_b":"channel_base_body","contact_count":721.0,"contact_point_centroid":[0.50584,0.06298,0.00936],"force_p95":0.55904,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.88411,"mean_force":0.56533,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51172,0.14345,0.20838]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":34.0,"contact_point_centroid":[0.53102,0.06295,0.03156],"force_p95":1.1362,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.98455,"mean_force":0.48262,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49976,0.19821,0.29701]}],"total_contact_groups":6},"final_pose_error":0.01986,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50571,0.06257,0.03399],"final_tcp_position":[0.50349,0.06687,0.1145],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.52962,0.06295,0.04]},"peak_contact_force":34.56091,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":749.0,"n_steps_budget":1000.0,"object_pos_end":[0.50596,0.06294,0.03381],"object_pos_start":[0.52962,0.06295,0.04],"object_to_goal_dist_end":0.1432,"object_to_goal_dist_start":0.14598,"object_z_max":0.04001,"peak_contact_force":0.55405,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":755.0,"raw_peak_contact_force":3.88411,"subtask_id":"approach","tcp_end":[0.52459,0.0907,0.12557],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.09767,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":327.0,"n_steps_budget":1000.0,"object_pos_end":[0.50604,0.06299,0.03381],"object_pos_start":[0.50596,0.06294,0.03381],"object_to_goal_dist_end":0.14325,"object_to_goal_dist_start":0.1432,"object_z_max":0.03381,"peak_contact_force":31.1466,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":328.0,"raw_peak_contact_force":31.1466,"subtask_id":"contact","tcp_end":[0.50851,0.08493,0.05978],"tcp_start":[0.52459,0.0907,0.12557],"tcp_to_object_dist_end":0.03409,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":0.0,"n_steps_budget":1000.0,"object_pos_end":[0.50604,0.06299,0.03381],"object_pos_start":[0.50604,0.06299,0.03381],"object_to_goal_dist_end":0.14325,"object_to_goal_dist_start":0.14325,"peak_contact_force":34.56091,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"push","tcp_end":[0.50851,0.08493,0.05978],"tcp_start":[0.50851,0.08493,0.05978],"tcp_to_object_dist_end":0.03409,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":196.0,"n_steps_budget":1000.0,"object_pos_end":[0.50571,0.06257,0.03399],"object_pos_start":[0.50604,0.06299,0.03381],"object_to_goal_dist_end":0.14281,"object_to_goal_dist_start":0.14325,"object_z_max":0.03563,"peak_contact_force":0.54802,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":219.0,"raw_peak_contact_force":23.09119,"tcp_end":[0.50349,0.06687,0.1145],"tcp_start":[0.50851,0.08493,0.05978],"tcp_to_object_dist_end":0.08066,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```