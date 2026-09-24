## Search State

- **Seed**: 7
- **Iteration**: 2 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
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

## Current Skill (Q=-0.277) — your mutation base

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

- **Composite score**: -0.277
- **task_score** (E): 0.001
- **fitness_score**: 0.203  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.480

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_peg | 1.00 | 1.00 | 0.1952 |
| descend_to_contact | 0.33 | 1.00 | 0.0754 |
| push_along_channel | 0.33 | 1.00 | 0.0684 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_peg | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.514, 0.119, 0.127) | (0.509, 0.098, 0.040)→(0.502, 0.098, 0.034) | 0.179→0.178 | 1.00 / 1.000 | 0.541 | 2.732 |
| descend_to_contact | descend | 0.33 / guard_failure | (0.514, 0.119, 0.127)→(0.504, 0.116, 0.054) | (0.502, 0.098, 0.034)→(0.502, 0.112, 0.027) | 0.178→0.192 | 1.00 / 1.667 | 52.317 | 53.037 |
| push_along_channel | push | 0.33 / guard_failure | (0.504, 0.115, 0.054)→(0.505, 0.047, 0.052) | (0.502, 0.112, 0.027)→(0.513, 0.111, 0.027) | 0.192→0.193 | 1.00 / 1.667 | 17.804 | 45.938 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.000
- alignment_error: None
- force_efficiency: 0.941
- terminal_score: 0.000
- phase_score: 0.660
- phase_breakdown.approach_score: 0.163
- phase_breakdown.push_score: 0.741
- phase_breakdown.contact_score: 0.914

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.396
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.004
- **Median Q (composite search score)**: -0.373
- **K-run variance**: 0.0186
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.49,"average_solve_count":100.0,"average_success_count":100.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_peg.approach_speed":0.08365,"approach_peg.lateral_correction_x":0.0151,"approach_peg.lateral_correction_y":0.01991,"descend_to_contact.descend_contact_y":0.01576,"descend_to_contact.descend_force_threshold":5.92171,"descend_to_contact.descend_speed":0.03861,"push_along_channel.push_force_limit":39.241,"push_along_channel.push_lateral_adjust":-0.0062,"push_along_channel.push_speed":0.05811},"optimized_scores":{"best_composite_score":-0.37349,"best_fitness_score":0.10651,"best_task_score":0.00366},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":13.0,"contact_point_centroid":[0.49105,0.11345,0.00928],"force_p95":39.66659,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":39.75689,"mean_force":26.35276,"phase_index":2.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.50519,0.12866,0.05924]},{"body_a":"attachment","body_b":"peg","contact_count":13.0,"contact_point_centroid":[0.51614,0.12399,0.05824],"force_p95":39.18769,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":39.2391,"mean_force":25.92965,"phase_index":2.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.50519,0.12866,0.05924]},{"body_a":"peg","body_b":"channel_base_body","contact_count":214.0,"contact_point_centroid":[0.5036,0.11161,0.00944],"force_p95":0.59299,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":38.21633,"mean_force":0.71771,"phase_index":1.0,"phase_name":"descend_to_contact","phase_type":"descend","tcp_position_centroid":[0.51205,0.13221,0.09305]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.51659,0.12438,0.05875],"force_p95":37.7253,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":37.7253,"mean_force":37.7253,"phase_index":1.0,"phase_name":"descend_to_contact","phase_type":"descend","tcp_position_centroid":[0.50577,0.12931,0.06029]},{"body_a":"peg","body_b":"channel_base_body","contact_count":569.0,"contact_point_centroid":[0.50365,0.11173,0.00936],"force_p95":0.62102,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06328,"mean_force":0.55917,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.50945,0.16691,0.2104]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":16.0,"contact_point_centroid":[0.52601,0.11178,0.02875],"force_p95":0.50724,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54079,"mean_force":0.34334,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.49989,0.19931,0.29897]}],"total_contact_groups":6},"final_pose_error":0.20833,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50291,0.11113,0.03369],"final_tcp_position":[0.50493,0.12742,0.05877],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.51001,0.11178,0.04]},"peak_contact_force":39.75689,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":591.0,"n_steps_budget":1000.0,"object_pos_end":[0.5037,0.11175,0.0338],"object_pos_start":[0.51001,0.11178,0.04],"object_to_goal_dist_end":0.19188,"object_to_goal_dist_start":0.19204,"object_z_max":0.04,"peak_contact_force":0.5233,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":585.0,"raw_peak_contact_force":2.06328,"tcp_end":[0.52009,0.13572,0.12758],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.09818,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":214.0,"n_steps_budget":1000.0,"object_pos_end":[0.50375,0.11176,0.03383],"object_pos_start":[0.5037,0.11175,0.0338],"object_to_goal_dist_end":0.19189,"object_to_goal_dist_start":0.19188,"object_z_max":0.03402,"peak_contact_force":38.21633,"phase_name":"descend_to_contact","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":215.0,"raw_peak_contact_force":38.21633,"subtask_id":"contact","tcp_end":[0.50573,0.1293,0.06],"tcp_start":[0.52009,0.13572,0.12758],"tcp_to_object_dist_end":0.03157,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":13.0,"n_steps_budget":1000.0,"object_pos_end":[0.50293,0.11137,0.03371],"object_pos_start":[0.50375,0.11176,0.03383],"object_to_goal_dist_end":0.1915,"object_to_goal_dist_start":0.19189,"object_z_max":0.03383,"peak_contact_force":1.08309,"phase_name":"push_along_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":26.0,"raw_peak_contact_force":39.75689,"subtask_id":"push","tcp_end":[0.50493,0.12742,0.05877],"tcp_start":[0.50495,0.12755,0.05884],"tcp_to_object_dist_end":0.02983,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.0754,"average_solve_count":252.0,"average_success_count":252.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_peg.approach_speed":0.01219,"approach_peg.lateral_correction_x":-0.00585,"approach_peg.lateral_correction_y":0.01999,"descend_to_contact.descend_contact_y":0.0195,"descend_to_contact.descend_force_threshold":25.61472,"descend_to_contact.descend_speed":0.02916,"push_along_channel.push_force_limit":35.81286,"push_along_channel.push_lateral_adjust":0.00391,"push_along_channel.push_speed":0.06982},"optimized_scores":{"best_composite_score":-0.08392,"best_fitness_score":0.39608,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"world","contact_count":194.0,"contact_point_centroid":[0.49642,0.15564,-0.00164],"force_p95":1.03698,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.93059,"mean_force":0.63287,"phase_index":1.0,"phase_name":"descend_to_contact","phase_type":"descend","tcp_position_centroid":[0.48593,0.13951,0.06697]},{"body_a":"peg","body_b":"channel_base_body","contact_count":574.0,"contact_point_centroid":[0.49619,0.11913,0.00944],"force_p95":0.62374,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.24822,"mean_force":0.55285,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.48839,0.1704,0.21095]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":24.0,"contact_point_centroid":[0.47288,0.11898,0.03087],"force_p95":0.72905,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.86893,"mean_force":0.3628,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.49941,0.19911,0.29816]},{"body_a":"peg","body_b":"world","contact_count":692.0,"contact_point_centroid":[0.50986,0.16003,-0.00203],"force_p95":0.77047,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.77052,"mean_force":0.60597,"phase_index":2.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.49154,0.03465,0.0368]},{"body_a":"peg","body_b":"channel_base_body","contact_count":134.0,"contact_point_centroid":[0.49524,0.11991,0.00945],"force_p95":0.59565,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.60541,"mean_force":0.50224,"phase_index":1.0,"phase_name":"descend_to_contact","phase_type":"descend","tcp_position_centroid":[0.4792,0.14135,0.11004]}],"total_contact_groups":5},"final_pose_error":0.01497,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.52963,0.16003,0.01405],"final_tcp_position":[0.49582,-0.06632,0.03558],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48616,0.11898,0.04]},"peak_contact_force":2.93059,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":599.0,"n_steps_budget":1000.0,"object_pos_end":[0.496,0.11938,0.03381],"object_pos_start":[0.48616,0.11898,0.04],"object_to_goal_dist_end":0.19951,"object_to_goal_dist_start":0.19946,"object_z_max":0.04,"peak_contact_force":0.55275,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":598.0,"raw_peak_contact_force":2.24822,"tcp_end":[0.47882,0.1427,0.12897],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.09947,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":332.0,"n_steps_budget":1000.0,"object_pos_end":[0.49744,0.16002,0.01404],"object_pos_start":[0.496,0.11938,0.03381],"object_to_goal_dist_end":0.24144,"object_to_goal_dist_start":0.19951,"object_z_max":0.03385,"peak_contact_force":0.77054,"phase_name":"descend_to_contact","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":328.0,"raw_peak_contact_force":2.93059,"subtask_id":"contact","tcp_end":[0.49024,0.13854,0.04182],"tcp_start":[0.47882,0.1427,0.12897],"tcp_to_object_dist_end":0.03585,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":692.0,"n_steps_budget":1000.0,"object_pos_end":[0.52963,0.16003,0.01405],"object_pos_start":[0.49744,0.16002,0.01404],"object_to_goal_dist_end":0.24324,"object_to_goal_dist_start":0.24144,"object_z_max":0.01405,"peak_contact_force":0.59349,"phase_name":"push_along_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":692.0,"raw_peak_contact_force":0.77052,"subtask_id":"push","tcp_end":[0.49582,-0.06632,0.03558],"tcp_start":[0.49024,0.13854,0.04182],"tcp_to_object_dist_end":0.22988,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.02899,"average_solve_count":138.0,"average_success_count":138.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_peg.approach_speed":0.06733,"approach_peg.lateral_correction_x":0.0199,"approach_peg.lateral_correction_y":0.00819,"descend_to_contact.descend_contact_y":0.01786,"descend_to_contact.descend_force_threshold":16.03261,"descend_to_contact.descend_speed":0.02427,"push_along_channel.push_force_limit":28.41439,"push_along_channel.push_lateral_adjust":-0.00194,"push_along_channel.push_speed":0.02363},"optimized_scores":{"best_composite_score":-0.37352,"best_fitness_score":0.10648,"best_task_score":3e-05},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_left_wall","contact_count":1.0,"contact_point_centroid":[0.52792,0.07913,0.05988],"force_p95":117.96311,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":117.96311,"mean_force":117.96311,"phase_index":1.0,"phase_name":"descend_to_contact","phase_type":"descend","tcp_position_centroid":[0.51605,0.07906,0.06154]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":3.0,"contact_point_centroid":[0.52772,0.07908,0.05968],"force_p95":92.73228,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":97.28735,"mean_force":62.26226,"phase_index":2.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.51586,0.07902,0.06114]},{"body_a":"peg","body_b":"channel_base_body","contact_count":757.0,"contact_point_centroid":[0.50578,0.06301,0.00936],"force_p95":0.55667,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.88411,"mean_force":0.56444,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.52149,0.13652,0.20739]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":34.0,"contact_point_centroid":[0.53102,0.06295,0.03156],"force_p95":1.1362,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.98455,"mean_force":0.48262,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.50009,0.19792,0.29679]},{"body_a":"peg","body_b":"channel_base_body","contact_count":210.0,"contact_point_centroid":[0.506,0.06299,0.00938],"force_p95":0.55235,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55419,"mean_force":0.54657,"phase_index":1.0,"phase_name":"descend_to_contact","phase_type":"descend","tcp_position_centroid":[0.52926,0.07794,0.09228]},{"body_a":"peg","body_b":"channel_base_body","contact_count":3.0,"contact_point_centroid":[0.5207,0.05744,0.00938],"force_p95":0.54762,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.5479,"mean_force":0.54577,"phase_index":2.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.51586,0.07902,0.06114]}],"total_contact_groups":6},"final_pose_error":0.16107,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50598,0.06293,0.0338],"final_tcp_position":[0.51568,0.07893,0.0609],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.52962,0.06295,0.04]},"peak_contact_force":117.96311,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":785.0,"n_steps_budget":1000.0,"object_pos_end":[0.50603,0.06301,0.0338],"object_pos_start":[0.52962,0.06295,0.04],"object_to_goal_dist_end":0.14327,"object_to_goal_dist_start":0.14598,"object_z_max":0.04001,"peak_contact_force":0.54798,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":791.0,"raw_peak_contact_force":3.88411,"tcp_end":[0.54345,0.0777,0.12436],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.09908,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":210.0,"n_steps_budget":1000.0,"object_pos_end":[0.50603,0.063,0.0338],"object_pos_start":[0.50603,0.06301,0.0338],"object_to_goal_dist_end":0.14326,"object_to_goal_dist_start":0.14327,"object_z_max":0.03381,"peak_contact_force":117.96311,"phase_name":"descend_to_contact","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":211.0,"raw_peak_contact_force":117.96311,"subtask_id":"contact","tcp_end":[0.51596,0.07907,0.06129],"tcp_start":[0.54345,0.0777,0.12436],"tcp_to_object_dist_end":0.03335,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.50603,0.06297,0.0338],"object_pos_start":[0.50603,0.063,0.0338],"object_to_goal_dist_end":0.14323,"object_to_goal_dist_start":0.14326,"object_z_max":0.0338,"peak_contact_force":51.73664,"phase_name":"push_along_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":6.0,"raw_peak_contact_force":97.28735,"subtask_id":"push","tcp_end":[0.51568,0.07893,0.0609],"tcp_start":[0.51575,0.07898,0.061],"tcp_to_object_dist_end":0.0329,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```