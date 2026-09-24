## Search State

- **Seed**: 4
- **Iteration**: 12 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 11 | push → align → release → insert | impedance_motion | linear_cartesian | linear_cartesian | impedance_motion | impedance_control | position_control | admittance_control | impedance_control | time_limit | pose_tolerance | pose_tolerance | force_exceeded | 6 | 0.3041 | 0.61 | ❌ rejected |
| 10 | approach → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | 5 | 0.2434 | 0.58 | ❌ rejected |
| 9 | approach → contact → push | linear_cartesian | linear_cartesian | impedance_motion | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | time_limit | 7 | -0.2933 | 0.01 | ❌ rejected |
| 8 | approach → contact → push | linear_cartesian | linear_cartesian | impedance_motion | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | 6 | 0.1780 | 0.58 | ❌ rejected |
| 7 | approach → contact → push | linear_cartesian | linear_cartesian | impedance_motion | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | 5 | 0.3408 | 0.22 | ❌ rejected |

**Proposal policy**: task_score is 0.61 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `5d75b33f12bcf5a2f8bdcc4693a93f63ce145f4d32d6acfe75032964e261854c`
- Frozen object start: [0.5354444884457894, 0.08090620422514894, 0.04]
- Frozen task target: [0.5354444884457894, -0.07909379577485107, 0.04]
- Goal object position: (0.5354444884457894, -0.07909379577485107, 0.04)
- Task success criterion: peg must traverse the channel (0.16 m long) along axis (0.0, -1.0, 0.0); score = axial progress × lateral alignment — NOT a fixed TCP endpoint
- Object initial pose: (0.5354444884457894, 0.08090620422514894, 0.04)
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
  frozen_object_start: [0.5354, 0.0809, 0.04]
  frozen_task_target: [0.5354, -0.0791, 0.04]
  frozen_fixture_position: [0.54, 0, 0.035]
  frozen_object_starts: {'peg': [0.5354444884457894, 0.08090620422514894, 0.04]}
  frozen_targets: {'channel_exit': [0.5354444884457894, -0.07909379577485107, 0.04]}
  frozen_fixtures: {'channel_left_wall': [0.54, 0.0, 0.035], 'channel_right_wall': [0.46, 0.0, 0.035]}
  channel_axis: [0, -1, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 40
  channel_length_m: 0.16
  force_scale_n: 5
  realized_scene_sha256: 5d75b33f12bcf5a2f8bdcc4693a93f63ce145f4d32d6acfe75032964e261854c

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

## Current Skill (Q=0.304) — your mutation base

```yaml
skill: peg_channel
skill_type: arm_gripper
phases:
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
    push_speed:
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
- id: release_1
  type: release
  generator: linear_cartesian
  control: admittance_control
  termination: pose_tolerance
  end_effector_action: open
- id: insert_1
  type: insert
  generator: impedance_motion
  control: impedance_control
  termination: force_exceeded
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

```

## Design Metrics

- **Composite score**: 0.304
- **task_score** (E): 0.605
- **fitness_score**: 0.331  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.333
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.360

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| push_1 | 1.00 | 1.00 | 0.1849 |
| align_1 | 1.00 | 1.00 | 0.1195 |
| release_1 | 1.00 | 1.00 | 0.1728 |
| insert_1 | 1.00 | 1.00 | 0.0000 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| push_1 | push | 1.00 / time_limit | (0.500, 0.200, 0.300)→(0.497, 0.086, 0.155) | (0.521, 0.084, 0.040)→(0.505, 0.084, 0.034) | 0.166→0.165 | 1.00 / 1.000 | 0.544 | 3.242 |
| align_1 | align | 1.00 / step_budget | (0.497, 0.086, 0.155)→(0.501, 0.121, 0.042) | (0.505, 0.084, 0.034)→(0.505, 0.082, 0.035) | 0.165→0.162 | 1.00 / 1.333 | 1.117 | 62.055 |
| release_1 | release | 1.00 / step_budget | (0.501, 0.121, 0.042)→(0.498, -0.052, 0.037) | (0.505, 0.082, 0.035)→(0.506, -0.081, 0.036) | 0.162→0.010 | 1.00 / 3.667 | 87.622 | 99.480 |
| insert_1 | insert | 1.00 / force_exceeded | (0.498, -0.052, 0.037)→(0.498, -0.052, 0.037) | (0.506, -0.081, 0.036)→(0.506, -0.081, 0.036) | 0.010→0.010 | 1.00 / 3.667 | 92.781 | 92.781 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.971
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.971
- phase_score: 0.187
- phase_breakdown.contact_score: 0.000
- phase_breakdown.approach_score: 0.889
- phase_breakdown.push_score: 0.016

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.501
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.971
- **Median Q (composite search score)**: 0.276
- **K-run variance**: 0.0166
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.247


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `424e8a040c59c1e1e42822c1022320b6050001458f7b9b4937cb9238911ce80b`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.04,0.04]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `72d2436204c0f1ee3bbdbdfe3e5489661153a48f95d8f0dc3b73e6ce1e1e081b`; realized-scene SHA-256: `5d75b33f12bcf5a2f8bdcc4693a93f63ce145f4d32d6acfe75032964e261854c`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.53544,0.08091,0.04]},{"name":"goal","value":[0.53544,-0.07909,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.53544,0.08091,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.53544,-0.07909,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.89474,"average_solve_count":114.0,"average_success_count":114.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":0.00565,"align_1.lateral_offset_y":-0.00016,"insert_1.insertion_depth":0.12069,"insert_1.insertion_force":5.99583,"push_1.push_distance":0.1048,"push_1.push_speed":0.08091},"optimized_scores":{"best_composite_score":0.16262,"best_fitness_score":0.18929,"best_task_score":0.30811},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":507.0,"contact_point_centroid":[0.54251,-0.01029,0.05999],"force_p95":77.73584,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":86.12051,"mean_force":57.66407,"phase_index":2.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.49775,-0.00977,0.03684]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.54274,-0.04955,0.05998],"force_p95":83.0295,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":83.0295,"mean_force":83.0295,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.49811,-0.05353,0.03662]},{"body_a":"attachment","body_b":"peg","contact_count":846.0,"contact_point_centroid":[0.50375,-0.0034,0.04482],"force_p95":20.43644,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":40.29927,"mean_force":8.0492,"phase_index":2.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.4977,0.00821,0.03688]},{"body_a":"peg","body_b":"channel_base_body","contact_count":176.0,"contact_point_centroid":[0.50693,-0.10045,0.05798],"force_p95":21.8432,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":39.90663,"mean_force":18.45216,"phase_index":2.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.49801,-0.05339,0.03664]},{"body_a":"peg","body_b":"channel_base_body","contact_count":615.0,"contact_point_centroid":[0.50538,-0.0144,0.00981],"force_p95":16.30627,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":23.66142,"mean_force":6.08508,"phase_index":2.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.49774,0.02926,0.03711]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.50704,-0.06527,0.0557],"force_p95":17.72013,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":17.72013,"mean_force":17.72013,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.49811,-0.05353,0.03662]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1.0,"contact_point_centroid":[0.50684,-0.10045,0.0605],"force_p95":17.64812,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":17.64812,"mean_force":17.64812,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.49811,-0.05353,0.03662]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":341.0,"contact_point_centroid":[0.52506,-0.01917,0.02531],"force_p95":4.42797,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.81303,"mean_force":1.02876,"phase_index":2.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.49768,0.00834,0.03688]},{"body_a":"peg","body_b":"channel_base_body","contact_count":971.0,"contact_point_centroid":[0.50581,0.08087,0.00937],"force_p95":0.55064,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.32595,"mean_force":0.56248,"phase_index":0.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49741,0.13943,0.22597]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":36.0,"contact_point_centroid":[0.5324,0.0809,0.02649],"force_p95":1.27622,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.70803,"mean_force":0.52144,"phase_index":0.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49933,0.19818,0.29745]},{"body_a":"peg","body_b":"channel_base_body","contact_count":415.0,"contact_point_centroid":[0.50598,0.08091,0.00938],"force_p95":0.55006,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55006,"mean_force":0.54678,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49783,0.09985,0.10113]}],"total_contact_groups":11},"final_pose_error":0.02676,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.5069,-0.08289,0.03551],"final_tcp_position":[0.49811,-0.05353,0.03662],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.53544,0.08091,0.04]},"peak_contact_force":86.12051,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50597,0.0809,0.03378],"object_pos_start":[0.53544,0.08091,0.04],"object_to_goal_dist_end":0.16113,"object_to_goal_dist_start":0.16476,"object_z_max":0.04001,"peak_contact_force":0.54527,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1007.0,"raw_peak_contact_force":4.32595,"tcp_end":[0.49683,0.08449,0.16188],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.12848,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":415.0,"n_steps_budget":840.0,"object_pos_end":[0.50599,0.08089,0.03378],"object_pos_start":[0.50597,0.0809,0.03378],"object_to_goal_dist_end":0.16112,"object_to_goal_dist_start":0.16113,"object_z_max":0.03378,"peak_contact_force":0.55006,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":415.0,"raw_peak_contact_force":0.55006,"tcp_end":[0.50114,0.11644,0.0413],"tcp_start":[0.49683,0.08449,0.16188],"tcp_to_object_dist_end":0.03666,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50689,-0.08288,0.03551],"object_pos_start":[0.50599,0.08089,0.03378],"object_to_goal_dist_end":0.00871,"object_to_goal_dist_start":0.16112,"object_z_max":0.0384,"peak_contact_force":75.32693,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2485.0,"raw_peak_contact_force":86.12051,"tcp_end":[0.49811,-0.05353,0.03662],"tcp_start":[0.50114,0.11644,0.0413],"tcp_to_object_dist_end":0.03066,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1.0,"n_steps_budget":600.0,"object_pos_end":[0.5069,-0.08289,0.03551],"object_pos_start":[0.50689,-0.08288,0.03551],"object_to_goal_dist_end":0.00872,"object_to_goal_dist_start":0.00871,"object_z_max":0.03551,"peak_contact_force":83.0295,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":3.0,"raw_peak_contact_force":83.0295,"tcp_end":[0.49811,-0.05353,0.03662],"tcp_start":[0.49811,-0.05353,0.03662],"tcp_to_object_dist_end":0.03067,"terminated_normally":true,"termination_reason":"force_exceeded"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `54762c1e743ba455eff3c9979c2b42f5642abe1893e28eae37dc231d7efcd4e4`; realized-scene SHA-256: `ca4f9624fc0e37438ffe7fd92236fc537e25f346e4aaef8c3b399c2f4b45089e`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.5244,0.10464,0.04]},{"name":"goal","value":[0.5244,-0.05536,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.5244,0.10464,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.5244,-0.05536,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.88889,"average_solve_count":108.0,"average_success_count":108.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":-0.00588,"align_1.lateral_offset_y":0.0009,"insert_1.insertion_depth":0.14207,"insert_1.insertion_force":12.83439,"push_1.push_distance":0.07958,"push_1.push_speed":0.09988},"optimized_scores":{"best_composite_score":0.27555,"best_fitness_score":0.30222,"best_task_score":0.53727},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg","contact_count":95.0,"contact_point_centroid":[0.51194,0.12686,0.05502],"force_p95":158.69048,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":185.06517,"mean_force":108.45244,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.50315,0.13263,0.05671]},{"body_a":"peg","body_b":"channel_base_body","contact_count":392.0,"contact_point_centroid":[0.50718,0.10773,0.00917],"force_p95":144.21573,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":175.81962,"mean_force":26.72345,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49881,0.11507,0.0849]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.5427,-0.03939,0.05998],"force_p95":78.87875,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":78.87875,"mean_force":78.87875,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.49807,-0.04389,0.03669]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":315.0,"contact_point_centroid":[0.54285,-0.02336,0.05998],"force_p95":77.2428,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":78.74962,"mean_force":58.38885,"phase_index":2.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.49817,-0.02335,0.03681]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":90.0,"contact_point_centroid":[0.52513,0.10954,0.04832],"force_p95":30.78328,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":53.93108,"mean_force":11.12077,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.5042,0.13485,0.05463]},{"body_a":"attachment","body_b":"peg","contact_count":894.0,"contact_point_centroid":[0.50375,0.01588,0.0423],"force_p95":13.6111,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":22.12317,"mean_force":3.89913,"phase_index":2.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.4988,0.02755,0.03709]},{"body_a":"peg","body_b":"channel_base_body","contact_count":729.0,"contact_point_centroid":[0.50639,-0.02047,0.00989],"force_p95":14.23368,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":20.06824,"mean_force":5.05178,"phase_index":2.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.49894,0.02457,0.03727]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":520.0,"contact_point_centroid":[0.52504,-0.00307,0.03023],"force_p95":3.77282,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":6.75706,"mean_force":0.82155,"phase_index":2.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.49887,0.02598,0.03717]},{"body_a":"peg","body_b":"channel_base_body","contact_count":973.0,"contact_point_centroid":[0.50574,0.10468,0.00938],"force_p95":0.57571,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.33087,"mean_force":0.55797,"phase_index":0.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49732,0.14279,0.21159]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":32.0,"contact_point_centroid":[0.52975,0.10463,0.03425],"force_p95":1.06006,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.32726,"mean_force":0.42874,"phase_index":0.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.4994,0.19841,0.29749]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1.0,"contact_point_centroid":[0.50715,-0.08835,0.00999],"force_p95":0.552,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.552,"mean_force":0.552,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.49807,-0.04389,0.03669]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.5036,-0.05565,0.04238],"force_p95":0.47065,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.47065,"mean_force":0.47065,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.49807,-0.04389,0.03669]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":1.0,"contact_point_centroid":[0.525,-0.07512,0.06],"force_p95":0.19869,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.19869,"mean_force":0.19869,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.49807,-0.04389,0.03669]}],"total_contact_groups":13},"final_pose_error":0.03631,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50698,-0.07285,0.0366],"final_tcp_position":[0.49807,-0.04389,0.03669],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.5244,0.10464,0.04]},"peak_contact_force":185.06517,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50599,0.10464,0.03384],"object_pos_start":[0.5244,0.10464,0.04],"object_to_goal_dist_end":0.18484,"object_to_goal_dist_start":0.18624,"object_z_max":0.04,"peak_contact_force":0.54104,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1005.0,"raw_peak_contact_force":3.33087,"tcp_end":[0.49662,0.09047,0.13347],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.10107,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":392.0,"n_steps_budget":720.0,"object_pos_end":[0.50651,0.09791,0.03598],"object_pos_start":[0.50599,0.10464,0.03384],"object_to_goal_dist_end":0.17808,"object_to_goal_dist_start":0.18484,"object_z_max":0.03577,"peak_contact_force":2.25224,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":577.0,"raw_peak_contact_force":185.06517,"tcp_end":[0.50465,0.14088,0.0429],"tcp_start":[0.49662,0.09047,0.13347],"tcp_to_object_dist_end":0.04356,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50698,-0.07285,0.0366],"object_pos_start":[0.50651,0.09791,0.03598],"object_to_goal_dist_end":0.01055,"object_to_goal_dist_start":0.17808,"object_z_max":0.03858,"peak_contact_force":72.55248,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2458.0,"raw_peak_contact_force":78.74962,"tcp_end":[0.49807,-0.04389,0.03669],"tcp_start":[0.50465,0.14088,0.0429],"tcp_to_object_dist_end":0.03029,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1.0,"n_steps_budget":600.0,"object_pos_end":[0.50698,-0.07285,0.0366],"object_pos_start":[0.50698,-0.07285,0.0366],"object_to_goal_dist_end":0.01055,"object_to_goal_dist_start":0.01055,"object_z_max":0.0366,"peak_contact_force":78.87875,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":4.0,"raw_peak_contact_force":78.87875,"tcp_end":[0.49807,-0.04389,0.03669],"tcp_start":[0.49807,-0.04389,0.03669],"tcp_to_object_dist_end":0.0303,"terminated_normally":true,"termination_reason":"force_exceeded"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `b230a5798f38c3fb8968a6bc74f96ee85fe7026f3170cf8216fc868a1c5c570f`; realized-scene SHA-256: `07dc0764c781629358e2f97446117d9c410d14c078397be91277b4276116a1de`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50305,0.06746,0.04]},{"name":"goal","value":[0.50305,-0.09254,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.50305,0.06746,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.50305,-0.09254,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.88596,"average_solve_count":114.0,"average_success_count":114.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":0.00034,"align_1.lateral_offset_y":-0.00057,"insert_1.insertion_depth":0.07655,"insert_1.insertion_force":13.32005,"push_1.push_distance":0.10932,"push_1.push_speed":0.08012},"optimized_scores":{"best_composite_score":0.47398,"best_fitness_score":0.50065,"best_task_score":0.97084},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":502.0,"contact_point_centroid":[0.54205,-0.02358,0.05999],"force_p95":123.02123,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":133.57045,"mean_force":70.80321,"phase_index":2.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.49729,-0.02354,0.03685]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.54341,-0.05534,0.05998],"force_p95":116.43577,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":116.43577,"mean_force":116.43577,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.49881,-0.05895,0.0365]},{"body_a":"attachment","body_b":"peg","contact_count":866.0,"contact_point_centroid":[0.50299,-0.01491,0.04433],"force_p95":82.40596,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":102.04112,"mean_force":22.4017,"phase_index":2.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.49679,-0.00356,0.03698]},{"body_a":"peg","body_b":"channel_base_body","contact_count":257.0,"contact_point_centroid":[0.50573,-0.10222,0.05512],"force_p95":84.33452,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":100.54587,"mean_force":59.98004,"phase_index":2.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.49838,-0.05763,0.03657]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.50461,-0.0705,0.04898],"force_p95":66.45142,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":66.45142,"mean_force":66.45142,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.49881,-0.05895,0.0365]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1.0,"contact_point_centroid":[0.50445,-0.10299,0.05998],"force_p95":66.2058,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":66.2058,"mean_force":66.2058,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.49881,-0.05895,0.0365]},{"body_a":"peg","body_b":"channel_base_body","contact_count":643.0,"contact_point_centroid":[0.50562,-0.02663,0.00983],"force_p95":17.26534,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":21.5864,"mean_force":6.2435,"phase_index":2.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.49647,0.01548,0.03727]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":423.0,"contact_point_centroid":[0.52509,-0.0072,0.02642],"force_p95":7.48346,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":11.2189,"mean_force":2.25305,"phase_index":2.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.49611,0.01957,0.0371]},{"body_a":"peg","body_b":"channel_base_body","contact_count":984.0,"contact_point_centroid":[0.50307,0.06748,0.00936],"force_p95":0.55225,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06903,"mean_force":0.55539,"phase_index":0.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49746,0.13919,0.2309]},{"body_a":"peg","body_b":"channel_base_body","contact_count":421.0,"contact_point_centroid":[0.50298,0.06744,0.00938],"force_p95":0.55057,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55071,"mean_force":0.54666,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49661,0.09297,0.10569]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1.0,"contact_point_centroid":[0.49535,-0.10323,0.00998],"force_p95":0.32339,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.32339,"mean_force":0.32339,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.49881,-0.05895,0.0365]}],"total_contact_groups":11},"final_pose_error":0.02138,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50449,-0.08787,0.03503],"final_tcp_position":[0.49881,-0.05894,0.0365],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50305,0.06746,0.04]},"peak_contact_force":133.57045,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50308,0.06743,0.0338],"object_pos_start":[0.50305,0.06746,0.04],"object_to_goal_dist_end":0.14759,"object_to_goal_dist_start":0.14749,"object_z_max":0.04,"peak_contact_force":0.54571,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":984.0,"raw_peak_contact_force":2.06903,"tcp_end":[0.49688,0.0827,0.16986],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.13706,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":421.0,"n_steps_budget":870.0,"object_pos_end":[0.50308,0.06748,0.0338],"object_pos_start":[0.50308,0.06743,0.0338],"object_to_goal_dist_end":0.14765,"object_to_goal_dist_start":0.14759,"object_z_max":0.0338,"peak_contact_force":0.54739,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":421.0,"raw_peak_contact_force":0.55071,"tcp_end":[0.49852,0.10425,0.04189],"tcp_start":[0.49688,0.0827,0.16986],"tcp_to_object_dist_end":0.03792,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50449,-0.08789,0.03505],"object_pos_start":[0.50308,0.06748,0.0338],"object_to_goal_dist_end":0.01034,"object_to_goal_dist_start":0.14765,"object_z_max":0.03865,"peak_contact_force":114.98584,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2691.0,"raw_peak_contact_force":133.57045,"tcp_end":[0.49881,-0.05895,0.0365],"tcp_start":[0.49852,0.10425,0.04189],"tcp_to_object_dist_end":0.02953,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1.0,"n_steps_budget":600.0,"object_pos_end":[0.50449,-0.08787,0.03503],"object_pos_start":[0.50449,-0.08789,0.03505],"object_to_goal_dist_end":0.01034,"object_to_goal_dist_start":0.01034,"object_z_max":0.03505,"peak_contact_force":116.43577,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":4.0,"raw_peak_contact_force":116.43577,"tcp_end":[0.49881,-0.05894,0.0365],"tcp_start":[0.49881,-0.05895,0.0365],"tcp_to_object_dist_end":0.02952,"terminated_normally":true,"termination_reason":"force_exceeded"}],"success":true}]}
```