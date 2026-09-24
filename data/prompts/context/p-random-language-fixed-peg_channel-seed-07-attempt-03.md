## Search State

- **Seed**: 7
- **Iteration**: 4 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 3 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | 5 | -0.0588 | 0.00 | ❌ rejected |
| 2 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | 5 | 0.1325 | 0.08 | ❌ rejected |
| 1 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | admittance_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | 9 | -0.2770 | 0.00 | ❌ rejected |
| 0 | descend → insert → grasp → approach → align | linear_cartesian | impedance_motion | — | linear_cartesian | linear_cartesian | admittance_control | admittance_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | 5 | -0.1315 | 0.26 | ✅ accepted |

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

## Current Skill (Q=-0.059) — your mutation base

```yaml
skill: peg_channel
skill_type: arm_gripper
phases:
- id: descend_1
  type: descend
  generator: linear_cartesian
  control: admittance_control
  termination: pose_tolerance
- id: insert_1
  type: insert
  generator: impedance_motion
  control: admittance_control
  termination: pose_tolerance
  parameters:
    insertion_depth:
      type: scalar
      range:
      - 0.01
      - 0.15
    insertion_force:
      type: scalar
      range:
      - 1.0
      - 20.0
- id: grasp_1
  type: grasp
  control: position_control
  termination: time_limit
  end_effector_action: force_grasp
- id: approach_1
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  parameters:
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1
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
    lateral_offset_y:
      type: scalar
      range:
      - -0.01
      - 0.01

```

## Design Metrics

- **Composite score**: -0.059
- **task_score** (E): 0.000
- **fitness_score**: 0.221  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.280

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_peg | 1.00 | 1.00 | 0.1652 |
| descend_to_contact | 0.00 | 1.00 | 0.0756 |
| push_along_channel | 1.00 | 1.00 | 0.1760 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_peg | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.505, 0.142, 0.148) | (0.509, 0.098, 0.040)→(0.502, 0.098, 0.034) | 0.179→0.178 | 1.00 / 1.000 | 0.548 | 2.732 |
| descend_to_contact | descend | 0.00 / step_budget | (0.505, 0.142, 0.148)→(0.499, 0.120, 0.077) | (0.502, 0.098, 0.034)→(0.502, 0.098, 0.034) | 0.178→0.178 | 1.00 / 1.000 | 0.532 | 0.616 |
| push_along_channel | push | 1.00 / step_budget | (0.499, 0.120, 0.077)→(0.496, -0.056, 0.072) | (0.502, 0.098, 0.034)→(0.502, 0.098, 0.034) | 0.178→0.178 | 1.00 / 1.000 | 0.543 | 0.613 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.000
- alignment_error: None
- force_efficiency: 0.922
- terminal_score: 0.000
- phase_score: 0.414
- phase_breakdown.approach_score: 0.120
- phase_breakdown.push_score: 0.516
- phase_breakdown.contact_score: 0.403

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.249
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.000
- **Median Q (composite search score)**: -0.066
- **K-run variance**: 0.0004
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.349


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.09677,"average_solve_count":186.0,"average_success_count":186.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_peg.speed":0.06292,"descend_to_contact.contact_force_threshold":8.09493,"descend_to_contact.descend_speed":0.09762,"push_along_channel.push_distance":0.19995,"push_along_channel.push_speed":0.08955},"optimized_scores":{"best_composite_score":-0.06632,"best_fitness_score":0.21368,"best_task_score":0.0004},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":520.0,"contact_point_centroid":[0.5036,0.11168,0.00936],"force_p95":0.6123,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06328,"mean_force":0.56025,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.50229,0.17677,0.22139]},{"body_a":"peg","body_b":"channel_base_body","contact_count":436.0,"contact_point_centroid":[0.50373,0.11162,0.00941],"force_p95":0.59582,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.63552,"mean_force":0.54358,"phase_index":2.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.49746,0.04277,0.07282]},{"body_a":"peg","body_b":"channel_base_body","contact_count":352.0,"contact_point_centroid":[0.50371,0.11171,0.00941],"force_p95":0.60192,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.63359,"mean_force":0.54321,"phase_index":1.0,"phase_name":"descend_to_contact","phase_type":"descend","tcp_position_centroid":[0.50228,0.14416,0.11191]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":16.0,"contact_point_centroid":[0.52601,0.11178,0.02875],"force_p95":0.50724,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54079,"mean_force":0.34334,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.49971,0.19944,0.29928]}],"total_contact_groups":4},"final_pose_error":0.0197,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50369,0.11171,0.03384],"final_tcp_position":[0.49713,-0.04771,0.07236],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.51001,0.11178,0.04]},"peak_contact_force":2.06328,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":542.0,"n_steps_budget":1000.0,"object_pos_end":[0.50375,0.11179,0.03381],"object_pos_start":[0.51001,0.11178,0.04],"object_to_goal_dist_end":0.19193,"object_to_goal_dist_start":0.19204,"object_z_max":0.04,"peak_contact_force":0.54419,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":536.0,"raw_peak_contact_force":2.06328,"subtask_id":"approach","tcp_end":[0.50621,0.15496,0.14845],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.12252,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":352.0,"n_steps_budget":600.0,"object_pos_end":[0.50372,0.11173,0.03386],"object_pos_start":[0.50375,0.11179,0.03381],"object_to_goal_dist_end":0.19186,"object_to_goal_dist_start":0.19193,"object_z_max":0.03392,"peak_contact_force":0.54005,"phase_name":"descend_to_contact","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":352.0,"raw_peak_contact_force":0.63359,"subtask_id":"contact","tcp_end":[0.50041,0.13338,0.07701],"tcp_start":[0.50621,0.15496,0.14845],"tcp_to_object_dist_end":0.0484,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":436.0,"n_steps_budget":1000.0,"object_pos_end":[0.50369,0.11171,0.03384],"object_pos_start":[0.50372,0.11173,0.03386],"object_to_goal_dist_end":0.19184,"object_to_goal_dist_start":0.19186,"object_z_max":0.03392,"peak_contact_force":0.52145,"phase_name":"push_along_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":436.0,"raw_peak_contact_force":0.63552,"subtask_id":"push","tcp_end":[0.49713,-0.04771,0.07236],"tcp_start":[0.50041,0.13338,0.07701],"tcp_to_object_dist_end":0.16414,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.80876,"average_solve_count":251.0,"average_success_count":251.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_peg.speed":0.07905,"descend_to_contact.contact_force_threshold":9.00031,"descend_to_contact.descend_speed":0.13618,"push_along_channel.push_distance":0.19993,"push_along_channel.push_speed":0.03652},"optimized_scores":{"best_composite_score":-0.07859,"best_fitness_score":0.20141,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":500.0,"contact_point_centroid":[0.49628,0.11906,0.00942],"force_p95":0.61009,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.24822,"mean_force":0.55609,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.49132,0.18007,0.22146]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":24.0,"contact_point_centroid":[0.47288,0.11898,0.03087],"force_p95":0.72905,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.86893,"mean_force":0.3628,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.49945,0.19924,0.29826]},{"body_a":"peg","body_b":"channel_base_body","contact_count":427.0,"contact_point_centroid":[0.49614,0.11898,0.00948],"force_p95":0.60214,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.66067,"mean_force":0.53734,"phase_index":1.0,"phase_name":"descend_to_contact","phase_type":"descend","tcp_position_centroid":[0.48681,0.15047,0.1107]},{"body_a":"peg","body_b":"channel_base_body","contact_count":465.0,"contact_point_centroid":[0.49601,0.11927,0.00946],"force_p95":0.58567,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.64893,"mean_force":0.53943,"phase_index":2.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.48849,0.04997,0.07145]}],"total_contact_groups":4},"final_pose_error":0.01968,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.496,0.11997,0.0339],"final_tcp_position":[0.48818,-0.04111,0.07105],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48616,0.11898,0.04]},"peak_contact_force":2.24822,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":525.0,"n_steps_budget":1000.0,"object_pos_end":[0.49599,0.11898,0.03387],"object_pos_start":[0.48616,0.11898,0.04],"object_to_goal_dist_end":0.19912,"object_to_goal_dist_start":0.19946,"object_z_max":0.04,"peak_contact_force":0.55404,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":524.0,"raw_peak_contact_force":2.24822,"subtask_id":"approach","tcp_end":[0.48452,0.16163,0.14924],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.12354,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":427.0,"n_steps_budget":600.0,"object_pos_end":[0.49607,0.1191,0.03388],"object_pos_start":[0.49599,0.11898,0.03387],"object_to_goal_dist_end":0.19923,"object_to_goal_dist_start":0.19912,"object_z_max":0.03425,"peak_contact_force":0.50279,"phase_name":"descend_to_contact","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":427.0,"raw_peak_contact_force":0.66067,"subtask_id":"contact","tcp_end":[0.49144,0.13993,0.07552],"tcp_start":[0.48452,0.16163,0.14924],"tcp_to_object_dist_end":0.04679,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":465.0,"n_steps_budget":1000.0,"object_pos_end":[0.496,0.11997,0.0339],"object_pos_start":[0.49607,0.1191,0.03388],"object_to_goal_dist_end":0.20011,"object_to_goal_dist_start":0.19923,"object_z_max":0.03409,"peak_contact_force":0.56645,"phase_name":"push_along_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":465.0,"raw_peak_contact_force":0.64893,"subtask_id":"push","tcp_end":[0.48818,-0.04111,0.07105],"tcp_start":[0.49144,0.13993,0.07552],"tcp_to_object_dist_end":0.16549,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.05797,"average_solve_count":207.0,"average_success_count":207.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_peg.speed":0.11619,"descend_to_contact.contact_force_threshold":11.98253,"descend_to_contact.descend_speed":0.07746,"push_along_channel.push_distance":0.18439,"push_along_channel.push_speed":0.05662},"optimized_scores":{"best_composite_score":-0.0315,"best_fitness_score":0.2485,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":623.0,"contact_point_centroid":[0.50577,0.06294,0.00936],"force_p95":0.56098,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.88411,"mean_force":0.56828,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.51167,0.15288,0.21883]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":34.0,"contact_point_centroid":[0.53102,0.06295,0.03156],"force_p95":1.1362,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.98455,"mean_force":0.48262,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.4998,0.19832,0.29707]},{"body_a":"peg","body_b":"channel_base_body","contact_count":429.0,"contact_point_centroid":[0.50598,0.06295,0.00938],"force_p95":0.55277,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55532,"mean_force":0.54656,"phase_index":2.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.50167,0.00307,0.07362]},{"body_a":"peg","body_b":"channel_base_body","contact_count":323.0,"contact_point_centroid":[0.5059,0.0631,0.00938],"force_p95":0.55163,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55422,"mean_force":0.54657,"phase_index":1.0,"phase_name":"descend_to_contact","phase_type":"descend","tcp_position_centroid":[0.51392,0.09761,0.11153]}],"total_contact_groups":4},"final_pose_error":0.01965,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50599,0.06304,0.0338],"final_tcp_position":[0.50134,-0.08002,0.07305],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.52962,0.06295,0.04]},"peak_contact_force":3.88411,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":651.0,"n_steps_budget":1000.0,"object_pos_end":[0.50594,0.063,0.03381],"object_pos_start":[0.52962,0.06295,0.04],"object_to_goal_dist_end":0.14326,"object_to_goal_dist_start":0.14598,"object_z_max":0.04001,"peak_contact_force":0.54548,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":657.0,"raw_peak_contact_force":3.88411,"subtask_id":"approach","tcp_end":[0.52446,0.10906,0.14589],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.12259,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":323.0,"n_steps_budget":600.0,"object_pos_end":[0.50601,0.06303,0.03381],"object_pos_start":[0.50594,0.063,0.03381],"object_to_goal_dist_end":0.14329,"object_to_goal_dist_start":0.14326,"object_z_max":0.03381,"peak_contact_force":0.55274,"phase_name":"descend_to_contact","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":323.0,"raw_peak_contact_force":0.55422,"subtask_id":"contact","tcp_end":[0.50468,0.08561,0.07785],"tcp_start":[0.52446,0.10906,0.14589],"tcp_to_object_dist_end":0.04952,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":429.0,"n_steps_budget":1000.0,"object_pos_end":[0.50599,0.06304,0.0338],"object_pos_start":[0.50601,0.06303,0.03381],"object_to_goal_dist_end":0.1433,"object_to_goal_dist_start":0.14329,"object_z_max":0.03381,"peak_contact_force":0.54139,"phase_name":"push_along_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":429.0,"raw_peak_contact_force":0.55532,"subtask_id":"push","tcp_end":[0.50134,-0.08002,0.07305],"tcp_start":[0.50468,0.08561,0.07785],"tcp_to_object_dist_end":0.14841,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```